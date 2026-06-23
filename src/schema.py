from typing import Optional, List
from pydantic import BaseModel
import re

class RiskItem(BaseModel):
    risk_title: str
    description: str
    category: str
    page_reference: str
    mitigation: Optional[list[str]] = None

class RiskReport(BaseModel):
    company_name: str = "unknown"
    year: str = "unknown"
    file_name: str = "unknown"
    risks: List[RiskItem] = None