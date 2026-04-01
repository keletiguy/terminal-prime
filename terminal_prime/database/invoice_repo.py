import sqlite3
from datetime import date
from typing import List, Optional

from terminal_prime.models.invoice import Invoice, InvoiceStatus


class InvoiceRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_invoice(self, row: sqlite3.Row) -> Invoice:
        return Invoice(
            id=row["id"],
            number=row["number"],
            client_id=row["client_id"],
            affiliate_id=row["affiliate_id"],
            date=date.fromisoformat(row["date"]),
            due_date=date.fromisoformat(row["due_date"]),
            amount=row["amount"],
            status=InvoiceStatus(row["status"]),
            total_paid=row["total_paid"] if "total_paid" in row.keys() else 0,
            client_name=row["client_name"] if "client_name" in row.keys() else None,
            affiliate_name=row["affiliate_name"] if "affiliate_name" in row.keys() else None,
        )

    def create(
        self,
        number: str,
        client_id: int,
        affiliate_id: int,
        inv_date: date,
        due_date: date,
        amount: int,
        status: str = "EN_ATTENTE",
    ) -> Invoice:
        cursor = self.conn.execute(
            "INSERT INTO invoices (number, client_id, affiliate_id, date, due_date, amount, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (number, client_id, affiliate_id, inv_date.isoformat(), due_date.isoformat(), amount, status),
        )
        self.conn.commit()
        return Invoice(
            id=cursor.lastrowid,
            number=number,
            client_id=client_id,
            affiliate_id=affiliate_id,
            date=inv_date,
            due_date=due_date,
            amount=amount,
            status=InvoiceStatus(status),
        )

    def create_if_not_exists(
        self,
        number: str,
        client_id: int,
        affiliate_id: int,
        inv_date: date,
        due_date: date,
        amount: int,
    ) -> Invoice:
        row = self.conn.execute(
            "SELECT * FROM invoices WHERE number = ?", (number,)
        ).fetchone()
        if row:
            return self._row_to_invoice(row)
        return self.create(number, client_id, affiliate_id, inv_date, due_date, amount)

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        row = self.conn.execute(
            """
            SELECT i.*,
                   c.name AS client_name,
                   a.name AS affiliate_name,
                   COALESCE(SUM(p.amount), 0) AS total_paid
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN affiliates a ON i.affiliate_id = a.id
            LEFT JOIN payments p ON p.invoice_id = i.id
            WHERE i.id = ?
            GROUP BY i.id
            """,
            (invoice_id,),
        ).fetchone()
        if row:
            return self._row_to_invoice(row)
        return None

    def get_all(
        self,
        client_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Invoice]:
        query = """
            SELECT i.*,
                   c.name AS client_name,
                   a.name AS affiliate_name,
                   COALESCE(SUM(p.amount), 0) AS total_paid
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN affiliates a ON i.affiliate_id = a.id
            LEFT JOIN payments p ON p.invoice_id = i.id
        """
        params: list = []
        conditions: list = []
        if client_id is not None:
            conditions.append("i.client_id = ?")
            params.append(client_id)
        if status is not None:
            conditions.append("i.status = ?")
            params.append(status)
        if date_from is not None:
            conditions.append("i.date >= ?")
            params.append(date_from.isoformat())
        if date_to is not None:
            conditions.append("i.date <= ?")
            params.append(date_to.isoformat())
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY i.id ORDER BY i.due_date ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_invoice(r) for r in rows]

    def count(
        self,
        client_id: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        query = "SELECT COUNT(*) AS cnt FROM invoices i"
        params: list = []
        conditions: list = []
        if client_id is not None:
            conditions.append("i.client_id = ?")
            params.append(client_id)
        if status is not None:
            conditions.append("i.status = ?")
            params.append(status)
        if date_from is not None:
            conditions.append("i.date >= ?")
            params.append(date_from.isoformat())
        if date_to is not None:
            conditions.append("i.date <= ?")
            params.append(date_to.isoformat())
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        row = self.conn.execute(query, params).fetchone()
        return row["cnt"]

    def get_unpaid(self) -> List[Invoice]:
        rows = self.conn.execute(
            """
            SELECT i.*,
                   c.name AS client_name,
                   a.name AS affiliate_name,
                   COALESCE(SUM(p.amount), 0) AS total_paid
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN affiliates a ON i.affiliate_id = a.id
            LEFT JOIN payments p ON p.invoice_id = i.id
            WHERE i.status != 'PAYEE'
            GROUP BY i.id
            ORDER BY i.due_date ASC
            """
        ).fetchall()
        return [self._row_to_invoice(r) for r in rows]

    def update_status_from_payments(self, invoice_id: int) -> None:
        row = self.conn.execute(
            """
            SELECT i.amount, COALESCE(SUM(p.amount), 0) AS total_paid
            FROM invoices i
            LEFT JOIN payments p ON p.invoice_id = i.id
            WHERE i.id = ?
            GROUP BY i.id
            """,
            (invoice_id,),
        ).fetchone()
        if row is None:
            return
        total_paid = row["total_paid"]
        amount = row["amount"]
        if total_paid >= amount:
            new_status = "PAYEE"
        elif total_paid > 0:
            new_status = "PARTIELLE"
        else:
            new_status = "EN_ATTENTE"
        self.conn.execute(
            "UPDATE invoices SET status = ? WHERE id = ?",
            (new_status, invoice_id),
        )
        self.conn.commit()
