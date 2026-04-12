"""Edge case and stress tests for experience calculation."""

import pytest
from unittest.mock import patch
from datetime import datetime

from resume_checker.extractors.experience import (
    calculate_experience_years,
    _shamsi_to_gregorian,
    _find_section_start,
    _merge_intervals,
)


# ── Internal helpers ──────────────────────────────────────────────────────


class TestShamsiToGregorian:
    def test_standard_conversion(self):
        assert _shamsi_to_gregorian(1402) == 2023

    def test_boundary_low(self):
        assert _shamsi_to_gregorian(1340) == 1961

    def test_boundary_high(self):
        assert _shamsi_to_gregorian(1430) == 2051

    def test_below_range_unchanged(self):
        assert _shamsi_to_gregorian(1339) == 1339

    def test_above_range_unchanged(self):
        assert _shamsi_to_gregorian(1431) == 1431

    def test_gregorian_year_unchanged(self):
        assert _shamsi_to_gregorian(2023) == 2023


class TestMergeIntervals:
    def test_single_interval(self):
        assert _merge_intervals([(2020, 2023)]) == 3

    def test_non_overlapping(self):
        assert _merge_intervals([(2015, 2017), (2020, 2023)]) == 5

    def test_overlapping(self):
        assert _merge_intervals([(2018, 2022), (2020, 2024)]) == 6

    def test_fully_contained(self):
        # (2015,2025) contains (2018,2020) → total = 10
        assert _merge_intervals([(2015, 2025), (2018, 2020)]) == 10

    def test_adjacent(self):
        assert _merge_intervals([(2015, 2018), (2018, 2022)]) == 7

    def test_many_overlapping(self):
        intervals = [(2015, 2017), (2016, 2019), (2018, 2021), (2020, 2023)]
        assert _merge_intervals(intervals) == 8  # 2015-2023

    def test_unsorted_input(self):
        intervals = [(2020, 2023), (2015, 2017)]
        assert _merge_intervals(intervals) == 5

    def test_same_year(self):
        assert _merge_intervals([(2020, 2020)]) == 0

    def test_three_separate_jobs(self):
        intervals = [(2010, 2012), (2014, 2016), (2018, 2020)]
        assert _merge_intervals(intervals) == 6


class TestFindSectionStart:
    def test_finds_header_at_line_start(self):
        text = "summary\nsome text\nwork experience\njob details"
        pos = _find_section_start(text, ["work experience"])
        assert pos == text.index("work experience")

    def test_ignores_header_mid_sentence(self):
        # _find_section_start expects lowercased text (the caller lowercases)
        text = "i have great experience in python\nwork experience\njob"
        pos = _find_section_start(text, ["work experience"])
        assert pos == text.index("work experience")

    def test_returns_text_length_when_not_found(self):
        text = "no headers here"
        pos = _find_section_start(text, ["work experience"])
        assert pos == len(text)

    def test_finds_earliest_header(self):
        text = "experience\nmore text\nwork experience\njob"
        pos = _find_section_start(text, ["work experience", "experience"])
        assert pos == 0  # "experience" comes first

    def test_allows_short_prefix(self):
        """Headers preceded by bullets/emoji (<=5 chars) should still match."""
        text = "intro\n● experience\njob details"
        pos = _find_section_start(text, ["experience"])
        assert pos < len(text)


# ── Edge cases for calculate_experience_years ─────────────────────────────


class TestExperienceEdgeCases:
    def test_empty_string(self):
        assert calculate_experience_years("") == 0.0

    def test_whitespace_only(self):
        assert calculate_experience_years("   \n\n  \t  ") == 0.0

    def test_random_text_no_experience(self):
        assert calculate_experience_years("Lorem ipsum dolor sit amet.") == 0.0

    def test_single_year_same_start_end(self):
        text = "Work Experience\nIntern\n2023 - 2023\n"
        assert calculate_experience_years(text) == 0.0

    def test_very_long_career(self):
        text = "Work Experience\nSenior Dev\n1995 - 2025\n"
        assert calculate_experience_years(text) == 30.0

    def test_future_dates_rejected(self):
        """Dates far in the future should be ignored."""
        text = "Work Experience\nDev\n2050 - 2060\n"
        assert calculate_experience_years(text) == 0.0

    def test_ancient_dates_rejected(self):
        """Dates before 1990 should be ignored."""
        text = "Work Experience\nDev\n1950 - 1960\n"
        assert calculate_experience_years(text) == 0.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_now_keyword(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nDev\n2020 - now\n"
        assert calculate_experience_years(text) == 6.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_current_keyword(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nDev\n2022 - current\n"
        assert calculate_experience_years(text) == 4.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_ongoing_keyword(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nDev\n2021 - ongoing\n"
        assert calculate_experience_years(text) == 5.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_persian_present_اکنون(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "سوابق شغلی\nتوسعه‌دهنده\n2020 - اکنون\n"
        assert calculate_experience_years(text) == 6.0

    @patch('resume_checker.extractors.experience.datetime')
    def test_persian_present_تاکنون(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "سوابق شغلی\nتوسعه‌دهنده\n2021 - تاکنون\n"
        assert calculate_experience_years(text) == 5.0

    def test_explicit_years_in_summary_not_in_body(self):
        """'3 years' in summary should take priority over date ranges."""
        text = (
            "Data Scientist with 3 years of experience.\n"
            "Work Experience\n"
            "Dev at Company A\n2015 - 2025\n"
        )
        assert calculate_experience_years(text) == 3.0

    def test_explicit_year_persian_سال(self):
        text = "مهندس نرم‌افزار با ۶ سال تجربه\nسوابق شغلی\n"
        assert calculate_experience_years(text) == 6.0

    def test_since_future_year_ignored(self):
        """'Since 2090' should not produce negative experience."""
        text = "Developer since 2090.\nWork Experience\n"
        assert calculate_experience_years(text) == 0.0

    def test_since_1989_ignored(self):
        """'Since 1989' is before 1990, should be ignored."""
        text = "Developer since 1989.\nWork Experience\n"
        assert calculate_experience_years(text) == 0.0


class TestAbbreviatedMonths:
    """Abbreviated month names like Jan, Feb, Aug."""

    def test_jan_to_dec(self):
        text = "Work Experience\nDev\nJan 2020 - Dec 2023\n"
        assert calculate_experience_years(text) == 3.0

    def test_aug_to_present(self):
        text = "Work Experience\nDev\nAug 2023 - Aug 2025\n"
        assert calculate_experience_years(text) == 2.0

    def test_mixed_full_and_abbreviated(self):
        text = "Work Experience\nDev\nJanuary 2018 - Sep 2021\n"
        assert calculate_experience_years(text) == 3.0

    def test_feb_mar_apr(self):
        text = "Work Experience\nDev A\nFeb 2019 - Mar 2021\nDev B\nApr 2021 - Apr 2024\n"
        assert calculate_experience_years(text) == 5.0


class TestMultipleWorkSections:
    """Resumes with complex layouts."""

    def test_five_jobs_with_gaps(self):
        text = (
            "Work Experience\n"
            "Job 1\n2010 - 2012\n"
            "Job 2\n2013 - 2015\n"
            "Job 3\n2015 - 2017\n"
            "Job 4\n2019 - 2021\n"
            "Job 5\n2022 - 2024\n"
        )
        # (2010-2012)=2 + (2013-2017)=4 + (2019-2021)=2 + (2022-2024)=2 = 10
        assert calculate_experience_years(text) == 10.0

    def test_education_before_work(self):
        """Education section comes first — should not count those dates."""
        text = (
            "Education\n"
            "BSc\n2008 - 2012\n"
            "MSc\n2012 - 2014\n"
            "Work Experience\n"
            "Dev\n2015 - 2020\n"
        )
        assert calculate_experience_years(text) == 5.0

    def test_persian_work_header(self):
        text = "سابقه کاری\nتوسعه‌دهنده\n1398 - 1402\n"
        assert calculate_experience_years(text) == 4.0

    def test_employment_history_header(self):
        text = "Employment History\nManager\n2016 - 2022\n"
        assert calculate_experience_years(text) == 6.0

    def test_professional_experience_header(self):
        text = "Professional Experience\nLead Dev\n2017 - 2024\n"
        assert calculate_experience_years(text) == 7.0


class TestWordNumbers:
    """All word-to-number conversions."""

    @pytest.mark.parametrize("word,num", [
        ("one", 1), ("two", 2), ("three", 3), ("four", 4), ("five", 5),
        ("six", 6), ("seven", 7), ("eight", 8), ("nine", 9), ("ten", 10),
    ])
    def test_word_number(self, word, num):
        text = f"Engineer with {word} years of experience.\nWork Experience\n"
        assert calculate_experience_years(text) == float(num)

    def test_over_word_number(self):
        text = "Engineer with over seven years experience.\nWork Experience\n"
        assert calculate_experience_years(text) == 7.0

    def test_more_than_word_number(self):
        text = "More than eight years of experience in ML.\nWork Experience\n"
        assert calculate_experience_years(text) == 8.0


class TestShamsiDatesInContext:
    """Shamsi calendar dates in realistic resume contexts."""

    def test_shamsi_multiple_jobs(self):
        text = (
            "سوابق شغلی\n"
            "شرکت الف\n1395 - 1398\n"
            "شرکت ب\n1399 - 1402\n"
        )
        # 1395→2016, 1398→2019 (3yr) + 1399→2020, 1402→2023 (3yr) = 6
        assert calculate_experience_years(text) == 6.0

    def test_shamsi_overlapping(self):
        text = (
            "سوابق شغلی\n"
            "شرکت الف\n1396 - 1400\n"
            "شرکت ب\n1398 - 1402\n"
        )
        # 1396→2017, 1402→2023, overlapping → merged = 6
        assert calculate_experience_years(text) == 6.0

    def test_shamsi_with_education_excluded(self):
        text = (
            "سوابق شغلی\n"
            "توسعه‌دهنده\n1398 - 1402\n"
            "تحصیلات\n"
            "کارشناسی\n1390 - 1394\n"
        )
        assert calculate_experience_years(text) == 4.0
