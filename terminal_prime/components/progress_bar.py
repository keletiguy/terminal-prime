import customtkinter as ctk
from tkinter import Canvas
from terminal_prime import theme


class GradientProgressBar(ctk.CTkFrame):
    def __init__(self, parent, label="", value=0, max_label=""):
        super().__init__(parent, fg_color="transparent")
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x")
        self._label_widget = ctk.CTkLabel(top, text=label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE)
        self._label_widget.pack(side="left")
        self._max_label_widget = ctk.CTkLabel(top, text=max_label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.PRIMARY)
        self._max_label_widget.pack(side="right")
        self.canvas = Canvas(self, bg=theme.SURFACE_LOWEST, highlightthickness=0, height=8)
        self.canvas.pack(fill="x", pady=(4, 0))
        self._value = value
        self.canvas.bind("<Configure>", lambda e: self._render_bar())

    def _render_bar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        fill_w = int(w * min(self._value / 100, 1.0))
        if fill_w > 0:
            self.canvas.create_rectangle(0, 0, fill_w, 8, fill=theme.PRIMARY, outline="")

    def set_value(self, value, label=None):
        self._value = value
        self._max_label_widget.configure(text=label or f"{value:.1f}%")
        self._render_bar()
