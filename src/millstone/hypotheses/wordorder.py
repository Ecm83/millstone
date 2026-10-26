"""Orden de palabras libre (codebook/cifrado) vs. sintaxis.

Si las palabras fueran entradas de inventario, cualquiera puede seguir a
cualquiera: el out-degree de tipos frecuentes es ~el del corpus barajado.
Si hay sintaxis entre palabras, el orden real es mucho más restrictivo.
Mill por diferencia: barajar palabras dentro de línea conserva tipos y
frecuencias pero destruye el orden — el nulo perfecto.
"""

from __future__ import annotations

import random
from collections import Counter
from statistics import mean

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def _out_degrees(lines, top_n: int = 50) -> dict[str, int]:
    pairs = Counter()
    freq = Counter()
    for ws in lines:
        freq.update(ws)
        pairs.update(zip(ws, ws[1:]))
    succ: dict[str, set] = {}
    for a, b in pairs:
        succ.setdefault(a, set()).add(b)
    top = [w for w, _ in freq.most_common(top_n)]
    return {w: len(succ.get(w, ())) for w in top}


class FreeWordOrder:
    name = "free-word-order"
    statement = (
        "El orden de palabras es libre (codebook): el out-degree de tipos "
        "frecuentes es igual al del corpus con líneas barajadas."
    )

    def __init__(self, top_n: int = 50, seed: int = 0):
        self.top_n = top_n
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        lines = [
            tuple(s.symbols) for s in view.unit_sequences("line", "word")
        ]
        if not lines:
            return [Evidence("líneas", None, "sin datos")]

        real = _out_degrees(lines, self.top_n)
        rng = random.Random(self.seed)
        shuffled = [tuple(rng.sample(ws, len(ws))) for ws in lines]
        null = _out_degrees(shuffled, self.top_n)

        # razón real/barajado por tipo; ~1 = orden libre
        ratios = [
            real[w] / null[w] for w in real if null.get(w)
        ]
        r = mean(ratios) if ratios else 0.0
        return [
            Evidence(
                "out-degree real ~= barajado (orden libre)",
                0.7 < r < 1.4,
                f"media real/barajado={r:.2f} | "
                f"ej. daiin real={real.get('daiin')} barajado={null.get('daiin')} "
                f"| top={self.top_n} tipos",
            )
        ]
