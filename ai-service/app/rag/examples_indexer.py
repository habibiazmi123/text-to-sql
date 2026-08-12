import psycopg2
from app.config import settings
from app.embeddings.model import embed_text


def index_sql_examples() -> dict:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute("SELECT id, question FROM sql_examples WHERE embedding IS NULL")
    rows = cur.fetchall()

    if not rows:
        cur.close()
        conn.close()
        return {"indexed": 0, "total": 0}

    cur.execute("SELECT COUNT(*) FROM sql_examples")
    total = cur.fetchone()[0]

    for example_id, question in rows:
        embedding = embed_text(question)
        cur.execute(
            "UPDATE sql_examples SET embedding = %s WHERE id = %s",
            (str(embedding), example_id),
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"indexed": len(rows), "total": total}
