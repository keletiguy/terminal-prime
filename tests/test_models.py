"""Tests for data models - written BEFORE implementation (TDD)."""
from datetime import date
import pytest


class TestClient:
    def test_create_client(self):
        from terminal_prime.models.client import Client
        client = Client(name="Pharma Corp")
        assert client.name == "Pharma Corp"
        assert client.id is None
        assert client.contact_email is None

    def test_create_client_with_all_fields(self):
        from terminal_prime.models.client import Client
        client = Client(name="Pharma Corp", id=1, contact_email="info@pharma.com")
        assert client.id == 1
        assert client.contact_email == "info@pharma.com"


class TestAffiliate:
    def test_create_affiliate(self):
        from terminal_prime.models.affiliate import Affiliate
        affiliate = Affiliate(name="Dakar Branch", client_id=1)
        assert affiliate.name == "Dakar Branch"
        assert affiliate.client_id == 1
        assert affiliate.id is None

    def test_create_affiliate_with_id(self):
        from terminal_prime.models.affiliate import Affiliate
        affiliate = Affiliate(name="Dakar Branch", client_id=1, id=5)
        assert affiliate.id == 5


class TestInvoice:
    def _make_invoice(self, **kwargs):
        from terminal_prime.models.invoice import Invoice, InvoiceStatus
        defaults = dict(
            number="FAC-001",
            client_id=1,
            affiliate_id=1,
            date=date(2026, 1, 15),
            due_date=date(2026, 3, 15),
            amount=5_000_000,
            status=InvoiceStatus.EN_ATTENTE,
        )
        defaults.update(kwargs)
        return Invoice(**defaults)

    def test_create_invoice(self):
        inv = self._make_invoice()
        assert inv.number == "FAC-001"
        assert inv.amount == 5_000_000
        assert inv.total_paid == 0

    def test_remaining(self):
        inv = self._make_invoice(amount=5_000_000, total_paid=2_000_000)
        assert inv.remaining == 3_000_000

    def test_remaining_fully_paid(self):
        inv = self._make_invoice(amount=5_000_000, total_paid=5_000_000)
        assert inv.remaining == 0

    def test_is_overdue_true(self):
        inv = self._make_invoice(due_date=date(2026, 1, 1))
        assert inv.is_overdue(today=date(2026, 3, 1)) is True

    def test_is_overdue_false_not_past_due(self):
        inv = self._make_invoice(due_date=date(2026, 6, 1))
        assert inv.is_overdue(today=date(2026, 3, 1)) is False

    def test_is_overdue_false_when_paid(self):
        from terminal_prime.models.invoice import InvoiceStatus
        inv = self._make_invoice(
            due_date=date(2026, 1, 1),
            status=InvoiceStatus.PAYEE,
        )
        assert inv.is_overdue(today=date(2026, 3, 1)) is False

    def test_display_status_overdue(self):
        inv = self._make_invoice(due_date=date(2026, 1, 1))
        assert inv.display_status(today=date(2026, 3, 1)) == "EN_RETARD"

    def test_display_status_normal(self):
        from terminal_prime.models.invoice import InvoiceStatus
        inv = self._make_invoice(
            due_date=date(2026, 6, 1),
            status=InvoiceStatus.PARTIELLE,
        )
        assert inv.display_status(today=date(2026, 3, 1)) == "PARTIELLE"

    def test_format_amount(self):
        inv = self._make_invoice(amount=5_000_000)
        assert inv.format_amount() == "5 000 000 FCFA"

    def test_format_amount_small(self):
        inv = self._make_invoice(amount=500)
        assert inv.format_amount() == "500 FCFA"


class TestPayment:
    def test_create_payment(self):
        from terminal_prime.models.payment import Payment, PaymentMode
        payment = Payment(
            invoice_id=1,
            client_id=1,
            date=date(2026, 2, 1),
            amount=1_000_000,
            mode=PaymentMode.VIREMENT,
            reference="PAY-00001",
        )
        assert payment.amount == 1_000_000
        assert payment.mode == PaymentMode.VIREMENT
        assert payment.id is None

    def test_payment_modes(self):
        from terminal_prime.models.payment import PaymentMode
        assert PaymentMode.VIREMENT.value == "VIREMENT"
        assert PaymentMode.CHEQUE.value == "CHEQUE"
        assert PaymentMode.ESPECES.value == "ESPECES"
