# test_evaluators.py
import pytest
from src.evaluators import extract_unique_pages, exact_match_eval, coverage_eval, semantic_eval

# Sample golden and output sets
golden_set = [
    {
        "risks": [
            {"risk_title": "Climate Risk", "description": "Impact of climate change", "category": "climate", "page_reference": "p.50"},
            {"risk_title": "Market Risk", "description": "Demand fluctuations", "category": "market", "page_reference": "p.50"},
        ]
    }
]

output_set = [
    {
        "risks": [
            {"risk_title": "Climate Risk", "description": "Climate change effects", "category": "climate", "page_reference": "p.50"},
            {"risk_title": "Operational Risk", "description": "Supply chain issues", "category": "operational", "page_reference": "p.50"},
        ]
    }
]


def test_extract_unique_pages_returns_all_page_refs():
    pages = extract_unique_pages(output_set)
    assert "p.50" in pages
    assert isinstance(pages, list)
    assert len(pages) == 1


def test_exact_match_eval_score_and_results():
    result = exact_match_eval(golden_set, output_set, "p.50")
    assert result["page_reference"] == "p.50"
    assert "exact_match_eval_results" in result
    assert "exact_match_eval_score" in result
    # Climate Risk should pass, Operational Risk should fail
    statuses = {r["risk_title"]: r["status"] for r in result["exact_match_eval_results"]}
    assert statuses["Climate Risk"] == "passed"
    assert statuses["Operational Risk"] == "failed"
    assert result["exact_match_eval_score"] < 100


def test_coverage_eval_detects_missing_and_extra_categories():
    result = coverage_eval(golden_set, output_set, "p.50")
    assert result["page_reference"] == "p.50"
    coverage_results = result["coverage_eval_results"][0]
    assert "climate" in coverage_results["matched"]
    assert "market" in coverage_results["missing_in_output"]
    assert "operational" in coverage_results["extra_in_output"]
    assert result["coverage_eval_score"] < 100


def test_semantic_eval_similarity_and_score(monkeypatch):
    # Monkeypatch model.encode to return fixed vectors
    from src import evaluators

    def fake_encode(text, convert_to_tensor=True):
        return [1.0] if "Climate" in text else [0.0]

    def fake_cos_sim(a, b):
        return [[1.0 if a == b else 0.5]]

    monkeypatch.setattr(evaluators.model, "encode", fake_encode)
    # monkeypatch.setattr(evaluators.util, "cos_sim", fake_cos_sim)

    result = semantic_eval(golden_set, output_set, "p.50", threshold=0.7)
    assert result["page_reference"] == "p.50"
    assert "semantic_eval_results" in result
    assert "semantic_eval_score" in result
    # Climate Risk should pass, Operational Risk has no golden match so not included
    statuses = {r["risk_title"]: r["status"] for r in result["semantic_eval_results"]}
    assert statuses["Climate Risk"] == "passed"
