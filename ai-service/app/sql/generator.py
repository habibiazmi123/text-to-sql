import json
from app.llm.client import chat_completion

SYSTEM_PROMPT = """You are a SQL expert. Generate PostgreSQL queries based on user questions.

Rules:
1. Only generate SELECT or WITH (CTE) queries
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
3. Return valid JSON with these fields:
   - sql: the SQL query
   - reasoning: short explanation
   - tables_used: list of table names
   - confidence: 0.0 to 1.0
4. Use PostgreSQL syntax
5. Use proper JOINs based on foreign keys
6. Return results in the exact JSON format"""


def build_sql_prompt(question: str, schema: str, rules: str = "", examples: str = "") -> str:
    parts = [schema]

    if rules:
        parts.append(rules)

    if examples:
        parts.append(examples)

    parts.append(f"USER QUESTION: {question}")
    parts.append("""Generate the SQL query. Return ONLY valid JSON:
{"sql": "...", "reasoning": "...", "tables_used": [...], "confidence": 0.0}""")

    return "\n\n".join(parts)


def parse_llm_sql_response(response: str) -> dict:
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"sql": response.strip(), "reasoning": "", "tables_used": [], "confidence": 0.5}


def generate_sql(question: str, schema: str, rules: str = "", examples: str = "") -> dict:
    user_prompt = build_sql_prompt(question, schema, rules, examples)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    response = chat_completion(messages)
    return parse_llm_sql_response(response)
