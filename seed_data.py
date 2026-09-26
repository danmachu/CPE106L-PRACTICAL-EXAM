"""
seed_data.py
Scholarship programs transcribed from Mapúa University's published
undergraduate scholarship page:
https://www.mapua.edu.ph/pages/admissions/mapua-scholarships/undergraduate
(transcribed from screenshots of the page, Sep 2026)

  1. E.T. Yuchengco (ETY) Scholarship
  2. Alfonso T. Yuchengco (ATY) Scholarship
  3. Don Tomas Mapúa Scholarship
  4. Academic Scholarship (President's List / Dean's List based)
  5. Mapúa Alumni Australia (MAA) Scholarship
  6. Mapúa Alumni Association - Alberta Chapter (MAAAC) Scholarship
  7. Mapúa Alumni Association of San Diego (MAASD) Scholarship
  8. MIT CE-EnSe Alumni Association, Inc. Scholarship
  9. Southern California Mapúa Alumni (SCMA) Scholarship

Call seed_programs(store) once at startup to pre-load these.
"""

from models import ScholarshipProgram, ScholarshipType


def seed_programs(store) -> None:
    programs = [
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="E.T. Yuchengco (ETY) Scholarship",
            provider="E.T. Yuchengco Foundation / Mapúa CSFA",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            book_allowance=12000.0,
            benefits_description=[
                "Free matriculation fee",
                "Annual stipend of Php 20,000",
                "Annual book allowance of Php 12,000",
            ],
            eligibility_criteria=[
                "Mapúa SHS student with a Semestral Weighted Average of 85% and above, no grade "
                "lower than 85% in any subject (SHS % scale - informational only)",
                "OR Freshman applicant who scored at least 80% in the Mapúa Program Placement "
                "Assessment (MPASS)",
                "Top scorers of the scholarship exam are invited for an interview",
            ],
            required_documents=["MPASS result or SHS grade certification"],
            application_period_notes=[
                "Freshman applicant takes MPASS first (min. 80%); SHS students with SWA 85%+ are "
                "invited directly to the scholarship exam; exam top scorers proceed to interview; "
                "final grantees are the top scorers of exam + interview combined.",
            ],
            grantee_responsibilities=[
                "Maintain a QWA of at least 2.50 or higher every term",
                "Maintain a cumulative GWA of 2.00 or better every end of the academic year",
                "No grades below 3.00 (including PE and NSTP)",
                "Must finish the program within the prescribed number of terms",
                "Must have scholarship validated every enrollment",
            ],
            eligible_year_levels=["Grade 12", "Incoming Freshman"],
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Alfonso T. Yuchengco (ATY) Scholarship",
            provider="Alfonso T. Yuchengco Foundation / Mapúa CSFA",
            scholarship_type=ScholarshipType.FINANCIAL_NEED,
            monthly_stipend=round(40000.0 / 12, 2),
            benefits_description=[
                "40% discount on tuition fee",
                "Annual stipend of Php 40,000",
            ],
            eligibility_criteria=[
                "Must be a graduate of any recognized Public Science High School in the Philippines",
                "Incoming Freshman who scored at least 70% in MPASS",
                "Must be approved as an Income-Based Financial Assistance Program (IBFAP) grantee "
                "(apply for IBFAP first, separately)",
            ],
            required_documents=[
                "IBFAP Application Form",
                "Parents'/Guardian's letter on the family's financial situation, addressed to CSFA",
                "For employed parents: ITR or Certificate of Compensation Payment/Tax Withheld, "
                "Certificate of Employment and Compensation (incl. bonuses/allowances/commissions); "
                "OFWs submit employment contract",
                "For self-employed parents: ITR, business description, income & financial statement",
                "For parents not filing an ITR: letter stating reason for non-filing",
                "Siblings helping with family expenses submit the same financial documents",
                "Proof of utility billing (electricity, water, telephone, etc.)",
                "Photocopy of latest Senior High School report card",
                "Certificate of good moral character",
                "Vicinity sketch of residence showing route from Mapúa, major streets/landmarks, "
                "house marked with an 'X'",
                "Narrative essay (250+ words) on accomplishments, with student portfolio",
            ],
            application_period_notes=[
                "SY 2026-2027: March 2, 2026 - May 15, 2026. Submit to Mapúa CSFA (Intramuros "
                "Campus), Mon-Fri 8AM-5PM, or email scholarships@mapua.edu.ph with subject "
                "'ATY Scholarship Application SY 2026-2027: <Surname>', all requirements in ONE PDF.",
            ],
            grantee_responsibilities=[
                "Maintain a QWA of at least 2.75 per term",
                "Must not have a grade lower than 3.0 in any course",
                "Must enroll in at least 12 academic units every term",
                "Must not shift to another program",
            ],
            eligible_year_levels=["Incoming Freshman"],
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Don Tomas Mapúa Scholarship",
            provider="Mapúa University / CSFA",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            benefits_description=[
                "100% discount in tuition for two (2) consecutive terms (provided no grade below "
                "3.0 in any subject, including PE and NSTP, in the first term)",
            ],
            eligibility_criteria=[
                "Incoming freshmen who graduated 'with Highest Honors' (GWA 98 and above, SHS % "
                "scale - informational only)",
                "Graduated among a batch of at least 60 students",
                "Enrolled in a DepEd-accredited High School in the Philippines or abroad",
                "Passed the Mapúa Program Placement Assessment (MPASS)",
            ],
            required_documents=[
                "Certificate (school dry seal) of 'with highest honors' award, signed by "
                "Principal/Registrar, stating school name/address, contact details, and batch size",
                "Complete Grade 12 report card",
            ],
            application_period_notes=[
                "SY 2026-2027: March 30, 2026 - July 24, 2026. Submit to Mapúa CSFA (Intramuros "
                "Campus), Mon-Fri 8AM-5PM, or email scholarships@mapua.edu.ph with subject "
                "'Don Tomas Mapua UG Scholarship Application SY 2026-2027: <Surname>', all "
                "requirements in ONE PDF.",
            ],
            grantee_responsibilities=[
                "Must validate scholarship on the 2nd term of enrollment if still eligible",
            ],
            eligible_year_levels=["Incoming Freshman"],
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Academic Scholarship",
            provider="Mapúa University / CSFA",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            benefits_description=[
                "President's List, QWA 1.00-1.50: 100% tuition discount",
                "President's List, QWA 1.51-1.75: 50% tuition discount",
                "Only students on the President's List qualify; only Dean's Listers qualify for "
                "the President's List",
            ],
            eligibility_criteria=[
                "Must be on the President's List (which itself requires prior Dean's List standing)",
                "Dean's Listers not on the President's List but in financial need may instead apply "
                "for the separate Need-Based Academic Scholarship (NBAS)",
            ],
            application_period_notes=[
                "Must sign the academic scholarship undertaking at CSFA to avail in the immediate "
                "succeeding term.",
            ],
            grantee_responsibilities=[
                "Must avail immediately in the succeeding term (sign undertaking at CSFA)",
                "On LOA: may still apply upon return if within two succeeding quarters, with "
                "Registrar clearance + Letter of Consideration to CSFA; two successive quarters "
                "on leave waives the right to the scholarship",
                "Grade-encoding disputes must be raised within 1 week of final grades release; no "
                "appeal after that period or after President's/Dean's List release",
                "If not auto-indicated in the GSA, must claim at CSFA within 2 weeks of classes "
                "opening or the scholarship is waived",
            ],
            max_gwa_1to5=1.75,  # outer bound to qualify for at least the 50% tier
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Mapúa Alumni Australia (MAA) Scholarship",
            provider="Mapúa Alumni Australia",
            scholarship_type=ScholarshipType.FINANCIAL_NEED,
            benefits_description=["Full matriculation fee"],
            eligibility_criteria=[
                "Undergraduate student in final year of study",
                "Currently enrolled, in good academic standing (no failing grades)",
                "Annual family income must not exceed Php 700,000",
            ],
            required_documents=[
                "Completed Scholarship Application Form", "2x2 ID picture",
                "Copy of latest Certificate of Matriculation (CM)",
                "Grade Certification from Customer Service of Mapúa",
                "Certificate of Good Moral Character (Prefect of Discipline)",
                "Certificate of Good Health",
                "Photocopy of parent's latest ITR or Affidavit of Non-Filing ITR "
                "(OFWs: employment contract with benefits)",
                "Brief essay on reason for the scholarship",
                "Two recommendation letters (department head/dean and professor)",
            ],
            grantee_responsibilities=[
                "Maintain a GWA of 2.50 or higher per term",
                "Must not obtain a grade lower than 3.0 in any subject",
                "Must provide and keep personal contact information updated",
                "Must validate scholarship at CSFA during enrollment period",
            ],
            eligible_year_levels=["4th Year", "Final Year"],
            max_household_income=700000.0,
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Mapúa Alumni Association - Alberta Chapter (MAAAC) Scholarship",
            provider="Mapúa Alumni Association - Alberta Chapter",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            benefits_description=[
                "Partial tuition fee grant per term by GWA tier: 1.99 and higher -> 75% of tuition; "
                "2.00-2.24 -> 50% of tuition; 2.25-2.50 -> 25% of tuition",
            ],
            eligibility_criteria=[
                "Must be enrolled and at least 2nd year standing",
                "Must be an Engineering student",
                "Must be of good moral character",
                "Must not be enjoying any other scholarship program other than Academic Scholarship",
                "Must be in good academic standing: GWA of at least 2.50 for the last two terms, "
                "no grade lower than 3.0",
            ],
            required_documents=[
                "Completed Scholarship Application Form with 2x2 ID picture",
                "Photocopy of latest Certificate of Matriculation (CM)",
                "Grade Certification from Customer Service of Mapúa",
                "Photocopy of latest ITR of both parents or Affidavit of Not Filing ITR "
                "(OFWs: contract with salary indicated)",
                "Certificate of Good Moral Character (Prefect of Discipline)",
                "Certificate of Good Health",
                "Brief essay stating reasons applicant is deserving of the scholarship",
            ],
            grantee_responsibilities=[
                "Maintain a GWA of 2.50 or higher per term",
                "Must not obtain a grade lower than 3.0 in any subject",
                "Must validate scholarship at CSFA during enrollment period",
            ],
            eligible_year_levels=["2nd Year", "3rd Year", "4th Year"],
            eligible_programs_keywords=["Engineering"],
            max_gwa_1to5=2.50,
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Mapúa Alumni Association of San Diego (MAASD) Scholarship",
            provider="Mapúa Alumni Association of San Diego",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            monthly_stipend=15000.0,  # published as "Php 15,000.00 grant per term"
            benefits_description=["Php 15,000.00 grant per term"],
            eligibility_criteria=[
                "Must be currently enrolled as an Engineering student",
                "Must be at least 2nd year standing",
                "Must have a GWA of at least 2.50 or higher for the last two terms",
                "Must not have failing and incomplete grades for the last two terms",
                "Preferably with Parent's Annual Income not exceeding Php 700,000 (soft preference, "
                "not a hard cap - not machine-enforced)",
            ],
            required_documents=[
                "Completed Scholarship Application Form with 2x2 ID picture",
                "Photocopy of latest Certificate of Matriculation (CM)",
                "Grade Certification from Customer Service of Mapúa",
                "Certificate of Good Moral Character (Prefect of Discipline)",
                "Certificate of Good Health",
                "Photocopy of latest ITR of both parents or Affidavit of Not Filing ITR "
                "(OFWs: contract with salary indicated)",
                "Proof of utility billing",
                "Brief essay stating reasons applicant is deserving of the scholarship",
                "Any other pertinent information the applicant is comfortable disclosing",
            ],
            grantee_responsibilities=[
                "Maintain a GWA of 2.50 or higher per term",
                "Must not obtain a grade lower than 3.0 in any subject",
                "Must validate scholarship at CSFA during enrollment period",
            ],
            eligible_year_levels=["2nd Year", "3rd Year", "4th Year"],
            eligible_programs_keywords=["Engineering"],
            max_gwa_1to5=2.50,
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="MIT CE-EnSe Alumni Association, Inc. Scholarship",
            provider="MIT CE-EnSe Alumni Association, Inc.",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            benefits_description=["Full matriculation fee"],
            eligibility_criteria=[
                "Must be currently enrolled as a BS Civil Engineering or BS Environmental and "
                "Sanitary Engineering student",
                "Must be at least 3rd year standing",
                "Must have a GWA of 2.5 or higher",
                "Must be of good moral character",
                "Must be in good physical condition",
            ],
            required_documents=[
                "Completed Scholarship Application Form with 2x2 ID picture",
                "Grade Certification from Customer Service of Mapúa",
                "Three recommendation letters (Department Head, Dean, or Professors)",
                "Certificate of Good Moral Character (Prefect of Discipline)",
                "Certificate of Good Health",
                "Latest ITR of both parents or Affidavit of Not Filing ITR "
                "(OFWs: contract with salary indicated)",
                "Electricity bill showing applicant's address",
                "Brief essay stating reasons applicant is deserving of the scholarship",
                "Any other pertinent information the applicant is comfortable disclosing",
            ],
            grantee_responsibilities=[],  # not shown/cut off in the source screenshot
            eligible_year_levels=["3rd Year", "4th Year"],
            eligible_programs_keywords=["Civil Engineering", "Environmental and Sanitary Engineering"],
            max_gwa_1to5=2.50,
        ),
        ScholarshipProgram(
            program_id=store.generate_program_id(),
            grant_name="Southern California Mapúa Alumni (SCMA) Scholarship",
            provider="Southern California Mapúa Alumni",
            scholarship_type=ScholarshipType.ACADEMIC_MERIT,
            monthly_stipend=400.0,  # published as "$400 grant per term" (USD)
            benefits_description=["$400 grant per term"],
            eligibility_criteria=[
                "Incoming 3rd or 4th Year Engineering or Architecture student",
                "GWA standing of 2.50 for the last two terms",
                "No failing/incomplete grades; in good health; good moral character",
            ],
            required_documents=[
                "Completed Scholarship Application Form with 2x2 ID picture",
                "Copy of latest Certificate of Matriculation (CM)",
                "Grade Certification from Customer Service of Mapúa",
                "Certificate of Good Moral Character (Prefect of Discipline)",
                "Photocopy of latest ITR of both parents or Affidavit of Not Filing ITR "
                "(OFWs: contract with salary indicated)",
                "Brief essay stating reasons applicant is deserving of the scholarship",
            ],
            grantee_responsibilities=[
                "Maintain a GWA of 2.50 or higher every term",
                "Must not have a grade lower than 3.0 in any course/subject",
                "Must finish the program within the prescribed number of terms",
                "Must visit CSFA before enrollment for validation",
            ],
            eligible_year_levels=["3rd Year", "4th Year"],
            eligible_programs_keywords=["Engineering", "Architecture"],
            max_gwa_1to5=2.50,
        ),
    ]

    for program in programs:
        store.add_program(program)