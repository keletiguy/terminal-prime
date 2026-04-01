"""Import service for Mediciel Excel files."""
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any, Dict

from openpyxl import load_workbook

from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo


# Excel serial date epoch (1899-12-30 for the 1900 date system)
_EXCEL_EPOCH = date(1899, 12, 30)

# Mediciel column indices (0-based)
_COL_DATE = 2        # "Date facture"
_COL_CLIENT = 3      # "Client principal"
_COL_AFFILIATE = 4   # "Affilié"
_COL_NUMBER = 5      # "N° Facture"
_COL_AMOUNT = 6      # "Montant Total"


def _parse_date(value: Any) -> date:
    """Parse a date value from Excel cell.

    Handles:
    - Python date objects
    - Python datetime objects
    - Excel serial dates (int/float)
    - ISO format strings
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        # Excel serial date
        return _EXCEL_EPOCH + timedelta(days=int(value))
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError(f"Cannot parse date from {value!r}")


class ImportService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.client_repo = ClientRepo(conn)
        self.affiliate_repo = AffiliateRepo(conn)
        self.invoice_repo = InvoiceRepo(conn)

    def import_file(self, file_path: str) -> Dict[str, int]:
        """Import invoices from a Mediciel Excel file.

        Returns dict with keys: imported, duplicates, clients_created,
        affiliates_created, errors.
        """
        wb = load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active

        stats = {
            "imported": 0,
            "duplicates": 0,
            "clients_created": 0,
            "affiliates_created": 0,
            "errors": 0,
        }

        # Track which clients/affiliates existed before this import
        existing_clients: Dict[str, int] = {}
        existing_affiliates: Dict[str, int] = {}

        rows = list(ws.iter_rows(min_row=2, values_only=True))  # skip header
        wb.close()

        for row in rows:
            try:
                # Skip empty rows
                if row is None or len(row) < _COL_AMOUNT + 1:
                    continue

                invoice_number = row[_COL_NUMBER]
                if not invoice_number:
                    continue

                invoice_number = str(invoice_number).strip()
                if not invoice_number:
                    continue

                # Check duplicate by invoice number
                existing = self.conn.execute(
                    "SELECT id FROM invoices WHERE number = ?",
                    (invoice_number,),
                ).fetchone()
                if existing:
                    stats["duplicates"] += 1
                    continue

                # Parse date
                date_val = row[_COL_DATE]
                if date_val is None:
                    stats["errors"] += 1
                    continue
                inv_date = _parse_date(date_val)

                # Parse client
                client_name = row[_COL_CLIENT]
                if not client_name:
                    stats["errors"] += 1
                    continue
                client_name = str(client_name).strip()

                # Parse affiliate
                affiliate_name = row[_COL_AFFILIATE]
                if not affiliate_name:
                    stats["errors"] += 1
                    continue
                affiliate_name = str(affiliate_name).strip()

                # Parse amount
                amount_val = row[_COL_AMOUNT]
                if amount_val is None:
                    stats["errors"] += 1
                    continue
                amount = int(amount_val)

                # Get or create client
                if client_name in existing_clients:
                    client_id = existing_clients[client_name]
                else:
                    # Check if client already exists in DB
                    existing_row = self.conn.execute(
                        "SELECT id FROM clients WHERE name = ?",
                        (client_name,),
                    ).fetchone()
                    if existing_row:
                        client_id = existing_row["id"]
                    else:
                        client = self.client_repo.create(client_name)
                        client_id = client.id
                        stats["clients_created"] += 1
                    existing_clients[client_name] = client_id

                # Get or create affiliate
                aff_key = (affiliate_name, client_id)
                if aff_key in existing_affiliates:
                    affiliate_id = existing_affiliates[aff_key]
                else:
                    existing_row = self.conn.execute(
                        "SELECT id FROM affiliates WHERE name = ? AND client_id = ?",
                        (affiliate_name, client_id),
                    ).fetchone()
                    if existing_row:
                        affiliate_id = existing_row["id"]
                    else:
                        affiliate = self.affiliate_repo.create(affiliate_name, client_id)
                        affiliate_id = affiliate.id
                        stats["affiliates_created"] += 1
                    existing_affiliates[aff_key] = affiliate_id

                # Calculate due date
                due_date = inv_date + timedelta(days=30)

                # Create invoice
                self.invoice_repo.create(
                    number=invoice_number,
                    client_id=client_id,
                    affiliate_id=affiliate_id,
                    inv_date=inv_date,
                    due_date=due_date,
                    amount=amount,
                )
                stats["imported"] += 1

            except Exception:
                stats["errors"] += 1

        return stats
