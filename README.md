# resume-checker

Extract structured data from PDF resumes (Persian & English) into Excel.

Handles diverse resume formats: different date styles, Unicode dash variants, Shamsi/Gregorian calendars, split-line names, and more.

## Install

```bash
# Requires Python 3.12+
uv sync
```

## Usage

### CLI

```bash
# Process all PDFs in a folder → Excel output
uv run resume-checker ./resumes/

# Custom output path
uv run resume-checker ./resumes/ -o results.xlsx
```

**Output columns:** file_name, name, phone, email, experience_years, education_field, skills, file_path

### As a Library

```python
from resume_checker import extract_all

# Extract all fields from a single PDF
result = extract_all("path/to/resume.pdf")
# Returns: {"name": "...", "phone": "...", "email": "...", "experience_years": 5.0, ...}
```

```python
# Use individual extractors
from resume_checker.extractors import calculate_experience_years, extract_name

text = open("resume.txt").read()  # or use resume_checker.pdf.extract_text()
years = calculate_experience_years(text)
name = extract_name(text)
```

## What It Extracts

| Field | Formats Supported |
|-------|-------------------|
| **Name** | English (Title Case, ALL CAPS), Persian, split across lines, with titles (Mr./مهندس/دکتر) |
| **Phone** | Iranian formats: 09xx, +98, (98), with Persian digits (۰۹۱۲...) |
| **Email** | Standard email regex |
| **Experience** | Explicit ("5 years", "five years", "۳ سال", "Since 2018"), date ranges (2020-2023, April 2022 – Dec 2024, Winter 2021-Winter 2024, 1398-1402 Shamsi) |
| **Education** | Field/major/degree extraction from education section |
| **Skills** | Text from skills/competencies section |

## Experience Calculation

The experience calculator uses two strategies:

1. **Explicit mentions** (checked first, in resume summary/header):
   - Digit: `"5 years"`, `"5+ years of experience"`, `"۳ سال تجربه"`
   - Words: `"five years"`, `"over ten years"`
   - Since: `"Since 2018"`

2. **Date range extraction** (fallback):
   - Extracts all `YYYY - YYYY` ranges from the work section
   - Handles all Unicode dashes (en-dash, em-dash, non-breaking hyphen, etc.)
   - Handles `Month YYYY - Month YYYY` and `Season YYYY - Season YYYY`
   - Handles open-ended ranges (`2024-` = present)
   - Converts Shamsi dates to Gregorian (`1398` → `2019`)
   - **Merges overlapping intervals** to avoid double-counting
   - **Excludes education section** dates

## Running Tests

```bash
uv run pytest -v
```

211 tests covering: utils, experience calculation (explicit years, date ranges, dashes, Shamsi, section detection, word numbers, present keywords), name extraction (merging, titles, forbidden keywords, locations), phone, email, education, skills, and integration tests with 5 real PDFs.

## Project Structure

```
src/resume_checker/
├── __init__.py           # extract_all() public API
├── cli.py                # CLI entry point
├── pdf.py                # PDF text extraction (PyMuPDF)
├── utils.py              # normalize_persian_digits, normalize_dashes, clean_text
└── extractors/
    ├── __init__.py        # re-exports all extractors
    ├── name.py
    ├── phone.py
    ├── email.py
    ├── experience.py
    ├── education.py
    └── skills.py

tests/
├── conftest.py            # shared PDF fixtures
├── test_utils.py
├── test_experience.py
├── test_experience_edge_cases.py
├── test_name_edge_cases.py
├── test_phone_edge_cases.py
├── test_email_edge_cases.py
├── test_education_edge_cases.py
├── test_skills_edge_cases.py
├── test_extractors.py
└── test_integration.py
```
