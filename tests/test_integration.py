"""Integration tests: extract_all and real PDF end-to-end."""

import pytest
from pathlib import Path

from resume_checker import extract_all
from resume_checker.extractors import (
    extract_name,
    extract_phone,
    extract_email,
    calculate_experience_years,
    extract_education_field,
    extract_skills,
)


class TestExtractAll:
    """End-to-end tests using extract_all on real PDFs."""

    @pytest.fixture(autouse=True)
    def _check_pdfs(self, pdf_texts):
        self.pdf_texts = pdf_texts

    def _get_pdf_path(self, prefix):
        resumes_dir = Path(__file__).resolve().parent.parent / "resumes"
        for pdf in resumes_dir.glob("*.pdf"):
            if pdf.name.startswith(prefix):
                return pdf
        pytest.skip(f"PDF starting with {prefix} not found")

    def test_extract_all_returns_all_keys(self):
        pdf = self._get_pdf_path("36bbddeb")
        result = extract_all(pdf)
        expected_keys = {"file_name", "name", "phone", "email",
                         "experience_years", "education_field", "skills", "file_path"}
        assert set(result.keys()) == expected_keys

    def test_extract_all_file_name(self):
        pdf = self._get_pdf_path("36bbddeb")
        result = extract_all(pdf)
        assert result["file_name"].endswith(".pdf")

    def test_extract_all_file_path(self):
        pdf = self._get_pdf_path("36bbddeb")
        result = extract_all(pdf)
        assert Path(result["file_path"]).exists()

    def test_extract_all_experience_is_numeric(self):
        pdf = self._get_pdf_path("36bbddeb")
        result = extract_all(pdf)
        assert isinstance(result["experience_years"], (int, float))


class TestRealPDFsFullExtraction:
    """Verify all extractors produce reasonable results on real PDFs."""

    def test_mahdi_full(self, pdf_texts):
        text = pdf_texts["36bbddeb"]
        assert extract_name(text) is not None
        assert extract_email(text) is not None
        assert "gmail" in extract_email(text)
        assert extract_phone(text) is not None
        assert 3 <= calculate_experience_years(text) <= 5

    def test_summary_resume_full(self, pdf_texts):
        text = pdf_texts["6e19db3c"]
        assert calculate_experience_years(text) == 5.0
        assert extract_email(text) is not None

    def test_ali_full(self, pdf_texts):
        text = pdf_texts["72437f4f"]
        assert extract_name(text) is not None
        assert calculate_experience_years(text) == 0.0
        assert extract_phone(text) is not None

    def test_arman_full(self, pdf_texts):
        text = pdf_texts["7ea10b2a"]
        name = extract_name(text)
        assert name is not None
        assert extract_email(text) is not None
        assert "gmail" in extract_email(text)
        assert 4 <= calculate_experience_years(text) <= 6

    def test_amir_full(self, pdf_texts):
        text = pdf_texts["f24a53dd"]
        assert extract_name(text) is not None
        assert extract_email(text) is not None
        assert extract_phone(text) is not None
        assert 7 <= calculate_experience_years(text) <= 9


class TestExtractorImports:
    """Verify all public APIs are importable."""

    def test_extractors_package(self):
        from resume_checker.extractors import (
            extract_name,
            extract_phone,
            extract_email,
            calculate_experience_years,
            extract_education_field,
            extract_skills,
        )
        assert callable(extract_name)
        assert callable(extract_phone)
        assert callable(extract_email)
        assert callable(calculate_experience_years)
        assert callable(extract_education_field)
        assert callable(extract_skills)

    def test_top_level_extract_all(self):
        from resume_checker import extract_all
        assert callable(extract_all)
