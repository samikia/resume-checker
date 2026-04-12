import re

_ALL_DASHES = re.compile(
    r'[\u002D\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uFE58\uFE63\uFF0D]'
)


def normalize_persian_digits(text: str) -> str:
    """Convert Persian/Arabic digits (۰-۹) to ASCII digits (0-9)."""
    table = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(table)


def normalize_dashes(text: str) -> str:
    """Replace all Unicode dash variants with a plain ASCII hyphen."""
    return _ALL_DASHES.sub('-', text)


def clean_text(text: str) -> str:
    """Remove control characters and zero-width Unicode that break Excel."""
    if not text:
        return ""
    text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B\u200C\u200D\u200E\u200F\u2028\u2029]', '', text)
    text = re.sub(r'[\u2000-\u200F\u2028-\u202F]', '', text)
    return text.strip()
