import re

from resume_checker.utils import clean_text

_FORBIDDEN = re.compile(
    r'(skills|interests|hobbies|education|experience|projects|languages|about me|summary|contact|'
    r'درباره من|سوابق شغلی|مهارت|تحصیلات|پروژه|Data Scientist|Machine Learning|'
    r'Signal Processing|Image Processing|Deep Learning|Critical Thinking|Team Work|'
    r'Artificial Intelligence|AI & Computer Vision Developer|Technical Experience)',
    re.I,
)

_SKIP = re.compile(
    r'(\+?98|09|\(\+?98\))\s*\d|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|linkedin|github'
)

_TITLES = re.compile(
    r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس|Data Enthusiast Developer|Data Analyst)',
    re.I,
)


def extract_name(text: str) -> str | None:
    """Extract the person's full name from resume text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Priority 1: first line (usually the name)
    if lines and not _SKIP.search(lines[0]) and not _FORBIDDEN.search(lines[0]):
        cleaned = _TITLES.sub('', lines[0]).strip()
        if len(cleaned.split()) >= 2 and len(cleaned) < 70:
            return clean_text(cleaned)

    # Priority 2: Persian name patterns
    for pat in [
        r'([آ-ی\s]+)\s*(Data Scientist|مهندس|دکتر)?',
        r'نام\s*[:\-]?\s*([آ-ی\s]+)',
        r'نام و نام خانوادگی\s*[:\-]?\s*([آ-ی\s]+)',
    ]:
        match = re.search(pat, text, re.I)
        if match:
            name = match.group(1).strip()
            if len(name.split()) >= 2:
                return clean_text(name)

    # Priority 3: English name (Title Case in first 25 lines)
    for line in lines[:25]:
        if _SKIP.search(line) or _FORBIDDEN.search(line):
            continue
        cleaned = _TITLES.sub('', line).strip()
        if (
            len(cleaned.split()) >= 2
            and len(cleaned) < 70
            and (cleaned.istitle() or any(c.isupper() for c in cleaned))
        ):
            return clean_text(cleaned)

    return None
