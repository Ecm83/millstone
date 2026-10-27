from pathlib import Path

import pytest

from millstone.ingest.protoelam import parse_file

DATA = Path("data/raw/protocuneiform.atf")


@pytest.mark.skipif(not DATA.exists(), reason="corpus proto-cuneiforme no descargado")
def test_protocuneiform_stats():
    corpus = parse_file(DATA)
    assert corpus.validate() == []
    assert sum(1 for _ in corpus.nodes("doc")) == 3000
    assert sum(1 for _ in corpus.nodes("sign")) > 40000


@pytest.mark.skipif(not DATA.exists(), reason="corpus proto-cuneiforme no descargado")
def test_protocuneiform_signature():
    # medido: misma clase administrativa que proto-elamita pero con
    # dualidad N/ideograma mas laxa (17,5% vs 4,8% mezcla interna)
    from collections import Counter

    from millstone.engine.view import MemoryCorpusView
    from millstone.hypotheses.echo import _collisions

    corpus = parse_file(DATA)
    v = MemoryCorpusView(corpus)
    lines = [s.symbols for s in v.unit_sequences("line", "word")]
    words = [w for ln in lines for w in ln]
    freq = Counter(words)
    hapax = sum(1 for n in freq.values() if n == 1) / len(freq)
    assert hapax > 0.6  # medido: 77,0%
    assert _collisions(lines, 3) == {}  # cero eco - entradas únicas
