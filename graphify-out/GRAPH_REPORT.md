# Graph Report - .  (2026-08-12)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 355 nodes · 534 edges · 35 communities (24 shown, 11 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fdfc4488`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Chat UI
- npm Dependencies
- UI Components
- shadcn Config
- Scripts & DevDeps
- TypeScript Config
- App Layout & Theme
- LLM Client
- Go Backend Tests
- OpenCode Plugin Config
- Embeddings & RAG Index
- Graphify Plugin
- PostCSS Config
- httpx Dep
- pydantic-settings Dep
- uvicorn Dep
- Go DB
- Go Config
- Docker Compose
- Go Module
- API Routes & Validators
- Go Query Service
- Business Rules RAG
- SQL Generation
- Query Models
- ESLint Config
- Next.js Config

## God Nodes (most connected - your core abstractions)
1. `cn()` - 31 edges
2. `SQLValidator` - 23 edges
3. `compilerOptions` - 16 edges
4. `embed_text()` - 12 edges
5. `generate_with_retry()` - 11 edges
6. `Business Rules Retriever (retrieve_relevant_rules)` - 10 edges
7. `generate()` - 9 edges
8. `retrieve_relevant_rules()` - 9 edges
9. `embed_texts()` - 8 edges
10. `include` - 8 edges

## Surprising Connections (you probably didn't know these)
- `RootLayout()` --calls--> `cn()`  [EXTRACTED]
  app/layout.tsx → lib/utils.ts
- `BotAvatar()` --calls--> `cn()`  [EXTRACTED]
  components/chat/chat.tsx → lib/utils.ts
- `Shimmer()` --calls--> `cn()`  [EXTRACTED]
  components/chat/chat.tsx → lib/utils.ts
- `API Integration (/ai/retrieve, /ai/index)` --references--> `FastAPI (>=0.111.0)`  [INFERRED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt
- `SQL Generator Prompt Integration (generate_sql)` --references--> `SQLParse (>=0.5.0)`  [INFERRED]
  docs/superpowers/specs/2026-08-12-phase3-business-rules-rag-design.md → ai-service/requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Business Knowledge RAG Pipeline (parallel retrieval -> context assembly -> SQL generation)** — repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_schema_rag, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_retriever, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_api_integration, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_sql_generator_prompt_integration [EXTRACTED 1.00]
- **Business Rules Indexing to Retrieval Data Flow** — repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_indexer, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_table, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_business_rules_retriever, repo::docs_superpowers_specs_2026_08_12_phase3_business_rules_rag_design_seed_business_rules [EXTRACTED 1.00]

## Communities (35 total, 11 thin omitted)

### Community 0 - "Chat UI"
Cohesion: 0.08
Nodes (24): POST(), Answer(), isRows(), BotAvatar(), Chat(), ChatItem, EXAMPLES, PHASES (+16 more)

### Community 1 - "npm Dependencies"
Cohesion: 0.06
Nodes (31): axios, class-variance-authority, clsx, lucide-react, next, next-themes, dependencies, axios (+23 more)

### Community 2 - "UI Components"
Cohesion: 0.13
Nodes (24): ChatInput(), ChatInputProps, cellText(), ResultTable(), Button(), buttonVariants, Card(), CardAction() (+16 more)

### Community 3 - "shadcn Config"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 4 - "Scripts & DevDeps"
Cohesion: 0.06
Nodes (32): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, prettier, prettier-plugin-tailwindcss, tailwindcss (+24 more)

### Community 5 - "TypeScript Config"
Cohesion: 0.07
Nodes (29): dom, dom.iterable, esnext, **/*.mts, next.config.ts, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts (+21 more)

### Community 6 - "App Layout & Theme"
Cohesion: 0.23
Nodes (8): fontMono, geist, RootLayout(), Providers(), isTypingTarget(), ThemeHotkey(), ThemeProvider(), Toaster()

### Community 7 - "LLM Client"
Cohesion: 0.83
Nodes (3): chat_completion(), get_llm_client(), OpenAI

### Community 8 - "Go Backend Tests"
Cohesion: 0.67
Nodes (3): TestHealthEndpoint(), TestQueryEndpointValidation(), T

### Community 9 - "OpenCode Plugin Config"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 10 - "Embeddings & RAG Index"
Cohesion: 0.13
Nodes (20): index(), Config, Settings, index_schema(), embed_text(), embed_texts(), get_model(), retrieve_relevant_schema() (+12 more)

### Community 27 - "API Routes & Validators"
Cohesion: 0.12
Nodes (32): generate(), generate_with_retry(), GenerateRequest, GenerateResponse, Generate SQL with EXPLAIN validation and retry on failure., retrieve(), RetrieveRequest, RetrieveResponse (+24 more)

### Community 28 - "Go Query Service"
Cohesion: 0.13
Nodes (15): main(), getEnv(), Load(), Context, DB, NewHealthHandler(), Context, NewQueryHandler() (+7 more)

### Community 29 - "Business Rules RAG"
Cohesion: 0.22
Nodes (16): FastAPI (>=0.111.0), OpenAI SDK (>=1.35.0), psycopg2-binary (>=2.9.12), sentence-transformers (>=3.1.0), SQLParse (>=0.5.0), PyTorch (>=2.0.0), API Integration (/ai/retrieve, /ai/index), Business Knowledge RAG (+8 more)

### Community 30 - "SQL Generation"
Cohesion: 0.50
Nodes (6): build_sql_prompt(), generate_sql(), parse_llm_sql_response(), test_build_sql_prompt(), test_parse_llm_sql_response(), test_parse_llm_sql_response_fallback()

### Community 31 - "Query Models"
Cohesion: 0.38
Nodes (5): ChatMessage, QueryRecord, QueryRequest, QueryResponse, Time

## Knowledge Gaps
- **105 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `text-to-sql-backend`, `Docker Compose Configuration`, `Config` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cn()` connect `UI Components` to `Chat UI`, `App Layout & Theme`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `dependencies` connect `npm Dependencies` to `Scripts & DevDeps`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SQLValidator` (e.g. with `GenerateRequest` and `GenerateResponse`) actually correct?**
  _`SQLValidator` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `text-to-sql-backend` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Chat UI` be split into smaller, more focused modules?**
  _Cohesion score 0.08258258258258258 - nodes in this community are weakly interconnected._
- **Should `npm Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `UI Components` be split into smaller, more focused modules?**
  _Cohesion score 0.1310483870967742 - nodes in this community are weakly interconnected._