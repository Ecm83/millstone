"""Léxico cerrado: el vocabulario es un conjunto seleccionado, no generado.

El FSA posicional inducido del corpus acepta astronómicamente más formas de
las atestiguadas. Si el lenguaje del modelo excede el vocabulario por
órdenes de magnitud, las palabras se *eligen* de un inventario finito —
lectura tipo código/inventario, no gramática productiva libre.
"""

from __future__ import annotations

import math

from millstone.engine.induce import induce, language_size
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


class ClosedLexicon:
    name = "closed-lexicon"
    statement = (
        "El vocabulario es un léxico cerrado: el modelo posicional inducido "
        "sobre-genera por órdenes de magnitud -> las palabras son un "
        "inventario seleccionado, no producidas libremente."
    )

    def __init__(self, max_len: int = 14):
        self.max_len = max_len

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        vocab = {s.symbols for s in view.sequences("word") if s.symbols}
        if len(vocab) < 100:
            return [Evidence("vocabulario suficiente", None, f"{len(vocab)}")]

        lang_seq = language_size(induce(view, "word"), self.max_len)
        lang_pos = language_size(
            induce(view, "word", positional=True), self.max_len
        )
        n = len(vocab)
        return [
            Evidence(
                "el modelo secuencial sobre-genera el vocabulario",
                lang_seq > 100 * n,
                f"|lenguaje bigrama| = {lang_seq:.2e} vs vocab {n} "
                f"-> ratio {lang_seq/n:.0e}x",
            ),
            Evidence(
                "el modelo posicional sigue sobre-generando (léxico cerrado)",
                lang_pos > 100 * n,
                f"|lenguaje slots| = {lang_pos:.2e} vs vocab {n} "
                f"-> ratio {lang_pos/n:.0e}x; "
                f"log2: {math.log2(lang_pos/n):.0f} bits de selección por tipo",
            ),
        ]
