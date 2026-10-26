"""Combinatoria productiva: la gramática genera palabras nunca vistas.

Si el vocabulario fuera una lista memorizada, muestrear la gramática
inducida solo reproduciría palabras del corpus. Si genera proporción alta
de formas inéditas pero válidas, la estructura es *generativa* — el
argumento fuerte de Timm/Schinner.
"""

from __future__ import annotations

import random
from collections import Counter

from millstone.engine.induce import induce
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class ProductiveGrammar:
    name = "productive-grammar"
    statement = (
        "La gramática inducida es productiva: genera muchas palabras "
        "válidas no atestiguadas en el corpus."
    )

    def __init__(self, n_samples: int = 5000, seed: int = 0):
        self.n_samples = n_samples
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        words = [
            s.symbols for s in view.sequences("word") if s.symbols
        ]
        if len(words) < 200:
            return [Evidence("corpus suficiente", None, f"{len(words)} palabras")]

        vocab = set(words)
        freq = Counter(words)
        g = induce(view, "word")
        rng = random.Random(self.seed)
        gen = [g.sample_word(rng) for _ in range(self.n_samples)]
        unseen = [w for w in gen if tuple(w) not in vocab]

        # ¿las palabras generadas-vistas son las frecuentes? (sanidad)
        gen_freq = sum(freq.get(tuple(w), 0) for w in gen) / len(gen)

        return [
            Evidence(
                "la gramática genera formas inéditas (productiva)",
                len(unseen) / len(gen) > 0.2,
                f"{len(unseen)}/{len(gen)} generadas no atestiguadas "
                f"({len(unseen)/len(gen):.0%}); vocab observado: {len(vocab)}",
            ),
            Evidence(
                "las formas generadas-vistas son las frecuentes del corpus",
                gen_freq > 1.0,
                f"ocurrencias medias por palabra generada: {gen_freq:.1f} "
                f"(media corpus: {sum(freq.values())/len(freq):.2f})",
            ),
        ]
