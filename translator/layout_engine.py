"""Layout absoluto relativo ao conteúdo do pai, com escala por eixo."""

import math

from translator.config import LVGL_COORD_MAX, dimension
from translator.css_parser import CSSParser
from translator.fonts import FontCatalog
from translator.fonts import FontMapper as FontMapper


def coordinate(value):
    if not math.isfinite(value) or abs(value) > LVGL_COORD_MAX:
        raise ValueError(f"Coordenada calculada excede o intervalo suportado (±{LVGL_COORD_MAX}).")
    return int(value)


class ViewportConfig:
    def __init__(self, design_width=172, design_height=320, display_width=172, display_height=320):
        self.design_width = dimension(design_width, "Largura do projeto")
        self.design_height = dimension(design_height, "Altura do projeto")
        self.display_width = dimension(display_width, "Largura do display")
        self.display_height = dimension(display_height, "Altura do display")
        self.scale_x = display_width / design_width
        self.scale_y = display_height / design_height

    def scale_position(self, x, y):
        return coordinate(x * self.scale_x), coordinate(y * self.scale_y)

    def scale_size(self, width, height):
        return self.scale_position(width, height)

    def scale_value(self, value, is_horizontal=False):
        return coordinate(value * (self.scale_x if is_horizontal else self.scale_y))


class LayoutEngine:
    def __init__(self, viewport, font_catalog=None):
        self.viewport = viewport
        self.font_catalog = font_catalog or FontCatalog.builtin()

    def compute_layout(self, element, styles, inherited=None):
        try:
            return self._compute_layout(element, styles, inherited)
        except ValueError as exc:
            if not hasattr(exc, "line"):
                exc.line = element.get("line", 1)
                exc.column = element.get("column", 1)
                exc.element_id = element.get("id")
            raise

    def _compute_layout(self, element, styles, inherited=None):
        own = styles.get(element.get("id"), {})
        inherited = inherited or {"font-size": 14, "color": "#FFFFFF", "text-align": "left"}
        typography = {key: own.get(key, value) for key, value in inherited.items()}

        def number(key, default=0):
            return CSSParser.get_numeric_value(own.get(key, default))

        left, top = self.viewport.scale_position(
            number("left") + number("margin-left"), number("top") + number("margin-top")
        )
        font_size = typography["font-size"] * max(self.viewport.scale_x, self.viewport.scale_y)
        computed = {
            "left": left,
            "top": top,
            "position_explicit": any(k in own for k in ("left", "top", "margin-left", "margin-top")),
            "width": self.viewport.scale_value(number("width"), True) if "width" in own else None,
            "height": self.viewport.scale_value(number("height")) if "height" in own else None,
            "font_size": font_size,
            "font": self.font_catalog.select(font_size)["symbol"],
            "color": typography["color"],
            "text_align": typography["text-align"],
            "bg_color": own.get("background-color"),
            "opacity": number("opacity", 1),
            "border_color": own.get("border-color", "#000000"),
            "border_width": self.viewport.scale_value(number("border-width")),
            "border_radius": self.viewport.scale_value(number("border-radius")),
            "hidden": own.get("display") == "none",
        }
        for side in ("left", "right", "top", "bottom"):
            computed[f"padding_{side}"] = self.viewport.scale_value(
                number(f"padding-{side}"), side in {"left", "right"}
            )
        return {
            **element,
            "computed": computed,
            "children": [self.compute_layout(child, styles, typography) for child in element.get("children", [])],
        }

    def compute_all_layouts(self, elements, styles):
        return [self.compute_layout(element, styles) for element in elements]
