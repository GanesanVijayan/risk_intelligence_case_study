# Future Implementation Roadmap

## Goal
Extend the single‑report risk pipeline into a scalable, resilient, and production‑ready system.  
Focus areas: **LangGraph orchestration**, **RAG integration**, **guardrails**, **observability**, **resilience**, and **multi‑report trend analysis**.

---

## LangGraph Multi‑Agent Pipeline

### State
### State
- **Global State Object**: Holds metadata (company, year, file_name), extracted risks, evaluation scores, embeddings, and query results.
- **Schema**: Pydantic models ensure structured state transitions.
- **Vector Store State**: Embeddings persisted in Redis, Vector DB / Pinecone for semantic retrieval.
- **Structured DB State**: Risks stored in relational DB (Postgres/SQL) for deterministic queries.

### Nodes (Agents)
1. **PDF Ingestion Node**
   - Input: PDF path + page numbers
   - Output: Raw text sections persisted in Redis with metadata
2. **Risk Candidate Detector Node**
   - Input: Raw text
   - Output: Candidate sentences flagged by spaCy + regex
3. **Summarizer & Classifier Node**
   - Input: Candidate sentences
   - Output: Structured risk items (title, description, category, mitigation)
4. **Schema Validator Node**
   - Input: Risk items
   - Output: Validated JSON (RiskReport)
5. **Evaluator Node**
   - Input: Validated JSON + golden set
   - Output: Exact match, semantic similarity, coverage scores
6. **Consolidator Node**
   - Input: Per‑page JSON
   - Output: Consolidated risk report persisted in Redis DB + SQL DB
7. **RAG Embedding & Retrieval Node**
   - Input: Consolidated risk report
   - Output: Embeddings stored in vector DB (Redis/Pinecone)
   - Enables semantic search across risks and mitigation narratives
8. **SQL Query Generator Node**
   - Input: Analyst natural language query
   - Output: Translated SQL query executed against structured DB
   - Ensures precise filtering, aggregation, joins
9. **Query Interface Node**
   - Input: Analyst queries
   - Output: Either semantic answers (via RAG) or structured results (via SQL)

---

### Edges
- **Sequential Edges**: Ingestion → Candidate Detection → Summarizer → Validator → Evaluator → Consolidator → (RAG / SQL) → Query Interface
- **Conditional Edges**:
  - If **Candidate Detector** finds no risks → skip Summarizer, return “No risks found”
  - If **Validator** fails → trigger fallback summarizer (rule‑based)
  - If **Evaluator** score < threshold → log regression, trigger alert
  - If **Query intent = semantic** → route through RAG Node
  - If **Query intent = structured** → route through SQL Query Generator Node
  - Else → default to SQL path for safety

---

## Guardrails
- **Schema Enforcement**: Pydantic strict mode (`extra="forbid"`).
- **Content Safety**: Regex + Azure AI Content Safety for prompt outputs.
- **Policy Checks**: OPA/Istio or API Management (Azure).

---

## Resilience
- **Rate Limiting**: API Management using Azure/ OpenShift Istio.
- **Retry Logic**: Built‑in decorator for transient failures.
- **Fail‑Fast**: Immediate stop on schema validation errors.
- **Fallback Mechanism**: Rule‑based summarizer if LLM fails.

---

## Observability & Metrics
- **Evaluation Metrics**: DeepEval, RAGAs, LangSmith integrated into CI/CD.
- **Monitoring**:
  - OpenShift: Prometheus + Grafana (TIG stack)
- **Drift Detection**:
  - Azure ML Model Monitoring
  - Kubeflow pipelines

---

## Build and Deployment Enhancements
- **Cloud/Hybrid (OpenShift)**:
  - Jenkins + Unit & Integration, performance eval metrics framework
  - Pods + Operators for orchestration
  - ELK/TIG stack for logs
  - Rate Limiting for API traffic shaping
  - Custom Model API catalog

---

## Next Week Deliverables (prioritized if asked)
- **OOPs structural implementation** for better modularity, scalability, testability, and reusability.
- **Robust unit, integration, and metrics evaluation framework** with acceptable coverage.
- **LangGraph orchestration code** with defined state, nodes, edges, and conditional edges.
- **Guardrails integration** (schema + content safety).
- **Observability hooks** (metrics, logs, drift monitoring).
- **Fallback summarizer agent**.
- **Multi‑report trend analysis prototype** (emerging risks across portfolio).

---