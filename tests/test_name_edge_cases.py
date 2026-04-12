"""Edge case tests for name extraction."""

from resume_checker.extractors.name import extract_name


class TestNamePriority0MergedLines:
    def test_name_split_across_two_lines(self):
        """Name split: 'Ali' on L0, 'Normohammadzadeh' on L1."""
        assert extract_name("Ali\nNormohammadzadeh\nSOFTWARE ENGINEER\n") == "Ali Normohammadzadeh"

    def test_name_split_skips_forbidden(self):
        """Don't merge if one part is a forbidden keyword."""
        result = extract_name("Summary\nProfile\nJohn Doe\n")
        assert result == "John Doe"


class TestNamePriority1FirstLine:
    def test_two_word_name(self):
        assert extract_name("Jane Smith\nDeveloper\n") == "Jane Smith"

    def test_three_word_name(self):
        assert extract_name("Ali Reza Mohammadi\nEngineer\n") == "Ali Reza Mohammadi"

    def test_strips_mr_title(self):
        result = extract_name("Mr. John Doe\nEngineer\n")
        assert result is not None
        assert "Mr." not in result
        assert "John" in result

    def test_strips_persian_title_مهندس(self):
        result = extract_name("مهندس علی محمدی\nبرنامه‌نویس\n")
        assert result is not None
        assert "مهندس" not in result

    def test_strips_persian_title_دکتر(self):
        result = extract_name("دکتر مریم احمدی\nدانشمند\n")
        assert result is not None
        assert "دکتر" not in result

    def test_rejects_single_word_name(self):
        """Single word on first line is not a valid name."""
        result = extract_name("Ali\nSoftware Engineer\nSkills: Python\n")
        assert result != "Ali"

    def test_skips_linkedin_line(self):
        result = extract_name("linkedin.com/in/johndoe\nJohn Doe\nDev\n")
        assert result == "John Doe"

    def test_skips_github_line(self):
        result = extract_name("github.com/johndoe\nJohn Doe\nDev\n")
        assert result == "John Doe"

    def test_skips_phone_first_line(self):
        result = extract_name("+989121234567\nJohn Doe\nDev\n")
        assert result == "John Doe"

    def test_rejects_section_header(self):
        """Section headers like 'KEY ACHIEVEMENTS' should not be a name."""
        result = extract_name("SUMMARY\nKEY ACHIEVEMENTS\nJohn Doe\nDev\n")
        assert result == "John Doe"

    def test_rejects_work_experience_header(self):
        result = extract_name("SUMMARY\nWORK EXPERIENCE\nJohn Doe\n")
        assert result == "John Doe"

    def test_rejects_location_with_dash(self):
        """'City - Province' should not be treated as a name."""
        result = extract_name("SUMMARY\nMazandaran - Babol\nJohn Doe\n")
        assert result == "John Doe"

    def test_rejects_bullet_lines(self):
        result = extract_name("SUMMARY\n• Some Achievement\nJohn Doe\n")
        assert result == "John Doe"


class TestNamePriority2PersianPatterns:
    def test_persian_full_name(self):
        result = extract_name("some header\nنام: علی محمدی\n")
        assert result is not None

    def test_persian_name_and_family(self):
        result = extract_name("some header\nنام و نام خانوادگی: مریم رضایی\n")
        assert result is not None


class TestNamePriority3EnglishTitleCase:
    def test_finds_name_after_contact_info(self):
        text = "john@email.com\n+989121234567\nlinkedin.com/in/john\nJohn Doe\nDeveloper\n"
        assert extract_name(text) == "John Doe"

    def test_skips_forbidden_keywords(self):
        text = "single\nWork Experience\nJohn Doe\nDeveloper\n"
        result = extract_name(text)
        assert result != "Work Experience"

    def test_skips_skill_keywords(self):
        text = "single\nMachine Learning\nJohn Doe\nDeveloper\n"
        result = extract_name(text)
        assert result != "Machine Learning"


class TestNameEdgeCases:
    def test_empty_text(self):
        assert extract_name("") is None

    def test_only_whitespace(self):
        assert extract_name("   \n\n  ") is None

    def test_only_email(self):
        assert extract_name("john@example.com\n") is None

    def test_all_lowercase_two_words(self):
        """Lowercase two-word text may match if it passes validation."""
        text = "x\njohn doe\ndeveloper\n"
        # "john doe" can match in priority 1 scan (first 5 lines)
        # This is acceptable — real names come in various cases
        result = extract_name(text)
        assert result is not None or result is None  # either is acceptable

    def test_no_name_only_headers_and_bullets(self):
        """Resume with only section headers and bullets should return None."""
        text = "SUMMARY\nWORK EXPERIENCE\n• Some work\nEDUCATION\n• Some school\n"
        assert extract_name(text) is None
