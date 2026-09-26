"""
validation.py
Reusable validation functions for the Scholarship Application System.
Each single-field function returns (is_valid: bool, error_message: str).
"""

import os
import re
from datetime import date

EMAIL_PATTERN = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
MOBILE_PATTERN = re.compile(r"^(09\d{9}|\+63\d{10})$")   # PH formats
NAME_PATTERN = re.compile(r"^[A-Za-zÑñ\.\-' ]+$")

GWA_MIN, GWA_MAX = 1.0, 5.0
ALLOWED_UPLOAD_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")


def validate_name(name: str, field_label: str = "Name"):
    if not name or not name.strip():
        return False, f"{field_label} is required."
    if not NAME_PATTERN.match(name.strip()):
        return False, f"{field_label} contains invalid characters."
    return True, ""


def validate_email(email: str):
    if not email or not email.strip():
        return False, "Email address is required."
    if not EMAIL_PATTERN.match(email.strip()):
        return False, "Email address format is invalid."
    return True, ""


def validate_mobile_number(number: str):
    if not number or not number.strip():
        return False, "Mobile number is required."
    if not MOBILE_PATTERN.match(number.strip()):
        return False, "Mobile number must be in 09XXXXXXXXX or +63XXXXXXXXXX format."
    return True, ""


def validate_date_of_birth(dob: date, min_age: int = 10, max_age: int = 100):
    if dob is None:
        return False, "Date of birth is required."
    if dob > date.today():
        return False, "Date of birth cannot be in the future."
    age = (date.today() - dob).days // 365
    if age < min_age or age > max_age:
        return False, f"Date of birth implies an unrealistic age ({age})."
    return True, ""


def validate_gwa(gwa):
    if gwa is None:
        return False, "GWA/GPA is required."
    try:
        gwa = float(gwa)
    except (TypeError, ValueError):
        return False, "GWA/GPA must be numeric."
    if not (GWA_MIN <= gwa <= GWA_MAX):
        return False, f"GWA/GPA must be between {GWA_MIN} and {GWA_MAX}."
    return True, ""


def validate_income(income):
    if income is None:
        return False, "Household monthly income is required."
    try:
        income = float(income)
    except (TypeError, ValueError):
        return False, "Household monthly income must be numeric."
    if income < 0:
        return False, "Household monthly income cannot be negative."
    return True, ""


def validate_file_upload(file_path: str, required: bool = True):
    if not file_path:
        return (False, "A required document upload is missing.") if required else (True, "")
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ALLOWED_UPLOAD_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed: {ALLOWED_UPLOAD_EXTENSIONS}."
    if not os.path.exists(file_path):
        return False, f"File not found at path: {file_path}"
    return True, ""


def validate_required_text(value: str, field_label: str):
    if not value or not value.strip():
        return False, f"{field_label} is required."
    return True, ""


def validate_evaluation_score(score):
    if score is None:
        return False, "Evaluation score is required."
    try:
        score = float(score)
    except (TypeError, ValueError):
        return False, "Evaluation score must be numeric."
    if not (0 <= score <= 100):
        return False, "Evaluation score must be between 0 and 100."
    return True, ""


def validate_application_for_submission(application):
    """
    Full battery of required-field checks needed before an Application
    can move out of DRAFT status. Returns (is_valid, list_of_errors).
    """
    errors = []
    checks = [
        validate_name(application.applicant.first_name, "First name"),
        validate_name(application.applicant.last_name, "Last name"),
        validate_email(application.applicant.email),
        validate_mobile_number(application.applicant.mobile_number),
        validate_date_of_birth(application.applicant.date_of_birth),
        validate_gwa(application.academic_background.gwa),
        validate_file_upload(application.academic_background.tor_file_path),
        validate_income(application.financial_profile.household_monthly_income),
    ]
    for is_valid, message in checks:
        if not is_valid:
            errors.append(message)
    return (len(errors) == 0), errors