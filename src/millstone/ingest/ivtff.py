"""Adaptador IVTFF → modelo de corpus (transcripciones Voynich).

Parsea ficheros IVTFF 2.0 (p.ej. Zandbergen-Landini `ZL3b-n.txt`, EVA nativo):

- `<fNN> <! $Q=.. $P=.. $L=.. $H=..>` — cabecera de folio con variables
  ($L = lenguaje Currier A/B, $H = mano). Se guardan en `folio.attrs`.
- `<fNN.n,TIPO>` — línea con locus: primer carácter de TIPO marca el tipo
  (`+` párrafo, `*` inicio, `@` etiqueta/diagrama, `=` cierre...), el resto
  es el identificador de elemento (`P0`, `Lf`, `Ri`...). Líneas consecutivas
  del mismo elemento se agrupan en un nodo `paragraph`.
- Texto EVA: `.` espacio cierto, `,` espacio incierto, `[a:b]` lecturas
  alternativas (se toma la primera), `?` glifo ilegible, `(abc)` ligadura,
  `{...}`/`@nn;`/`<!...>` comentarios, `<X>` marcas.

El nivel `section` se asigna por división de Currier aproximada sobre el
número de folio.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from millstone.model import Corpus, CorpusSchema, Node

VOYNICH_SCHEMA = CorpusSchema(
    ("symbol", "word", "line", "paragraph", "folio", "section", "corpus")
)

_HEADER = re.compile(r"^#=IVTFF\s+(\S+)\s+(\S+)")
_FOLIO_TAG = re.compile(r"^<(f\w+)>\s*(?:<!\s*([^>]*?)\s*>)?\s*$")
_LINE_TAG = re.compile(r"^<(f\w+)\.([^,>]+),([^>]+)>\s*(.*)$")
_FOLIO_NUM = re.compile(r"^f(\d+)([rv])(\d*)$")

# División de Currier (aproximada; los folios plegados f67-73/f85-86
# son "astronomical"/"cosmological" según la numeración física)
def _section(folio_id: str) -> str:
    m = _FOLIO_NUM.match(folio_id)
    if not m:
        return "other"
    n = int(m.group(1))
    if n <= 57:
        return "herbal"
    if n <= 66:
        return "astronomical"
    if n <= 73:
        return "cosmological"
    if n <= 84:
        return "biological"
    if n <= 86:
        return "cosmological"
    if n <= 102:
        return "pharmaceutical"
    return "recipes"


def _folio_sort_key(folio_id: str) -> tuple:
    m = _FOLIO_NUM.match(folio_id)
    if not m:
        return (999, folio_id)
    n, rv, sub = m.group(1), m.group(2), m.group(3)
    return (int(n), rv, int(sub or 0), folio_id)


def _vars(text: str | None) -> dict[str, str]:
    return dict(re.findall(r"\$(\w+)=(\S+)", text or ""))


def _tokens(text: str):
    """EVA → stream de ("sym", ch) / ("break", certain) / ("marker", tag)."""
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "<":
            j = text.index(">", i)
            yield ("marker", text[i : j + 1])
            i = j + 1
        elif ch == "{":
            i = text.index("}", i) + 1  # comentario inline
        elif ch == "@":
            j = text.find(";", i)
            i = n if j < 0 else j + 1  # comentario legado @nnn;
        elif ch == "[":
            j = text.index("]", i)
            alt = re.split(r"[@{]", text[i + 1 : j])[0]  # 1ª lectura
            yield from _tokens(alt.split(":", 1)[0])
            i = j + 1
        elif ch == "(":
            j = text.index(")", i)
            yield ("sym", text[i : j + 1])  # ligadura: un solo símbolo
            i = j + 1
        elif ch == ".":
            yield ("break", "certain")
            i += 1
        elif ch == ",":
            yield ("break", "uncertain")
            i += 1
        elif ch == "?":
            yield ("sym", "?")
            i += 1
        elif ch in " \t'":
            i += 1
        else:
            yield ("sym", ch)
            i += 1


def _line_node(locus: str, locus_type: str, text: str) -> Node:
    words: list[Node] = []
    symbols: list[Node] = []
    markers: list[str] = []
    pending_break = "certain"

    def close_word() -> None:
        nonlocal symbols
        if symbols:
            words.append(
                Node(
                    level="word",
                    locus=f"{locus}.w{len(words) + 1}",
                    attrs={} if pending_break == "certain"
                    else {"space": "uncertain"},
                    children=symbols,
                )
            )
            symbols = []

    for kind, val in _tokens(text):
        if kind == "sym":
            symbols.append(
                Node(level="symbol", value=val, attrs={} if val != "?"
                                                     else {"reading": "uncertain"})
            )
        elif kind == "break":
            close_word()
            pending_break = val
        else:
            markers.append(val)
    close_word()

    return Node(
        level="line",
        locus=locus,
        attrs={"locus_type": locus_type, **({"markers": ",".join(markers)} if markers else {})},
        children=words,
    )


def parse_file(path: str | Path) -> Corpus:
    meta: dict[str, str] = {}
    folios: dict[str, Node] = {}
    folio_order: list[str] = []
    # element_id -> paragraph node en construcción (por folio)
    cur: dict[str, tuple[str, Node]] = {}
    seen: dict[str, Counter] = {}
    folio_vars: dict[str, dict[str, str]] = {}

    def current_paragraph(folio: Node, element: str, locus_type: str) -> Node:
        prev = cur.get(folio.locus or "")
        if prev and prev[0] == element:
            return prev[1]
        counts = seen.setdefault(folio.locus or "", Counter())
        counts[element] += 1
        suffix = "" if counts[element] == 1 else f"~{counts[element]}"
        par = Node(
            level="paragraph",
            locus=f"{folio.locus}.{element.lower()}{suffix}",
            attrs={"element": element, "locus_type": locus_type},
        )
        folio.children.append(par)
        cur[folio.locus or ""] = (element, par)
        return par

    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if raw.startswith("#"):
            if not meta:
                m = _HEADER.match(raw)
                if m:
                    meta = {"format": f"IVTFF {m.group(2)}", "alphabet_src": m.group(1)}
            continue
        if mf := _FOLIO_TAG.match(raw):
            fid = mf.group(1)
            folio_vars[fid] = _vars(mf.group(2))
            folios.setdefault(
                fid,
                Node(
                    level="folio",
                    locus=fid,
                    attrs={"section": _section(fid), **folio_vars[fid]},
                ),
            )
            if fid not in folio_order:
                folio_order.append(fid)
            continue
        if ml := _LINE_TAG.match(raw):
            fid, line_id, locus_type, text = ml.groups()
            folio = folios.setdefault(
                fid, Node(level="folio", locus=fid, attrs={"section": _section(fid)})
            )
            if fid not in folio_order:
                folio_order.append(fid)
            element = locus_type[1:] or locus_type
            line = _line_node(f"{fid}.{line_id}", locus_type, text)
            if not line.children:
                continue  # línea solo con marcas/comentarios: sin datos
            par = current_paragraph(folio, element, locus_type)
            par.children.append(line)

    # agrupa folios por sección
    sections: dict[str, Node] = {}
    for fid in sorted(folio_order, key=_folio_sort_key):
        sec = _section(fid)
        sections.setdefault(sec, Node(level="section", locus=sec)).children.append(
            folios[fid]
        )

    return Corpus(
        schema=VOYNICH_SCHEMA,
        root=Node(
            level="corpus",
            children=list(sections.values()),
            attrs={"source": "ivtff", **meta},
        ),
        meta=meta,
    )
