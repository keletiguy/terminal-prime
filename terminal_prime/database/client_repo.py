import sqlite3
from typing import List, Optional

from terminal_prime.models.client import Client


class ClientRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_client(self, row: sqlite3.Row) -> Client:
        return Client(
            id=row["id"],
            name=row["name"],
            contact_email=row["contact_email"],
        )

    def create(self, name: str, contact_email: Optional[str] = None) -> Client:
        cursor = self.conn.execute(
            "INSERT INTO clients (name, contact_email) VALUES (?, ?)",
            (name, contact_email),
        )
        self.conn.commit()
        return Client(id=cursor.lastrowid, name=name, contact_email=contact_email)

    def get_or_create(self, name: str) -> Client:
        row = self.conn.execute(
            "SELECT * FROM clients WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return self._row_to_client(row)
        return self.create(name)

    def get_by_id(self, client_id: int) -> Optional[Client]:
        row = self.conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        if row:
            return self._row_to_client(row)
        return None

    def get_all(self) -> List[Client]:
        rows = self.conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
        return [self._row_to_client(r) for r in rows]

    def search(self, query: str) -> List[Client]:
        rows = self.conn.execute(
            "SELECT * FROM clients WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",),
        ).fetchall()
        return [self._row_to_client(r) for r in rows]
