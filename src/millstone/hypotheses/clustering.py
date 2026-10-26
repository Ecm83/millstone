"""¿Hay agrupación temática por línea, o el orden es azar puro?

Si es un catálogo/inventario, las palabras de una línea deberían repetirse
más que bajo barajado global (temas, listas relacionadas). Si el texto es
glosolalia/cifrado posicional, la repetición intra-línea ≈ azar.

Mill: baraja TODAS las palabras del corpus conservando la longitud de cada
línea — destruye la agrupación, conserva el vocabulario y su frecuencia.
"""

from __future__ import annotations

import random
from collections import Counter

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def _repeat_mass(lines: list[tuple[str, ...]]) -> float:
    """Fracción de tokens cuyo tipo aparece >1 vez en su línea."""
    rep = tot = 0
    for ws in lines:
        c = Counter(ws)
        rep += sum(n for n in c.values() if n > 1)
        tot += len(ws)
    return rep / tot if tot else 0.0


class LineClustering:
    name = "line-clustering"
    statement = (
        "Las palabras se agrupan por línea más que bajo azar "
        "(estructura temática/catalográfica); si no, orden libre total."
    )

    def __init__(self, seed: int = 0):
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        lines = [
            tuple(s.symbols) for s in view.unit_sequences("line", "word")
            if s.symbols
        ]
        if len(lines) < 50:
            return [Evidence("líneas suficientes", None, f"{len(lines)}")]

        real = _repeat_mass(lines)
        # nulo: baraja global conservando longitudes de línea
        pool = [w for ws in lines for w in ws]
        rng = random.Random(self.seed)
        rng.shuffle(pool)
        null_lines, i = [], 0
        for ws in lines:
            null_lines.append(tuple(pool[i : i + len(ws)]))
            i += len(ws)
        null = _repeat_mass(null_lines)

        return [
            Evidence(
                "repetición intra-línea supera el barajado global",
                real > 1.3 * null,
                f"masa repetida: real={real:.1%} vs nulo={null:.1%} "
                f"({real/null if null else 0:.1f}x) en {len(lines)} líneas",
            )
        ]
