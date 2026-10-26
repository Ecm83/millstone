"""Frontera de q->o: ¿ruido de escriba o regla suave?

Si las ~124 violaciones se concentraran en una mano/quire concreta, sería
evidencia de error o convención local. Si se distribuyen en proporción a la
masa de palabras, la casi-regla es estructuralmente suave.
"""

from __future__ import annotations

from millstone.engine.constraints import FollowedBy
from millstone.engine.frontier import frontier_by_attr
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class QoFrontier:
    name = "qo-frontier"
    statement = (
        "Las violaciones de q->o son ruido concentrado (mano/quire/folio), "
        "no una propiedad distribuida del lenguaje."
    )

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        out: list[Evidence] = []
        for attr, label in (("H", "mano"), ("Q", "quire"), ("L", "lenguaje")):
            cells = frontier_by_attr(view, corpus, "word", FollowedBy("q", "o"), attr)
            cells = {k: c for k, c in cells.items() if c.checked >= 100}
            if not cells:
                out.append(Evidence(f"violaciones por {label}", None, "sin datos"))
                continue
            total_v = sum(c.violations for c in cells.values())
            top = max(cells.values(), key=lambda c: c.violations)
            share_v = top.violations / total_v if total_v else 0.0
            share_w = top.checked / sum(c.checked for c in cells.values())
            # concentrado: el grupo dominante acapara violaciones muy por
            # encima de su masa de palabras
            concentrated = share_v > 2 * share_w and share_v > 0.3
            dist = ", ".join(
                f"{k}:{c.violations}/{c.checked}"
                for k, c in sorted(cells.items(), key=lambda kv: -kv[1].violations)
            )
            out.append(
                Evidence(
                    f"violaciones de q->o concentradas por {label}",
                    concentrated,
                    f"grupo top '{top.key}': {share_v:.1%} de violaciones "
                    f"con {share_w:.1%} de palabras | {dist}",
                )
            )
        return out
