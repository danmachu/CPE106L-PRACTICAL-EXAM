"""
search.py
Search functions over stored Application records.
Each function takes a DataStore and returns a filtered list of Application objects.
"""

from typing import List, Optional
from models import Application, ApplicationStatus, ScholarshipType


def search_by_name(store, keyword: str) -> List[Application]:
    keyword = keyword.strip().lower()
    return [a for a in store.list_applications() if keyword in a.applicant.full_name().lower()]


def search_by_applicant_id(store, applicant_id: str) -> List[Application]:
    return [a for a in store.list_applications() if a.applicant.applicant_id == applicant_id]


def search_by_status(store, status: ApplicationStatus) -> List[Application]:
    return [a for a in store.list_applications() if a.status == status]


def search_by_scholarship_type(store, scholarship_type: ScholarshipType) -> List[Application]:
    return [a for a in store.list_applications() if a.program.scholarship_type == scholarship_type]


def search_by_program_name(store, keyword: str) -> List[Application]:
    keyword = keyword.strip().lower()
    return [a for a in store.list_applications() if keyword in a.program.grant_name.lower()]


def search_by_gwa_range(store, min_gwa: float, max_gwa: float) -> List[Application]:
    return [
        a for a in store.list_applications()
        if a.academic_background.gwa is not None and min_gwa <= a.academic_background.gwa <= max_gwa
    ]


def search_by_score_range(store, min_score: float, max_score: float) -> List[Application]:
    return [
        a for a in store.list_applications()
        if a.evaluation_score is not None and min_score <= a.evaluation_score <= max_score
    ]


def advanced_search(
    store,
    name_keyword: Optional[str] = None,
    status: Optional[ApplicationStatus] = None,
    scholarship_type: Optional[ScholarshipType] = None,
    min_gwa: Optional[float] = None,
    max_gwa: Optional[float] = None,
) -> List[Application]:
    """Combine multiple optional filters (AND logic) in one call."""
    results = store.list_applications()

    if name_keyword:
        kw = name_keyword.strip().lower()
        results = [a for a in results if kw in a.applicant.full_name().lower()]
    if status is not None:
        results = [a for a in results if a.status == status]
    if scholarship_type is not None:
        results = [a for a in results if a.program.scholarship_type == scholarship_type]
    if min_gwa is not None:
        results = [a for a in results if a.academic_background.gwa is not None and a.academic_background.gwa >= min_gwa]
    if max_gwa is not None:
        results = [a for a in results if a.academic_background.gwa is not None and a.academic_background.gwa <= max_gwa]

    return results