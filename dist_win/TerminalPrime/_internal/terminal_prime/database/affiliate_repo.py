import sqlite3
from typing import List, Optional

from terminal_prime.models.affiliate import Affiliate


class AffiliateRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_affiliate(self, row: sqlite3.Row) -> Affiliate:
        return Affiliate(
            id=row["id"],
            name=row["name"],
            client_id=row["client_id"],
        )

    def create(self, name: str, client_id: int) -> Affiliate:
        cursor = self.conn.execute(
            "INSERT INTO affiliates (name, client_id) VALUES (?, ?)",
            (name, client_id),
        )
        self.conn.commit()
        return Affiliate(id=cursor.lastrowid, name=name, client_id=client_id)

    def get_or_create(self, name: str, client_id: int) -> Affiliate:
        row = self.conn.execute(
            "SELECT * FROM affiliates WHERE name = ? AND client_id = ?",
            (name, client_id),
        ).fetchone()
        if row:
            return self._row_to_affiliate(row)
        return self.create(name, client_id)

    def get_by_id(self, affiliate_id: int) -> Optional[Affiliate]:
        row = self.conn.execute(
            "SELECT * FROM affiliates WHERE id = ?", (affiliate_id,)
        ).fetchone()
        if row:
            return self._row_to_affiliate(row)
        return None

    def get_by_client(self, client_id: int) -> List[Affiliate]:
        rows = self.conn.execute(
            "SELECT * FROM affiliates WHERE client_id = ? ORDER BY name",
            (client_id,),
        ).fetchall()
        return [self._row_to_affiliate(r) for r in rows]
