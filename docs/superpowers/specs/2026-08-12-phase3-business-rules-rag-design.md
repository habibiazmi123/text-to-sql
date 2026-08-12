# Phase 3: Business Knowledge RAG — Design Spec

## Overview

Add Business Knowledge RAG to retrieve relevant business definitions during SQL generation. Users ask questions like "Berapa revenue bulan lalu?" and the system retrieves the Revenue business rule to ensure correct SQL generation.

## Data Flow

```
Question
  ↓
Parallel retrieval:
  ├── Schema RAG (existing)     → RELEVANT DATABASE SCHEMA
  └── Business Rules RAG (new)  → BUSINESS RULES
  ↓
Context assembly (combine both)
  ↓
LLM generates SQL (with rules in prompt)
```

## Components

### 1. Business Rules Retriever

**File:** `ai-service/app/rag/rules_retriever.py`

**Function:** `retrieve_relevant_rules(question: str, top_k: int = 5) -> str`

**Hybrid strategy:**
- Embedding search: pgvector similarity on `business_rules.embedding` column
- Keyword match: `ILIKE` on `term` field for exact term matches
- Merge: dedup by `id`, limit to `top_k` total results

**Returns formatted string:**
```
BUSINESS RULES:
- Revenue: Total amount of orders with status = completed and payment status = paid
- Active User: A customer who has placed at least one order in the last 30 days
```

### 2. Business Rules Indexer

**File:** `ai-service/app/rag/rules_indexer.py`

**Function:** `index_business_rules() -> dict`

**Process:**
1. Read all rows from `business_rules` table
2. Embed `"term: definition"` for each rule
3. Store embedding in `business_rules.embedding` column
4. Return count of indexed rules

### 3. API Integration

**Extend `/ai/retrieve`:**
- Add `retrieve_relevant_rules()` call alongside `retrieve_relevant_schema()`
- Return both in response: `schema_context` + `rules_context`

**Extend `/ai/index`:**
- Add `index_business_rules()` call
- Return counts for both schema and rules

### 4. Prompt Integration

**Extend `generate_sql` prompt:**
```
RELEVANT DATABASE SCHEMA:
[existing schema context]

BUSINESS RULES:
- Revenue: Total amount of orders with status = completed and payment status = paid
- Active User: A customer who has placed at least one order in the last 30 days

USER QUESTION: {question}
```

**Rule:** When a business rule exists for a term in the question, use the rule's definition instead of assuming from column names.

## Seed Data

Add 10+ business rules to `backend/seeds/seed.sql`:
- Revenue (existing)
- Active User (existing)
- Monthly Revenue (existing)
- Enterprise Customer (existing)
- Gross Profit: Total revenue minus cost of goods sold
- Net Profit: Gross profit minus operating expenses
- Customer Lifetime Value: Total revenue from a customer over their entire relationship
- Churn Rate: Percentage of customers who stop purchasing in a given period
- Average Order Value: Total revenue divided by number of orders
- Customer Segmentation: Grouping customers by purchase behavior and value

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `ai-service/app/rag/__init__.py` | Create | Package init |
| `ai-service/app/rag/rules_retriever.py` | Create | Hybrid retrieval logic |
| `ai-service/app/rag/rules_indexer.py` | Create | Indexing logic |
| `ai-service/app/api/routes.py` | Modify | Extend `/ai/retrieve` and `/ai/index` |
| `ai-service/app/sql/generator.py` | Modify | Add rules to prompt |
| `ai-service/tests/test_rules_retriever.py` | Create | Unit tests |
| `backend/seeds/seed.sql` | Modify | Add more business rules |

## Testing

- Unit test for `retrieve_relevant_rules()` — mock DB, verify hybrid merge
- Unit test for `index_business_rules()` — verify embedding generation
- Integration test: query "Berapa revenue bulan lalu?" should retrieve Revenue rule

## Dependencies

No new dependencies. Uses existing:
- `sentence-transformers` (embeddings)
- `psycopg2` (database)
- `pgvector` (vector search)
