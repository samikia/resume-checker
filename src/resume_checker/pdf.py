from pathlib import Path

import fitz


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF file, joining pages with newlines."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return text
