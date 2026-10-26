"""Inducción de restricciones: qué reglas del DSL se cumplen en el corpus.

Métodos de Mill operacionalizados: el corpus revela los conjuntos observados
(sucesores, precedentes, iniciales/finales, posiciones, bigramas). Una
restricción solo se reporta con su soporte y su cuenta de violaciones —
las casi-reglas (`violations > 0`) son el borde inválido que el proyecto
estudia: la frontera válido/inválido es el objeto, no el ruido.

Para `NextInSet`/`PrevInSet` se emite la frontera de Pareto: cada prefijo
del ranking de sucesores observados es un candidato con su propio par
(|allowed|, violations). MDL decide cuál comprime mejor.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterator

from millstone.engine.constraints import (
    Constraint,
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    NextInSet,
    OnlyInPosition,
    PrevInSet,
    StartsWith,
)
from millstone.engine.view import CorpusView


@dataclass(frozen=True)
class Discovery:
    """Una restricción candidata con su evidencia."""

    constraint: Constraint
    support: int       # ocurrencias que testean la regla
    checked: int       # secuencias examinadas
    violations: int = 0  # ocurrencias que la violan (0 = regla exacta)


def _pareto_sets(
    observed: Counter, total: int, terminal: int
) -> Iterator[tuple[frozenset[str], int]]:
    """Prefijos del ranking de observados: (allowed, violations) creciente."""
    items = [(s, n) for s, n in observed.most_common() if s is not None]
    allowed: set[str] = set()
    covered = 0
    for s, n in items:
        allowed.add(s)
        covered += n
        yield frozenset(allowed), terminal + (total - terminal - covered)


def discover(
    view: CorpusView, level: str, min_support: int = 5
) -> list[Discovery]:
    seqs = list(view.sequences(level))
    # alfabeto del NIVEL analizado (puede ser glifo transformado, no hoja)
    alpha = frozenset(s for seq in seqs for s in seq.symbols)
    n = len(seqs)
    out: list[Discovery] = []
    if not seqs or not alpha:
        return out

    counts: Counter[str] = Counter()
    followers: dict[str, Counter] = {a: Counter() for a in alpha}
    preceders: dict[str, Counter] = {a: Counter() for a in alpha}
    start_pos: dict[str, set[int]] = {a: set() for a in alpha}
    end_pos: dict[str, set[int]] = {a: set() for a in alpha}
    bigrams: set[tuple[str, str]] = set()

    for s in seqs:
        L = len(s.symbols)
        for i, ch in enumerate(s.symbols):
            counts[ch] += 1
            start_pos[ch].add(i)
            end_pos[ch].add(i - L)
            nxt = s.symbols[i + 1] if i + 1 < L else None
            prv = s.symbols[i - 1] if i > 0 else None
            followers[ch][nxt] += 1
            preceders[ch][prv] += 1
            if nxt is not None:
                bigrams.add((ch, nxt))

    # Símbolos que solo abren / solo cierran: el conjunto observado exacto
    initials = frozenset(s.symbols[0] for s in seqs if s.symbols)
    if initials and initials < alpha:
        out.append(Discovery(StartsWith(initials), n, n))
    finals = frozenset(s.symbols[-1] for s in seqs if s.symbols)
    if finals and finals < alpha:
        out.append(Discovery(EndsWith(finals), n, n))

    for a in sorted(alpha):
        if counts[a] < min_support:
            continue
        tot = counts[a]

        # Sucesor único exacto: "toda a va seguida de b"
        if len(followers[a]) == 1 and None not in followers[a]:
            (b,) = followers[a]
            out.append(Discovery(FollowedBy(a, b), tot, n))

        # NextInSet / PrevInSet: frontera de Pareto por prefijo del ranking.
        # Solo conjuntos propios del alfabeto (de lo contrario no restringen).
        for allowed, viol in _pareto_sets(followers[a], tot, followers[a][None]):
            if len(allowed) < len(alpha):
                out.append(Discovery(NextInSet(a, allowed), tot, n, viol))
        for allowed, viol in _pareto_sets(preceders[a], tot, preceders[a][None]):
            if len(allowed) < len(alpha):
                out.append(Discovery(PrevInSet(a, allowed), tot, n, viol))

        # Posición exclusiva: "a solo en índice k" / "a solo al final"
        if len(start_pos[a]) == 1:
            out.append(Discovery(OnlyInPosition(a, start_pos[a].pop()), tot, n))
        elif len(end_pos[a]) == 1:
            out.append(Discovery(OnlyInPosition(a, end_pos[a].pop()), tot, n))

        # Hueco sorprendente: a y b son frecuentes pero "ab" nunca ocurre
        for b in sorted(alpha):
            if counts[b] >= min_support and (a, b) not in bigrams:
                out.append(
                    Discovery(ForbidsBigram((a, b)), counts[a] + counts[b], n)
                )

    out.sort(key=lambda d: (-d.support, d.violations))
    return out
