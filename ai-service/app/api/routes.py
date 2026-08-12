import json
import time

from fastapi import APIRouter
from pydantic import BaseModel
from app.llm.client import chat_completion
from app.schema.introspector import get_schema_context
from app.sql.generator import SYSTEM_PROMPT, build_sql_prompt, generate_sql, parse_llm_sql_response
from app.sql.validator import SQLValidator

router = APIRouter(prefix="/ai", tags=["ai"])
validator = SQLValidator()


def retrieve_context(question: str) -> tuple[str, str, str, float]:
    """Returns (schema, rules, examples, elapsed_ms). Broad excepts keep
    retrieval resilient - every source is independently optional."""
    start = time.perf_counter()

    try:
        from app.embeddings.retriever import retrieve_relevant_schema
        schema = retrieve_relevant_schema(question)
    except Exception:
        schema = ""
    if not schema.strip():
        try:
            schema = get_schema_context()
        except Exception:
            schema = ""

    try:
        from app.rag.rules_retriever import retrieve_relevant_rules
        rules = retrieve_relevant_rules(question)
    except Exception:
        rules = ""

    try:
        from app.rag.examples_retriever import retrieve_similar_examples
        examples = retrieve_similar_examples(question)
    except Exception:
        examples = ""

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return schema, rules, examples, elapsed_ms


class GenerateRequest(BaseModel):
    question: str


class GenerateResponse(BaseModel):
    sql: str
    reasoning: str
    tables_used: list[str]
    confidence: float
    is_valid: bool
    validation_error: str = ""
    retrieval_ms: int = 0
    llm_ms: int = 0
    tokens_used: int = 0


class ValidateRequest(BaseModel):
    sql: str


class ValidateResponse(BaseModel):
    is_valid: bool
    error: str = ""
    sql: str = ""


class SummarizeRequest(BaseModel):
    question: str
    sql: str
    result: list[dict]


class SummarizeResponse(BaseModel):
    answer: str


class RetryRequest(BaseModel):
    question: str
    max_retries: int = 2
    history: list[dict] = []


class RetryResponse(BaseModel):
    sql: str
    reasoning: str
    tables_used: list[str]
    confidence: float
    is_valid: bool
    validation_error: str = ""
    retries_used: int = 0
    needs_clarify: bool = False
    clarify_text: str = ""
    retrieval_ms: int = 0
    llm_ms: int = 0
    tokens_used: int = 0


class RetrieveRequest(BaseModel):
    question: str
    top_k: int = 10


class RetrieveResponse(BaseModel):
    schema_context: str
    tables_found: list[str]
    rules_context: str
    examples_context: str


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    schema, rules, examples, retrieval_ms = retrieve_context(req.question)

    llm_start = time.perf_counter()
    result = generate_sql(req.question, schema, rules, examples)
    llm_ms = int((time.perf_counter() - llm_start) * 1000)

    validation = validator.validate(result.get("sql", ""))

    return GenerateResponse(
        sql=result.get("sql", ""),
        reasoning=result.get("reasoning", ""),
        tables_used=result.get("tables_used", []),
        confidence=result.get("confidence", 0.0),
        is_valid=validation.is_valid,
        validation_error=validation.error,
        retrieval_ms=retrieval_ms,
        llm_ms=llm_ms,
        tokens_used=result.get("tokens_used", 0),
    )


@router.post("/generate-with-retry", response_model=RetryResponse)
async def generate_with_retry(req: RetryRequest):
    """Generate SQL with EXPLAIN validation and retry on failure."""
    schema, rules, examples, retrieval_ms = retrieve_context(req.question)

    history_text = ""
    if req.history:
        history_lines = []
        for msg in req.history[-6:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.get('content', '')}")
        history_text = "\n\nCONVERSATION HISTORY:\n" + "\n".join(history_lines)

    last_sql = ""
    last_reasoning = ""
    last_tables_used = []
    last_confidence = 0.0
    last_error = ""
    llm_ms = 0
    tokens_used = 0

    for attempt in range(req.max_retries + 1):
        error_context = ""
        if last_error:
            error_context = f"\n\nPREVIOUS ATTEMPT FAILED:\nSQL: {last_sql}\nError: {last_error}\n\nFix the SQL query based on this error."

        user_prompt = build_sql_prompt(req.question, schema, rules, examples) + history_text + error_context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        llm_start = time.perf_counter()
        response, stats = chat_completion(messages)
        llm_ms += int((time.perf_counter() - llm_start) * 1000)
        tokens_used += stats.get("tokens", 0)
        result = parse_llm_sql_response(response)

        if result.get("needs_clarify"):
            return RetryResponse(
                sql="",
                reasoning="",
                tables_used=[],
                confidence=0.0,
                is_valid=False,
                needs_clarify=True,
                clarify_text=result.get("clarify_text", "Could you clarify your question?"),
                retries_used=attempt,
                retrieval_ms=retrieval_ms,
                llm_ms=llm_ms,
                tokens_used=tokens_used,
            )

        last_sql = result.get("sql", "")
        last_reasoning = result.get("reasoning", "")
        last_tables_used = result.get("tables_used", [])
        last_confidence = result.get("confidence", 0.0)

        validation = validator.validate_with_explain(last_sql)
        if validation.is_valid:
            return RetryResponse(
                sql=last_sql,
                reasoning=last_reasoning,
                tables_used=last_tables_used,
                confidence=last_confidence,
                is_valid=True,
                retries_used=attempt,
                retrieval_ms=retrieval_ms,
                llm_ms=llm_ms,
                tokens_used=tokens_used,
            )

        last_error = validation.error

    return RetryResponse(
        sql=last_sql,
        reasoning=last_reasoning,
        tables_used=last_tables_used,
        confidence=last_confidence,
        is_valid=False,
        validation_error=last_error,
        retries_used=req.max_retries,
        retrieval_ms=retrieval_ms,
        llm_ms=llm_ms,
        tokens_used=tokens_used,
    )


@router.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    result = validator.validate(req.sql)
    return ValidateResponse(
        is_valid=result.is_valid,
        error=result.error,
        sql=result.sql,
    )


MAX_SUMMARIZE_CHARS = 6000  # ponytail: cap result size, full result far exceeds context window


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    result_str = json.dumps(req.result, ensure_ascii=False)
    if len(result_str) > MAX_SUMMARIZE_CHARS:
        result_str = result_str[:MAX_SUMMARIZE_CHARS] + f"\n... (truncated, {len(req.result)} rows total)"
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Summarize SQL query results in natural language. Use Indonesian language. Be concise."},
        {"role": "user", "content": f"Question: {req.question}\nSQL: {req.sql}\nResult: {result_str}\n\nProvide a concise natural language answer."},
    ]
    answer, _ = chat_completion(messages)
    return SummarizeResponse(answer=answer)


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest):
    from app.embeddings.retriever import retrieve_relevant_schema
    from app.rag.rules_retriever import retrieve_relevant_rules
    from app.rag.examples_retriever import retrieve_similar_examples

    schema = retrieve_relevant_schema(req.question, req.top_k)
    rules = retrieve_relevant_rules(req.question)
    examples = retrieve_similar_examples(req.question)

    tables_found = []
    for line in schema.split("\n"):
        if line.startswith("TABLE: "):
            tables_found.append(line[7:])

    return RetrieveResponse(schema_context=schema, tables_found=tables_found, rules_context=rules, examples_context=examples)


@router.post("/index")
async def index():
    from app.embeddings.indexer import index_schema
    from app.rag.rules_indexer import index_business_rules
    from app.rag.examples_indexer import index_sql_examples
    schema_result = index_schema()
    rules_result = index_business_rules()
    examples_result = index_sql_examples()
    return {"status": "ok", **schema_result, **rules_result, **examples_result}
