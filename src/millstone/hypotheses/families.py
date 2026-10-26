"""Familias paradigmáticas: el vocabulario forma clusters a 1 edición.

Si las palabras se producen por slots, muchas difieren de otra en un solo
símbolo (daiin/daiiin, chol/chor). Nulo de Mill: mismo vocabulario con
símbolos barajados por posición dentro de cada longitud — conserva
alfabeto, longitudes y frecuencias posicionales, destruye la estructura.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def _has_neighbor1(w: str, by_len: dict[int, set[str]]) -> bool:
    """¿Existe otro tipo a distancia de Hamming 1 (misma longitud)?"""
    sibs = by_len.get(len(w), set())
    for i in range(len(w)):
        for ch in "abcdefghijklmnopqrstuvwxyz":
            if ch != w[i] and w[:i] + ch + w[i + 1 :] in sibs:
                return True
    return False


def _fraction_with_neighbors(vocab: set[str], rng=None, shuffle=False) -> float:
    by_len: dict[int, set[str]] = defaultdict(set)
    for w in vocab:
        by_len[len(w)].add(w)
    if shuffle:
        # baraja símbolos por posición dentro de cada longitud
        by_len = defaultdict(set)
        cols: dict[int, dict[int, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for w in vocab:
            for i, ch in enumerate(w):
                cols[len(w)][i].append(ch)
        for L, positions in cols.items():
            for i in positions:
                rng.shuffle(positions[i])
            for k in range(sum(1 for w in vocab if len(w) == L)):
                by_len[L].add("".join(positions[i][k] for i in sorted(positions)))
        vocab = set().union(*by_len.values()) if by_len else set()
    hit = sum(1 for w in vocab if _has_neighbor1(w, by_len))
    return hit / len(vocab) if vocab else 0.0


class ParadigmaticFamilies:
    name = "paradigmatic-families"
    statement = (
        "El vocabulario forma familias a 1 edición por encima de lo que "
        "permite el azar: las palabras son variantes de plantillas."
    )

    def __init__(self, seed: int = 0):
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        vocab = {
            "".join(s.symbols) for s in view.sequences("word") if s.symbols
        }
        if len(vocab) < 100:
            return [Evidence("vocabulario suficiente", None, f"{len(vocab)}")]

        real = _fraction_with_neighbors(vocab)
        rng = random.Random(self.seed)
        null = _fraction_with_neighbors(vocab, rng, shuffle=True)
        return [
            Evidence(
                "fracción con vecino a 1 edición > vocabulario barajado",
                real > 2 * null,
                f"real={real:.1%} vs nulo={null:.1%} "
                f"({real/null if null else float('inf'):.1f}x)",
            )
        ]
