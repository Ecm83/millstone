from pathlib import Path

import pytest

from millstone.hypotheses.currier import CurrierAB
from millstone.ingest.ivtff import parse_file
from millstone.model import Corpus, CorpusSchema, Node, subcorpus

DATA = Path("data/raw/ZL3b-n.txt")


def two_grammar_corpus() -> Corpus:
    """Dos folios con gramáticas distintas y atributo L."""
    schema = CorpusSchema(("sym", "word", "folio", "corpus"))

    def folio(fid, lang, words):
        return Node(
            level="folio", locus=fid, attrs={"L": lang},
            children=[
                Node(level="word", children=[Node(level="sym", value=c) for c in w])
                for w in words
            ],
        )

    return Corpus(schema=schema, root=Node(level="corpus", children=[
        folio("fA", "A", [("q", "o", "n"), ("a", "n")]),
        folio("fB", "B", [("x", "y"), ("x", "x", "y")]),
        folio("fC", "A", [("q", "o", "y")]),
    ]))


def test_subcorpus_filters_and_keeps_ancestors():
    corpus = two_grammar_corpus()
    a = subcorpus(corpus, "folio", lambda n: n.attrs.get("L") == "A")
    folios = [f.locus for f in a.nodes("folio")]
    assert folios == ["fA", "fC"]
    words = [w for f in a.nodes("folio") for w in f.children]
    assert len(words) == 3
    assert a.validate() == []


def test_subcorpus_empty_match_drops_containers():
    corpus = two_grammar_corpus()
    none = subcorpus(corpus, "folio", lambda n: n.attrs.get("L") == "Z")
    assert none.validate() == []  # raíz vacía
    assert sum(1 for _ in none.nodes("folio")) == 0


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_currier_ab_on_real_corpus():
    corpus = parse_file(DATA)
    evidence = CurrierAB().evaluate(corpus)
    assert evidence[0].supported is True
    # las gramáticas A/B deben diferir: esa es la predicción de Currier
    assert evidence[1].supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_qo_frontier_is_distributed():
    # refutación esperada: las excepciones de q->o no se concentran
    from millstone.hypotheses.qo import QoFrontier

    evidence = QoFrontier().evaluate(parse_file(DATA))
    by_hand = next(e for e in evidence if "mano" in e.prediction)
    assert by_hand.supported is False
