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


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
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


@router.post("/index")
async def index():
    return {"status": "indexing not implemented in Phase 1"}
