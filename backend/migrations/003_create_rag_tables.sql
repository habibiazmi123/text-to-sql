CREATE TABLE IF NOT EXISTS business_rules (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    example_sql TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sql_examples (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    sql TEXT NOT NULL,
    description TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);
