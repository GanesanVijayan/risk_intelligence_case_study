# test_ingestion.py
import pytest
from unittest.mock import MagicMock, patch
from src.ingestion import clean_text, extract_sections


def test_clean_text_removes_hyphenated_line_breaks_and_newlines():
    raw_text = "com-\nmitment\nis   strong"
    cleaned = clean_text(raw_text)
    assert cleaned == "commitment is strong"


@patch("src.ingestion.pdfplumber.open")
def test_extract_sections_with_mocked_pdf(mock_pdf_open):
    # Mock a PDF with one page
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample\nText"
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf_open.return_value.__enter__.return_value = mock_pdf

    result = extract_sections("dummy.pdf", [1], apply_cleaning=True)

    # Verify output dictionary
    assert "p.1" in result
    assert result["p.1"] == "Sample Text"  # cleaned text
