"""Ingest Copiale: cifrado (symbol→line→page) y alemán descifrado."""

from millstone.ingest.copiale import parse_cipher, parse_plain
from millstone.model import surface

CIPHER_TXT = """## header comment
## PAGE 1

grr bar lam

sqi oh j

## PAGE 2

pi uh zs
"""


def test_parse_cipher_structure(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text(CIPHER_TXT, encoding="utf-8")
    c = parse_cipher(f)
    assert c.schema.levels == ("symbol", "line", "page", "corpus")
    assert c.validate() == []
    assert sum(1 for _ in c.nodes("page")) == 2
    assert sum(1 for _ in c.nodes("line")) == 3
    assert [surface(l) for l in c.nodes("line")][0] == "grrbarlam"


def test_parse_cipher_skips_catchwords(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("## PAGE 1\n\na b #catch c\n", encoding="utf-8")
    c = parse_cipher(f)
    assert surface(next(c.nodes("line"))) == "abc"


def test_parse_plain_strips_headers(tmp_path):
    f = tmp_path / "g.txt"
    f.write_text(
        "## PAGE 1\n## comment\nund der staat der dinge.\n", encoding="utf-8"
    )
    c = parse_plain(f)
    words = [surface(w) for w in c.nodes("word")]
    assert "und" in words and "page" not in words
