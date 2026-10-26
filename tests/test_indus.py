"""Tests del corpus de la escritura del Indo (ICIT/Mahadevan CSV)."""

from pathlib import Path

import pytest

INDUS = Path("data/raw/indus.csv")


@pytest.mark.skipif(not INDUS.exists(), reason="corpus Indo no descargado")
def test_indus_ingest():
    from millstone.ingest.indus import parse_file

    c = parse_file(INDUS)
    assert c.validate() == []
    assert len(c.root.children) > 4000


@pytest.mark.skipif(not INDUS.exists(), reason="corpus Indo no descargado")
def test_indus_jar_is_terminal():
    # en orden de lectura el signo 740 (jar) va al final ~2/3
    from millstone.engine.view import MemoryCorpusView
    from millstone.ingest.indus import parse_file

    v = MemoryCorpusView(parse_file(INDUS))
    last = tot = 0
    for s in v.sequences("inscription"):
        if "740" in s.symbols:
            tot += 1
            if s.symbols[-1] == "740":
                last += 1
    assert last / tot > 0.5
