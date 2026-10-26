"""Inducción de gramática: el FSA de primer orden que el corpus implica.

Estados = símbolo previo (bigrama). start="^", finals = símbolos vistos al
final de palabra. La `RegularGrammar` resultante tiene `accepts` y
`sample_word` gratis — la misma clase con la que calibramos el engine
cierra el círculo: ahora el corpus produce la gramática.
"""

from __future__ import annotations

from collections import Counter

from millstone.engine.view import CorpusView
from millstone.ingest.synthetic import RegularGrammar, Transition

START = "^"


def induce(
    view: CorpusView, level: str = "word", positional: bool = False
) -> RegularGrammar:
    """FSA inducido del corpus.

    `positional=False`: estado = último símbolo (bigramario).
    `positional=True`: estado = (posición, último símbolo) — un modelo de
    slots: lo permitido depende de *dónde* estás en la palabra.
    """
    trans: dict[tuple, int] = Counter()
    finals: set = set()
    for seq in view.sequences(level):
        w = seq.symbols
        if not w:
            continue
        prev = (0, START) if positional else START
        for i, ch in enumerate(w):
            dst = (i + 1, ch) if positional else ch
            trans[(prev, ch)] += 1
            prev = dst
        finals.add(prev)
    return RegularGrammar(
        start=(0, START) if positional else START,
        finals=frozenset(finals),
        transitions=tuple(
            Transition(src=a, symbol=b, dst=d, weight=n)
            for (a, b), (d, n) in _with_dst(trans, positional)
        ),
    )


def _with_dst(trans: dict[tuple, int], positional: bool):
    """Reconstruye el destino: (src,sym)->sym, o (src,sym)->(pos+1,sym)."""
    for (src, sym), n in trans.items():
        dst = (src[0] + 1, sym) if positional else sym
        yield (src, sym), (dst, n)


def language_size(grammar: RegularGrammar, max_len: int = 14) -> int:
    """Número de palabras aceptadas de longitud <= max_len (DP de caminos)."""
    from collections import defaultdict

    adj: dict = defaultdict(list)
    for t in grammar.transitions:
        adj[t.src].append(t.dst)
    counts = {grammar.start: 1}
    total = 0
    for _ in range(max_len):
        nxt: dict = defaultdict(int)
        for st, n in counts.items():
            for dst in adj.get(st, ()):
                nxt[dst] += n
        counts = nxt
        total += sum(n for st, n in counts.items() if st in grammar.finals)
    return total
