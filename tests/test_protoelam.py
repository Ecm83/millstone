from pathlib import Path

import pytest

from millstone.ingest.protoelam import parse, parse_file
from millstone.engine.view import MemoryCorpusView

DATA = Path("data/raw/protoelamite.atf")

SAMPLE = """&P008001 = MDP 06, 201
#atf: lang qpc
@tablet
@obverse
1. M157# ,
# header
2. M319 M032 , 1(N14) 7(N01)#
3. M321~j# , 1(N01)
$ n lines broken
4'. |M106+M288|# x , 5(N14)
@reverse
1. M288 , 3(N01)
&P008002 = MDP 06, 202
#atf: lang qpc
@tablet
@obverse
1. M036 M288 , 2(N01)
"""


def test_parse_structure():
    corpus = parse(SAMPLE)
    assert corpus.validate() == []
    docs = list(corpus.nodes("doc"))
    assert len(docs) == 2
    assert docs[0].locus == "P008001"


def test_cluster_kinds():
    corpus = parse(SAMPLE)
    kinds = [w.attrs.get("kind") for w in corpus.nodes("word")]
    # M157 solo (header sin coma->signs), linea 2: signs+nums, ...
    assert kinds.count("nums") >= 4
    assert "signs" in kinds


def test_numeral_becomes_sign_with_count():
    corpus = parse(SAMPLE)
    n01 = [s for w in corpus.nodes("word") for s in w.children
           if w.attrs.get("kind") == "nums"]
    values = {s.value for s in n01}
    assert "N01" in values and "N14" in values
    seven = next(s for s in n01 if s.attrs.get("n") == "7")
    assert seven.value == "N01"


def test_compound_and_uncertainty():
    corpus = parse(SAMPLE)
    signs = {s.value: s for w in corpus.nodes("word") for s in w.children}
    assert "M106+M288" in signs  # compuesto |A+B| atomico
    assert "x" in signs          # ilegible
    assert signs["M321~j"].attrs.get("damaged") == "1"


@pytest.mark.skipif(not DATA.exists(), reason="corpus proto-elamita no descargado")
def test_real_corpus_stats():
    corpus = parse_file(DATA)
    assert corpus.validate() == []
    assert sum(1 for _ in corpus.nodes("doc")) > 1300
    assert sum(1 for _ in corpus.nodes("sign")) > 30000


@pytest.mark.skipif(not DATA.exists(), reason="corpus proto-elamita no descargado")
def test_real_corpus_signature():
    # medido: firma administrativa - lexico cerrado, sin eco, sin flujo
    from millstone.hypotheses.echo import VerbatimEcho
    from millstone.hypotheses.lexicon import ClosedLexicon

    corpus = parse_file(DATA)
    assert all(e.supported for e in ClosedLexicon().evaluate(corpus))
    echo = VerbatimEcho().evaluate(corpus)
    assert echo[0].supported is False  # colisiones en el nulo
