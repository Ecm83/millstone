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


def test_timm_on_slot_generated_corpus():
    # la gramática sintética ES de slots: cobertura held-out ~total
    from millstone.engine.view import MemoryCorpusView
    from millstone.hypotheses.timm import TimmSlots
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=1000, seed=11)
    evidence = TimmSlots().evaluate(corpus)
    coverage = next(e for e in evidence if "held-out" in e.prediction)
    assert coverage.supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_initial_effect_on_voynich():
    # efecto gallows medido: 'p' debe estar muy sobrerrepresentada
    from millstone.hypotheses.initial import InitialEffect

    evidence = InitialEffect().evaluate(parse_file(DATA))
    para = next(e for e in evidence if "paragraph" in e.prediction)
    assert para.supported is True
    assert "'p'" in para.detail


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_timm_on_voynich():
    from millstone.hypotheses.timm import TimmSlots

    evidence = TimmSlots().evaluate(parse_file(DATA))
    mill = next(e for e in evidence if "barajado" in e.prediction)
    assert mill.supported is True  # estructura combinatoria real, no ruido


def test_induced_grammar_accepts_training_data():
    # la gramática inducida del corpus sintético acepta sus palabras
    from millstone.engine.induce import induce
    from millstone.engine.view import MemoryCorpusView
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar, word_strings

    corpus = generate(q_o_grammar(), n_words=300, seed=5)
    v = MemoryCorpusView(corpus)
    g = induce(v, "word")
    assert all(g.accepts(w) for w in word_strings(corpus))
    # y rechaza lo que la gramática fuente rechaza
    assert not g.accepts("qan")


TT = Path("data/raw/IT2a-n.txt")


@pytest.mark.skipif(
    not (DATA.exists() and TT.exists()), reason="corpus ZL/TT no descargado"
)
def test_transcription_robust_qo():
    from millstone.hypotheses.transcription import TranscriptionRobust

    evidence = TranscriptionRobust().evaluate(parse_file(DATA), parse_file(TT))
    # ~90% de solape esperado: las excepciones estan en el manuscrito
    assert evidence[0].supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_uncertain_space_on_voynich():
    # medido: `,` se distribuye como corte de palabra (TV 0.385 < 0.676)
    from millstone.hypotheses.spaces import UncertainSpace

    evidence = UncertainSpace().evaluate(parse_file(DATA))
    assert evidence[0].supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_natural_language_on_voynich():
    from millstone.hypotheses.natural import NaturalLanguage

    evidence = NaturalLanguage().evaluate(parse_file(DATA))
    by_pred = {e.prediction: e for e in evidence}
    zipf = next(e for e in evidence if "Zipfiana" in e.prediction)
    funct = next(e for e in evidence if "funcionales" in e.prediction)
    assert zipf.supported is True   # cola natural
    assert funct.supported is False  # sin funcionales dominantes


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_closed_lexicon_on_voynich():
    from millstone.hypotheses.lexicon import ClosedLexicon

    evidence = ClosedLexicon().evaluate(parse_file(DATA))
    assert all(e.supported for e in evidence)
