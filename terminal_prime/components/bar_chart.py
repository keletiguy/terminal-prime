import customtkinter as ctk
from tkinter import Canvas
from typing import List, Tuple
from terminal_prime import theme

class BarChart(ctk.CTkFrame):
    def __init__(self, parent, title="", subtitle=""):
        super().__init__(parent, fg_color=theme.SURFACE_CONT, corner_radius=theme.CORNER_RADIUS)
        if title:
            ctk.CTkLabel(self, text=title, font=theme.FONT_TITLE,
                         text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 2), anchor="w")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=theme.FONT_SMALL,
                         text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(0, 16), anchor="w")
        self.canvas = Canvas(self, bg=theme.SURFACE_CONT, highlightthickness=0, height=200)
        self.canvas.pack(fill="x", padx=24, pady=(0, 20))
        self._bars_data = []
        self.canvas.bind("<Configure>", lambda e: self._draw())

    def set_data(self, bars: List[Tuple[str, int, str]]):
        """bars: [(label, value, color), ...]"""
        self._bars_data = bars
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        if not self._bars_data:
            return
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 200
        max_val = max(v for _, v, _ in self._bars_data) or 1
        n = len(self._bars_data)
        bar_width = max(20, (w - 60) // n - 20)
        x = 30
        for label, value, color in self._bars_data:
            bar_height = int((value / max_val) * (h - 60))
            y_top = h - 30 - bar_height
            self.canvas.create_rectangle(x, y_top, x + bar_width, h - 30,
                                          fill=color, outline="")
            formatted = f"{value:,.0f}".replace(",", " ")
            self.canvas.create_text(x + bar_width // 2, y_top - 12, text=formatted,
                                     fill=color, font=(theme.FONT_FAMILY, 9, "bold"))
            self.canvas.create_text(x + bar_width // 2, h - 12, text=label,
                                     fill=theme.ON_SURFACE_VAR, font=(theme.FONT_FAMILY, 9, "bold"))
            x += bar_width + 20
