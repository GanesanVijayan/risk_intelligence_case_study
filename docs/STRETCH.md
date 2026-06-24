### State
- **Global State Object**: Holds metadata (company, year, file_name), extracted risks, evaluation scores, embeddings, and query results.
- **Schema**: Pydantic models ensure structured state transitions.
- **Vector Store State**: Embeddings persisted in Redis Vector DB / Pinecone for semantic retrieval.
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
   - Output: Embeddings stored in vector DB (Redis/Pinecone/Weaviate)
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