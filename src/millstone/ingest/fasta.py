"""FASTA → corpus: secuencias biológicas como dominio no-lingüístico.

El test de agnosticidad del motor: símbolo→line→sequence→corpus, donde
`line` es cada fila del fichero (~60-80 bases, análogo a una línea de
manuscrito) y `sequence` cada entrada `>`. Codones no se modelan — el
motor debe ver la estructura solo desde adyacencia de símbolos.
"""

from __future__ import annotations

from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

FASTA_SCHEMA = CorpusSchema(("symbol", "line", "sequence", "corpus"))


def parse_file(path: str | Path) -> Corpus:
    seqs: list[Node] = []
    lines: list[Node] = []
    seq_name = "seq0"
    n_line = 0

    def flush_seq() -> None:
        nonlocal lines
        if lines:
            seqs.append(
                Node(level="sequence", locus=seq_name, children=lines)
            )
            lines = []

    for raw in Path(path).read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        row = raw.strip()
        if row.startswith(">") or row.startswith(";"):
            flush_seq()
            seq_name = row[1:].split()[0] if row.startswith(">") else seq_name
            continue
        if not row:
            continue
        n_line += 1
        lines.append(
            Node(
                level="line",
                locus=f"{seq_name}.l{n_line}",
                children=[
                    Node(level="symbol", value=ch.upper()) for ch in row
                ],
            )
        )
    flush_seq()
    return Corpus(
        schema=FASTA_SCHEMA,
        root=Node(level="corpus", locus=Path(path).stem, children=seqs),
        meta={"source": "fasta"},
    )
