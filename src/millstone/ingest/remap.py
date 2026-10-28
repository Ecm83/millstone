"""Re-codificación glifo→fonema: testbed de candidatos de descifrado.

A diferencia de `render` (hoja→grafemas, solo expande), el mapeo opera
sobre la secuencia de hojas con maximal-munch: una clave puede fusionar
varias hojas en un solo fonema (`ch`→`š`), mapear una hoja a varios
tokens (`x`→`k s`) o borrarla (`?`→∅). El corpus resultante pasa por el
mismo engine: restricciones y firma se re-miden en el alfabeto propuesto.

Formato del fichero de mapeo — una entrada por línea:

    <unidad fuente> <token1> [token2 ...]
    <unidad fuente> -          # borrar la unidad

`#` comenta. La fuente se casa contra la concatenación de hojas de cada
secuencia, con preferencia por la clave más larga (los bancos EVA como
`cth` ganan a `c`). `^x` ancla la clave al inicio de la unidad y `x$`
al final (asignaciones posicionales, p.ej. `m$` solo cerrando palabra).
Las unidades sin entrada pasan intactas y se cuentan
en la cobertura que devuelve `apply_map`.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from millstone.model import Corpus, Node

_DELETE = "-"


def parse_map(path: str | Path) -> dict[str, tuple[str, ...]]:
    """Lee un fichero de mapeo. Devuelve {fuente: (tokens,)}; () = borrar."""
    mapping: dict[str, tuple[str, ...]] = {}
    for n, line in enumerate(
        Path(path).read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) < 2:
            raise ValueError(
                f"{path}:{n}: entrada sin objetivo ({line!r}); usa '-' para borrar"
            )
        src, targets = fields[0], fields[1:]
        if src in mapping:
            raise ValueError(f"{path}:{n}: fuente duplicada {src!r}")
        mapping[src] = () if targets == [_DELETE] else tuple(targets)
    return mapping


def _segment(symbols: tuple[str, ...], keys: list[str]) -> list[str]:
    """Maximal-munch: claves casadas u hojas sueltas, en orden.

    Una clave puede anclarse: `^x` solo casa al inicio de la secuencia
    y `x$` solo al final — asignaciones posicionales de la literatura
    (p.ej. `m$` = valor distinto cerrando palabra). Las ancladas se
    prueban antes que la misma clave sin ancla.
    """
    out: list[str] = []
    i, n = 0, len(symbols)
    while i < n:
        hit = None
        for k in keys:
            core = k.strip("^$")
            m = len(core)
            if len(symbols[i]) > m:
                continue
            acc = ""
            for j in range(i, n):
                acc += symbols[j]
                if len(acc) > m:
                    break
                if acc == core:
                    if (k.startswith("^") and i != 0) or (
                        k.endswith("$") and j + 1 != n
                    ):
                        break
                    hit = k
                    i = j + 1
                    break
            if hit:
                break
        if hit:
            out.append(hit)
        else:
            out.append(symbols[i])
            i += 1
    return out


@dataclass(frozen=True)
class RemapResult:
    """Corpus re-codificado + cobertura del mapeo."""

    corpus: Corpus
    unmapped: Counter          # hoja fuente → ocurrencias sin entrada
    total_leaves: int = 0

    @property
    def coverage(self) -> float:
        if not self.total_leaves:
            return 1.0
        return 1.0 - sum(self.unmapped.values()) / self.total_leaves


def apply_map(
    corpus: Corpus, mapping: dict[str, tuple[str, ...]]
) -> RemapResult:
    """Corpus con hojas re-codificadas + cobertura del mapeo.

    Las claves se aplican por orden de longitud decreciente dentro de cada
    secuencia de hojas (palabra). Una unidad mapeada a `()` desaparece.
    """
    leaf = corpus.schema.leaf_level
    keys = sorted(
        mapping,
        key=lambda k: (len(k.strip("^$")), "^" in k or "$" in k),
        reverse=True,
    )
    unmapped: Counter = Counter()
    total = 0

    def rec(node: Node) -> Node:
        nonlocal total
        if node.children and all(c.level == leaf for c in node.children):
            leaves = tuple(c.value or "" for c in node.children)
            total += len(leaves)
            children: list[Node] = []
            for key in _segment(leaves, keys):
                if key in mapping:
                    children.extend(
                        Node(level=leaf, value=t) for t in mapping[key]
                    )
                else:
                    unmapped[key] += 1
                    children.append(Node(level=leaf, value=key))
            return Node(
                level=node.level, locus=node.locus,
                attrs=dict(node.attrs), children=children,
            )
        return Node(
            level=node.level, locus=node.locus, attrs=dict(node.attrs),
            children=[rec(c) for c in node.children],
        )

    mapped = Corpus(
        schema=corpus.schema, root=rec(corpus.root), meta=dict(corpus.meta)
    )
    mapped.meta["remap"] = f"{len(mapping)} reglas"
    return RemapResult(corpus=mapped, unmapped=unmapped, total_leaves=total)
