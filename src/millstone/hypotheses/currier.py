"""Currier A/B: el corpus contiene dos "lenguajes" distintos por folio.

La variable $L de la cabecera de folio IVTFF lleva la clasificación.
Predicción testeable: si A y B son lenguajes distintos, sus conjuntos de
restricciones exactas y sus fronteras de casi-reglas difieren; si la
etiqueta fuera arbitraria, las gramáticas inducidas serían iguales.
"""

from __future__ import annotations

from millstone.engine.check import check
from millstone.engine.constraints import FollowedBy
from millstone.engine.discover import discover
from millstone.engine.view import CorpusView, MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus, subcorpus


class CurrierAB:
    name = "currier-ab"
    statement = (
        "Los folios etiquetados $L=A y $L=B siguen gramáticas distintas: "
        "no es ruido de transcripción sino estructura."
    )

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        a = MemoryCorpusView(
            subcorpus(corpus, "folio", lambda n: n.attrs.get("L") == "A")
        )
        b = MemoryCorpusView(
            subcorpus(corpus, "folio", lambda n: n.attrs.get("L") == "B")
        )
        na = sum(1 for _ in a.sequences("word"))
        nb = sum(1 for _ in b.sequences("word"))
        if na < 100 or nb < 100:
            return [Evidence("particiones A/B no vacías", None,
                             f"A={na} palabras, B={nb}")]

        da = discover(a, "word")
        db = discover(b, "word")
        exact_a = {d.constraint for d in da if d.violations == 0}
        exact_b = {d.constraint for d in db if d.violations == 0}
        only_a = exact_a - exact_b
        only_b = exact_b - exact_a

        # frontera de la casi-regla canónica en cada partición
        qa = check(a, "word", FollowedBy("q", "o")).violation_rate
        qb = check(b, "word", FollowedBy("q", "o")).violation_rate

        return [
            Evidence(
                "particiones A/B no vacías", True,
                f"A={na} palabras, B={nb}",
            ),
            Evidence(
                "los conjuntos de reglas exactas difieren",
                bool(only_a or only_b),
                f"solo-A: {len(only_a)}, solo-B: {len(only_b)}; "
                f"ejemplos A-only: {sorted(map(str, only_a))[:3]}; "
                f"B-only: {sorted(map(str, only_b))[:3]}",
            ),
            Evidence(
                "la frontera de q->o difiere entre A y B",
                abs(qa - qb) > 0.005,
                f"viol. q->o: A={qa:.4%} ({na}), B={qb:.4%} ({nb})",
            ),
        ]
