"""Tests del corpus de Lineal A (Navarre-AI corpus.json)."""

from pathlib import Path

import pytest

LA = Path("data/raw/linear_a.json")


@pytest.mark.skipif(not LA.exists(), reason="corpus Lineal A no descargado")
def test_lineara_ingest():
    from millstone.ingest.lineara import parse_file

    c = parse_file(LA)
    assert c.validate() == []
    assert len(c.root.children) > 1500


@pytest.mark.skipif(not LA.exists(), reason="corpus Lineal A no descargado")
def test_lineara_is_accounting():
    # 40% de tokens contienen numeros egeos -> firma contable
    from millstone.engine.view import MemoryCorpusView
    from millstone.ingest.lineara import parse_file

    v = MemoryCorpusView(parse_file(LA))
    words = list(v.sequences("word"))
    num = sum(
        1 for s in words if any(x.startswith("U+101") for x in s.symbols)
    )
    assert num / len(words) > 0.3
