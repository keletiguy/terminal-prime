"""Tests for the export service."""
import os
import sqlite3
import tempfile
from datetime import date, timedelta

import pytest

from terminal_prime.database.schema import create_tables
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.payment_repo import PaymentRepo
from terminal_prime.services.export_service import ExportService


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    create_tables(c)
    return c


@pytest.fixture
def seeded_conn(conn):
    client_repo = ClientRepo(conn)
    affiliate_repo = AffiliateRepo(conn)
    invoice_repo = InvoiceRepo(conn)
    payment_repo = PaymentRepo(conn)

    client = client_repo.create("Client Test")
    affiliate = affiliate_repo.create("Affilie Test", client.id)

    today = date.today()
    inv = invoice_repo.create(
        number="FAC-001", client_id=client.id, affiliate_id=affiliate.id,
        inv_date=today - timedelta(days=45), due_date=today - timedelta(days=15),
        amount=100000,
    )

    payment_repo.create(
        invoice_id=inv.id, client_id=client.id,
        pay_date=today - timedelta(days=5), amount=30000, mode="VIREMENT",
    )

    return conn


def test_export_excel(seeded_conn):
    svc = ExportService(seeded_conn)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        filepath = f.name

    try:
        svc.export_aging_excel(filepath)
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    finally:
        os.unlink(filepath)


def test_export_invoice_pdf(seeded_conn):
    svc = ExportService(seeded_conn)

    # Get the invoice id
    row = seeded_conn.execute("SELECT id FROM invoices LIMIT 1").fetchone()
    invoice_id = row["id"]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        filepath = f.name

    try:
        svc.export_invoice_pdf(invoice_id, filepath)
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    finally:
        os.unlink(filepath)
