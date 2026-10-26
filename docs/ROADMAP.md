# Roadmap

> Documentación por corpus en `docs/corpora/`: `voynich.md`, `indus.md`,
> `lineara.md`, `culpeper.md`, `synthetic.md`

millstone es un motor genérico de caracterización gramatical. El Voynich
es el caso de estudio estrella, no el sistema. Estado: **completo** —
pipeline entero verificado sobre cinco corpus, 75 tests.

## Fase 0 — Fundaciones ✅

- [x] Skeleton: `pyproject.toml`, layout `src/`, pytest
- [x] Modelo de corpus genérico: jerarquía de niveles declarada por corpus.
      "Glifo/Folio/Línea" son instancias, no el esquema fijo.

## Fase 1 — `ingest`: adaptadores de fuente → modelo ✅

- [x] `synthetic.py` — genera corpus desde una gramática regular con
      oráculo `accepts()` — el instrumento de calibración
- [x] `plaintext.py` — texto tokenizado genérico (en/es recupera `q→u`)
- [x] `ivtff.py` — Voynich: ZL (ZL3b-n.txt) + Takahashi (IT2a-n.txt),
      cabeceras, loci, `$Q/$P/$L/$H`, incertidumbre
- [x] `render.py` — re-codificación glifo→grafema (control de sesgo EVA)
- [x] `indus.py` — corpus ICIT/Mahadevan, normalización de dirección R/L
- [x] `lineara.py` — corpus Navarre-AI (GORILA+SigLA), codepoints Unicode

## Fase 2 — `engine` genérico ✅

- [x] `CorpusView` + implementación RAM; Neo4j intercambiable
- [x] DSL de restricciones (8 tipos): FollowedBy, StartsWith, EndsWith,
      ForbidsBigram, SymbolAt, OnlyInPosition, NextInSet, PrevInSet
- [x] Negativos por restricción: frontera válido/inválido como dato
- [x] `discover`: inducción de restricciones con frontera de Pareto
      (caso-exactas vs casi-reglas con su cuenta de violaciones)
- [x] `mdl.prune`: base mínima sin reglas entrañadas
- [x] `frontier`: geometría de la frontera por atributo (mano/quire/sección)
- [x] `induce`: gramáticas inducidas (secuencial + posicional) y tamaño
      del lenguaje por DP — sobre-generación medida
- [x] `glyphs`: `GlyphView`/`to_glyphs` — nivel glifo (bancos EVA atómicos)
- [x] Batería de calibración: sintético recupera la gramática exacta;
      lenguas reales recuperan restricciones fonotácticas

## Fase 3 — Hipótesis y aplicación ✅

`hypotheses/` — cada teoría es un objeto con predicciones y evidencia
enlazada. Evaluadas sobre el corpus real:

- [x] `currier-ab` — gramáticas A/B distintas; `q→o` compartido
- [x] `qo-frontier` — REFUTA ruido de escriba; regla suave distribuida
- [x] `timm-slots` — 99,8% held-out con 364 bigramas
- [x] `initial-effect` — gallows medido (`p` ×11,6 en párrafo)
- [x] `closed-lexicon` — vocab seleccionado, no generado libre
- [x] `free-word-order` — orden libre entre palabras (0,93)
- [x] `natural-language` — mixto: Zipf sí, funcionales no
- [x] `uncertain-space` — `,` mayormente cortes reales
- [x] `transcription-robust` — la frontera está en el manuscrito
      (108/124 loci coinciden ZL vs Takahashi)
- [x] `line-clustering` — agrupación intra-línea débil (2,5×)
- [x] `flow-across-lines` — REFUTADO: celdas independientes
- [x] `paradigmatic-families` — vocabulario de variantes (73,7%)
- [x] `productive-grammar` — REFUTADO: no genera formas nuevas

## Fase 4 — `store` + `cli` ✅

- [x] Neo4j en vivo: 237k nodos, `Constraint→Word`, `Hypothesis→Evidence`
      navegable en localhost:7474
- [x] CLI: `stats` `discover` `check` `frontier` `hypothesize` `report`

## Fase 5 — Multicorpus (la fase que resultó ser el punto)

El motor se probó agnóstico: cada corpus cae en su clase sin código
específico — Voynich=inventario, Indo=sello, Lineal A=contabilidad,
Culpeper=lengua natural, sintético=oráculo. **Esa discriminación es el
producto**, no un paso más hacia el Voynich.

## Pendiente

- [ ] Excluir `?` (lecturas inciertas) del alfabeto en análisis
- [ ] `TranscriptionComparison` formal con more granularidad de locus
- [ ] FSA/slot grammar exportado a Neo4j como grafo navegable
- [ ] Testbed de candidatos de descifrado (mapeo glifo→fonema + check)

## Lógica del orden

- `ingest` primero: sin corpus no hay nada que caracterizar.
- `synthetic` y la calibración son prioritarias: son lo único que dice si
  el motor detecta gramática real o solo ruido.
- `engine` antes que `store`: el motor es el valor; Neo4j solo persiste.
- El DSL convierte la lógica específica de lengua de "código" a "datos".
