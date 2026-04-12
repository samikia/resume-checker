import unittest
from unittest.mock import patch
from pyMuPDF import calculate_experience_years


class TestExplicitYears(unittest.TestCase):
    """Strategy 1: Explicit year mentions in summary/header area."""

    def test_digit_years_of_experience(self):
        text = "Senior developer with 7 years of experience in Python.\nWORK EXPERIENCE\n..."
        self.assertEqual(calculate_experience_years(text), 7.0)

    def test_digit_plus_years(self):
        text = "Data scientist — 5+ years experience in ML and AI.\nWork Experience\n..."
        self.assertEqual(calculate_experience_years(text), 5.0)

    def test_persian_years(self):
        text = "برنامه‌نویس با ۳ سال تجربه در پایتون\nسوابق شغلی\n..."
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_word_five_years(self):
        text = "I have over five years of experience in data science.\nWORK EXPERIENCE\n..."
        self.assertEqual(calculate_experience_years(text), 5.0)

    def test_word_ten_years(self):
        text = "Specialist with more than ten years experience.\nWork Experience\n..."
        self.assertEqual(calculate_experience_years(text), 10.0)

    def test_takes_max_not_sum(self):
        """If summary mentions both '8 years' and '3 years', take the max."""
        text = "I have 8 years of experience overall, including 3 years in management.\nWork Experience\n..."
        self.assertEqual(calculate_experience_years(text), 8.0)

    def test_since_year(self):
        """'Since 2018' should calculate from that year to current year."""
        text = "Software Engineer since 2018, specializing in AI.\nWork Experience\n..."
        from datetime import datetime
        expected = datetime.now().year - 2018
        self.assertEqual(calculate_experience_years(text), expected)


class TestDateRangeExtraction(unittest.TestCase):
    """Strategy 2: Date range extraction with interval merging."""

    def test_simple_range(self):
        text = "WORK EXPERIENCE\nSoftware Engineer\n2020 - 2023\n"
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_consecutive_jobs(self):
        text = "Work Experience\nJob A\n2015 - 2018\nJob B\n2018 - 2022\n"
        self.assertEqual(calculate_experience_years(text), 7.0)

    def test_gap_between_jobs(self):
        """Jobs with a gap: should NOT count the gap years."""
        text = "Work Experience\nJob A\n2015 - 2017\nJob B\n2020 - 2023\n"
        self.assertEqual(calculate_experience_years(text), 5.0)

    def test_overlapping_jobs(self):
        """Overlapping jobs should not double-count."""
        text = "Work Experience\nJob A\n2018 - 2022\nJob B (freelance)\n2020 - 2023\n"
        self.assertEqual(calculate_experience_years(text), 5.0)

    def test_month_year_format(self):
        text = "Work Experience\nDev at Company\nApril 2020 - December 2023\n"
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_season_year_format(self):
        text = "Work Experience\nDev\nWinter 2021 - Winter 2024\n"
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_en_dash(self):
        text = "Work Experience\nEngineer\n2019 \u2013 2022\n"
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_non_breaking_hyphen(self):
        text = "Work Experience\nEngineer\nApril 2022 \u2011 December 2024\n"
        self.assertEqual(calculate_experience_years(text), 2.0)

    def test_em_dash(self):
        text = "Work Experience\nEngineer\n2019 \u2014 2023\n"
        self.assertEqual(calculate_experience_years(text), 4.0)

    @patch('pyMuPDF.datetime')
    def test_open_ended_range(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nEngineer\n2024-\n"
        self.assertEqual(calculate_experience_years(text), 2.0)

    @patch('pyMuPDF.datetime')
    def test_present_keyword(self, mock_dt):
        mock_dt.now.return_value.year = 2026
        text = "Work Experience\nEngineer\n2020 - present\n"
        self.assertEqual(calculate_experience_years(text), 6.0)


class TestShamsiCalendar(unittest.TestCase):
    """Shamsi (Persian/Solar Hijri) calendar date handling."""

    def test_shamsi_range(self):
        text = "سوابق شغلی\nبرنامه‌نویس\n1398 - 1402\n"
        # 1398 → 2019, 1402 → 2023 → 4 years
        self.assertEqual(calculate_experience_years(text), 4.0)

    def test_shamsi_mixed_should_not_happen(self):
        """Pure shamsi range in work section."""
        text = "Work Experience\nDeveloper\n1395 - 1400\n"
        # 1395 → 2016, 1400 → 2021 → 5 years
        self.assertEqual(calculate_experience_years(text), 5.0)


class TestSectionDetection(unittest.TestCase):
    """Ensure education dates are excluded and section headers are detected properly."""

    def test_education_excluded(self):
        """Education dates after work section should not be counted."""
        text = (
            "Work Experience\n"
            "Developer\n2020 - 2023\n"
            "Education\n"
            "BSc Computer Science\n2012 - 2016\n"
        )
        self.assertEqual(calculate_experience_years(text), 3.0)

    def test_experience_in_sentence_not_header(self):
        """'experience' in a sentence should not be treated as a section header."""
        text = (
            "I have great experience in software development.\n"
            "Education\n"
            "BSc\n2010 - 2014\n"
            "Work Experience\n"
            "Developer\n2019 - 2023\n"
        )
        self.assertEqual(calculate_experience_years(text), 4.0)

    def test_no_dates_returns_zero(self):
        text = "Ali Normohammadzadeh\nSoftware Engineer\nSkills: Python, Node.js\n"
        self.assertEqual(calculate_experience_years(text), 0.0)


class TestRealPDFs(unittest.TestCase):
    """Integration tests using actual sample PDFs."""

    @classmethod
    def setUpClass(cls):
        try:
            import fitz
            from pathlib import Path
            cls.pdf_texts = {}
            for pdf in Path('resumes').glob('*.pdf'):
                doc = fitz.open(pdf)
                text = '\n'.join(page.get_text('text') for page in doc)
                doc.close()
                cls.pdf_texts[pdf.name[:8]] = text
            cls.has_pdfs = len(cls.pdf_texts) > 0
        except ImportError:
            cls.has_pdfs = False

    def _get_text(self, prefix):
        if not self.has_pdfs:
            self.skipTest("PyMuPDF not installed or PDFs not found")
        for key, text in self.pdf_texts.items():
            if key.startswith(prefix):
                return text
        self.skipTest(f"PDF starting with {prefix} not found")

    def test_mahdi_rezaie(self):
        """Mahdi: April 2021–May 2025 and April 2022–Dec 2024 (overlapping) → ~4 years"""
        text = self._get_text('36bbddeb')
        result = calculate_experience_years(text)
        self.assertAlmostEqual(result, 4.0, delta=1.0)

    def test_summary_five_years(self):
        """Resume with 'over five years of experience' in summary → 5"""
        text = self._get_text('6e19db3c')
        result = calculate_experience_years(text)
        self.assertEqual(result, 5.0)

    def test_ali_no_dates(self):
        """Ali: no date ranges → 0"""
        text = self._get_text('72437f4f')
        result = calculate_experience_years(text)
        self.assertEqual(result, 0.0)

    def test_arman_seasonal_dates(self):
        """Arman: Winter 2021–present (seasonal format) → ~5 years"""
        text = self._get_text('7ea10b2a')
        result = calculate_experience_years(text)
        self.assertAlmostEqual(result, 5.0, delta=1.0)

    def test_amir_since_2018(self):
        """Amir: Since 2018 in summary → ~8 years"""
        text = self._get_text('f24a53dd')
        result = calculate_experience_years(text)
        self.assertAlmostEqual(result, 8.0, delta=1.0)


if __name__ == '__main__':
    unittest.main()
