# Escritura del Indo (Harappa)

**Fuente**: corpus ICIT/Mahadevan vía `field-cady/indus_valley_script_corpus`
(`data/raw/indus.csv`). **Adaptador**: `ingest/indus.py` ·
**Niveles**: `symbol → inscription → corpus`

## Notas de ingest

- El CSV guarda **orden físico**; los sellos se leen mayormente R/L →
  `normalize_direction` invierte las R/L para obtener orden de lectura.
  Sin esto, el signo terminal aparece al principio y las reglas se
  invierten.
- Filtra inscripciones de un solo signo (el nivel `inscription` exige
  ≥2 símbolos para que haya estructura interna).

## Hechos medidos

- 4.449 inscripciones · 17.213 signos · **alfabeto de 672 signos**
- Longitud media 3,9 (mediana 3) — textos brevísimos, sellos

## Firma formal

| rasgo | valor |
|---|---|
| Signo 740 ("jar") | final un **66%** en orden de lectura — marcador terminal |
| Signo 700 | inicial un **76%** — marcador inicial |
| Estructura | posicional sobre signos; casi no hay bigramas de conjunto cerrado |

**Veredicto**: firma opuesta al Voynich — alfabeto amplio, unidades
cortas, marcadores posicionales (sellos + etiqueta breve, no prosa).
millstone distingue "gramática de palabra" (Voynich) de "posición de
signo" (Indo) sin código específico.
