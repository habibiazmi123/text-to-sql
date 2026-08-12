import psycopg2
from app.config import settings
from app.embeddings.model import embed_texts


def index_business_rules() -> dict:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute("SELECT id, term, definition FROM business_rules")
    rows = cur.fetchall()

    if not rows:
        cur.close()
        conn.close()
        return {"rules_indexed": 0}

    texts = [f"{term}: {definition}" for _, term, definition in rows]
    embeddings = embed_texts(texts)

    for (rule_id, _, _), embedding in zip(rows, embeddings):
        cur.execute(
            "UPDATE business_rules SET embedding = %s WHERE id = %s",
            (str(embedding), rule_id),
        )

    conn.commit()
    count = len(rows)
    cur.close()
    conn.close()

    return {"rules_indexed": count}
