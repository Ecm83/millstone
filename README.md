# millstone

Motor determinista de caracterización gramatical sobre corpus cerrados.

No es un LLM ni un analizador estadístico. Es una **IA simbólica** agnóstica de
lengua que caracteriza la topología gramatical de un corpus: grafo de
conocimiento jerárquico + motor de restricciones + validación por generación de
negativos (métodos de Mill / identificación de Gold / MDL).

Caso de estudio estrella: el **Manuscrito Voynich** — el corpus cerrado más
famoso que nadie ha descifrado. Pero el motor no sabe nada del Voynich:
funciona igual sobre latín, fonemas del inglés o una gramática sintética.

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
│                plaintext, synthetic, render (re-codificación),
│                indus (ICIT), lineara (GORILA), protoelam (CDLI),
│                rongorongo (Barthel), cuneiform (CDLI, sux+qpc).
│                Sin dependencias de grafo
├── store/       modelo → Neo4j (almacén + exploración visual; NO razona)
├── engine/      motor: view, constraints (8 tipos), check, discover
│                (Pareto), mdl, frontier, induce, glyphs (nivel glifo)
│                opera sobre CorpusView (interfaz abstracta; Neo4j o RAM)
├── hypotheses/  17 hipótesis evaluadas: predicciones, refutaciones,
│                geometrías de frontera — todas con evidencia enlazada
└── cli/         punto de entrada que conecta todo
```

Regla de oro: **desacoplado ≠ distribuido**. Un repo, módulos con fronteras
claras. `engine` funciona sobre un corpus en memoria en tests — Neo4j es
intercambiable.

## Estado

Funcional end-to-end y calibrado sobre **nueve corpus** (ver
`docs/corpora/` y `docs/FINDINGS.md` para los hallazgos medidos;
`docs/PAPER.md` para la nota informal):

| Corpus | Firma detectada | Veredicto |
|---|---|---|
| **Voynich** (ZL + Takahashi) | plantilla intra-palabra + orden libre + léxico cerrado | inventario combinatorio |
| **Indo** (ICIT/Mahadevan) | marcadores posicionales (jar final 66%) + núcleos 84% hapax | sello administrativo |
| **Lineal A** (GORILA/SigLA) | 40% tokens numéricos + 90% hapax | contabilidad palacial |
| **Culpeper 1653** | funcionales dominantes, vocabulario abierto | lengua natural ✓ |
| **Sintético** | gramática recuperada exacta | oráculo ✓ |

CLI: `python -m millstone <corpus> stats|discover|check|frontier|
hypothesize|report|testbed`. `report` regenera los veredictos en
markdown. `--map <fichero>` re-codifica el corpus con un candidato de
descifrado (unidad→fonema, maximal-munch; ver `data/maps/`) antes de
cualquier comando; `testbed` compara la firma original vs descifrada.
Neo4j opcional: `docker compose up -d` → grafo navegable con
`Constraint→Word` e `Hypothesis→Evidence`.
