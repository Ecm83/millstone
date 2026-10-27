"""Métricas a N fijo con bootstrap por bloques (battery, regla 1).

Todo rasgo que depende del tamaño muestral (hapax, TTR, Heaps) se mide
sobre submuestras del MISMO número de tokens, con >=20 extracciones
bootstrap por unidad (línea/inscripción/doc — los tokens no son i.i.d.).
Resultado: media ± desviación comparable entre corpus.

Corpus que no llega a N: devuelve `None` (N insuficiente) en vez de
extrapolar.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass

from millstone.engine.generative import _edit1


def _flat(seqs, n, rng):
    """Bootstrap por bloques: re-muestrea unidades hasta >=n tokens."""
    out = []
    while len(out) < n:
        out.extend(seqs[rng.randrange(len(seqs))])
    return out[:n]


def heaps_beta(tokens) -> float:
    """Exponente de Heaps V ~ K·n^β por regresión log-log en 4 puntos."""
    n = len(tokens)
    xs, ys = [], []
    seen = set()
    for i, t in enumerate(tokens, 1):
        seen.add(t)
        if i in (n // 4, n // 2, 3 * n // 4, n):
            xs.append(math.log(i))
            ys.append(math.log(max(len(seen), 1)))
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else float("nan")


def new_per_1k(tokens) -> float:
    """Tipos nuevos por 1.000 tokens en el último cuartil."""
    n = len(tokens)
    head, tail = tokens[: 3 * n // 4], tokens[3 * n // 4 :]
    seen = set(head)
    new = sum(1 for t in tail if t not in seen and not seen.add(t))
    return new / max(len(tail), 1) * 1000


def hapax_rate(tokens) -> float:
    f = Counter(tokens)
    return sum(1 for v in f.values() if v == 1) / max(len(f), 1)


def ttr(tokens) -> float:
    return len(set(tokens)) / max(len(tokens), 1)


@dataclass(frozen=True)
class MetricResult:
    mean: float
    sd: float
    n_samples: int

    def __str__(self):
        return f"{self.mean:.4g}±{self.sd:.2g}"


def fixed_n_metrics(
    sequences,
    n_tokens: int,
    reps: int = 20,
    seed: int = 0,
) -> dict[str, MetricResult] | None:
    """Batería de apertura léxica a N fijo sobre `sequences` (lista de
    listas de tokens, p.ej. palabras por línea). `None` si no llega a N.
    """
    total = sum(len(s) for s in sequences)
    if total < n_tokens or not sequences:
        return None
    rng = random.Random(seed)
    acc = {k: [] for k in ("hapax", "ttr", "heaps", "new1k")}
    for _ in range(reps):
        toks = _flat(sequences, n_tokens, rng)
        acc["hapax"].append(hapax_rate(toks))
        acc["ttr"].append(ttr(toks))
        acc["heaps"].append(heaps_beta(toks))
        acc["new1k"].append(new_per_1k(toks))

    def ms(vals):
        m = sum(vals) / len(vals)
        sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        return MetricResult(m, sd, len(vals))

    return {k: ms(v) for k, v in acc.items()}


# ---- rasgos de la batería (sequences = lista de listas de tokens) ----


def template_coverage(train, test) -> float:
    """Fracción de palabras held-out aceptadas por el bigrama inducido
    en train (rasgo Timm a nivel forma de palabra)."""
    bigrams = set()
    for w in train:
        s = ("^",) + tuple(w) + ("$",)
        bigrams |= set(zip(s, s[1:]))
    ok = sum(
        1
        for w in test
        if all(p in bigrams for p in zip(("^",) + tuple(w) + ("$",), (tuple(w) + ("$",))))
    )
    return ok / max(len(test), 1)


def _accepts(bigrams, w) -> bool:
    s = ("^",) + tuple(w) + ("$",)
    return all(p in bigrams for p in zip(s, s[1:]))


def families_rate(types, rng, reps: int = 10) -> tuple[float, float]:
    """Fracción de tipos con vecino a edición 1; (real, media nulo)."""
    real = _fam(types)
    nulls = []
    for _ in range(reps):
        shuffled = [tuple(rng.sample(w, len(w))) for w in types]
        nulls.append(_fam(shuffled))
    return real, sum(nulls) / len(nulls)


def _fam(types) -> float:
    types = list(types)
    near = sum(
        1
        for i, w in enumerate(types)
        if any(_edit1(w, o) for o in types[i + 1 : i + 60])
    )
    return near / max(len(types), 1)


def out_degree_ratio(lines, rng, top: int = 50, reps: int = 10):
    """out-degree medio de los top-tipos / media de barajados intra-línea."""
    freq = Counter(w for l in lines for w in l)
    tops = [w for w, _ in freq.most_common(top)]

    def od(ls):
        fol = {t: set() for t in tops}
        for l in ls:
            for a, b in zip(l, l[1:]):
                if a in fol:
                    fol[a].add(b)
        return sum(len(v) for v in fol.values()) / top

    real = od(lines)
    nulls = [
        od([tuple(rng.sample(l, len(l))) for l in lines]) for _ in range(reps)
    ]
    return real, sum(nulls) / len(nulls)


def adjacent_mi(lines) -> float:
    """Información mutua media entre tokens adyacentes (bits)."""
    uni = Counter(w for l in lines for w in l)
    bi = Counter(p for l in lines for p in zip(l, l[1:]))
    n, nb = sum(uni.values()), sum(bi.values())
    mi = 0.0
    for (a, b), c in bi.items():
        p, pa, pb = c / nb, uni[a] / n, uni[b] / n
        mi += p * math.log2(p / (pa * pb))
    return mi


def echo_z(lines, rng, ns=(2, 3, 4), reps: int = 10) -> dict[int, float]:
    """z de colisiones verbatim vs barajado intra-línea (eco)."""
    from millstone.hypotheses.echo import _collisions

    out = {}
    for n in ns:
        real = len(_collisions(lines, n))
        ns_ = [
            len(_collisions([tuple(rng.sample(l, len(l))) for l in lines], n))
            for _ in range(reps)
        ]
        m = sum(ns_) / len(ns_)
        sd = max((sum((x - m) ** 2 for x in ns_) / len(ns_)) ** 0.5, 0.5)
        out[n] = (real - m) / sd
    return out


def repeat_mass(lines, rng, reps: int = 10) -> tuple[float, float]:
    """Masa de tokens en posiciones con su tipo repetido intra-línea."""
    def mass(ls):
        rep = tot = 0
        for l in ls:
            c = Counter(l)
            rep += sum(1 for t in l if c[t] > 1)
            tot += len(l)
        return rep / max(tot, 1)

    real = mass(lines)
    nulls = [
        mass([tuple(rng.sample(l, len(l))) for l in lines])
        for _ in range(reps)
    ]
    return real, sum(nulls) / len(nulls)


def first_symbol_enrichment(firsts, marginal, min_n: int = 10):
    """Max enriquecimiento del primer símbolo de unidad vs marginal."""
    tot_f, tot_m = sum(firsts.values()), sum(marginal.values())
    best, bs, bn = 0.0, None, 0
    for s, n in firsts.items():
        if n >= min_n and marginal.get(s):
            r = (n / tot_f) / (marginal[s] / tot_m)
            if r > best:
                best, bs, bn = r, s, n
    return best, bs, bn
