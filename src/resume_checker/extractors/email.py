import re


def extract_email(text: str) -> str | None:
    """Extract first email address from resume text."""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None
