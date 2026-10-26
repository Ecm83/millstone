"""Efecto inicial: la primera palabra de línea/párrafo no es cualquiera.

En la literatura Voynich las palabras iniciales de párrafo se enriquecen en
ciertos símbolos (efecto "gallows"). Predicción comprobable: la distribución
del símbolo inicial en posición de inicio de unidad difiere de la marginal.
"""

from __future__ import annotations

from collections import Counter

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class InitialEffect:
    name = "initial-effect"
    statement = (
        "El símbolo inicial de la primera palabra de línea/párrafo no sigue "
        "la distribución marginal de símbolos iniciales."
    )

    def __init__(self, min_support: int = 30, min_ratio: float = 1.8):
        self.min_support = min_support
        self.min_ratio = min_ratio

    def _enrichment(self, initials: Counter, marginal: Counter):
        total_i = sum(initials.values())
        total_m = sum(marginal.values())
        if not total_i or not total_m:
            return []
        rows = []
        for sym, n in initials.most_common():
            ratio = (n / total_i) / (marginal[sym] / total_m)
            if n >= self.min_support:
                rows.append((sym, n, total_i, ratio, marginal[sym] / total_m))
        return rows

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        marginal = Counter(
            s.symbols[0] for s in view.sequences("word") if s.symbols
        )
        out = []
        for level in ("line", "paragraph"):
            firsts = Counter(
                seq.symbols[0][0]
                for seq in view.unit_sequences(level, "word")
                if seq.symbols and seq.symbols[0]
            )
            rows = self._enrichment(firsts, marginal)
            enriched = [r for r in rows if r[3] >= self.min_ratio]
            top = max(rows, key=lambda r: r[3]) if rows else None
            detail = (
                "; ".join(
                    f"'{s}': {r:.1f}x marginal ({n}/{tot}, base {p:.1%})"
                    for s, n, tot, r, p in sorted(enriched, key=lambda r: -r[3])[:5]
                )
                or "sin símbolos enriquecidos sobre el umbral"
            )
            out.append(
                Evidence(
                    f"símbolo inicial de {level} sesgado",
                    bool(enriched),
                    f"{len(firsts)} unidades | top: "
                    + (f"'{top[0]}' {top[3]:.2f}x" if top else "-")
                    + " | " + detail,
                )
            )
        # bigrama de palabras idénticas: ¿se repiten palabras adyacentes?
        reps = tot = 0
        for seq in view.unit_sequences("line", "word"):
            for a, b in zip(seq.symbols, seq.symbols[1:]):
                tot += 1
                reps += a == b
        if tot:
            out.append(
                Evidence(
                    "existen duplicados adyacentes de palabra",
                    reps > 0,
                    f"{reps}/{tot} pares adyacentes idénticos ({reps/tot:.2%})",
                )
            )
        return out
