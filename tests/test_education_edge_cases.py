"""Edge case tests for education field extraction."""

from resume_checker.extractors.education import extract_education_field


class TestEducationFormats:
    def test_degree_in(self):
        text = "Education\nBSc degree in Computer Science\n2018 - 2022"
        result = extract_education_field(text)
        assert result is not None
        assert "Computer Science" in result

    def test_major_keyword(self):
        text = "Education\nMajor: Electrical Engineering\nGPA: 3.8"
        result = extract_education_field(text)
        assert result is not None
        assert "Electrical Engineering" in result

    def test_field_keyword(self):
        text = "Education\nField of Study: Data Science\n2020"
        result = extract_education_field(text)
        assert result is not None

    def test_persian_رشته(self):
        text = "تحصیلات\nرشته: مهندسی کامپیوتر\nدانشگاه تهران"
        result = extract_education_field(text)
        assert result is not None

    def test_persian_گرایش(self):
        text = "تحصیلات\nگرایش: نرم‌افزار\nدانشگاه صنعتی"
        result = extract_education_field(text)
        assert result is not None

    def test_persian_header_سوابق_تحصیلی(self):
        text = "سوابق تحصیلی\nرشته: فیزیک\nدانشگاه شریف"
        result = extract_education_field(text)
        assert result is not None


class TestEducationNegative:
    def test_no_education_section(self):
        assert extract_education_field("Work Experience\nDeveloper\n") is None

    def test_education_without_field(self):
        """Education section exists but no field/major/degree keyword."""
        text = "Education\nUniversity of Tehran\n2018 - 2022\nGPA: 3.5"
        assert extract_education_field(text) is None

    def test_empty(self):
        assert extract_education_field("") is None
