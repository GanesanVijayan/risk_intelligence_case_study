import json
import sys
from typing import Dict
from openai import OpenAI
import traceback
import re as regex
from src.utils import load_api_key

from sympy import re

SK_LM_API_KEY = load_api_key()

# Initialize lmstudio client from local server. Make sure local server is running before using this.
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key=SK_LM_API_KEY)

def clean_and_parse_json(raw_text: str):
    """
    Remove markdown code fences and parse JSON safely.
    """
    # Remove code fences like ```json ... ```
    cleaned = regex.sub(r"```json|```", "", raw_text).strip()

    # Extract JSON block if extra text is present
    match = regex.search(r"\[.*\]|\{.*\}", cleaned, regex.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON parsing failed:", e)
        print("Cleaned text was:\n", cleaned)
        return None

def summarize_and_classify(candidate: str, page_ref: str, model: str, prompt_strenth: str="stronger") -> Dict[str, str]:
    """
    Summarize and classify candidate risk text using Hugging Face Inference API.
    Handles both single-risk and multi-risk cases.
    """

    prompt = f"""
    You are an assistant that extracts structured risk information.

    Candidate risk text (from {page_ref}):
    "{candidate}"

    Instructions:
    Structure the output as JSON. 
    - Avoid inline comments or explanations, only return the JSON array.
    - If the text contains ONE clear risk, return a JSON array of single JSON object with:
        risk_title, description, category, page_reference, mitigation.
    - If the text contains MULTIPLE distinct risks, return a JSON array of up to TEN objects,
      each with the same keys (risk_title, description, category, page_reference, mitigation).
    - risk_title: most relevant short title (max 6 words).
    - description: short and crisp 2–3 sentence summary.
    - category: only one of [financial, operational, regulatory, market, climate, cyber, supply chain].
    - page_reference: {page_ref}.
    - mitigation: list of mitigation actions if mitigations mentioned, else empty list.
    """
 
    weaker_prompt = f"""
    You are an assistant that extracts structured risk information.

    Candidate risk text (from {page_ref}):
    "{candidate}"

    Instructions:
    Structure the output as JSON. 
    - Avoid inline comments or explanations, only return the JSON array.
    - If the text contains ONE clear risk, return a JSON array of single JSON object with:
        risk_title, description, category, page_reference, mitigation.
    - If the text contains MULTIPLE distinct risks, return a JSON array of up to TEN objects,
      each with the same keys (risk_title, description, category, page_reference, mitigation).
    - risk_title: most relevant short title (max 6 words).
    - description: short and crisp 2–3 sentence summary.
    - category: only one of [financial, operational, regulatory, market, climate, cyber, supply chain].
    - page_reference: {page_ref}.
    - mitigation: mitigation actions in one liner if more mitigations mentioned, else empty string "".
    """

    prompt = weaker_prompt if prompt_strenth=="weaker" else prompt

    completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=4096,)

    response = completion.choices[0].message.content.strip()
    structured = None
    try:
        print("Raw model output:", response)
        structured = clean_and_parse_json(response)
    except Exception as e:
        print("Error during summarization and classification:", e)
        structured = [{
                "risk_title": None,
                "description": None,
                "category": None,
                "page_reference": None,
                "mitigation": [],
            }]
    return structured


