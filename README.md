
# Design approach:

# Current Solution Approach: Plain Python + pdfplumber + spaCy + Pydantic.
Plain Python + Libraries (pdfplumber, spaCy, Pydantic)

- pdfplumber → PDF ingestion
- spaCy/regex → candidate extraction
- LLM API → summarization/classification
- Pydantic → schema validation
- Rule-based evaluator → regression checks

# Steps followed for installation

# Steps 
1. create project structure
2. create venv "python -m venv .venv"
3. activate venv ".\.venv\Scripts\activate.bat"
4. install dependecies "pip install -r requirements.txt"
5. download spacy language model "python -m spacy download en_core_web_sm"
6. use model from https://huggingface.co/models -> vestas_case_study: "hf_xxxx" (or) run local server http://127.0.0.1:1234 to use LMStudio model locally. No access token required unless set explicitly.


# Issues/challenges I encountered/resolved during this project implementation
1. resolved python dependency failures upon downloading spacy occured due to version incompatibility
2. Strong system prompt to identify one vs. many risks from the given page
3. p.118 had multiple mitigation actions mentioned which had to be handled as type list instead of str.
4. I couldn't manually prepare a golden set, hence had to generate it using a heavyweight model GPT5.7(Microsfot Copilot)
5. Apply embedding model in eval pipeline to find matching title first by semantic and then apply eval checks, because of the risk order mismatch, or random matching on "category"/"risk_title", the evaluation might go wrong during comparison.

# Refer ./docs/* for more details.