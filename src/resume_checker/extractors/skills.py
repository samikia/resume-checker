from resume_checker.utils import clean_text

_HEADERS = ["skills", "مهارت‌ها", "competencies"]


def extract_skills(text: str) -> str:
    """Extract skills section text (first 400 chars)."""
    text_lower = text.lower()
    for h in _HEADERS:
        pos = text_lower.find(h)
        if pos != -1:
            return clean_text(text[pos : pos + 500].replace(h, "").strip()[:400])
    return ""
