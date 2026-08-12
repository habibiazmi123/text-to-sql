# Graph Report - .  (2026-08-12)

## Corpus Check
- Corpus is ~13,548 words - fits in a single context window. You may not need a graph.

## Summary
- 152 nodes · 267 edges · 27 communities (19 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- API Routes & Orchestration
- Go Backend
- Embeddings & RAG Retrieval
- Business Rules RAG
- SQL Validation
- SQL Generation
- Query Models
- LLM Client
- Backend Tests
- OpenCode Plugin
- Python Config
- Graphify Plugin
- httpx Dep
- pydantic-settings Dep
- uvicorn Dep
- Go DB
- Go config
- Docker Compose
- Go Module

## God Nodes (most connected - your core abstractions)
1. `SQLValidator` - 23 edges
2. `embed_text()` - 12 edges
3. `generate_with_retry()` - 11 edges
4. `Business Rules Retriever (retrieve_relevant_rules)` - 10 edges
5. `generate()` - 9 edges
6. `retrieve_relevant_rules()` - 9 edges
7. `embed_texts()` - 8 edges
8. `retrieve()` - 7 edges
9. `QueryService` - 7 edges
10. `Business Rules Indexer (index_business_rules)` - 7 edges

## Surprising Connections (you probably didn't know these)
- `API Integration (/ai/retrieve, /ai/index)` --references--> `FastAPI (>=0.111.0)`  [INFERRED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt
- `SQL Generator Prompt Integration (generate_sql)` --references--> `SQLParse (>=0.5.0)`  [INFERRED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt
- `Business Rules Indexer (index_business_rules)` --references--> `psycopg2-binary (>=2.9.12)`  [EXTRACTED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt
- `Business Rules Retriever (retrieve_relevant_rules)` --references--> `psycopg2-binary (>=2.9.12)`  [EXTRACTED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt
- `SQL Generator Prompt Integration (generate_sql)` --references--> `OpenAI SDK (>=1.35.0)`  [INFERRED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Business Knowledge RAG Pipeline (parallel retrieval -> context assembly -> SQL generation)** — docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_schema_rag, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_retriever, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_api_integration, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_sql_generator_prompt_integration [EXTRACTED 1.00]
- **Business Rules Indexing to Retrieval Data Flow** — docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_indexer, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_table, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_retriever, docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_seed_business_rules [EXTRACTED 1.00]

## Communities (27 total, 8 thin omitted)

### Community 0 - "API Routes & Orchestration"
Cohesion: 0.14
Nodes (27): generate(), generate_with_retry(), GenerateRequest, GenerateResponse, index(), Generate SQL with EXPLAIN validation and retry on failure., retrieve(), RetrieveRequest (+19 more)

### Community 1 - "Go Backend"
Cohesion: 0.13
Nodes (15): main(), getEnv(), Load(), Context, DB, NewHealthHandler(), Context, NewQueryHandler() (+7 more)

### Community 2 - "Embeddings & RAG Retrieval"
Cohesion: 0.21
Nodes (11): index_schema(), embed_text(), embed_texts(), get_model(), retrieve_relevant_schema(), index_sql_examples(), retrieve_similar_examples(), get_schema_entries() (+3 more)

### Community 3 - "Business Rules RAG"
Cohesion: 0.22
Nodes (16): FastAPI (>=0.111.0), OpenAI SDK (>=1.35.0), psycopg2-binary (>=2.9.12), sentence-transformers (>=3.1.0), SQLParse (>=0.5.0), PyTorch (>=2.0.0), API Integration (/ai/retrieve, /ai/index), Business Knowledge RAG (+8 more)

### Community 4 - "SQL Validation"
Cohesion: 0.25
Nodes (11): Basic validation + EXPLAIN dry-run to catch runtime errors., SQLValidator, ValidationResult, test_allows_select(), test_allows_with(), test_rejects_delete(), test_rejects_drop(), test_rejects_insert() (+3 more)

### Community 5 - "SQL Generation"
Cohesion: 0.50
Nodes (6): build_sql_prompt(), generate_sql(), parse_llm_sql_response(), test_build_sql_prompt(), test_parse_llm_sql_response(), test_parse_llm_sql_response_fallback()

### Community 6 - "Query Models"
Cohesion: 0.38
Nodes (5): ChatMessage, QueryRecord, QueryRequest, QueryResponse, Time

### Community 7 - "LLM Client"
Cohesion: 0.83
Nodes (3): chat_completion(), get_llm_client(), OpenAI

### Community 8 - "Backend Tests"
Cohesion: 0.67
Nodes (3): TestHealthEndpoint(), TestQueryEndpointValidation(), T

### Community 9 - "OpenCode Plugin"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 10 - "Python Config"
Cohesion: 0.67
Nodes (3): Config, Settings, BaseSettings

## Knowledge Gaps
- **12 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `text-to-sql-backend`, `Docker Compose Configuration`, `Config` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLValidator` connect `SQL Validation` to `API Routes & Orchestration`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `generate_with_retry()` connect `API Routes & Orchestration` to `Embeddings & RAG Retrieval`, `SQL Generation`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `retrieve_relevant_rules()` connect `API Routes & Orchestration` to `Embeddings & RAG Retrieval`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SQLValidator` (e.g. with `GenerateRequest` and `GenerateResponse`) actually correct?**
  _`SQLValidator` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Business Rules Retriever (retrieve_relevant_rules)` (e.g. with `Business Rules Indexer (index_business_rules)` and `SQL Generator Prompt Integration (generate_sql)`) actually correct?**
  _`Business Rules Retriever (retrieve_relevant_rules)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `text-to-sql-backend` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API Routes & Orchestration` be split into smaller, more focused modules?**
  _Cohesion score 0.14482758620689656 - nodes in this community are weakly interconnected._