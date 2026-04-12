import pytest
from unittest.mock import patch

from resume_checker.extractors.experience import calculate_experience_years


class TestExplicitYears:
    """Strategy 1: Explicit year mentions in summary/header area."""

    def test_digit_years_of_experience(self):
        text = "Senior developer with 7 years of experience in Python.\nWORK EXPERIENCE\n..."
        assert calculate_experience_years(text) == 7.0

    def test_digit_plus_years(self):
        text = "Data scientist — 5+ years experience in ML and AI.\nWork Experience\n..."
        assert calculate_experience_years(text) == 5.0

    def test_persian_years(self):
        text = "برنامه‌نویس با ۳ سال تجربه در پایتون\nسوابق شغلی\n..."
        assert calculate_experience_years(text) == 3.0

    def test_word_five_years(self):
        text = "I have over five years of experience in data science.\nWORK EXPERIENCE\n..."
        assert calculate_experience_years(text) == 5.0

    def test_word_ten_years(self):
        text = "Specialist with more than ten years experience.\nWork Experience\n..."
        assert calculate_experience_years(text) == 10.0

    def test_takes_max_not_sum(self):
        text = "I have 8 years of experience overall, including 3 years in management.\nWork Experience\n..."
        assert calculate_experience_years(text) == 8.0

    def test_since_year(self):
        text = "Software Engineer since 2018, specializing in AI.\nWork Experience\n..."
        from datetime import datetime
        expected = datetime.now().year - 2018
        assert calculate_experience_years(text) == expected


class TestDateRangeExtraction:
    """Strategy 2: Date range extraction with interval merging."""

    def test_simple_range(self):
        text = "WORK EXPERIENCE\nSoftware Engineer\n2020 - 2023\n"
        assert calculate_experience_years(text) == 3.0

    def test_consecutive_jobs(self):
        text = "Work Experience\nJob A\n2015 - 2018\nJob B\n2018 - 2022\n"
        assert calculate_experience_years(text) == 7.0

    def test_gap_between_jobs(self):
        text = "Work Experience\nJob A\n2015 - 2017\nJob B\n2020 - 2023\n"
        assert calculate_experience_years(text) == 5.0

    def test_overlapping_jobs(self):
        text = "Work Experience\nJob A\n2018 - 2022\nJob B (freelance)\n2020 - 2023\n"
        assert calculate_experience_years(text) == 5.0

    def test_month_year_format(self):
        text = "Work Experience\nDev at Company\nApril 2020 - December 2023\n"
        assert calculate_experience_years(text) == 3.0

    def test_season_year_format(self):
        text = "Work Experience\nDev\nWinter 2021 - Winter 2024\n"
        assert calculate_experience_years(text) == 3.0

    def test_en_dash(self):
        text = "Work Experience\nEngineer\n2019 \u2013 2022\n"
        assert calculate_experience_years(text) == 3.0

    def test_non_breaking_hyphen(self):
        text = "Work Experience\nEngineer\nApril 2022 \u2011 December 2024\n"
        assert calculate_experience_years(text) == 2.0

    def test_em_dash(self):
        text = "Work Experience\nEngineer\n2019 \u2014 2023\n"
        assert calculate_experience_years(text) == 4.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_open_ended_range(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nEngineer\n2024-\n"
        assert calculate_experience_years(text) == 2.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_present_keyword(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nEngineer\n2020 - present\n"
        assert calculate_experience_years(text) == 6.0


class TestShamsiCalendar:
    """Shamsi (Persian/Solar Hijri) calendar date handling."""

    def test_shamsi_range(self):
        text = "سوابق شغلی\nبرنامه‌نویس\n1398 - 1402\n"
        assert calculate_experience_years(text) == 4.0

    def test_shamsi_in_work_section(self):
        text = "Work Experience\nDeveloper\n1395 - 1400\n"
        assert calculate_experience_years(text) == 5.0


class TestSectionDetection:
    """Ensure education dates are excluded and section headers detected properly."""

    def test_education_excluded(self):
        text = (
            "Work Experience\n"
            "Developer\n2020 - 2023\n"
            "Education\n"
            "BSc Computer Science\n2012 - 2016\n"
        )
        assert calculate_experience_years(text) == 3.0

    def test_experience_in_sentence_not_header(self):
        text = (
            "I have great experience in software development.\n"
            "Education\n"
            "BSc\n2010 - 2014\n"
            "Work Experience\n"
            "Developer\n2019 - 2023\n"
        )
        assert calculate_experience_years(text) == 4.0

    def test_no_dates_returns_zero(self):
        text = "Ali Normohammadzadeh\nSoftware Engineer\nSkills: Python, Node.js\n"
        assert calculate_experience_years(text) == 0.0


class TestRealPDFs:
    """Integration tests using actual sample PDFs."""

    def test_mahdi_rezaie(self, pdf_texts):
        result = calculate_experience_years(pdf_texts["36bbddeb"])
        assert abs(result - 4.0) <= 1.0

    def test_summary_five_years(self, pdf_texts):
        assert calculate_experience_years(pdf_texts["6e19db3c"]) == 5.0

    def test_ali_no_dates(self, pdf_texts):
        assert calculate_experience_years(pdf_texts["72437f4f"]) == 0.0

    def test_arman_seasonal_dates(self, pdf_texts):
        result = calculate_experience_years(pdf_texts["7ea10b2a"])
        assert abs(result - 5.0) <= 1.0

    def test_amir_since_2018(self, pdf_texts):
        result = calculate_experience_years(pdf_texts["f24a53dd"])
        assert abs(result - 8.0) <= 1.0
