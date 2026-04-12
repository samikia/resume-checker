import re
from datetime import datetime

from resume_checker.utils import normalize_persian_digits, normalize_dashes

_MONTHS = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
_SEASONS = r'(?:spring|summer|fall|autumn|winter)'
_MONTH_OR_SEASON = rf'(?:{_MONTHS}|{_SEASONS})'
_PRESENT_WORDS = [
    'هم‌اکنون', 'هم اکنون', 'تاکنون',  # longer Persian words first to avoid partial replacement
    'اکنون', 'کنون',
    'present', 'ongoing', 'current', 'now',
]
_WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
}

_WORK_HEADERS = [
    "technical experience", "work experience", "professional experience",
    "work experiences", "employment history", "experience",
    "سابقه کاری", "تجربه کاری", "سوابق شغلی", "تجربیات شغلی", "سوابق کاری",
]
_EDU_HEADERS = ["education", "تحصیلات", "سوابق تحصیلی"]


def _shamsi_to_gregorian(year: int) -> int:
    if 1340 <= year <= 1430:
        return year + 621
    return year


def _find_section_start(text_lower: str, headers: list[str]) -> int:
    """Find where a section starts — header must be at/near line start."""
    best = len(text_lower)
    for h in headers:
        for m in re.finditer(re.escape(h.lower()), text_lower):
            pos = m.start()
            line_start = text_lower.rfind('\n', 0, pos)
            prefix = text_lower[line_start + 1 : pos].strip()
            if len(prefix) <= 5:
                best = min(best, pos)
    return best


def _merge_intervals(intervals: list[tuple[int, int]]) -> float:
    """Sort, merge overlapping intervals, return total duration."""
    intervals.sort()
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def calculate_experience_years(text: str) -> float:
    """Calculate total years of work experience from resume text.

    Strategy 1: Look for explicit mentions in the summary area
                (digits, word-numbers, or "since YYYY").
    Strategy 2: Extract date ranges from the work section,
                merge overlapping intervals, sum durations.
    """
    current_year = datetime.now().year
    text_norm = normalize_persian_digits(text)
    text_lower = normalize_dashes(text_norm.lower())

    # --- Strategy 1: Explicit total in summary/header (first ~800 chars) ---
    summary = text_lower[:800]

    # 1a: digit-based ("5 years", "5+ years of experience")
    digit_matches = re.findall(
        r'(\d{1,2})\+?\s*(?:year|years?|سال)\s*(?:of\s*)?(?:experience|تجربه)?',
        summary,
    )
    if digit_matches:
        return round(max(float(m) for m in digit_matches), 1)

    # 1b: word-based ("five years of experience")
    word_pattern = rf'(?:over\s+|more\s+than\s+)?({"|".join(_WORD_TO_NUM)})\s+years?\s*(?:of\s*)?(?:experience)?'
    word_matches = re.findall(word_pattern, summary)
    if word_matches:
        return round(max(_WORD_TO_NUM[w] for w in word_matches), 1)

    # 1c: "Since YYYY"
    since = re.search(r'since\s+(\d{4})', summary)
    if since:
        since_year = int(since.group(1))
        if 1990 <= since_year <= current_year:
            return round(current_year - since_year, 1)

    # --- Strategy 2: Date ranges → merge intervals → sum durations ---
    work_start = _find_section_start(text_lower, _WORK_HEADERS)
    edu_start = _find_section_start(text_lower, _EDU_HEADERS)

    if work_start < len(text_lower):
        work_text = text_lower[work_start:edu_start] if edu_start > work_start else text_lower[work_start:]
    else:
        work_text = text_lower

    for pw in _PRESENT_WORDS:
        work_text = work_text.replace(pw, str(current_year))

    # Pattern 1: [Month/Season] YYYY - [Month/Season] YYYY
    range_pattern = rf'(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})\s*-\s*(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})'
    matches = re.findall(range_pattern, work_text)

    # Pattern 2: [Month/Season] YYYY- (open-ended = present)
    open_pattern = rf'(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})\s*-\s*$'
    open_matches = re.findall(open_pattern, work_text, re.MULTILINE)

    intervals: list[tuple[int, int]] = []

    for start_str, end_str in matches:
        try:
            start = _shamsi_to_gregorian(int(start_str))
            end = _shamsi_to_gregorian(int(end_str))
            if 1990 <= start <= current_year + 1 and start <= end <= current_year + 1:
                intervals.append((start, end))
        except ValueError:
            pass

    for start_str in open_matches:
        try:
            start = _shamsi_to_gregorian(int(start_str))
            if 1990 <= start <= current_year + 1:
                intervals.append((start, current_year))
        except ValueError:
            pass

    if not intervals:
        return 0.0

    return round(_merge_intervals(intervals), 1)
