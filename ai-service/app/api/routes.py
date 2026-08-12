from fastapi import APIRouter
from pydantic import BaseModel
from app.schema.introspector import get_schema_context
from app.sql.generator import generate_sql
from app.sql.validator import SQLValidator

router = APIRouter(prefix="/ai", tags=["ai"])
validator = SQLValidator()


class GenerateRequest(BaseModel):
    question: str


class GenerateResponse(BaseModel):
    sql: str
    reasoning: str
    tables_used: list[str]
    confidence: float
    is_valid: bool
    validation_error: str = ""


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


class RetryResponse(BaseModel):
    sql: str
    reasoning: str
    tables_used: list[str]
    confidence: float
    is_valid: bool
    validation_error: str = ""
    retries_used: int = 0


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
    try:
        from app.embeddings.retriever import retrieve_relevant_schema
        schema = retrieve_relevant_schema(req.question)
    except Exception:
        schema = get_schema_context()

    if not schema.strip():
        schema = get_schema_context()

    try:
        from app.rag.rules_retriever import retrieve_relevant_rules
        rules = retrieve_relevant_rules(req.question)
    except Exception:
        rules = ""

    try:
        from app.rag.examples_retriever import retrieve_similar_examples
        examples = retrieve_similar_examples(req.question)
    except Exception:
        examples = ""

    result = generate_sql(req.question, schema, rules, examples)
    validation = validator.validate(result.get("sql", ""))

    return GenerateResponse(
        sql=result.get("sql", ""),
        reasoning=result.get("reasoning", ""),
        tables_used=result.get("tables_used", []),
        confidence=result.get("confidence", 0.0),
        is_valid=validation.is_valid,
        validation_error=validation.error,
    )


@router.post("/generate-with-retry", response_model=RetryResponse)
async def generate_with_retry(req: RetryRequest):
    """Generate SQL with EXPLAIN validation and retry on failure."""
    try:
        from app.embeddings.retriever import retrieve_relevant_schema
        schema = retrieve_relevant_schema(req.question)
    except Exception:
        schema = get_schema_context()

    if not schema.strip():
        schema = get_schema_context()

    try:
        from app.rag.rules_retriever import retrieve_relevant_rules
        rules = retrieve_relevant_rules(req.question)
    except Exception:
        rules = ""

    try:
        from app.rag.examples_retriever import retrieve_similar_examples
        examples = retrieve_similar_examples(req.question)
    except Exception:
        examples = ""

    last_sql = ""
    last_reasoning = ""
    last_tables_used = []
    last_confidence = 0.0
    last_error = ""

    for attempt in range(req.max_retries + 1):
        error_context = ""
        if last_error:
            error_context = f"\n\nPREVIOUS ATTEMPT FAILED:\nSQL: {last_sql}\nError: {last_error}\n\nFix the SQL query based on this error."

        user_prompt = build_sql_prompt(req.question, schema, rules, examples) + error_context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        response = chat_completion(messages)
        result = parse_llm_sql_response(response)

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
    )


@router.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    result = validator.validate(req.sql)
    return ValidateResponse(
        is_valid=result.is_valid,
        error=result.error,
        sql=result.sql,
    )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    from app.llm.client import chat_completion

    result_str = str(req.result)
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Summarize SQL query results in natural language. Use Indonesian language. Be concise."},
        {"role": "user", "content": f"Question: {req.question}\nSQL: {req.sql}\nResult: {result_str}\n\nProvide a concise natural language answer."},
    ]
    answer = chat_completion(messages)
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
