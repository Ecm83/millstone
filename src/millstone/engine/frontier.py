"""Geometría de la frontera: dónde viven las excepciones de una casi-regla.

`frontier_by_attr` agrupa las violaciones por el valor de un atributo del
folio que contiene la palabra (mano $H, quire $Q, lenguaje $L, sección).
La concentración vs. dispersión distingue "ruido de escriba" de "regla
sistemática con excepciones".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from millstone.engine.constraints import Constraint
from millstone.engine.view import CorpusView
from millstone.model import Corpus


@dataclass
class FrontierCell:
    """Violaciones de una regla dentro de un grupo (p.ej. una mano)."""

    key: str
    checked: int = 0
    violations: int = 0
    loci: list[str] = field(default_factory=list)

    @property
    def rate(self) -> float:
        return self.violations / self.checked if self.checked else 0.0


def frontier_by_attr(
    view: CorpusView,
    corpus: Corpus,
    level: str,
    constraint: Constraint,
    folio_attr: str,
) -> dict[str, FrontierCell]:
    """Agrupa violaciones por `folio_attr` resuelto vía prefijo del locus.

    Requiere que el locus de palabra empiece por el id de folio
    ("f1r.5.w3" -> "f1r"), como produce el adaptador IVTFF.
    """
    folio_attrs = {f.locus: f.attrs for f in corpus.nodes("folio")}
    cells: dict[str, FrontierCell] = {}
    for seq in view.sequences(level):
        fid = (seq.locus or "").split(".", 1)[0]
        key = folio_attrs.get(fid, {}).get(folio_attr, "?")
        cell = cells.setdefault(key, FrontierCell(key=key))
        cell.checked += 1
        if not constraint.holds(seq.symbols):
            cell.violations += 1
            if seq.locus:
                cell.loci.append(seq.locus)
    return cells
