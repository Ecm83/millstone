"""¿Los espacios inciertos `,` son cortes de palabra o continuaciones?

Mill por diferencia: compara la distribución de pares de símbolos alrededor
de cada tipo de frontera con los bigramas internos de palabra.

- Si `,` se parece a interno → los transcritores dudaban, pero no hay corte.
- Si `,` se parece a `.` → es un espacio real con glifo dudoso al margen.
"""

from __future__ import annotations

from collections import Counter

from millstone.hypotheses.core import Evidence
from millstone.model import Corpus


def boundary_pairs(corpus: Corpus):
    """Tres perfiles de pares (último de w_i, primero de w_{i+1}).

    Devuelve (ciertos, inciertos, internos) — internos = bigramas dentro de
    palabra (el perfil "no hay corte").
    """
    certain: Counter = Counter()
    uncertain: Counter = Counter()
    internal: Counter = Counter()
    for line in corpus.nodes("line"):
        words = line.children
        for i, w in enumerate(words):
            syms = [s.value for s in w.leaves() if s.value]
            if not syms:
                continue
            internal.update(zip(syms, syms[1:]))
            if i + 1 < len(words):
                nxt = [s.value for s in words[i + 1].leaves() if s.value]
                if not nxt:
                    continue
                pair = (syms[-1], nxt[0])
                if words[i + 1].attrs.get("space") == "uncertain":
                    uncertain[pair] += 1
                else:
                    certain[pair] += 1
    return certain, uncertain, internal


class UncertainSpace:
    name = "uncertain-space"
    statement = (
        "Los espacios inciertos `,` son en su mayoría cortes de palabra "
        "reales: su distribución de pares se parece a `.`, no a bigramas "
        "internos — con una subpoblación continuadora (l/r/o elevados)."
    )

    def evaluate(self, corpus: Corpus) -> list[Evidence]:
        certain, uncertain, internal = boundary_pairs(corpus)
        tot_u = sum(uncertain.values())
        if tot_u < 50:
            return [Evidence("suficientes espacios inciertos", None, f"{tot_u}")]

        def first_profile(cnt):
            p: Counter = Counter()
            for (a, _), n in cnt.items():
                p[a] += n
            t = sum(p.values())
            return {k: v / t for k, v in p.items()}

        def tv(p, q):
            return 0.5 * sum(
                abs(p.get(s, 0) - q.get(s, 0)) for s in set(p) | set(q)
            )

        pc, pu, pi = (
            first_profile(certain),
            first_profile(uncertain),
            first_profile(internal),
        )
        tv_bound = tv(pu, pc)
        tv_intern = tv(pu, pi)

        top = ", ".join(
            f"'{a}{b}'({n})" for (a, b), n in uncertain.most_common(8)
        )
        return [
            Evidence(
                "los `,` se distribuyen como cortes de palabra, "
                "no como continuaciones",
                tv_bound < tv_intern,
                f"TV(`,`, `.`)={tv_bound:.3f} < "
                f"TV(`,`, interno)={tv_intern:.3f}",
            ),
            Evidence(
                "perfil de los espacios inciertos",
                None,
                f"{tot_u} casos | top pares: {top} | "
                f"primer símbolo: `,` mezcla final({sum(pu.get(s,0) for s in 'ynrls'):.0%}) "
                f"con elevación interna en l/r/o",
            ),
        ]
