"""Testbed de descifrado: parseo de mapas y re-codificación del corpus."""

from collections import Counter
from pathlib import Path

import pytest

from millstone.ingest.remap import apply_map, parse_map
from millstone.model import Corpus, CorpusSchema, Node, surface


def _corpus(words):
    schema = CorpusSchema(("symbol", "word", "line", "corpus"))
    return Corpus(
        schema=schema,
        root=Node(level="corpus", children=[
            Node(level="line", children=[
                Node(level="word", locus=f"w{i}", children=[
                    Node(level="symbol", value=ch) for ch in w
                ]) for i, w in enumerate(words)
            ])
        ]),
    )


def surfaces(corpus):
    return [surface(w) for w in corpus.nodes("word")]


def test_parse_map_comments_delete_multitarget(tmp_path):
    f = tmp_path / "m.map"
    f.write_text(
        "# comentario\n"
        "ch  s\n"
        "?   -\n"
        "x   k s\n"
        "\n",
        encoding="utf-8",
    )
    m = parse_map(f)
    assert m == {"ch": ("s",), "?": (), "x": ("k", "s")}


def test_parse_map_requires_target(tmp_path):
    f = tmp_path / "m.map"
    f.write_text("q\n", encoding="utf-8")
    with pytest.raises(ValueError, match="objetivo"):
        parse_map(f)


def test_apply_map_merges_bench():
    res = apply_map(_corpus(["chol", "qor"]), {"ch": ("s",), "q": ("k",)})
    assert surfaces(res.corpus) == ["sol", "kor"]
    assert res.coverage < 1.0  # o, l, r sin mapear


def test_apply_map_maximal_munch_prefers_long():
    c = _corpus(["cho", "co"])
    res = apply_map(c, {"ch": ("s",), "c": ("k",)})
    assert surfaces(res.corpus) == ["so", "ko"]


def test_apply_map_delete_and_multitarget():
    res = apply_map(_corpus(["a?b", "axb"]), {"?": (), "x": ("k", "s")})
    assert surfaces(res.corpus) == ["ab", "aksb"]


def test_apply_map_unmapped_counter():
    res = apply_map(_corpus(["ab", "ac"]), {"a": ("t",)})
    assert res.unmapped == Counter({"b": 1, "c": 1})
    assert res.total_leaves == 4
    assert res.coverage == 0.5


def test_apply_map_structure_preserved():
    res = apply_map(_corpus(["ab"]), {"a": ("t",)})
    assert res.corpus.validate() == []
    assert [n.locus for n in res.corpus.nodes("word")] == ["w0"]
