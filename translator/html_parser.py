"""Árvore da linguagem simplificada. IDs públicos são opcionais e únicos."""

from bs4 import BeautifulSoup, NavigableString, Comment

from translator.config import dimension
from translator.diagnostics import Diagnostic, raise_errors


class HTMLElement:
    def __init__(self, element_type, element_id=None, text="", parent_id=None, line=None, column=None):
        self.type, self.id, self.text, self.parent_id = element_type, element_id, text, parent_id
        self.line, self.column = line, column
        self.children = []

    def to_dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "text": self.text,
            "parent_id": self.parent_id,
            "line": self.line,
            "column": self.column,
            "children": [x.to_dict() for x in self.children],
        }


class HTMLParser:
    SUPPORTED_ELEMENTS = {"label", "button", "div", "container", "screen"}

    @staticmethod
    def parse_screen_attributes(screen_tag):
        try:
            return {
                name: dimension(int(screen_tag.get(name, default)), name)
                for name, default in (("width", "240"), ("height", "430"))
            }
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Dimensões de screen inválidas: {exc}") from exc

    @classmethod
    def parse_element_recursive(cls, tag, parent_id=None, diagnostics=None, depth=0):
        diagnostics = [] if diagnostics is None else diagnostics
        if depth >= 128:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "html.nesting",
                    "Use no máximo 128 níveis de componentes.",
                    tag.sourceline,
                    tag.sourcepos + 1,
                )
            )
            return None
        if tag.name not in cls.SUPPORTED_ELEMENTS or tag.name == "screen":
            if tag.name != "style":
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "html.element",
                        f"Elemento <{tag.name}> não suportado; sua subárvore foi ignorada.",
                        tag.sourceline,
                        tag.sourcepos + 1 if tag.sourcepos is not None else None,
                    )
                )
            return None
        element = HTMLElement(
            tag.name, tag.get("id"), parent_id=parent_id, line=tag.sourceline, column=tag.sourcepos + 1
        )
        for attribute in tag.attrs:
            if attribute != "id":
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "html.attribute",
                        f"Atributo não suportado em <{tag.name}>: {attribute}.",
                        tag.sourceline,
                        element.column,
                        element_id=element.id,
                    )
                )
        if tag.name == "label":
            element.text = tag.get_text()
            if tag.find(True):
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "html.label_markup",
                        "Markup dentro de label é convertido em texto simples.",
                        tag.sourceline,
                        element.column,
                        element_id=element.id,
                    )
                )
            return element
        for child in tag.find_all(recursive=False):
            parsed = cls.parse_element_recursive(child, element.id, diagnostics, depth + 1)
            if parsed:
                element.children.append(parsed)
        direct_text = "".join(
            str(x) for x in tag.children if isinstance(x, NavigableString) and not isinstance(x, Comment)
        ).strip()
        if tag.name == "button" and direct_text:
            if element.children:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "html.button_text",
                        "Botão deve usar texto direto ou elementos filhos, sem misturar os dois.",
                        tag.sourceline,
                        element.column,
                        element_id=element.id,
                    )
                )
            else:
                element.children.append(
                    HTMLElement(
                        "label", text=direct_text, parent_id=element.id, line=element.line, column=element.column
                    )
                )
        elif direct_text:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "html.text",
                    "Texto fora de label ou button foi ignorado.",
                    tag.sourceline,
                    element.column,
                    element_id=element.id,
                )
            )
        return element

    @classmethod
    def parse(cls, html_text, diagnostics=None):
        diagnostics = [] if diagnostics is None else diagnostics
        soup = BeautifulSoup(html_text, "html.parser")
        screens = soup.find_all("screen")
        if len(screens) != 1:
            diagnostics.append(Diagnostic("error", "html.screen", "Informe exatamente uma tag <screen>.", 1, 1))
            raise_errors(diagnostics)
        screen = screens[0]
        try:
            attrs = cls.parse_screen_attributes(screen)
        except ValueError as exc:
            diagnostics.append(
                Diagnostic("error", "html.dimensions", str(exc), screen.sourceline, screen.sourcepos + 1)
            )
            raise_errors(diagnostics)
        ids = set()
        for tag in [screen, *screen.find_all(True)]:
            element_id = tag.get("id")
            if element_id is not None:
                if not element_id or any(c.isspace() or ord(c) < 32 for c in element_id):
                    diagnostics.append(
                        Diagnostic(
                            "error", "html.id", "ID vazio ou com espaço/controle.", tag.sourceline, tag.sourcepos + 1
                        )
                    )
                elif element_id in ids:
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "html.duplicate_id",
                            f"ID duplicado: {element_id}.",
                            tag.sourceline,
                            tag.sourcepos + 1,
                            element_id=element_id,
                        )
                    )
                ids.add(element_id)
        for attribute in screen.attrs:
            if attribute not in {"id", "width", "height"}:
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "html.attribute",
                        f"Atributo não suportado em screen: {attribute}.",
                        screen.sourceline,
                        screen.sourcepos + 1,
                    )
                )
        elements = []
        if any(
            str(child).strip()
            for child in screen.children
            if isinstance(child, NavigableString) and not isinstance(child, Comment)
        ):
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "html.text",
                    "Texto direto em screen foi ignorado; use label.",
                    screen.sourceline,
                    screen.sourcepos + 1,
                )
            )
        for tag in screen.find_all(recursive=False):
            element = cls.parse_element_recursive(tag, diagnostics=diagnostics)
            if element:
                elements.append(element.to_dict())
        raise_errors(diagnostics)
        return {**attrs, "id": screen.get("id"), "elements": elements}

    @staticmethod
    def flatten_elements(elements):
        flat = []
        for element in elements:
            data = element.to_dict() if isinstance(element, HTMLElement) else element
            flat.append(data)
            flat.extend(HTMLParser.flatten_elements(data.get("children", [])))
        return flat
