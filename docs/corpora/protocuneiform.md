# Proto-cuneiforme — corpus nº 9, comparación de familia

**Fuente**: volcado CDLI (`cdli-gh/data`, CC-BY-4.0) → 3.000 textos
`lang qpc` no-MDP en `data/raw/protocuneiform.atf`.
**Adaptador**: reutiliza `ingest/protoelam.py` (mismo ATF: signos
`ZATU`/`NU`/... + numerales `k(Nxx)`; schema compartido).

Sistema padre del proto-elamita (~3400-3000 a.C., Uruk/Jemdet Nasr).
Contabilidad + listas léxicas. Solo parcialmente comprendido.

## Hechos medidos (muestra de 3.000 docs)

- 16.113 líneas · 30.879 clusters · 48.429 signos · ~1.900 códigos

| rasgo | proto-CUNEIFORM | proto-ELAMITA | lectura |
|---|---|---|---|
| hapax | 77,0% | 82,7% | ambos inventario |
| top-10 | 59,2% | 49,3% | cabeceras más concentradas en PC |
| eco verbatim n≥3 | 0 | 0 | entradas únicas |
| mezcla N↔ideograma interna | **17,5%** | **4,8%** | el hijo rigidiza la dualidad |

**El hallazgo de familia**: la partición ideograma/numeral que el
motor descubrió en proto-elamita existe en el padre — pero el
proto-elamita la hace **casi hermética** (4,8% de bigramas mixtos vs
17,5%). El sistema hijo no copia el formato contable: lo
**sistematiza**.

**Caveat**: la muestra incluye listas léxicas (`CDLI Lexical`), que
inflan el hapax de tipos — la clase del corpus sigue siendo
administrativa, el rango es honesto.

```bash
python -m millstone data/raw/protocuneiform.atf --format protoelam stats
```
