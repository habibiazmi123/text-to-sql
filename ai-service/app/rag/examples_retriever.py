import psycopg2
from app.config import settings
from app.embeddings.model import embed_text


def retrieve_similar_examples(question: str, top_k: int = 3) -> str:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    # Embedding search
    query_embedding = embed_text(question)
    cur.execute(
        """SELECT id, question, sql, description,
                  1 - (embedding <=> %s::vector) AS similarity
           FROM sql_examples
           WHERE embedding IS NOT NULL
           ORDER BY embedding <=> %s::vector
           LIMIT %s""",
        (str(query_embedding), str(query_embedding), top_k * 2),
    )
    embedding_results = {row[0]: row for row in cur.fetchall()}

    # Keyword search on question
    cur.execute(
        """SELECT id, question, sql, description, 1.0 AS similarity
           FROM sql_examples
           WHERE question ILIKE %s
           LIMIT %s""",
        (f"%{question}%", top_k),
    )
    keyword_results = {row[0]: row for row in cur.fetchall()}

    cur.close()
    conn.close()

    # Merge: keyword matches first (exact), then embedding (semantic)
    merged = {}
    for row in keyword_results.values():
        merged[row[0]] = row
    for row in embedding_results.values():
        if row[0] not in merged:
            merged[row[0]] = row

    results = sorted(merged.values(), key=lambda r: r[4], reverse=True)[:top_k]

    if not results:
        return ""

    lines = ["SQL EXAMPLES (similar questions and their queries):"]
    for _, q, sql, desc, _ in results:
        lines.append(f"\nQuestion: {q}")
        lines.append(f"SQL: {sql}")
        if desc:
            lines.append(f"Description: {desc}")

    return "\n".join(lines)
