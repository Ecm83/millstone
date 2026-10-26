"""Re-codificación de símbolos: separa glifo de grafema.

Control experimental para el sesgo del sistema de transliteración: si un
alfabeto se escribe con dígrafos (un glifo = dos caracteres EVA), el engine
encontrará "restricciones" que son artefacto de la codificación, no
gramática. Detectarlas en un corpus sintético conocido calibra qué clase
de hallazgo es la regla `c→{h,t,k,p,f}` del Voynich.
"""

from __future__ import annotations

from millstone.model import Corpus, Node


def render(corpus: Corpus, mapping: dict[str, str]) -> Corpus:
    """Reescribe valores hoja vía mapping, expandiendo dígrafos.

    `C -> "ch"` convierte una hoja en dos: igual que EVA escribe una
    ligadura del manuscrito con varias letras. La estructura de niveles
    se conserva (los grafemas son hijos normales del padre).
    """
    leaf = corpus.schema.leaf_level

    def rec(node: Node) -> Node:
        # padre cuyos hijos son todos hojas: reescribe expandiendo
        if node.children and all(c.level == leaf for c in node.children):
            children = [
                Node(level=leaf, value=g)
                for c in node.children
                for g in (mapping.get(c.value, c.value) or "")
            ]
            return Node(
                level=node.level, locus=node.locus,
                attrs=dict(node.attrs), children=children,
            )
        return Node(
            level=node.level, locus=node.locus, attrs=dict(node.attrs),
            children=[rec(c) for c in node.children],
        )

    return Corpus(
        schema=corpus.schema, root=rec(corpus.root), meta=dict(corpus.meta)
    )
