"""Compatibilidade para utilitários antigos de hierarquia.

O pipeline público usa LayoutEngine e não aplica fluxo CSS ou Flexbox.
Helpers antigos que inventavam dimensões foram retirados explicitamente.
"""

from translator.html_parser import HTMLParser


class ContainerManager:
    @staticmethod
    def validate_hierarchy(element):
        """Confere os mesmos tipos de componentes aceitos pelo pipeline."""
        if not isinstance(element, dict) or element.get("type") not in HTMLParser.SUPPORTED_ELEMENTS:
            return False
        children = element.get("children", [])
        if not isinstance(children, list) or (element["type"] == "label" and children):
            return False
        return all(
            isinstance(child, dict) and child.get("type") != "screen" and ContainerManager.validate_hierarchy(child)
            for child in children
        )

    @staticmethod
    def flatten_with_parents(elements):
        """Mantém a ordem de criação e os IDs públicos dos pais, quando existem."""
        flat = []

        def traverse(element, parent_id=None):
            flat.append({**element, "computed_parent_id": parent_id})
            for child in element.get("children", []):
                traverse(child, element.get("id"))

        for element in elements:
            traverse(element)
        return flat

    @staticmethod
    def calculate_container_bounds(element, computed_elements):
        raise ValueError(
            "Auto-sizing não está implementado. Use computed_layout para dimensões explícitas; "
            "dimensões automáticas de texto precisam ser medidas pelo LVGL."
        )


class SimplexFlexbox:
    """Nome legado preservado apenas para informar a retirada do protótipo."""

    DIRECTIONS = ("row", "column")
    JUSTIFY_OPTS = ("flex-start", "center", "flex-end", "space-between")
    ALIGN_OPTS = ("flex-start", "center", "flex-end", "stretch")

    @staticmethod
    def apply_flexbox(container, direction="column", justify_content="flex-start", align_items="flex-start", gap=0):
        raise ValueError(
            "Flexbox não está implementado no tradutor. Use posições absolutas com left/top, "
            "width/height e padding; o protótipo antigo foi retirado por produzir layouts incorretos."
        )
