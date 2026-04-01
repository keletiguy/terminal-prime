"""Tests for theme module - written BEFORE implementation (TDD)."""
import pytest


class TestThemeColors:
    def test_surface_colors_exist(self):
        from terminal_prime.theme import (
            SURFACE_LOWEST, SURFACE, SURFACE_LOW, SURFACE_CONT,
            SURFACE_HIGH, SURFACE_BRIGHT, SURFACE_HIGHEST,
        )
        assert SURFACE_LOWEST == "#0e0e0e"
        assert SURFACE == "#131313"
        assert SURFACE_LOW == "#1c1b1b"
        assert SURFACE_CONT == "#20201f"
        assert SURFACE_HIGH == "#2a2a2a"
        assert SURFACE_BRIGHT == "#393939"
        assert SURFACE_HIGHEST == "#353535"

    def test_primary_colors(self):
        from terminal_prime.theme import PRIMARY, PRIMARY_CONT
        assert PRIMARY == "#a5c8ff"
        assert PRIMARY_CONT == "#1f538d"

    def test_secondary_colors(self):
        from terminal_prime.theme import SECONDARY, SECONDARY_CONT
        assert SECONDARY == "#b7c7e4"
        assert SECONDARY_CONT == "#3a4a61"

    def test_tertiary_colors(self):
        from terminal_prime.theme import TERTIARY, TERTIARY_CONT
        assert TERTIARY == "#fdbb2e"
        assert TERTIARY_CONT == "#6d4c00"

    def test_error_colors(self):
        from terminal_prime.theme import ERROR, ERROR_CONT
        assert ERROR == "#ffb4ab"
        assert ERROR_CONT == "#93000a"

    def test_text_colors(self):
        from terminal_prime.theme import ON_SURFACE, ON_SURFACE_VAR, ON_PRIMARY, ON_ERROR
        assert ON_SURFACE == "#e5e2e1"
        assert ON_SURFACE_VAR == "#c2c6d1"
        assert ON_PRIMARY == "#00315e"
        assert ON_ERROR == "#690005"

    def test_outline_colors(self):
        from terminal_prime.theme import OUTLINE, OUTLINE_VAR
        assert OUTLINE == "#8c919b"
        assert OUTLINE_VAR == "#424750"


class TestThemeDesign:
    def test_corner_radius(self):
        from terminal_prime.theme import CORNER_RADIUS
        assert CORNER_RADIUS == 10

    def test_font_family(self):
        from terminal_prime.theme import FONT_FAMILY
        assert FONT_FAMILY == "Inter"

    def test_fonts_defined(self):
        from terminal_prime.theme import (
            HEADING, TITLE, BODY, BODY_BOLD, LABEL,
            LABEL_UPPER, SMALL, KPI,
        )
        assert isinstance(HEADING, tuple)
        assert isinstance(KPI, tuple)

    def test_status_colors(self):
        from terminal_prime.theme import STATUS_COLORS
        assert "EN_ATTENTE" in STATUS_COLORS
        assert "PAYEE" in STATUS_COLORS
        assert "PARTIELLE" in STATUS_COLORS
        assert "EN_RETARD" in STATUS_COLORS

    def test_sidebar_width(self):
        from terminal_prime.theme import SIDEBAR_WIDTH
        assert SIDEBAR_WIDTH == 250

    def test_window_dimensions(self):
        from terminal_prime.theme import WINDOW_WIDTH, WINDOW_HEIGHT
        assert isinstance(WINDOW_WIDTH, int)
        assert isinstance(WINDOW_HEIGHT, int)


class TestFormatFcfa:
    def test_format_fcfa(self):
        from terminal_prime.theme import format_fcfa
        assert format_fcfa(5_000_000) == "5 000 000 FCFA"

    def test_format_fcfa_small(self):
        from terminal_prime.theme import format_fcfa
        assert format_fcfa(500) == "500 FCFA"

    def test_format_fcfa_zero(self):
        from terminal_prime.theme import format_fcfa
        assert format_fcfa(0) == "0 FCFA"
