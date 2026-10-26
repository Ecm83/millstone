"""Modelo de corpus genérico.

La jerarquía no está hardcodeada: cada corpus declara sus niveles de más fino
a más grueso en un `CorpusSchema`. Ejemplos:

    Voynich:  ("symbol", "word", "line", "paragraph", "folio", "section", "corpus")
    Texto:    ("symbol", "word", "sentence", "paragraph", "document", "corpus")

Sin dependencias de grafo ni de ninguna capa superior: dataclasses puras.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterator


@dataclass(frozen=True)
class CorpusSchema:
    """Niveles jerárquicos de un corpus, ordenados de más fino a más grueso.

    El último nivel es la raíz del árbol. Mínimo dos niveles (hoja y raíz).
    """

    levels: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.levels) < 2:
            raise ValueError("un schema necesita al menos dos niveles")
        if len(set(self.levels)) != len(self.levels):
            raise ValueError("los niveles del schema deben ser únicos")

    @property
    def leaf_level(self) -> str:
        return self.levels[0]

    @property
    def root_level(self) -> str:
        return self.levels[-1]

    def index(self, level: str) -> int:
        return self.levels.index(level)

    def parent_level(self, level: str) -> str | None:
        i = self.index(level)
        return self.levels[i + 1] if i + 1 < len(self.levels) else None

    def child_level(self, level: str) -> str | None:
        i = self.index(level)
        return self.levels[i - 1] if i > 0 else None


@dataclass
class Node:
    """Nodo del árbol de corpus.

    `value`  es la forma de superficie en hojas (p.ej. un símbolo EVA) y None
    en contenedores. `locus` es la referencia externa opcional
    ("f1r.P.1", "cap.3 §2", etc.). `attrs` guarda metadatos de la fuente
    (lecturas inciertas, ilustración del folio, etc.).
    """

    level: str
    children: list[Node] = field(default_factory=list)
    value: str | None = None
    locus: str | None = None
    attrs: dict[str, str] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def iter_level(self, level: str) -> Iterator[Node]:
        if self.level == level:
            yield self
        for child in self.children:
            yield from child.iter_level(level)

    def leaves(self) -> Iterator[Node]:
        if self.is_leaf:
            yield self
        else:
            for child in self.children:
                yield from child.leaves()


@dataclass
class Corpus:
    schema: CorpusSchema
    root: Node
    meta: dict[str, str] = field(default_factory=dict)

    def nodes(self, level: str) -> Iterator[Node]:
        return self.root.iter_level(level)

    def tokens(self, level: str | None = None) -> Iterator[str]:
        """Formas de superficie de los nodos de un nivel (hojas por defecto)."""
        level = level or self.schema.leaf_level
        for node in self.nodes(level):
            if node.value is not None:
                yield node.value

    def validate(self) -> list[str]:
        """Verifica que el árbol respeta el schema. Devuelve errores."""
        errors: list[str] = []

        def walk(node: Node, expected: str) -> None:
            if node.level != expected:
                errors.append(
                    f"{node.locus or '?'}: nivel {node.level!r}, "
                    f"esperado {expected!r}"
                )
            child_level = self.schema.child_level(expected)
            if node.is_leaf:
                # raíz vacía = corpus vacío (válido); en otro nivel es un hueco
                if child_level is not None and node is not self.root:
                    errors.append(
                        f"{node.locus or '?'}: {node.level!r} sin hijos"
                    )
            else:
                if child_level is None:
                    errors.append(
                        f"{node.locus or '?'}: hoja {node.level!r} con hijos"
                    )
                else:
                    for child in node.children:
                        walk(child, child_level)

        walk(self.root, self.schema.root_level)
        return errors


def subcorpus(
    corpus: Corpus, level: str, keep: Callable[[Node], bool]
) -> Corpus:
    """Subcorpus con solo los nodos de `level` que cumplen `keep`.

    Conserva la cadena de ancestros (los contenedores sin descendientes
    mantenidos se podan) y comparte los subárboles intactos.
    """
    def rec(node: Node) -> Node | None:
        if node.level == level:
            return node if keep(node) else None
        children = [c for c in (rec(ch) for ch in node.children) if c]
        if not children and node.level != corpus.schema.root_level:
            return None
        return Node(
            level=node.level, children=children,
            locus=node.locus, attrs=dict(node.attrs),
        )

    return Corpus(
        schema=corpus.schema, root=rec(corpus.root), meta=dict(corpus.meta)
    )
