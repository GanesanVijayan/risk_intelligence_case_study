# test_risk_candidate.py
import pytest
from src.candidate_check import is_risk_candidate   # adjust import path if needed


def test_is_risk_candidate_detects_risk_keywords():
    text = "The company faces significant cybersecurity risk due to phishing attacks."
    assert is_risk_candidate(text) is True


def test_is_risk_candidate_returns_false_for_non_risk_text():
    text = "The company reported strong financial growth this quarter."
    assert is_risk_candidate(text) is False

