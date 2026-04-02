import sqlite3
from typing import Optional

_connection: Optional[sqlite3.Connection] = None
_db_path: Optional[str] = None


def get_connection(db_path: str = "terminal_prime.db") -> sqlite3.Connection:
    """Get a database connection with foreign keys enabled and Row factory."""
    global _connection
    if db_path != "terminal_prime.db":
        # Non-default path: return a fresh connection (for tests)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    if _connection is None:
        _connection = sqlite3.connect(db_path)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
        _db_path = db_path
    return _connection


def get_db_path() -> Optional[str]:
    """Return the path of the current database file."""
    return _db_path


def close_connection() -> None:
    """Close the singleton connection if open."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
