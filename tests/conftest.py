from pathlib import Path

import pytest

RESUMES_DIR = Path(__file__).resolve().parent.parent / "resumes"


@pytest.fixture(scope="session")
def pdf_texts() -> dict[str, str]:
    """Load all sample PDF texts once, keyed by first 8 chars of filename."""
    try:
        from resume_checker.pdf import extract_text
    except ImportError:
        pytest.skip("PyMuPDF not installed")

    if not RESUMES_DIR.exists():
        pytest.skip("resumes/ directory not found")

    texts = {}
    for pdf in RESUMES_DIR.glob("*.pdf"):
        texts[pdf.name[:8]] = extract_text(pdf)
    return texts
