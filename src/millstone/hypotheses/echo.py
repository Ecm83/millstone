"""Colisiones verbatim entre líneas: ¿cita, eco o azar combinatorio?

FINDINGS reporta n-gramas de palabras repetidos en líneas distintas:
n=2→2.389, n=3→155, n=4→uno solo (`ol shedy qokedy qokeedy`,
f75v.47 / f84r.22), n=5→cero. El conteo crudo no basta — falta el
nulo: ¿cuántas colisiones produce el azar con el mismo vocabulario,
las mismas longitudes de línea y orden libre (consistente con
`free-word-order`)?

- Si el real SUPERA al nulo: orden no aleatorio, hay eco fijo
  (citas, frases repetidas, plantillas de línea).
- Si cae POR DEBAJO: el generador evita repeticiones verbatim — cada
  línea es celda fresca (compatible con matriz/catálogo).
- Si coincide con el nulo: la colisión única es ruido combinatorio.
"""

from __future__ import annotations

import random
from collections import Counter
from statistics import mean, pstdev

from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def _collisions(
    lines: list[tuple[str, ...]], n: int
) -> dict[tuple[str, ...], set[int]]:
    """n-gramas verbatim que aparecen en 2+ líneas distintas."""
    seen: dict[tuple[str, ...], set[int]] = {}
    for li, words in enumerate(lines):
        for i in range(len(words) - n + 1):
            ng = tuple(words[i : i + n])
            seen.setdefault(ng, set()).add(li)
    return {g: ls for g, ls in seen.items() if len(ls) >= 2}


def _window(words: tuple[str, ...], start: int, n: int) -> tuple[str, ...]:
    """Contexto ±1 alrededor del n-grama que empieza en `start`."""
    lo = max(0, start - 1)
    hi = min(len(words), start + n + 1)
    return words[lo:hi]


class VerbatimEcho:
    name = "verbatim-echo"
    statement = (
        "Las colisiones verbatim entre líneas (n=2..5) se desvían del "
        "nulo combinatorio intra-línea: hay eco estructurado (exceso) o "
        "supresión de repeticiones (defecto)."
    )

    def __init__(self, replicates: int = 25, seed: int = 0):
        self.replicates = replicates
        self.seed = seed

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        levels = corpus.schema.levels
        if "line" not in levels or "word" not in levels:
            return [
                Evidence(
                    "niveles line/word disponibles", None,
                    "schema sin líneas",
                )
            ]
        view = MemoryCorpusView(corpus)
        line_seqs = list(view.unit_sequences("line", "word"))
        lines = [s.symbols for s in line_seqs]
        loci = [s.locus for s in line_seqs]
        if len(lines) < 100:
            return [
                Evidence("corpus suficiente", None, f"{len(lines)} líneas")
            ]

        rng = random.Random(self.seed)
        ns = (2, 3, 4, 5)
        real = {n: _collisions(lines, n) for n in ns}
        null: dict[int, list[int]] = {n: [] for n in ns}
        for _ in range(self.replicates):
            sh = [tuple(rng.sample(w, len(w))) for w in lines]
            for n in ns:
                null[n].append(len(_collisions(sh, n)))

        tabla = []
        max_z = 0.0
        for n in ns:
            mu, sd = mean(null[n]), pstdev(null[n]) or 1e-9
            r = len(real[n])
            z = (r - mu) / sd
            max_z = max(max_z, abs(z))
            tabla.append(
                f"n={n}: real={r} vs nulo={mu:.0f}±{sd:.0f} "
                f"[{min(null[n])}-{max(null[n])}] z={z:+.1f}"
            )

        out = [
            Evidence(
                "los conteos verbatim se desvían del nulo combinatorio "
                "(|z| > 2 en algún n)",
                max_z > 2,
                " | ".join(tabla),
            )
        ]

        # Contexto de la colisión única n=4: ¿los dos loci comparten
        # vecinos (eco más largo) o es verbatim aislado (coincidencia)?
        if real[4]:
            detalles = []
            shared = 0
            for g, idxs in real[4].items():
                spots = sorted(idxs)
                wins = []
                for li in spots:
                    words = lines[li]
                    i = next(
                        k for k in range(len(words) - 3)
                        if tuple(words[k : k + 4]) == g
                    )
                    wins.append(_window(words, i, 4))
                    detalles.append(
                        f"{' '.join(g)} @ {loci[li]}: "
                        f"«{' '.join(wins[-1])}»"
                    )
                if len(wins) >= 2:
                    extra = [
                        set(w) - set(g) for w in wins
                    ]
                    shared = len(set.intersection(*extra)) \
                        if all(extra) else 0
            out.append(
                Evidence(
                    "la colisión n=4 comparte contexto en ambos loci "
                    "(eco más largo que el propio n-grama)",
                    shared > 0 if real[4] else None,
                    f"{shared} vecinos compartidos | " + " | ".join(detalles),
                )
            )

            # ¿Mismo escriba/quire/lengua? Un eco intra-folio o intra-mano
            # es más trivial que una cita entre folios distantes.
            folio_attrs = {f.locus: f.attrs for f in corpus.nodes("folio")}
            for g, idxs in real[4].items():
                attrs = [
                    folio_attrs.get((loci[li] or "").split(".", 1)[0], {})
                    for li in sorted(idxs)
                ]
                if len(attrs) >= 2:
                    coincide = [
                        f"{k}={attrs[0].get(k)}"
                        for k in ("Q", "L", "H")
                        if len({a.get(k) for a in attrs}) == 1
                    ]
                    detalle = (
                        "loci: "
                        + ", ".join(loci[li] for li in sorted(idxs))
                        + f" | atributos compartidos: "
                        + (", ".join(coincide) if coincide else "ninguno")
                    )
                    out.append(
                        Evidence(
                            "la colisión es intra-mano/quire (eco local "
                            "de escriba, no cita global)",
                            bool(coincide),
                            detalle,
                        )
                    )
        return out
