"""Diagnósticos compartilhados pela biblioteca, CLI e futura extensão."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    line: int | None = None
    column: int | None = None
    element_id: str | None = None

    def to_dict(self):
        return asdict(self)


class TranslationError(ValueError):
    def __init__(self, diagnostics):
        self.diagnostics = list(diagnostics)
        super().__init__("; ".join(d.message for d in self.diagnostics if d.severity == "error"))


def raise_errors(diagnostics):
    if any(d.severity == "error" for d in diagnostics):
        raise TranslationError(diagnostics)
