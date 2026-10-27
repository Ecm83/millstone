"""Runner de la batería pre-registrada (`battery.yaml`).

`run_battery(lines)` consume el vector congelado: métricas a N fijo
(bootstrap por bloques) + rasgos contra nulo. Devuelve el vector
estandarizado por eje — la entrada del panel comparativo.
"""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import millstone.engine.metrics as M

BATTERY_YAML = Path(__file__).resolve().parents[3] / "battery.yaml"


def battery_hash() -> str:
    return hashlib.sha256(BATTERY_YAML.read_bytes()).hexdigest()[:12]


def run_battery(
    lines, n_tokens: int = 10000, reps: int = 20, seed: int = 0
) -> dict | None:
    """Vector completo sobre `lines` (lista de listas de tokens)."""
    fn = M.fixed_n_metrics(lines, n_tokens, reps=reps, seed=seed)
    if fn is None:
        return None
    rng = random.Random(seed)
    words = [w for l in lines for w in l]
    types = sorted(set(words))

    # timm: bigrama inducido en la mitad, cobertura en la otra
    bi = set()
    for l in lines[: len(lines) // 2]:
        for w in l:
            s = ("^",) + tuple(w) + ("$",)
            bi |= set(zip(s, s[1:]))
    testw = set(w for l in lines[len(lines) // 2 :] for w in l)
    timm = sum(1 for w in testw if M._accepts(bi, w)) / max(len(testw), 1)

    od_r, od_n = M.out_degree_ratio(lines, rng)
    rm_r, rm_n = M.repeat_mass(lines, rng)
    fam_r, fam_n = M.families_rate(types, rng)
    ez = M.echo_z(lines, rng, ns=(2, 3), reps=10)

    return {
        "hapax": fn["hapax"].mean,
        "ttr": fn["ttr"].mean,
        "heaps_beta": fn["heaps"].mean,
        "new1k": fn["new1k"].mean,
        "timm": timm,
        "families": fam_r / max(fam_n, 1e-9),
        "outdeg": od_r / max(od_n, 1e-9),
        "mi": M.adjacent_mi(lines),
        "repmass": rm_r / max(rm_n, 1e-9),
        "echo_z2": ez[2],
        "echo_z3": ez[3],
        "hash": battery_hash(),
    }
