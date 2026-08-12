import psycopg2
from app.config import settings
from app.embeddings.model import embed_text


def retrieve_relevant_schema(question: str, top_k: int = 10) -> str:
    query_embedding = embed_text(question)

    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute(
        """SELECT table_name, column_name, entry_type, description,
                  1 - (embedding <=> %s::vector) AS similarity
           FROM schema_embeddings
           ORDER BY embedding <=> %s::vector
           LIMIT %s""",
        (str(query_embedding), str(query_embedding), top_k * 3),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return ""

    tables: dict[str, list[str]] = {}
    for table_name, column_name, entry_type, description, similarity in rows:
        if table_name not in tables:
            tables[table_name] = []
        if entry_type == "column" and column_name:
            tables[table_name].append(f"  {column_name}")

    if not tables:
        return ""

    lines = ["RELEVANT DATABASE SCHEMA:"]
    for table_name, cols in tables.items():
        lines.append(f"\nTABLE: {table_name}")
        if cols:
            lines.extend(cols)

    return "\n".join(lines)
