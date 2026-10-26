"""Robustez inter-transcripción: ¿las fronteras están en el manuscrito?

Si una casi-regla violara por ruido de lectura, las violaciones entre dos
transcripciones independientes (Zandbergen-Landini vs Takahashi) caerían en
loci distintos. Si coinciden, la excepción es del manuscrito — ambos
transcritores leyeron el mismo glifo.
"""

from __future__ import annotations

from millstone.engine.check import check
from millstone.engine.constraints import FollowedBy
from millstone.engine.view import CorpusView, MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class TranscriptionRobust:
    name = "transcription-robust"
    statement = (
        "Las violaciones de una casi-regla coinciden en locus entre "
        "transcripciones independientes -> la frontera es del manuscrito."
    )

    def __init__(self, constraint=None):
        self.constraint = constraint or FollowedBy("q", "o")

    def evaluate(self, corpus: Corpus, other: Corpus) -> list[Evidence]:
        va = MemoryCorpusView(corpus)
        vb = MemoryCorpusView(other)
        ra = check(va, "word", self.constraint)
        rb = check(vb, "word", self.constraint)
        # líneas violadoras (locus sin el sufijo .wN)
        la = {x.locus.rsplit(".w", 1)[0] for x in ra.violations}
        lb = {x.locus.rsplit(".w", 1)[0] for x in rb.violations}
        common = la & lb
        # proporción sobre la transcripción con menos violaciones
        overlap = len(common) / min(len(la), len(lb)) if la and lb else 0.0
        return [
            Evidence(
                "las violaciones coinciden en locus entre transcripciones",
                overlap > 0.7,
                f"loci violadores: A={len(la)} B={len(lb)} comunes={len(common)} "
                f"({overlap:.0%} de solape)",
            )
        ]
