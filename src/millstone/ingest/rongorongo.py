"""Adaptador Rongorongo (RR-corpus XML) → modelo de corpus.

Fuente: `data/raw/rongorongo/*.xml` — corpus XML de phspaelti/RR-corpus
(transcripción Barthel contrastada C.E.I.P.P., CC-BY). ~5.460 glifos
en 6 tablillas (A–F), el único sistema de escritura autóctono de
Oceanía, sin descifrar.

Cada `<glyph>` lleva:
- `<code>`: código Barthel (`430`, `003a`, `022bf`...) — las variantes
  con letra se conservan; `!`/`?` = identificación dudosa → attrs;
  `_` = hueco/ilegible.
- `<link>`: cómo enlaza con el siguiente glifo (`-` secuencial, `.`,
  `*` fin de línea, `:`...) — va al attr `link`.

Schema: glyph → line → side → tablet → corpus.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

RONGO_SCHEMA = CorpusSchema(
    ("glyph", "line", "side", "tablet", "corpus")
)

_MARK = re.compile(r"[!?]+$")


def _glyph(el: ET.Element) -> Node | None:
    code = (el.findtext("code") or "").strip()
    if not code:
        return None
    attrs: dict[str, str] = {}
    if m := _MARK.search(code):
        attrs["uncertain"] = "1" if "!" in m.group(0) else "2"
        code = _MARK.sub("", code)
    if code == "_":
        attrs["broken"] = "1"
    link = (el.findtext("link") or "").strip()
    if link:
        attrs["link"] = link
    return Node(level="glyph", value=code, attrs=attrs)


def parse_dir(path: str | Path) -> Corpus:
    tablets = []
    for xml_path in sorted(Path(path).glob("*.xml")):
        root = ET.parse(xml_path).getroot()
        tablet = Node(
            level="tablet",
            locus=root.get("id") or xml_path.stem,
            attrs={"name": root.findtext("tablet-name") or ""},
        )
        for side_el in root.iter("side"):
            side = Node(
                level="side",
                locus=side_el.get("id") or "?",
                attrs={"name": side_el.findtext("side-name") or ""},
            )
            for line_el in side_el.iter("line"):
                glyphs = [
                    g for g in (_glyph(g) for g in line_el.iter("glyph"))
                    if g is not None
                ]
                if glyphs:
                    side.children.append(
                        Node(
                            level="line",
                            locus=line_el.get("id") or "?",
                            children=glyphs,
                        )
                    )
            if side.children:
                tablet.children.append(side)
        if tablet.children:
            tablets.append(tablet)
    return Corpus(
        schema=RONGO_SCHEMA, root=Node(level="corpus", children=tablets)
    )


def parse_file(path: str) -> Corpus:
    return parse_dir(path)
