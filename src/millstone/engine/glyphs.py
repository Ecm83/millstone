"""Nivel glifo: los símbolos del manuscrito, no las letras EVA.

EVA escribe una ligadura del manuscrito con varias letras (`ch`, `sh`,
`cth`, `ckh`, `cph`, `cfh` = los "bancos"). A nivel letra, el engine
descubrió que c siempre precede a h — artefacto ortográfico. A nivel
glifo esas ligaduras son UN solo símbolo y las reglas desaparecen.

`GlyphView` envuelve cualquier CorpusView: aplica maximal-munch sobre las
secuencias para que el análisis corra sobre glifos reales.
"""

from __future__ import annotations

import re
from typing import Iterator

from millstone.engine.view import CorpusView, Sequence

# bancos EVA: c + [t k p f]? + h ; y sh. Más largo primero.
_BENCH = re.compile(r"c[tkpf]?h|sh")


def to_glyphs(symbols: tuple[str, ...]) -> tuple[str, ...]:
    """Letras EVA -> glifos (bancos fusionados en un solo símbolo)."""
    text = "".join(symbols)
    parts = _BENCH.split(text)
    out: list[str] = []
    pos = 0
    for m in _BENCH.finditer(text):
        out.extend(text[pos : m.start()])
        out.append(m.group(0))
        pos = m.end()
    out.extend(text[pos:])
    return tuple(p for p in out if p)


class GlyphView:
    """CorpusView que expone glifos (bancos EVA fusionados)."""

    def __init__(self, inner: CorpusView):
        self.inner = inner

    def levels(self) -> tuple[str, ...]:
        return self.inner.levels()

    def sequences(self, level: str) -> Iterator[Sequence]:
        for s in self.inner.sequences(level):
            yield Sequence(locus=s.locus, symbols=to_glyphs(s.symbols))
