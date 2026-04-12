import re

from resume_checker.utils import clean_text

_FORBIDDEN = re.compile(
    r'^(skills|interests|hobbies|education|experience|projects|languages|about me|'
    r'summary|contact|objective|profile|certifications|references|awards|publications|'
    r'key achievements|achievements|work history|career|professional summary|'
    r'work experience|professional experience|employment history|technical experience|'
    r'درباره من|سوابق شغلی|مهارت|تحصیلات|پروژه|Data Scientist|Machine Learning|'
    r'Signal Processing|Image Processing|Deep Learning|Critical Thinking|Team Work|'
    r'Artificial Intelligence|AI & Computer Vision Developer|Technical Experience|'
    r'Software Engineer|Backend Developer|Frontend Developer|Full Stack|DevOps|'
    r'Solutions Architect|Operations)s?$',
    re.I,
)

_FORBIDDEN_CONTAINS = re.compile(
    r'(linkedin|github|stackoverflow|http|www\.|\.com|\.ir|\.org)',
    re.I,
)

_SKIP = re.compile(
    r'(\+?98|09|\(\+?98\))\s*\d|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
)

_TITLES = re.compile(
    r'(mr\.|ms\.|mrs\.|dr\.|مهندس|دکتر|کارشناس|Data Enthusiast Developer|Data Analyst)',
    re.I,
)

_DATE_LIKE = re.compile(
    r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b\s+\d{4}|'
    r'\b(?:january|february|march|april|june|july|august|september|october|november|december)\b\s+\d{4}|'
    r'\b(?:spring|summer|fall|winter)\b\s+\d{4}|'
    r'\bpresent\b|'
    r'\d{4}\s*[-–—‑])',
    re.I,
)


def _is_valid_name(text: str) -> bool:
    """Check if text looks like a person's name, not a section header or junk."""
    words = text.split()
    if len(words) < 2 or len(text) > 50:
        return False
    if _FORBIDDEN.match(text.strip()):
        return False
    if _FORBIDDEN_CONTAINS.search(text):
        return False
    if _DATE_LIKE.search(text):
        return False
    # All-caps short phrases are likely headers, not names (unless 2-3 words only)
    if text.isupper() and len(words) > 3:
        return False
    # Locations: "City - Province" or "City, Country"
    if re.search(r'\s*[-–,]\s*', text) and len(words) <= 4:
        return False
    # Lines starting with bullets are not names
    if text.startswith(('•', '-', '–', '▪', '■', '►', '○', '●', '*')):
        return False
    # Lines that are too long are likely descriptions, not names
    if len(text) > 40:
        return False
    return True


def extract_name(text: str) -> str | None:
    """Extract the person's full name from resume text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Priority 0: Merge consecutive single-word lines at the top
    # (handles names split across lines like "Ali\nNormohammadzadeh")
    if len(lines) >= 2:
        for i in range(min(3, len(lines) - 1)):
            if (
                len(lines[i].split()) == 1
                and len(lines[i + 1].split()) == 1
                and not _SKIP.search(lines[i])
                and not _SKIP.search(lines[i + 1])
                and not _FORBIDDEN.match(lines[i])
                and not _FORBIDDEN.match(lines[i + 1])
                and not _FORBIDDEN_CONTAINS.search(lines[i])
                and not _FORBIDDEN_CONTAINS.search(lines[i + 1])
            ):
                merged = f"{lines[i]} {lines[i + 1]}"
                cleaned = _TITLES.sub('', merged).strip()
                if _is_valid_name(cleaned):
                    return clean_text(cleaned)

    # Priority 1: first non-skip line (usually the name)
    for line in lines[:5]:
        if _SKIP.search(line):
            continue
        cleaned = _TITLES.sub('', line).strip()
        if _is_valid_name(cleaned):
            return clean_text(cleaned)

    # Priority 2: Persian name patterns
    for pat in [
        r'نام و نام خانوادگی\s*[:\-]?\s*([آ-ی\s]+)',
        r'نام\s*[:\-]?\s*([آ-ی\s]+)',
    ]:
        match = re.search(pat, text, re.I)
        if match:
            name = match.group(1).strip()
            if len(name.split()) >= 2:
                return clean_text(name)

    # Priority 3: English name (Title Case in first 25 lines)
    for line in lines[:25]:
        if _SKIP.search(line):
            continue
        cleaned = _TITLES.sub('', line).strip()
        if _is_valid_name(cleaned) and (cleaned.istitle() or any(c.isupper() for c in cleaned)):
            return clean_text(cleaned)

    return None
