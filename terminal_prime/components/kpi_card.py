import customtkinter as ctk
from terminal_prime import theme


class KpiCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, badge="", badge_color=None, value_color=None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT, corner_radius=theme.CORNER_RADIUS)

        self._label_widget = ctk.CTkLabel(self, text=label.upper(), font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR)
        self._label_widget.pack(padx=16, pady=(16, 4), anchor="w", fill="x")

        # Use a slightly smaller font that adapts better
        self._value_widget = ctk.CTkLabel(self, text=value,
                     font=(theme.FONT_FAMILY, 36, "bold"),
                     text_color=value_color or theme.ON_SURFACE,
                     anchor="w")
        self._value_widget.pack(padx=16, anchor="w", fill="x")

        self._badge_widget = ctk.CTkLabel(self, text=badge or "", font=theme.FONT_SMALL,
                     text_color=badge_color or theme.PRIMARY,
                     fg_color=theme.SURFACE_HIGH if badge else "transparent",
                     corner_radius=12, padx=8, pady=2)
        self._badge_widget.pack(padx=16, pady=(4, 16), anchor="w")

        # Auto-adjust font size to fit width
        self.bind("<Configure>", self._on_resize)
        self._base_font_size = 36

    def _on_resize(self, event):
        card_width = event.width
        if card_width < 250:
            size = 24
        elif card_width < 350:
            size = 28
        elif card_width < 450:
            size = 32
        else:
            size = 36
        if size != self._base_font_size:
            self._base_font_size = size
            self._value_widget.configure(font=(theme.FONT_FAMILY, size, "bold"))

    def update_values(self, value, badge="", value_color=None, badge_color=None):
        """Update displayed values without recreating widgets."""
        self._value_widget.configure(text=value, text_color=value_color or theme.ON_SURFACE)
        if badge:
            self._badge_widget.configure(text=badge, fg_color=theme.SURFACE_HIGH,
                                          text_color=badge_color or theme.PRIMARY)
        else:
            self._badge_widget.configure(text="", fg_color="transparent")
