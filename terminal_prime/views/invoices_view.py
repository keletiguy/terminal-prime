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
                 on_data_changed: Optional[Callable] = None,
                 on_open_collection: Optional[Callable] = None):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.on_data_changed = on_data_changed
        self.on_open_collection = on_open_collection
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

        # ── Search Bar ───────────────────────────────────────────────────
        search_bar = ctk.CTkFrame(self, fg_color=theme.SURFACE_CONT,
                                   corner_radius=theme.CORNER_RADIUS)
        search_bar.pack(fill="x", padx=24, pady=(0, 8))

        search_inner = ctk.CTkFrame(search_bar, fg_color="transparent")
        search_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(search_inner, text="RECHERCHER", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 8))
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_inner, textvariable=self.search_var,
            fg_color=theme.SURFACE_LOWEST, border_width=0,
            font=theme.FONT_BODY, width=400,
            placeholder_text="N° facture, client ou affilie...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_var.trace_add("write", lambda *_: self._on_search_changed())

        ctk.CTkButton(search_inner, text="Effacer", width=80,
                      fg_color=theme.SURFACE_HIGH, text_color=theme.ON_SURFACE_VAR,
                      font=theme.FONT_BODY,
                      command=self._clear_search).pack(side="left")

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

        # Period filter
        self.period_var = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(inner, values=["Tous", "Mois en cours", "Dernier trimestre", "Annee en cours"],
                          variable=self.period_var,
                          fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_BRIGHT,
                          font=theme.FONT_BODY, width=180,
                          command=lambda _: self._apply_filters()
                          ).pack(side="left", padx=(0, 8))

        # Buttons (right side, packed right-to-left)
        ctk.CTkButton(inner, text="Importer Mediciel", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD, width=160,
                      command=self._import_file).pack(side="right", padx=(8, 0))
        ctk.CTkButton(inner, text="Nouvelle Facture", fg_color=theme.SURFACE_BRIGHT,
                      text_color=theme.ON_SURFACE, font=theme.FONT_BODY_BOLD, width=150,
                      command=self._new_invoice).pack(side="right", padx=(8, 0))
        ctk.CTkButton(inner, text="Vider la base", fg_color=theme.ERROR_CONT,
                      text_color=theme.ERROR, font=theme.FONT_BODY_BOLD, width=130,
                      command=self._reset_database).pack(side="right")

        # ── DataGrid ────────────────────────────────────────────────────
        self.grid_widget = DataGrid(
            self,
            columns=[("N.Facture", 160), ("Date", 100), ("Client", 150),
                     ("Affilie", 150), ("Montant", 120), ("Solde", 100), ("Statut", 100)],
            status_columns={6},
            on_page_change=self._on_page_change,
            on_double_click=self._on_invoice_double_click,
        )
        self.grid_widget.pack(fill="x", padx=24, pady=(0, 24))
        self._current_invoices = []

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
        date_from, date_to = self._get_period_dates()
        return {
            "status": None if status == "Tous" else status,
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

    def _on_search_changed(self):
        self.current_page = 0
        self._load_data()

    def _clear_search(self):
        self.search_var.set("")
        self.current_page = 0
        self._load_data()

    def _load_data(self):
        search = self.search_var.get().strip()
        params = self._get_filter_params()

        if len(search) >= 2:
            invoices, total = self._search_invoices(search, params)
        else:
            total = self.invoice_repo.count(**params)
            invoices = self.invoice_repo.get_all(
                **params, limit=self.PAGE_SIZE, offset=self.current_page * self.PAGE_SIZE)

        self._current_invoices = invoices
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

    def _search_invoices(self, search, params):
        """Search invoices by number, client name or affiliate name."""
        from terminal_prime.models.invoice import Invoice, InvoiceStatus

        query = """SELECT i.*, c.name as client_name, a.name as affiliate_name,
                          COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as total_paid
                   FROM invoices i
                   JOIN clients c ON i.client_id = c.id
                   JOIN affiliates a ON i.affiliate_id = a.id
                   WHERE (i.number LIKE ? OR c.name LIKE ? OR a.name LIKE ?)"""
        sql_params = [f"%{search}%", f"%{search}%", f"%{search}%"]

        if params.get("status"):
            query += " AND i.status = ?"
            sql_params.append(params["status"])
        if params.get("date_from"):
            query += " AND i.date >= ?"
            sql_params.append(params["date_from"].isoformat())
        if params.get("date_to"):
            query += " AND i.date <= ?"
            sql_params.append(params["date_to"].isoformat())

        count_query = f"SELECT COUNT(*) FROM ({query})"
        total = self.conn.execute(count_query, sql_params).fetchone()[0]

        query += " ORDER BY i.date DESC LIMIT ? OFFSET ?"
        sql_params.extend([self.PAGE_SIZE, self.current_page * self.PAGE_SIZE])
        rows = self.conn.execute(query, sql_params).fetchall()

        invoices = []
        for r in rows:
            invoices.append(Invoice(
                id=r["id"], number=r["number"],
                client_id=r["client_id"], affiliate_id=r["affiliate_id"],
                date=date.fromisoformat(r["date"]),
                due_date=date.fromisoformat(r["due_date"]),
                amount=r["amount"], status=InvoiceStatus(r["status"]),
                total_paid=r["total_paid"],
                client_name=r["client_name"],
                affiliate_name=r["affiliate_name"],
            ))
        return invoices, total

    def _on_invoice_double_click(self, idx, row_data):
        """Navigate to collections with this invoice pre-selected."""
        if idx < len(self._current_invoices) and self.on_open_collection:
            inv = self._current_invoices[idx]
            self.on_open_collection(inv)

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
                f"Nouvelles factures: {stats['imported']}\n"
                f"Reglements mis a jour: {stats['updated']}\n"
                f"Inchangees: {stats['duplicates']}\n"
                f"Clients crees: {stats['clients_created']}\n"
                f"Affilies crees: {stats['affiliates_created']}\n"
                f"Erreurs: {stats['errors']}",
            )
            self.refresh()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Erreur d'import", str(e))

    def _reset_database(self):
        confirm = messagebox.askyesno(
            "Reinitialiser la base",
            "Attention : cette action va supprimer TOUTES les factures, "
            "paiements, clients et affilies.\n\n"
            "Vous pourrez ensuite reimporter un nouveau fichier Mediciel.\n\n"
            "Continuer ?",
            parent=self)
        if not confirm:
            return

        try:
            self.conn.executescript("""
                DELETE FROM payments;
                DELETE FROM invoices;
                DELETE FROM affiliates;
                DELETE FROM clients;
            """)
            messagebox.showinfo("Base reintialisee",
                                "Toutes les donnees ont ete supprimees.\n"
                                "Vous pouvez maintenant importer un nouveau fichier.",
                                parent=self)
            self.refresh()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Erreur", str(e), parent=self)

    def _new_invoice(self):
        InvoiceModal(self, self.conn, on_save=self._on_invoice_saved)

    def _on_invoice_saved(self):
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()

    def refresh(self):
        """Refresh data without rebuilding widgets."""
        self.current_page = 0
        outstanding = self._get_outstanding()
        self.kpi_encours.update_values(theme.format_fcfa(outstanding))
        self._load_data()
