from __future__ import annotations

from typing import Any, Optional

import enrollment_starter as backend


def get_current_student() -> dict[str, str]:
    """Return the simulated current student context."""
    return backend.CURRENT_STUDENT


def get_enrolled_classes(student_id: str) -> list[dict[str, Any]]:
    """Return the enrolled classes for the given student."""
    return backend.get_student_enrollments(student_id)


def enroll_student_with_key(
    student_id: str,
    email: str,
    enrollment_key: str,
) -> Optional[dict[str, Any]]:
    """Enroll or re-enroll the student using an enrollment key."""
    return backend.enroll_with_key(student_id, email, enrollment_key)


def soft_unenroll_student(student_id: str, course_id: str) -> bool:
    """Soft-unenroll the student from a course without deleting the record."""
    return backend.soft_unenroll_student(student_id, course_id)


def get_class_details(student_id: str, course_id: str) -> Optional[dict[str, Any]]:
    """Return a single course enrollment record for the student."""
    return backend.get_student_course_record(student_id, course_id)
