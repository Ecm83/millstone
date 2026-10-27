from pathlib import Path

import pytest

from millstone.ingest.rongorongo import parse_dir
from millstone.engine.view import MemoryCorpusView

DATA = Path("data/raw/rongorongo")


@pytest.mark.skipif(not DATA.exists(), reason="corpus rongorongo no descargado")
def test_rongo_corpus_stats():
    corpus = parse_dir(DATA)
    assert corpus.validate() == []
    assert sum(1 for _ in corpus.nodes("tablet")) == 6
    assert sum(1 for _ in corpus.nodes("glyph")) == 5460


@pytest.mark.skipif(not DATA.exists(), reason="corpus rongorongo no descargado")
def test_rongo_verbatim_echo_is_real():
    # medido: ecos de glifos entre lineas muy por encima del nulo -
    # estructura de refranes, no inventario administrativo
    from millstone.hypotheses.echo import _collisions

    corpus = parse_dir(DATA)
    view = MemoryCorpusView(corpus)
    seqs = list(view.sequences("line"))
    lines = [s.symbols for s in seqs]
    loci = [s.locus for s in seqs]
    n4 = _collisions(lines, 4)
    assert len(n4) >= 60  # medido: 65 vs ~2 del nulo
    # ecos cortos que cruzan tablillas distintas (fórmulas viajeras)
    cross = [
        g for g, ls in n4.items()
        if len({loci[i][0] for i in ls}) > 1
    ]
    assert len(cross) >= 5  # medido: 6


@pytest.mark.skipif(not DATA.exists(), reason="corpus rongorongo no descargado")
def test_rongo_glyph001_runs():
    # el glifo 001 casi no mezcla: los forbids dominantes lo involucran
    from millstone.engine.discover import discover

    corpus = parse_dir(DATA)
    v = MemoryCorpusView(corpus)
    ds = discover(v, "line", min_support=10)
    top = [d for d in ds[:30]]
    assert any("001" in str(d.constraint) for d in top)
