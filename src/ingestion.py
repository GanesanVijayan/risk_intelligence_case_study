import pdfplumber
import re
from typing import Dict, List

def clean_text(text: str) -> str:
    """
    Normalize PDF-extracted text for downstream processing.
    - Remove hyphenated line breaks (e.g., 'com-\nmitment' → 'commitment')
    - Replace newlines with spaces
    - Collapse multiple spaces
    """
    if not text:
        return ""

    # Fix hyphenated line breaks
    text = re.sub(r"-\n", "", text)

    # Replace newlines with spaces
    text = re.sub(r"\n+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def extract_sections(pdf_path: str, page_nums: List[int], apply_cleaning: bool = False) -> Dict[str, str]:
    """
    Extract and clean text from specific pages of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.
        pages (List[int]): List of page indices (0-based) to extract.
        apply_cleaning (bool): Whether to apply text cleaning.

    Returns:
        Dict[str, str]: Dictionary mapping page reference (e.g., "p.50") to cleaned text.
    """
    text_sections = {}
    pages = None
    try:
        pages = [num - 1 for num in page_nums if isinstance(page_nums, List)] # index starts from 0. so, index = page_number-1
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in pages:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    raw_text = page.extract_text()
                    cleaned = clean_text(raw_text) if raw_text and apply_cleaning else raw_text or "[No text extracted]"
                    text_sections[f"p.{page_num+1}"] = cleaned
                else:
                    text_sections[f"p.{page_num+1}"] = "[Page out of range]"
    except Exception as e:
        raise RuntimeError(f"Error extracting sections: {e}")

    return text_sections
