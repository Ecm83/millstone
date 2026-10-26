"""Aplicación de restricciones sobre un CorpusView.

`check()` recorre las secuencias de un nivel y devuelve las violaciones con
su locus — la evidencia enlazada que el grafo de conocimiento registrará.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from millstone.engine.constraints import Constraint
from millstone.engine.view import CorpusView, Sequence


@dataclass(frozen=True)
class Violation:
    locus: str | None
    sequence: tuple[str, ...]


@dataclass
class CheckResult:
    constraint: Constraint
    level: str
    checked: int = 0
    violations: list[Violation] = field(default_factory=list)

    @property
    def holds(self) -> bool:
        """La restricción es exacta sobre el corpus (cero excepciones)."""
        return not self.violations

    @property
    def violation_rate(self) -> float:
        return len(self.violations) / self.checked if self.checked else 0.0


def check(view: CorpusView, level: str, constraint: Constraint) -> CheckResult:
    result = CheckResult(constraint=constraint, level=level)
    for seq in view.sequences(level):
        result.checked += 1
        if not constraint.holds(seq.symbols):
            result.violations.append(Violation(locus=seq.locus, sequence=seq.symbols))
    return result


def alphabet(view: CorpusView) -> frozenset[str]:
    """Símbolos hoja observados en el corpus."""
    return frozenset(
        s for seq in view.sequences(view.levels()[0]) for s in seq.symbols
    )
