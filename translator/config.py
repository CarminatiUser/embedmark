"""Configurações explícitas do projeto e da área de exibição."""

from translator.fonts import FontCatalog

# LVGL 8.3 reserva bits para porcentagens e LV_SIZE_CONTENT. Este limite
# permanece válido também quando o firmware habilita LV_USE_LARGE_COORD.
LVGL_COORD_MAX = 8191


def dimension(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= LVGL_COORD_MAX:
        raise ValueError(f"{name} deve ser um inteiro entre 1 e {LVGL_COORD_MAX}.")
    return value


class DisplayPresets:
    # Estes presets especificam dimensões, não configuram drivers.
    DISPLAYS = {
        "st7789": (172, 320, "ST7789 de referência (172 × 320)"),
        "st7735": (128, 160, "ST7735 (128 × 160; não validado em hardware)"),
        "ili9341": (240, 320, "ILI9341 (240 × 320; não validado em hardware)"),
        "ssd1306": (128, 64, "SSD1306 (128 × 64; não validado em hardware)"),
        "custom": (240, 430, "Dimensões personalizadas"),
    }

    @classmethod
    def get_display(cls, name, orientation="portrait"):
        if not isinstance(name, str) or name not in cls.DISPLAYS:
            raise ValueError(f"Preset desconhecido: {name}.")
        if not isinstance(orientation, str) or orientation not in {"portrait", "landscape"}:
            raise ValueError("Orientação deve ser portrait ou landscape.")
        w, h = cls.DISPLAYS[name][:2]
        return (h, w) if orientation == "landscape" else (w, h)

    @classmethod
    def list_displays(cls):
        return {k: v[2] for k, v in cls.DISPLAYS.items()}


class TranslationConfig:
    def __init__(
        self,
        design_width=None,
        design_height=None,
        display_preset="st7789",
        orientation="portrait",
        verbose=True,
        enable_debug_output=False,
        output_format="c",
        display_width=None,
        display_height=None,
        strict=False,
        font_catalog=None,
    ):
        self.design_width = None if design_width is None else dimension(design_width, "Largura do projeto")
        self.design_height = None if design_height is None else dimension(design_height, "Altura do projeto")
        self.display_preset = display_preset
        self.orientation = orientation
        for name, value in (("verbose", verbose), ("enable_debug_output", enable_debug_output), ("strict", strict)):
            if type(value) is not bool:
                raise ValueError(f"{name} deve ser um booleano.")
        self.verbose = verbose
        self.enable_debug_output = enable_debug_output
        self.output_format = output_format
        self.strict = strict
        if font_catalog is not None and not isinstance(font_catalog, FontCatalog):
            raise ValueError("font_catalog deve ser um FontCatalog.")
        self.font_catalog = font_catalog or FontCatalog.builtin()
        if not isinstance(output_format, str) or output_format not in {"c", "json"}:
            raise ValueError("Formato de saída deve ser c ou json.")
        w, h = DisplayPresets.get_display(display_preset, orientation)
        if display_preset == "custom":
            if display_width is None or display_height is None:
                raise ValueError("Display custom exige display_width e display_height.")
            w = dimension(display_width, "Largura do display")
            h = dimension(display_height, "Altura do display")
            if orientation == "landscape":
                w, h = h, w
        elif display_width is not None or display_height is not None:
            raise ValueError("Dimensões de display exigem o preset custom.")
        self.display_width, self.display_height = w, h

    def to_dict(self):
        w, h = self.display_width, self.display_height
        if self.orientation == "landscape":
            w, h = h, w
        return {
            "design": {"width": self.design_width, "height": self.design_height},
            "display": {"preset": self.display_preset, "width": w, "height": h, "orientation": self.orientation},
            "generation": {
                "verbose": self.verbose,
                "debug_output": self.enable_debug_output,
                "format": self.output_format,
                "strict": self.strict,
                "font_catalog": self.font_catalog.to_dict(),
            },
        }

    @classmethod
    def from_dict(cls, data):
        design, display, generation = (data.get(k, {}) for k in ("design", "display", "generation"))
        custom = display.get("preset") == "custom"
        return cls(
            design_width=design.get("width"),
            design_height=design.get("height"),
            display_preset=display.get("preset", "st7789"),
            orientation=display.get("orientation", "portrait"),
            display_width=display.get("width") if custom else None,
            display_height=display.get("height") if custom else None,
            verbose=generation.get("verbose", True),
            enable_debug_output=generation.get("debug_output", False),
            output_format=generation.get("format", "c"),
            strict=generation.get("strict", False),
            font_catalog=FontCatalog(generation["font_catalog"])
            if generation.get("font_catalog") is not None
            else None,
        )
