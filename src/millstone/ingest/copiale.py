"""Copiale: cifrado homofónico descifrado (Knight, Megyesi, Schaefer 2011).

El manuscrito es un stream de ~90 códigos-cifra sin espacios de palabra —
no existe nivel `word`: symbol → line → page → corpus. El alemán
descifrado (`parse_plain`) es el ground truth del mismo documento: un
corpus de lengua natural cuya versión cifrada podemos comparar con los
indescifrados.

Formato de la transcripción (su.se): líneas de documento separadas por
línea en blanco; `##` comenta y `## PAGE n` marca página; `#` marca
catchwords (previews al pie, no texto); `?` lecturas inciertas;
`*code*` logogramas (un símbolo cada uno).
"""

from __future__ import annotations

from pathlib import Path

from millstone.ingest import plaintext
from millstone.model import Corpus, CorpusSchema, Node

CIPHER_SCHEMA = CorpusSchema(("symbol", "line", "page", "corpus"))


def parse_cipher(path: str | Path) -> Corpus:
    """Transcripción Copiale → symbol→line→page→corpus."""
    pages: list[Node] = []
    cur_lines: list[Node] = []
    buf: list[Node] = []
    page_no = 0

    def flush_line() -> None:
        nonlocal buf
        if buf:
            cur_lines.append(
                Node(
                    level="line",
                    locus=f"p{page_no}.l{len(cur_lines) + 1}",
                    children=buf,
                )
            )
            buf = []

    def flush_page() -> None:
        nonlocal cur_lines
        flush_line()
        if cur_lines:
            pages.append(
                Node(level="page", locus=f"p{page_no}", children=cur_lines)
            )
            cur_lines = []

    for raw in Path(path).read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        line = raw.strip()
        if line.startswith("##"):
            if line.upper().startswith("## PAGE"):
                flush_page()
                page_no += 1
            continue
        if not line:
            flush_line()
            continue
        for tok in line.split():
            if not tok.startswith("#"):
                buf.append(Node(level="symbol", value=tok))
    flush_page()
    return Corpus(
        schema=CIPHER_SCHEMA,
        root=Node(level="corpus", locus="copiale", children=pages),
        meta={"source": "copiale-cipher"},
    )


def parse_plain(path: str | Path) -> Corpus:
    """El alemán descifrado: mismo documento como lengua natural."""
    text = "\n".join(
        raw
        for raw in Path(path)
        .read_text(encoding="utf-8", errors="replace")
        .splitlines()
        if not raw.strip().startswith("##")
    )
    corpus = plaintext.parse(text)
    corpus.meta["source"] = "copiale-german"
    return corpus
