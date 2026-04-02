"""Aging service for aged trade balance analysis."""
import sqlite3
from datetime import date
from typing import Dict, Optional


class AgingService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _build_buckets(self, client_id: Optional[int] = None, today: Optional[date] = None) -> Dict[str, int]:
        """Build aging buckets from unpaid invoices.

        Classifies remaining amounts (amount - paid) by days overdue:
        - "current": not yet due (days_overdue <= 0)
        - "0-30": 1-30 days overdue
        - "31-60": 31-60 days overdue
        - "61-90": 61-90 days overdue
        - "90+": >90 days overdue
        """
        today = today or date.today()

        query = """
            SELECT i.due_date,
                   i.amount - COALESCE(SUM(p.amount), 0) AS remaining
            FROM invoices i
            LEFT JOIN payments p ON p.invoice_id = i.id
            WHERE i.status != 'PAYEE'
        """
        params: list = []

        if client_id is not None:
            query += " AND i.client_id = ?"
            params.append(client_id)

        query += " GROUP BY i.id"

        rows = self.conn.execute(query, params).fetchall()

        buckets: Dict[str, int] = {
            "current": 0,
            "0-30": 0,
            "31-60": 0,
            "61-90": 0,
            "90+": 0,
        }

        for row in rows:
            remaining = row["remaining"]
            if remaining <= 0:
                continue
            due_date = date.fromisoformat(row["due_date"])
            days_overdue = (today - due_date).days

            if days_overdue <= 0:
                buckets["current"] += remaining
            elif days_overdue <= 30:
                buckets["0-30"] += remaining
            elif days_overdue <= 60:
                buckets["31-60"] += remaining
            elif days_overdue <= 90:
                buckets["61-90"] += remaining
            else:
                buckets["90+"] += remaining

        return buckets

    def get_aging_buckets(self, today: Optional[date] = None) -> Dict[str, int]:
        """Get aging buckets for all clients."""
        return self._build_buckets(today=today)

    def get_client_aging(self, client_id: int, today: Optional[date] = None) -> Dict[str, int]:
        """Get aging buckets filtered by client_id."""
        return self._build_buckets(client_id=client_id, today=today)
