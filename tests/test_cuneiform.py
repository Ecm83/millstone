from pathlib import Path

import pytest

from millstone.ingest.cuneiform import parse_file

DATA = Path("data/raw/cuneiform.atf")


@pytest.mark.skipif(not DATA.exists(), reason="corpus cuneiforme no descargado")
def test_cuneiform_stats():
    corpus = parse_file(DATA)
    assert corpus.validate() == []
    assert sum(1 for _ in corpus.nodes("doc")) > 2000
    assert sum(1 for _ in corpus.nodes("word")) > 100000


@pytest.mark.skipif(not DATA.exists(), reason="corpus cuneiforme no descargado")
def test_cuneiform_is_natural_language():
    # medido: lengua real con formulas administrativas - ni inventario
    # cerrado ni prosa pura
    from collections import Counter

    from millstone.engine.view import MemoryCorpusView

    corpus = parse_file(DATA)
    words = [
        w
        for s in MemoryCorpusView(corpus).unit_sequences("line", "word")
        for w in s.symbols
    ]
    freq = Counter(words)
    hapax = sum(1 for n in freq.values() if n == 1) / len(freq)
    top10 = sum(n for _, n in freq.most_common(10)) / len(words)
    assert 0.4 < hapax < 0.8  # medido: 60,6%
    assert top10 > 0.15       # medido: 19,8% - funcionales presentes
