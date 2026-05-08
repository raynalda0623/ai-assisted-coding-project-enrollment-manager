from __future__ import annotations

import streamlit as st

from service_layer import (
    enroll_student_with_key,
    get_class_details,
    get_current_student,
    get_enrolled_classes,
    soft_unenroll_student,
)


def init_session_state() -> None:
    if "role" not in st.session_state:
        st.session_state["role"] = "student"
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"
    if "selected_class" not in st.session_state:
        st.session_state["selected_class"] = None
    if "feedback" not in st.session_state:
        st.session_state["feedback"] = None
    if "enrollment_key" not in st.session_state:
        st.session_state["enrollment_key"] = ""


def set_feedback(message: str, level: str = "success") -> None:
    st.session_state["feedback"] = {"type": level, "text": message}


def display_feedback() -> None:
    feedback = st.session_state.get("feedback")
    if not feedback:
        return

    if feedback.get("type") == "success":
        st.success(feedback.get("text", ""))
    elif feedback.get("type") == "error":
        st.error(feedback.get("text", ""))
    else:
        st.warning(feedback.get("text", ""))


def render_dashboard() -> None:
    student = get_current_student()

    st.title("Student Dashboard")
    display_feedback()

    st.text_input(
        "Enter enrollment key",
        key="enrollment_key",
        placeholder="MISY350-SPRING",
    )

    if st.button("Submit enrollment key"):
        enrollment_key = st.session_state["enrollment_key"].strip()
        if not enrollment_key:
            set_feedback("Please enter an enrollment key before submitting.", "warning")
            st.experimental_rerun()

        result = enroll_student_with_key(student["user_id"], student["email"], enrollment_key)
        if result:
            set_feedback(
                f"Successfully enrolled in {result['course_id']}.",
                "success",
            )
        else:
            set_feedback(
                "Enrollment failed. Please check the enrollment key and try again.",
                "error",
            )
        st.experimental_rerun()

    enrolled_classes = get_enrolled_classes(student["user_id"])
    if enrolled_classes:
        st.dataframe(enrolled_classes)
    else:
        st.info("You are not currently enrolled in any classes.")

    for record in enrolled_classes:
        cols = st.columns([3, 1, 1])
        cols[0].markdown(
            f"**{record['course_id']}** - {record['course_name']}  \n"
            f"Instructor: {record['instructor']}  \n"
            f"Status: {record['status']}  \n"
            f"Enrolled at: {record['enrolled_at']}"
        )

        if cols[1].button("Go to Class", key=f"go_{record['course_id']}"):
            st.session_state["selected_class"] = record
            st.session_state["page"] = "selected_class"
            st.experimental_rerun()

        if cols[2].button("Unenroll", key=f"unenroll_{record['course_id']}"):
            success = soft_unenroll_student(student["user_id"], record["course_id"])
            if success:
                set_feedback(
                    f"Successfully unenrolled from {record['course_id']}.",
                    "success",
                )
            else:
                set_feedback(
                    f"Could not unenroll from {record['course_id']}.",
                    "error",
                )
            st.session_state["page"] = "dashboard"
            st.experimental_rerun()


def render_selected_class_page() -> None:
    selected_class = st.session_state.get("selected_class")
    student = get_current_student()

    if not selected_class:
        st.warning("No class selected. Returning to the dashboard.")
        st.session_state["page"] = "dashboard"
        st.experimental_rerun()
        return

    class_details = get_class_details(student["user_id"], selected_class["course_id"])
    if class_details:
        selected_class = class_details
        st.session_state["selected_class"] = class_details

    st.title(f"Class Details: {selected_class['course_name']}")
    display_feedback()

    st.write("**Course ID:**", selected_class["course_id"])
    st.write("**Instructor:**", selected_class["instructor"])
    st.write("**Status:**", selected_class["status"])
    st.write("**Enrolled at:**", selected_class["enrolled_at"])

    if st.button("Back to Dashboard"):
        st.session_state["page"] = "dashboard"
        st.experimental_rerun()


def main() -> None:
    init_session_state()

    if st.session_state["role"] != "student":
        st.warning("Access denied. You must be signed in as a student to use this app.")
        return

    if st.session_state["page"] == "selected_class":
        render_selected_class_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
