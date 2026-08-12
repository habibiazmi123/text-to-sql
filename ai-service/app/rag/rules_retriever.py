import psycopg2
from app.config import settings
from app.embeddings.model import embed_text


def retrieve_relevant_rules(question: str, top_k: int = 5) -> str:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    # Embedding search
    query_embedding = embed_text(question)
    cur.execute(
        """SELECT id, term, definition,
                  1 - (embedding <=> %s::vector) AS similarity
           FROM business_rules
           WHERE embedding IS NOT NULL
           ORDER BY embedding <=> %s::vector
           LIMIT %s""",
        (str(query_embedding), str(query_embedding), top_k * 2),
    )
    embedding_results = {row[0]: row for row in cur.fetchall()}

    # Keyword search on term
    cur.execute(
        """SELECT id, term, definition, 1.0 AS similarity
           FROM business_rules
           WHERE term ILIKE %s
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

    results = sorted(merged.values(), key=lambda r: r[3], reverse=True)[:top_k]

    if not results:
        return ""

    lines = ["BUSINESS RULES:"]
    for _, term, definition, _ in results:
        lines.append(f"- {term}: {definition}")

    return "\n".join(lines)
