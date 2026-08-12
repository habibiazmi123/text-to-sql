import psycopg2
from app.config import settings
from app.embeddings.model import embed_texts
from app.schema.introspector import get_schema_entries


def index_schema():
    entries = get_schema_entries()
    if not entries:
        return {"indexed": 0, "message": "No schema entries found"}

    texts = [e["description"] for e in entries]
    embeddings = embed_texts(texts)

    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute("DELETE FROM schema_embeddings")

    for entry, embedding in zip(entries, embeddings):
        cur.execute(
            """INSERT INTO schema_embeddings (table_name, column_name, entry_type, description, embedding)
               VALUES (%s, %s, %s, %s, %s)""",
            (entry["table_name"], entry.get("column_name"), entry["entry_type"], entry["description"], str(embedding)),
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"indexed": len(entries), "message": f"Indexed {len(entries)} schema entries"}
