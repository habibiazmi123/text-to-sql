# Graph Report - .  (2026-08-11)

## Corpus Check
- Corpus is ~10,804 words - fits in a single context window. You may not need a graph.

## Summary
- 131 nodes · 207 edges · 19 communities (16 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- System Architecture & Requirements
- AI Service API Layer
- Go API Backend
- AI Service Core Logic
- Infrastructure & Dependencies
- SQL Validation & Tests
- Go Health Handler
- Go Query Models
- Go API Tests
- OpenCode Plugin
- Graphify Plugin
- Test Dependencies
- Go Package

## God Nodes (most connected - your core abstractions)
1. `Text-to-SQL + RAG System` - 23 edges
2. `SQLValidator` - 18 edges
3. `Text-to-SQL Phase 1 Implementation Plan` - 14 edges
4. `QueryService` - 8 edges
5. `Text-to-SQL + RAG System Design Spec` - 8 edges
6. `generate()` - 6 edges
7. `chat_completion()` - 6 edges
8. `generate_sql()` - 6 edges
9. `Business Knowledge RAG` - 6 edges
10. `summarize()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Text-to-SQL + RAG System Design Spec` --references--> `Text-to-SQL + RAG System`  [EXTRACTED]
  docs/superpowers/specs/2026-08-11-text-to-sql-design.md → PRD.md
- `openai` --implements--> `Text-to-SQL Generation`  [INFERRED]
  ai-service/requirements.txt → PRD.md
- `sqlparse` --implements--> `SQL Validation Pipeline`  [INFERRED]
  ai-service/requirements.txt → PRD.md
- `psycopg2-binary` --implements--> `PostgreSQL`  [INFERRED]
  ai-service/requirements.txt → PRD.md
- `Text-to-SQL Phase 1 Implementation Plan` --references--> `FastAPI`  [EXTRACTED]
  docs/superpowers/plans/2026-08-11-text-to-sql-phase1.md → ai-service/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **RAG Retrieval Pipeline** — prd_schema_rag, prd_business_knowledge_rag, prd_sql_example_rag, prd_rag_retrieval_strategy, prd_hybrid_retrieval [EXTRACTED 1.00]
- **Text-to-SQL Pipeline (Natural Language → SQL → Answer)** — prd_text_to_sql, prd_schema_introspection, prd_sql_generation, prd_sql_validation_pipeline, prd_query_execution, prd_result_processing [EXTRACTED 1.00]
- **Core Technology Stack (Go + Python + PostgreSQL)** — prd_postgresql, prd_gorm, docker_compose_postgres, docker_compose_go_api, docker_compose_ai_service [EXTRACTED 1.00]

## Communities (19 total, 3 thin omitted)

### Community 0 - "System Architecture & Requirements"
Cohesion: 0.15
Nodes (20): Business Knowledge RAG, Business Rules as First-Class RAG Documents, Clarification, Conversation Context, Evaluation, GORM, Hybrid Retrieval, LangGraph (+12 more)

### Community 1 - "AI Service API Layer"
Cohesion: 0.22
Nodes (15): generate(), GenerateRequest, GenerateResponse, index(), summarize(), SummarizeRequest, SummarizeResponse, validate() (+7 more)

### Community 2 - "Go API Backend"
Cohesion: 0.18
Nodes (12): main(), getEnv(), Load(), Context, NewQueryHandler(), DB, NewQueryService(), Client (+4 more)

### Community 3 - "AI Service Core Logic"
Cohesion: 0.22
Nodes (12): Config, Settings, chat_completion(), get_llm_client(), build_sql_prompt(), generate_sql(), parse_llm_sql_response(), test_build_sql_prompt() (+4 more)

### Community 4 - "Infrastructure & Dependencies"
Cohesion: 0.24
Nodes (16): FastAPI, openai, psycopg2-binary, pydantic-settings, sqlparse, ai-service service, go-api service, postgres service (+8 more)

### Community 5 - "SQL Validation & Tests"
Cohesion: 0.28
Nodes (10): SQLValidator, ValidationResult, test_allows_select(), test_allows_with(), test_rejects_delete(), test_rejects_drop(), test_rejects_insert(), test_rejects_multiple_statements() (+2 more)

### Community 6 - "Go Health Handler"
Cohesion: 0.53
Nodes (4): Context, DB, NewHealthHandler(), HealthHandler

### Community 7 - "Go Query Models"
Cohesion: 0.40
Nodes (4): QueryRecord, QueryRequest, QueryResponse, Time

### Community 8 - "Go API Tests"
Cohesion: 0.67
Nodes (3): TestHealthEndpoint(), TestQueryEndpointValidation(), T

### Community 9 - "OpenCode Plugin"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Knowledge Gaps
- **18 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `Config`, `text-to-sql-backend`, `Query Execution` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Text-to-SQL + RAG System` connect `System Architecture & Requirements` to `Infrastructure & Dependencies`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `SQLValidator` connect `SQL Validation & Tests` to `AI Service API Layer`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `main()` connect `Go API Backend` to `Go Health Handler`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `SQLValidator` (e.g. with `GenerateRequest` and `GenerateResponse`) actually correct?**
  _`SQLValidator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `Config` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `System Architecture & Requirements` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._