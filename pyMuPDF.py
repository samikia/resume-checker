# # import fitz  # PyMuPDF
# # import re
# # import pandas as pd
# # from pathlib import Path
# # from tqdm import tqdm
# # from datetime import datetime
# # from typing import Dict, Optional

# # # ================== SETTINGS ==================
# # input_folder = Path(r"D:\jobinja-excel\resumes")
# # output_excel = input_folder / "resumes_extracted.xlsx"

# # def normalize_persian_digits(text: str) -> str:
# #     persian_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
# #     return text.translate(persian_digits)

# # # ================== نام — نسخه نهایی ==================
# # def extract_name(text: str) -> Optional[str]:
# #     lines = [line.strip() for line in text.splitlines() if line.strip()]
    
# #     forbidden = re.compile(
# #         r'(skills|interests|hobbies|education|experience|projects|languages|about me|summary|contact|'
# #         r'درباره من|سوابق شغلی|مهارت|تحصیلات|پروژه|Data Scientist|Machine Learning|'
# #         r'Signal Processing|Image Processing|Deep Learning|Critical Thinking|Team Work|'
# #         r'Artificial Intelligence|AI & Computer Vision Developer|Technical Experience)', re.I
# #     )
    
# #     skip_patterns = re.compile(r'(\+?98|09|\(\+?98\))\s*\d|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|linkedin|github')
    
# #     # خط اول
# #     if lines and not skip_patterns.search(lines[0]) and not forbidden.search(lines[0]):
# #         cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس|Data Enthusiast Developer|Data Analyst)', '', lines[0], flags=re.I).strip()
# #         if len(cleaned.split()) >= 2 and len(cleaned) < 70:
# #             return cleaned
    
# #     # الگوهای فارسی
# #     name_patterns = [
# #         r'([آ-ی\s]+)\s*(Data Scientist|مهندس|دکتر)?',
# #         r'نام\s*[:\-]?\s*([آ-ی\s]+)',
# #         r'نام و نام خانوادگی\s*[:\-]?\s*([آ-ی\s]+)'
# #     ]
# #     for pat in name_patterns:
# #         match = re.search(pat, text, re.I)
# #         if match:
# #             name = match.group(1).strip()
# #             if len(name.split()) >= 2:
# #                 return name
    
# #     # نام انگلیسی
# #     for line in lines[:25]:
# #         if skip_patterns.search(line) or forbidden.search(line):
# #             continue
# #         cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس)', '', line, flags=re.I).strip()
# #         if len(cleaned.split()) >= 2 and len(cleaned) < 70 and (cleaned.istitle() or any(c.isupper() for c in cleaned)):
# #             return cleaned
# #     return None

# # # ================== شماره تماس ==================
# # def extract_phone(text: str) -> Optional[str]:
# #     text_norm = normalize_persian_digits(text)
# #     patterns = [
# #         r'\(\+?98\)\s*9\d{2,3}\s*[\d\s-]+',
# #         r'(\+?98|09)\s*\d{2,3}\s*[\d\s-]+',
# #         r'09\d{9}',
# #         r'9\d{9}',
# #         r'\+98\s?9\d{9}',
# #         r'09\d{2}\s?\d{3}\s?\d{4}'
# #     ]
# #     for pat in patterns:
# #         match = re.search(pat, text_norm)
# #         if match:
# #             return re.sub(r'[\s\(\)]+', '', match.group(0))
# #     return None

# # # ================== سابقه کاری — نسخه نهایی (جمع کردن 1 Year) ==================
# # # ================== سابقه کاری — نسخه نهایی و قوی (جمع کردن همه 1 Year) ==================
# # def calculate_experience_years(text: str) -> float:
# #     current_year = datetime.now().year
# #     text_lower = normalize_persian_digits(text.lower())
# #     text_lower = text_lower.replace('–', '-').replace('—', '-').replace('present', str(current_year)).replace('now', str(current_year)).replace('اکنون', str(current_year))

# #     # الگوی بسیار قوی برای جمع کردن همه (1 Year) ، 1 Year ، ( 1 Year ) و ...
# #     explicit_pattern = r'[\(\[]?\s*(\d{1,2})\s*(?:year|years?|سال|تجربه|experience)'
# #     explicit_matches = re.findall(explicit_pattern, text_lower)
# #     explicit_total = sum(float(m) for m in explicit_matches)
# #     if explicit_total > 0:
# #         return round(explicit_total, 1)

# #     # اگر عدد صریح نبود → محاسبه از تاریخ‌ها (همان نسخه قبلی)
# #     work_headers = [
# #         "technical experience", "work experience", "professional experience", "experience",
# #         "employment history", "سابقه کاری", "تجربه کاری", "سوابق شغلی", "تجربیات شغلی", "سوابق کاری"
# #     ]
    
# #     work_start = len(text)
# #     for h in work_headers:
# #         pos = text_lower.find(h)
# #         if pos != -1:
# #             work_start = min(work_start, pos)
    
# #     work_text = text[work_start:] if work_start < len(text) else text
# #     work_text_norm = normalize_persian_digits(work_text.lower())
# #     work_text_norm = work_text_norm.replace('–', '-').replace('—', '-')

# #     year_pattern = r'(\b\d{4}\b)\s*[-–]\s*(\b\d{4}\b|present|now|اکنون)'
# #     matches = re.findall(year_pattern, work_text_norm)
    
# #     years = set()
# #     for start_str, end_str in matches:
# #         try:
# #             start = int(start_str)
# #             end = int(end_str) if end_str.isdigit() else current_year
# #             if (1380 <= start <= current_year + 5) or (2010 <= start <= current_year + 5):
# #                 years.add(start)
# #                 years.add(end)
# #         except:
# #             pass
    
# #     if years:
# #         span = max(years) - min(years) + 1
# #         return round(span, 1)
    
# #     return 0.0

# # # ================== بقیه توابع (بدون تغییر) ==================
# # def extract_email(text: str) -> Optional[str]:
# #     match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
# #     return match.group(0) if match else None

# # def extract_education_field(text: str) -> Optional[str]:
# #     text_lower = text.lower()
# #     for header in ["education", "تحصیلات", "سوابق تحصیلی"]:
# #         pos = text_lower.find(header)
# #         if pos != -1:
# #             snippet = text[pos:pos + 700]
# #             match = re.search(r'(?:رشته|گرایش|field|major|degree in).*?[:\-]?\s*([^\n\r]+)', snippet, re.I)
# #             if match:
# #                 return match.group(1).strip()
# #     return None

# # def extract_skills(text: str) -> str:
# #     for h in ["skills", "مهارت‌ها", "competencies"]:
# #         pos = text.lower().find(h)
# #         if pos != -1:
# #             return text[pos:pos + 500].replace(h, "").strip()[:400]
# #     return ""

# # # ================== MAIN ==================
# # pdf_files = list(input_folder.glob("*.pdf"))
# # print(f"تعداد فایل PDF پیدا شده: {len(pdf_files)}")

# # data = []

# # for pdf_file in tqdm(pdf_files, desc="پردازش رزومه‌ها"):
# #     try:
# #         doc = fitz.open(pdf_file)
# #         text = "\n".join(page.get_text("text") for page in doc)
# #         doc.close()

# #         info: Dict = {
# #             "نام فایل": pdf_file.name,
# #             "نام و فامیلی": extract_name(text),
# #             "شماره تماس": extract_phone(text),
# #             "ایمیل": extract_email(text),
# #             "سابقه کاری (سال)": calculate_experience_years(text),
# #             "رشته تحصیلی": extract_education_field(text),
# #             "مهارت‌ها و تجربیات": extract_skills(text),
# #             "مسیر فایل": str(pdf_file)
# #         }
# #         data.append(info)

# #     except Exception as e:
# #         print(f"خطا در فایل {pdf_file.name}: {e}")

# # if data:
# #     df = pd.DataFrame(data)
# #     columns_order = ["نام فایل", "نام و فامیلی", "شماره تماس", "ایمیل",
# #                      "سابقه کاری (سال)", "رشته تحصیلی", "مهارت‌ها و تجربیات", "مسیر فایل"]
# #     df = df[columns_order]
# #     df.to_excel(output_excel, index=False)
# #     print(f"\n✅ تمام شد! {len(data)} رزومه پردازش و ذخیره شد:")
# #     print(output_excel)
    
# #     # چک سریع رزومه جدید
# #     for row in data:
# #         if "1a8f9df9" in row["نام فایل"]:
# #             print(f"\nAli Boudaghi → سابقه کاری: {row['سابقه کاری (سال)']} سال")
# # else:
# #     print("هیچ فایلی پردازش نشد.")

# import fitz  # PyMuPDF
# import re
# import pandas as pd
# from pathlib import Path
# from tqdm import tqdm
# from datetime import datetime
# from typing import Dict, Optional

# # ================== SETTINGS ==================
# input_folder = Path(r"D:\jobinja-excel\resumes")
# output_excel = input_folder / "resumes_extracted.xlsx"


# def normalize_persian_digits(text: str) -> str:
#     """Convert Persian/Arabic digits to English digits"""
#     persian_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
#     return text.translate(persian_digits)


# # ================== NAME — FINAL VERSION ==================
# def extract_name(text: str) -> Optional[str]:
#     """Extract full name from resume text (works for both Persian and English)"""
#     lines = [line.strip() for line in text.splitlines() if line.strip()]
    
#     # Keywords that should NOT be part of the name
#     forbidden = re.compile(
#         r'(skills|interests|hobbies|education|experience|projects|languages|about me|summary|contact|'
#         r'درباره من|سوابق شغلی|مهارت|تحصیلات|پروژه|Data Scientist|Machine Learning|'
#         r'Signal Processing|Image Processing|Deep Learning|Critical Thinking|Team Work|'
#         r'Artificial Intelligence|AI & Computer Vision Developer|Technical Experience)', re.I
#     )
    
#     skip_patterns = re.compile(r'(\+?98|09|\(\+?98\))\s*\d|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|linkedin|github')
    
#     # Priority 1: First line of resume (usually the name)
#     if lines and not skip_patterns.search(lines[0]) and not forbidden.search(lines[0]):
#         cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس|Data Enthusiast Developer|Data Analyst)', '', lines[0], flags=re.I).strip()
#         if len(cleaned.split()) >= 2 and len(cleaned) < 70:
#             return cleaned
    
#     # Priority 2: Persian name patterns
#     name_patterns = [
#         r'([آ-ی\s]+)\s*(Data Scientist|مهندس|دکتر)?',
#         r'نام\s*[:\-]?\s*([آ-ی\s]+)',
#         r'نام و نام خانوادگی\s*[:\-]?\s*([آ-ی\s]+)'
#     ]
#     for pat in name_patterns:
#         match = re.search(pat, text, re.I)
#         if match:
#             name = match.group(1).strip()
#             if len(name.split()) >= 2:
#                 return name
    
#     # Priority 3: English name (Title Case)
#     for line in lines[:25]:
#         if skip_patterns.search(line) or forbidden.search(line):
#             continue
#         cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس)', '', line, flags=re.I).strip()
#         if len(cleaned.split()) >= 2 and len(cleaned) < 70 and (cleaned.istitle() or any(c.isupper() for c in cleaned)):
#             return cleaned
#     return None


# # ================== PHONE NUMBER ==================
# def extract_phone(text: str) -> Optional[str]:
#     """Extract phone number (supports Persian and English formats)"""
#     text_norm = normalize_persian_digits(text)
#     patterns = [
#         r'\(\+?98\)\s*9\d{2,3}\s*[\d\s-]+',
#         r'(\+?98|09)\s*\d{2,3}\s*[\d\s-]+',
#         r'09\d{9}',
#         r'9\d{9}',
#         r'\+98\s?9\d{9}',
#         r'09\d{2}\s?\d{3}\s?\d{4}'
#     ]
#     for pat in patterns:
#         match = re.search(pat, text_norm)
#         if match:
#             return re.sub(r'[\s\(\)]+', '', match.group(0))
#     return None


# # ================== WORK EXPERIENCE — FINAL VERSION (Summing 1 Year) ==================
# def calculate_experience_years(text: str) -> float:
#     """Calculate total years of experience.
#     - First looks for explicit numbers like (1 Year), 1 Year, ۱ سال
#     - If none found, falls back to date ranges"""
#     current_year = datetime.now().year
#     text_lower = normalize_persian_digits(text.lower())
#     text_lower = text_lower.replace('–', '-').replace('—', '-').replace('present', str(current_year)).replace('now', str(current_year)).replace('اکنون', str(current_year))

#     # Strong pattern for explicit years: (1 Year), 1 Year, ۱ سال, etc.
#     explicit_pattern = r'[\(\[]?\s*(\d{1,2})\s*(?:year|years?|سال|تجربه|experience)'
#     explicit_matches = re.findall(explicit_pattern, text_lower)
#     explicit_total = sum(float(m) for m in explicit_matches)
#     if explicit_total > 0:
#         return round(explicit_total, 1)

#     # If no explicit number → extract from date ranges
#     work_headers = [
#         "technical experience", "work experience", "professional experience", "experience",
#         "employment history", "سابقه کاری", "تجربه کاری", "سوابق شغلی", "تجربیات شغلی", "سوابق کاری"
#     ]
    
#     work_start = len(text)
#     for h in work_headers:
#         pos = text_lower.find(h)
#         if pos != -1:
#             work_start = min(work_start, pos)
    
#     work_text = text[work_start:] if work_start < len(text) else text
#     work_text_norm = normalize_persian_digits(work_text.lower())
#     work_text_norm = work_text_norm.replace('–', '-').replace('—', '-')

#     year_pattern = r'(\b\d{4}\b)\s*[-–]\s*(\b\d{4}\b|present|now|اکنون)'
#     matches = re.findall(year_pattern, work_text_norm)
    
#     years = set()
#     for start_str, end_str in matches:
#         try:
#             start = int(start_str)
#             end = int(end_str) if end_str.isdigit() else current_year
#             if (1380 <= start <= current_year + 5) or (2010 <= start <= current_year + 5):
#                 years.add(start)
#                 years.add(end)
#         except:
#             pass
    
#     if years:
#         span = max(years) - min(years) + 1
#         return round(span, 1)
    
#     return 0.0


# # ================== OTHER FUNCTIONS (UNCHANGED) ==================
# def extract_email(text: str) -> Optional[str]:
#     match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
#     return match.group(0) if match else None


# def extract_education_field(text: str) -> Optional[str]:
#     text_lower = text.lower()
#     for header in ["education", "تحصیلات", "سوابق تحصیلی"]:
#         pos = text_lower.find(header)
#         if pos != -1:
#             snippet = text[pos:pos + 700]
#             match = re.search(r'(?:رشته|گرایش|field|major|degree in).*?[:\-]?\s*([^\n\r]+)', snippet, re.I)
#             if match:
#                 return match.group(1).strip()
#     return None


# def extract_skills(text: str) -> str:
#     for h in ["skills", "مهارت‌ها", "competencies"]:
#         pos = text.lower().find(h)
#         if pos != -1:
#             return text[pos:pos + 500].replace(h, "").strip()[:400]
#     return ""


# # ================== MAIN ==================
# pdf_files = list(input_folder.glob("*.pdf"))
# print(f"Number of PDF files found: {len(pdf_files)}")

# data = []

# for pdf_file in tqdm(pdf_files, desc="Processing resumes"):
#     try:
#         doc = fitz.open(pdf_file)
#         text = "\n".join(page.get_text("text") for page in doc)
#         doc.close()

#         info: Dict = {
#             "نام فایل": pdf_file.name,
#             "نام و فامیلی": extract_name(text),
#             "شماره تماس": extract_phone(text),
#             "ایمیل": extract_email(text),
#             "سابقه کاری (سال)": calculate_experience_years(text),
#             "رشته تحصیلی": extract_education_field(text),
#             "مهارت‌ها و تجربیات": extract_skills(text),
#             "مسیر فایل": str(pdf_file)
#         }
#         data.append(info)

#     except Exception as e:
#         print(f"Error in file {pdf_file.name}: {e}")

# if data:
#     df = pd.DataFrame(data)
#     columns_order = ["نام فایل", "نام و فامیلی", "شماره تماس", "ایمیل",
#                      "سابقه کاری (سال)", "رشته تحصیلی", "مهارت‌ها و تجربیات", "مسیر فایل"]
#     df = df[columns_order]
#     df.to_excel(output_excel, index=False)
#     print(f"\n✅ Done! {len(data)} resumes processed and saved to:")
#     print(output_excel)
    
#     # Quick check for the new resume
#     for row in data:
#         if "1a8f9df9" in row["نام فایل"]:
#             print(f"\nAli Boudaghi → Experience: {row['سابقه کاری (سال)']} years")
# else:
#     print("No files were processed.")

import fitz  # PyMuPDF
import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from typing import Dict, Optional

# ================== SETTINGS ==================
input_folder = Path(r"D:\jobinja-excel\resumes")
output_excel = input_folder / "resumes_extracted.xlsx"

def normalize_persian_digits(text: str) -> str:
    """Convert Persian/Arabic digits to English"""
    persian_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(persian_digits)


def clean_text(text: str) -> str:
    """Remove illegal characters for Excel (very important for Persian text)"""
    if not text:
        return ""
    # Remove control characters and Excel-forbidden Unicode
    text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B\u200C\u200D\u200E\u200F\u2028\u2029]', '', text)
    # Remove any remaining non-printable or zero-width chars
    text = re.sub(r'[\u2000-\u200F\u2028-\u202F]', '', text)
    return text.strip()


# ================== NAME ==================
def extract_name(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    forbidden = re.compile(
        r'(skills|interests|hobbies|education|experience|projects|languages|about me|summary|contact|'
        r'درباره من|سوابق شغلی|مهارت|تحصیلات|پروژه|Data Scientist|Machine Learning|'
        r'Signal Processing|Image Processing|Deep Learning|Critical Thinking|Team Work|'
        r'Artificial Intelligence|AI & Computer Vision Developer|Technical Experience)', re.I
    )
    
    skip_patterns = re.compile(r'(\+?98|09|\(\+?98\))\s*\d|@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|linkedin|github')
    
    if lines and not skip_patterns.search(lines[0]) and not forbidden.search(lines[0]):
        cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس|Data Enthusiast Developer|Data Analyst)', '', lines[0], flags=re.I).strip()
        if len(cleaned.split()) >= 2 and len(cleaned) < 70:
            return clean_text(cleaned)
    
    name_patterns = [
        r'([آ-ی\s]+)\s*(Data Scientist|مهندس|دکتر)?',
        r'نام\s*[:\-]?\s*([آ-ی\s]+)',
        r'نام و نام خانوادگی\s*[:\-]?\s*([آ-ی\s]+)'
    ]
    for pat in name_patterns:
        match = re.search(pat, text, re.I)
        if match:
            name = match.group(1).strip()
            if len(name.split()) >= 2:
                return clean_text(name)
    
    for line in lines[:25]:
        if skip_patterns.search(line) or forbidden.search(line):
            continue
        cleaned = re.sub(r'(mr\.|ms\.|mrs\.|مهندس|دکتر|کارشناس)', '', line, flags=re.I).strip()
        if len(cleaned.split()) >= 2 and len(cleaned) < 70 and (cleaned.istitle() or any(c.isupper() for c in cleaned)):
            return clean_text(cleaned)
    return None


# ================== PHONE ==================
def extract_phone(text: str) -> Optional[str]:
    text_norm = normalize_persian_digits(text)
    patterns = [
        r'\(\+?98\)\s*9\d{2,3}\s*[\d\s-]+',
        r'(\+?98|09)\s*\d{2,3}\s*[\d\s-]+',
        r'09\d{9}',
        r'9\d{9}',
        r'\+98\s?9\d{9}',
        r'09\d{2}\s?\d{3}\s?\d{4}'
    ]
    for pat in patterns:
        match = re.search(pat, text_norm)
        if match:
            return re.sub(r'[\s\(\)]+', '', match.group(0))
    return None


# ================== WORK EXPERIENCE ==================
_ALL_DASHES = re.compile(r'[\u002D\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uFE58\uFE63\uFF0D]')
_MONTHS = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
_SEASONS = r'(?:spring|summer|fall|autumn|winter)'
_MONTH_OR_SEASON = rf'(?:{_MONTHS}|{_SEASONS})'
_PRESENT_WORDS = ['present', 'now', 'current', 'ongoing', 'اکنون', 'تاکنون', 'هم‌اکنون', 'هم اکنون', 'کنون']
_WORD_TO_NUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}


def _shamsi_to_gregorian(year: int) -> int:
    if 1340 <= year <= 1430:
        return year + 621
    return year


def _normalize_dashes(text: str) -> str:
    return _ALL_DASHES.sub('-', text)


def _find_section_start(text_lower: str, headers: list[str]) -> int:
    """Find where a section starts by looking for headers on their own line."""
    best = len(text_lower)
    for h in headers:
        for m in re.finditer(re.escape(h.lower()), text_lower):
            pos = m.start()
            # Check that the header is at or near the start of a line (not mid-sentence)
            line_start = text_lower.rfind('\n', 0, pos)
            prefix = text_lower[line_start + 1:pos].strip()
            # Accept if prefix is empty or very short (e.g. bullet, emoji, number)
            if len(prefix) <= 5:
                best = min(best, pos)
    return best


def _find_education_start(text_lower: str) -> int:
    """Find where education section starts so we can exclude it."""
    edu_headers = ["education", "تحصیلات", "سوابق تحصیلی"]
    pos = _find_section_start(text_lower, edu_headers)
    return pos if pos < len(text_lower) else len(text_lower)


def calculate_experience_years(text: str) -> float:
    current_year = datetime.now().year
    text_norm = normalize_persian_digits(text)
    text_lower = _normalize_dashes(text_norm.lower())

    # --- Strategy 1: Explicit total in summary/header (first ~800 chars) ---
    summary_area = text_lower[:800]
    # Match digit-based: "5 years", "5+ years of experience", "۳ سال تجربه"
    explicit_pattern = r'(\d{1,2})\+?\s*(?:year|years?|سال)\s*(?:of\s*)?(?:experience|تجربه)?'
    explicit_matches = re.findall(explicit_pattern, summary_area)
    if explicit_matches:
        return round(max(float(m) for m in explicit_matches), 1)

    # Match word-based: "five years of experience", "over three years"
    word_num_pattern = rf'(?:over\s+|more\s+than\s+)?({"|".join(_WORD_TO_NUM.keys())})\s+years?\s*(?:of\s*)?(?:experience)?'
    word_matches = re.findall(word_num_pattern, summary_area)
    if word_matches:
        return round(max(_WORD_TO_NUM[w] for w in word_matches), 1)

    # Match "Since YYYY" pattern
    since_match = re.search(r'since\s+(\d{4})', summary_area)
    if since_match:
        since_year = int(since_match.group(1))
        if 1990 <= since_year <= current_year:
            return round(current_year - since_year, 1)

    # --- Strategy 2: Extract date ranges → merge intervals → sum durations ---
    work_headers = [
        "technical experience", "work experience", "professional experience",
        "work experiences", "employment history", "experience",
        "سابقه کاری", "تجربه کاری", "سوابق شغلی", "تجربیات شغلی", "سوابق کاری"
    ]

    work_start = _find_section_start(text_lower, work_headers)
    edu_start = _find_education_start(text_lower)

    # Use only the work section, stop before education if education comes after work
    if work_start < len(text_lower):
        if edu_start > work_start:
            work_text = text_lower[work_start:edu_start]
        else:
            work_text = text_lower[work_start:]
    else:
        work_text = text_lower

    # Replace present/now words with current year
    for pw in _PRESENT_WORDS:
        work_text = work_text.replace(pw, str(current_year))

    # Pattern 1: [optional Month/Season] YYYY - [optional Month/Season] YYYY
    date_range_pattern = rf'(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})\s*-\s*(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})'
    matches = re.findall(date_range_pattern, work_text)

    # Pattern 2: [optional Month/Season] YYYY- (open-ended = present)
    open_ended_pattern = rf'(?:{_MONTH_OR_SEASON}\s+)?(\d{{4}})\s*-\s*$'
    open_matches = re.findall(open_ended_pattern, work_text, re.MULTILINE)

    intervals = []
    for start_str, end_str in matches:
        try:
            start = _shamsi_to_gregorian(int(start_str))
            end = _shamsi_to_gregorian(int(end_str))
            if 1990 <= start <= current_year + 1 and start <= end <= current_year + 1:
                intervals.append((start, end))
        except:
            pass

    for start_str in open_matches:
        try:
            start = _shamsi_to_gregorian(int(start_str))
            if 1990 <= start <= current_year + 1:
                intervals.append((start, current_year))
        except:
            pass

    if not intervals:
        return 0.0

    # Merge overlapping intervals, then sum each duration
    intervals.sort()
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    total = sum(end - start for start, end in merged)
    return round(total, 1)


# ================== OTHER FUNCTIONS ==================
def extract_email(text: str) -> Optional[str]:
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None


def extract_education_field(text: str) -> Optional[str]:
    text_lower = text.lower()
    for header in ["education", "تحصیلات", "سوابق تحصیلی"]:
        pos = text_lower.find(header)
        if pos != -1:
            snippet = text[pos:pos + 700]
            match = re.search(r'(?:رشته|گرایش|field|major|degree in).*?[:\-]?\s*([^\n\r]+)', snippet, re.I)
            if match:
                return clean_text(match.group(1).strip())
    return None


def extract_skills(text: str) -> str:
    for h in ["skills", "مهارت‌ها", "competencies"]:
        pos = text.lower().find(h)
        if pos != -1:
            return clean_text(text[pos:pos + 500].replace(h, "").strip()[:400])
    return ""


# ================== MAIN ==================
pdf_files = list(input_folder.glob("*.pdf"))
print(f"Number of PDF files found: {len(pdf_files)}")

data = []

for pdf_file in tqdm(pdf_files, desc="Processing resumes"):
    try:
        doc = fitz.open(pdf_file)
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()

        info: Dict = {
            "نام فایل": pdf_file.name,
            "نام و فامیلی": extract_name(text),
            "شماره تماس": extract_phone(text),
            "ایمیل": extract_email(text),
            "سابقه کاری (سال)": calculate_experience_years(text),
            "رشته تحصیلی": extract_education_field(text),
            "مهارت‌ها و تجربیات": extract_skills(text),
            "مسیر فایل": str(pdf_file)
        }
        data.append(info)

    except Exception as e:
        print(f"Error in file {pdf_file.name}: {e}")

if data:
    df = pd.DataFrame(data)
    columns_order = ["نام فایل", "نام و فامیلی", "شماره تماس", "ایمیل",
                     "سابقه کاری (سال)", "رشته تحصیلی", "مهارت‌ها و تجربیات", "مسیر فایل"]
    df = df[columns_order]
    df.to_excel(output_excel, index=False)
    print(f"\n✅ Done! {len(data)} resumes processed and saved to:")
    print(output_excel)
else:
    print("No files were processed.")