"""Edge case tests for email extraction."""

from resume_checker.extractors.email import extract_email


class TestEmailFormats:
    def test_standard(self):
        assert extract_email("email: user@example.com") == "user@example.com"

    def test_with_dots(self):
        assert extract_email("john.doe@company.org") == "john.doe@company.org"

    def test_with_plus(self):
        assert extract_email("user+tag@gmail.com") == "user+tag@gmail.com"

    def test_with_numbers(self):
        assert extract_email("user123@test.io") == "user123@test.io"

    def test_subdomain(self):
        assert extract_email("me@mail.company.co.uk") == "me@mail.company.co.uk"

    def test_first_email_returned(self):
        text = "primary@a.com and secondary@b.com"
        assert extract_email(text) == "primary@a.com"

    def test_email_in_multiline(self):
        text = "Name: John Doe\nEmail: john@example.com\nPhone: 123"
        assert extract_email(text) == "john@example.com"

    def test_uppercase_domain(self):
        assert extract_email("User@Example.COM") == "User@Example.COM"


class TestEmailNegative:
    def test_no_email(self):
        assert extract_email("No email here") is None

    def test_empty(self):
        assert extract_email("") is None

    def test_at_sign_alone(self):
        assert extract_email("user @ example") is None

    def test_no_domain(self):
        assert extract_email("user@") is None
