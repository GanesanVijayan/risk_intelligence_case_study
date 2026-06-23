import re
import spacy
from typing import List

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")

def is_risk_candidate(text: str) -> bool:
    """
    Check if the given text contains risk-related content.

    Args:
        text (str): Raw text from a PDF section.

    Returns:
        bool: True if the text contains risk-related content, False otherwise.
    """
    candidates = []
    if not text:
        return False

    # Process text with spaCy
    doc = nlp(text)

    # Regex keywords to flag risk-related sentences
    risk_keywords = re.compile(r"(risk|uncertainty|challenge|exposure"
    "|threat|vulnerability|hazard|danger|loss|liability|instability|volatility)", re.IGNORECASE)

    for sent in doc.sents:
        if risk_keywords.search(sent.text):
            candidates.append(sent.text.strip())

    return True if candidates else False