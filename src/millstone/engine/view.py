"""CorpusView: el contrato entre el engine y cualquier fuente de corpus.

El engine solo ve `Sequence`s — tuplas de símbolos hoja agrupadas bajo un
nivel — más la lista de niveles del schema. `MemoryCorpusView` lo implementa
sobre un `Corpus` en RAM; una versión Neo4j implementará el mismo contrato.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol

from millstone.model import Corpus


@dataclass(frozen=True)
class Sequence:
    """Secuencia de símbolos hoja bajo un nodo de nivel dado."""

    locus: str | None
    symbols: tuple[str, ...]


class CorpusView(Protocol):
    def levels(self) -> tuple[str, ...]:
        """Niveles del schema, de más fino a más grueso."""
        ...

    def sequences(self, level: str) -> Iterator[Sequence]:
        """Secuencias de hojas agrupadas por nodo de `level`."""
        ...


class MemoryCorpusView:
    def __init__(self, corpus: Corpus):
        self.corpus = corpus

    def levels(self) -> tuple[str, ...]:
        return self.corpus.schema.levels

    def sequences(self, level: str) -> Iterator[Sequence]:
        for node in self.corpus.nodes(level):
            yield Sequence(
                locus=node.locus,
                symbols=tuple(
                    leaf.value for leaf in node.leaves() if leaf.value is not None
                ),
            )
