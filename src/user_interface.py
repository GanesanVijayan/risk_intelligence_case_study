import json
import pandas as pd
import regex
from openai import OpenAI
from tabulate import tabulate
from src.utils import load_api_key

SK_LM_API_KEY = load_api_key()
MODEL_NAME = "qwen2.5-0.5b-instruct"


# Initialize LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key=SK_LM_API_KEY)

def clean_and_parse_json(raw_text: str):
    """Remove markdown fences and parse JSON safely."""
    cleaned = regex.sub(r"```json|```", "", raw_text).strip()
    match = regex.search(r"\[.*\]|\{.*\}", cleaned, regex.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON parsing failed:", e)
        print("Cleaned text was:\n", cleaned)
        return None

def extract_filters(user_query: str):
    """
    Use LLM to extract filter criteria from user query.
    """
    prompt = f"""
    You are an assistant that extracts filter criteria from user queries.
    User query: "{user_query}"

    Instructions:
    - Return a JSON object with possible filters.
    - Keys can be: category, page_reference, risk_title.
    - If not mentioned, set value to null.
    Example:
    {{"category": "climate", "page_reference": "p.86", "risk_title": null}}
    """

    completion = client.chat.completions.create(
        model="mistralai/ministral-3-3b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )

    response = completion.choices[0].message.content.strip()
    print(clean_and_parse_json(response))
    # return json.loads(clean_and_parse_json(response))
    return clean_and_parse_json(response)

def apply_filters(data, filters):
    """
    Deterministically filter JSON data using extracted filters.
    Supports risk_title, description (wildcard search), category,
    page_reference, and mitigation (string or list).
    
    Args:
        data (list): Parsed JSON list of reports.
        filters (dict): Dictionary of filters. Keys can be:
            - risk_title (str)
            - description (str, wildcard substring search)
            - category (str)
            - page_reference (str)
            - mitigation (str or list of str)
    
    Returns:
        list: Filtered risks.
    """
    filtered = []
    for report in data:
        for risk in report.get("risks", []):
            # Exact match filters
            if filters.get("risk_title") and risk.get("risk_title") != filters["risk_title"]:
                continue
            if filters.get("category") and risk.get("category") != filters["category"]:
                continue
            if filters.get("page_reference") and risk.get("page_reference") != filters["page_reference"]:
                continue

            # Wildcard search for description
            if filters.get("description"):
                if filters["description"].lower() not in risk.get("description", "").lower():
                    continue

            # Mitigation filter (string or list)
            if filters.get("mitigation"):
                risk_mitigations = risk.get("mitigation", [])
                if isinstance(filters["mitigation"], str):
                    if not any(filters["mitigation"].lower() in m.lower() for m in risk_mitigations):
                        continue
                elif isinstance(filters["mitigation"], list):
                    if not all(any(f.lower() in m.lower() for m in risk_mitigations) for f in filters["mitigation"]):
                        continue

            filtered.append(risk)
    return filtered


def to_dataframe(filtered_results):
    """
    Convert filtered results to pandas DataFrame for readability.
    """
    return pd.DataFrame(filtered_results)
