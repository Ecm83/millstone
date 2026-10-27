"""Replicación out-of-sample: ¿las reglas inducidas son del corpus o de la muestra?

Predicción pre-registrada: `discover` induce restricciones sobre la mitad A
(secuencias pares, intercaladas) y cada regla se evalúa sobre la mitad B
(impares), que el motor nunca vio. Si la gramática caracterizada es real:

1. las reglas exactas en A se mantienen casi exactas en B;
2. las casi-reglas mantienen su tasa de violación dentro de tolerancia
   estadística - la frontera es estable, no un artefacto de submuestreo;
3. control por diferencia de Mill: las mismas reglas aplicadas a B con los
   símbolos barajados dentro de cada secuencia deben colapsar - si
   replicaran igual, el instrumento no mediría nada.

Dos splits:

- `interleaved` (par/impar): A y B muestrean la misma mezcla de
  secciones/manos/lenguas — testea replicación de muestra.
- `contiguous` (primera/segunda mitad del documento): testea si las
  reglas sobreviven a la heterogeneidad regional — estacionariedad.
  Las reglas que no replican aquí delatan variación real entre regiones
  del corpus (p.ej. los sublenguajes Currier), no fallo del instrumento.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterator

from millstone.engine.check import check
from millstone.engine.discover import discover
from millstone.engine.view import MemoryCorpusView, Sequence
from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


@dataclass
class _HalfView:
    """CorpusView mínimo sobre las secuencias de una mitad ya filtradas."""

    all_levels: tuple[str, ...]
    level: str
    seqs: list[Sequence]

    def levels(self) -> tuple[str, ...]:
        return self.all_levels

    def sequences(self, level: str) -> Iterator[Sequence]:
        if level == self.level:
            yield from self.seqs


class HoldoutReplication:
    name = "holdout-replication"
    statement = (
        "Las restricciones inducidas sobre la mitad A del corpus son "
        "propiedades estables del lenguaje: se replican con tasa de "
        "violación similar sobre la mitad B reservada, y no sobre B "
        "barajada."
    )

    def __init__(
        self,
        strategy: str = "interleaved",
        min_support: int = 5,
        max_rules: int = 100,
        exact_tol: float = 0.02,
        sigma: float = 4.0,
        seed: int = 0,
    ):
        if strategy not in ("interleaved", "contiguous"):
            raise ValueError(f"estrategia desconocida: {strategy}")
        self.strategy = strategy
        self.min_support = min_support
        self.max_rules = max_rules
        self.exact_tol = exact_tol
        self.sigma = sigma
        self.seed = seed

    def _replicates(self, rate_a: float, rate_b: float, checked_b: int) -> bool:
        """¿La tasa observada en B es compatible con la de A?

        Regla exacta en A (rate 0): debe seguir ~exacta. Casi-regla: la
        desviación debe caber en `sigma` errores estándar binomiales.
        """
        if rate_a == 0.0:
            return rate_b <= self.exact_tol
        se = math.sqrt(rate_a * (1 - rate_a) / max(checked_b, 1))
        return abs(rate_b - rate_a) <= max(self.exact_tol, self.sigma * se)

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        view = MemoryCorpusView(corpus)
        level = (
            "word" if "word" in corpus.schema.levels
            else corpus.schema.levels[1]
        )
        seqs = list(view.sequences(level))
        if len(seqs) < 400:
            return [
                Evidence("corpus suficiente", None, f"{len(seqs)} secuencias")
            ]

        if self.strategy == "interleaved":
            a_seqs, b_seqs = seqs[0::2], seqs[1::2]
        else:
            mid = len(seqs) // 2
            a_seqs, b_seqs = seqs[:mid], seqs[mid:]
        a = _HalfView(corpus.schema.levels, level, a_seqs)
        b = _HalfView(corpus.schema.levels, level, b_seqs)

        ds = discover(a, level, min_support=self.min_support)[: self.max_rules]
        if len(ds) < 5:
            return [
                Evidence(
                    "reglas inducidas suficientes", None,
                    f"solo {len(ds)} candidatas en A",
                )
            ]

        rng = random.Random(self.seed)
        shuffled_b = _HalfView(
            corpus.schema.levels, level,
            [
                Sequence(s.locus, tuple(rng.sample(s.symbols, len(s.symbols))))
                for s in b.seqs
            ],
        )

        # Tasa de referencia en A con el mismo denominador que en B
        # (check cuenta secuencias violadoras, no ocurrencias).
        exact_rep = exact_tot = 0
        near_rep = near_tot = 0
        null_rep = 0
        worst: list[tuple[float, str]] = []

        for d in ds:
            c = d.constraint
            ra = check(a, level, c)
            rb = check(b, level, c)
            rs = check(shuffled_b, level, c)

            rep = self._replicates(ra.violation_rate, rb.violation_rate, rb.checked)
            rep_null = self._replicates(
                ra.violation_rate, rs.violation_rate, rs.checked
            )
            null_rep += rep_null

            if not ra.violations:
                exact_tot += 1
                exact_rep += rep
            else:
                near_tot += 1
                near_rep += rep
            if not rep:
                worst.append(
                    (
                        rb.violation_rate - ra.violation_rate,
                        f"{c}: {ra.violation_rate:.2%} -> {rb.violation_rate:.2%}",
                    )
                )

        out: list[Evidence] = []

        frac_exact = exact_rep / exact_tot if exact_tot else 0.0
        out.append(
            Evidence(
                "reglas exactas de A replican en B",
                frac_exact >= 0.8 if exact_tot else None,
                f"{exact_rep}/{exact_tot} reglas exactas en A con tasa "
                f"<= {self.exact_tol:.0%} en B",
            )
        )

        frac_near = near_rep / near_tot if near_tot else 0.0
        detalle_worst = "; ".join(w for _, w in sorted(worst, reverse=True)[:3])
        out.append(
            Evidence(
                "casi-reglas mantienen su frontera en B",
                frac_near >= 0.8 if near_tot else None,
                f"{near_rep}/{near_tot} dentro de tolerancia "
                f"({self.sigma:.0f} sigma)"
                + (f" | peores: {detalle_worst}" if detalle_worst else ""),
            )
        )

        total = exact_tot + near_tot
        frac_real = (exact_rep + near_rep) / total if total else 0.0
        frac_null = null_rep / total if total else 0.0
        out.append(
            Evidence(
                "la replicación supera al corpus barajado (Mill: diferencia)",
                frac_real - frac_null >= 0.3 if total else None,
                f"real={frac_real:.1%} vs barajado={frac_null:.1%} "
                f"sobre {total} reglas",
            )
        )
        return out


class RegionalReplication(HoldoutReplication):
    name = "regional-replication"
    statement = (
        "Las restricciones inducidas sobre la primera mitad del documento "
        "se mantienen en la segunda mitad: la gramática caracterizada es "
        "estacionaria entre regiones del corpus, no solo entre muestras "
        "intercaladas."
    )

    def __init__(self, **kw):
        super().__init__(strategy="contiguous", **kw)
