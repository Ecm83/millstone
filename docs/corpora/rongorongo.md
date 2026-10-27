# Rongorongo — corpus indescifrado nº 7

**Fuente**: `phspaelti/RR-corpus` (XML, transcripción Barthel/C.E.I.P.P.)
→ `data/raw/rongorongo/*.xml` (6 tablillas A–F).
**Adaptador**: `ingest/rongorongo.py` → **Niveles**: `glyph → line →
side → tablet → corpus`

El único sistema de escritura autóctono de Oceanía (Isla de Pascua,
s. XVIII-XIX), sin descifrar. Bustrofedon invertido.

## Hechos medidos

- 6 tablillas · 12 caras · 107 líneas · 5.460 glifos
- 941 códigos Barthel distintos (variantes con letra conservadas)
- `001` casi no mezcla (domina los ForbidsBigram) — pero **no** forma
  series: 276 runs, 270 de largo 1, máximo 2. La imagen de "series
  001 001 001" es mito: `001` es un singleton de fórmula.
- **La fórmula `X·380·001` recuperada sola**: `380→001` es el 77% de
  los `380` (43/56), y vive **solo en C (20) y E (23)** — las dos
  tablillas refránicas del echo-map. Es la estructura de la
  conocida fórmula de procreación de las listas genealógicas
  (Mamari/Keiti), sin sabérsela.

## Ecos verbatim entre líneas (a nivel glifo)

| n | real | nulo intra-línea (10 rep) |
|---|---|---|
| 3 | 157 | ~32 |
| 4 | 65 | ~2 |
| 6 | 23 | 0 |
| 8 | 6 | 0 |
| 9 | 2 | — |
| ≥10 | 0 | — |

- **Refranes intra-tablilla**: los n-gramas ≥8 comparten líneas
  *consecutivas de la misma tablilla* (Ca10/Ca11, Bv05/Bv06, Er02/Er04,
  Ca07/Ca08) — estructura de repetición paralela, tipo estribillo.
- **Fórmulas viajeras**: 6 tetra-gramas cruzan tablillas distintas
  (`001 009 755 050` entre Ca01 y Er09, `004 002 004 002` en Ab05,
  Cb08, Cb11) — motivos cortos compartidos entre documentos.

## Echo-map: % de cada tablilla en material compartido (n>=4, sin `_`)

| tablilla | glifos | % en eco>=4 | lectura |
|---|---|---|---|
| E (Keiti) | 888 | **16,8%** | la mas refranica del corpus |
| C (Mamari) | 1.011 | **12,9%** | 12 ecos largos >=8: calendario/estribillos |
| B (Aruku) | 1.298 | 7,1% | mixta |
| A (Tahua) | 1.842 | 3,1% | texto largo mayormente unico |
| D | 266 | 1,5% | pequeña, casi toda unica |
| F | 69 | 0,0% | fragmento |

- Leccion de artefacto: contando `_` (roto), la linea Da08 salia
  100% eco — era `_ _ _ _ _` compartido con Da01. Marcas de daño
  crean ecos falsos; el mapa cuentos sin ellas.
- El mapa discrimina: **E y C son liturgia/formula** (refranes
  largos entre lineas consecutivas); **A es texto corrido** —
  coincide con la literatura (Mamari/Keiti = tradicion paralela y
  calendario; Tahua = texto extenso unico).

## Firma

**Texto con refranes y fórmulas** — la clase opuesta al inventario
administrativo (Indo/Lineal A/Proto-Elamita: cero colisiones ≥3).
Estructura de repetición compatible con composición oral/cantada,
consistente con la hipótesis clásica del canto/rezo.

## Reproducir

```bash
python -m millstone data/raw/rongorongo --format rongorongo stats
python -m millstone data/raw/rongorongo --format rongorongo discover --level line
```

## Findings

## Rongorongo: la anticlase administrativa

`ingest/rongorongo.py` sobre el corpus Barthel XML (6 tablillas, 5.460
glifos, 941 códigos): donde el proto-elamita dio *cero* colisiones ≥3,
rongorongo da **157 trigramas y ecos de hasta 9 glifos** entre líneas —
el nulo intra-línea produce ~0.

- Los ecos largos (n≥8) son **refranes intra-tablilla** entre líneas
  consecutivas — estructura de estribillo, no de listado.
- Los cortos (n=4) incluyen **6 fórmulas que cruzan tablillas
  distintas** — motivos compartidos del corpus.
- `001` (el glifo más frecuente) casi solo se junta consigo mismo:
  las famosas series `001 001 001`, recuperadas sin conocerlas.

La firma: **texto con refranes y fórmulas viajeras** — compatible con
composición oral/cantada, la lectura clásica de rongorongo. El panel
gana su sexta clase, y es justo la simétrica de la administrativa.
