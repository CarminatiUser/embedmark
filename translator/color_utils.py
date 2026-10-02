"""
color_utils.py - Sistema de conversão de cores para LVGL
"""

import re


class ColorConverter:
    """Converte cores de diferentes formatos para LVGL hex."""

    # Paleta de cores nomeadas CSS
    NAMED_COLORS = {
        # Básicas
        "white": "#FFFFFF",
        "black": "#000000",
        "red": "#FF0000",
        "green": "#008000",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        # Extended
        "gray": "#808080",
        "grey": "#808080",
        "silver": "#C0C0C0",
        "maroon": "#800000",
        "olive": "#808000",
        "lime": "#00FF00",
        "aqua": "#00FFFF",
        "teal": "#008080",
        "navy": "#000080",
        "purple": "#800080",
        "orange": "#FFA500",
        "pink": "#FFC0CB",
        "brown": "#A52A2A",
        "darkgray": "#A9A9A9",
        "lightgray": "#D3D3D3",
        "gold": "#FFD700",
        "coral": "#FF7F50",
        "salmon": "#FA8072",
        "khaki": "#F0E68C",
    }

    @classmethod
    def normalize(cls, color: str) -> str:
        """Aceita nomes da paleta, #RGB, #RRGGBB e rgb(0..255,0..255,0..255)."""
        if not isinstance(color, str):
            raise ValueError("Cor deve ser uma string.")
        color = color.strip().lower()
        if color in cls.NAMED_COLORS:
            return cls.NAMED_COLORS[color]
        if re.fullmatch(r"#[0-9a-f]{3}", color):
            return "#" + "".join(c * 2 for c in color[1:]).upper()
        if re.fullmatch(r"#[0-9a-f]{6}", color):
            return color.upper()
        if color.startswith("rgb"):
            return cls.parse_rgb(color)
        raise ValueError(f"Cor inválida ou não suportada: {color!r}.")

    @classmethod
    def hex_to_lvgl(cls, color):
        if not isinstance(color, str) or not color.startswith("#"):
            raise ValueError("Cor hexadecimal deve começar com #.")
        return "0x" + cls.normalize(color)[1:]

    @staticmethod
    def rgb_to_hex(r, g, b):
        if any(type(v) is not int or not 0 <= v <= 255 for v in (r, g, b)):
            raise ValueError("Componentes RGB devem ser inteiros entre 0 e 255.")
        return f"#{r:02X}{g:02X}{b:02X}"

    @classmethod
    def parse_rgb(cls, color):
        match = re.fullmatch(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color.strip(), re.I)
        if not match:
            raise ValueError("Use rgb(r, g, b), com inteiros entre 0 e 255.")
        return cls.rgb_to_hex(*(int(v) for v in match.groups()))

    @classmethod
    def to_lvgl(cls, color):
        return "0x" + cls.normalize(color)[1:]

    @classmethod
    def blend_opacity(cls, color, opacity):
        if not 0 <= opacity <= 1:
            raise ValueError("Opacidade deve estar entre 0 e 1.")
        return f"{cls.normalize(color)}({int(opacity * 100)}%)"
