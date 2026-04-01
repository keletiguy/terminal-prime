import customtkinter as ctk
from tkinter import Canvas
from terminal_prime import theme

class GradientProgressBar(ctk.CTkFrame):
    def __init__(self, parent, label="", value=0, max_label=""):
        super().__init__(parent, fg_color="transparent")
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE).pack(side="left")
        ctk.CTkLabel(top, text=max_label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE).pack(side="right")
        self.canvas = Canvas(self, bg=theme.SURFACE_LOWEST, highlightthickness=0, height=8)
        self.canvas.pack(fill="x", pady=(4, 0))
        self._value = value
        self.canvas.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        fill_w = int(w * min(self._value / 100, 1.0))
        if fill_w > 0:
            self.canvas.create_rectangle(0, 0, fill_w, 8, fill=theme.PRIMARY, outline="")

    def set_value(self, value):
        self._value = value
        self._draw()
