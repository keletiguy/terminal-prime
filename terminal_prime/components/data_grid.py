import customtkinter as ctk
from typing import List, Tuple, Callable, Optional, Set
from terminal_prime import theme
from terminal_prime.components.status_pill import StatusPill

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

        # Header row
        self.header = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW, corner_radius=0)
        self.header.pack(fill="x")
        for col_name, col_width in columns:
            ctk.CTkLabel(self.header, text=col_name.upper(), width=col_width,
                         font=theme.FONT_LABEL_UPPER, text_color=theme.ON_SURFACE_VAR,
                         anchor="w").pack(side="left", padx=20, pady=12)

        # Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        # Pagination
        self.pagination = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW, corner_radius=0)
        self.pagination.pack(fill="x")
        self.page_label = ctk.CTkLabel(self.pagination, text="",
                                        font=theme.FONT_LABEL_UPPER, text_color=theme.ON_SURFACE_VAR)
        self.page_label.pack(side="left", padx=20, pady=12)
        nav = ctk.CTkFrame(self.pagination, fg_color="transparent")
        nav.pack(side="right", padx=20, pady=8)
        self.btn_prev = ctk.CTkButton(nav, text="<", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH, corner_radius=theme.CORNER_RADIUS,
                                       command=self._prev_page)
        self.btn_prev.pack(side="left", padx=2)
        self.btn_next = ctk.CTkButton(nav, text=">", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH, corner_radius=theme.CORNER_RADIUS,
                                       command=self._next_page)
        self.btn_next.pack(side="left", padx=2)

    def set_data(self, rows: List[List[str]], total: int, page: int, page_size: int):
        for widget in self.body.winfo_children():
            widget.destroy()
        self.current_page = page
        self.total_pages = max(1, (total + page_size - 1) // page_size)
        for i, row_data in enumerate(rows):
            bg = theme.SURFACE_LOW if i % 2 == 0 else theme.SURFACE_CONT
            row_frame = ctk.CTkFrame(self.body, fg_color=bg, corner_radius=0, height=52)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)
            for j, (_, col_width) in enumerate(self.columns):
                cell_value = row_data[j] if j < len(row_data) else ""
                if j in self.status_columns and cell_value:
                    StatusPill(row_frame, str(cell_value)).pack(side="left", padx=20, pady=8)
                else:
                    ctk.CTkLabel(row_frame, text=str(cell_value), width=col_width,
                                 font=theme.FONT_BODY, text_color=theme.ON_SURFACE,
                                 anchor="w").pack(side="left", padx=20, pady=8)
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
