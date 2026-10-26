"""Idioma natural: ¿el corpus se comporta como una lengua?

Predicciones comprobables de "lengua natural":
- cola Zipfiana: muchos tipos de una sola ocurrencia (hapax)
- palabras funcionales: los tipos más frecuentes cubren mucha masa
- longitudes de palabra variadas (sílabas, raíces, morfología libre)

El interés del Voynich es que parte de la evidencia apunta a cada lado.
"""

from __future__ import annotations

from collections import Counter

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class NaturalLanguage:
    name = "natural-language"
    statement = (
        "El corpus tiene estadísticas de lengua natural: cola Zipfiana, "
        "funcionales dominantes, longitudes variadas."
    )

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        words = [s.symbols for s in view.sequences("word") if s.symbols]
        if len(words) < 200:
            return [Evidence("corpus suficiente", None, f"{len(words)}")]

        freq = Counter(words)
        types, toks = len(freq), len(words)
        hapax = sum(1 for c in freq.values() if c == 1) / types
        top10 = sum(n for _, n in freq.most_common(10)) / toks
        lens = [len(w) for w in words]
        mean_len = sum(lens) / len(lens)
        outside = sum(1 for L in lens if abs(L - mean_len) > 1.5) / len(lens)

        return [
            Evidence(
                "cola Zipfiana (hapax >= 40% de tipos)",
                hapax >= 0.40,
                f"hapax={hapax:.1%} ({sum(1 for c in freq.values() if c==1)}"
                f"/{types} tipos)",
            ),
            Evidence(
                "palabras funcionales dominantes (top-10 >= 15% tokens)",
                top10 >= 0.15,
                f"top-10 cubre {top10:.1%} de {toks} tokens",
            ),
            Evidence(
                "longitudes variadas (>=20% fuera de media±1.5)",
                outside >= 0.20,
                f"len media={mean_len:.2f}, fuera de rango={outside:.1%}",
            ),
        ]
