import re

from resume_checker.utils import normalize_persian_digits

_PATTERNS = [
    r'\(\+?98\)\s*9\d{2,3}\s*[\d\s-]+',
    r'(\+?98|09)\s*\d{2,3}\s*[\d\s-]+',
    r'09\d{9}',
    r'9\d{9}',
    r'\+98\s?9\d{9}',
    r'09\d{2}\s?\d{3}\s?\d{4}',
]


def extract_phone(text: str) -> str | None:
    """Extract Iranian phone number from resume text."""
    text_norm = normalize_persian_digits(text)
    for pat in _PATTERNS:
        match = re.search(pat, text_norm)
        if match:
            return re.sub(r'[\s\(\)]+', '', match.group(0))
    return None
