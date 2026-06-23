# test_risk_models.py
import pytest
from pydantic import ValidationError
from src.schema import RiskItem, RiskReport   # adjust import path if needed


def test_valid_risk_item():
    item = RiskItem(
        risk_title="Climate Risk",
        description="Impact of climate change on operations",
        category="climate",
        page_reference="p.50",
        mitigation=["Carbon offset", "Renewable sourcing"]
    )
    assert item.risk_title == "Climate Risk"
    assert item.mitigation == ["Carbon offset", "Renewable sourcing"]


def test_risk_item_without_mitigation():
    item = RiskItem(
        risk_title="Operational Risk",
        description="Supply chain disruption",
        category="operational",
        page_reference="p.72"
    )
    assert item.mitigation is None


def test_invalid_risk_item_missing_field():
    with pytest.raises(ValidationError):
        RiskItem(
            description="Missing title",
            category="market",
            page_reference="p.85"
        )


def test_valid_risk_report_with_defaults():
    item = RiskItem(
        risk_title="Regulatory Risk",
        description="Policy changes affecting compliance",
        category="regulatory",
        page_reference="p.86"
    )
    report = RiskReport(risks=[item])
    assert report.company_name == "unknown"
    assert report.year == "unknown"
    assert report.file_name == "unknown"
    assert len(report.risks) == 1


def test_risk_report_with_metadata():
    item = RiskItem(
        risk_title="Cyber Risk",
        description="Data breach exposure",
        category="cyber",
        page_reference="p.118"
    )
    report = RiskReport(
        company_name="Vestas",
        year="2025",
        file_name="VestasAnnualReport2025.pdf",
        risks=[item]
    )
    assert report.company_name == "Vestas"
    assert report.year == "2025"
    assert report.file_name.endswith(".pdf")

