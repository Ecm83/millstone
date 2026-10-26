"""Generador tipo Timm: el vocabulario es composición de slots finitos.

Si las palabras se generan combinando piezas de un inventario pequeño, un
modelo de bigramas entrenado en una mitad del corpus *acepta* casi todas las
palabras held-out — estructura de plantilla. En una lengua natural el
vocabulario es abierto y la cobertura cae.

Control por diferencia de Mill: el mismo corpus con símbolos barajados
dentro de cada palabra (mismo alfabeto, mismas longitudes, combinatoria
destruida) — la cobertura debe desplomarse si la señal es real.
"""

from __future__ import annotations

import random

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus

_START, _END = "^", "$"


def _bigrams(word: tuple[str, ...]):
    prev = _START
    for ch in word:
        yield (prev, ch)
        prev = ch
    yield (prev, _END)


def _vocabulary(words) -> set[tuple[str, str]]:
    return {bg for w in words for bg in _bigrams(w)}


def _coverage(vocab: set[tuple[str, str]], words) -> float:
    if not words:
        return 0.0
    ok = sum(1 for w in words if all(bg in vocab for bg in _bigrams(w)))
    return ok / len(words)


class TimmSlots:
    name = "timm-slots"
    statement = (
        "El vocabulario se genera por composición de slots: bigramas "
        "inducidos en train aceptan casi todo held-out, y mucho más que "
        "sobre el corpus barajado."
    )

    def __init__(self, every_kth: int = 5, seed: int = 0):
        self.every_kth = every_kth
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        words = [s.symbols for s in view.sequences("word") if s.symbols]
        if len(words) < 200:
            return [Evidence("corpus suficiente", None, f"{len(words)} palabras")]

        # split determinista: cada k-ésima palabra va a test
        test = [w for i, w in enumerate(words) if i % self.every_kth == 0]
        train = [w for i, w in enumerate(words) if i % self.every_kth != 0]
        vocab = _vocabulary(train)
        cov_real = _coverage(vocab, test)

        # nulo: barajar símbolos dentro de cada palabra de test
        rng = random.Random(self.seed)
        shuffled = [tuple(rng.sample(w, len(w))) for w in test]
        cov_null = _coverage(vocab, shuffled)

        margin = cov_real - cov_null
        err_reduction = (
            (1 - cov_null) / (1 - cov_real) if cov_real < 1 else float("inf")
        )
        return [
            Evidence(
                "cobertura held-out alta (estructura de plantilla)",
                cov_real > 0.5,
                f"{cov_real:.1%} de {len(test)} palabras held-out aceptadas "
                f"({len(vocab)} bigramas de {len(train)} train)",
            ),
            Evidence(
                "la cobertura supera al corpus barajado (Mill: diferencia)",
                cov_real > 0.5 and margin > 0.2,
                f"real={cov_real:.1%} vs barajado={cov_null:.1%} "
                f"(error x{err_reduction:.0f} menor)",
            ),
        ]
