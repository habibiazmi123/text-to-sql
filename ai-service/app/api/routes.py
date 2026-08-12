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


class RetrieveRequest(BaseModel):
    question: str
    top_k: int = 10


class RetrieveResponse(BaseModel):
    schema_context: str
    tables_found: list[str]


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    try:
        from app.embeddings.retriever import retrieve_relevant_schema
        schema = retrieve_relevant_schema(req.question)
    except Exception:
        schema = get_schema_context()

    if not schema.strip():
        schema = get_schema_context()

    result = generate_sql(req.question, schema)
    validation = validator.validate(result.get("sql", ""))

    return GenerateResponse(
        sql=result.get("sql", ""),
        reasoning=result.get("reasoning", ""),
        tables_used=result.get("tables_used", []),
        confidence=result.get("confidence", 0.0),
        is_valid=validation.is_valid,
        validation_error=validation.error,
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
    import psycopg2
    from app.config import settings

    schema = retrieve_relevant_schema(req.question, req.top_k)

    tables_found = []
    for line in schema.split("\n"):
        if line.startswith("TABLE: "):
            tables_found.append(line[7:])

    return RetrieveResponse(schema_context=schema, tables_found=tables_found)


@router.post("/index")
async def index():
    from app.embeddings.indexer import index_schema
    result = index_schema()
    return {"status": "ok", **result}
