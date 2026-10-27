# Proto-Elamita — corpus indescifrado nº 6

**Fuente**: volcado CDLI (`cdli-gh/data`, CC-BY-4.0) → subconjunto
`lang qpc` de las publicaciones MDP extraído a
`data/raw/protoelamite.atf` (1.384 textos).
**Adaptador**: `ingest/protoelam.py` → **Niveles**: `sign → word
(cluster signs|nums) → line → doc → corpus`

El último sistema de escritura sustancial sin descifrar del Cercano
Oriente antiguo (~3100-2900 a.C., Susa e Irán). Sistema dual:
ideogramas `M\d{3}` + numerales `N\d{2}` heredados de proto-cuneiforme.

## Hechos medidos

- 1.381 documentos · 10.311 líneas · 19.390 clusters · 32.490 signos
- 1.661 signos distintos (variantes `~x` y compuestos `|A+B|` atómicos)
- Estructura de entrada: `signos , numerales` — el motor descubrió
  solo la partición: los bigramas prohibidos dominantes son todos M↔N.

## Batería (resumen)

| rasgo | valor | lectura |
|---|---|---|
| Léxico | sobre-generación 1e+17× bigrama / 1e+04× slots | cerrado |
| Entradas | hapax 82,7%; eco verbatim en el nulo (z=-0,9) | cada una casi única |
| Longitud entrada | media 1,68; 7,7% fuera de rango | uniforme |
| Flujo entre líneas | 0 pares | celdas independientes |
| Clustering intra-línea | 1,3% vs 5,9% nulo | anti-agrupado |
| Marcador inicial | `M009` ×1,9 en inicio de línea | header/owner |
| Timm held-out | 84,4% vs 78,5% nulo (×1) | plantilla débil |
| Familias 1-ed | 12,8% vs 3,4% nulo | variantes moderadas |
| Holdout exactas | 98/100 replican | estable |
| Mill en holdout | real=98% vs barajado=98% | reglas vacuas (honesto) |

**Veredicto**: misma clase que Lineal A / Indo — **inventario
administrativo** (entradas únicas `entidad : cantidad`, marcadores
posicionales, sin eco ni flujo). El panel discrimina la clase correcta
sobre un corpus que el motor nunca había visto.

## Reproducir

```bash
python -m millstone data/raw/protoelamite.atf --format protoelam stats
python -m millstone data/raw/protoelamite.atf --format protoelam hypothesize
```

## Findings

## Proto-Elamita: el panel se confirma sobre un corpus indescifrado nuevo

`ingest/protoelam.py` sobre el volcado CDLI (1.384 tablillas MDP
`lang qpc`, ~3100 a.C.): la batería completa lo clasifica en la misma
clase que Lineal A — **contabilidad** — sin ajustar nada:

- El motor descubrió solo la arquitectura dual: los ForbidsBigram
  dominantes separan ideogramas M de numerales N (los clusters son
  homogéneos) — la regla `entidad : cantidad` recuperada sin conocerla.
- Marcador posicional como en el Indo: `M009` ×1,9 en inicio de línea.
- Cero colisiones verbatim ≥3: cada entrada contable es única.
- Honestidad del instrumento: el holdout replica las exactas (98/100)
  pero Mill avisa `98% real = 98% barajado` — sobre alfabeto abierto
  esas reglas son vacuas, y el motor lo dice en vez de inflarse.
