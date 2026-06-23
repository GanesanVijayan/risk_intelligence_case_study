import json
from sentence_transformers import util
from src.utils import load_api_key
from openai import OpenAI


SK_LM_API_KEY = load_api_key()
MODEL_NAME = "text-embedding-nomic-embed-text-v1.5"

# Initialize lmstudio client from local server. Make sure local server is running before using this.
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key=SK_LM_API_KEY)

def get_embedding(text: str):
    """
    Get embedding vector from LM Studio for given text.
    """
    response = client.embeddings.create(
        model=MODEL_NAME,
        input=text
    )
    return response.data[0].embedding

def extract_unique_pages(output_set):
    pages = set()
    for report in output_set:
        for risk in report.get("risks", []):
            page_ref = risk.get("page_reference")
            if page_ref:
                pages.add(page_ref)
    return list(pages)


def exact_match_eval(golden_set, output_set, page_number: str):
    results = []
    golden_risks = [r for report in golden_set for r in report.get("risks", []) if r.get("page_reference") == page_number]
    output_risks = [r for report in output_set for r in report.get("risks", []) if r.get("page_reference") == page_number]

    for risk in output_risks:
        # golden_risk = next((g for g in golden_risks if g["risk_title"] == risk["risk_title"]), None)
        golden_risk = next((g for g in golden_risks if g["category"] == risk["category"]), None)
        if golden_risk:
            status = "passed" if (risk["category"] == golden_risk["category"] and risk["page_reference"] == golden_risk["page_reference"]) else "failed"
            results.append({
                "risk_title": risk["risk_title"],
                "category_match": risk["category"] == golden_risk["category"],
                "page_match": risk["page_reference"] == golden_risk["page_reference"],
                "status": status
            })
        else:
            results.append({
                "risk_title": risk["risk_title"],
                "status": "failed",
                "failure_reason": "missing in golden set"
            })

    # Score = % passed
    passed = sum(1 for r in results if r["status"] == "passed")
    score = (passed / len(results) * 100) if results else 0
    return {"page_reference": page_number, "exact_match_eval_results": results, "exact_match_eval_score": round(score, 2)}


def coverage_eval(golden_set, output_set, page_number: str):
    results = []
    golden_categories = {r.get("category") for report in golden_set for r in report.get("risks", []) if r.get("page_reference") == page_number}
    output_categories = {r.get("category") for report in output_set for r in report.get("risks", []) if r.get("page_reference") == page_number}

    matched = list(golden_categories & output_categories)
    missing_in_output = list(golden_categories - output_categories)
    extra_in_output = list(output_categories - golden_categories)
    coverage_percent = (len(matched) / len(golden_categories) * 100) if golden_categories else 0.0
    status = "passed" if matched and not missing_in_output and not extra_in_output else "failed"
    
    results.append({
        "matched": matched,
        "missing_in_output": missing_in_output,
        "extra_in_output": extra_in_output,
        "status": status,
    })
    return {
        "page_reference": page_number, "coverage_eval_results": results, "coverage_eval_score": round(coverage_percent, 2)
    }


def semantic_eval(golden_set, output_set, page_number: str, threshold: float = 0.7):
    results = []
    golden_risks = [r for report in golden_set for r in report.get("risks", []) if r.get("page_reference") == page_number]
    output_risks = [r for report in output_set for r in report.get("risks", []) if r.get("page_reference") == page_number]

    for risk in output_risks:
        # golden_risk = next((g for g in golden_risks if g["risk_title"] == risk["risk_title"]), None)
        golden_risk = next((g for g in golden_risks if g["category"] == risk["category"]), None)
        if golden_risk:
            emb1 = get_embedding(risk["description"])
            emb2 = get_embedding(golden_risk["description"])
            sim = util.cos_sim(emb1, emb2).item()
            status = "passed" if sim >= threshold else "failed"
            results.append({
                "risk_title": risk["risk_title"],
                "similarity": round(sim, 3),
                "page_reference": page_number,
                "status": status
            })

    # Score = % passed
    passed = sum(1 for r in results if r["status"] == "passed")
    score = (passed / len(results) * 100) if results else 0
    return {"page_reference": page_number, "semantic_eval_results": results, "semantic_eval_score": round(score, 2)}

def evaluator_pipeline(extracted, golden, page):
    """
    Run all evaluation layers except schema validation.
    """
    return {
        "exact_match": exact_match_eval(extracted, golden, page),
        "semantic_similarity": semantic_eval(extracted, golden, page),
        "coverage": coverage_eval(extracted, golden, page)
    }
