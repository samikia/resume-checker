import re
import unicodedata

_ALL_DASHES = re.compile(
    r'[\u002D\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uFE58\uFE63\uFF0D]'
)

# Jobinja PDFs render "تا" (meaning "to") as a corrupted sequence:
# an ASCII character + ﺎ (U+FE8E, Arabic Letter Alef isolated form).
# The ASCII char varies by font/glyph mapping (seen: \x1d, H, [).
# The separator is always followed by a space — use that to avoid false positives
# from Arabic shaped glyphs that also end in U+FE8E but are followed by Arabic chars.
_JOBINJA_TA = re.compile(r'[^\u0600-\u06FF\s]\uFE8E(?=\s)')


def normalize_persian_digits(text: str) -> str:
    """Convert Persian/Arabic digits (۰-۹) to ASCII digits (0-9).
    Runs Jobinja 'تا' normalisation first (before NFKC destroys the shaped
    glyphs it relies on), then applies NFKC to convert Arabic presentation
    forms to standard Unicode, strips stray C0 control characters left behind,
    normalises any remaining lone 'ا' separators between year-like tokens,
    unifies Arabic ي/ك with Persian ی/ک, then maps Persian digits and ٫ to ASCII.
    """
    text = _JOBINJA_TA.sub(' - ', text)          # must run before NFKC
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F]', '', text)      # strip control chars, preserve \n and \r
    # After stripping control chars, Jobinja 'تا' may leave a lone 'ا' between
    # a year/month and a digit — normalise that to ' - '
    text = re.sub(r'(?<=\d) ا (?=\d)', ' - ', text)
    # Unify Arabic ي (U+064A) and ك (U+0643) with Persian ی (U+06CC) and ک (U+06A9)
    text = text.replace('\u064A', '\u06CC').replace('\u0643', '\u06A9')
    table = str.maketrans('۰۱۲۳۴۵۶۷۸۹\u066B', '0123456789.')
    return text.translate(table)


def normalize_jobinja_ta(text: str) -> str:
    """Normalise real 'تا' (to/until) word separator to ' - '.

    The Jobinja corrupted variant is already handled inside
    normalize_persian_digits (before NFKC).  This function handles the plain
    Persian 'تا' word used by JobVision and similar sites.
    """
    return re.sub(r'(?<= )تا(?= )', ' - ', text)


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
