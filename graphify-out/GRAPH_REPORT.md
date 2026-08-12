# Graph Report - .  (2026-08-12)

## Corpus Check
- Corpus is ~11,389 words - fits in a single context window. You may not need a graph.

## Summary
- 113 nodes · 187 edges · 21 communities (17 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Embeddings & Retrieval
- API Routes
- SQL Validation
- Go Backend
- LLM & SQL Generation
- Health Check
- Query Execution
- Config Management
- Backend Tests
- OpenCode Plugin
- FastAPI App
- Graphify Plugin
- Docker & Dependencies
- Backend Package

## God Nodes (most connected - your core abstractions)
1. `SQLValidator` - 20 edges
2. `QueryService` - 8 edges
3. `generate()` - 7 edges
4. `embed_text()` - 6 edges
5. `embed_texts()` - 6 edges
6. `chat_completion()` - 6 edges
7. `generate_sql()` - 6 edges
8. `summarize()` - 5 edges
9. `retrieve()` - 5 edges
10. `index_schema()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `GenerateRequest` --uses--> `SQLValidator`  [INFERRED]
  ai-service/app/api/routes.py → ai-service/app/sql/validator.py
- `GenerateResponse` --uses--> `SQLValidator`  [INFERRED]
  ai-service/app/api/routes.py → ai-service/app/sql/validator.py
- `ValidateRequest` --uses--> `SQLValidator`  [INFERRED]
  ai-service/app/api/routes.py → ai-service/app/sql/validator.py
- `ValidateResponse` --uses--> `SQLValidator`  [INFERRED]
  ai-service/app/api/routes.py → ai-service/app/sql/validator.py
- `SummarizeRequest` --uses--> `SQLValidator`  [INFERRED]
  ai-service/app/api/routes.py → ai-service/app/sql/validator.py

## Import Cycles
- None detected.

## Communities (21 total, 4 thin omitted)

### Community 0 - "Embeddings & Retrieval"
Cohesion: 0.20
Nodes (12): Config, Settings, index_schema(), embed_text(), embed_texts(), get_model(), retrieve_relevant_schema(), get_schema_entries() (+4 more)

### Community 1 - "API Routes"
Cohesion: 0.26
Nodes (16): generate(), GenerateRequest, GenerateResponse, index(), retrieve(), RetrieveRequest, RetrieveResponse, summarize() (+8 more)

### Community 2 - "SQL Validation"
Cohesion: 0.28
Nodes (10): SQLValidator, ValidationResult, test_allows_select(), test_allows_with(), test_rejects_delete(), test_rejects_drop(), test_rejects_insert(), test_rejects_multiple_statements() (+2 more)

### Community 3 - "Go Backend"
Cohesion: 0.23
Nodes (9): main(), Context, NewQueryHandler(), DB, NewQueryService(), Client, Config, QueryHandler (+1 more)

### Community 4 - "LLM & SQL Generation"
Cohesion: 0.33
Nodes (9): chat_completion(), get_llm_client(), build_sql_prompt(), generate_sql(), parse_llm_sql_response(), test_build_sql_prompt(), test_parse_llm_sql_response(), test_parse_llm_sql_response_fallback() (+1 more)

### Community 5 - "Health Check"
Cohesion: 0.53
Nodes (4): Context, DB, NewHealthHandler(), HealthHandler

### Community 6 - "Query Execution"
Cohesion: 0.40
Nodes (4): QueryRecord, QueryRequest, QueryResponse, Time

### Community 7 - "Config Management"
Cohesion: 0.83
Nodes (3): getEnv(), Load(), Config

### Community 8 - "Backend Tests"
Cohesion: 0.67
Nodes (3): TestHealthEndpoint(), TestQueryEndpointValidation(), T

### Community 9 - "OpenCode Plugin"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Knowledge Gaps
- **6 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Config`, `text-to-sql-backend`, `AI Service Dependencies` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SQLValidator` connect `SQL Validation` to `API Routes`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `main()` connect `Go Backend` to `Health Check`, `Config Management`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `retrieve_relevant_schema()` connect `Embeddings & Retrieval` to `API Routes`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `SQLValidator` (e.g. with `GenerateRequest` and `GenerateResponse`) actually correct?**
  _`SQLValidator` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `Config` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._