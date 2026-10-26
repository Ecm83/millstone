# Findings — millstone vs. Voynich (ZL3b-n, EVA)

Primera corrida de `discover` sobre el corpus real: 227 folios, 5.385 líneas,
38.213 palabras, 193.300 símbolos, 27 símbolos EVA distintos.

## Hallazgo principal: en el Voynich no hay casi nada exacto

`discover` no encontró **ninguna** regla `NextInSet`/`PrevInSet` exacta de
conjunto pequeño. Todas las reglas estructurales son *casi-reglas* con una
frontera de excepciones — consistente con ruido de transcripción, glifos
raros, o estructura genuinamente suave. La frontera no es ruido a eliminar:
es el objeto de estudio.

## Reglas recuperadas (con su frontera)

| Regla | Soporte | Violaciones | Nota |
|---|---|---|---|
| `h` solo tras `{c,s,t,k,p,f}` (+h) | 17.613 | 1–4 | Inventario de ligaduras EVA (ch, sh, cth, ckh, cph, cfh) recuperado sin conocerlo |
| `c` solo antes de `{h,t,k,p,f}` | 13.087 | 6–8 | `c` solo existe dentro de ligaduras; `cc` y `c?` son las excepciones |
| `q` seguida de `o` | 5.435 | ~124 (2,3%) | La regla famosa `q→o` NO es exacta: qe(61), qk(20), qc(17), qy(11), qa(7)... |
| `n` precedida de `{a,e,i,o,r}` | 6.186 | 3–9 | `n` nunca cierra tras conso-cluster |
| Ninguna palabra empieza por `b`/`h` | 38.213 | 0 | `StartsWith` exacto: `b` y `h` jamás iniciales |
| `m` precedida de ~11 símbolos | 1.071 | 12–15 | `m` es casi exclusivamente final de palabra |

## Estructura descubierta

El alfabeto EVA se stratifica solo, sin decírselo:

- **{c,s,t,k,p,f} + h** — el sistema de ligaduras ("benches" EVA)
- **q** — casi-determinista hacia `o`
- **{n,y,m,d,l,s,r}** — símbolos de cierre (fin de palabra)
- **{o,a,e,i}** — núcleo vocálico

Los ~110 `ForbidsBigram` (oh, co, ce, ah, eh...) son en su mayoría entrañados
por las reglas de conjunto — `h` solo tras bench-heads explica toda la columna
`(·,h)` prohibida. MDL los poda salvo los huecos genuinamente inexplicados.

## Implicación para el DSL

`FollowedBy` (sucesor único) era demasiado estricto para el Voynich: hacen
falta `NextInSet`/`PrevInSet` (contexto de conjunto) y tolerancia a
excepciones. Las reglas Voynich viven en la frontera 0 < viol < soporte·ε —
exactamente el espacio que Mill+Gold predicen para estructura sin
ground truth.

## Siguiente: hipótesis comprobables

- Currier A vs B: `$L` ya está en `folio.attrs` — particionar el corpus por
  lenguaje y comparar fronteras de reglas
- Las ~124 excepciones de `q→o`: ¿se concentran en folios/sección/manos
  concretos? (evidencia para/against scribe-error vs regla real)
