from app.sql.generator import build_sql_prompt, parse_llm_sql_response


def test_build_sql_prompt():
    schema = "TABLE: customers\n  id uuid\n  name varchar"
    question = "How many customers?"
    prompt = build_sql_prompt(question, schema)
    assert "How many customers?" in prompt
    assert "customers" in prompt


def test_parse_llm_sql_response():
    response = '{"sql": "SELECT COUNT(*) FROM customers", "reasoning": "count customers", "tables_used": ["customers"], "confidence": 0.95}'
    result = parse_llm_sql_response(response)
    assert result["sql"] == "SELECT COUNT(*) FROM customers"
    assert result["tables_used"] == ["customers"]


def test_parse_llm_sql_response_fallback():
    response = "SELECT * FROM customers"
    result = parse_llm_sql_response(response)
    assert result["sql"] == "SELECT * FROM customers"
