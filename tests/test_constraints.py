from millstone.engine.check import alphabet, check
from millstone.engine.constraints import (
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    NextInSet,
    PrevInSet,
    StartsWith,
    SymbolAt,
)
from millstone.engine.view import MemoryCorpusView
from millstone.ingest.synthetic import generate

from test_synthetic import q_o_grammar, word_strings


def view(n_words=500, seed=7):
    return MemoryCorpusView(generate(q_o_grammar(), n_words=n_words, seed=seed))


# --- unidad: semántica de cada restricción ---

def test_followed_by():
    c = FollowedBy("q", "o")
    assert c.holds(("q", "o", "n"))
    assert not c.holds(("q", "a", "n"))
    assert not c.holds(("a", "q"))      # trigger en posición final
    assert c.holds(("a", "n"))          # sin trigger: no viola


def test_starts_ends_with():
    assert StartsWith(frozenset({"q", "k"})).holds(("q", "o"))
    assert not StartsWith(frozenset({"q"})).holds(("k",))
    assert not StartsWith(frozenset({"q"})).holds(())
    assert EndsWith(frozenset({"n", "y"})).holds(("a", "y"))
    assert not EndsWith(frozenset({"n"})).holds(("a", "y"))


def test_forbids_bigram():
    c = ForbidsBigram(("k", "t"))
    assert c.holds(("k", "a", "t"))
    assert not c.holds(("a", "k", "t"))


def test_symbol_at():
    assert SymbolAt(0, frozenset({"q"})).holds(("q", "o"))
    assert not SymbolAt(0, frozenset({"q"})).holds(("k", "o"))
    assert SymbolAt(-1, frozenset({"n"})).holds(("a", "n"))
    assert SymbolAt(5, frozenset({"q"})).holds(("a",))  # slot ausente no viola


def test_next_prev_in_set():
    n = NextInSet("c", frozenset({"h", "t"}))
    assert n.holds(("c", "h")) and n.holds(("c", "t"))
    assert not n.holds(("c", "o"))
    assert not n.holds(("a", "c"))       # trigger al final viola
    p = PrevInSet("h", frozenset({"c", "s"}))
    assert p.holds(("c", "h")) and p.holds(("s", "h"))
    assert not p.holds(("o", "h"))
    assert not p.holds(("h",))          # h inicial viola


# --- frontera: los negativos de cada regla violan la regla ---

def test_negatives_actually_violate():
    alpha = frozenset("aeoktnq")
    for c in (
        FollowedBy("q", "o"),
        StartsWith(frozenset({"q"})),
        EndsWith(frozenset({"n"})),
        ForbidsBigram(("k", "t")),
        SymbolAt(0, frozenset({"q"})),
        NextInSet("c", frozenset({"h"})),
        PrevInSet("h", frozenset({"c"})),
    ):
        negs = list(c.negatives(alpha))
        assert negs, f"{c} no genera negativos"
        assert all(not c.holds(n) for n in negs)


# --- calibración end-to-end sobre corpus sintético ---

def test_known_constraint_holds_on_corpus():
    v = view()
    result = check(v, "word", FollowedBy("q", "o"))
    assert result.checked == 500
    assert result.holds
    assert result.violation_rate == 0.0


def test_closure_constraint_holds_on_corpus():
    result = check(view(), "word", EndsWith(frozenset({"n", "y"})))
    assert result.holds


def test_false_constraint_finds_violations():
    # "k solo va seguida de a" es falsa: el generador emite ko, ke, etc.
    result = check(view(), "word", FollowedBy("k", "a"))
    assert not result.holds
    assert 0.0 < result.violation_rate < 1.0
    assert all(v.locus for v in result.violations)  # evidencia enlazada


def test_alphabet_matches_generator():
    v = view()
    assert alphabet(v) <= frozenset("aeoktqyn")
