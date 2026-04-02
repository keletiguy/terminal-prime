"""Fast data grid using native ttk.Treeview with Carbon Console styling."""
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional, Set
import customtkinter as ctk
from terminal_prime import theme


def _setup_treeview_style():
    """Configure ttk style to match Carbon Console theme."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("CarbonGrid.Treeview",
                     background=theme.SURFACE_CONT,
                     foreground=theme.ON_SURFACE,
                     fieldbackground=theme.SURFACE_CONT,
                     font=(theme.FONT_FAMILY, 12),
                     rowheight=44,
                     borderwidth=0,
                     relief="flat")
    style.configure("CarbonGrid.Treeview.Heading",
                     background=theme.SURFACE_LOW,
                     foreground=theme.ON_SURFACE_VAR,
                     font=(theme.FONT_FAMILY, 10, "bold"),
                     borderwidth=0,
                     relief="flat",
                     padding=(20, 10))
    style.map("CarbonGrid.Treeview",
              background=[("selected", theme.PRIMARY_CONT)],
              foreground=[("selected", "white")])
    style.map("CarbonGrid.Treeview.Heading",
              background=[("active", theme.SURFACE_HIGH)])

    # Zebra stripe tags
    style.configure("CarbonGrid.Treeview", rowheight=44)


class DataGrid(ctk.CTkFrame):
    def __init__(self, parent, columns: List[Tuple[str, int]],
                 on_page_change: Optional[Callable] = None,
                 status_columns: Optional[Set[int]] = None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT, corner_radius=theme.CORNER_RADIUS)
        self.columns = columns
        self.on_page_change = on_page_change
        self.status_columns = status_columns or set()
        self.current_page = 0
        self.total_pages = 1

        _setup_treeview_style()

        # Column IDs
        col_ids = [f"c{i}" for i in range(len(columns))]

        # Treeview
        self.tree = ttk.Treeview(self, columns=col_ids, show="headings",
                                  style="CarbonGrid.Treeview", selectmode="browse")

        for i, (col_name, col_width) in enumerate(columns):
            self.tree.heading(col_ids[i], text=col_name.upper(), anchor="w")
            self.tree.column(col_ids[i], width=col_width, minwidth=50,
                             stretch=True, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=2, pady=(2, 0))

        # Zebra stripe tags
        self.tree.tag_configure("even", background=theme.SURFACE_LOW,
                                 foreground=theme.ON_SURFACE)
        self.tree.tag_configure("odd", background=theme.SURFACE_CONT,
                                 foreground=theme.ON_SURFACE)
        # Status tags
        self.tree.tag_configure("EN_RETARD", foreground=theme.ERROR)
        self.tree.tag_configure("PAYEE", foreground="#66bb6a")
        self.tree.tag_configure("PARTIELLE", foreground=theme.TERTIARY)
        self.tree.tag_configure("EN_ATTENTE", foreground=theme.ON_SURFACE_VAR)

        # Pagination bar
        pag = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW, height=44, corner_radius=0)
        pag.pack(fill="x", padx=0, pady=0)
        pag.pack_propagate(False)

        self.page_label = ctk.CTkLabel(pag, text="", font=theme.FONT_LABEL_UPPER,
                                        text_color=theme.ON_SURFACE_VAR)
        self.page_label.pack(side="left", padx=20)

        nav = ctk.CTkFrame(pag, fg_color="transparent")
        nav.pack(side="right", padx=20)
        self.btn_prev = ctk.CTkButton(nav, text="<", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH,
                                       corner_radius=theme.CORNER_RADIUS,
                                       command=self._prev_page)
        self.btn_prev.pack(side="left", padx=2)
        self.btn_next = ctk.CTkButton(nav, text=">", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH,
                                       corner_radius=theme.CORNER_RADIUS,
                                       command=self._next_page)
        self.btn_next.pack(side="left", padx=2)

    def set_data(self, rows: List[List[str]], total: int, page: int, page_size: int):
        """Replace all rows. Fast — Treeview handles thousands of rows natively."""
        # Clear existing
        self.tree.delete(*self.tree.get_children())

        self.current_page = page
        self.total_pages = max(1, (total + page_size - 1) // page_size)

        col_ids = [f"c{i}" for i in range(len(self.columns))]
        for i, row_data in enumerate(rows):
            values = [row_data[j] if j < len(row_data) else "" for j in range(len(self.columns))]
            tags = ["even" if i % 2 == 0 else "odd"]
            # Add status tag for coloring
            for sc in self.status_columns:
                if sc < len(row_data) and row_data[sc]:
                    tags.append(str(row_data[sc]))
            self.tree.insert("", "end", values=values, tags=tags)

        if total > 0:
            start = page * page_size + 1
            end = min(start + page_size - 1, total)
            self.page_label.configure(text=f"AFFICHAGE {start}-{end} SUR {total}")
        else:
            self.page_label.configure(text="AUCUNE DONNEE")

    def _prev_page(self):
        if self.current_page > 0 and self.on_page_change:
            self.on_page_change(self.current_page - 1)

    def _next_page(self):
        if self.current_page < self.total_pages - 1 and self.on_page_change:
            self.on_page_change(self.current_page + 1)
