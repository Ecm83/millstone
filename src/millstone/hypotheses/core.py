"""Hipótesis como objetos: predicciones declaradas, evidencia enlazada.

Una hipótesis declara predicciones comprobables; `evaluate` las confronta
con un corpus y devuelve `Evidence` — cada una soportada, refutada o sin
suficiente evidencia, siempre con el detalle de datos detrás.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from millstone.model import Corpus


@dataclass(frozen=True)
class Evidence:
    prediction: str
    supported: bool | None  # None = evidencia insuficiente
    detail: str


class Hypothesis(Protocol):
    name: str
    statement: str

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        ...
