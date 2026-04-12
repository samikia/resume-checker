import re

from resume_checker.utils import clean_text

_HEADERS = ["education", "تحصیلات", "سوابق تحصیلی"]


def extract_education_field(text: str) -> str | None:
    """Extract field of study from education section."""
    text_lower = text.lower()
    for header in _HEADERS:
        pos = text_lower.find(header)
        if pos != -1:
            snippet = text[pos : pos + 700]
            match = re.search(
                r'(?:رشته|گرایش|field|major|degree in).*?[:\-]?\s*([^\n\r]+)',
                snippet,
                re.I,
            )
            if match:
                return clean_text(match.group(1).strip())
    return None
