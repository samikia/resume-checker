---
name: resume-checker
description: >
  Use this skill whenever working with the resume-checker Python project — running it,
  extending extractors, debugging parsing issues, adding new fields, writing tests,
  or understanding how it processes Persian/English PDF resumes. Trigger on any mention
  of: resume parsing, PDF extraction, experience calculation, Shamsi dates, name/phone/email
  extraction, Excel output, or anything involving `resume_checker`, `extract_all`,
  or the `uv run resume-checker` CLI. Use even for vague requests like "process these
  resumes" or "why is the experience wrong".
---

# resume-checker Skill

A Python tool that extracts structured data from Persian & English PDF resumes into Excel.

## Project Layout

```
src/resume_checker/
├── __init__.py          # Public API: extract_all()
├── cli.py               # CLI entry point
├── pdf.py               # PDF → text via pdfminer
├── utils.py             # Shared helpers
└── extractors/
    ├── name.py
    ├── phone.py
    ├── email.py
    ├── experience.py    # Most complex — two-strategy approach
    ├── education.py
    └── skills.py
tests/                   # pytest, 163+ edge case tests
resumes/                 # Sample PDFs for manual testing
```

## Install & Run

```bash
uv sync                                        # install deps
uv run resume-checker ./resumes/               # process folder → Excel
uv run resume-checker ./resumes/ -o out.xlsx   # custom output path
uv run pytest -v                               # run tests
```

**Output columns:** `file_name`, `name`, `phone`, `email`, `experience_years`, `education_field`, `skills`, `file_path`

## Public API

```python
from resume_checker import extract_all

result = extract_all("path/to/resume.pdf")
# → {"name": "...", "phone": "...", "email": "...", "experience_years": 5.0,
#    "education_field": "...", "skills": "...", "file_name": "...", "file_path": "..."}
```

Individual extractors:

```python
from resume_checker.extractors import (
    extract_name,
    extract_phone,
    extract_email,
    calculate_experience_years,
    extract_education_field,
    extract_skills,
)
text = "..."  # plain text from resume_checker.pdf.extract_text(path)
years = calculate_experience_years(text)
```

## Experience Calculation (two-strategy)

The experience extractor in `extractors/experience.py` works in order:

1. **Explicit mentions** (checked first, in summary/header):
   - `"5 years"`, `"5+ years of experience"`, `"۳ سال تجربه"`, `"Since 2018"`, word numbers (`"five years"`)

2. **Date range fallback** — extracts all date ranges, merges overlapping intervals:
   - `YYYY - YYYY`, `Month YYYY - Month YYYY`, `Season YYYY - Season YYYY`
   - All Unicode dash variants (en-dash, em-dash, non-breaking hyphen)
   - Open-ended ranges: `2024-` = present
   - Shamsi → Gregorian conversion (e.g. `1398` → `2019`)
   - Skips education section dates to avoid double-counting

## Supported Formats

| Field | What's handled |
|-------|---------------|
| **Name** | English title case / ALL CAPS, Persian, split-line, titles (Mr./مهندس/دکتر) |
| **Phone** | Iranian: `09xx`, `+98`, `(98)`, Persian digits (`۰۹۱۲...`) |
| **Email** | Standard regex |
| **Experience** | See above |
| **Education** | Field/major from education section |
| **Skills** | Text block from skills/competencies section |

## Adding a New Extractor

1. Create `src/resume_checker/extractors/my_field.py` with a function `extract_my_field(text: str) -> str`
2. Import and call it in `src/resume_checker/__init__.py` → `extract_all()`
3. Add the column name to `cli.py`'s DataFrame
4. Write tests in `tests/test_my_field.py`

## Debugging Tips

- **Wrong experience years?** Check if explicit mention is being found first — it takes priority. Print `calculate_experience_years(text)` with intermediate logging.
- **Name not extracted?** The extractor looks at the first ~5 lines. Check for leading whitespace or unusual Unicode.
- **Persian text garbled?** `pdf.py` uses `pdfminer` — some scanned PDFs need OCR (not currently supported).
- **Test a single file quickly:**
  ```bash
  uv run python -c "from resume_checker import extract_all; import json; print(json.dumps(extract_all('resumes/sample.pdf'), ensure_ascii=False, indent=2))"
  ```

## Testing Patterns

Tests live in `tests/` and use `pytest`. Edge cases are inline strings, not real PDFs:

```python
def test_experience_shamsi_range():
    text = "کارشناس نرم‌افزار | ۱۳۹۸ - ۱۴۰۲"
    assert calculate_experience_years(text) == pytest.approx(4.0, abs=0.5)
```

Run a specific test file:
```bash
uv run pytest tests/test_experience.py -v
```
