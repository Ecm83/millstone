"""Comparación formal entre dos transcripciones del mismo corpus.

Dos transcripciones independientes (ZL vs Takahashi) del mismo manuscrito
se alinean por locus a nivel de palabra. El informe separa tres clases de
desacuerdo:

- idénticas: ambos transcritores leyeron lo mismo (la forma es del objeto)
- confusión: una sustitución aislada — par (a,b) de glifos en disputa
- estructural: longitudes distintas (un glifo leído como ligadura, etc.)

`by_folio` da la geometría del desacuerdo: qué regiones concentran la
incertidumbre de lectura — la frontera transcripción-dependiente.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from millstone.engine.view import MemoryCorpusView
from millstone.model import Corpus


@dataclass(frozen=True)
class TranscriptionComparison:
    """Informe de comparación a granularidad de locus palabra."""

    level: str
    paired: int = 0
    identical: int = 0
    only_a: int = 0
    only_b: int = 0
    structural: int = 0          # longitudes distintas
    confusion: Counter = field(default_factory=Counter)
    by_folio: dict[str, tuple[int, int]] = field(default_factory=dict)

    @property
    def agreement(self) -> float:
        return self.identical / self.paired if self.paired else 0.0


def compare(corpus_a: Corpus, corpus_b: Corpus, level: str = "word") -> TranscriptionComparison:
    """Empareja secuencias por locus y cuenta desacuerdos."""
    sa = {
        s.locus: s.symbols
        for s in MemoryCorpusView(corpus_a).sequences(level)
        if s.locus
    }
    sb = {
        s.locus: s.symbols
        for s in MemoryCorpusView(corpus_b).sequences(level)
        if s.locus
    }
    common = sa.keys() & sb.keys()

    identical = structural = 0
    confusion: Counter = Counter()
    folio: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for loc in common:
        wa, wb = sa[loc], sb[loc]
        f = loc.split(".")[0]
        folio[f][1] += 1
        if wa == wb:
            identical += 1
            folio[f][0] += 1
        elif len(wa) != len(wb):
            structural += 1
        else:
            diffs = [(x, y) for x, y in zip(wa, wb) if x != y]
            if len(diffs) == 1:
                confusion[diffs[0]] += 1
            else:
                structural += 1

    return TranscriptionComparison(
        level=level,
        paired=len(common),
        identical=identical,
        only_a=len(sa) - len(common),
        only_b=len(sb) - len(common),
        structural=structural,
        confusion=confusion,
        by_folio={k: (v[0], v[1]) for k, v in folio.items()},
    )
