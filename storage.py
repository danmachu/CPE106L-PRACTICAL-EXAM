"""
storage.py
In-memory data store for the Scholarship Application System.
No external database — data lives only for the runtime of the program.
"""

import itertools
from typing import Dict, List

from models import Applicant, ScholarshipProgram, Application


class DuplicateIDError(Exception):
    pass


class NotFoundError(Exception):
    pass


class DataStore:
    """Central in-memory repository for applicants, programs, and applications."""

    def __init__(self):
        self._applicants: Dict[str, Applicant] = {}
        self._programs: Dict[str, ScholarshipProgram] = {}
        self._applications: Dict[str, Application] = {}
        self._applicant_id_counter = itertools.count(1)
        self._application_id_counter = itertools.count(1)
        self._program_id_counter = itertools.count(1)

    # -- ID generation --------------------------------------------------
    def generate_applicant_id(self) -> str:
        return f"APP-{next(self._applicant_id_counter):05d}"

    def generate_application_id(self) -> str:
        return f"SCH-{next(self._application_id_counter):05d}"

    def generate_program_id(self) -> str:
        return f"PRG-{next(self._program_id_counter):03d}"

    # -- Applicants -------------------------------------------------------
    def add_applicant(self, applicant: Applicant) -> None:
        if applicant.applicant_id in self._applicants:
            raise DuplicateIDError(f"Applicant ID '{applicant.applicant_id}' already exists.")
        self._applicants[applicant.applicant_id] = applicant

    def get_applicant(self, applicant_id: str) -> Applicant:
        try:
            return self._applicants[applicant_id]
        except KeyError:
            raise NotFoundError(f"No applicant with ID '{applicant_id}'.")

    def list_applicants(self) -> List[Applicant]:
        return list(self._applicants.values())

    # -- Scholarship Programs ----------------------------------------------
    def add_program(self, program: ScholarshipProgram) -> None:
        if program.program_id in self._programs:
            raise DuplicateIDError(f"Program ID '{program.program_id}' already exists.")
        self._programs[program.program_id] = program

    def get_program(self, program_id: str) -> ScholarshipProgram:
        try:
            return self._programs[program_id]
        except KeyError:
            raise NotFoundError(f"No scholarship program with ID '{program_id}'.")

    def list_programs(self) -> List[ScholarshipProgram]:
        return list(self._programs.values())

    # -- Applications --------------------------------------------------------
    def add_application(self, application: Application) -> None:
        if application.application_id in self._applications:
            raise DuplicateIDError(f"Application ID '{application.application_id}' already exists.")
        self._applications[application.application_id] = application

    def get_application(self, application_id: str) -> Application:
        try:
            return self._applications[application_id]
        except KeyError:
            raise NotFoundError(f"No application with ID '{application_id}'.")

    def list_applications(self) -> List[Application]:
        return list(self._applications.values())

    def update_application_status(self, application_id: str, new_status) -> Application:
        application = self.get_application(application_id)
        application.status = new_status
        return application

    def update_evaluation_score(self, application_id: str, score: float) -> Application:
        application = self.get_application(application_id)
        application.evaluation_score = score
        return application