import customtkinter as ctk
from terminal_prime import theme

class KpiCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, badge="", badge_color=None, value_color=None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT, corner_radius=theme.CORNER_RADIUS)
        ctk.CTkLabel(self, text=label.upper(), font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, pady=(20, 8), anchor="w")
        ctk.CTkLabel(self, text=value, font=theme.FONT_KPI,
                     text_color=value_color or theme.ON_SURFACE).pack(padx=24, anchor="w")
        if badge:
            ctk.CTkLabel(self, text=badge, font=theme.FONT_SMALL,
                         text_color=badge_color or theme.PRIMARY,
                         fg_color=theme.SURFACE_LOW, corner_radius=12,
                         padx=8, pady=2).pack(padx=24, pady=(8, 20), anchor="w")
        else:
            ctk.CTkFrame(self, height=20, fg_color="transparent").pack()
