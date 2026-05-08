# Streamlit UI Plan for Student Enrollment App

## Overview

This plan describes a student-facing Streamlit interface for a simulated enrollment backend. The app assumes the user is already logged in as `student_1` and uses the existing simulated student context. The UI is layered: the Streamlit front end interacts only with a service layer, which provides enrollment-related operations.

The UI uses `st.session_state` to manage navigation and state:

- `st.session_state["role"]` — stores the current user role and is checked before rendering the app.
- `st.session_state["page"]` — controls the active page (`dashboard` or `selected_class`).
- `st.session_state["selected_class"]` — stores the currently chosen class record for the selected class page.
- `st.session_state["feedback"]` — stores transient feedback messages for the user.

## Role check and initial session state

1. On app start, the Streamlit script should initialize session state keys if missing.
2. Verify that `st.session_state["role"]` exists and is equal to `student`.
3. If the role is not a student, show a simple warning or informational message and do not render the student experience.
4. Default the page to `dashboard` and the selected class to `None` if not already set.

## Page routing with `st.session_state["page"]`

The app uses simple routing based on `st.session_state["page"]`:

- `dashboard` — the main student dashboard.
- `selected_class` — the details view for a chosen class.

Navigation flows:

- From the dashboard, selecting a class sets `st.session_state["selected_class"]` and changes `st.session_state["page"]` to `selected_class`.
- From the selected class page, clicking the back button sets `st.session_state["page"]` to `dashboard`.

## Page 1: Student Dashboard

### Layout

- Use `st.title("Student Dashboard")` as the page header.
- Place the enrollment key input near the top of the dashboard, directly beneath the title and any feedback messages.
- Retrieve the current student’s enrolled classes through the service layer.
- Display enrolled classes in `st.dataframe`.

### Enrollment key input

- Provide a `st.text_input` labeled something like `"Enter enrollment key"`.
- Provide a `st.button` to submit the enrollment key.
- When the button is clicked:
  - call the service layer enrollment function with the current student and the entered key.
  - update `st.session_state["feedback"]` with success or error text.
  - if enrollment succeeds, refresh the enrolled classes view by reloading from the service layer.
  - use rerun logic after the action to ensure the UI reflects the new state.

### Class actions

- For each enrolled class row shown in the dashboard, include:
  - a `Go to Class` action that sets `st.session_state["selected_class"]` to that class record and changes `st.session_state["page"]` to `selected_class`.
  - an `Unenroll` action that triggers a soft unenroll through the service layer.
- When `Unenroll` is clicked:
  - call the service layer soft-unenroll operation with the student and class identifier.
  - set `st.session_state["page"]` to `dashboard` so the user is returned to the dashboard immediately.
  - update `st.session_state["feedback"]` with a clear success message on success, or `st.error` text on failure.
  - refresh the dashboard listing and keep the record in the database.
  - show `st.success` when the unenroll action succeeds, or `st.error` when it fails.

### Feedback

- Use `st.success`, `st.error`, or `st.warning` to surface messages after actions.
- Show the latest message stored in `st.session_state["feedback"]` near the top of the dashboard.
- Clear the message when the page reruns with a stable state or after it has been displayed once.

## Page 2: Selected Class Page

### Layout

- Use `st.title` to display the selected class name or a generic title like `"Class Details"`.
- Use `st.write` to display details of the selected class, including course ID, instructor, enrollment status, and any relevant course metadata.
- Use `st.button("Back to Dashboard")` to return to the dashboard.

### Behavior

- If `st.session_state["selected_class"]` is missing, fall back to a dashboard redirect or show a warning and set the page to `dashboard`.
- The back button should set `st.session_state["page"] = "dashboard"` and optionally clear `st.session_state["selected_class"]`.
- Show any feedback message relevant to the selected class page if present.

## Service layer interactions

The UI should treat the service layer as the only backend interface. It should not directly execute SQL or perform database operations.

Required service layer operations assumed to exist:

- `get_enrolled_classes(student_id)` — returns the student’s currently enrolled classes.
- `enroll_student_with_key(student_id, email, enrollment_key)` — enrolls or reactivates a student, returning the updated record or a failure indicator.
- `soft_unenroll_student(student_id, course_id)` — marks a class record as unenrolled without deleting it.
- `get_class_details(student_id, course_id)` or equivalent access to the selected class details.

The UI flow should:

- call the service layer on page load to populate the dashboard.
- call the service layer to perform enrollment key submission and unenroll actions.
- use the returned result to determine what success/error message to display.

## Feedback and rerun logic

- After an action, update `st.session_state["feedback"]` with the message type and text.
- Use a rerun mechanism so the dashboard or selected class page refreshes after the action.
- Display feedback with the correct Streamlit message helper:
  - success messages with `st.success`
  - error messages with `st.error`
  - non-critical notices with `st.warning`

## Summary of UI flow

1. App starts and validates `st.session_state["role"]` as `student`.
2. If valid, show the dashboard page.
3. Dashboard displays enrolled classes and input controls.
4. Enrollment key submission goes through the service layer and updates feedback.
5. The student can navigate to a selected class page using `Go to Class`.
6. The selected class page shows details and a back control.
7. Unenroll actions are soft and keep the record in the database; the dashboard updates after the action.

This plan keeps UI responsibilities separate from the backend and uses `st.session_state` to manage page routing, selected class context, and feedback messages.