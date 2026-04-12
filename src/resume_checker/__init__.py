"""resume-checker — Extract structured data from PDF resumes."""

from pathlib import Path
from typing import Any

from resume_checker.pdf import extract_text
from resume_checker.extractors import (
    extract_name,
    extract_phone,
    extract_email,
    calculate_experience_years,
    extract_education_field,
    extract_skills,
)


def extract_all(pdf_path: str | Path) -> dict[str, Any]:
    """Extract all fields from a single PDF resume.

    Returns a dict with keys: file_name, name, phone, email,
    experience_years, education_field, skills, file_path.
    """
    pdf_path = Path(pdf_path)
    text = extract_text(pdf_path)
    return {
        "file_name": pdf_path.name,
        "name": extract_name(text),
        "phone": extract_phone(text),
        "email": extract_email(text),
        "experience_years": calculate_experience_years(text),
        "education_field": extract_education_field(text),
        "skills": extract_skills(text),
        "file_path": str(pdf_path),
    }
