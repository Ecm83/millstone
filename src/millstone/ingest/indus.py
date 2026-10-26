"""Ingest del corpus de la escritura del Indo (Indus script).

Fuente: corpus ICIT/Mahadevan en CSV (columna `text` con secuencias de
signos numerados `+AAA-BBB-CCC+`, columna `dir.` con dirección de
lectura). Los sellos se leen R/L en su mayoría; el CSV guarda orden
físico — esta capa lo normaliza a orden de lectura.

Niveles: `symbol -> inscription -> corpus`. Cada inscripción es una
"palabra" para el engine — las reglas son posicionales sobre signos.
"""

from __future__ import annotations

import csv
from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

INDUS_SCHEMA = CorpusSchema(levels=("symbol", "inscription", "corpus"))


def parse_file(path, normalize_direction: bool = True) -> Corpus:
    """Parsea el CSV ICIT a un Corpus.

    `normalize_direction`: invierte las inscripciones R/L para que todas
    las secuencias estén en orden de lectura real. Sin esto, el signo
    terminal (jar) aparece primero y las reglas posicionales se
    invierten.
    """
    children = []
    for row in csv.DictReader(open(path, encoding="utf-8")):
        raw = (row.get("text") or "").strip().strip("+")
        signs = [s for s in raw.split("-") if s.strip().isdigit()]
        if len(signs) < 2:
            continue
        if normalize_direction and row.get("dir.", "").strip().upper() == "R/L":
            signs = signs[::-1]
        children.append(Node(
            level="inscription", locus=row.get("id", "?"),
            attrs={"site": row.get("site", ""), "dir": row.get("dir.", "")},
            children=[Node(level="symbol", value=s) for s in signs],
        ))
    return Corpus(
        schema=INDUS_SCHEMA,
        root=Node(level="corpus", children=children),
        meta={"source": str(path), "name": "indus-icit"},
    )
