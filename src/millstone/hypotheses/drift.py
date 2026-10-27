"""Deriva regional: ¿salto categórico Currier o evolución gradual por quire?

`regional-replication` demostró que las casi-reglas derivan entre la
primera y la segunda mitad del manuscrito (núcleo duro estacionario,
textura suave regional). Falta la geometría de esa deriva:

- **salto**: la tasa de violación cambia con el sublenguaje Currier ($L)
  — dos plateaus, no una rampa;
- **gradual**: los quires ($Q ordenado) de una *misma* lengua también se
  separan — evolución continua de la práctica escribal.

Método: se toman las reglas que más derivan entre mitades y se mide su
tasa de violación por celda (quire, lengua) **por ocurrencia de
trigger** — factoriza la longitud de palabra, el confounder que la
primera versión de este módulo dejó escapar (el nulo barajado lo
reveló: las tasas por secuencia varían solas con la composición de la
región). Si el gap entre lenguas supera la dispersión entre quires de
la misma lengua, la deriva es categórica. Control de Mill: sobre el
corpus barajado los gaps deben colapsar a ~0.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import median
from typing import Iterator

from millstone.engine.check import check
from millstone.engine.discover import discover
from millstone.engine.view import MemoryCorpusView, Sequence
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


@dataclass
class _SeqsView:
    """CorpusView mínimo sobre una lista de secuencias."""

    all_levels: tuple[str, ...]
    level: str
    seqs: list[Sequence]

    def levels(self) -> tuple[str, ...]:
        return self.all_levels

    def sequences(self, level: str) -> Iterator[Sequence]:
        if level == self.level:
            yield from self.seqs


@dataclass
class _Drift:
    """Perfil de deriva de una regla: gap Currier vs dispersión intra-lengua."""

    constraint: object
    delta_halves: float
    delta_lang: float | None      # |rate(lengua A) - rate(lengua B)|
    within_spread: float          # max |rate(q1) - rate(q2)| dentro de una lengua
    n_cells: int


class DriftProfile:
    name = "drift-profile"
    statement = (
        "La deriva de las casi-reglas entre regiones sigue el corte "
        "Currier A/B (salto categórico entre sublenguajes) más que una "
        "evolución gradual a lo largo de los quires."
    )

    def __init__(
        self,
        min_support: int = 5,
        max_rules: int = 100,
        n_track: int = 10,
        min_cell: int = 150,
        min_drift: float = 0.02,
        seed: int = 0,
    ):
        self.min_support = min_support
        self.max_rules = max_rules
        self.n_track = n_track
        self.min_cell = min_cell
        self.min_drift = min_drift
        self.seed = seed

    def _cells(self, view, corpus, level, constraint):
        """Tasa de violación por celda (quire $Q, lengua $L).

        Las tasas son **por ocurrencia de trigger** (`events`), no por
        palabra: factoriza la longitud de la secuencia, el confounder
        que el nulo barajado reveló en la primera versión.
        """
        folio_attrs = {f.locus: f.attrs for f in corpus.nodes("folio")}
        cells: dict[tuple[str, str], list[int]] = {}
        for seq in view.sequences(level):
            fid = (seq.locus or "").split(".", 1)[0]
            attrs = folio_attrs.get(fid, {})
            key = (attrs.get("Q", "?"), attrs.get("L", "?"))
            cell = cells.setdefault(key, [0, 0])
            opp, viol = constraint.events(seq.symbols)
            cell[0] += opp
            cell[1] += viol
        return {
            k: v[1] / v[0]
            for k, v in cells.items()
            if v[0] >= self.min_cell and "?" not in k
        }

    def _profile(self, view, corpus, level, constraint, delta_halves):
        cells = self._cells(view, corpus, level, constraint)
        if len(cells) < 3:
            return None
        by_lang: dict[str, dict[str, float]] = {}
        for (q, lang), rate in cells.items():
            by_lang.setdefault(lang, {})[q] = rate
        delta_lang = None
        spreads = []
        if len(by_lang) >= 2:
            means = {
                lang: sum(rs.values()) / len(rs)
                for lang, rs in by_lang.items()
            }
            vals = list(means.values())
            delta_lang = max(vals) - min(vals)
        for rs in by_lang.values():
            if len(rs) >= 2:
                spreads.append(max(rs.values()) - min(rs.values()))
        return _Drift(
            constraint=constraint,
            delta_halves=delta_halves,
            delta_lang=delta_lang,
            within_spread=max(spreads) if spreads else 0.0,
            n_cells=len(cells),
        )

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        levels = corpus.schema.levels
        if "folio" not in levels:
            return [
                Evidence(
                    "atributos $Q/$L disponibles", None,
                    "schema sin nivel folio",
                )
            ]
        level = "word" if "word" in levels else levels[1]
        view = MemoryCorpusView(corpus)
        seqs = list(view.sequences(level))
        if len(seqs) < 400:
            return [
                Evidence("corpus suficiente", None, f"{len(seqs)} secuencias")
            ]

        mid = len(seqs) // 2
        a = _SeqsView(levels, level, seqs[:mid])
        b = _SeqsView(levels, level, seqs[mid:])

        ds = discover(a, level, min_support=self.min_support)[: self.max_rules]
        ranked = []
        for d in ds:
            ra = check(a, level, d.constraint)
            rb = check(b, level, d.constraint)
            ranked.append(
                (abs(rb.violation_rate - ra.violation_rate), d.constraint)
            )
        ranked.sort(key=lambda r: -r[0])
        tracked = [r for r in ranked if r[0] > self.min_drift][: self.n_track]
        if len(tracked) < 3:
            return [
                Evidence(
                    "reglas que derivan suficientes", None,
                    f"solo {len(tracked)} con deriva > {self.min_drift:.0%}",
                )
            ]

        # Nulo Mill: símbolos barajados dentro de cada palabra - los gaps
        # regionales deben desaparecer si la deriva es estructura real.
        rng = random.Random(self.seed)
        shuf = _SeqsView(
            levels, level,
            [
                Sequence(s.locus, tuple(rng.sample(s.symbols, len(s.symbols))))
                for s in seqs
            ],
        )

        drifts: list[_Drift] = []
        null_drifts: list[_Drift] = []
        for delta, c in tracked:
            prof = self._profile(view, corpus, level, c, delta)
            if prof is not None:
                drifts.append(prof)
            nul = self._profile(shuf, corpus, level, c, 0.0)
            if nul is not None:
                null_drifts.append(nul)

        if not drifts:
            return [
                Evidence(
                    "celdas (quire, lengua) suficientes", None,
                    f"min_cell={self.min_cell} sin cobertura",
                )
            ]

        comparable = [d for d in drifts if d.delta_lang is not None]
        aligned = sum(
            1 for d in comparable if d.delta_lang > d.within_spread
        )
        frac_aligned = aligned / len(comparable) if comparable else 0.0
        med_lang = median(d.delta_lang for d in comparable) if comparable else 0.0
        med_within = median(d.within_spread for d in drifts)
        # Nulo mecánico: sobre el barajado, las tasas por celda también se
        # separan - las regiones difieren en longitud/composición de
        # palabra, así que cualquier regla a nivel secuencia varía sola.
        # Solo el exceso sobre ese nulo es deriva real.
        null_lang = median(
            d.delta_lang for d in null_drifts if d.delta_lang is not None
        ) if null_drifts else 0.0
        null_within = median(d.within_spread for d in null_drifts) \
            if null_drifts else 0.0

        peores = "; ".join(
            f"{d.constraint}: Δlengua={d.delta_lang:.1%} "
            f"vs intra={d.within_spread:.1%}"
            for d in sorted(
                comparable, key=lambda x: -(x.delta_lang - x.within_spread)
            )[:3]
            if d.delta_lang is not None
        )

        return [
            Evidence(
                "la deriva se alinea con el corte Currier ($L)",
                frac_aligned >= 0.6 and med_lang - null_lang > 0.05,
                f"{aligned}/{len(comparable)} reglas con gap entre lenguas "
                f"> dispersión intra-lengua | mediana Δlengua={med_lang:.1%} "
                f"vs intra={med_within:.1%} | {peores}",
            ),
            Evidence(
                "residual gradual dentro de lengua, por encima del nulo "
                "mecánico",
                med_within - null_within > 0.05,
                f"dispersión intra-lengua mediana real={med_within:.1%} vs "
                f"barajado={null_within:.1%} sobre {len(drifts)} reglas",
            ),
            Evidence(
                "el gap Currier supera al corpus barajado (Mill: diferencia)",
                med_lang - null_lang > 0.05,
                f"Δlengua mediana real={med_lang:.1%} vs "
                f"barajado={null_lang:.1%}"
                + (
                    " - por debajo del nulo, el corte A/B es mecánico "
                    "(longitud/composición), no deriva"
                    if med_lang - null_lang <= 0.05
                    else ""
                ),
            ),
        ]
