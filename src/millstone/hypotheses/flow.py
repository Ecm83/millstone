"""¿El texto fluye a través del salto de línea, o cada línea es una celda?

Si el corpus es prosa continua, el par (última palabra de línea, primera
de la siguiente) debería comportarse como un bigrama de palabras
cualquiera — pares atestiguados dentro de línea. Si son entradas de una
cuadrícula/tabla, los pares cross-line son combinaciones al azar.

Nulo: mismos pares pero emparejando final de línea i con inicio de línea
i+1 barajadas — conserva las distribuciones marginales, destruye la
adyacencia real.
"""

from __future__ import annotations

import random
from collections import Counter

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class FlowAcrossLines:
    name = "flow-across-lines"
    statement = (
        "El texto fluye entre líneas (prosa continua): los pares "
        "fin-de-línea → inicio-de-línea se comportan como bigramas "
        "de palabra atestiguados, no como combinaciones al azar."
    )

    def __init__(self, seed: int = 0):
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        # líneas consecutivas DENTRO de cada párrafo
        pairs_cross = []
        vocab_pairs = set()
        for par in corpus.nodes("paragraph"):
            line_words = []
            for line in par.children:
                ws = ["".join(s.value for s in w.leaves() if s.value)
                      for w in line.children]
                if ws:
                    line_words.append(ws)
                    vocab_pairs.update(zip(ws, ws[1:]))
            for a, b in zip(line_words, line_words[1:]):
                pairs_cross.append((a[-1], b[0]))
        if len(pairs_cross) < 50:
            return [Evidence("suficientes pares cross-line", None,
                             f"{len(pairs_cross)}")]

        hit = sum(1 for p in pairs_cross if p in vocab_pairs) / len(pairs_cross)
        # nulo: empareja finales con inicios barajados
        ends = [p[0] for p in pairs_cross]
        starts = [p[1] for p in pairs_cross]
        rng = random.Random(self.seed)
        rng.shuffle(starts)
        null = sum(1 for p in zip(ends, starts) if p in vocab_pairs) / len(pairs_cross)
        return [
            Evidence(
                "los pares cross-line son bigramas atestiguados (flujo)",
                hit > 1.5 * null,
                f"{hit:.1%} de {len(pairs_cross)} pares cross-line son "
                f"bigramas internos vs nulo {null:.1%} "
                f"({hit/null if null else 0:.1f}x)",
            )
        ]
