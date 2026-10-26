import math

from millstone.engine.constraints import (
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    NextInSet,
    OnlyInPosition,
    StartsWith,
)
from millstone.engine.discover import discover
from millstone.engine.mdl import (
    constraint_cost,
    data_cost,
    entails,
    model_cost,
    prune,
)
from millstone.engine.view import MemoryCorpusView
from millstone.ingest.synthetic import generate

from test_synthetic import q_o_grammar

ALPHA8 = 8


def view(n_words=1000, seed=7):
    return MemoryCorpusView(generate(q_o_grammar(), n_words=n_words, seed=seed))


def test_constraint_costs():
    # FollowedBy(q,o): tag + 2 símbolos; StartsWith: tag + vector indicador
    assert constraint_cost(FollowedBy("q", "o"), ALPHA8) == math.log2(8) + 6
    assert constraint_cost(StartsWith(frozenset({"q"})), ALPHA8) == math.log2(8) + 8


def test_model_cost_sums():
    cs = [FollowedBy("q", "o"), EndsWith(frozenset({"n", "y"}))]
    assert model_cost(cs, ALPHA8) == sum(constraint_cost(c, ALPHA8) for c in cs)


def test_entails_position_implies_bigrams():
    assert entails(OnlyInPosition("n", -1), ForbidsBigram(("n", "a")))
    assert entails(OnlyInPosition("n", -1), ForbidsBigram(("n", "n")))
    assert not entails(OnlyInPosition("n", -1), ForbidsBigram(("a", "n")))
    assert entails(OnlyInPosition("q", 0), ForbidsBigram(("a", "q")))
    assert not entails(OnlyInPosition("q", 0), ForbidsBigram(("q", "a")))


def test_entails_followed_by_implies_bigrams():
    assert entails(FollowedBy("q", "o"), ForbidsBigram(("q", "a")))
    assert not entails(FollowedBy("q", "o"), ForbidsBigram(("q", "o")))
    assert not entails(FollowedBy("q", "o"), ForbidsBigram(("a", "q")))


def test_data_cost_compression():
    v = view()
    alpha = frozenset("aeoktqyn")
    free = data_cost(v, "word", [], alpha)
    constrained = data_cost(
        v, "word",
        [FollowedBy("q", "o"), EndsWith(frozenset({"n", "y"})),
         OnlyInPosition("n", -1), OnlyInPosition("y", -1)],
        alpha,
    )
    # las restricciones predicen posiciones: codificar cuesta menos
    assert constrained < free


def test_prune_recovers_exact_basis():
    # los candidatos colapsan a las reglas reales de la gramática
    v = view()
    result = prune(v, "word", discover(v, "word"))
    basis = {d.constraint for d in result.basis}
    # la regla q->o en una de sus dos formas equivalentes
    assert basis & {FollowedBy("q", "o"), NextInSet("q", frozenset({"o"}))}
    assert EndsWith(frozenset({"n", "y"})) in basis
    assert OnlyInPosition("n", -1) in basis
    assert OnlyInPosition("y", -1) in basis
    # todos los bigramas prohibidos eran entrañados: ninguno sobrevive
    assert not any(isinstance(c, ForbidsBigram) for c in basis)
    # y nada inexacto entra en la base
    assert all(d.violations == 0 for d in result.basis)


def test_pruned_loses_zero_predictive_power():
    # podar no cambia el coste de datos frente al conjunto exacto completo
    v = view()
    alpha = frozenset("aeoktqyn")
    ds = discover(v, "word")
    exact_full = [d.constraint for d in ds if d.violations == 0]
    result = prune(v, "word", ds)
    pruned = [d.constraint for d in result.basis]
    assert data_cost(v, "word", pruned, alpha) == data_cost(
        v, "word", exact_full, alpha
    )
    assert result.model_bits < model_cost(exact_full, len(alpha))
