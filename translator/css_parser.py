"""Parser do subconjunto CSS; regras inválidas nunca viram defaults silenciosos."""

import math
import re

import tinycss2

from translator.color_utils import ColorConverter
from translator.config import LVGL_COORD_MAX
from translator.diagnostics import Diagnostic, raise_errors


class CSSParser:
    LENGTH_PROPERTIES = {
        "left",
        "top",
        "width",
        "height",
        "font-size",
        "border-radius",
        "border-width",
        *{f"{kind}-{side}" for kind in ("margin", "padding") for side in ("left", "right", "top", "bottom")},
    }
    SUPPORTED_PROPERTIES = LENGTH_PROPERTIES | {
        "padding",
        "margin",
        "color",
        "background-color",
        "background",
        "border-color",
        "border",
        "text-align",
        "opacity",
        "display",
    }
    # Posição absoluta com deslocamento à esquerda/acima; não há fluxo CSS.
    UNSUPPORTED_MARGINS = {"margin-right", "margin-bottom"}
    NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?(?:px)?", re.I)

    @staticmethod
    def parse_value(value_str):
        value = str(value_str).strip()
        if CSSParser.NUMBER.fullmatch(value):
            result = float(re.sub(r"px$", "", value, flags=re.I))
            if not math.isfinite(result):
                raise ValueError("O valor deve ser finito.")
            return int(result) if result.is_integer() else result
        return value

    @classmethod
    def _length(cls, value, prop):
        result = cls.parse_value(value)
        if not isinstance(result, (float, int)):
            raise ValueError(f"{prop}: use um número ou um valor em px.")
        if prop not in {"left", "top"} and not prop.startswith("margin-") and result < 0:
            raise ValueError(f"{prop}: o valor não pode ser negativo.")
        if prop == "font-size" and result <= 0:
            raise ValueError("font-size deve ser maior que zero.")
        if abs(result) > LVGL_COORD_MAX:
            raise ValueError(f"{prop}: valor fora do intervalo suportado (±{LVGL_COORD_MAX}).")
        return result

    @classmethod
    def _spacing(cls, value, prefix):
        values = value.strip().split()
        if len(values) not in (1, 2, 3, 4):
            raise ValueError(f"{prefix}: informe de um a quatro valores.")
        if len(values) == 1:
            values *= 4
        elif len(values) == 2:
            values *= 2
        elif len(values) == 3:
            values.append(values[1])
        return {
            f"{prefix}-{side}": cls._length(v, f"{prefix}-{side}")
            for side, v in zip(("top", "right", "bottom", "left"), values)
        }

    @classmethod
    def parse_shorthand_padding(cls, value):
        return cls._spacing(value, "padding")

    @classmethod
    def parse_shorthand_margin(cls, value):
        return cls._spacing(value, "margin")

    @classmethod
    def _declaration(cls, prop, value):
        if prop in ("padding", "margin"):
            return cls._spacing(value, prop)
        if prop in cls.LENGTH_PROPERTIES:
            return {prop: cls._length(value, prop)}
        if prop in {"color", "background-color", "background", "border-color"}:
            return {"background-color" if prop == "background" else prop: ColorConverter.normalize(value)}
        if prop == "opacity":
            if not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", value):
                raise ValueError("opacity deve ser um número entre 0 e 1.")
            number = float(value)
            if not 0 <= number <= 1:
                raise ValueError("opacity deve estar entre 0 e 1.")
            return {prop: number}
        if prop == "text-align":
            if value not in {"left", "center", "right"}:
                raise ValueError("text-align aceita left, center ou right.")
        if prop == "display" and value not in {"block", "none"}:
            raise ValueError("display aceita block ou none; Flexbox não está integrado.")
        if prop == "border":
            match = re.fullmatch(r"(\S+)\s+solid\s+(.+)", value)
            if not match:
                raise ValueError("border aceita apenas: <largura> solid <cor>.")
            return {
                "border-width": cls._length(match[1], "border-width"),
                "border-color": ColorConverter.normalize(match[2]),
            }
        return {prop: value}

    @classmethod
    def parse_stylesheet(cls, css_text, diagnostics=None, *, locations=None):
        diagnostics = [] if diagnostics is None else diagnostics
        locations = {} if locations is None else locations
        property_locations = {}
        styles, priorities = {}, {}
        rules = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
        for rule in rules:
            line, column = rule.source_line, rule.source_column
            if rule.type != "qualified-rule":
                diagnostics.append(
                    Diagnostic(
                        "error" if rule.type == "error" else "warning",
                        "css.rule",
                        getattr(rule, "message", "Regra CSS não suportada."),
                        line,
                        column,
                    )
                )
                continue
            tokens = [t for t in rule.prelude if t.type not in ("whitespace", "comment")]
            if len(tokens) != 1 or tokens[0].type != "hash" or not tokens[0].is_identifier:
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "css.selector",
                        "Somente seletores simples por ID (#identificador) são suportados.",
                        line,
                        column,
                    )
                )
                continue
            element_id = tokens[0].value
            locations[element_id] = (line, column)
            target = styles.setdefault(element_id, {})
            for decl in tinycss2.parse_declaration_list(rule.content, skip_comments=True, skip_whitespace=True):
                if decl.type != "declaration":
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "css.syntax",
                            getattr(decl, "message", "Declaração CSS inválida."),
                            decl.source_line,
                            decl.source_column,
                            element_id,
                        )
                    )
                    continue
                prop = decl.lower_name
                value = tinycss2.serialize(decl.value).strip()
                if prop not in cls.SUPPORTED_PROPERTIES:
                    diagnostics.append(
                        Diagnostic(
                            "warning",
                            "css.unsupported",
                            f"Propriedade não suportada: {prop}.",
                            decl.source_line,
                            decl.source_column,
                            element_id,
                        )
                    )
                    continue
                try:
                    expanded = cls._declaration(prop, value)
                except ValueError as exc:
                    diagnostics.append(
                        Diagnostic("error", "css.value", str(exc), decl.source_line, decl.source_column, element_id)
                    )
                    continue
                for key, parsed in expanded.items():
                    priority_key = (element_id, key)
                    if priorities.get(priority_key, False) and not decl.important:
                        continue
                    target[key] = parsed
                    property_locations[priority_key] = (decl.source_line, decl.source_column)
                    priorities[priority_key] = decl.important
        for element_id, props in styles.items():
            for prop in cls.UNSUPPORTED_MARGINS:
                if props.get(prop, 0) != 0:
                    diagnostics.append(
                        Diagnostic(
                            "warning",
                            "css.margin",
                            f"{prop} não altera o layout absoluto desta versão.",
                            *property_locations[(element_id, prop)],
                            element_id=element_id,
                        )
                    )
        raise_errors(diagnostics)
        return styles

    @staticmethod
    def get_numeric_value(value, default=0):
        result = CSSParser.parse_value(value)
        if isinstance(result, (int, float)) and math.isfinite(result):
            return float(result)
        raise ValueError(f"Valor numérico inválido: {value!r}.")
