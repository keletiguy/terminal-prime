"""Collections management view with payment form and recent payments."""
import sqlite3
from datetime import date
from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.payment_repo import PaymentRepo
from terminal_prime.services.dashboard_service import DashboardService


class CollectionsView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn: sqlite3.Connection,
                 on_data_changed: Optional[Callable] = None):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.on_data_changed = on_data_changed
        self.invoice_repo = InvoiceRepo(conn)
        self.payment_repo = PaymentRepo(conn)
        self.dashboard_svc = DashboardService(conn)
        self._unpaid = []
        self._invoice_map = {}
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Gestion des Recouvrements", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(24, 16), anchor="w")

        # ── Two-column layout ────────────────────────────────────────────
        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="x", padx=24, pady=(0, 16))
        cols.grid_columnconfigure(0, weight=1)
        cols.grid_columnconfigure(1, weight=1)

        # ── Left: Payment Form ──────────────────────────────────────────
        form_panel = ctk.CTkFrame(cols, fg_color=theme.SURFACE_CONT,
                                  corner_radius=theme.CORNER_RADIUS)
        form_panel.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(form_panel, text="Nouveau Paiement", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        # Facture dropdown
        self._unpaid = self.invoice_repo.get_unpaid()
        self._invoice_map = {}
        invoice_labels = []
        for inv in self._unpaid:
            label = f"{inv.number} - {inv.client_name or 'N/A'} ({inv.remaining:,} FCFA)".replace(",", " ")
            invoice_labels.append(label)
            self._invoice_map[label] = inv

        ctk.CTkLabel(form_panel, text="FACTURE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.invoice_var = ctk.StringVar()
        self.invoice_dd = ctk.CTkOptionMenu(
            form_panel, values=invoice_labels or ["--"], variable=self.invoice_var,
            fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
            font=theme.FONT_BODY, command=self._on_invoice_selected)
        self.invoice_dd.pack(fill="x", padx=24, pady=(0, 12))

        # Date entry
        ctk.CTkLabel(form_panel, text="DATE (JJ/MM/AAAA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.date_var = ctk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        ctk.CTkEntry(form_panel, textvariable=self.date_var, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY).pack(fill="x", padx=24, pady=(0, 12))

        # Mode dropdown
        ctk.CTkLabel(form_panel, text="MODE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.mode_var = ctk.StringVar(value="VIREMENT")
        ctk.CTkOptionMenu(form_panel, values=["VIREMENT", "CHEQUE", "ESPECES"],
                          variable=self.mode_var,
                          fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
                          font=theme.FONT_BODY).pack(fill="x", padx=24, pady=(0, 12))

        # Amount entry
        ctk.CTkLabel(form_panel, text="MONTANT (FCFA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.amount_var = ctk.StringVar()
        ctk.CTkEntry(form_panel, textvariable=self.amount_var, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY).pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(form_panel, text="Valider le Paiement", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD,
                      command=self._validate_payment).pack(padx=24, pady=(0, 20), anchor="e")

        # Auto-select first invoice
        if invoice_labels:
            self.invoice_var.set(invoice_labels[0])
            self._on_invoice_selected(invoice_labels[0])

        # ── Right: Recent Payments ──────────────────────────────────────
        recent_panel = ctk.CTkFrame(cols, fg_color=theme.SURFACE_CONT,
                                    corner_radius=theme.CORNER_RADIUS)
        recent_panel.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(recent_panel, text="Paiements Recents", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        recent = self.payment_repo.get_recent(5)
        if recent:
            for pay in recent:
                row_frame = ctk.CTkFrame(recent_panel, fg_color=theme.SURFACE_LOW,
                                         corner_radius=theme.CORNER_RADIUS)
                row_frame.pack(fill="x", padx=24, pady=(0, 8))
                ctk.CTkLabel(row_frame, text=pay.reference, font=theme.FONT_BODY_BOLD,
                             text_color=theme.ON_SURFACE).pack(side="left", padx=16, pady=12)
                ctk.CTkLabel(row_frame, text=theme.format_fcfa(pay.amount),
                             font=theme.FONT_BODY, text_color=theme.PRIMARY
                             ).pack(side="right", padx=16, pady=12)
        else:
            ctk.CTkLabel(recent_panel, text="Aucun paiement", font=theme.FONT_BODY,
                         text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=20)

        # Spacer
        ctk.CTkFrame(recent_panel, height=20, fg_color="transparent").pack()

        # ── Stats Bar ───────────────────────────────────────────────────
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=24, pady=(0, 24))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1)

        collected_mtd = self.payment_repo.get_total_collected_mtd()
        KpiCard(stats_row, label="Total Collecte MTD",
                value=theme.format_fcfa(collected_mtd)).grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        kpis = self.dashboard_svc.get_kpis()
        KpiCard(stats_row, label="Encours Restant",
                value=theme.format_fcfa(kpis["outstanding"])).grid(row=0, column=1, padx=8, sticky="nsew")

        dso = self.dashboard_svc.get_dso()
        KpiCard(stats_row, label="DSO",
                value=f"{dso:.0f} jours").grid(row=0, column=2, padx=(8, 0), sticky="nsew")

    def _on_invoice_selected(self, label):
        inv = self._invoice_map.get(label)
        if inv:
            self.amount_var.set(str(inv.remaining))

    def _validate_payment(self):
        label = self.invoice_var.get()
        inv = self._invoice_map.get(label)
        if inv is None:
            messagebox.showwarning("Facture requise", "Veuillez selectionner une facture.",
                                   parent=self)
            return

        # Parse date
        date_str = self.date_var.get().strip()
        try:
            parts = date_str.split("/")
            pay_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
        except (ValueError, IndexError):
            messagebox.showwarning("Date invalide", "Format attendu: JJ/MM/AAAA", parent=self)
            return

        # Parse amount
        try:
            amount = int(self.amount_var.get().strip())
        except ValueError:
            messagebox.showwarning("Montant invalide", "Le montant doit etre un nombre entier.",
                                   parent=self)
            return

        if amount <= 0:
            messagebox.showwarning("Montant invalide", "Le montant doit etre positif.",
                                   parent=self)
            return

        if amount > inv.remaining:
            messagebox.showwarning(
                "Montant trop eleve",
                f"Le montant ({amount:,} FCFA) depasse le solde restant ({inv.remaining:,} FCFA).".replace(",", " "),
                parent=self)
            return

        mode = self.mode_var.get()

        try:
            self.payment_repo.create(
                invoice_id=inv.id, client_id=inv.client_id,
                pay_date=pay_date, amount=amount, mode=mode)
            self.invoice_repo.update_status_from_payments(inv.id)
            messagebox.showinfo("Succes", f"Paiement de {theme.format_fcfa(amount)} enregistre.",
                                parent=self)
            self.refresh()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
