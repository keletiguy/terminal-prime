"""Tests for ImportService - written BEFORE implementation (TDD)."""
import os
import sqlite3
import tempfile
from datetime import date, timedelta

import pytest
from openpyxl import Workbook

from terminal_prime.database.schema import create_tables


@pytest.fixture
def db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    yield conn
    conn.close()
    os.unlink(db_path)


def _create_test_xlsx(rows, path=None):
    """Create a test xlsx file with Mediciel format.

    rows: list of tuples (date_facture, client_principal, affilié, n_facture, montant_total)
    Other columns (M, S, Règlement, Solde, !, Statut Envoi, Date Envoi, Code Recap) are filled with blanks.
    """
    wb = Workbook()
    ws = wb.active
    # Headers (row 0 in spec = row 1 in openpyxl)
    headers = [
        "M", "S", "Date facture", "Client principal", "Affilié",
        "N° Facture", "Montant Total", "Règlement", "Solde", "!",
        "Statut Envoi", "Date Envoi", "Code Recap. Client",
    ]
    ws.append(headers)

    for row in rows:
        date_val, client, affiliate, number, amount = row
        ws.append([
            None,       # M
            None,       # S
            date_val,   # Date facture
            client,     # Client principal
            affiliate,  # Affilié
            number,     # N° Facture
            amount,     # Montant Total
            None,       # Règlement
            None,       # Solde
            None,       # !
            None,       # Statut Envoi
            None,       # Date Envoi
            None,       # Code Recap. Client
        ])

    if path is None:
        fd, path = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
    wb.save(path)
    return path


class TestImportBasic:
    def test_import_basic(self, db):
        """Import 2 invoices, verify count."""
        from terminal_prime.services.import_service import ImportService

        xlsx_path = _create_test_xlsx([
            (date(2026, 1, 15), "Pharma Corp", "Dakar Branch", "FAC-001", 5_000_000),
            (date(2026, 1, 20), "Pharma Corp", "Dakar Branch", "FAC-002", 3_000_000),
        ])
        try:
            service = ImportService(db)
            stats = service.import_file(xlsx_path)
            assert stats["imported"] == 2
            assert stats["errors"] == 0
        finally:
            os.unlink(xlsx_path)


class TestImportDuplicates:
    def test_import_duplicates(self, db):
        """Import same file twice, second import has 0 imported."""
        from terminal_prime.services.import_service import ImportService

        xlsx_path = _create_test_xlsx([
            (date(2026, 1, 15), "Pharma Corp", "Dakar Branch", "FAC-001", 5_000_000),
            (date(2026, 1, 20), "Pharma Corp", "Dakar Branch", "FAC-002", 3_000_000),
        ])
        try:
            service = ImportService(db)
            stats1 = service.import_file(xlsx_path)
            assert stats1["imported"] == 2

            stats2 = service.import_file(xlsx_path)
            assert stats2["imported"] == 0
            assert stats2["duplicates"] == 2
        finally:
            os.unlink(xlsx_path)


class TestImportDueDate:
    def test_import_due_date_30_days(self, db):
        """Verify due_date = date + 30 days."""
        from terminal_prime.services.import_service import ImportService
        from terminal_prime.database.invoice_repo import InvoiceRepo

        inv_date = date(2026, 2, 10)
        xlsx_path = _create_test_xlsx([
            (inv_date, "Pharma Corp", "Branch A", "FAC-100", 1_000_000),
        ])
        try:
            service = ImportService(db)
            service.import_file(xlsx_path)

            repo = InvoiceRepo(db)
            invoices = repo.get_all()
            assert len(invoices) == 1
            assert invoices[0].due_date == inv_date + timedelta(days=30)
        finally:
            os.unlink(xlsx_path)


class TestImportCreatesClientsAndAffiliates:
    def test_import_creates_clients_and_affiliates(self, db):
        """3 invoices across 2 clients, verify client/affiliate creation counts."""
        from terminal_prime.services.import_service import ImportService

        xlsx_path = _create_test_xlsx([
            (date(2026, 1, 15), "Client A", "Branch A1", "FAC-201", 1_000_000),
            (date(2026, 1, 16), "Client A", "Branch A2", "FAC-202", 2_000_000),
            (date(2026, 1, 17), "Client B", "Branch B1", "FAC-203", 3_000_000),
        ])
        try:
            service = ImportService(db)
            stats = service.import_file(xlsx_path)
            assert stats["imported"] == 3
            assert stats["clients_created"] == 2
            assert stats["affiliates_created"] == 3
        finally:
            os.unlink(xlsx_path)
