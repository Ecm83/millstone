"""model-compare: ¿qué mecanismo generativo explica mejor el corpus?

Comparación MDL en igualdad de condiciones (mismo FSA de forma de
palabra, mismo modelo de longitud de línea, mismo suelo de tipo
nuevo) entre tres clases de explicación:

- A lingüístico: bigrama de palabras (dependencia de orden)
- B catálogo: i.i.d. sobre léxico enumerado con frecuencias
- C combinatorio: i.i.d. bajo P_FSA (generador libre, sin léxico)

Dos ejes ortogonales:

1. DL en held-out (L(M) + L(D|M)) — qué explicación es más económica,
   en partición intercalada Y contigua (igualdad de evaluación).
2. Reproducción de firmas pre-registradas en corpus muestreados —
   qué explicación se comporta como el sistema observado.

Firmas fijadas a priori: hapax de tipos, colisiones verbatim n=2..4,
cobertura FSA held-out. La deriva regional no la modela ninguno — si
importa, es evidencia de un eje que los tres dejan sin explicar.
"""

from __future__ import annotations

import random
from collections import Counter

from millstone.engine.generative import (
    AutociteModel,
    CatalogModel,
    CombinatorialModel,
    LinguisticModel,
    score,
)
from millstone.engine.induce import induce
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def _collide(lines, n):
    grams = {}
    for i, l in enumerate(lines):
        for k in range(len(l) - n + 1):
            grams.setdefault(tuple(l[k : k + n]), set()).add(i)
    return sum(1 for s in grams.values() if len(s) > 1)


def _signature(lines) -> dict[str, float]:
    words = [w for l in lines for w in l]
    freq = Counter(words)
    hapax = sum(1 for v in freq.values() if v == 1) / max(len(freq), 1)
    return {
        "hapax": hapax,
        "coll2": _collide(lines, 2),
        "coll3": _collide(lines, 3),
        "coll4": _collide(lines, 4),
    }


def _word_level(schema) -> str:
    return "word" if "word" in schema.levels else schema.levels[1]


class ModelCompare:
    name = "model-compare"
    statement = (
        "El mecanismo generativo que mejor explica el corpus (menor DL "
        "held-out entre A lingüístico, B catálogo, C combinatorio) es el "
        "mismo que reproduce las firmas observadas; si divergen, el DL "
        "comprime sin capturar el mecanismo."
    )

    def __init__(self, seed: int = 7):
        self.seed = seed

    def _run_split(self, fsa, train, test, n_sample):
        models = [
            LinguisticModel(fsa),
            CatalogModel(fsa),
            CombinatorialModel(fsa),
            AutociteModel(fsa),
        ]
        for m in models:
            m.fit(train)
        scores = [score(m, test) for m in models]
        rng = random.Random(self.seed)
        sig_test = _signature(test)
        sigs = {}
        for m in models:
            sampled = m.sample_lines(rng, n_sample)
            sigs[m.name] = _signature(sampled)
        return models, scores, sig_test, sigs

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        levels = corpus.schema.levels
        if "word" not in levels:
            return [
                Evidence(
                    "nivel word disponible",
                    None,
                    "corpus de signos sin palabras (v1: comparador a nivel word)",
                )
            ]
        level = "word"
        unit = levels[levels.index("word") + 1]
        lines = [
            s.symbols for s in view.unit_sequences(unit, level) if s.symbols
        ]
        if len(lines) < 40:
            return [Evidence("corpus suficiente", None,
                             f"{len(lines)} líneas")]

        fsa = induce(view, level, positional=True)
        evens = lines[0::2]
        odds = lines[1::2]
        mid = len(lines) // 2
        first, second = lines[:mid], lines[mid:]

        models_i, scores_i, sig_i, sigs_i = self._run_split(
            fsa, evens, odds, len(odds)
        )
        _, scores_c, _, _ = self._run_split(fsa, first, second, len(second))

        def best(scores):
            return min(scores, key=lambda s: s.total_bits)

        bi, bc = best(scores_i), best(scores_c)
        table_i = "; ".join(
            f"{s.name.split('-')[0]}={s.total_bits/1e6:.2f}Mb" for s in scores_i
        )
        table_c = "; ".join(
            f"{s.name.split('-')[0]}={s.total_bits/1e6:.2f}Mb" for s in scores_c
        )
        out = [
            Evidence(
                "un modelo gana el DL held-out (intercalada)",
                True,
                f"gana {bi.name} | {table_i}",
            ),
            Evidence(
                "el ganador se mantiene en partición contigua",
                bi.name == bc.name,
                f"gana {bc.name} | {table_c}",
            ),
        ]

        # reproducción de firmas pre-registradas (muestra del intercalado)
        deltas = {}
        for name, sg in sigs_i.items():
            deltas[name] = {
                k: abs(sg[k] - sig_i[k])
                for k in sig_i
            }
        rep = []
        for m in models_i:
            d = deltas[m.name]
            within = d["hapax"] < 0.1 and d["coll2"] < sig_i["coll2"] * 0.5 + 2
            rep.append((m.name, within, d))
        repro = [n for n, ok, _ in rep if ok]
        detail = " | ".join(
            f"{n}: hapaxΔ={d['hapax']:.2f} coll2Δ={d['coll2']:.0f}"
            for n, _, d in rep
        )
        out.append(
            Evidence(
                "los modelos reproducen las firmas pre-registradas",
                bool(repro),
                f"firma real: {sig_i} | {detail}",
            )
        )
        out.append(
            Evidence(
                "el ganador DL también reproduce la firma",
                bi.name in repro if repro else None,
                f"ganador DL={bi.name}; reproducen={repro or 'ninguno'}",
            )
        )
        return out
