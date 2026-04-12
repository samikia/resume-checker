"""Edge case tests for phone extraction."""

from resume_checker.extractors.phone import extract_phone


class TestPhoneFormats:
    def test_plain_09_format(self):
        assert extract_phone("09121234567") == "09121234567"

    def test_with_dashes(self):
        result = extract_phone("0912-123-4567")
        assert result is not None
        assert "0912" in result

    def test_with_spaces(self):
        result = extract_phone("0912 123 4567")
        assert result is not None

    def test_plus98_no_space(self):
        result = extract_phone("+989121234567")
        assert result is not None
        assert "912" in result

    def test_plus98_with_space(self):
        result = extract_phone("+98 9121234567")
        assert result is not None

    def test_parenthesized_country_code(self):
        result = extract_phone("(+98)9121234567")
        assert result is not None

    def test_parenthesized_98_with_space(self):
        result = extract_phone("(98) 912 123 4567")
        assert result is not None

    def test_persian_digits_phone(self):
        result = extract_phone("تلفن: ۰۹۳۵۱۲۳۴۵۶۷")
        assert result is not None
        assert "0935" in result

    def test_mixed_text_and_phone(self):
        result = extract_phone("Contact me at 09121234567 for details")
        assert result is not None
        assert "0912" in result

    def test_phone_in_multiline(self):
        text = "Name: John\nPhone: 09121234567\nEmail: john@test.com"
        result = extract_phone(text)
        assert result is not None


class TestPhoneNegative:
    def test_no_phone(self):
        assert extract_phone("No phone number here") is None

    def test_short_number(self):
        """Numbers too short should not match."""
        assert extract_phone("Call 0912") is None

    def test_empty_string(self):
        assert extract_phone("") is None

    def test_non_iranian_number(self):
        """US format should not match."""
        assert extract_phone("+1 555 123 4567") is None
