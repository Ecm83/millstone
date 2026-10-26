"""DSL de restricciones: reglas gramaticales como datos.

Cada restricción es un dataclass inmutable con dos operaciones:

- `holds(symbols)` — semántica: ¿la secuencia respeta la regla?
- `negatives(alphabet)` — frontera: cadenas mínimas que la violan.

Nada aquí sabe del Voynich: `FollowedBy("q", "o")` es solo una instancia.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


class Constraint:
    def holds(self, symbols: tuple[str, ...]) -> bool:
        raise NotImplementedError

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        """Violadores mínimos: el borde inválido que la regla define."""
        raise NotImplementedError


@dataclass(frozen=True)
class FollowedBy(Constraint):
    """Toda aparición de `trigger` va seguida inmediatamente de `required`.

    `trigger` en posición final también viola (nada puede seguirla).
    """

    trigger: str
    required: str

    def holds(self, symbols: tuple[str, ...]) -> bool:
        for i, s in enumerate(symbols):
            if s == self.trigger:
                if i + 1 >= len(symbols) or symbols[i + 1] != self.required:
                    return False
        return True

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield (self.trigger,)
        for a in sorted(alphabet - {self.required}):
            yield (self.trigger, a)


@dataclass(frozen=True)
class NextInSet(Constraint):
    """Todo `trigger` va seguido inmediatamente de un símbolo de `allowed`.

    Generaliza FollowedBy (singleton). `trigger` en posición final viola.
    """

    trigger: str
    allowed: frozenset[str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        for i, s in enumerate(symbols):
            if s == self.trigger:
                if i + 1 >= len(symbols) or symbols[i + 1] not in self.allowed:
                    return False
        return True

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield (self.trigger,)
        for a in sorted(alphabet - self.allowed):
            yield (self.trigger, a)


@dataclass(frozen=True)
class PrevInSet(Constraint):
    """Todo `symbol` va precedido inmediatamente por uno de `allowed`.

    `symbol` en posición inicial viola.
    """

    symbol: str
    allowed: frozenset[str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        for i, s in enumerate(symbols):
            if s == self.symbol:
                if i == 0 or symbols[i - 1] not in self.allowed:
                    return False
        return True

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield (self.symbol,)
        for a in sorted(alphabet - self.allowed):
            yield (a, self.symbol)


@dataclass(frozen=True)
class StartsWith(Constraint):
    """La secuencia abre con un símbolo de `allowed`. La vacía viola."""

    allowed: frozenset[str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        return bool(symbols) and symbols[0] in self.allowed

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield ()
        for a in sorted(alphabet - self.allowed):
            yield (a,)


@dataclass(frozen=True)
class EndsWith(Constraint):
    """La secuencia cierra con un símbolo de `allowed`. La vacía viola."""

    allowed: frozenset[str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        return bool(symbols) and symbols[-1] in self.allowed

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield ()
        for a in sorted(alphabet - self.allowed):
            yield (a,)


@dataclass(frozen=True)
class ForbidsBigram(Constraint):
    """El par ordenado (a, b) nunca aparece adjunto."""

    pair: tuple[str, str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        return self.pair not in zip(symbols, symbols[1:])

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        yield self.pair


@dataclass(frozen=True)
class OnlyInPosition(Constraint):
    """`symbol` solo aparece en la posición `index` (−1 = última).

    P.ej. "n solo cierra palabra" = OnlyInPosition("n", -1).
    """

    symbol: str
    index: int

    def holds(self, symbols: tuple[str, ...]) -> bool:
        for i, s in enumerate(symbols):
            if s == self.symbol:
                pos = i if self.index >= 0 else i - len(symbols)
                if pos != self.index:
                    return False
        return True

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        others = sorted(alphabet - {self.symbol})
        if self.index == 0:
            for a in others:
                yield (a, self.symbol)
        elif self.index == -1:
            for a in others:
                yield (self.symbol, a)
        else:
            yield (self.symbol,)


@dataclass(frozen=True)
class SymbolAt(Constraint):
    """Slot posicional: el símbolo en `index` (−1 = último) ∈ `allowed`.

    Secuencias más cortas que |index| no violan (no tienen ese slot).
    """

    index: int
    allowed: frozenset[str]

    def holds(self, symbols: tuple[str, ...]) -> bool:
        i = self.index if self.index >= 0 else len(symbols) + self.index
        if not 0 <= i < len(symbols):
            return True
        return symbols[i] in self.allowed

    def negatives(self, alphabet: frozenset[str]) -> Iterator[tuple[str, ...]]:
        i = abs(self.index)
        pad = ("_",) * i if self.index >= 0 else ()
        for a in sorted(alphabet - self.allowed):
            yield pad + (a,) if self.index >= 0 else (a,)
