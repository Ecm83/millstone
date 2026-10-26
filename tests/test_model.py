from millstone.model import Corpus, CorpusSchema, Node


def leaf(level: str, value: str) -> Node:
    return Node(level=level, value=value)


def tiny_corpus() -> Corpus:
    schema = CorpusSchema(("sym", "tok", "line", "corpus"))
    line = Node(
        level="line",
        locus="f1r.1",
        children=[
            Node(level="tok", children=[leaf("sym", "a"), leaf("sym", "b")]),
            Node(level="tok", children=[leaf("sym", "c")]),
        ],
    )
    return Corpus(schema=schema, root=Node(level="corpus", children=[line]))


def test_schema_requires_two_levels():
    try:
        CorpusSchema(("solo",))
    except ValueError:
        return
    raise AssertionError("schema de un nivel no debería ser válido")


def test_schema_rejects_duplicate_levels():
    try:
        CorpusSchema(("a", "a", "corpus"))
    except ValueError:
        return
    raise AssertionError("niveles duplicados no deberían ser válidos")


def test_level_navigation():
    schema = CorpusSchema(("sym", "tok", "line", "corpus"))
    assert schema.leaf_level == "sym"
    assert schema.root_level == "corpus"
    assert schema.parent_level("tok") == "line"
    assert schema.child_level("line") == "tok"
    assert schema.parent_level("corpus") is None


def test_valid_corpus_passes_validation():
    assert tiny_corpus().validate() == []


def test_token_and_node_iteration():
    corpus = tiny_corpus()
    assert list(corpus.tokens()) == ["a", "b", "c"]
    assert [n.locus for n in corpus.nodes("line")] == ["f1r.1"]
    assert sum(1 for _ in corpus.nodes("tok")) == 2


def test_skipped_level_is_an_error():
    schema = CorpusSchema(("sym", "tok", "corpus"))
    # símbolo directamente bajo la raíz, saltándose "tok"
    corpus = Corpus(schema=schema, root=Node(level="corpus", children=[leaf("sym", "x")]))
    assert corpus.validate()


def test_empty_container_is_an_error():
    schema = CorpusSchema(("sym", "tok", "corpus"))
    corpus = Corpus(
        schema=schema,
        root=Node(level="corpus", children=[Node(level="tok")]),
    )
    assert corpus.validate()
