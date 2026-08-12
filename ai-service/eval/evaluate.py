#!/usr/bin/env python3
"""Evaluation harness for the text-to-SQL pipeline.

Runs each dataset case through retrieval -> generation -> validation -> execution
and reports PRD §15 metrics: SQL correctness, execution correctness, schema and
business-rule retrieval accuracy, latency, and token usage.

Usage: python eval/evaluate.py [path/to/dataset.json]
"""

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.sql.generator import parse_llm_sql_response, generate_sql  # noqa: E402
from app.sql.validator import SQLValidator  # noqa: E402
from app.api.routes import retrieve_context  # noqa: E402

DATASET = Path(__file__).resolve().parent / "dataset.json"


def evaluate_case(validator: SQLValidator, case: dict, conn_uri: str) -> dict:
    question = case["question"]
    start = time.perf_counter()
    schema, rules, examples, retrieval_ms = retrieve_context(question)
    retrieval_ms = float(retrieval_ms)

    llm_start = time.perf_counter()
    result = generate_sql(question, schema, rules, examples)
    llm_ms = (time.perf_counter() - llm_start) * 1000

    sql = result.get("sql", "")
    validation = validator.validate(sql)
    total_ms = (time.perf_counter() - start) * 1000

    exec_error = ""
    exec_rows = 0
    if validation.is_valid:
        import psycopg2
        try:
            conn = psycopg2.connect(conn_uri)
            cur = conn.cursor()
            cur.execute(sql)
            exec_rows = len(cur.fetchall())
            cur.close()
            conn.close()
        except Exception as e:  # noqa: BLE001
            exec_error = str(e)

    # Schema retrieval accuracy: fraction of expected tables present in the
    # retrieved schema context (the retriever emits "TABLE: <name>" lines).
    retrieved_tables = {m.group(1) for line in schema.splitlines() if (m := re.match(r"TABLE:\s*(\w+)", line))}
    expected_tables = set(case.get("expected_tables", []))
    schema_accuracy = len(retrieved_tables & expected_tables) / len(expected_tables) if expected_tables else None

    # Business-rule retrieval accuracy: fraction of expected rule terms present
    # in the retrieved rules context ("- <term>: ..." lines).
    retrieved_terms = {m.group(1) for line in rules.splitlines() if (m := re.match(r"-\s*([^:]+):", line))}
    expected_rules = set(case.get("expected_rules", []))
    rule_accuracy = len(retrieved_terms & expected_rules) / len(expected_rules) if expected_rules else None

    return {
        "question": question,
        "sql_ok": validation.is_valid,
        "validation_error": validation.error,
        "exec_ok": validation.is_valid and not exec_error,
        "exec_error": exec_error,
        "rows_returned": exec_rows,
        "retrieved_tables": sorted(retrieved_tables),
        "expected_tables": sorted(expected_tables),
        "schema_accuracy": schema_accuracy,
        "rule_accuracy": rule_accuracy,
        "retrieval_ms": retrieval_ms,
        "llm_ms": llm_ms,
        "total_ms": total_ms,
        "tokens": result.get("tokens_used", 0),
    }


def main() -> None:
    dataset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATASET
    cases = json.loads(dataset_path.read_text())
    validator = SQLValidator()
    # Eval executes SELECT-only queries, so the read-only role from settings is fine.
    conn_uri = getattr(settings, "database_url", "")

    results = [evaluate_case(validator, case, conn_uri) for case in cases]

    print(f"{'question':<45} {'sql':>4} {'exec':>5} {'s-tab':>6} {'rule':>5} {'ms':>8} {'tok':>5}")
    for r in results:
        schema_acc = f"{r['schema_accuracy']:.2f}" if r["schema_accuracy"] is not None else "-"
        rule_acc = f"{r['rule_accuracy']:.2f}" if r["rule_accuracy"] is not None else "-"
        print(
            f"{r['question'][:44]:<45} {str(r['sql_ok']):>4} {str(r['exec_ok']):>5} "
            f"{schema_acc:>6} {rule_acc:>5} "
            f"{r['total_ms']:>8.0f} {r['tokens']:>5}"
        )

    n_sql = sum(1 for r in results if r["sql_ok"])
    n_exec = sum(1 for r in results if r["exec_ok"])
    n = len(results)
    exec_var = ", ".join(f"#{i}: {r['validation_error'] or r['exec_error']}" for i, r in enumerate(results, 1) if not r["exec_ok"])
    print(f"\n{n} cases: SQL correct {n_sql}/{n}, executed cleanly {n_exec}/{n}" + (f"\nFailures: {exec_var}" if exec_var else ""))

    print(f"schema retrieval accuracy: {avg(results, 'schema_accuracy')}")
    print(f"rules retrieval accuracy:  {avg(results, 'rule_accuracy')}")
    print(f"avg retrieval ms: {avg(results, 'retrieval_ms'):.0f}, avg llm ms: {avg(results, 'llm_ms'):.0f}, avg tokens: {avg(results, 'tokens'):.0f}")

    sys.exit(0 if n_exec == n else 1)


def avg(results: list[dict], key: str) -> float:
    vals = [r[key] for r in results if r[key] is not None]
    return (sum(vals) / len(vals)) if vals else 0.0


if __name__ == "__main__":
    main()