import psycopg2
from app.config import settings


def get_schema_context() -> str:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()

    tables: dict[str, list] = {}
    for table, col, dtype, nullable in rows:
        if table not in tables:
            tables[table] = []
        tables[table].append(f"  {col} {dtype}{' NULL' if nullable == 'YES' else ' NOT NULL'}")

    cur.execute("""
        SELECT tc.table_name, kcu.column_name,
               ccu.table_name AS ref_table, ccu.column_name AS ref_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    """)
    fks = cur.fetchall()

    cur.close()
    conn.close()

    lines = ["DATABASE SCHEMA:"]
    for table, cols in tables.items():
        lines.append(f"\nTABLE: {table}")
        lines.extend(cols)

    if fks:
        lines.append("\nRELATIONSHIPS:")
        for table, col, ref_table, ref_col in fks:
            lines.append(f"  {table}.{col} -> {ref_table}.{ref_col}")

    return "\n".join(lines)
