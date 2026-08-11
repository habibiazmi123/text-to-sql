import sqlparse
from dataclasses import dataclass

BLOCKED_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}
BLOCKED_TABLES = {"pg_catalog", "information_schema", "pg_tables", "pg_stat", "pg_class", "pg_roles"}
ALLOWED_STATEMENTS = {"SELECT", "WITH"}


@dataclass
class ValidationResult:
    is_valid: bool
    error: str = ""
    sql: str = ""


class SQLValidator:
    def validate(self, sql: str) -> ValidationResult:
        sql = sql.strip()
        if not sql:
            return ValidationResult(is_valid=False, error="Empty SQL")

        parsed = sqlparse.parse(sql)
        if len(parsed) > 1 and any(str(stmt).strip() for stmt in parsed[1:]):
            return ValidationResult(is_valid=False, error="Multiple statements not allowed")

        stmt = parsed[0]
        stmt_type = stmt.get_type()

        if stmt_type and stmt_type.upper() not in ALLOWED_STATEMENTS:
            return ValidationResult(
                is_valid=False,
                error=f"Statement type '{stmt_type}' not allowed. Only SELECT/WITH permitted."
            )

        sql_upper = sql.upper()
        for keyword in BLOCKED_KEYWORDS:
            if keyword in sql_upper:
                return ValidationResult(is_valid=False, error=f"Keyword '{keyword}' not allowed")

        sql_lower = sql.lower()
        for table in BLOCKED_TABLES:
            if table in sql_lower or table in sql_upper:
                return ValidationResult(is_valid=False, error=f"Access to '{table}' not allowed")

        return ValidationResult(is_valid=True, sql=sql)
