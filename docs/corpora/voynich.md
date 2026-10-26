# Voynich (MS 408) — corpus de referencia

**Fuente**: Zandbergen-Landini EVA IVTFF 2.0 (`data/raw/ZL3b-n.txt`,
voynich.nu) + Takahashi (`data/raw/IT2a-n.txt`, validación cruzada).
**Adaptador**: `ingest/ivtff.py` · **Niveles**: `symbol → word → line →
paragraph → folio → section → corpus`

## Hechos medidos (ZL)

- 227 folios · 38.213 palabras · 193.300 símbolos · 5.376 líneas
- ~27 símbolos EVA (+ dígrafos: bancos `ch|sh|cth|ckh|cph|cfh`)

## Firma formal (resumen de FINDINGS)

| rasgo | valor | lectura |
|---|---|---|
| Plantilla intra-palabra | Timm: 99,8% held-out, 364 bigramas | rígida |
| Orden entre palabras | out-degree real/barajado = 0,93 | libre |
| Flujo entre líneas | 5,7% vs 4,9% nulo | celdas, no prosa |
| Vocabulario | léxico cerrado (~28 bits/tipo) | seleccionado |
| Familias 1-edición | 73,7% vs 24,2% nulo | variantes de plantilla |
| `q→o` | ~124 violaciones distribuidas | casi-regla real |
| Efecto gallows | `p` ×11,6 en inicio de párrafo | marcador posicional |
| Triples | 649+ (`eee`, `iii`) | no-alfabético |

**Veredicto**: artefacto combinatorio / inventario estructurado — no
lengua natural, no ruido, no sustitución monoalfabética. El límite del
formalismo documentado: glosolalia y catálogo deliberado comparten la
misma firma.

## Verificación en vivo

`python -m millstone data\raw\ZL3b-n.txt report` regenera `REPORT.md`.
Neo4j (`docker compose up -d`): 237k nodos, `(:Constraint)-[:VIOLATED_AT]
→(:Word)`, `(:Hypothesis)-[:SUPPORTS|REFUTES]→(:Evidence)`.
