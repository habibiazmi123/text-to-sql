# Build a Production-Grade Text-to-SQL + RAG System

Build a production-grade **Text-to-SQL system using RAG** that allows users to ask questions in natural language and receive answers based on data from PostgreSQL.

## Goal

The system should convert:

> Natural language → relevant database context → SQL → validation → execution → natural language answer

Example:

```text
User:
"Berapa total revenue bulan lalu berdasarkan region?"

        ↓

RAG retrieves:
- orders table
- payments table
- regions table
- relevant relationships
- revenue business definition
- similar SQL examples

        ↓

LLM generates SQL

        ↓

SQL validation

        ↓

Execute against PostgreSQL

        ↓

Return:
"Total revenue bulan lalu adalah Rp 2.4 Miliar.
Region Jawa Barat menyumbang Rp 800 Juta..."
```

---

# Architecture

Use this architecture:

```text
                    ┌──────────────┐
                    │   Frontend   │
                    │   Next.js    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   API / Go   │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Text-to-SQL Agent    │
              └────────────┬───────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    Schema RAG       Business RAG      SQL Examples
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                          LLM
                           │
                           ▼
                    SQL Validation
                           │
                           ▼
                    Query PostgreSQL
                           │
                           ▼
                    Result Validation
                           │
                           ▼
                  Natural Language Answer
```

---

# Technology Stack

Use:

### Backend

* Go
* PostgreSQL
* pgvector
* GORM
* Redis
* REST API

### AI / RAG

* Python
* FastAPI
* LangGraph
* Embedding model
* LLM provider should be configurable
* Support OpenAI-compatible APIs

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* TanStack Query

### Infrastructure

* Docker Compose
* PostgreSQL + pgvector
* Redis
* Go API
* Python AI service

---

# Core Features

## 1. Schema Introspection

Automatically inspect PostgreSQL metadata.

Retrieve:

```text
tables
columns
column types
primary keys
foreign keys
indexes
relationships
```

Example:

```json
{
  "table": "orders",
  "description": "Customer orders",
  "columns": [
    {
      "name": "id",
      "type": "uuid",
      "description": "Order identifier"
    },
    {
      "name": "customer_id",
      "type": "uuid",
      "description": "Customer identifier"
    },
    {
      "name": "total_amount",
      "type": "numeric",
      "description": "Total order amount"
    }
  ],
  "relationships": [
    {
      "column": "customer_id",
      "references": "customers.id"
    }
  ]
}
```

Store the metadata in a dedicated RAG collection.

---

# 2. Schema RAG

Create embeddings for database metadata.

The system should retrieve only relevant tables and columns instead of sending the entire database schema to the LLM.

Example:

```text
User:
"Revenue customer enterprise bulan lalu"

Retrieve:

customers
orders
payments

Instead of:

500 database tables
```

Use pgvector for similarity search.

---

# 3. Business Knowledge RAG

Create a knowledge base containing business definitions.

Example:

```text
Revenue:
Revenue means the total amount of successfully paid orders.

Active User:
A user who has logged in within the last 30 days.

Churned Customer:
A customer without a successful transaction for 90 days.
```

The LLM must use these definitions when generating SQL.

Important:

**Do not assume business definitions from table or column names when a business rule exists.**

---

# 4. SQL Example RAG

Store verified question → SQL examples.

Example:

```json
{
  "question": "What is monthly revenue?",
  "sql": "SELECT ...",
  "description": "Calculate monthly paid revenue"
}
```

Retrieve similar examples before SQL generation.

The examples should guide the model but must not be blindly copied.

---

# 5. Text-to-SQL Generation

Create a structured prompt for the LLM.

The LLM receives:

```text
USER QUESTION

RELEVANT DATABASE SCHEMA

RELATIONSHIPS

BUSINESS RULES

SIMILAR SQL EXAMPLES
```

The LLM must return structured JSON:

```json
{
  "sql": "SELECT ...",
  "reasoning": "Short explanation",
  "tables_used": ["orders", "payments"],
  "confidence": 0.92
}
```

Do not expose chain-of-thought reasoning to the user.

Use a short explanation or query summary instead.

---

# 6. SQL Security

This is mandatory.

The system must be **read-only**.

Reject:

```sql
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
```

Only allow safe queries such as:

```sql
SELECT
WITH
```

Also implement:

* SQL parser validation
* query timeout
* row limit
* statement timeout
* allowed schema whitelist
* table-level permissions
* column-level permissions where necessary
* protection against SQL injection
* protection against prompt injection
* prevent access to PostgreSQL system tables

Never execute arbitrary SQL generated by the LLM without validation.

---

# 7. SQL Validation Pipeline

Implement:

```text
Generated SQL
      ↓
Parse SQL
      ↓
Check statement type
      ↓
Check allowed tables
      ↓
Check allowed columns
      ↓
Check dangerous operations
      ↓
EXPLAIN
      ↓
Estimate query cost
      ↓
Execute with timeout
```

If validation fails:

```text
SQL
 ↓
Validation Error
 ↓
LLM receives error
 ↓
Generate corrected SQL
 ↓
Validate again
```

Limit automatic retries to 2–3 attempts.

---

# 8. Query Execution

Execute SQL using a dedicated read-only PostgreSQL user.

Example:

```text
application_user
    └── read/write application database

text_to_sql_user
    └── SELECT only
```

Never allow the AI service to use database credentials with write permissions.

---

# 9. Result Processing

After executing SQL:

```text
SQL Result
    ↓
Result Analyzer
    ↓
LLM
    ↓
Natural Language Answer
```

Example:

```text
SQL result:

region       revenue
Jawa Barat   800000000
Jawa Timur   600000000
Jakarta      1000000000
```

Answer:

```text
Total revenue bulan lalu adalah Rp2,4 miliar.

Kontributor terbesar:
1. Jakarta — Rp1,0 miliar
2. Jawa Barat — Rp800 juta
3. Jawa Timur — Rp600 juta
```

---

# 10. Clarification

If the question is ambiguous, do not generate dangerous assumptions.

Example:

```text
User:
"Berapa revenue?"

AI:
"Revenue untuk periode apa?
- Hari ini
- Minggu ini
- Bulan ini
- Custom"
```

Another example:

```text
User:
"Berapa user aktif?"

AI:
"Apakah 'user aktif' mengikuti definisi:
user yang login dalam 30 hari terakhir?"
```

---

# 11. Conversation Context

Support follow-up questions.

Example:

````text
User:
"Berapa revenue bulan lalu?"

AI:
"Rp2.4 Miliar"

User:
"Bagaimana dengan bulan sebelumnya?"

AI should understand:

```text
"bulan sebelumnya"
=
previous month relative to the previously discussed period
````

Do not rely only on vector search for conversational context.

Maintain structured conversation state.

---

# 12. RAG Retrieval Strategy

Do not use only semantic similarity.

Use hybrid retrieval where appropriate:

```text
User Question
      │
      ├── Vector Search
      │
      ├── Keyword Search
      │
      └── Metadata Filtering
              │
              ▼
        Candidate Context
              │
              ▼
           Reranker
              │
              ▼
       Final Context
```

Prioritize:

1. Relevant tables
2. Relevant columns
3. Relationships
4. Business rules
5. Similar SQL examples

Avoid retrieving unrelated schema information.

---

# 13. Query Planning

Before generating SQL, create an intermediate structured plan.

Example:

```json
{
  "intent": "revenue_analysis",
  "metrics": ["revenue"],
  "dimensions": ["region"],
  "filters": [
    {
      "field": "date",
      "value": "last_month"
    }
  ],
  "required_entities": [
    "orders",
    "payments",
    "regions"
  ]
}
```

Then:

```text
User Question
      ↓
Intent / Query Plan
      ↓
RAG Retrieval
      ↓
SQL Generation
```

This should improve reliability.

---

# 14. Observability

Track every Text-to-SQL request.

Log:

```text
request_id
user_id
question
retrieved_tables
retrieved_business_rules
retrieved_examples
generated_sql
validation_result
execution_time
rows_returned
retry_count
final_answer
```

Do not log sensitive user data unnecessarily.

Add metrics:

```text
text_to_sql_success_rate
sql_validation_failure_rate
sql_execution_failure_rate
average_query_latency
rag_retrieval_latency
llm_latency
average_tokens
query_retry_rate
```

---

# 15. Evaluation

Create an evaluation dataset.

Example:

```json
{
  "question": "Berapa revenue bulan lalu?",
  "expected_sql": "SELECT ...",
  "expected_result": 2400000000
}
```

Evaluate:

```text
SQL correctness
Execution correctness
Result correctness
Schema retrieval accuracy
Business-rule retrieval accuracy
Latency
Token usage
```

Important:

Do not evaluate only whether the generated SQL looks correct.

Actually execute the SQL against a test database and compare the result.

---

# 16. Project Structure

Use a clean architecture.

### Go

```text
backend/
├── cmd/
│   └── api/
├── internal/
│   ├── domain/
│   ├── handler/
│   ├── service/
│   ├── repository/
│   ├── middleware/
│   └── config/
├── migrations/
├── tests/
├── go.mod
└── Makefile
```

### Python

```text
ai-service/
├── app/
│   ├── api/
│   ├── agents/
│   ├── rag/
│   ├── embeddings/
│   ├── sql/
│   ├── llm/
│   ├── models/
│   └── config/
├── tests/
├── requirements.txt
└── Dockerfile
```

---

# 17. Docker Compose

Provide a development environment containing:

```text
postgres + pgvector
redis
go-api
python-ai-service
nextjs
```

Everything must be runnable with:

```bash
docker compose up
```

Also provide:

```bash
make dev
make test
make lint
make migrate
make seed
make rag-index
```

---

# 18. Development Approach

Build incrementally.

### Phase 1

Build:

```text
PostgreSQL
     ↓
Schema introspection
     ↓
LLM
     ↓
SQL
     ↓
PostgreSQL
```

No RAG yet.

### Phase 2

Add:

```text
Schema RAG
```

### Phase 3

Add:

```text
Business Knowledge RAG
```

### Phase 4

Add:

```text
SQL Example RAG
```

### Phase 5

Add:

```text
SQL validation
EXPLAIN
read-only execution
query timeout
```

### Phase 6

Add:

```text
query planning
retry loop
clarification
conversation context
```

### Phase 7

Add:

```text
observability
evaluation
metrics
security
```

---

# Important Engineering Rules

1. Do not dump the entire database schema into every LLM prompt.
2. Do not execute unvalidated LLM-generated SQL.
3. Use a read-only database user.
4. Treat business definitions as first-class RAG documents.
5. Retrieve relevant schema before generating SQL.
6. Prefer structured JSON output from the LLM.
7. Validate SQL before execution.
8. Limit automatic SQL correction retries.
9. Support query timeouts and result limits.
10. Keep LLM provider configurable.
11. Never expose chain-of-thought reasoning.
12. Write tests for every major component.
13. Build an evaluation dataset with known questions and expected results.
14. Optimize retrieval before increasing LLM complexity.
15. Prefer deterministic validation over asking the LLM to "be careful."

---

# Expected Final User Experience

The user should be able to type:

```text
Tampilkan 10 customer dengan revenue terbesar
dalam 3 bulan terakhir
```

and receive:

```text
Top 10 Customer — 3 Bulan Terakhir

1. PT ABC       Rp1.2 M
2. PT XYZ       Rp980 Jt
3. PT DEF       Rp870 Jt
...

Total revenue:
Rp8.4 M
```

The UI should also optionally show:

```text
Generated SQL
↓
SELECT ...

Tables used
↓
customers
orders
payments

Execution time
↓
182 ms
```

The generated SQL should be hidden by default and available through an expandable section.

---

# Deliverables

Implement the complete working project with:

* Go API
* Python AI/RAG service
* PostgreSQL + pgvector
* Redis
* Next.js UI
* Docker Compose
* Database migrations
* Schema indexing pipeline
* RAG retrieval
* Text-to-SQL generation
* SQL validation
* Read-only execution
* Result summarization
* Conversation context
* Retry mechanism
* Observability
* Tests
* Evaluation dataset
* Makefile
* README with setup instructions

Start by designing the architecture and database schema.

Then implement Phase 1 first.

Do not build everything at once. After each phase, make sure the system is runnable and tested before proceeding to the next phase.
