"""
debug.py - Utilitários de debug e visualização de dados
"""

import json
from typing import Dict, List, Any


class DebugLogger:
    """Logger de debug com formatação estruturada."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log simples."""
        if self.verbose:
            print(f"[{level}] {message}")

    def log_viewport(self, design_w: int, design_h: int, display_w: int, display_h: int):
        """Log de viewport."""
        self.log("=== VIEWPORT CONFIGURATION ===")
        self.log(f"Design resolution:  {design_w}x{design_h} px")
        self.log(f"Display resolution: {display_w}x{display_h} px")
        self.log(f"Scale X: {display_w / design_w:.4f}")
        self.log(f"Scale Y: {display_h / design_h:.4f}")
        self.log("")

    def log_elements(self, elements: List[Dict[str, Any]]):
        """Log da árvore de elementos."""
        self.log("=== ELEMENT TREE ===")

        def print_tree(elem, indent=0):
            prefix = "  " * indent + "└─ "
            elem_type = elem.get("type", "unknown")
            elem_id = elem.get("id", "(no id)")
            text = elem.get("text", "")

            if text:
                self.log(f"{prefix}{elem_type} #{elem_id} [{text}]")
            else:
                self.log(f"{prefix}{elem_type} #{elem_id}")

            for child in elem.get("children", []):
                print_tree(child, indent + 1)

        for elem in elements:
            print_tree(elem)
        self.log("")

    def log_styles(self, styles: Dict[str, Dict[str, Any]]):
        """Log de estilos aplicados."""
        self.log("=== APPLIED STYLES ===")
        for elem_id, style_dict in styles.items():
            self.log(f"#{elem_id}:")
            for prop, value in style_dict.items():
                self.log(f"  {prop}: {value}")
        self.log("")

    def log_computed_layout(self, element: Dict[str, Any], indent: int = 0):
        """Log de layout computado (com scaling)."""
        prefix = "  " * indent
        elem_type = element.get("type", "unknown")
        elem_id = element.get("id", "(no id)")
        computed = element.get("computed", {})

        self.log(f"{prefix}{elem_type} #{elem_id}")

        if computed:
            self.log(f"{prefix}  pos: ({computed.get('left')}, {computed.get('top')})")

            if computed.get("width") is not None:
                self.log(f"{prefix}  size: {computed.get('width')}x{computed.get('height')}")

            if computed.get("color"):
                self.log(f"{prefix}  text color: {computed.get('color')}")

            if computed.get("bg_color"):
                self.log(f"{prefix}  bg color: {computed.get('bg_color')}")

            if computed.get("font"):
                self.log(f"{prefix}  font: {computed.get('font')}")

        for child in element.get("children", []):
            self.log_computed_layout(child, indent + 1)

    def log_generated_code_stats(self, code: str, num_elements: int):
        """Log de estatísticas do código gerado."""
        self.log("=== GENERATED CODE STATS ===")
        self.log(f"Total elements: {num_elements}")
        self.log(f"Code lines: {len(code.splitlines())}")
        self.log(f"Includes: {code.count('#include')}")
        self.log(f"Function definitions: {code.count('void ')}")
        self.log("")

    def log_json(self, data: Any, label: str = "DATA"):
        """Log JSON formatado."""
        self.log(f"=== {label} ===")
        if self.verbose:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        self.log("")


class DebugReporter:
    """Gera relatório de debug completo."""

    @staticmethod
    def generate_report(
        html_text: str,
        css_text: str,
        ast: Dict[str, Any],
        styles: Dict[str, Dict[str, Any]],
        computed_layout: List[Dict[str, Any]],
        generated_code: str,
        viewport_config: Any,
    ) -> str:
        """Gera relatório de debug em formato legível."""
        lines = []

        lines.append("=" * 70)
        lines.append("TRANSLATOR DEBUG REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Input
        lines.append("INPUT FILES")
        lines.append("-" * 70)
        lines.append(f"HTML lines: {len(html_text.splitlines())}")
        lines.append(f"CSS rules: {len(styles)}")
        lines.append("")

        # Viewport
        lines.append("VIEWPORT CONFIGURATION")
        lines.append("-" * 70)
        lines.append(f"Design: {ast['width']}x{ast['height']} px")
        lines.append(f"Display: {viewport_config.display_width}x{viewport_config.display_height} px")
        lines.append(f"Scale X: {viewport_config.scale_x:.4f}")
        lines.append(f"Scale Y: {viewport_config.scale_y:.4f}")
        lines.append("")

        # AST
        lines.append("PARSED ELEMENTS")
        lines.append("-" * 70)
        lines.append(f"Root elements: {len(ast['elements'])}")

        def count_all(elems):
            count = len(elems)
            for elem in elems:
                count += count_all(elem.get("children", []))
            return count

        total = count_all(ast["elements"])
        lines.append(f"Total elements: {total}")
        lines.append("")

        # Styles
        lines.append("STYLES")
        lines.append("-" * 70)
        for elem_id, style_dict in styles.items():
            lines.append(f"  #{elem_id}: {len(style_dict)} properties")
        lines.append("")

        # Generated code
        lines.append("CODE GENERATION")
        lines.append("-" * 70)
        lines.append(f"Lines of code: {len(generated_code.splitlines())}")
        lines.append(f"Includes: {generated_code.count('#include')}")
        lines.append(f"Function defs: {generated_code.count('void ')}")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)
