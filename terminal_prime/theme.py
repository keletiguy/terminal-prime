"""Carbon Console design system with switchable dark/light themes."""

# ─── Theme Definitions ──────────────────────────────────────────────────────

THEMES = {
    "dark": {
        "SURFACE_LOWEST": "#0e0e0e",
        "SURFACE": "#131313",
        "SURFACE_LOW": "#1c1b1b",
        "SURFACE_CONT": "#20201f",
        "SURFACE_HIGH": "#2a2a2a",
        "SURFACE_BRIGHT": "#393939",
        "SURFACE_HIGHEST": "#353535",
        "PRIMARY": "#a5c8ff",
        "PRIMARY_CONT": "#1f538d",
        "SECONDARY": "#b7c7e4",
        "SECONDARY_CONT": "#3a4a61",
        "TERTIARY": "#fdbb2e",
        "TERTIARY_CONT": "#6d4c00",
        "ERROR": "#ffb4ab",
        "ERROR_CONT": "#93000a",
        "ON_SURFACE": "#e5e2e1",
        "ON_SURFACE_VAR": "#c2c6d1",
        "ON_PRIMARY": "#00315e",
        "ON_ERROR": "#690005",
        "OUTLINE": "#8c919b",
        "OUTLINE_VAR": "#424750",
        "STATUS_COLORS": {
            "EN_ATTENTE": ("#3a4a61", "#b7c7e4"),
            "PAYEE": ("#1b5e20", "#66bb6a"),
            "PARTIELLE": ("#6d4c00", "#fdbb2e"),
            "EN_RETARD": ("#93000a", "#ffb4ab"),
        },
    },
    "light": {
        "SURFACE_LOWEST": "#ffffff",
        "SURFACE": "#f5f7f5",
        "SURFACE_LOW": "#e8ece8",
        "SURFACE_CONT": "#f0f4f0",
        "SURFACE_HIGH": "#dce5dc",
        "SURFACE_BRIGHT": "#d0dbd0",
        "SURFACE_HIGHEST": "#c5d2c5",
        "PRIMARY": "#2e7d32",
        "PRIMARY_CONT": "#388e3c",
        "SECONDARY": "#558b2f",
        "SECONDARY_CONT": "#c8e6c9",
        "TERTIARY": "#e65100",
        "TERTIARY_CONT": "#fff3e0",
        "ERROR": "#c62828",
        "ERROR_CONT": "#ffebee",
        "ON_SURFACE": "#1b1b1b",
        "ON_SURFACE_VAR": "#4a4a4a",
        "ON_PRIMARY": "#ffffff",
        "ON_ERROR": "#ffffff",
        "OUTLINE": "#9e9e9e",
        "OUTLINE_VAR": "#bdbdbd",
        "STATUS_COLORS": {
            "EN_ATTENTE": ("#e0e0e0", "#616161"),
            "PAYEE": ("#c8e6c9", "#2e7d32"),
            "PARTIELLE": ("#fff3e0", "#e65100"),
            "EN_RETARD": ("#ffebee", "#c62828"),
        },
    },
}

# ─── Active Theme State ─────────────────────────────────────────────────────

_current_theme = "dark"
_listeners = []


def get_current_theme():
    return _current_theme


def set_theme(name):
    global _current_theme
    if name not in THEMES:
        return
    _current_theme = name
    _apply_theme()
    for callback in _listeners:
        callback(name)


def on_theme_change(callback):
    _listeners.append(callback)


def _apply_theme():
    t = THEMES[_current_theme]
    g = globals()
    for key, value in t.items():
        g[key] = value


# ─── Initialize with dark theme ─────────────────────────────────────────────
_apply_theme()

# ─── Design constants (theme-independent) ───────────────────────────────────
CORNER_RADIUS = 10
FONT_FAMILY = "Inter"

HEADING = (FONT_FAMILY, 32, "bold")
TITLE = (FONT_FAMILY, 20, "bold")
BODY = (FONT_FAMILY, 14)
BODY_BOLD = (FONT_FAMILY, 14, "bold")
LABEL = (FONT_FAMILY, 12)
LABEL_UPPER = (FONT_FAMILY, 10, "bold")
SMALL = (FONT_FAMILY, 11)
KPI = (FONT_FAMILY, 48, "bold")

FONT_HEADING = HEADING
FONT_TITLE = TITLE
FONT_BODY = BODY
FONT_BODY_BOLD = BODY_BOLD
FONT_LABEL = LABEL
FONT_LABEL_UPPER = LABEL_UPPER
FONT_SMALL = SMALL
FONT_KPI = KPI

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 600
SIDEBAR_WIDTH = 250


def format_fcfa(amount: int) -> str:
    """Format an integer amount as FCFA currency string."""
    return f"{amount:,.0f} FCFA".replace(",", " ")
