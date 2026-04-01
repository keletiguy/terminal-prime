"""Tests for repositories - written BEFORE implementation (TDD)."""
import os
import tempfile
from datetime import date
import pytest


@pytest.fixture
def conn():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    from terminal_prime.database.connection import get_connection
    from terminal_prime.database.schema import create_tables
    connection = get_connection(path)
    create_tables(connection)
    yield connection
    connection.close()
    os.unlink(path)


# ─── ClientRepo ──────────────────────────────────────────────────────────────

class TestClientRepo:
    def test_create(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        client = repo.create("Pharma Corp")
        assert client.id is not None
        assert client.name == "Pharma Corp"

    def test_get_or_create_new(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        client = repo.get_or_create("New Client")
        assert client.id is not None
        assert client.name == "New Client"

    def test_get_or_create_existing(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        c1 = repo.get_or_create("Pharma Corp")
        c2 = repo.get_or_create("Pharma Corp")
        assert c1.id == c2.id

    def test_get_by_id(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        created = repo.create("Pharma Corp")
        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.name == "Pharma Corp"

    def test_get_by_id_not_found(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        assert repo.get_by_id(999) is None

    def test_get_all(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        repo.create("A Corp")
        repo.create("B Corp")
        clients = repo.get_all()
        assert len(clients) == 2

    def test_search(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        repo = ClientRepo(conn)
        repo.create("Pharma Corp")
        repo.create("Bio Labs")
        results = repo.search("pharma")
        assert len(results) == 1
        assert results[0].name == "Pharma Corp"


# ─── AffiliateRepo ───────────────────────────────────────────────────────────

class TestAffiliateRepo:
    def _create_client(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        return ClientRepo(conn).create("Test Client")

    def test_create(self, conn):
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = self._create_client(conn)
        repo = AffiliateRepo(conn)
        affiliate = repo.create("Dakar Branch", client.id)
        assert affiliate.id is not None
        assert affiliate.name == "Dakar Branch"
        assert affiliate.client_id == client.id

    def test_get_or_create_new(self, conn):
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = self._create_client(conn)
        repo = AffiliateRepo(conn)
        a = repo.get_or_create("Branch X", client.id)
        assert a.id is not None

    def test_get_or_create_existing(self, conn):
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = self._create_client(conn)
        repo = AffiliateRepo(conn)
        a1 = repo.get_or_create("Branch X", client.id)
        a2 = repo.get_or_create("Branch X", client.id)
        assert a1.id == a2.id

    def test_get_by_id(self, conn):
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = self._create_client(conn)
        repo = AffiliateRepo(conn)
        created = repo.create("Branch Y", client.id)
        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.name == "Branch Y"

    def test_get_by_client(self, conn):
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = self._create_client(conn)
        repo = AffiliateRepo(conn)
        repo.create("Branch A", client.id)
        repo.create("Branch B", client.id)
        affiliates = repo.get_by_client(client.id)
        assert len(affiliates) == 2


# ─── InvoiceRepo ─────────────────────────────────────────────────────────────

class TestInvoiceRepo:
    def _seed(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        client = ClientRepo(conn).create("Test Client")
        affiliate = AffiliateRepo(conn).create("Branch", client.id)
        return client, affiliate

    def test_create(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        inv = repo.create(
            number="FAC-001",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        assert inv.id is not None
        assert inv.number == "FAC-001"

    def test_create_if_not_exists_new(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        inv = repo.create_if_not_exists(
            number="FAC-002",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=3_000_000,
        )
        assert inv.id is not None

    def test_create_if_not_exists_existing(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        inv1 = repo.create(
            number="FAC-003",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        inv2 = repo.create_if_not_exists(
            number="FAC-003",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        assert inv1.id == inv2.id

    def test_get_by_id_with_joins(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        created = repo.create(
            number="FAC-010",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.client_name == "Test Client"
        assert found.affiliate_name == "Branch"
        assert found.total_paid == 0

    def test_get_all_pagination(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        for i in range(5):
            repo.create(
                number=f"FAC-{i:03d}",
                client_id=client.id,
                affiliate_id=affiliate.id,
                inv_date=date(2026, 1, 15),
                due_date=date(2026, 3, 15),
                amount=1_000_000,
            )
        page = repo.get_all(limit=2, offset=0)
        assert len(page) == 2

    def test_get_unpaid(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        from terminal_prime.models.invoice import InvoiceStatus
        client, affiliate = self._seed(conn)
        repo = InvoiceRepo(conn)
        repo.create(
            number="FAC-U1",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        # Mark one as paid via direct SQL
        repo.create(
            number="FAC-U2",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=3_000_000,
        )
        conn.execute("UPDATE invoices SET status='PAYEE' WHERE number='FAC-U2'")
        conn.commit()
        unpaid = repo.get_unpaid()
        assert len(unpaid) == 1
        assert unpaid[0].number == "FAC-U1"

    def test_update_status_from_payments(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate = self._seed(conn)
        inv_repo = InvoiceRepo(conn)
        pay_repo = PaymentRepo(conn)
        inv = inv_repo.create(
            number="FAC-S1",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        pay_repo.create(
            invoice_id=inv.id,
            client_id=client.id,
            pay_date=date(2026, 2, 1),
            amount=5_000_000,
            mode="VIREMENT",
        )
        inv_repo.update_status_from_payments(inv.id)
        updated = inv_repo.get_by_id(inv.id)
        assert updated.status.value == "PAYEE"

    def test_update_status_partial(self, conn):
        from terminal_prime.database.invoice_repo import InvoiceRepo
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate = self._seed(conn)
        inv_repo = InvoiceRepo(conn)
        pay_repo = PaymentRepo(conn)
        inv = inv_repo.create(
            number="FAC-S2",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        pay_repo.create(
            invoice_id=inv.id,
            client_id=client.id,
            pay_date=date(2026, 2, 1),
            amount=2_000_000,
            mode="CHEQUE",
        )
        inv_repo.update_status_from_payments(inv.id)
        updated = inv_repo.get_by_id(inv.id)
        assert updated.status.value == "PARTIELLE"


# ─── PaymentRepo ─────────────────────────────────────────────────────────────

class TestPaymentRepo:
    def _seed(self, conn):
        from terminal_prime.database.client_repo import ClientRepo
        from terminal_prime.database.affiliate_repo import AffiliateRepo
        from terminal_prime.database.invoice_repo import InvoiceRepo
        client = ClientRepo(conn).create("Pay Client")
        affiliate = AffiliateRepo(conn).create("Branch", client.id)
        invoice = InvoiceRepo(conn).create(
            number="FAC-P1",
            client_id=client.id,
            affiliate_id=affiliate.id,
            inv_date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
        )
        return client, affiliate, invoice

    def test_create_auto_reference(self, conn):
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate, invoice = self._seed(conn)
        repo = PaymentRepo(conn)
        payment = repo.create(
            invoice_id=invoice.id,
            client_id=client.id,
            pay_date=date(2026, 2, 1),
            amount=1_000_000,
            mode="VIREMENT",
        )
        assert payment.id is not None
        assert payment.reference.startswith("PAY-")
        assert len(payment.reference) == 9  # PAY-NNNNN

    def test_get_by_invoice(self, conn):
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate, invoice = self._seed(conn)
        repo = PaymentRepo(conn)
        repo.create(invoice.id, client.id, date(2026, 2, 1), 1_000_000, "VIREMENT")
        repo.create(invoice.id, client.id, date(2026, 2, 15), 500_000, "CHEQUE")
        payments = repo.get_by_invoice(invoice.id)
        assert len(payments) == 2

    def test_get_recent(self, conn):
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate, invoice = self._seed(conn)
        repo = PaymentRepo(conn)
        for i in range(15):
            repo.create(invoice.id, client.id, date(2026, 2, i + 1), 100_000, "ESPECES")
        recent = repo.get_recent(limit=10)
        assert len(recent) == 10

    def test_get_total_collected_mtd(self, conn):
        from terminal_prime.database.payment_repo import PaymentRepo
        client, affiliate, invoice = self._seed(conn)
        repo = PaymentRepo(conn)
        repo.create(invoice.id, client.id, date(2026, 3, 5), 1_000_000, "VIREMENT")
        repo.create(invoice.id, client.id, date(2026, 3, 10), 2_000_000, "CHEQUE")
        # Payment from previous month - should not count
        repo.create(invoice.id, client.id, date(2026, 2, 28), 500_000, "ESPECES")
        total = repo.get_total_collected_mtd(today=date(2026, 3, 15))
        assert total == 3_000_000
