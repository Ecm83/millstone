"""Tests de store sin Neo4j: filas generadas + driver falso que graba."""

from millstone.model import Corpus, CorpusSchema, Node
from millstone.store.graph import (
    edge_rows,
    node_rows,
    record_constraint,
    record_grammar,
    record_hypothesis,
    write,
)
from millstone.hypotheses.core import Evidence
from millstone.engine.check import CheckResult, Violation
from millstone.engine.constraints import FollowedBy


def tiny() -> Corpus:
    schema = CorpusSchema(("sym", "word", "folio", "corpus"))
    f = Node(
        level="folio", locus="f1r", attrs={"L": "A"},
        children=[
            Node(level="word", locus="f1r.w1",
                 children=[Node(level="sym", value="q"), Node(level="sym", value="o")]),
        ],
    )
    return Corpus(schema=schema, root=Node(level="corpus", children=[f]))


def test_node_rows_stable_ids():
    rows = list(node_rows(tiny().root))
    assert [r["level"] for r in rows] == ["corpus", "folio", "word", "sym", "sym"]
    by_level = {r["level"]: r for r in rows}
    assert by_level["folio"]["id"] == "corpus/f1r"
    assert by_level["word"]["locus"] == "f1r.w1"
    # símbolos sin locus: id por ruta con índice
    syms = [r for r in rows if r["level"] == "sym"]
    assert syms[0]["id"].endswith("/0") and syms[1]["id"].endswith("/1")


def test_edge_rows_match_node_ids():
    root = tiny().root
    node_ids = {r["id"] for r in node_rows(root)}
    for parent, child in edge_rows(root):
        assert parent in node_ids and child in node_ids
    # 4 aristas en el árbol de 5 nodos
    assert sum(1 for _ in edge_rows(root)) == 4


class FakeSession:
    def __init__(self):
        self.calls = []

    def run(self, query, **params):
        self.calls.append((query, params))

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeDriver:
    def __init__(self):
        self.session_obj = FakeSession()

    def session(self):
        return self.session_obj


def test_write_emits_batched_unwinds():
    drv = FakeDriver()
    n = write(drv, tiny())
    assert n == 5
    queries = [q for q, _ in drv.session_obj.calls]
    assert any("CorpusMeta" in q for q in queries)
    assert any(":Word" in q for q in queries)
    assert any("CONTAINS" in q for q in queries)


def test_record_constraint_links_violations():
    drv = FakeDriver()
    res = CheckResult(constraint=FollowedBy("q", "o"), level="word", checked=10)
    res.violations.append(Violation(locus="f1r.w1", sequence=("q", "e")))
    record_constraint(drv, res)
    queries = [q for q, _ in drv.session_obj.calls]
    assert any("Constraint" in q for q in queries)
    assert any("VIOLATED_AT" in q and "Word" in q for q in queries)


def test_record_grammar_links_states():
    from millstone.ingest.synthetic import RegularGrammar, Transition

    g = RegularGrammar(
        start="^",
        finals=frozenset({"o"}),
        transitions=(
            Transition(src="^", symbol="q", dst="q", weight=10),
            Transition(src="q", symbol="o", dst="o", weight=5),
        ),
    )
    drv = FakeDriver()
    ns, nt = record_grammar(drv, g, name="g")
    assert ns == 3 and nt == 2  # ^, q, o
    queries = [q for q, _ in drv.session_obj.calls]
    assert any("FSAState" in q for q in queries)
    assert any("HAS_STATE" in q for q in queries)
    assert any("TRANS" in q for q in queries)


def test_record_hypothesis_links_evidence():
    drv = FakeDriver()
    record_hypothesis(
        drv, "test-h", "afirmación",
        [Evidence("pred1", True, "det"), Evidence("pred2", False, "det2")],
    )
    queries = [q for q, _ in drv.session_obj.calls]
    assert any("Hypothesis" in q for q in queries)
    assert any("SUPPORTS" in q for q in queries)
    assert any("REFUTES" in q for q in queries)
