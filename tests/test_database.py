"""Tests for database connection and schema - written BEFORE implementation (TDD)."""
import os
import sqlite3
import tempfile
import pytest


@pytest.fixture
def db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


class TestConnection:
    def test_get_connection_returns_connection(self, db_path):
        from terminal_prime.database.connection import get_connection
        conn = get_connection(db_path)
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_row_factory_is_row(self, db_path):
        from terminal_prime.database.connection import get_connection
        conn = get_connection(db_path)
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_foreign_keys_enabled(self, db_path):
        from terminal_prime.database.connection import get_connection
        conn = get_connection(db_path)
        result = conn.execute("PRAGMA foreign_keys").fetchone()
        assert result[0] == 1
        conn.close()


class TestSchema:
    def test_create_tables(self, db_path):
        from terminal_prime.database.connection import get_connection
        from terminal_prime.database.schema import create_tables
        conn = get_connection(db_path)
        create_tables(conn)
        # Check all tables exist
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "clients" in table_names
        assert "affiliates" in table_names
        assert "invoices" in table_names
        assert "payments" in table_names
        conn.close()

    def test_clients_unique_name(self, db_path):
        from terminal_prime.database.connection import get_connection
        from terminal_prime.database.schema import create_tables
        conn = get_connection(db_path)
        create_tables(conn)
        conn.execute("INSERT INTO clients (name) VALUES ('Pharma Corp')")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO clients (name) VALUES ('Pharma Corp')")
            conn.commit()
        conn.close()

    def test_invoices_unique_number(self, db_path):
        from terminal_prime.database.connection import get_connection
        from terminal_prime.database.schema import create_tables
        conn = get_connection(db_path)
        create_tables(conn)
        conn.execute("INSERT INTO clients (name) VALUES ('C1')")
        conn.execute("INSERT INTO affiliates (name, client_id) VALUES ('A1', 1)")
        conn.execute(
            "INSERT INTO invoices (number, client_id, affiliate_id, date, due_date, amount) "
            "VALUES ('FAC-001', 1, 1, '2026-01-01', '2026-03-01', 5000000)"
        )
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO invoices (number, client_id, affiliate_id, date, due_date, amount) "
                "VALUES ('FAC-001', 1, 1, '2026-02-01', '2026-04-01', 3000000)"
            )
            conn.commit()
        conn.close()

    def test_affiliates_unique_name_per_client(self, db_path):
        from terminal_prime.database.connection import get_connection
        from terminal_prime.database.schema import create_tables
        conn = get_connection(db_path)
        create_tables(conn)
        conn.execute("INSERT INTO clients (name) VALUES ('C1')")
        conn.execute("INSERT INTO affiliates (name, client_id) VALUES ('Branch1', 1)")
        conn.commit()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO affiliates (name, client_id) VALUES ('Branch1', 1)")
            conn.commit()
        conn.close()

    def test_foreign_key_enforcement(self, db_path):
        from terminal_prime.database.connection import get_connection
        from terminal_prime.database.schema import create_tables
        conn = get_connection(db_path)
        create_tables(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO affiliates (name, client_id) VALUES ('Branch1', 999)"
            )
            conn.commit()
        conn.close()
