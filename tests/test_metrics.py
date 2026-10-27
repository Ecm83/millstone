from millstone.engine.metrics import (
    adjacent_mi,
    echo_z,
    fixed_n_metrics,
    heaps_beta,
    out_degree_ratio,
    repeat_mass,
)


def test_fixed_n_rejects_small_corpus():
    assert fixed_n_metrics([("a", "b")], n_tokens=100) is None


def test_heaps_beta_range():
    # tipos que crecen linealmente -> beta ~1; saturado -> beta ~0
    assert heaps_beta([f"w{i}" for i in range(10000)]) > 0.8
    assert heaps_beta([f"w{i % 100}" for i in range(10000)]) < 0.2


def test_fixed_n_stable():
    import random

    rng = random.Random(0)
    vocab = [f"w{i}" for i in range(400)]
    seqs = [tuple(rng.choices(vocab, k=6)) for _ in range(3000)]
    m = fixed_n_metrics(seqs, 5000, reps=10, seed=1)
    assert m and 0 < m["hapax"].mean < 1 and 0 < m["heaps"].mean < 1


def test_battery_functions_on_synthetic():
    import random as r
    rng = r.Random(0)
    lines = [tuple(rng.choices("abcde", k=6)) for _ in range(60)]
    assert 0 < adjacent_mi(lines)
    real, null = out_degree_ratio(lines, rng, top=5, reps=3)
    assert real > 0 and null > 0
    ez = echo_z(lines, rng, ns=(2,), reps=3)
    assert 2 in ez
    r_, n_ = repeat_mass(lines, rng, reps=3)
    assert 0 < r_ < 1
