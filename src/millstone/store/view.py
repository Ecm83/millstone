"""Neo4jCorpusView: el contrato CorpusView sobre el grafo persistido.

El engine no nota la diferencia con la RAM — mismo Protocol. Requiere el
driver opcional `neo4j` (`pip install millstone[neo4j]`).

Nota: el orden de hojas bajo niveles profundos usa `idx` por padre —
exacto para word→symbol, aproximado para niveles más altos.
"""

from __future__ import annotations

import re
from typing import Iterator

from millstone.engine.view import Sequence

_LABEL = re.compile(r"[^A-Za-z]")


class Neo4jCorpusView:
    def __init__(self, driver):
        self.driver = driver

    def levels(self) -> tuple[str, ...]:
        with self.driver.session() as s:
            rec = s.run(
                "MATCH (c:CorpusMeta) RETURN c.levels AS lv LIMIT 1"
            ).single()
            return tuple(rec["lv"]) if rec else ()

    def sequences(self, level: str) -> Iterator[Sequence]:
        label = _LABEL.sub("", level).capitalize()
        cur_locus: str | None = None
        buf: list[str] = []
        with self.driver.session() as s:
            for rec in s.run(
                f"MATCH (n:{label}) "
                "OPTIONAL MATCH (n)-[:CONTAINS*]->(leaf) "
                "WHERE leaf.value IS NOT NULL "
                "RETURN n.id AS nid, n.locus AS locus, "
                "       leaf.value AS v, leaf.idx AS idx "
                "ORDER BY nid, idx"
            ):
                if rec["nid"] != cur_locus:
                    if cur_locus is not None:
                        yield Sequence(locus, tuple(buf))
                    cur_locus, locus, buf = rec["nid"], rec["locus"], []
                if rec["v"] is not None:
                    buf.append(rec["v"])
        if cur_locus is not None:
            yield Sequence(locus, tuple(buf))
