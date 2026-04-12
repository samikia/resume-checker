import re

from resume_checker.utils import clean_text

_HEADERS = ["education", "تحصیلات", "سوابق تحصیلی"]

# Patterns ordered from most specific to least specific
_FIELD_PATTERNS = [
    # Explicit keywords: "رشته: ...", "major: ...", "field of study: ..."
    r'(?:رشته|گرایش|field(?:\s+of\s+study)?|major)\s*[:\-]?\s*([^\n\r]+)',
    # "degree in X" / "Bachelor of Science in X" / "B.Sc. in X"
    r'(?:degree|bachelor|master|b\.?s\.?c\.?|m\.?s\.?c\.?|ph\.?d\.?|دکتری|کارشناسی|کارشناسی ارشد)'
    r'(?:\s+of\s+\w+)?\s+in\s+([^\n\r,]+)',
    # "Bachelor of X" / "Master of X" (without "in")
    r'(?:bachelor|master)\s+of\s+([^\n\r,|]+)',
    # "M.Sc., Field Name" / "B.Sc., Field Name" (comma-separated)
    r'(?:b\.?s\.?c\.?|m\.?s\.?c\.?|ph\.?d\.?)\s*[.,]\s*([A-Za-z][A-Za-z\s]+)',
    # "Undergraduate/Graduate, University, \n Field" pattern — field on next line
    r'(?:undergraduate|graduate|کارشناسی|کارشناسی ارشد)[,\s]+[^\n]+\n\s*([A-Za-z][A-Za-z\s]+?)(?:\n|\d)',
]


def extract_education_field(text: str) -> str | None:
    """Extract field of study from education section."""
    text_lower = text.lower()
    for header in _HEADERS:
        pos = text_lower.find(header)
        if pos != -1:
            snippet = text[pos : pos + 700]
            for pattern in _FIELD_PATTERNS:
                match = re.search(pattern, snippet, re.I)
                if match:
                    field = match.group(1).strip()
                    # Skip if it's just a year, GPA, or too short
                    if len(field) < 3 or re.match(r'^[\d.]+', field):
                        continue
                    # Clean trailing punctuation, dates, GPA
                    field = re.sub(r'\s*[,|]\s*\d{4}.*$', '', field)
                    field = re.sub(r'\s*GPA.*$', '', field, flags=re.I)
                    field = field.strip(' ,.-–')
                    if len(field) >= 3:
                        return clean_text(field)
    return None
