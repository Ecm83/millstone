"""Generador de corpus sintéticos desde una gramática regular conocida.

Sirve para calibrar el engine: si la gramática generadora dice "toda q va
seguida de o", el motor debe recuperar esa frontera. La gramática es un
autómata finito ponderado — subsume gramáticas de slots como caso particular.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from millstone.model import Corpus, CorpusSchema, Node

DEFAULT_SCHEMA = CorpusSchema(("symbol", "word", "line", "corpus"))


@dataclass(frozen=True)
class Transition:
    src: str
    symbol: str
    dst: str
    weight: float = 1.0


@dataclass(frozen=True)
class RegularGrammar:
    """AFND ponderado: estados implícitos en las transiciones."""

    start: str
    finals: frozenset[str]
    transitions: tuple[Transition, ...]

    def out_edges(self, state: str) -> list[Transition]:
        return [t for t in self.transitions if t.src == state]

    def accepts(self, word: str) -> bool:
        """Aceptación por conjuntos de estados (semántica AFND)."""
        states = {self.start}
        for ch in word:
            states = {
                t.dst
                for t in self.transitions
                if t.src in states and t.symbol == ch
            }
            if not states:
                return False
        return bool(states & self.finals)

    def sample_word(
        self, rng: random.Random, max_len: int = 32, retries: int = 100
    ) -> str:
        """Random walk ponderado. Nunca devuelve la palabra vacía."""
        for _ in range(retries):
            state, word = self.start, []
            while len(word) < max_len:
                edges = self.out_edges(state)
                if not edges or (word and state in self.finals):
                    break
                edge = rng.choices(edges, weights=[e.weight for e in edges])[0]
                state, word = edge.dst, word + [edge.symbol]
            if word and state in self.finals:
                return "".join(word)
        raise RuntimeError("la gramática no produce palabras finitas")


def generate(
    grammar: RegularGrammar,
    n_words: int = 200,
    words_per_line: tuple[int, int] = (4, 10),
    schema: CorpusSchema = DEFAULT_SCHEMA,
    seed: int | None = None,
) -> Corpus:
    """Genera un Corpus agrupando palabras muestreadas en líneas."""
    rng = random.Random(seed)
    if schema.levels != DEFAULT_SCHEMA.levels:
        raise NotImplementedError("generate() solo soporta el schema por defecto")

    lines: list[Node] = []
    produced = 0
    while produced < n_words:
        n = min(rng.randint(*words_per_line), n_words - produced)
        words = [
            Node(
                level="word",
                locus=f"s.L{len(lines) + 1}.W{i + 1}",
                children=[
                    Node(level="symbol", value=ch)
                    for ch in grammar.sample_word(rng)
                ],
            )
            for i in range(n)
        ]
        lines.append(Node(level="line", locus=f"s.L{len(lines) + 1}", children=words))
        produced += n

    return Corpus(
        schema=schema,
        root=Node(level="corpus", children=lines),
        meta={"source": "synthetic", "grammar": repr(grammar)},
    )


# ---- generadores de negativos para la batería (devuelven líneas) ----


def markov_lines(words, n_lines, lens, order: int = 1, seed: int = 0):
    """Cadena de Markov sobre símbolos: genera formas de palabra libres
    sin plantilla fija (negativo "combinatorio barato")."""
    import random
    from collections import defaultdict

    rng = random.Random(seed)
    trans = defaultdict(lambda: defaultdict(int))
    starts = []
    for w in words:
        w = tuple(w)
        hist = ("^",) * order
        starts.append(w[:order])
        for ch in w + ("$",):
            trans[hist][ch] += 1
            hist = tuple((hist + (ch,))[1:])
    def gen():
        hist = ("^",) * order
        w = []
        for _ in range(30):
            nxt = trans.get(hist)
            if not nxt:
                break
            ch = rng.choices(list(nxt), weights=list(nxt.values()))[0]
            if ch == "$":
                break
            w.append(ch)
            hist = tuple((hist + (ch,))[1:])
        return tuple(w) if w else ("x",)
    join = (lambda w: "".join(w)) if all(isinstance(w, str) for w in words) else (lambda w: w)
    return [tuple(join(gen()) for _ in range(L))
            for L in rng.choices(lens, k=n_lines)]


def autocite_lines(words, n_lines, lens, p_copy=0.15, p_mut=0.08, K=16,
                   seed: int = 0):
    """Generador de autocita (Timm): copia reciente + muta a 1 edición."""
    import random
    from millstone.engine.generative import _mutate

    rng = random.Random(seed)
    vocab = list(set(words))
    uni = {w: words.count(w) for w in vocab}
    out = []
    for L in rng.choices(lens, k=n_lines):
        line = []
        for _ in range(L):
            r = rng.random()
            rec = line[-K:]
            if rec and r < p_copy:
                line.append(rng.choice(rec))
            elif rec and r < p_copy + p_mut:
                m = _mutate(rng.choice(rec), rng, uni)
                line.append("".join(m) if isinstance(rec[0], str) else m)
            else:
                line.append(rng.choices(vocab, weights=[uni[w] for w in vocab])[0])
        out.append(tuple(line))
    return out


def recode_as_codebook(lines, seed: int = 0):
    """Recodifica palabra->entrada opaca: cada tipo se vuelve un código
    atómico. Misma estadística de token, estructura interna borrada —
    el codebook perfecto conocido."""
    import random
    rng = random.Random(seed)
    types = list({w for l in lines for w in l})
    rng.shuffle(types)
    code = {w: f"E{i:05d}" for i, w in enumerate(types)}
    return [tuple(code[w] for w in l) for l in lines]
