"""Modelos generativos rivales para comparación MDL (model-compare).

Tres mecanismos que compiten por explicar el corpus en igualdad de
condiciones (mismo submodelo de forma de palabra: el FSA inducido;
mismo modelo de longitud de línea: la distribución empírica; mismo
suelo de probabilidad para tipos no vistos en train):

- `LinguisticModel` (A): transiciones bigrama de palabras + backoff a
  unigrama — orden con dependencia local, tipo sintaxis suave.
- `CatalogModel` (B): sorteo i.i.d. de un léxico enumerado con sus
  frecuencias — las entradas son un inventario; paga el léxico en
  `model_bits` (cada tipo codificado bajo el FSA + sus frecuencias).
- `CombinatorialModel` (C): sorteo i.i.d. bajo P_FSA — el generador de
  slots emite palabras libres; sin léxico, pero la masa se reparte
  sobre todo el lenguaje del FSA (sobre-genera).

`data_bits(lines)` es entropía cruzada en held-out: bits para
transmitir las líneas dado el modelo. `sample_lines` permite el test
de reproducción de firmas.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass

from millstone.ingest.synthetic import RegularGrammar

# suelo de probabilidad para tipos no vistos en train - identico en los
# tres modelos (condicion de igualdad: el tipo nuevo cuesta lo mismo)
P_UNSEEN = 1e-6


def _bic(k: int, n: int) -> float:
    """Coste de parámetros libres: k·log2(n)/2 (esquema BIC uniforme)."""
    return 0.0 if k <= 0 or n <= 0 else k * math.log2(n) / 2


def fsa_prob(grammar: RegularGrammar, word) -> float:
    """P(caminar por `word`) bajo el FSA ponderado (0 si no acepta)."""
    state, p = grammar.start, 1.0
    for ch in word:
        edges = grammar.out_edges(state)
        if not edges:
            return 0.0
        edge = next((t for t in edges if t.symbol == ch), None)
        if edge is None:
            return 0.0
        p *= edge.weight / sum(t.weight for t in edges)
        state = edge.dst
    return p if state in grammar.finals else 0.0


def _len_cost(lines) -> tuple[float, dict[int, float]]:
    """Coste compartido de longitudes de línea (empírica +suavizado)."""
    counts = Counter(len(l) for l in lines)
    tot = len(lines)
    lens = {k: v / tot for k, v in counts.items()}
    bits = sum(-math.log2(max(lens.get(len(l), 1e-6), 1e-6)) for l in lines)
    return bits, lens


def _line_cost(lens: dict[int, float], lines) -> float:
    return sum(-math.log2(max(lens.get(len(l), 1e-6), 1e-6)) for l in lines)


class GenerativeModel:
    """Interfaz común: fit sobre líneas de tipos de palabra."""

    name = "?"

    def fit(self, lines: list[tuple]) -> None: ...
    def model_bits(self) -> float: ...
    def data_bits(self, lines: list[tuple]) -> float: ...
    def sample_lines(self, rng: random.Random, n: int) -> list[tuple]: ...


class LinguisticModel(GenerativeModel):
    """A: bigrama de palabras (dependencia de orden) + backoff unigrama."""

    name = "A-lingüístico"

    def __init__(self, fsa: RegularGrammar, lamb: float = 0.4):
        self.fsa = fsa
        self.lamb = lamb  # peso del backoff: p = (1-λ)·bigrama + λ·unigrama

    def fit(self, lines):
        self.uni = Counter(w for l in lines for w in l)
        self.bi = defaultdict(Counter)
        for l in lines:
            prev = None
            for w in l + (None,):
                if prev is not None:
                    self.bi[prev][w] += 1
                prev = w
        self.n_tok = sum(self.uni.values())
        self.lens_p, self.lens_list = self._len_fit(lines)
        return self

    def _len_fit(self, lines):
        c = Counter(len(l) for l in lines)
        t = len(lines)
        return {k: v / t for k, v in c.items()}, [len(l) for l in lines]

    def _p(self, w, prev):
        u = (self.uni.get(w, 0) + 1) / (self.n_tok + len(self.uni) + 1)
        if prev in self.bi:
            tot = sum(self.bi[prev].values())
            b = self.bi[prev].get(w, 0) / tot if w is not None else 0.0
        else:
            b = u if w is not None else 0.0
        if w is None:  # fin de línea
            eot = self.bi[prev].get(None, 0) if prev in self.bi else 0
            tot = sum(self.bi[prev].values()) if prev in self.bi else 1
            return max(eot / tot, 1e-6)
        return max((1 - self.lamb) * b + self.lamb * u, P_UNSEEN)

    def model_bits(self):
        trans = sum(len(v) for v in self.bi.values())
        lex_bits = sum(-math.log2(max(fsa_prob(self.fsa, w), 1e-12))
                       for w in self.uni)
        return lex_bits + _bic(trans + len(self.uni), self.n_tok)

    def data_bits(self, lines):
        bits = 0.0
        for l in lines:
            prev = None
            for w in l + (None,):
                bits += -math.log2(self._p(w, prev))
                prev = w
        return bits

    def sample_lines(self, rng, n):
        types = list(self.uni)
        wts = [self.uni[w] for w in types]
        out = []
        for L in rng.choices(self.lens_list, k=n):
            line = []
            prev = None
            for _ in range(L):
                cand = self.bi.get(prev)
                if cand and rng.random() > self.lamb:
                    tot = sum(cand.values())
                    items = [(w, c) for w, c in cand.items() if w]
                    w = rng.choices([w for w, _ in items],
                                    weights=[c for _, c in items])[0] if items \
                        else rng.choices(types, weights=wts)[0]
                else:
                    w = rng.choices(types, weights=wts)[0]
                line.append(w); prev = w
            out.append(tuple(line))
        return out


class CatalogModel(GenerativeModel):
    """B: inventario — i.i.d. sobre el léxico enumerado con frecuencias."""

    name = "B-catálogo"

    def __init__(self, fsa: RegularGrammar):
        self.fsa = fsa

    def fit(self, lines):
        self.uni = Counter(w for l in lines for w in l)
        self.n_tok = sum(self.uni.values())
        self.v = len(self.uni)
        self.lens_list = [len(l) for l in lines]
        return self

    def _p(self, w):
        return max((self.uni.get(w, 0) + 1) / (self.n_tok + self.v + 1),
                   P_UNSEEN)

    def model_bits(self):
        lex = sum(-math.log2(max(fsa_prob(self.fsa, w), 1e-12))
                  for w in self.uni)
        return lex + _bic(self.v, self.n_tok)

    def data_bits(self, lines):
        return sum(-math.log2(self._p(w)) for l in lines for w in l)

    def sample_lines(self, rng, n):
        types = list(self.uni); wts = [self.uni[w] for w in types]
        return [tuple(rng.choices(types, weights=wts, k=L))
                for L in rng.choices(self.lens_list, k=n)]


class CombinatorialModel(GenerativeModel):
    """C: generador libre — i.i.d. bajo P_FSA (sobre-genera el léxico)."""

    name = "C-combinatorio"

    def __init__(self, fsa: RegularGrammar, k_fallback: int = 8):
        self.fsa = fsa
        self.k = k_fallback  # bits de fallback para palabras no aceptadas

    def fit(self, lines):
        self.uni = Counter(w for l in lines for w in l)
        self.n_tok = sum(self.uni.values())
        self.lens_list = [len(l) for l in lines]
        # masa del FSA que cae sobre tipos observados (el resto sobre-genera)
        self.p_seen = {w: fsa_prob(self.fsa, w) for w in self.uni}
        self.m_seen = sum(self.p_seen.values())
        return self

    def _p(self, w):
        if self.m_seen <= 0:
            return P_UNSEEN
        return max(self.p_seen.get(w, 0.0) / self.m_seen, P_UNSEEN)

    def model_bits(self):
        # solo los parámetros del FSA: transiciones ponderadas
        return _bic(len(self.fsa.transitions), self.n_tok)

    def data_bits(self, lines):
        return sum(-math.log2(self._p(w)) for l in lines for w in l)

    def sample_lines(self, rng, n):
        # generación libre: el FSA emite palabras NUEVAS - es la unica
        # forma honesta de que C reproduzca hapax/tipos no vistos
        def gen_word():
            w = self.fsa.sample_word(rng)
            return tuple(w) if isinstance(w, str) else w
        out = []
        for L in rng.choices(self.lens_list, k=n):
            out.append(tuple(gen_word() for _ in range(L)))
        return out


class AutociteModel(GenerativeModel):
    """D: autocita - copia una palabra reciente (ventana K) y la muta a
    1 edicion con probabilidad p_mut, si no, sorteo del lexico.

    Es la propuesta Timm/Schinner (self-citation): explica a la vez
    eco verbatim, familias a Hamming 1, exceso de hapax y deriva por
    grano - cuatro firmas que A/B/C no capturan.
    """

    name = "D-autocita"

    def __init__(self, fsa: RegularGrammar, window: int = 16):
        self.fsa = fsa
        self.K = window

    def fit(self, lines):
        self.uni = Counter(w for l in lines for w in l)
        self.n_tok = sum(self.uni.values())
        self.v = len(self.uni)
        self.lens_list = [len(l) for l in lines]
        # estima p_copy (token identico a alguno de los ultimos K en linea)
        # y p_mut (token a distancia de edicion 1 de algun reciente)
        copies = muts = 0
        for l in lines:
            for i, w in enumerate(l):
                recent = l[max(0, i - self.K):i]
                if w in recent:
                    copies += 1
                elif any(_edit1(w, r) for r in set(recent)):
                    muts += 1
        n = max(self.n_tok - len(lines), 1)  # ignora primer token de linea
        self.p_copy = copies / n
        self.p_mut = muts / n
        self.alpha = len({s for w in self.uni for s in w})
        return self

    def _p(self, w, recent):
        lex = (self.uni.get(w, 0) + 1) / (self.n_tok + self.v + 1)
        p = (1 - self.p_copy - self.p_mut) * lex
        for r in set(recent):
            share = 1.0 / max(len(set(recent)), 1)
            if w == r:
                p += self.p_copy * share
            elif _edit1(w, r):
                p += self.p_mut * share * 0.5
        return max(p, P_UNSEEN)

    def model_bits(self):
        lex = sum(-math.log2(max(fsa_prob(self.fsa, w), 1e-12))
                  for w in self.uni)
        return lex + _bic(self.v + 2, self.n_tok)

    def data_bits(self, lines):
        bits = 0.0
        for l in lines:
            for i, w in enumerate(l):
                bits += -math.log2(self._p(w, l[max(0, i - self.K):i]))
        return bits

    def sample_lines(self, rng, n):
        types = list(self.uni); wts = [self.uni[w] for w in types]
        out = []
        for L in rng.choices(self.lens_list, k=n):
            line = []
            for _ in range(L):
                r = rng.random()
                recent = line[-self.K:]
                if recent and r < self.p_copy:
                    line.append(rng.choice(recent))
                elif recent and r < self.p_copy + self.p_mut:
                    line.append(_mutate(rng.choice(recent), rng, self.uni))
                else:
                    line.append(rng.choices(types, weights=wts)[0])
            out.append(tuple(line))
        return out


def _edit1(a, b) -> bool:
    """distancia de edicion 1 (insert/delete/substitute) entre tuplas."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    i = j = skips = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            j += 1; skips += 1
            if skips > 1:
                return False
    return True


def _mutate(word, rng, vocab):
    """una edicion aleatoria sobre `word` (sub/ins/del)."""
    sym = list(word)
    op = rng.random()
    alpha = list({s for w in vocab for s in w})
    if op < 1 / 3 and sym:
        sym[rng.randrange(len(sym))] = rng.choice(alpha)
    elif op < 2 / 3 and sym:
        del sym[rng.randrange(len(sym))]
    else:
        sym.insert(rng.randrange(len(sym) + 1), rng.choice(alpha))
    return tuple(sym)


@dataclass(frozen=True)
class ModelScore:
    name: str
    model_bits: float
    data_bits: float

    @property
    def total_bits(self) -> float:
        return self.model_bits + self.data_bits


def score(model: GenerativeModel, test_lines) -> ModelScore:
    """DL total: L(M) + L(D|M) sobre el held-out."""
    return ModelScore(
        name=model.name,
        model_bits=model.model_bits(),
        data_bits=model.data_bits(test_lines),
    )
