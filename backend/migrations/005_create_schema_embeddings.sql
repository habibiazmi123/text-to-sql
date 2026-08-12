CREATE TABLE IF NOT EXISTS schema_embeddings (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100),
    entry_type VARCHAR(20) NOT NULL, -- 'table' or 'column'
    description TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schema_embeddings_table ON schema_embeddings(table_name);
CREATE INDEX IF NOT EXISTS idx_schema_embeddings_type ON schema_embeddings(entry_type);
