"""Tests for AgingService and DashboardService - written BEFORE implementation (TDD)."""
import os
import sqlite3
import tempfile
from datetime import date, timedelta

import pytest

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


def _seed_client_affiliate(conn, client_name="Test Client", affiliate_name="Branch"):
    """Helper to create a client and affiliate, returning (client_id, affiliate_id)."""
    from terminal_prime.database.client_repo import ClientRepo
    from terminal_prime.database.affiliate_repo import AffiliateRepo

    client = ClientRepo(conn).create(client_name)
    affiliate = AffiliateRepo(conn).create(affiliate_name, client.id)
    return client.id, affiliate.id


def _create_invoice(conn, client_id, affiliate_id, number, inv_date, due_date, amount, status="EN_ATTENTE"):
    from terminal_prime.database.invoice_repo import InvoiceRepo
    return InvoiceRepo(conn).create(
        number=number,
        client_id=client_id,
        affiliate_id=affiliate_id,
        inv_date=inv_date,
        due_date=due_date,
        amount=amount,
        status=status,
    )


def _create_payment(conn, invoice_id, client_id, pay_date, amount):
    from terminal_prime.database.payment_repo import PaymentRepo
    return PaymentRepo(conn).create(
        invoice_id=invoice_id,
        client_id=client_id,
        pay_date=pay_date,
        amount=amount,
        mode="VIREMENT",
    )


# ─── AgingService ────────────────────────────────────────────────────────────


class TestAgingBuckets:
    def test_aging_buckets(self, db):
        """Create invoices at different ages, verify bucket amounts."""
        from terminal_prime.services.aging_service import AgingService

        today = date(2026, 3, 15)
        client_id, affiliate_id = _seed_client_affiliate(db)

        # "current" - not yet due (due_date in the future)
        _create_invoice(db, client_id, affiliate_id, "INV-CURR",
                        date(2026, 3, 1), date(2026, 3, 20), 1_000_000)

        # "0-30" - 1-30 days overdue (due_date = today - 15 days)
        _create_invoice(db, client_id, affiliate_id, "INV-030",
                        date(2026, 2, 1), date(2026, 3, 1), 2_000_000)

        # "31-60" - 31-60 days overdue (due_date = today - 45 days)
        _create_invoice(db, client_id, affiliate_id, "INV-3160",
                        date(2026, 1, 1), date(2026, 1, 30), 3_000_000)

        # "61-90" - 61-90 days overdue (due_date = today - 75 days)
        _create_invoice(db, client_id, affiliate_id, "INV-6190",
                        date(2025, 12, 1), date(2025, 12, 31), 4_000_000)

        # "90+" - >90 days overdue (due_date = today - 120 days)
        _create_invoice(db, client_id, affiliate_id, "INV-90P",
                        date(2025, 10, 1), date(2025, 11, 16), 5_000_000)

        service = AgingService(db)
        buckets = service.get_aging_buckets(today=today)

        assert buckets["current"] == 1_000_000
        assert buckets["0-30"] == 2_000_000
        assert buckets["31-60"] == 3_000_000
        assert buckets["61-90"] == 4_000_000
        assert buckets["90+"] == 5_000_000

    def test_aging_buckets_with_partial_payments(self, db):
        """Aging should use remaining (amount - paid), not full amount."""
        from terminal_prime.services.aging_service import AgingService

        today = date(2026, 3, 15)
        client_id, affiliate_id = _seed_client_affiliate(db)

        inv = _create_invoice(db, client_id, affiliate_id, "INV-PART",
                              date(2026, 2, 1), date(2026, 3, 1), 5_000_000)
        _create_payment(db, inv.id, client_id, date(2026, 3, 5), 2_000_000)

        service = AgingService(db)
        buckets = service.get_aging_buckets(today=today)

        # 5M - 2M paid = 3M remaining, 14 days overdue -> "0-30" bucket
        assert buckets["0-30"] == 3_000_000


class TestClientAging:
    def test_client_aging(self, db):
        """Aging filtered by client_id."""
        from terminal_prime.services.aging_service import AgingService

        today = date(2026, 3, 15)
        cid1, aid1 = _seed_client_affiliate(db, "Client A", "Branch A")
        cid2, aid2 = _seed_client_affiliate(db, "Client B", "Branch B")

        # Client A: 1M current
        _create_invoice(db, cid1, aid1, "INV-A1",
                        date(2026, 3, 1), date(2026, 3, 20), 1_000_000)

        # Client B: 2M overdue 0-30
        _create_invoice(db, cid2, aid2, "INV-B1",
                        date(2026, 2, 1), date(2026, 3, 1), 2_000_000)

        service = AgingService(db)

        aging_a = service.get_client_aging(cid1, today=today)
        assert aging_a["current"] == 1_000_000
        assert aging_a["0-30"] == 0

        aging_b = service.get_client_aging(cid2, today=today)
        assert aging_b["current"] == 0
        assert aging_b["0-30"] == 2_000_000


# ─── DashboardService ────────────────────────────────────────────────────────


class TestDashboardKPIs:
    def test_dashboard_kpis(self, db):
        """Verify total_issued, total_collected, outstanding."""
        from terminal_prime.services.dashboard_service import DashboardService

        client_id, affiliate_id = _seed_client_affiliate(db)

        inv1 = _create_invoice(db, client_id, affiliate_id, "INV-K1",
                               date(2026, 1, 1), date(2026, 2, 1), 5_000_000)
        inv2 = _create_invoice(db, client_id, affiliate_id, "INV-K2",
                               date(2026, 1, 15), date(2026, 2, 15), 3_000_000)

        _create_payment(db, inv1.id, client_id, date(2026, 2, 1), 2_000_000)

        service = DashboardService(db)
        kpis = service.get_kpis()

        assert kpis["total_issued"] == 8_000_000
        assert kpis["total_collected"] == 2_000_000
        assert kpis["outstanding"] == 6_000_000


class TestTopDebtors:
    def test_top_debtors(self, db):
        """Verify ordering and amounts of top debtors."""
        from terminal_prime.services.dashboard_service import DashboardService

        cid1, aid1 = _seed_client_affiliate(db, "Small Debtor", "Branch S")
        cid2, aid2 = _seed_client_affiliate(db, "Big Debtor", "Branch B")

        _create_invoice(db, cid1, aid1, "INV-D1",
                        date(2026, 1, 1), date(2026, 2, 1), 1_000_000)
        _create_invoice(db, cid2, aid2, "INV-D2",
                        date(2026, 1, 1), date(2026, 2, 1), 5_000_000)
        _create_invoice(db, cid2, aid2, "INV-D3",
                        date(2026, 1, 15), date(2026, 2, 15), 3_000_000)

        service = DashboardService(db)
        top = service.get_top_debtors(limit=5)

        assert len(top) == 2
        assert top[0]["name"] == "Big Debtor"
        assert top[0]["total_due"] == 8_000_000
        assert top[1]["name"] == "Small Debtor"
        assert top[1]["total_due"] == 1_000_000


class TestDSO:
    def test_dso_calculation(self, db):
        """Verify DSO is >= 0."""
        from terminal_prime.services.dashboard_service import DashboardService

        client_id, affiliate_id = _seed_client_affiliate(db)

        _create_invoice(db, client_id, affiliate_id, "INV-DSO1",
                        date(2026, 1, 1), date(2026, 2, 1), 5_000_000)
        _create_payment(db, 1, client_id, date(2026, 2, 1), 2_000_000)

        service = DashboardService(db)
        dso = service.get_dso()
        assert dso >= 0


class TestCollectionRate:
    def test_collection_rate(self, db):
        """Verify collection rate as percentage."""
        from terminal_prime.services.dashboard_service import DashboardService

        client_id, affiliate_id = _seed_client_affiliate(db)

        inv = _create_invoice(db, client_id, affiliate_id, "INV-CR1",
                              date(2026, 1, 1), date(2026, 2, 1), 10_000_000)
        _create_payment(db, inv.id, client_id, date(2026, 2, 1), 4_000_000)

        service = DashboardService(db)
        rate = service.get_collection_rate()

        # 4M / 10M * 100 = 40%
        assert rate == pytest.approx(40.0)
