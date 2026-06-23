# Risk Intelligence Pipeline

## Product Context
We are building a structured risk intelligence pipeline that ingests corporate annual reports and extracts principal risks into a queryable database. The immediate deliverable is a single‑report pipeline (Vestas Annual Report 2025), but the design anticipates scaling across hundreds of reports per quarter.

## Users
- **Primary Users**: Analysts at asset management and compliance teams.
- **Consumption Mode**: Analysts will query structured risk data via:
  - Batch API (for portfolio‑wide queries).
  - Interactive UI (filters, search, tabular views).
  - Alerting/monitoring (e.g., new emerging risks flagged).

## Optimization Target (First Slice)
- **Correctness**: Ensure extracted risks are schema‑valid and semantically faithful.
- **Coverage**: Capture all principal risks in the specified sections.
- **Evaluation**: Integrate golden set comparison + evaluators (exact match, semantic similarity, coverage).
- **Cost/Throughput**: Secondary in this slice; focus is on accuracy and robustness.

## Assumptions
- Annual reports are available in PDF format with consistent structure.
- Risk sections are semi‑structured (titles, descriptions, mitigation actions).
- LLMs (via summarizer/classifier) can reliably extract structured risk items when guided by strong prompts.
- Analysts prefer concise, schema‑validated outputs (JSON/Pydantic).

## Deferred Scope
- **Scaling**: Latency/cost optimization across 200+ reports is deferred.
- **UI polish**: Current interface is CLI + tabulated text; full web UI deferred.
- **Advanced NLP**: Hybrid NER/regex + LLM ensemble deferred; current slice uses spaCy + regex + LLM.
- **Multi‑report trend analysis**: Out of scope for first slice.
- **Production deployment**: Cloud/on‑prem orchestration strategy (AKS/OpenShift) deferred to DESIGN.md.

## Implementation Decisions (Traceable to Plan)
- **PDF ingestion**: `pdfplumber` extracts text sections.
- **Candidate detection**: `spaCy` + regex ensures only risk‑related text is processed.
- **Summarization/classification**: LLM API with strong prompt logic.
- **Schema validation**: Pydantic `RiskReport` ensures structured consistency.
- **Evaluation**: Golden set + evaluator pipeline (exact, semantic, coverage).
- **Retry/fail‑fast**: Decorator ensures resilience against transient errors.
- **User queries**: Filter + tabulate results for analyst consumption.

## Next Steps (Stretch Goals)
- Deploy pipeline with **LangGraph multi‑agent orchestration** (agents for ingestion, candidate detection, summarization, validation, evaluation, consolidation, query interface).
- Integrate **guardrails** (content safety, schema enforcement).
- Add **observability** (metrics via DeepEval, RAGAs, LangSmith).
- Implement **fallback mechanisms** (rule‑based summarizer if LLM fails).
- Scale to batch processing across portfolios with drift monitoring.
- Deploy it in GPU/vRAM containers/pods using kubernetes with LLM runtime enviornment such as vLLM or similar environment
---
