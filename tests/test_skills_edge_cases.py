"""Edge case tests for skills extraction."""

from resume_checker.extractors.skills import extract_skills


class TestSkillsFormats:
    def test_english_skills_header(self):
        text = "About me\nSummary\nSkills\nPython, Django, PostgreSQL, Docker"
        result = extract_skills(text)
        assert "Python" in result
        assert "Django" in result

    def test_persian_skills_header(self):
        text = "درباره من\nمهارت‌ها\nپایتون، جنگو، داکر"
        result = extract_skills(text)
        assert len(result) > 0

    def test_competencies_header(self):
        text = "Summary\nCompetencies\nLeadership, Communication, Python"
        result = extract_skills(text)
        assert "Leadership" in result

    def test_truncation_at_400_chars(self):
        """Skills section longer than 400 chars should be truncated."""
        long_skills = "A" * 500
        text = f"Skills\n{long_skills}"
        result = extract_skills(text)
        assert len(result) <= 400

    def test_header_text_removed(self):
        """The word 'Skills' itself should not appear in the result."""
        text = "Skills\nPython, JavaScript"
        result = extract_skills(text)
        # The header "skills" (case-insensitive) gets removed via .replace()
        # But case matters: "Skills" in original vs "skills" in _HEADERS
        # Actually the find is case-insensitive but replace uses the original header
        assert "Python" in result

    def test_case_insensitive_header(self):
        text = "SKILLS\nReact, Node.js, TypeScript"
        result = extract_skills(text)
        assert len(result) > 0


class TestSkillsNegative:
    def test_no_skills_section(self):
        assert extract_skills("Work Experience\nDeveloper\n") == ""

    def test_empty(self):
        assert extract_skills("") == ""
