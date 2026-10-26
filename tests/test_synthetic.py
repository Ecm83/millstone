import random

from millstone.ingest.synthetic import (
    RegularGrammar,
    Transition,
    generate,
)


def q_o_grammar() -> RegularGrammar:
    """Restricción conocida a priori: 'q' solo puede ir seguida de 'o'.

    Además toda palabra termina en 'n' o 'y'. Es la versión juguete de las
    reglas fonotácticas que el engine tendrá que recuperar del Voynich.
    """
    states = {"S", "B", "Q", "F"}
    core = [("a", "B"), ("e", "B"), ("o", "B"), ("k", "B"), ("t", "B")]
    transitions = [
        *(Transition(src=s, symbol=sym, dst=dst) for s in ("S", "B") for sym, dst in core),
        *(Transition(src=s, symbol="q", dst="Q") for s in ("S", "B")),
        Transition(src="Q", symbol="o", dst="B"),
        Transition(src="B", symbol="n", dst="F", weight=2.0),
        Transition(src="B", symbol="y", dst="F", weight=2.0),
    ]
    assert {t.src for t in transitions} | {t.dst for t in transitions} <= states
    return RegularGrammar(start="S", finals=frozenset({"F"}), transitions=tuple(transitions))


def word_strings(corpus):
    """Reconstruye las palabras como strings desde los nodos symbol."""
    return [
        "".join(sym.value for sym in word.children)
        for word in corpus.nodes("word")
    ]


def test_accepts_positive_and_negative():
    g = q_o_grammar()
    assert g.accepts("qon")
    assert g.accepts("kaoy")    # n/y son cierre: nada puede seguirlas
    assert not g.accepts("kanoy")  # símbolo después del cierre
    assert not g.accepts("qan")   # q no seguida de o
    assert g.accepts("kon")       # palabra positiva sin q
    assert not g.accepts("ka")    # sin cierre n/y
    assert not g.accepts("")      # vacía no aceptada
    assert not g.accepts("q")     # q sin cierre


def test_generated_corpus_is_valid():
    corpus = generate(q_o_grammar(), n_words=200, seed=7)
    assert corpus.validate() == []


def test_generated_words_respect_known_grammar():
    corpus = generate(q_o_grammar(), n_words=500, seed=7)
    words = word_strings(corpus)
    assert len(words) == 500
    for w in words:
        # propiedad conocida a priori: q -> o, cierre en n/y
        for i, ch in enumerate(w):
            if ch == "q":
                assert i + 1 < len(w) and w[i + 1] == "o"
        assert w[-1] in ("n", "y")
        assert q_o_grammar().accepts(w)


def test_generate_is_deterministic_with_seed():
    a = generate(q_o_grammar(), n_words=50, seed=42)
    b = generate(q_o_grammar(), n_words=50, seed=42)
    assert word_strings(a) == word_strings(b)


def test_words_per_line_bounds():
    corpus = generate(q_o_grammar(), n_words=100, words_per_line=(3, 5), seed=1)
    sizes = [len(line.children) for line in corpus.nodes("line")]
    assert all(3 <= s <= 5 for s in sizes)
