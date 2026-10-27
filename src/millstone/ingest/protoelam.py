"""Adaptador CDLI ATF proto-elamita → modelo de corpus.

Fuente: `data/raw/protoelamite.atf` — subconjunto `lang qpc` de las
publicaciones MDP del volcado CDLI (cdli-gh/data, CC-BY-4.0).
~1.384 tablillas, ~3100-2900 a.C.: el último sistema de escritura
sustancial sin descifrar del Cercano Oriente antiguo.

Formato de línea ATF:

    N. signos , numerales        2. M319 M032 , 1(N14) 7(N01)#

- Signos ideográficos: códigos `M\\d{3}` con variantes `~a`, compuestos
  `|M106+M288|` (se conservan atómicos), `x` = signo ilegible.
- Numerales `k(Nxx)`: el sistema numérico heredado de proto-cuneiforme;
  la cantidad `k` va al atributo `n` del nodo y el signo es `Nxx`.
- `[...]` = hueco roto → símbolo `?`; `#`/`?` = dañado/dudoso → attrs.
- `@obverse/@reverse/@column` → atributo `face` de la línea.

Schema: sign → word (cluster ideográfico `signs` | numérico `nums`)
→ line → doc → corpus.
"""

from __future__ import annotations

import re

from millstone.model import Corpus, CorpusSchema, Node

PROTOELAM_SCHEMA = CorpusSchema(
    ("sign", "word", "line", "doc", "corpus")
)

_TEXT_TAG = re.compile(r"^&?P?(\d+) = (.*)")
_LINE_NO = re.compile(r"^(\d+)'?\.")
_NUMERAL = re.compile(r"^(\w+)\(([^)]+)\)$")
_SUBENTRY = re.compile(r"^[a-zA-Z]\d*'?\.$")
_STRIP = "[]<>!,"


def _token(raw: str) -> Node | None:
    """Token ATF → nodo sign con attrs de certeza/cantidad.

    Devuelve None para marcadores de sub-entrada (`a.`, `b2.`...)."""
    attrs: dict[str, str] = {}
    tok = raw
    if _SUBENTRY.match(tok):
        return None
    if "#" in tok:
        attrs["damaged"] = "1"
    if "?" in tok:
        attrs["doubtful"] = "1"
    tok = tok.replace("#", "").replace("?", "")
    if set(tok) <= {".", "[", "]"}:
        return Node(level="sign", value="?", attrs={"broken": "1"})
    tok = tok.strip(_STRIP)
    if tok.startswith("|") and tok.endswith("|"):
        tok = tok[1:-1].strip(_STRIP)  # compuesto |A+B| atómico
        attrs["compound"] = "1"
    if m := _NUMERAL.match(tok):
        attrs["n"] = m.group(1)
        tok = m.group(2)
    if not tok or set(tok) <= {"."}:
        return Node(level="sign", value="?", attrs={"broken": "1"})
    return Node(level="sign", value=tok, attrs=attrs)


def parse(text: str) -> Corpus:
    """ATF proto-elamita → Corpus. Las líneas de entrada son entradas
    contables: cluster ideográfico + cluster numérico."""
    docs: list[Node] = []
    doc = None
    face = ""
    line_no = 0

    def flush_doc() -> None:
        nonlocal doc
        if doc is not None and doc.children:
            docs.append(doc)
        doc = None

    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if m := _TEXT_TAG.match(raw):
            flush_doc()
            doc = Node(level="doc", locus=f"P{m.group(1)}",
                       attrs={"pub": m.group(2).strip()})
            face, line_no = "", 0
            continue
        if doc is None:
            continue
        if raw.startswith("@"):
            part = raw[1:].split()[0]
            if part in ("obverse", "reverse"):
                face = part[0]  # o / r
            continue
        if raw.startswith(("$", "#", ">>")):
            continue  # notas estructurales, anotaciones, cross-refs
        if not _LINE_NO.match(raw):
            continue

        content = _LINE_NO.sub("", raw).strip()
        line_no += 1
        left, _, right = content.partition(" , ")
        children = []
        for kind, side in (("signs", left), ("nums", right)):
            toks = [t for t in side.split() if t]
            signs = [s for s in (_token(t) for t in toks) if s]
            if signs:
                children.append(
                    Node(level="word",
                         locus=f"{doc.locus}.{line_no}{kind[0]}",
                         attrs={"kind": kind},
                         children=signs)
                )
        if children:
            doc.children.append(
                Node(level="line",
                     locus=f"{doc.locus}.{face}.{line_no}",
                     attrs={"face": face},
                     children=children)
            )
    flush_doc()
    return Corpus(schema=PROTOELAM_SCHEMA,
                  root=Node(level="corpus", children=docs))


def parse_file(path: str) -> Corpus:
    with open(path, encoding="utf-8") as f:
        return parse(f.read())
