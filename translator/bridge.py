"""Protocolo JSON 1 por stdin/stdout para a extensão, sem gravação de arquivos."""

import json
import sys

from translator import __version__
from translator.config import TranslationConfig
from translator.diagnostics import Diagnostic, TranslationError
from translator.fonts import FontCatalog
from translator.main import UITranslator

PROTOCOL = 1
MAX_REQUEST_BYTES = 8 * 1024 * 1024
CONFIG_KEYS = {
    "display_preset",
    "orientation",
    "design_width",
    "design_height",
    "display_width",
    "display_height",
    "strict",
    "font_manifest",
}


def failure(code, message, diagnostics=None):
    return {
        "protocol": PROTOCOL,
        "ok": False,
        "version": __version__,
        "diagnostics": [
            d.to_dict()
            for d in (diagnostics if diagnostics is not None else [Diagnostic("error", code, message, 1, 1)])
        ],
    }


def process_request(request):
    """Uma requisição isolada; validação usa exatamente o mesmo pipeline da geração."""
    try:
        if not isinstance(request, dict):
            raise ValueError("A requisição deve ser um objeto JSON.")
        unknown = set(request) - {"protocol", "action", "source", "config"}
        if unknown:
            raise ValueError("Campos de requisição desconhecidos: " + ", ".join(sorted(unknown)) + ".")
        if type(request.get("protocol")) is not int or request["protocol"] != PROTOCOL:
            raise ValueError("Versão de protocolo incompatível; use protocol: 1.")
        action = request.get("action")
        if not isinstance(action, str) or action not in {"validate", "generate"}:
            raise ValueError("action deve ser validate ou generate.")
        source = request.get("source")
        if not isinstance(source, str):
            raise ValueError("source deve ser uma string com o conteúdo HTML.")
        options = request.get("config", {})
        if not isinstance(options, dict):
            raise ValueError("config deve ser um objeto JSON.")
        unknown = set(options) - CONFIG_KEYS
        if unknown:
            raise ValueError("Configurações desconhecidas: " + ", ".join(sorted(unknown)) + ".")
        options = dict(options)
        for key in ("display_preset", "orientation"):
            if key in options and not isinstance(options[key], str):
                raise ValueError(f"{key} deve ser uma string.")
        if "strict" in options and type(options["strict"]) is not bool:
            raise ValueError("strict deve ser um booleano.")
        manifest = options.pop("font_manifest", None)
        if manifest is not None and (not isinstance(manifest, str) or not manifest.strip()):
            raise ValueError("font_manifest deve ser um caminho de arquivo JSON não vazio.")
        options.setdefault("strict", True)
        config = TranslationConfig(
            **options,
            verbose=False,
            font_catalog=FontCatalog.load(manifest) if manifest is not None else None,
        )
    except (OSError, ValueError) as exc:
        return failure("bridge.request", str(exc))
    try:
        result = UITranslator(config).translate(source)
    except TranslationError as exc:
        return failure("translation.failure", str(exc), exc.diagnostics)
    except (RecursionError, MemoryError):
        return failure("bridge.limit", "A interface excede os limites de complexidade suportados.")
    response = {
        "protocol": PROTOCOL,
        "ok": True,
        "version": __version__,
        "diagnostics": [diagnostic.to_dict() for diagnostic in result.diagnostics],
        "fonts": result.fonts,
        "result": result.to_dict(),
    }
    if action == "generate":
        response.update(code=result.code, header=result.header)
    return response


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Campo JSON duplicado: {key}.")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Constante JSON inválida: {value}.")


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            response = failure("bridge.limit", "A requisição excede o limite de 8 MiB.")
        else:
            request = json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
            response = process_request(request)
    except (UnicodeError, ValueError) as exc:
        response = failure("bridge.json", f"Requisição JSON inválida: {exc}")
    except (RecursionError, MemoryError):
        response = failure("bridge.limit", "A requisição excede os limites de complexidade suportados.")
    # Protocolo nunca mistura mensagens de progresso ou código C com o JSON.
    sys.stdout.write(json.dumps(response, ensure_ascii=True, allow_nan=False) + "\n")
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
