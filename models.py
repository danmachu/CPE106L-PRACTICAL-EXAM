"""
models.py
Data models for the Scholarship Application System.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations (controlled vocabularies)
# ---------------------------------------------------------------------------

class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class SchoolType(Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"


class EmploymentStatus(Enum):
    EMPLOYED = "Employed"
    UNEMPLOYED = "Unemployed"
    SELF_EMPLOYED = "Self-Employed"
    OFW = "Overseas Filipino Worker"
    RETIRED = "Retired"
    DECEASED = "Deceased"


class ScholarshipType(Enum):
    ACADEMIC_MERIT = "Academic Merit"
    FINANCIAL_NEED = "Financial Need-Based"
    ATHLETIC_TALENT = "Athletic/Talent"
    WORKING_STUDENT = "Working Student"


class ApplicationStatus(Enum):
    DRAFT = "Draft / Incomplete"
    SUBMITTED = "Submitted / Pending Verification"
    UNDER_EVALUATION = "Under Evaluation"
    APPROVED = "Approved / Awarded"
    REJECTED = "Rejected / Disqualified"


# ---------------------------------------------------------------------------
# Section 1: Applicant Personal Profile
# ---------------------------------------------------------------------------

@dataclass
class Applicant:
    applicant_id: str                  # system-generated, or LRN / Institutional ID
    first_name: str
    last_name: str
    middle_name: str = ""
    suffix: str = ""                   # e.g. Jr., III
    email: str = ""
    mobile_number: str = ""
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    permanent_address: str = ""

    def full_name(self) -> str:
        parts = [self.last_name + ",", self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)


# ---------------------------------------------------------------------------
# Section 2: Academic Background
# ---------------------------------------------------------------------------

@dataclass
class AcademicBackground:
    year_level: str = ""                # Current Year/Grade Level
    program: str = ""                   # Enrolled Course/Program/Strand
    school_name: str = ""
    school_type: Optional[SchoolType] = None
    gwa: Optional[float] = None         # 1.0 (highest) - 5.0 (lowest)
    tor_file_path: str = ""             # uploaded TOR / Form 138


# ---------------------------------------------------------------------------
# Section 3: Financial & Socio-Economic Status
# ---------------------------------------------------------------------------

@dataclass
class FinancialProfile:
    household_monthly_income: Optional[float] = None
    father_name: str = ""
    father_occupation: str = ""
    father_employment_status: Optional[EmploymentStatus] = None
    mother_name: str = ""
    mother_occupation: str = ""
    mother_employment_status: Optional[EmploymentStatus] = None
    guardian_name: str = ""
    guardian_occupation: str = ""
    guardian_employment_status: Optional[EmploymentStatus] = None
    supporting_document_paths: list = field(default_factory=list)  # ITR, Indigency, Tax Exemption


# ---------------------------------------------------------------------------
# Section 4: Scholarship Program Profile (The Grant)
# ---------------------------------------------------------------------------

@dataclass
class ScholarshipProgram:
    program_id: str
    grant_name: str
    provider: str
    scholarship_type: ScholarshipType
    tuition_allowance: float = 0.0
    monthly_stipend: float = 0.0
    book_allowance: float = 0.0

    # -- Human-readable, transcribed straight from the source page --
    benefits_description: list = field(default_factory=list)        # exact benefit bullets
    eligibility_criteria: list = field(default_factory=list)         # exact requirement bullets (incl. non-checkable ones)
    required_documents: list = field(default_factory=list)           # documents applicant must submit
    grantee_responsibilities: list = field(default_factory=list)     # obligations to KEEP the grant, post-award
    application_period_notes: list = field(default_factory=list)     # submission window / method, as published

    # -- Structured, machine-checkable eligibility fields (subset of the above) --
    eligible_year_levels: list = field(default_factory=list)         # e.g. ["Grade 12", "Incoming Freshman"]
    eligible_programs_keywords: list = field(default_factory=list)   # e.g. ["Engineering", "Architecture"]
    max_household_income: Optional[float] = None                     # annual cap, Php
    max_gwa_1to5: Optional[float] = None                             # only for criteria stated on the 1.0-5.0 college scale

    def total_coverage(self) -> float:
        return self.tuition_allowance + self.monthly_stipend + self.book_allowance


# ---------------------------------------------------------------------------
# Section 5: Application Metadata & Operational Controls
# ---------------------------------------------------------------------------

@dataclass
class Application:
    application_id: str
    applicant: Applicant
    academic_background: AcademicBackground
    financial_profile: FinancialProfile
    program: ScholarshipProgram
    opening_date: Optional[date] = None
    submission_deadline: Optional[date] = None
    submitted_at: Optional[datetime] = None   # timestamp of actual submission
    status: ApplicationStatus = ApplicationStatus.DRAFT
    evaluation_score: Optional[float] = None  # reviewer's final score, 0-100