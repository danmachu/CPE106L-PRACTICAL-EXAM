"""
main.py
Interactive console application for the Scholarship Application System.
Starts pre-loaded with 9 real scholarship programs (see seed_data.py).
Applicant/academic/financial data comes from real user input; every
field is checked with validation.py before it's accepted.
"""

from datetime import datetime
from functools import partial

from models import (
    Applicant, AcademicBackground, FinancialProfile, ScholarshipProgram,
    Application, Gender, SchoolType, EmploymentStatus, ScholarshipType,
    ApplicationStatus,
)
from validation import (
    validate_name, validate_email, validate_mobile_number, validate_date_of_birth,
    validate_gwa, validate_income, validate_evaluation_score, validate_required_text,
    validate_application_for_submission,
)
from storage import DataStore, NotFoundError, DuplicateIDError
from search import (
    search_by_name, search_by_status, search_by_scholarship_type,
    search_by_gwa_range, advanced_search,
)
from cli_helpers import (
    prompt_text, prompt_free_text, prompt_date, prompt_optional_date,
    prompt_float, prompt_enum, InputCancelled,
)
from eligibility import list_eligible_programs
from seed_data import seed_programs

store = DataStore()
seed_programs(store)


# ---------------------------------------------------------------------------
# Registration flows
# ---------------------------------------------------------------------------

def register_applicant():
    print("\n--- Register New Applicant ---  (type 'cancel' anytime to abort)")
    try:
        first_name = prompt_text("First name", partial(validate_name, field_label="First name"))
        middle_name = prompt_free_text("Middle name (blank if none)")
        last_name = prompt_text("Last name", partial(validate_name, field_label="Last name"))
        suffix = prompt_free_text("Suffix, e.g. Jr./III (blank if none)")
        email = prompt_text("Email address", validate_email)
        mobile_number = prompt_text("Mobile number (09XXXXXXXXX)", validate_mobile_number)
        date_of_birth = prompt_date("Date of birth", validate_date_of_birth)
        gender = prompt_enum("Gender", Gender)
        address = prompt_text("Permanent residential address",
                               partial(validate_required_text, field_label="Address"))
    except InputCancelled:
        print("Cancelled. No applicant was added.")
        return None

    applicant_id = store.generate_applicant_id()
    applicant = Applicant(
        applicant_id=applicant_id,
        first_name=first_name, middle_name=middle_name, last_name=last_name, suffix=suffix,
        email=email, mobile_number=mobile_number,
        date_of_birth=date_of_birth, gender=gender,
        permanent_address=address,
    )
    store.add_applicant(applicant)
    print(f"[OK] Applicant registered with ID: {applicant_id}")
    return applicant


def register_program():
    print("\n--- Register Scholarship Program ---  (type 'cancel' anytime to abort)")
    try:
        grant_name = prompt_text("Scholarship grant name", partial(validate_required_text, field_label="Grant name"))
        provider = prompt_text("Grant provider/donor", partial(validate_required_text, field_label="Provider"))
        scholarship_type = prompt_enum("Scholarship type", ScholarshipType)
        tuition = prompt_float("Tuition allowance", lambda v: (v >= 0, "Must not be negative."))
        stipend = prompt_float("Monthly stipend", lambda v: (v >= 0, "Must not be negative."))
        book = prompt_float("Book allowance", lambda v: (v >= 0, "Must not be negative."))
    except InputCancelled:
        print("Cancelled. No program was added.")
        return None

    program_id = store.generate_program_id()
    program = ScholarshipProgram(
        program_id=program_id, grant_name=grant_name, provider=provider,
        scholarship_type=scholarship_type,
        tuition_allowance=tuition, monthly_stipend=stipend, book_allowance=book,
    )
    store.add_program(program)
    print(f"[OK] Program registered with ID: {program_id}")
    return program


def view_programs():
    programs = store.list_programs()
    if not programs:
        print("No programs registered yet.")
        return
    for p in programs:
        print(f"\n{'=' * 64}")
        print(f"{p.program_id} - {p.grant_name}")
        print(f"Provider: {p.provider}")
        print(f"Type: {p.scholarship_type.value}")
        print(f"Total modeled coverage: Php {p.total_coverage():,.2f}")
        if p.benefits_description:
            print("Benefits:")
            for b in p.benefits_description:
                print(f"  - {b}")
        if p.eligibility_criteria:
            print("Eligibility criteria:")
            for e in p.eligibility_criteria:
                print(f"  - {e}")
        if p.required_documents:
            print("Required documents:")
            for d in p.required_documents:
                print(f"  - {d}")
        if p.application_period_notes:
            print("Application period / process:")
            for n in p.application_period_notes:
                print(f"  - {n}")
        if p.grantee_responsibilities:
            print("Responsibilities of grantees:")
            for r in p.grantee_responsibilities:
                print(f"  - {r}")


def create_application():
    print("\n--- Create Application ---  (type 'cancel' anytime to abort)")
    applicants = store.list_applicants()
    programs = store.list_programs()
    if not applicants:
        print("No applicants registered yet. Register one first (option 1).")
        return None
    if not programs:
        print("No scholarship programs registered yet.")
        return None

    print("\nApplicants on file:")
    for a in applicants:
        print(f"  {a.applicant_id} - {a.full_name()}")
    print("\nPrograms on file:")
    for p in programs:
        print(f"  {p.program_id} - {p.grant_name}")

    applicant_ids = {a.applicant_id for a in applicants}
    program_ids = {p.program_id for p in programs}

    try:
        applicant_id = prompt_text("Applicant ID", lambda v: (v in applicant_ids, "Unknown applicant ID."))
        program_id = prompt_text("Program ID", lambda v: (v in program_ids, "Unknown program ID."))

        print("\n-- Academic Background --")
        year_level = prompt_free_text("Current year/grade level", required=True)
        program_name = prompt_free_text("Enrolled course/program/strand", required=True)
        school_name = prompt_free_text("Name of current school/university", required=True)
        school_type = prompt_enum("School type", SchoolType)
        gwa = prompt_float("GWA/GPA (1.0 - 5.0 scale)", validate_gwa)
        tor_path = prompt_free_text("Path to TOR/Form 138 file (blank if not yet uploaded)")

        print("\n-- Financial & Socio-Economic Status --")
        income = prompt_float("Household monthly income", validate_income)
        father_name = prompt_free_text("Father's name (blank if N/A)")
        father_occupation = prompt_free_text("Father's occupation (blank if N/A)")
        father_status = prompt_enum("Father's employment status", EmploymentStatus)
        mother_name = prompt_free_text("Mother's name (blank if N/A)")
        mother_occupation = prompt_free_text("Mother's occupation (blank if N/A)")
        mother_status = prompt_enum("Mother's employment status", EmploymentStatus)
        guardian_name = prompt_free_text("Guardian's name (blank if N/A)")
        doc_path = prompt_free_text("Path to ITR/Indigency/Tax Exemption file (blank if not yet uploaded)")

        print("\n-- Application Control Dates --")
        opening_date = prompt_optional_date("Opening date")
        deadline = prompt_optional_date("Submission deadline")
    except InputCancelled:
        print("Cancelled. No application was created.")
        return None

    applicant = store.get_applicant(applicant_id)
    program = store.get_program(program_id)

    academic = AcademicBackground(
        year_level=year_level, program=program_name, school_name=school_name,
        school_type=school_type, gwa=gwa, tor_file_path=tor_path,
    )
    financial = FinancialProfile(
        household_monthly_income=income,
        father_name=father_name, father_occupation=father_occupation, father_employment_status=father_status,
        mother_name=mother_name, mother_occupation=mother_occupation, mother_employment_status=mother_status,
        guardian_name=guardian_name,
        supporting_document_paths=[doc_path] if doc_path else [],
    )
    application_id = store.generate_application_id()
    application = Application(
        application_id=application_id, applicant=applicant, academic_background=academic,
        financial_profile=financial, program=program,
        opening_date=opening_date, submission_deadline=deadline,
    )
    store.add_application(application)
    print(f"[OK] Application created with ID: {application_id} (status: {application.status.value})")
    return application


def check_eligibility_menu():
    print("\n--- Check Application Eligibility ---")
    application_id = prompt_free_text("Application ID", required=True)
    try:
        application = store.get_application(application_id)
    except NotFoundError as e:
        print(f"  ! {e}")
        return

    results = list_eligible_programs(store, application)
    print(f"\nEligibility check for {application.applicant.full_name()} ({application_id}):")
    for program, is_eligible, reasons in results:
        verdict = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE (machine-checkable criteria)"
        print(f"\n  [{verdict}] {program.grant_name}")
        for r in reasons:
            print(f"     - {r}")
        if not reasons:
            print("     (no unmet machine-checkable criteria; still confirm text-only criteria manually)")


def submit_application():
    print("\n--- Submit Application ---")
    application_id = prompt_free_text("Application ID", required=True)
    try:
        application = store.get_application(application_id)
    except NotFoundError as e:
        print(f"  ! {e}")
        return

    is_valid, errors = validate_application_for_submission(application)
    if not is_valid:
        print("[REJECTED] This application cannot be submitted yet:")
        for e in errors:
            print(f"   - {e}")
        return

    application.submitted_at = datetime.now()
    store.update_application_status(application_id, ApplicationStatus.SUBMITTED)
    print(f"[OK] Application {application_id} submitted at {application.submitted_at}.")


def update_status():
    print("\n--- Update Application Status ---")
    application_id = prompt_free_text("Application ID", required=True)
    try:
        store.get_application(application_id)
    except NotFoundError as e:
        print(f"  ! {e}")
        return
    new_status = prompt_enum("New status", ApplicationStatus)
    store.update_application_status(application_id, new_status)
    print(f"[OK] Application {application_id} status set to: {new_status.value}")


def log_score():
    print("\n--- Log Evaluation Score ---")
    application_id = prompt_free_text("Application ID", required=True)
    try:
        store.get_application(application_id)
    except NotFoundError as e:
        print(f"  ! {e}")
        return
    score = prompt_float("Evaluation score (0-100)", validate_evaluation_score)
    store.update_evaluation_score(application_id, score)
    print(f"[OK] Application {application_id} scored {score}.")


def search_menu():
    print("\n--- Search Applications ---")
    print("  1. By applicant name")
    print("  2. By status")
    print("  3. By scholarship type")
    print("  4. By GWA range")
    print("  5. Advanced (name + status + scholarship type)")
    choice = input("Choose a number: ").strip()

    if choice == "1":
        keyword = input("Name keyword: ").strip()
        results = search_by_name(store, keyword)
    elif choice == "2":
        status = prompt_enum("Status", ApplicationStatus)
        results = search_by_status(store, status)
    elif choice == "3":
        s_type = prompt_enum("Scholarship type", ScholarshipType)
        results = search_by_scholarship_type(store, s_type)
    elif choice == "4":
        min_gwa = prompt_float("Minimum GWA")
        max_gwa = prompt_float("Maximum GWA")
        results = search_by_gwa_range(store, min_gwa, max_gwa)
    elif choice == "5":
        keyword = input("Name keyword (blank to skip): ").strip() or None
        results = advanced_search(store, name_keyword=keyword)
    else:
        print("  ! Invalid choice.")
        return

    if not results:
        print("No matching applications found.")
        return
    print(f"\n{len(results)} result(s):")
    for a in results:
        print(f"  {a.application_id} | {a.applicant.full_name()} | {a.program.grant_name} "
              f"| {a.status.value} | GWA {a.academic_background.gwa}")


def view_all():
    applications = store.list_applications()
    if not applications:
        print("No applications yet.")
        return
    print(f"\n{len(applications)} application(s) on file:")
    for a in applications:
        print(f"  {a.application_id} | {a.applicant.full_name()} | {a.program.grant_name} "
              f"| {a.status.value} | Score: {a.evaluation_score}")


MENU = """
==================================================
   SCHOLARSHIP APPLICATION SYSTEM
==================================================
 1. Register New Applicant
 2. Register Scholarship Program
 3. View Scholarship Programs
 4. Create Application
 5. Check Application Eligibility
 6. Submit Application (runs validation)
 7. Update Application Status
 8. Log Evaluation Score
 9. Search Applications
10. View All Applications
11. Exit
==================================================
"""

ACTIONS = {
    "1": register_applicant,
    "2": register_program,
    "3": view_programs,
    "4": create_application,
    "5": check_eligibility_menu,
    "6": submit_application,
    "7": update_status,
    "8": log_score,
    "9": search_menu,
    "10": view_all,
}


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "11":
            print("Goodbye.")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("  ! Invalid option.")
            continue
        try:
            action()
        except DuplicateIDError as e:
            print(f"  ! {e}")


if __name__ == "__main__":
    main()