DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'text_to_sql_user') THEN
        CREATE ROLE text_to_sql_user WITH LOGIN PASSWORD 'text_to_sql_password';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO text_to_sql_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO text_to_sql_user;
