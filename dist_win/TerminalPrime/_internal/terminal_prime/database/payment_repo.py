import sqlite3
from datetime import date
from typing import List, Optional

from terminal_prime.models.payment import Payment, PaymentMode


class PaymentRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_payment(self, row: sqlite3.Row) -> Payment:
        return Payment(
            id=row["id"],
            invoice_id=row["invoice_id"],
            client_id=row["client_id"],
            date=date.fromisoformat(row["date"]),
            amount=row["amount"],
            mode=PaymentMode(row["mode"]),
            reference=row["reference"],
        )

    def _next_reference(self) -> str:
        row = self.conn.execute("SELECT COUNT(*) AS cnt FROM payments").fetchone()
        next_num = row["cnt"] + 1
        return f"PAY-{next_num:05d}"

    def create(
        self,
        invoice_id: int,
        client_id: int,
        pay_date: date,
        amount: int,
        mode: str,
        reference: Optional[str] = None,
    ) -> Payment:
        if reference is None:
            reference = self._next_reference()
        cursor = self.conn.execute(
            "INSERT INTO payments (invoice_id, client_id, date, amount, mode, reference) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (invoice_id, client_id, pay_date.isoformat(), amount, mode, reference),
        )
        self.conn.commit()
        return Payment(
            id=cursor.lastrowid,
            invoice_id=invoice_id,
            client_id=client_id,
            date=pay_date,
            amount=amount,
            mode=PaymentMode(mode),
            reference=reference,
        )

    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        rows = self.conn.execute(
            "SELECT * FROM payments WHERE invoice_id = ? ORDER BY date",
            (invoice_id,),
        ).fetchall()
        return [self._row_to_payment(r) for r in rows]

    def get_recent(self, limit: int = 10) -> List[Payment]:
        rows = self.conn.execute(
            "SELECT * FROM payments ORDER BY date DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_payment(r) for r in rows]

    def get_total_collected_mtd(self, today: Optional[date] = None) -> int:
        today = today or date.today()
        first_of_month = today.replace(day=1).isoformat()
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE date >= ?",
            (first_of_month,),
        ).fetchone()
        return row["total"]
