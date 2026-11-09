"""Start only the packaged backend, without user site packages or PYTHONPATH."""
import json
from pathlib import Path
import runpy
import sys

if sys.version_info < (3, 10):
    print(json.dumps({"protocol": 1, "ok": False, "version": "0.4.1", "diagnostics": [
        {"severity": "error", "code": "PYTHON_VERSION", "message": "Instale Python 3.10 ou superior."}
    ]}))
    raise SystemExit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent / "python"))
runpy.run_module("translator.bridge", run_name="__main__")
