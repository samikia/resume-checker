"""CLI entry point: resume-checker <input_folder> [-o output.xlsx]"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from resume_checker import extract_all


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="resume-checker",
        description="Extract structured data from PDF resumes into Excel.",
    )
    parser.add_argument("input_folder", type=Path, help="Folder containing PDF resumes")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output Excel path (default: <input_folder>/resumes_extracted.xlsx)",
    )
    args = parser.parse_args()

    if not args.input_folder.is_dir():
        print(f"Error: {args.input_folder} is not a directory", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.input_folder / "resumes_extracted.xlsx"
    pdf_files = sorted(args.input_folder.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    if not pdf_files:
        print("No PDF files found.", file=sys.stderr)
        sys.exit(1)

    data = []
    for pdf_file in tqdm(pdf_files, desc="Processing resumes"):
        try:
            data.append(extract_all(pdf_file))
        except Exception as e:
            print(f"Error in {pdf_file.name}: {e}", file=sys.stderr)

    if data:
        df = pd.DataFrame(data)
        df.to_excel(output, index=False)
        print(f"\nDone! {len(data)} resumes saved to: {output}")
    else:
        print("No files were processed.", file=sys.stderr)
        sys.exit(1)
