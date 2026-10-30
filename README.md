# millstone

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23804059.svg)](https://doi.org/10.5281/zenodo.23804059)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*English: [README_EN.md](README_EN.md) | Simple: [README_SIMPLE_EN.md](README_SIMPLE_EN.md)*

Motor determinista de caracterización gramatical sobre corpus cerrados.

No es un LLM ni un analizador estadístico. Es una **IA simbólica** agnóstica de
lengua que caracteriza la topología gramatical de un corpus: grafo de
conocimiento jerárquico + motor de restricciones + validación por generación de
negativos (métodos de Mill / identificación de Gold / MDL).

Caso de estudio estrella: el **Manuscrito Voynich** — el corpus cerrado más
famoso que nadie ha descifrado. Pero el motor no sabe nada del Voynich:
funciona igual sobre latín, fonemas del inglés o una gramática sintética.

## Citar

Castelló March, E. (2026). *millstone: motor determinista de
caracterización gramatical sobre corpus cerrados* (v0.1.1). Zenodo.
https://doi.org/10.5281/zenodo.23804059

## La idea

Un corpus cerrado sin ground truth no se puede "aprender"; se puede
*caracterizar*. millstone trata la gramática como un objeto matemático:

- **Grafo jerárquico**: niveles declarados por corpus, p.ej.
  Símbolo → Palabra → Línea → Párrafo → Folio → Sección
- **Restricciones**: reglas deterministas expresadas en un DSL genérico
  (posicionales, de slots, entre niveles), registradas como nodos con su
  evidencia enlazada
- **Negativos**: cada restricción define qué cadenas son inválidas → la
  frontera válido/inválido es el objeto de estudio
- **Hipótesis**: nodos de teoría con predicciones y refutaciones registradas
  en el grafo
- **Criterio**: MDL — la gramática correcta es la que comprime mejor el corpus

## Calibración

El Voynich no tiene ground truth, así que no puede validar el motor. Por eso
millstone se calibra primero sobre corpus **con** gramática conocida:

- corpus sintéticos generados desde una gramática regular/CFG dada → el motor
  debe recuperarla
- lenguas reales → el motor debe recuperar restricciones fonotácticas conocidas

Solo un instrumento calibrado se aplica después al Voynich.

## Arquitectura

Capas desacopladas. Ninguna capa conoce la implementación de la de abajo, solo
el contrato:

```
millstone/
├── model.py     modelo de corpus genérico (schema de niveles + nodos)
├── ingest/      adaptadores de fuente → modelo: ivtff (Voynich),
│                plaintext, synthetic, render + remap (re-codificación
│                y testbed de descifrado), indus (ICIT), lineara
│                (GORILA), protoelam (CDLI), rongorongo (Barthel),
│                cuneiform (CDLI), copiale (cifrado + alemán descifrado)
├── store/       modelo → Neo4j (almacén + exploración visual; NO razona)
├── engine/      motor: view, constraints (8 tipos), check, discover
│                (Pareto), mdl, frontier, induce, glyphs, metrics,
│                battery (firma pre-registrada), generative (5 modelos),
│                transcription (comparación ZL↔TT + consenso)
│                opera sobre CorpusView (interfaz abstracta; Neo4j o RAM)
├── hypotheses/  18 hipótesis evaluadas: predicciones, refutaciones,
│                geometrías de frontera — todas con evidencia enlazada
└── cli/         punto de entrada que conecta todo
```

Regla de oro: **desacoplado ≠ distribuido**. Un repo, módulos con fronteras
claras. `engine` funciona sobre un corpus en memoria en tests — Neo4j es
intercambiable.

## Estado

Funcional end-to-end y calibrado sobre **11 corpus** (ver
`docs/corpora/` y `docs/FINDINGS.md` para los hallazgos medidos;
`docs/PAPER.md` para la nota informal):

| Corpus | Firma detectada | Veredicto |
|---|---|---|
| **Voynich** (ZL + Takahashi) | plantilla intra-palabra + orden libre + léxico cerrado | inventario combinatorio |
| **Indo** (ICIT/Mahadevan) | marcadores posicionales + núcleos 84% hapax | sello administrativo |
| **Lineal A** (GORILA/SigLA) | 40% tokens numéricos + 90% hapax | contabilidad palacial |
| **Proto-Elamita** (CDLI) | reglas vacuas vs alfabetos abiertos | inventario/rorro oscuro |
| **Rongorongo** (Barthel) | ecos n≤9 entre líneas consecutivas | texto con refranes |
| **Cuneiforme** (sux, CDLI) | hapax 60% + fórmulas legales | lengua administrativa |
| **Copiale** | eco letra-línea +47 (signo opuesto al Voynich) | cifrado real (control) |
| **Culpeper 1653** | funcionales dominantes, vocabulario abierto | lengua natural ✓ |
| **Lingua Ignota** (Hildegard) | sufijos categóricos + fam 10% | nomenclátor construido |
| **Letanía latina** | cola de eco n≤6 | refrán litúrgico |
| **Sintético** | gramática recuperada exacta | oráculo ✓ |

Datos: los corpus no van en el repo — `docs/data.md` lista fuentes y
comandos de descarga. `pytest` corre sin datos (controles sintéticos).

CLI: `python -m millstone <corpus> stats|discover|check|frontier|
hypothesize|report|testbed|compare|battery|push`. Opciones globales:
`--map FILE` (descifrado candidato antes de cualquier comando),
`--consensus-with FILE` (núcleo robusto de dos transcripciones),
`--with FILE` (segundo corpus p. ej. para `transcription-robust`),
`--format` (ivtff, plaintext, protoelam, rongorongo, cuneiform,
copiale, copiale-de). `testbed` compara la firma original vs
descifrada incl. nulos `--nulls N`; `battery` da el vector de firma;
`compare` mide el acuerdo entre transcripciones. Neo4j opcional:
`docker compose up -d` + `push` → grafo con FSA navegable.
