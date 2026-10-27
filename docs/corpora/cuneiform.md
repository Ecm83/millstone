# Cuneiforme (sumerio) — control descifrado nº 8

**Fuente**: volcado CDLI (`cdli-gh/data`, CC-BY-4.0) → muestra de 2.500
textos `lang sux` en `data/raw/cuneiform.atf`.
**Adaptador**: `ingest/cuneiform.py` → **Niveles**: `sign → word →
line → doc → corpus`

Sumerio (Ur III y afines), corpus *descifrado*: el control perfecto —
administración real escrita en lengua real. ¿El motor la distingue de
los sistemas indescifrados? Sí: cae entre clases.

## Hechos medidos

- 2.499 documentos · 56.406 líneas · 137.600 palabras · 13.789 tipos

| rasgo | valor | lectura |
|---|---|---|
| TTR | 0,100 | vocabulario real (vs 0,040 Culpeper, 0,220 Voynich) |
| hapax | 60,6% | lengua abierta |
| top-10 tokens | 19,8% | funcionales presentes |
| Colisiones n=4 | 2.376 tipos | fórmulas legales estándar |
| Eco | n=3 real ≈ nulo (4.518 vs 4.026) | repetición fórmulaica, no combinatoria |

**Veredicto**: **lengua natural administrativa** — ni inventario
cerrado (proto-Elamita: entradas únicas) ni prosa (Culpeper). La clase
intermedia que el panel necesitaba calibrar: contabilidad escrita en
una lengua de verdad, con plantillas de frase compartidas.

## Findings

## Cuneiforme: el control descifrado que faltaba

`ingest/cuneiform.py` sobre 2.500 textos `sux` del volcado CDLI. La
pregunta de calibración: ¿distingue el motor contabilidad-en-sistema-
indescifrado de contabilidad-en-lengua-real? Respuesta: sí, y cae en
una clase intermedia propia:

- Vocabulario **abierto** (hapax 60,6%, top-10 19,8%) — lengua real,
  no inventario. Ni proto-Elamita (82,7% hapax pero entradas únicas)
  ni Culpeper (42,8%) se le parecen exactamente.
- **Repetición fórmulaica masiva**: 2.376 tetra-gramas compartidos —
  son las frases legales contables estándar. Mismo género administrativo
  que proto-Elamita, pero escrito *en* lengua: el contenido formulaico
  se nota, el sistema no es combinatorio.
- Conclusión del control: el panel no solo separa descifrado/no —
  separa **clases de objeto**, y el cuneiforme marca dónde está la
  frontera "lengua + administración".
