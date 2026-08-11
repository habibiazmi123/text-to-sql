import pytest
from app.sql.validator import SQLValidator


def test_allows_select():
    v = SQLValidator()
    result = v.validate("SELECT * FROM customers")
    assert result.is_valid is True


def test_allows_with():
    v = SQLValidator()
    result = v.validate("WITH cte AS (SELECT * FROM orders) SELECT * FROM cte")
    assert result.is_valid is True


def test_rejects_insert():
    v = SQLValidator()
    result = v.validate("INSERT INTO customers (name) VALUES ('test')")
    assert result.is_valid is False
    assert "INSERT" in result.error


def test_rejects_update():
    v = SQLValidator()
    result = v.validate("UPDATE customers SET name = 'test'")
    assert result.is_valid is False


def test_rejects_delete():
    v = SQLValidator()
    result = v.validate("DELETE FROM customers WHERE id = 1")
    assert result.is_valid is False


def test_rejects_drop():
    v = SQLValidator()
    result = v.validate("DROP TABLE customers")
    assert result.is_valid is False


def test_rejects_multiple_statements():
    v = SQLValidator()
    result = v.validate("SELECT 1; DROP TABLE customers")
    assert result.is_valid is False


def test_rejects_system_tables():
    v = SQLValidator()
    result = v.validate("SELECT * FROM pg_catalog.pg_tables")
    assert result.is_valid is False
