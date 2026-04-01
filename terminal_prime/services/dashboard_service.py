"""Dashboard service for KPIs and analytics."""
import sqlite3
from datetime import date, timedelta
from typing import Dict, List, Optional


class DashboardService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_kpis(self) -> Dict[str, int]:
        """Get key performance indicators.

        Returns dict with:
        - total_issued: sum of all invoice amounts
        - total_collected: sum of all payments
        - outstanding: total_issued - total_collected
        """
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM invoices"
        ).fetchone()
        total_issued = row["total"]

        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments"
        ).fetchone()
        total_collected = row["total"]

        return {
            "total_issued": total_issued,
            "total_collected": total_collected,
            "outstanding": total_issued - total_collected,
        }

    def get_top_debtors(self, limit: int = 5) -> List[Dict]:
        """Get top debtors sorted by total_due descending.

        Returns list of dicts with id, name, total_due.
        total_due = sum of invoice amounts - sum of payments for that client.
        """
        rows = self.conn.execute(
            """
            SELECT c.id, c.name,
                   COALESCE(SUM(i.amount), 0) -
                   COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.client_id = c.id), 0)
                   AS total_due
            FROM clients c
            JOIN invoices i ON i.client_id = c.id
            WHERE i.status != 'PAYEE'
            GROUP BY c.id
            HAVING total_due > 0
            ORDER BY total_due DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            {"id": row["id"], "name": row["name"], "total_due": row["total_due"]}
            for row in rows
        ]

    def get_dso(self, today: Optional[date] = None) -> float:
        """Calculate Days Sales Outstanding.

        DSO = (outstanding / credit_sales_90_days) * 90
        """
        today = today or date.today()
        ninety_days_ago = (today - timedelta(days=90)).isoformat()

        # Outstanding = unpaid balance across non-PAYEE invoices
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(
                i.amount - COALESCE(
                    (SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0
                )
            ), 0) AS outstanding
            FROM invoices i
            WHERE i.status != 'PAYEE'
            """
        ).fetchone()
        outstanding = row["outstanding"]

        # Credit sales in last 90 days
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM invoices WHERE date >= ?",
            (ninety_days_ago,),
        ).fetchone()
        credit_sales_90 = row["total"]

        if credit_sales_90 == 0:
            return 0.0

        return (outstanding / credit_sales_90) * 90

    def get_collection_rate(self) -> float:
        """Calculate collection rate as percentage.

        collection_rate = (total_collected / total_issued) * 100
        """
        kpis = self.get_kpis()
        if kpis["total_issued"] == 0:
            return 0.0
        return (kpis["total_collected"] / kpis["total_issued"]) * 100

    def get_cei(self, today: Optional[date] = None) -> float:
        """Calculate Collection Effectiveness Index.

        CEI = ((receivables_start + invoiced_this_month - receivables_end) /
               (receivables_start + invoiced_this_month)) * 100
        """
        today = today or date.today()
        first_of_month = today.replace(day=1).isoformat()

        # Receivables at start of month (outstanding as of first_of_month)
        # = sum of amounts for invoices created before this month minus payments before this month
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(i.amount), 0) -
                   COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.date < ?), 0)
                   AS receivables
            FROM invoices i
            WHERE i.date < ?
            """,
            (first_of_month, first_of_month),
        ).fetchone()
        receivables_start = max(row["receivables"], 0)

        # Invoiced this month
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM invoices WHERE date >= ?",
            (first_of_month,),
        ).fetchone()
        invoiced_this_month = row["total"]

        # Receivables at end (current outstanding)
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(
                i.amount - COALESCE(
                    (SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0
                )
            ), 0) AS outstanding
            FROM invoices i
            WHERE i.status != 'PAYEE'
            """
        ).fetchone()
        receivables_end = row["outstanding"]

        denominator = receivables_start + invoiced_this_month
        if denominator == 0:
            return 0.0

        return ((receivables_start + invoiced_this_month - receivables_end) / denominator) * 100
