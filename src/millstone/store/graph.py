"""Persistencia del corpus en Neo4j.

`node_rows`/`edge_rows` convierten el árbol en filas planas (id estable por
ruta: `corpus/herbal/f1r/p0/f1r.5/f1r.5.w3`), y `write` las vuelca con
UNWIND+MERGE — todo testeable sin base de datos. `record_constraint`
registra una restricción y sus violaciones enlazadas a los nodos `Word`
por locus — la evidencia vive en el grafo.

Neo4j almacena y explora; NO razona. El driver `neo4j` es opcional.
"""

from __future__ import annotations

import re
from typing import Iterator

from millstone.engine.check import CheckResult
from millstone.model import Corpus, Node

_LABEL = re.compile(r"[^A-Za-z]")


def _label(level: str) -> str:
    return _LABEL.sub("", level).capitalize() or "Node"


def node_rows(root: Node) -> Iterator[dict]:
    """Filas {id, level, locus, value, idx, props} por preorden."""
    def rec(node: Node, path: str, idx: int) -> Iterator[dict]:
        seg = node.locus or str(idx)
        nid = f"{path}/{seg}" if path else (node.locus or node.level)
        yield {
            "id": nid,
            "level": node.level,
            "locus": node.locus,
            "value": node.value,
            "idx": idx,
            "props": node.attrs,
        }
        for i, child in enumerate(node.children):
            yield from rec(child, nid, i)

    yield from rec(root, "", 0)


def edge_rows(root: Node) -> Iterator[tuple[str, str]]:
    """Pares (id_padre, id_hijo) con la misma construcción de ids."""
    def rec(node: Node, path: str, idx: int) -> Iterator[tuple[str, str]]:
        seg = node.locus or str(idx)
        nid = f"{path}/{seg}" if path else (node.locus or node.level)
        for i, child in enumerate(node.children):
            cseg = child.locus or str(i)
            yield nid, f"{nid}/{cseg}"
            yield from rec(child, nid, i)

    yield from rec(root, "", 0)


def write(driver, corpus: Corpus, batch: int = 5000) -> int:
    """Vuelca el árbol a Neo4j. Devuelve nº de nodos escritos."""
    rows = list(node_rows(corpus.root))
    with driver.session() as s:
        # metadatos del schema
        s.run(
            "MERGE (c:CorpusMeta {id: $id}) SET c.levels = $levels",
            id=corpus.root.locus or "corpus",
            levels=list(corpus.schema.levels),
        )
        for level in corpus.schema.levels:
            level_rows = [r for r in rows if r["level"] == level]
            query = (
                f"UNWIND $rows AS r MERGE (n:{_label(level)} {{id: r.id}}) "
                "SET n.level=r.level, n.locus=r.locus, n.value=r.value, "
                "n.idx=r.idx, n += r.props"
            )
            for i in range(0, len(level_rows), batch):
                s.run(query, rows=level_rows[i : i + batch])
        edges = list(edge_rows(corpus.root))
        for i in range(0, len(edges), batch):
            s.run(
                "UNWIND $edges AS e MATCH (p {id: e[0]}), (c {id: e[1]}) "
                "MERGE (p)-[:CONTAINS]->(c)",
                edges=edges[i : i + batch],
            )
    return len(rows)


def record_constraint(driver, result: CheckResult) -> None:
    """(:Constraint) -[:VIOLATED_AT]-> (:Word) por locus — evidencia viva."""
    with driver.session() as s:
        s.run(
            "MERGE (c:Constraint {dsl: $dsl}) "
            "SET c.level=$level, c.checked=$checked, c.violations=$v",
            dsl=repr(result.constraint),
            level=result.level,
            checked=result.checked,
            v=len(result.violations),
        )
        s.run(
            "UNWIND $loci AS loc "
            "MATCH (c:Constraint {dsl: $dsl}), (w:Word {locus: loc}) "
            "MERGE (c)-[:VIOLATED_AT]->(w)",
            dsl=repr(result.constraint),
            loci=[v.locus for v in result.violations if v.locus],
        )
