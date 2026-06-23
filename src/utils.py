
import re as regex
import os
import glob
import json

# Load API key from config.yaml
def load_api_key(config_path: str = "conf/config.yaml") -> str:
    with open(config_path, "r") as f:
        config = json.load(f)
    return config.get("SK_LM_API_KEY")

def extract_metadata_from_filename(file_name: str) -> dict:
    """
    Extract company name and year from a PDF filename.
    Example: 'VestasAnnualReport2025.pdf' -> {'company_name': 'Vestas', 'year': '2025'}
    """
    base = file_name.replace(".pdf", "")
    # Try to extract year (4 consecutive digits)
    year_match = regex.search(r"(20\d{2})", base)
    year = year_match.group(1) if year_match else "unknown"

    # Extract company name by removing 'AnnualReport' and year
    company = regex.sub(r"(20\d{2})", "", base)
    company = company.replace("AnnualReport", "").strip()
    if not company:
        company = "unknown"

    return {
        "company_name": company,
        "year": year,
        "file_name": file_name
    }

def cleanup_dir(dir_path: str):
    """
    Utility function to clean up a directory by removing all files in it if it exists.
    """
    if not os.path.exists(dir_path):
        return

    files = glob.glob(os.path.join(dir_path, "*"))
    for f in files:
        os.remove(f)

def consolidate_risk_reports(input_dir: str, output_file: str):
    """
    Consolidate multiple risk report JSON files into a single JSON file.
    """
    consolidated_data = []
    for file in glob.glob(os.path.join(input_dir, "*.json")):
        with open(file, "r") as f:
            data = json.load(f)
            consolidated_data.append(data)

    with open(output_file, "w") as f:
        json.dump(consolidated_data, f, indent=3)


def find_file_by_relative_name(directory: str, relative_name: str):
    """
    Search for files in the given directory whose names contain the relative_name substring.

    Args:
        directory (str): Path to the directory to search.
        relative_name (str): Substring to look for in filenames (e.g., 'report_2025').

    Returns:
        list: List of matching file paths.
    """
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if relative_name in file:  # substring match
                matches.append(os.path.join(root, file))
    return matches[0] if len(matches) >= 1 else None