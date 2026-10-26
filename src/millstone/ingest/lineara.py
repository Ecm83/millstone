"""Ingest del corpus de Lineal A (Navarre-AI/linear-a corpus.json).

Estructura: {doc_id: {unicode_text, type, site, ...}}. El texto usa el
bloque Unicode de Lineal A: U+106xx = signos fonéticos, U+107xx =
ideogramas/logogramas, U+101xx = números egeos. Las palabras se separan
por espacios/nuevas líneas; los signos "compuestos" (UN 1xxxx) se tratan
como símbolos atómicos — igual que los dígrafos EVA.

Niveles: `symbol → word → doc → corpus`. Los signos fonéticos puros son
un nivel de análisis; el corpus es mayoritariamente administrativo
(nodules, tablets, roundels), lo que contrasta con la lectura "texto
sagrado".
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

LINEAR_A_SCHEMA = CorpusSchema(levels=("symbol", "word", "doc", "corpus"))

# signos fonéticos (U+10600–1067F) + ideogramas (U+10740–10755, 10760–…)
_PHONETIC = re.compile(r"[\U00010600-\U0001067f]")
_LOGOGRAM = re.compile(r"[\U00010740-\U0001077f]")
_NUMERAL = re.compile(r"[\U00010100-\U0001013f]")


def word_signs(text: str) -> list[tuple[str, ...]]:
    """Texto Unicode -> secuencias de signos (por palabra).

    Cada "símbolo" es el codepoint como hex string, para análisis
    agnóstico del sistema de escritura. Se ignoran separadores y
    caracteres de formato.
    """
    words = []
    for w in re.split(r"[\s\.\-·]+", text):
        signs = tuple(
            f"U+{ord(c):04X}" for c in w
            if _PHONETIC.match(c) or _LOGOGRAM.match(c)
            or _NUMERAL.match(c)
        )
        if signs:
            words.append(signs)
    return words


def parse_file(path) -> Corpus:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    children = []
    for doc_id, doc in data.items():
        if not isinstance(doc, dict):
            continue
        text = doc.get("unicode_text") or ""
        words = word_signs(text)
        if not words:
            continue
        children.append(Node(
            level="doc", locus=doc_id,
            attrs={
                "type": doc.get("type", ""),
                "site": doc.get("site", ""),
                "linguistic": doc.get("linguistic_value", ""),
            },
            children=[
                Node(level="word", children=[
                    Node(level="symbol", value=s) for s in signs
                ])
                for signs in words
            ],
        ))
    return Corpus(
        schema=LINEAR_A_SCHEMA,
        root=Node(level="corpus", children=children),
        meta={"source": str(path), "name": "linear-a"},
    )
