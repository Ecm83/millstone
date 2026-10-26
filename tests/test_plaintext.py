from millstone.engine.constraints import FollowedBy
from millstone.engine.discover import discover
from millstone.engine.view import MemoryCorpusView
from millstone.ingest.plaintext import parse

ENGLISH_QU = (
    "The quick brown fox is quite quirky. A quiet queen quizzes a quaint "
    "quote. Frequent requests require quick sequential checks! "
    "Squads squeeze liquid equipment. "
) * 4  # ~40 palabras, q siempre seguida de u

SPANISH = "El niño rápido comió queso. ¿Quién quiere más?"


def word_strings(corpus):
    return [
        "".join(s.value for s in w.children) for w in corpus.nodes("word")
    ]


def test_parse_builds_valid_corpus():
    corpus = parse(ENGLISH_QU)
    assert corpus.validate() == []
    assert corpus.meta["source"] == "plaintext"


def test_counts_and_loci():
    corpus = parse("Hola mundo. Adios mundo!")
    assert sum(1 for _ in corpus.nodes("sentence")) == 2
    assert sum(1 for _ in corpus.nodes("word")) == 4
    assert [w.locus for w in corpus.nodes("word")] == [
        "s1.w1", "s1.w2", "s2.w1", "s2.w2",
    ]


def test_lowercase_and_symbol_filter():
    corpus = parse("ABC-123 x9y!")
    assert word_strings(corpus) == ["abc", "xy"]


def test_empty_text():
    corpus = parse("   \n  ")
    assert corpus.validate() == []
    assert sum(1 for _ in corpus.nodes("word")) == 0


def test_calibration_discovers_english_qu():
    # restricción real de lengua conocida: en inglés q siempre va seguida de u
    view = MemoryCorpusView(parse(ENGLISH_QU))
    found = {d.constraint for d in discover(view, "word", min_support=3)}
    assert FollowedBy("q", "u") in found


def test_spanish_unicode():
    corpus = parse(SPANISH)
    words = word_strings(corpus)
    assert "niño" in words and "quién" in words
    view = MemoryCorpusView(corpus)
    found = {d.constraint for d in discover(view, "word", min_support=1)}
    # el español también tiene q→u (qu)
    assert FollowedBy("q", "u") in found
