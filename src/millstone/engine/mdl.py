"""MDL: la gramática correcta es la que comprime mejor el corpus.

Dos partes:

- `model_cost` — bits para describir el conjunto de restricciones.
- `data_cost` — bits para codificar el corpus dado el conjunto: en cada
  posición las restricciones reducen los símbolos permitidos, y el coste es
  log2|permitidos|. Restricciones entrañadas por otras no reducen nada —
  `prune()` las elimina sin perder poder predictivo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from millstone.engine.constraints import (
    Constraint,
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    NextInSet,
    OnlyInPosition,
    PrevInSet,
    StartsWith,
    SymbolAt,
)
from millstone.engine.check import alphabet
from millstone.engine.discover import Discovery
from millstone.engine.view import CorpusView

N_TYPES = 8  # tipos de restricción del DSL
MAX_INDEX = 16  # posiciones codificables en el DSL


def constraint_cost(c: Constraint, alphabet_size: int) -> float:
    """Bits para describir una restricción sobre un alfabeto dado."""
    tag = math.log2(N_TYPES)
    sym = math.log2(alphabet_size)
    if isinstance(c, (FollowedBy, ForbidsBigram)):
        return tag + 2 * sym
    if isinstance(c, (NextInSet, PrevInSet)):
        return tag + sym + alphabet_size  # trigger + vector indicador
    if isinstance(c, (StartsWith, EndsWith)):
        return tag + alphabet_size  # vector indicador
    if isinstance(c, OnlyInPosition):
        return tag + sym + math.log2(MAX_INDEX)
    if isinstance(c, SymbolAt):
        return tag + math.log2(MAX_INDEX) + alphabet_size
    raise TypeError(f"tipo de restricción desconocido: {type(c)}")


def model_cost(constraints: list[Constraint], alphabet_size: int) -> float:
    return sum(constraint_cost(c, alphabet_size) for c in constraints)


def _allowed_at(
    symbols: tuple[str, ...],
    i: int,
    constraints: list[Constraint],
    alpha: frozenset[str],
) -> frozenset[str]:
    """Símbolos permitidos en la posición i según el conjunto de reglas."""
    L = len(symbols)
    allowed = set(alpha)
    prev = symbols[i - 1] if i > 0 else None
    for c in constraints:
        if isinstance(c, StartsWith) and i == 0:
            allowed &= c.allowed
        elif isinstance(c, EndsWith) and i == L - 1:
            allowed &= c.allowed
        elif isinstance(c, SymbolAt) and (i == c.index or i - L == c.index):
            allowed &= c.allowed
        elif isinstance(c, OnlyInPosition):
            pos = i if c.index >= 0 else i - L
            if pos != c.index:
                allowed.discard(c.symbol)
        elif isinstance(c, FollowedBy) and prev == c.trigger:
            allowed &= {c.required}
        elif isinstance(c, NextInSet) and prev == c.trigger:
            allowed &= c.allowed
        elif isinstance(c, PrevInSet) and prev not in c.allowed:
            allowed.discard(c.symbol)
        elif isinstance(c, ForbidsBigram) and prev == c.pair[0]:
            allowed.discard(c.pair[1])
    return frozenset(allowed)


def data_cost(
    view: CorpusView,
    level: str,
    constraints: list[Constraint],
    alpha: frozenset[str],
) -> float:
    """Bits para codificar el corpus: log2|permitidos| por símbolo.

    Un símbolo no permitido se codifica como excepción: 1 bit de flag más
    log2|alfabeto| literal.
    """
    total = 0.0
    for seq in view.sequences(level):
        L = len(seq.symbols)
        total += math.log2(max(L, 1) + 1)  # longitud de la secuencia
        for i, s in enumerate(seq.symbols):
            allowed = _allowed_at(seq.symbols, i, constraints, alpha)
            if s not in allowed:
                total += 1.0 + math.log2(len(alpha))
            else:
                total += math.log2(max(len(allowed), 1))
    return total


def entails(a: Constraint, b: Constraint) -> bool:
    """¿`a` implica lógicamente `b`? (sobre cualquier secuencia)."""
    if a == b:
        return True
    if isinstance(a, OnlyInPosition) and isinstance(b, ForbidsBigram):
        # s solo al final ⇒ ningún bigrama (s, ·); solo al inicio ⇒ ningún (·, s)
        return (a.index == -1 and b.pair[0] == a.symbol) or (
            a.index == 0 and b.pair[1] == a.symbol
        )
    if isinstance(a, FollowedBy) and isinstance(b, ForbidsBigram):
        return b.pair[0] == a.trigger and b.pair[1] != a.required
    if isinstance(a, NextInSet) and isinstance(b, ForbidsBigram):
        return b.pair[0] == a.trigger and b.pair[1] not in a.allowed
    if isinstance(a, PrevInSet) and isinstance(b, ForbidsBigram):
        return b.pair[1] == a.symbol and b.pair[0] not in a.allowed
    if isinstance(a, NextInSet) and isinstance(b, NextInSet):
        return a.trigger == b.trigger and a.allowed <= b.allowed
    if isinstance(a, PrevInSet) and isinstance(b, PrevInSet):
        return a.symbol == b.symbol and a.allowed <= b.allowed
    if isinstance(a, FollowedBy) and isinstance(b, NextInSet):
        return a.trigger == b.trigger and {a.required} <= b.allowed
    if isinstance(a, NextInSet) and len(a.allowed) == 1 and isinstance(b, FollowedBy):
        return a.trigger == b.trigger and b.required in a.allowed
    return False


@dataclass(frozen=True)
class MDLResult:
    basis: list[Discovery]
    model_bits: float
    data_bits: float

    @property
    def total_bits(self) -> float:
        return self.model_bits + self.data_bits


def prune(view: CorpusView, level: str, discoveries: list[Discovery]) -> MDLResult:
    """Selección MDL: base mínima sin restricciones entrañadas por otras.

    Solo las restricciones exactas (`violations == 0`) entran en la base:
    una casi-regla describe una frontera con excepciones, no una ley —
    eso es material de `hypotheses`, no del conjunto de restricciones.

    Orden: primero las que más candidatos explican (cobertura), luego soporte.
    Una candidata entrañada por la base se descarta.
    """
    discoveries = [d for d in discoveries if d.violations == 0]
    alpha = alphabet(view)
    coverage = [
        sum(
            1
            for j, o in enumerate(discoveries)
            if i != j and entails(d.constraint, o.constraint)
        )
        for i, d in enumerate(discoveries)
    ]
    order = sorted(
        range(len(discoveries)),
        key=lambda i: (-coverage[i], -discoveries[i].support),
    )
    basis: list[Discovery] = []
    for i in order:
        d = discoveries[i]
        if not any(entails(k.constraint, d.constraint) for k in basis):
            basis.append(d)

    constraints = [d.constraint for d in basis]
    return MDLResult(
        basis=basis,
        model_bits=model_cost(constraints, len(alpha)),
        data_bits=data_cost(view, level, constraints, alpha),
    )
