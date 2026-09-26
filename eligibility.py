"""
eligibility.py
Checks an applicant's academic/financial profile against a scholarship
program's machine-checkable eligibility fields.

LIMITATION (documented, not silently ignored): some real scholarship
criteria are stated on a Senior High School PERCENTAGE grading scale
(e.g. "SWA of 85% and above"), while this system's AcademicBackground.gwa
is captured on the Philippine college 1.0 (highest) - 5.0 (lowest) scale.
Percentage-based criteria are listed under `eligibility_criteria` as
informational text only and are NOT numerically checked here.
"""

from typing import List, Tuple
from models import Application, ScholarshipProgram


def check_eligibility(application: Application, program: ScholarshipProgram) -> Tuple[bool, List[str]]:
    """Returns (is_eligible, list_of_unmet_reasons). Only checks fields that
    are actually comparable between the applicant's data and the program's
    structured criteria; free-text criteria are informational only."""
    reasons = []
    academic = application.academic_background
    financial = application.financial_profile

    if program.eligible_year_levels:
        if not any(level.lower() in academic.year_level.lower() for level in program.eligible_year_levels):
            reasons.append(
                f"Year/grade level '{academic.year_level}' does not match "
                f"required: {', '.join(program.eligible_year_levels)}"
            )

    if program.eligible_programs_keywords:
        if not any(kw.lower() in academic.program.lower() for kw in program.eligible_programs_keywords):
            reasons.append(
                f"Enrolled program '{academic.program}' does not match required "
                f"keyword(s): {', '.join(program.eligible_programs_keywords)}"
            )

    if program.max_household_income is not None and financial.household_monthly_income is not None:
        annual_income = financial.household_monthly_income * 12
        if annual_income > program.max_household_income:
            reasons.append(
                f"Estimated annual household income (Php {annual_income:,.2f}) "
                f"exceeds the program's cap of Php {program.max_household_income:,.2f}."
            )

    if program.max_gwa_1to5 is not None and academic.gwa is not None:
        if academic.gwa > program.max_gwa_1to5:
            reasons.append(
                f"GWA {academic.gwa} does not meet the required {program.max_gwa_1to5} "
                f"or better (1.0 = highest, 5.0 = lowest)."
            )

    return (len(reasons) == 0), reasons


def list_eligible_programs(store, application: Application):
    """Check one application against every registered program; return
    a list of (program, is_eligible, unmet_reasons) tuples."""
    results = []
    for program in store.list_programs():
        is_eligible, reasons = check_eligibility(application, program)
        results.append((program, is_eligible, reasons))
    return results