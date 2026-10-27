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
def test_free_word_order_on_voynich():
    # medido: out-degree real/barajado = 0.93 -> orden libre
    from millstone.hypotheses.wordorder import FreeWordOrder

    evidence = FreeWordOrder().evaluate(parse_file(DATA))
    assert evidence[0].supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_paradigmatic_families_on_voynich():
    # medido: 73.7% vs 24.2% barajado
    from millstone.hypotheses.families import ParadigmaticFamilies

    evidence = ParadigmaticFamilies().evaluate(parse_file(DATA))
    assert evidence[0].supported is True


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_line_clustering_on_voynich():
    # medido: 7.2% vs 2.9% barajado -> agrupacion debil pero real
    from millstone.hypotheses.clustering import LineClustering

    evidence = LineClustering().evaluate(parse_file(DATA))
    assert evidence[0].supported is True


def test_glyph_view_merges_benches():
    from millstone.engine.glyphs import to_glyphs

    assert to_glyphs(tuple("cth")) == ("cth",)
    assert to_glyphs(tuple("shol")) == ("sh", "o", "l")
    assert to_glyphs(tuple("cphar")) == ("cph", "a", "r")
    assert to_glyphs(tuple("daiin")) == tuple("daiin")


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_glyph_level_discovery_on_voynich():
    from millstone.engine.glyphs import GlyphView
    from millstone.engine.view import MemoryCorpusView

    v = GlyphView(MemoryCorpusView(parse_file(DATA)))
    found = {str(d.constraint) for d in
             __import__("millstone.engine.discover", fromlist=["discover"]).discover(
                 v, "word", min_support=50)}
    # a nivel glifo ya no hay regla "h tras c" — eran artefacto de letra
    assert not any("PrevInSet(symbol='h'" in f for f in found)


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_flow_across_lines_refuted():
    # medido: 5.7% vs 4.9% nulo -> las lineas son celdas independientes
    from millstone.hypotheses.flow import FlowAcrossLines

    evidence = FlowAcrossLines().evaluate(parse_file(DATA))
    assert evidence[0].supported is False


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_closed_lexicon_on_voynich():
    from millstone.hypotheses.lexicon import ClosedLexicon

    evidence = ClosedLexicon().evaluate(parse_file(DATA))
    assert all(e.supported for e in evidence)


def test_holdout_replication_on_synthetic():
    # gramática real y estable: las reglas inducidas deben replicar entre
    # mitades y colapsar sobre la mitad barajada
    from millstone.hypotheses.replication import HoldoutReplication
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=2000, seed=17)
    evidence = HoldoutReplication().evaluate(corpus)
    by_pred = {e.prediction: e for e in evidence}
    assert by_pred["reglas exactas de A replican en B"].supported is True
    mill = by_pred[
        "la replicación supera al corpus barajado (Mill: diferencia)"
    ]
    assert mill.supported is True


def test_holdout_replication_tiny_corpus():
    from millstone.hypotheses.replication import HoldoutReplication
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=50, seed=1)
    evidence = HoldoutReplication().evaluate(corpus)
    assert evidence[0].supported is None


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_holdout_replication_on_voynich():
    # medido: las reglas inducidas replican out-of-sample
    from millstone.hypotheses.replication import HoldoutReplication

    evidence = HoldoutReplication().evaluate(parse_file(DATA))
    by_pred = {e.prediction: e for e in evidence}
    mill = by_pred[
        "la replicación supera al corpus barajado (Mill: diferencia)"
    ]
    assert mill.supported is True  # la gramática es real, no ruido


def test_regional_replication_on_synthetic():
    # gramática estacionaria: el split contiguo también debe replicar
    from millstone.hypotheses.replication import RegionalReplication
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=2000, seed=17)
    evidence = RegionalReplication().evaluate(corpus)
    assert all(e.supported for e in evidence)


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_regional_replication_on_voynich():
    # medido: núcleo duro estacionario (48/48 exactas) pero las casi-reglas
    # derivan entre mitades - la deriva se concentra en el contexto de 'o'
    from millstone.hypotheses.replication import RegionalReplication

    evidence = RegionalReplication().evaluate(parse_file(DATA))
    by_pred = {e.prediction: e for e in evidence}
    assert by_pred["reglas exactas de A replican en B"].supported is True
    assert by_pred["casi-reglas mantienen su frontera en B"].supported is False
    mill = by_pred[
        "la replicación supera al corpus barajado (Mill: diferencia)"
    ]
    assert mill.supported is True


def test_drift_profile_no_folio_level():
    # sin atributos $Q/$L (sintético, plaintext) -> evidencia insuficiente
    from millstone.hypotheses.drift import DriftProfile
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=500, seed=3)
    evidence = DriftProfile().evaluate(corpus)
    assert evidence[0].supported is None


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_drift_profile_on_voynich():
    # medido (por ocurrencia): la deriva es REAL - intra-lengua 34,9% vs
    # nulo 11,3% y gap Currier 19,4% vs nulo 0,9% - pero la dispersión
    # intra-lengua supera al gap A/B: textura de grano quire, no dos
    # dialectos
    from millstone.hypotheses.drift import DriftProfile

    evidence = DriftProfile().evaluate(parse_file(DATA))
    by_pred = {e.prediction: e for e in evidence}
    currier = by_pred["la deriva se alinea con el corte Currier ($L)"]
    assert currier.supported is False
    mill = by_pred[
        "el gap Currier supera al corpus barajado (Mill: diferencia)"
    ]
    assert mill.supported is True
    residual = by_pred[
        "residual gradual dentro de lengua, por encima del nulo mecánico"
    ]
    assert residual.supported is True


def test_verbatim_echo_synthetic_at_null():
    # generación independiente: las colisiones caen dentro del nulo -
    # el instrumento no inventa eco donde no lo hay
    from millstone.hypotheses.echo import VerbatimEcho
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=2000, seed=17)
    evidence = VerbatimEcho(replicates=10).evaluate(corpus)
    assert evidence[0].supported is False


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_verbatim_echo_on_voynich():
    # medido: ecos cortos inflados (z=+8.6/+20 en n<=3), la colisión n=4
    # cae en rango nulo y es intra-escriba (mismo quire M, mano 2, B)
    from millstone.hypotheses.echo import VerbatimEcho

    evidence = VerbatimEcho().evaluate(parse_file(DATA))
    by_pred = {e.prediction: e for e in evidence}
    desvio = next(e for e in evidence if "desvían" in e.prediction)
    assert desvio.supported is True
    contexto = next(e for e in evidence if "contexto" in e.prediction)
    assert contexto.supported is False  # sin eco más largo
    local = next(e for e in evidence if "intra-mano" in e.prediction)
    assert local.supported is True  # mismo quire/mano/lengua


def test_model_compare_calibrates_on_slot_corpus():
    # un corpus generado por slots debe ser ganado por C en ambos splits
    from millstone.hypotheses.modelcompare import ModelCompare
    from millstone.ingest.synthetic import generate
    from test_synthetic import q_o_grammar

    corpus = generate(q_o_grammar(), n_words=4000, seed=7)
    ev = ModelCompare().evaluate(corpus)
    assert "C-combinatorio" in ev[0].detail
    assert ev[1].supported is True  # ganador estable en contigua


@pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")
def test_model_compare_on_voynich():
    # medido: C gana DL pero ningun modelo reproduce la firma -
    # el vocabulario es una seleccion dentro del espacio generativo
    from millstone.hypotheses.modelcompare import ModelCompare

    ev = ModelCompare().evaluate(parse_file(DATA))
    assert "C-combinatorio" in ev[0].detail
    assert ev[1].supported is True
    assert ev[2].supported is False  # nadie reproduce la firma
    # la firma se descompone: ningun mecanismo gana todas las metricas
    assert ev[4].supported is False
    assert "repmass->D" in ev[4].detail
