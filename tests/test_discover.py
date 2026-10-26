from millstone.engine.check import check
from millstone.engine.constraints import (
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    OnlyInPosition,
    StartsWith,
)
from millstone.engine.discover import discover
from millstone.engine.view import MemoryCorpusView
from millstone.ingest.synthetic import generate

from test_synthetic import q_o_grammar


def view(n_words=1000, seed=7):
    return MemoryCorpusView(generate(q_o_grammar(), n_words=n_words, seed=seed))


def found(view, cls):
    return [d for d in discover(view, "word") if isinstance(d.constraint, cls)]


def test_recovers_q_o_rule():
    # LA regla de la gramática juguete: el engine debe encontrarla solo
    qs = found(view(), FollowedBy)
    assert FollowedBy("q", "o") in [d.constraint for d in qs]


def test_recovers_closure_rule():
    ends = found(view(), EndsWith)
    assert EndsWith(frozenset({"n", "y"})) in [d.constraint for d in ends]


def test_recovers_final_only_symbols():
    only = {d.constraint for d in found(view(), OnlyInPosition)}
    assert OnlyInPosition("n", -1) in only
    assert OnlyInPosition("y", -1) in only


def test_recovers_initial_set():
    starts = found(view(), StartsWith)
    # n e y nunca abren palabra en la gramática
    assert StartsWith(frozenset({"a", "e", "o", "k", "t", "q"})) in [
        d.constraint for d in starts
    ]


def test_no_false_positives():
    # "k solo va seguida de a" es falsa: el generador emite ko, ke...
    constraints = {d.constraint for d in discover(view(), "word")}
    assert FollowedBy("k", "a") not in constraints
    assert FollowedBy("a", "e") not in constraints


def test_forbidden_bigrams_are_real_gaps():
    # n/y solo cierran: ningún bigrama (n, ·) ni (y, ·) existe
    forbids = {d.constraint.pair for d in found(view(), ForbidsBigram)}
    assert ("n", "a") in forbids
    assert ("y", "k") in forbids


def test_discoveries_recheck_clean():
    # violations==0 <-> la restricción se cumple en todo el corpus
    v = view()
    for d in discover(v, "word"):
        assert check(v, "word", d.constraint).holds == (d.violations == 0), d


def test_min_support_filters_rare_symbols():
    # con un corpus minúsculo algunas reglas pueden no tener testigos
    v = view(n_words=20, seed=3)
    for d in discover(v, "word", min_support=10):
        assert d.support >= 10 or isinstance(
            d.constraint, (StartsWith, EndsWith)
        )
