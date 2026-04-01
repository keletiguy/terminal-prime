"""Invoices management view with filtering, import, and manual creation."""
import sqlite3
from datetime import date, timedelta
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import customtkinter as ctk

from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.import_service import ImportService


class InvoiceModal(ctk.CTkToplevel):
    """Modal dialog for creating a new invoice."""

    def __init__(self, parent, conn: sqlite3.Connection, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.conn = conn
        self.on_save = on_save
        self.client_repo = ClientRepo(conn)
        self.affiliate_repo = AffiliateRepo(conn)
        self.invoice_repo = InvoiceRepo(conn)

        self.title("Nouvelle Facture")
        self.geometry("450x400")
        self.configure(fg_color=theme.SURFACE)
        self.resizable(False, False)
        self.grab_set()

        self._clients = self.client_repo.get_all()
        self._client_map = {c.name: c.id for c in self._clients}
        self._affiliates = []

        pad = {"padx": 24, "pady": (8, 0), "anchor": "w"}

        ctk.CTkLabel(self, text="Nouvelle Facture", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        ctk.CTkLabel(self, text="N. FACTURE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(**pad)
        self.number_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.number_var, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY).pack(fill="x", padx=24, pady=(4, 0))

        ctk.CTkLabel(self, text="CLIENT PRINCIPAL", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(**pad)
        client_names = [c.name for c in self._clients]
        self.client_var = ctk.StringVar()
        self.client_dd = ctk.CTkOptionMenu(
            self, values=client_names or ["--"], variable=self.client_var,
            fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
            font=theme.FONT_BODY, command=self._on_client_changed)
        self.client_dd.pack(fill="x", padx=24, pady=(4, 0))

        ctk.CTkLabel(self, text="AFFILIE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(**pad)
        self.affiliate_var = ctk.StringVar()
        self.affiliate_dd = ctk.CTkOptionMenu(
            self, values=["--"], variable=self.affiliate_var,
            fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
            font=theme.FONT_BODY)
        self.affiliate_dd.pack(fill="x", padx=24, pady=(4, 0))

        ctk.CTkLabel(self, text="MONTANT (FCFA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(**pad)
        self.amount_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.amount_var, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY).pack(fill="x", padx=24, pady=(4, 0))

        ctk.CTkButton(self, text="Enregistrer", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD,
                      command=self._save).pack(padx=24, pady=20, anchor="e")

        if client_names:
            self.client_var.set(client_names[0])
            self._on_client_changed(client_names[0])

    def _on_client_changed(self, name):
        client_id = self._client_map.get(name)
        if client_id is None:
            return
        self._affiliates = self.affiliate_repo.get_by_client(client_id)
        aff_names = [a.name for a in self._affiliates]
        self.affiliate_dd.configure(values=aff_names or ["--"])
        if aff_names:
            self.affiliate_var.set(aff_names[0])
        else:
            self.affiliate_var.set("--")

    def _save(self):
        number = self.number_var.get().strip()
        client_name = self.client_var.get()
        affiliate_name = self.affiliate_var.get()
        amount_str = self.amount_var.get().strip()

        if not number or not amount_str or client_name == "--" or affiliate_name == "--":
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs.",
                                   parent=self)
            return
        try:
            amount = int(amount_str)
        except ValueError:
            messagebox.showwarning("Montant invalide", "Le montant doit etre un nombre entier.",
                                   parent=self)
            return

        client_id = self._client_map[client_name]
        aff_map = {a.name: a.id for a in self._affiliates}
        affiliate_id = aff_map.get(affiliate_name)
        if affiliate_id is None:
            messagebox.showwarning("Affilie invalide", "Affilie non trouve.", parent=self)
            return

        inv_date = date.today()
        due_date = inv_date + timedelta(days=30)

        try:
            self.invoice_repo.create(
                number=number, client_id=client_id, affiliate_id=affiliate_id,
                inv_date=inv_date, due_date=due_date, amount=amount)
            messagebox.showinfo("Succes", f"Facture {number} creee.", parent=self)
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)


class InvoicesView(ctk.CTkScrollableFrame):
    PAGE_SIZE = 10

    def __init__(self, parent, conn: sqlite3.Connection,
                 on_data_changed: Optional[Callable] = None):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.on_data_changed = on_data_changed
        self.invoice_repo = InvoiceRepo(conn)
        self.client_repo = ClientRepo(conn)
        self.import_svc = ImportService(conn)
        self.current_page = 0
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Gestion des Factures", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).grid(row=0, column=0, sticky="w")

        # Encours KPI
        outstanding = self._get_outstanding()
        self.kpi_encours = KpiCard(header, label="Total Encours",
                                   value=theme.format_fcfa(outstanding))
        self.kpi_encours.grid(row=0, column=2, padx=(16, 0), sticky="e")

        # ── Filter Bar ───────────────────────────────────────────────────
        filter_bar = ctk.CTkFrame(self, fg_color=theme.SURFACE_HIGH,
                                  corner_radius=theme.CORNER_RADIUS)
        filter_bar.pack(fill="x", padx=24, pady=(0, 16))

        inner = ctk.CTkFrame(filter_bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        # Status filter
        self.status_var = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(inner, values=["Tous", "EN_ATTENTE", "PARTIELLE", "PAYEE"],
                          variable=self.status_var,
                          fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_BRIGHT,
                          font=theme.FONT_BODY, width=150,
                          command=lambda _: self._apply_filters()
                          ).pack(side="left", padx=(0, 8))

        # Client filter
        self.client_var = ctk.StringVar(value="Tous")
        clients = self.client_repo.get_all()
        client_names = ["Tous"] + [c.name for c in clients]
        self._client_map = {c.name: c.id for c in clients}
        ctk.CTkOptionMenu(inner, values=client_names, variable=self.client_var,
                          fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_BRIGHT,
                          font=theme.FONT_BODY, width=180,
                          command=lambda _: self._apply_filters()
                          ).pack(side="left", padx=(0, 8))

        # Period filter
        self.period_var = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(inner, values=["Tous", "Mois en cours", "Dernier trimestre", "Annee en cours"],
                          variable=self.period_var,
                          fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_BRIGHT,
                          font=theme.FONT_BODY, width=180,
                          command=lambda _: self._apply_filters()
                          ).pack(side="left", padx=(0, 8))

        # Buttons
        ctk.CTkButton(inner, text="Importer Mediciel", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD, width=160,
                      command=self._import_file).pack(side="right", padx=(8, 0))
        ctk.CTkButton(inner, text="Nouvelle Facture", fg_color=theme.SURFACE_BRIGHT,
                      text_color=theme.ON_SURFACE, font=theme.FONT_BODY_BOLD, width=150,
                      command=self._new_invoice).pack(side="right")

        # ── DataGrid ────────────────────────────────────────────────────
        self.grid_widget = DataGrid(
            self,
            columns=[("N.Facture", 160), ("Date", 100), ("Client", 150),
                     ("Affilie", 150), ("Montant", 120), ("Solde", 100), ("Statut", 100)],
            status_columns={6},
            on_page_change=self._on_page_change,
        )
        self.grid_widget.pack(fill="x", padx=24, pady=(0, 24))

        self._load_data()

    def _get_period_dates(self):
        period = self.period_var.get()
        today = date.today()
        if period == "Mois en cours":
            return today.replace(day=1), today
        elif period == "Dernier trimestre":
            return today - timedelta(days=90), today
        elif period == "Annee en cours":
            return date(today.year, 1, 1), today
        return None, None

    def _get_filter_params(self):
        status = self.status_var.get()
        client = self.client_var.get()
        date_from, date_to = self._get_period_dates()
        return {
            "status": None if status == "Tous" else status,
            "client_id": self._client_map.get(client),
            "date_from": date_from,
            "date_to": date_to,
        }

    def _get_outstanding(self):
        row = self.conn.execute(
            """SELECT COALESCE(SUM(i.amount - COALESCE(
                (SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0
            )), 0) AS total
            FROM invoices i WHERE i.status != 'PAYEE'"""
        ).fetchone()
        return row["total"]

    def _load_data(self):
        params = self._get_filter_params()
        total = self.invoice_repo.count(**params)
        invoices = self.invoice_repo.get_all(
            **params, limit=self.PAGE_SIZE, offset=self.current_page * self.PAGE_SIZE)

        rows = []
        for inv in invoices:
            rows.append([
                inv.number,
                inv.date.strftime("%d/%m/%Y"),
                inv.client_name or "",
                inv.affiliate_name or "",
                theme.format_fcfa(inv.amount),
                theme.format_fcfa(inv.remaining),
                inv.display_status(),
            ])
        self.grid_widget.set_data(rows, total, self.current_page, self.PAGE_SIZE)

    def _apply_filters(self):
        self.current_page = 0
        self._load_data()

    def _on_page_change(self, page):
        self.current_page = page
        self._load_data()

    def _import_file(self):
        path = filedialog.askopenfilename(
            title="Importer fichier Mediciel",
            filetypes=[("Excel", "*.xlsx *.xls")],
        )
        if not path:
            return
        try:
            stats = self.import_svc.import_file(path)
            messagebox.showinfo(
                "Import termine",
                f"Importes: {stats['imported']}\n"
                f"Doublons: {stats['duplicates']}\n"
                f"Clients crees: {stats['clients_created']}\n"
                f"Affilies crees: {stats['affiliates_created']}\n"
                f"Erreurs: {stats['errors']}",
            )
            self.refresh()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Erreur d'import", str(e))

    def _new_invoice(self):
        InvoiceModal(self, self.conn, on_save=self._on_invoice_saved)

    def _on_invoice_saved(self):
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_page = 0
        self._build()
