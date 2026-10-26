# Corpus sintético — oráculo de calibración

**Adaptador**: `ingest/synthetic.py` ·
**Niveles**: `symbol → word → line → corpus`

Gramática juguete `q_o_grammar()`: AFND ponderado con oráculo
`accepts(word)` — `q` solo seguido de `o`, palabras cierran en `n`/`y`.
Es el instrumento de calibración: el engine debe recuperar exactamente
esa gramática sin alucinar.

## Render (sesgo de codificación)

`ingest/render.py` mapea glifos a dígrafos (`C→ch`, `S→sh`) — demuestra
que el engine "descubre" reglas de ligadura que son artefactos puros de
la codificación. Control que justifica tratar las ligaduras EVA como
ortografía, no gramática, y motiva `GlyphView` (`engine/glyphs.py`).
