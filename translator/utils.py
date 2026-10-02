"""Validação auxiliar, contagens reais e exportação de resultados."""

import json
from pathlib import Path
import re

from translator.css_parser import CSSParser
from translator.html_parser import HTMLParser
from translator.main import UITranslator, atomic_write
from translator.config import TranslationConfig


class HTMLValidator:
    VALID_TAGS = HTMLParser.SUPPORTED_ELEMENTS
    VALID_ATTRIBUTES = {"id", "width", "height"}

    @classmethod
    def validate_structure(cls, elements):
        return all(e.get("type") in cls.VALID_TAGS for e in HTMLParser.flatten_elements(elements))


class CSSValidator:
    VALID_PROPERTIES = CSSParser.SUPPORTED_PROPERTIES

    @classmethod
    def validate_styles(cls, styles):
        return [
            f"Propriedade não suportada: #{identifier} {prop}"
            for identifier, props in styles.items()
            for prop in props
            if prop not in cls.VALID_PROPERTIES
        ]


class CodeAnalyzer:
    @staticmethod
    def count_styles(code):
        return code.count("static lv_style_t")

    @staticmethod
    def count_objects(code):
        return len(re.findall(r"lv_obj_t\s*\*\w+\s*=\s*lv_\w+_create\(", code))

    @staticmethod
    def estimate_ram_usage(code):
        raise ValueError("RAM e ROM exigem medição do firmware; tamanho do código-fonte não é tamanho do binário.")

    @classmethod
    def print_analysis(cls, code):
        print(f"Objetos: {cls.count_objects(code)}")
        print(f"Estilos: {cls.count_styles(code)}")
        print(f"Linhas: {len(code.splitlines())}")
        print(f"Texto C: {len(code.encode('utf-8'))} bytes; não representa memória do firmware.")


class ExportUtils:
    @staticmethod
    def export_json(html_ast, styles, computed, filepath):
        data = {
            "schema_version": 1,
            "design": {k: html_ast[k] for k in ("width", "height")},
            "elements": html_ast["elements"],
            "styles": styles,
            "computed_layout": computed,
        }
        atomic_write(filepath, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    @staticmethod
    def export_c_header(code, filepath, guard_name="UI_GENERATED_H"):
        raise ValueError("Use UITranslator.translate_file para gerar .c e .h separados, sem definições duplicadas.")


class PerformanceMetrics:
    @staticmethod
    def estimate_render_time(num_objects):
        raise ValueError("Tempo de renderização exige medição no dispositivo.")

    @staticmethod
    def check_performance(code):
        raise ValueError("Desempenho exige medição no dispositivo.")


def batch_translate(input_dir, output_dir):
    translator = UITranslator(TranslationConfig(verbose=False))
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results = {"success": 0, "failed": 0, "files": []}
    for source in sorted(Path(input_dir).glob("*.html")):
        destination = output / f"{source.stem}_generated.c"
        ok = translator.translate_file(source, destination)
        results["success" if ok else "failed"] += 1
        results["files"].append({"input": str(source), "output": str(destination), "status": "OK" if ok else "FAILED"})
    return results
