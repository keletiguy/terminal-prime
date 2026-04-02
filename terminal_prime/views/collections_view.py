"""Collections management view with payment form and recent payments."""
import sqlite3
from datetime import date
from tkinter import messagebox, ttk
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

        # Facture search (instead of dropdown - too many invoices for dropdown)
        self._unpaid = []
        self._selected_invoice = None

        ctk.CTkLabel(form_panel, text="RECHERCHER FACTURE (N° OU CLIENT)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            form_panel, textvariable=self.search_var, fg_color=theme.SURFACE_LOWEST,
            border_width=0, font=theme.FONT_BODY,
            placeholder_text="Tapez un numero ou nom de client...")
        self.search_entry.pack(fill="x", padx=24, pady=(0, 4))
        self.search_var.trace_add("write", lambda *_: self._on_search())

        # Results list (scrollable Treeview)
        self.results_frame = ctk.CTkFrame(form_panel, fg_color=theme.SURFACE_LOWEST,
                                           corner_radius=theme.CORNER_RADIUS, height=180)
        self.results_frame.pack(fill="x", padx=24, pady=(0, 12))
        self.results_frame.pack_propagate(False)

        style = ttk.Style()
        style.configure("Search.Treeview",
                         background=theme.SURFACE_LOWEST,
                         foreground=theme.ON_SURFACE,
                         fieldbackground=theme.SURFACE_LOWEST,
                         font=(theme.FONT_FAMILY, 11),
                         rowheight=32, borderwidth=0, relief="flat")
        style.configure("Search.Treeview.Heading", background=theme.SURFACE_LOWEST,
                         foreground=theme.ON_SURFACE_VAR,
                         font=(theme.FONT_FAMILY, 9, "bold"), borderwidth=0)
        style.map("Search.Treeview",
                  background=[("selected", theme.PRIMARY_CONT)],
                  foreground=[("selected", "white")])

        self.results_tree = ttk.Treeview(self.results_frame,
                                          columns=("number", "client", "solde"),
                                          show="headings", style="Search.Treeview",
                                          selectmode="browse")
        self.results_tree.heading("number", text="N. FACTURE", anchor="w")
        self.results_tree.heading("client", text="CLIENT", anchor="w")
        self.results_tree.heading("solde", text="SOLDE", anchor="e")
        self.results_tree.column("number", width=160, minwidth=100)
        self.results_tree.column("client", width=160, minwidth=100)
        self.results_tree.column("solde", width=100, minwidth=80, anchor="e")

        scrollbar = ctk.CTkScrollbar(self.results_frame, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.results_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._search_results = []

        # Selected invoice display
        self.selected_label = ctk.CTkLabel(form_panel, text="Aucune facture selectionnee",
                                            font=theme.FONT_BODY,
                                            text_color=theme.ON_SURFACE_VAR)
        self.selected_label.pack(padx=24, pady=(0, 12), anchor="w")

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

        # Reference piece
        ctk.CTkLabel(form_panel, text="REFERENCE PIECE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.reference_var = ctk.StringVar()
        ctk.CTkEntry(form_panel, textvariable=self.reference_var, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY,
                     placeholder_text="N° cheque, ref virement, bordereau...").pack(fill="x", padx=24, pady=(0, 12))

        # Payment type toggle
        type_frame = ctk.CTkFrame(form_panel, fg_color="transparent")
        type_frame.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkLabel(type_frame, text="TYPE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 12))
        self.partial_var = ctk.BooleanVar(value=False)
        self.btn_total = ctk.CTkButton(type_frame, text="Total", width=80, height=30,
                                        fg_color=theme.PRIMARY_CONT, text_color="white",
                                        font=theme.FONT_BODY_BOLD,
                                        corner_radius=theme.CORNER_RADIUS,
                                        command=lambda: self._set_payment_type(False))
        self.btn_total.pack(side="left", padx=(0, 4))
        self.btn_partial = ctk.CTkButton(type_frame, text="Partiel", width=80, height=30,
                                          fg_color=theme.SURFACE_HIGH, text_color=theme.ON_SURFACE_VAR,
                                          font=theme.FONT_BODY,
                                          corner_radius=theme.CORNER_RADIUS,
                                          command=lambda: self._set_payment_type(True))
        self.btn_partial.pack(side="left")

        # Amount entry
        ctk.CTkLabel(form_panel, text="MONTANT (FCFA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 4), anchor="w")
        self.amount_var = ctk.StringVar()
        self.amount_entry = ctk.CTkEntry(form_panel, textvariable=self.amount_var,
                     fg_color=theme.SURFACE_LOWEST, border_width=0, font=theme.FONT_BODY,
                     state="disabled")
        self.amount_entry.pack(fill="x", padx=24, pady=(0, 4))
        self.amount_var.trace_add("write", lambda *_: self._update_remaining_preview())

        # Remaining preview after payment
        self.remaining_label = ctk.CTkLabel(form_panel, text="",
                                             font=theme.FONT_SMALL,
                                             text_color=theme.ON_SURFACE_VAR)
        self.remaining_label.pack(padx=24, pady=(0, 12), anchor="w")

        ctk.CTkButton(form_panel, text="Valider le Paiement", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD,
                      command=self._validate_payment).pack(padx=24, pady=(0, 20), anchor="e")

        # ── Right: Recent Payments ──────────────────────────────────────
        recent_panel = ctk.CTkFrame(cols, fg_color=theme.SURFACE_CONT,
                                    corner_radius=theme.CORNER_RADIUS)
        recent_panel.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(recent_panel, text="Paiements Recents", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        # Recent payments as Treeview for speed
        recent_tree = ttk.Treeview(recent_panel,
                                    columns=("ref", "mode", "montant"),
                                    show="headings", style="Search.Treeview",
                                    selectmode="none", height=8)
        recent_tree.heading("ref", text="REFERENCE", anchor="w")
        recent_tree.heading("mode", text="MODE", anchor="w")
        recent_tree.heading("montant", text="MONTANT", anchor="e")
        recent_tree.column("ref", width=180, minwidth=100, stretch=True)
        recent_tree.column("mode", width=100, minwidth=60, stretch=True)
        recent_tree.column("montant", width=120, minwidth=80, anchor="e", stretch=True)
        recent_tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        recent = self.payment_repo.get_recent(10)
        for i, pay in enumerate(recent):
            tags = ["even" if i % 2 == 0 else "odd"]
            recent_tree.insert("", "end",
                               values=(pay.reference, pay.mode.value,
                                       theme.format_fcfa(pay.amount)),
                               tags=tags)
        recent_tree.tag_configure("even", background=theme.SURFACE_LOW)
        recent_tree.tag_configure("odd", background=theme.SURFACE_CONT)

        # ── Stats Bar ───────────────────────────────────────────────────
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=24, pady=(0, 24))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat")

        collected_mtd = self.payment_repo.get_total_collected_mtd()
        KpiCard(stats_row, label="Total Collecte MTD",
                value=theme.format_fcfa(collected_mtd)).grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        kpis = self.dashboard_svc.get_kpis()
        KpiCard(stats_row, label="Encours Restant",
                value=theme.format_fcfa(kpis["outstanding"])).grid(row=0, column=1, padx=8, sticky="nsew")

        dso = self.dashboard_svc.get_dso()
        KpiCard(stats_row, label="DSO",
                value=f"{dso:.0f} jours").grid(row=0, column=2, padx=(8, 0), sticky="nsew")

    def _on_search(self):
        query = self.search_var.get().strip()
        self.results_tree.delete(*self.results_tree.get_children())
        self._search_results = []

        if len(query) < 2:
            return

        # Search in DB - no LIMIT, all matching unpaid invoices
        rows = self.conn.execute(
            """SELECT i.id, i.number, i.amount, i.status, i.client_id, c.name as client_name,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as paid
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               WHERE i.status != 'PAYEE'
                 AND (i.number LIKE ? OR c.name LIKE ?)
               ORDER BY c.name, i.date DESC""",
            (f"%{query}%", f"%{query}%")
        ).fetchall()

        self._search_results = rows
        for row in rows:
            remaining = row["amount"] - row["paid"]
            solde_text = f"{remaining:,} FCFA".replace(",", " ")
            self.results_tree.insert("", "end",
                                      values=(row["number"], row["client_name"], solde_text))

    def _on_tree_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return
        idx = self.results_tree.index(selection[0])
        if idx >= len(self._search_results):
            return
        row = self._search_results[idx]
        remaining = row["amount"] - row["paid"]

        from terminal_prime.models.invoice import Invoice, InvoiceStatus
        self._selected_invoice = Invoice(
            id=row["id"], number=row["number"], client_id=row["client_id"], affiliate_id=0,
            date=date.today(), due_date=date.today(),
            amount=row["amount"], status=InvoiceStatus(row["status"]),
            total_paid=row["paid"], client_name=row["client_name"]
        )
        self.selected_label.configure(
            text=f"Facture: {row['number']} - {row['client_name']} | Solde: {remaining:,} FCFA".replace(",", " "),
            text_color=theme.PRIMARY)
        # Set amount based on payment type
        if self.partial_var.get():
            self.amount_entry.configure(state="normal")
            self.amount_var.set("")
            self.remaining_label.configure(
                text=f"Solde total: {remaining:,} FCFA — saisissez le montant partiel".replace(",", " "))
        else:
            self.amount_entry.configure(state="disabled")
            self.amount_var.set(str(remaining))
            self.remaining_label.configure(text="")

    def _set_payment_type(self, is_partial: bool):
        self.partial_var.set(is_partial)
        if is_partial:
            self.btn_partial.configure(fg_color=theme.PRIMARY_CONT, text_color="white",
                                        font=theme.FONT_BODY_BOLD)
            self.btn_total.configure(fg_color=theme.SURFACE_HIGH, text_color=theme.ON_SURFACE_VAR,
                                      font=theme.FONT_BODY)
            self.amount_entry.configure(state="normal")
            if self._selected_invoice:
                self.amount_var.set("")
                remaining = self._selected_invoice.remaining
                self.remaining_label.configure(
                    text=f"Solde total: {remaining:,} FCFA — saisissez le montant partiel".replace(",", " "))
        else:
            self.btn_total.configure(fg_color=theme.PRIMARY_CONT, text_color="white",
                                      font=theme.FONT_BODY_BOLD)
            self.btn_partial.configure(fg_color=theme.SURFACE_HIGH, text_color=theme.ON_SURFACE_VAR,
                                        font=theme.FONT_BODY)
            self.amount_entry.configure(state="disabled")
            if self._selected_invoice:
                self.amount_var.set(str(self._selected_invoice.remaining))
                self.remaining_label.configure(text="")

    def _update_remaining_preview(self):
        if not self._selected_invoice or not self.partial_var.get():
            return
        try:
            amount = int(self.amount_var.get().strip())
            remaining = self._selected_invoice.remaining
            after = remaining - amount
            if amount <= 0:
                self.remaining_label.configure(
                    text=f"Solde total: {remaining:,} FCFA".replace(",", " "),
                    text_color=theme.ON_SURFACE_VAR)
            elif after > 0:
                self.remaining_label.configure(
                    text=f"Solde apres paiement: {after:,} FCFA (partiel)".replace(",", " "),
                    text_color=theme.TERTIARY)
            elif after == 0:
                self.remaining_label.configure(
                    text="Solde apres paiement: 0 FCFA (solde complet)",
                    text_color="#66bb6a")
            else:
                self.remaining_label.configure(
                    text=f"Montant depasse le solde de {-after:,} FCFA".replace(",", " "),
                    text_color=theme.ERROR)
        except ValueError:
            pass

    def _validate_payment(self):
        inv = self._selected_invoice
        if inv is None:
            messagebox.showwarning("Facture requise", "Veuillez rechercher et selectionner une facture.",
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
        reference = self.reference_var.get().strip()

        if not reference:
            messagebox.showwarning("Reference requise",
                                   "Veuillez saisir la reference de la piece (N° cheque, ref virement, etc.).",
                                   parent=self)
            return

        try:
            self.payment_repo.create(
                invoice_id=inv.id, client_id=inv.client_id,
                pay_date=pay_date, amount=amount, mode=mode, reference=reference)
            self.invoice_repo.update_status_from_payments(inv.id)

            after_remaining = inv.remaining - amount
            if after_remaining > 0:
                pay_type = "PARTIEL"
                extra = f"\nSolde restant: {theme.format_fcfa(after_remaining)}"
            else:
                pay_type = "TOTAL"
                extra = "\nFacture entierement soldee."

            messagebox.showinfo("Paiement enregistre",
                                f"Paiement {pay_type} de {theme.format_fcfa(amount)}\n"
                                f"Reference: {reference}\n"
                                f"Facture: {inv.number}{extra}",
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
