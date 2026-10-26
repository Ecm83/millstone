"""Smoke test del parser IVTFF contra la transcripción Zandbergen-Landini real.

Se salta si el corpus no está descargado (data/raw/ no se versiona).
"""

from pathlib import Path

import pytest

from millstone.engine.check import check
from millstone.engine.constraints import FollowedBy
from millstone.engine.view import MemoryCorpusView
from millstone.ingest.ivtff import parse_file

DATA = Path("data/raw/ZL3b-n.txt")
pytestmark = pytest.mark.skipif(not DATA.exists(), reason="corpus ZL no descargado")


@pytest.fixture(scope="module")
def corpus():
    return parse_file(DATA)


def test_corpus_scale(corpus):
    # ~38k tokens es la cifra publicada de la transcripción
    assert sum(1 for _ in corpus.nodes("word")) > 30_000
    assert sum(1 for _ in corpus.nodes("folio")) > 200
    assert sum(1 for _ in corpus.nodes("line")) > 5_000


def test_structure_is_valid(corpus):
    assert corpus.validate() == []


def test_folio_metadata(corpus):
    f1r = next(n for n in corpus.nodes("folio") if n.locus == "f1r")
    assert f1r.attrs.get("L") == "A"  # Currier language A
    assert f1r.attrs.get("H") == "1"  # mano 1
    assert f1r.attrs["section"] == "herbal"


def test_loci_present(corpus):
    assert any(w.locus == "f1r.1.w1" for w in corpus.nodes("word"))


def test_q_o_rule_is_quasi_not_exact(corpus):
    # el famoso q->o es fuerte pero con excepciones: la frontera existe
    v = MemoryCorpusView(corpus)
    result = check(v, "word", FollowedBy("q", "o"))
    assert not result.holds
    assert 0 < result.violation_rate < 0.02  # ~124/38k palabras violan
