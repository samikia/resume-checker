from resume_checker.extractors import (
    extract_name,
    extract_phone,
    extract_email,
    extract_education_field,
    extract_skills,
)


class TestExtractName:
    def test_english_name_first_line(self):
        assert extract_name("John Doe\nSoftware Engineer\n") == "John Doe"

    def test_persian_name(self):
        assert extract_name("علی محمدی\nبرنامه‌نویس\n") is not None

    def test_skips_email_line(self):
        result = extract_name("john@example.com\nJohn Doe\nEngineer\n")
        assert result == "John Doe"

    def test_returns_none_for_empty(self):
        assert extract_name("") is None


class TestExtractPhone:
    def test_standard_format(self):
        assert extract_phone("Call me: 09121234567") == "09121234567"

    def test_with_country_code(self):
        result = extract_phone("Phone: +98 912 123 4567")
        assert result is not None
        assert "912" in result

    def test_persian_digits(self):
        result = extract_phone("تلفن: ۰۹۱۲۱۲۳۴۵۶۷")
        assert result is not None

    def test_no_phone(self):
        assert extract_phone("No phone here") is None


class TestExtractEmail:
    def test_standard_email(self):
        assert extract_email("Email: john@example.com") == "john@example.com"

    def test_no_email(self):
        assert extract_email("No email here") is None


class TestExtractEducation:
    def test_english_education(self):
        text = "Education\nBSc degree in Computer Science\nUniversity of Tehran"
        result = extract_education_field(text)
        assert result is not None

    def test_no_education(self):
        assert extract_education_field("Work Experience\nDeveloper\n") is None


class TestExtractSkills:
    def test_skills_section(self):
        text = "About me\nHello\nSkills\nPython, Django, React, PostgreSQL"
        result = extract_skills(text)
        assert "Python" in result

    def test_no_skills(self):
        assert extract_skills("Just a resume with no relevant section") == ""
