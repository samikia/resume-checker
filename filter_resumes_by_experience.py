import fitz  # PyMuPDF
import re
import shutil
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# ================== SETTINGS ==================
input_folder = Path(r"D:\jobinja\resumes)
output_folder = input_folder / "+5"
output_folder.mkdir(exist_ok=True)


def normalize_persian_digits(text: str) -> str:
    """Convert Persian/Arabic digits to English (۱۴۰۳ → 1403)"""
    persian_digits = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(persian_digits)


def calculate_experience_years(text: str) -> float:
    """
    Calculate total years of professional experience.
    - First tries to find Work Experience section
    - If not found (common in some Persian PDFs), falls back to ALL years in the resume
    """
    current_year = datetime.now().year
    text_lower = text.lower()
    
    # Strong headers for Work Experience
    work_headers = [
        "technical experience", "work experience", "professional experience",
        "experience", "employment history", "سابقه کاری", "تجربه کاری",
        "سابقه کار", "تجربیات شغلی", "سوابق شغلی", "سوابق کاری"
    ]
    
    work_start_pos = len(text)
    for header in work_headers:
        pos = text_lower.find(header)
        if pos != -1:
            work_start_pos = min(work_start_pos, pos)
    
    # If no work header found → fallback to entire text (robust for Persian PDFs)
    if work_start_pos == len(text):
        work_text = text
    else:
        # Find end of work section
        end_headers = [
            "education", "skills", "projects", "courses", "about me", "about",
            "references", "تحصیلات", "مهارت", "پروژه", "دوره‌های", "سوابق تحصیلی"
        ]
        work_end_pos = len(text)
        for header in end_headers:
            pos = text_lower.find(header, work_start_pos + 20)
            if pos != -1:
                work_end_pos = min(work_end_pos, pos)
        work_text = text[work_start_pos:work_end_pos]
    
    # Normalize text
    work_text_norm = normalize_persian_digits(work_text.lower())
    work_text_norm = work_text_norm.replace('–', '-').replace('—', '-')
    work_text_norm = work_text_norm.replace('present', str(current_year)).replace('now', str(current_year))
    
    # Extract year ranges
    year_range_pattern = r'(\b\d{4}\b)\s*[-–]\s*(\b\d{4}\b|present|now)'
    matches = re.findall(year_range_pattern, work_text_norm)
    
    all_years = set()
    for start_str, end_str in matches:
        try:
            start = int(start_str)
            end = int(end_str) if end_str.isdigit() else current_year
            if 1300 <= start <= current_year + 10:
                all_years.add(start)
                all_years.add(end)
        except:
            pass
    
    # Fallback: any 4-digit year
    fallback_years = re.findall(r'\b(\d{4})\b', work_text_norm)
    for y in fallback_years:
        year = int(y)
        if 1300 <= year <= current_year + 10:
            all_years.add(year)
    
    # Calculate span
    span_years = max(all_years) - min(all_years) if all_years else 0.0
    
    # Add explicit numbers like "۷ سال سابقه"
    explicit_patterns = [
        r'(\d{1,2})\s*(?:سال|years?|تجربه|experience)',
        r'(\d{1,2})\+\s*(?:سال|years?)'
    ]
    for pat in explicit_patterns:
        for match in re.findall(pat, work_text_norm):
            try:
                span_years += float(match)
            except:
                pass
    
    return span_years


# ================== MAIN EXECUTION ==================
pdf_files = list(input_folder.glob("*.pdf"))

print(f"Number of PDF files found: {len(pdf_files)}")

moved_count = 0
for pdf_file in tqdm(pdf_files, desc="Scanning and moving resumes"):
    try:
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        
        years = calculate_experience_years(text)
        
        if years > 5:
            destination = output_folder / pdf_file.name
            shutil.move(pdf_file, destination)  # Cut (Move)
            moved_count += 1
            print(f"✓ Moved (+{years:.0f} years): {pdf_file.name}")
    
    except Exception as e:
        print(f"✗ Error reading {pdf_file.name}: {e}")

print(f"\nDone! {moved_count} resumes with more than 5 years of experience were moved to the +5 folder")