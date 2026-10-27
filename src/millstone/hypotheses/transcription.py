"""Robustez inter-transcripción: ¿las fronteras están en el manuscrito?

Si una casi-regla violara por ruido de lectura, las violaciones entre dos
transcripciones independientes (Zandbergen-Landini vs Takahashi) caerían en
loci distintos. Si coinciden, la excepción es del manuscrito — ambos
transcritores leyeron el mismo glifo.
"""

from __future__ import annotations

from millstone.engine.check import check
from millstone.engine.constraints import FollowedBy
from millstone.engine.transcription import compare
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class TranscriptionRobust:
    name = "transcription-robust"
    needs_two = True  # evaluate(corpus, other): dos transcripciones
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

        # granularidad palabra: el .wN debe coincidir exactamente — si la
        # línea coincide pero la palabra no, hay desacuerdo de segmentación
        wa = {x.locus for x in ra.violations}
        wb = {x.locus for x in rb.violations}
        common_w = wa & wb
        overlap_w = (
            len(common_w) / min(len(wa), len(wb)) if wa and wb else 0.0
        )

        rep = compare(corpus, other, "word")
        top = ", ".join(
            f"{a}->{b} x{n}" for (a, b), n in rep.confusion.most_common(5)
        )
        return [
            Evidence(
                "las violaciones coinciden en locus entre transcripciones",
                overlap > 0.7,
                f"loci violadores: A={len(la)} B={len(lb)} comunes={len(common)} "
                f"({overlap:.0%} de solape)",
            ),
            Evidence(
                "las violaciones coinciden a nivel de palabra exacta",
                overlap_w > 0.5,
                f"palabras violadoras: A={len(wa)} B={len(wb)} "
                f"comunes={len(common_w)} ({overlap_w:.0%} de solape)",
            ),
            Evidence(
                "las transcripciones acuerdan la mayoría de palabras",
                rep.agreement > 0.8,
                f"{rep.paired} pares: {rep.agreement:.1%} idénticas | "
                f"estructurales {rep.structural} | "
                f"solo-A {rep.only_a}, solo-B {rep.only_b}"
                + (f" | confusión top: {top}" if top else ""),
            ),
        ]
