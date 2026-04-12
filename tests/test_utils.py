"""Tests for resume_checker.utils — shared text normalization utilities."""

import pytest

from resume_checker.utils import normalize_persian_digits, normalize_dashes, clean_text


class TestNormalizePersianDigits:
    def test_basic_conversion(self):
        assert normalize_persian_digits("۰۱۲۳۴۵۶۷۸۹") == "0123456789"

    def test_mixed_text_and_digits(self):
        assert normalize_persian_digits("سال ۱۴۰۲") == "سال 1402"

    def test_already_ascii(self):
        assert normalize_persian_digits("2023") == "2023"

    def test_empty_string(self):
        assert normalize_persian_digits("") == ""

    def test_no_digits(self):
        assert normalize_persian_digits("hello world") == "hello world"

    def test_mixed_persian_and_ascii_digits(self):
        assert normalize_persian_digits("۲۰۲3") == "2023"

    def test_phone_number_persian(self):
        assert normalize_persian_digits("۰۹۱۲۱۲۳۴۵۶۷") == "09121234567"


class TestNormalizeDashes:
    """Every Unicode dash variant should become ASCII hyphen (U+002D)."""

    @pytest.mark.parametrize("dash,name", [
        ("\u002D", "hyphen-minus"),
        ("\u2010", "hyphen"),
        ("\u2011", "non-breaking hyphen"),
        ("\u2012", "figure dash"),
        ("\u2013", "en dash"),
        ("\u2014", "em dash"),
        ("\u2015", "horizontal bar"),
        ("\u2212", "minus sign"),
        ("\uFE58", "small em dash"),
        ("\uFE63", "small hyphen-minus"),
        ("\uFF0D", "fullwidth hyphen-minus"),
    ])
    def test_dash_variant(self, dash, name):
        assert normalize_dashes(f"2020{dash}2023") == "2020-2023", f"Failed for {name}"

    def test_multiple_different_dashes(self):
        text = "2020\u20132023 and 2018\u20142020"
        assert normalize_dashes(text) == "2020-2023 and 2018-2020"

    def test_no_dashes(self):
        assert normalize_dashes("hello world") == "hello world"

    def test_empty(self):
        assert normalize_dashes("") == ""


class TestCleanText:
    def test_removes_control_chars(self):
        assert clean_text("hello\x00world") == "helloworld"

    def test_removes_zero_width_chars(self):
        assert clean_text("hello\u200Bworld") == "helloworld"

    def test_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_none_returns_empty(self):
        # clean_text checks `if not text` which covers None-like falsy
        assert clean_text("") == ""

    def test_normal_text_unchanged(self):
        assert clean_text("John Doe") == "John Doe"

    def test_persian_text_preserved(self):
        # Normal Persian chars should be kept (zero-width non-joiner removed though)
        result = clean_text("علی محمدی")
        assert "علی" in result
        assert "محمدی" in result

    def test_line_separator_removed(self):
        assert clean_text("line1\u2028line2") == "line1line2"

    def test_paragraph_separator_removed(self):
        assert clean_text("para1\u2029para2") == "para1para2"
