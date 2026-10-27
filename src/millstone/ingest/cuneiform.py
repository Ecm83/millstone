"""Adaptador CDLI ATF cuneiforme (sux) → modelo de corpus.

Fuente: `data/raw/cuneiform.atf` — subconjunto `lang sux` del volcado
CDLI (cdli-gh/data, CC-BY-4.0). Sumerio, corpus *descifrado*: control
de clase "lengua natural + administración" frente a los indescifrados.

Formato de línea ATF:

    N. palabra palabra          1. x e2-nig2 ansze sze gu7

- Los signos dentro de una palabra van separados por `-`
  (`e2-nig2` = e2 + nig2). Numerales `k(disz)`/`k(u)`/`k(barig)` →
  signo N-normalizado con attr `n`. Determinantes `{d}` → prefijo `{d}`
  en el valor. `x` = ilegible, `[...]`/`[x]` = roto → `?`, `!`/`?` →
  attrs. `@column` se ignora (face obverse/reverse sí se guarda).

Schema: sign → word → line → doc → corpus.
"""

from __future__ import annotations

import re
from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

CUNEIFORM_SCHEMA = CorpusSchema(
    ("sign", "word", "line", "doc", "corpus")
)

_TEXT_TAG = re.compile(r"^&?P?(\d+) = (.*)")
_LINE_NO = re.compile(r"^(\d+)'?\.")
_NUMERAL = re.compile(r"^(\w+)\((\w+)\)$")


def _sign(raw: str) -> Node | None:
    """Componente de palabra (post-split por '-') → nodo sign."""
    attrs: dict[str, str] = {}
    tok = raw
    if "#" in tok:
        attrs["damaged"] = "1"
    if "!" in tok or "?" in tok:
        attrs["doubtful"] = "1"
    tok = tok.replace("#", "").replace("!", "").replace("?", "")
    if set(tok) <= {".", "[", "]"} or not tok:
        return Node(level="sign", value="?", attrs={"broken": "1"})
    tok = tok.strip("[]<>(),")
    if not tok:
        return None
    if m := _NUMERAL.match(raw):
        attrs["n"] = m.group(1)
        tok = m.group(2)
    return Node(level="sign", value=tok, attrs=attrs)


def parse(text: str) -> Corpus:
    docs: list[Node] = []
    doc = None
    face = ""
    line_no = 0

    def flush() -> None:
        nonlocal doc
        if doc is not None and doc.children:
            docs.append(doc)
        doc = None

    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if m := _TEXT_TAG.match(raw):
            flush()
            doc = Node(level="doc", locus=f"P{m.group(1)}",
                       attrs={"pub": m.group(2).strip()})
            face, line_no = "", 0
            continue
        if doc is None:
            continue
        if raw.startswith("@"):
            part = raw[1:].split()[0]
            if part in ("obverse", "reverse"):
                face = part[0]
            continue
        if raw.startswith(("$", "#", ">>")) or not _LINE_NO.match(raw):
            continue
        content = _LINE_NO.sub("", raw).strip()
        line_no += 1
        words = []
        for wtok in content.split():
            signs = [s for s in (_sign(p) for p in wtok.split("-")) if s]
            if signs:
                words.append(
                    Node(level="word",
                         locus=f"{doc.locus}.{line_no}.w{len(words)+1}",
                         children=signs)
                )
        if words:
            doc.children.append(
                Node(level="line",
                     locus=f"{doc.locus}.{face}.{line_no}",
                     attrs={"face": face},
                     children=words)
            )
    flush()
    return Corpus(schema=CUNEIFORM_SCHEMA,
                  root=Node(level="corpus", children=docs))


def parse_file(path: str | Path) -> Corpus:
    with open(path, encoding="utf-8") as f:
        return parse(f.read())
