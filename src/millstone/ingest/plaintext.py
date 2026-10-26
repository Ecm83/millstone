"""Adaptador de texto plano → modelo de corpus.

Cualquier lengua con ortografía alfabética: texto → oraciones → palabras →
símbolos (caracteres Unicode). Sirve para calibrar el engine contra
restricciones reales conocidas — p.ej. en inglés toda `q` va seguida de `u`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from millstone.model import Corpus, CorpusSchema, Node

PLAINTEXT_SCHEMA = CorpusSchema(("symbol", "word", "sentence", "corpus"))

_SENT_SPLIT = re.compile(r"[.!?;:\n]+")
_WORD = re.compile(r"\S+")


def parse(
    text: str,
    *,
    lowercase: bool = True,
    keep: Callable[[str], bool] = str.isalpha,
    schema: CorpusSchema = PLAINTEXT_SCHEMA,
) -> Corpus:
    """Tokeniza texto en el árbol symbol→word→sentence→corpus.

    `keep` filtra símbolos (por defecto solo letras); `lowercase` normaliza.
    """
    if schema != PLAINTEXT_SCHEMA:
        raise NotImplementedError("parse() solo soporta PLAINTEXT_SCHEMA")

    sentences: list[Node] = []
    for raw in _SENT_SPLIT.split(text):
        words: list[Node] = []
        for m in _WORD.finditer(raw):
            w = m.group(0)
            if lowercase:
                w = w.lower()
            symbols = [Node(level="symbol", value=ch) for ch in w if keep(ch)]
            if symbols:
                words.append(
                    Node(
                        level="word",
                        locus=f"s{len(sentences) + 1}.w{len(words) + 1}",
                        children=symbols,
                    )
                )
        if words:
            sentences.append(
                Node(level="sentence", locus=f"s{len(sentences) + 1}", children=words)
            )

    return Corpus(
        schema=schema,
        root=Node(level="corpus", children=sentences),
        meta={"source": "plaintext"},
    )


def parse_file(path: str | Path, **kwargs) -> Corpus:
    return parse(Path(path).read_text(encoding="utf-8"), **kwargs)
