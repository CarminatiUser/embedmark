"""Catálogos de fontes e cobertura declarada dos glifos."""

import json
from copy import deepcopy
import math
from pathlib import Path
import re


class FontMapper:
    # Cobertura das fontes Montserrat padrão do LVGL 8.3.11 (cmaps).
    CODEPOINTS = (
        frozenset(range(32, 127))
        | frozenset(
            [
                176,
                8226,
                61441,
                61448,
                61451,
                61452,
                61453,
                61457,
                61459,
                61461,
                61465,
                61468,
                61473,
                61478,
                61479,
                61480,
                61502,
                61507,
                61512,
                61515,
                61516,
                61517,
                61521,
                61522,
                61523,
                61524,
                61543,
                61544,
                61550,
                61552,
                61553,
                61556,
                61559,
                61560,
                61561,
                61563,
                61587,
                61589,
                61636,
                61637,
                61639,
                61641,
                61664,
                61671,
                61674,
                61683,
                61724,
                61732,
                61787,
                61931,
                62016,
                62017,
                62018,
                62019,
                62020,
                62087,
                62099,
                62189,
                62212,
                62810,
                63426,
                63650,
            ]
        )
        | {9, 10, 13}
    )
    FONT_MAP = {n: f"lv_font_montserrat_{n}" for n in (8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32, 38, 48)}

    @classmethod
    def get_font(cls, font_size):
        if not math.isfinite(font_size) or font_size <= 0:
            raise ValueError("Tamanho de fonte deve ser positivo e finito.")
        # Empates escolhem a maior fonte, sem truncar a distância antes da comparação.
        size = min(cls.FONT_MAP, key=lambda n: (abs(n - font_size), -n))
        return cls.FONT_MAP[size]


class FontCatalog:
    """Metadados de fontes externas; a aplicação compila os arquivos C declarados."""

    def __init__(self, data):
        try:
            # Metadados extras também atravessam o protocolo JSON da extensão.
            json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("Catálogo de fontes deve conter apenas JSON finito e Unicode válido.") from exc
        if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            raise ValueError("Catálogo de fontes exige schema_version: 1.")
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise ValueError("Catálogo de fontes exige name não vazio.")
        entries = data.get("fonts")
        if not isinstance(entries, list) or not entries:
            raise ValueError("Catálogo de fontes exige uma lista fonts não vazia.")
        sizes, symbols, sources = set(), set(), set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("Cada fonte deve ser um objeto.")
            size, symbol, source = (entry.get(key) for key in ("size", "symbol", "source"))
            if type(size) is not int or not 1 <= size <= 512 or size in sizes:
                raise ValueError("Tamanhos de fonte devem ser inteiros únicos entre 1 e 512.")
            if not isinstance(symbol, str) or not re.fullmatch(r"tcc_font_[A-Za-z0-9_]+", symbol) or symbol in symbols:
                raise ValueError("Símbolos de fontes devem ser únicos e usar o prefixo tcc_font_.")
            if (
                not isinstance(source, str)
                or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\.c", source)
                or source in sources
            ):
                raise ValueError("Cada fonte deve indicar um nome de arquivo C único, sem diretórios.")
            ranges = entry.get("ranges")
            if not isinstance(ranges, list) or not ranges:
                raise ValueError("Cada fonte exige ranges de pontos de código Unicode.")
            for pair in ranges:
                if (
                    not isinstance(pair, list)
                    or len(pair) != 2
                    or any(type(n) is not int for n in pair)
                    or not 0 <= pair[0] <= pair[1] <= 0x10FFFF
                    or (pair[0] <= 0xDFFF and pair[1] >= 0xD800)
                ):
                    raise ValueError("Intervalo Unicode inválido no catálogo de fontes.")
            sizes.add(size)
            symbols.add(symbol)
            sources.add(source)
        self._data = deepcopy(data)
        self._data["fonts"] = sorted(self._data["fonts"], key=lambda item: item["size"])
        self.is_builtin = False

    @classmethod
    def builtin(cls):
        catalog = cls.__new__(cls)
        catalog.is_builtin = True
        catalog._data = {
            "schema_version": 1,
            "name": "Montserrat padrão LVGL 8.3",
            "fonts": [{"size": size, "symbol": symbol} for size, symbol in FontMapper.FONT_MAP.items()],
        }
        return catalog

    @classmethod
    def load(cls, path):
        try:
            return cls(json.loads(Path(path).read_text(encoding="utf-8")))
        except (OSError, ValueError, RecursionError) as exc:
            raise ValueError(f"Não foi possível ler o catálogo de fontes: {exc}") from exc

    def to_dict(self):
        return None if self.is_builtin else deepcopy(self._data)

    def select(self, size):
        if not math.isfinite(size) or size <= 0:
            raise ValueError("Tamanho de fonte deve ser positivo e finito.")
        return deepcopy(min(self._data["fonts"], key=lambda item: (abs(item["size"] - size), -item["size"])))

    def describe(self, symbol):
        for entry in self._data["fonts"]:
            if entry["symbol"] == symbol:
                return deepcopy(entry)
        raise ValueError(f"Fonte não pertence ao catálogo configurado: {symbol}.")

    def missing_characters(self, symbol, text):
        entry = self.describe(symbol)

        def has_glyph(code):
            if code in {0, 9, 10, 13}:
                return True
            if self.is_builtin:
                return code in FontMapper.CODEPOINTS
            return any(low <= code <= high for low, high in entry["ranges"])

        return sorted({char for char in text if not has_glyph(ord(char))})
