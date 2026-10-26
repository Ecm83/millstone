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

---

## Currier A/B — primera hipótesis evaluada

Partición por `$L` de folio: A=11.073 palabras, B=23.837.

- **[SOPORTA] las gramáticas difieren**: 125 restricciones exactas solo en A,
  57 solo en B. La etiqueta Currier corresponde a estructura real.
- **[SOPORTA parcial] B es más restrictiva al final de palabra**: el
  `EndsWith` de A tolera ~21 símbolos; el de B es menor.
- **[REFUTA] la frontera de `q→o` difiere entre A y B**: A=0,26% vs B=0,39%
  de palabras violando — la regla se comporta igual en ambos. Indica
  convención ortográfica compartida, no rasgo gramatical de cada "lengua".
- Caveat metodológico: gran parte del diff son `ForbidsBigram` con `?`
  (lecturas inciertas) — el símbolo `?` contamina; valorar excluirlo de
  `alphabet` en análisis serios.

## Frontera de q→o — refutada la hipótesis "ruido de escriba"

`engine/frontier.py` agrupa las ~124 violaciones por atributo de folio:

- **Por mano**: distribuidas (top: mano 2 con 36,5% de violaciones sobre
  28,8% de palabras — levemente por encima, no concentración)
- **Por quire**: distribuidas (top: quire T, 33,3% sobre 28,5%)
- **Por lenguaje**: B acumula 73% sobre 62% de masa — coherente con el
  tamaño de B, no sesgo

Conclusión: las excepciones de `q→o` son una **propiedad distribuida del
sistema**, no errores localizados. La regla es suave de verdad.

## Timm (generador de slots) — soportado con contundencia

Modelo: bigramas carácter-carácter inducidos sobre train, evaluados sobre
palabras held-out (`hypotheses/timm.py`).

- **Voynich**: 99,8% de 7.643 palabras held-out aceptadas con solo 364
  bigramas. Vocabulario casi cerrado: la plantilla predice lo que no ha visto.
- **Barajado (Mill: diferencia)**: mismo alfabeto y longitudes, combinatoria
  destruida → 51,6%. Error real ×240 menor → la estructura es combinatoria,
  no artefacto del alfabeto.
- **Control en lengua natural** (docs del repo, ~1.2k palabras
  español/inglés): 91,6% vs 53,4% barajado — error solo ×6 menor. El
  Voynich es cualitativamente más cerrado que texto natural.

Consistente con la tesis de Timm & Schinner: la palabra Voynich se comporta
como salida de un proceso combinatorio de plantillas, no como vocabulario
de lengua abierta.

## Léxico cerrado — el vocabulario es un inventario seleccionado

`engine/induce.py` induce el FSA del corpus (estados = símbolo previo, o
(posición, símbolo) para el modelo de slots). `language_size` cuenta por DP
las palabras que la gramática acepta:

- FSA bigramario: acepta **4,7×10¹⁶** palabras (≤14 chars) vs 8.424 tipos
  observados → sobre-genera 6×10¹²×
- FSA posicional (slots): acepta **2,1×10¹²** → 10.000× más restrictivo,
  pero sigue 2×10⁸× por encima del vocabulario

Lectura: la estructura de palabra es real y posicional (los slots existen),
pero el vocabulario no es un muestreo libre del lenguaje de la plantilla —
es un **conjunto finito seleccionado** (~28 bits de selección por tipo).
Favorece lecturas tipo código/inventario fijo por encima de "generador
estocástico puro": un generador libre produciría más hapax y vocabulario
más abierto.

También: el muestreo ponderado del FSA solo reproduce palabras
atestiguadas (2/5000 inéditas) — la masa de probabilidad está
concentradísima en el vocabulario real.

## Validación cruzada de transcripciones (ZL vs Takahashi)

`IT2a-n.txt` = lectura independiente de Takahashi (37.044 palabras,
23 símbolos) vs ZL (38.213, 27 símbolos):

- **La frontera de `q→o` es del manuscrito**: tasas casi idénticas
  (0,33% vs 0,36%) y **108 de ~124 líneas violadoras coinciden** — ambos
  transcritores leyeron los mismos glifos (`qkeeody`, `qpol`, `qkeey`).
  Las discrepancias restantes (`qkar`/`qkos`) son lecturas divergentes en
  el mismo locus — también información.
- 78 reglas exactas comunes; 34 solo-ZL, 10 solo-TT — ZL distingue más
  (lee más símbolos raros).
- Conclusión metodológica: las restricciones descubiertas no son
  artefacto de la transcripción. El instrumento mide el manuscrito.

## Espacios inciertos `,` — son cortes, con una minoría continuadora

2.743 espacios inciertos. Distancia de variación total del primer símbolo
del par que cruza la frontera:

- TV(`,`, `.`) = **0,385** vs TV(`,`, interno) = **0,676** → se distribuyen
  como cortes de palabra reales
- Pero `l`(27%), `r`(21%), `o`(16%) están elevados vs `.` → ~1/5 parecen
  continuaciones (p.ej. `ol`, `ra`, `lk` que también son finales válidos)
- Pares top: `ra`(286), `lk`(147), `lc`(145), `ls`(125), `sa`(124)

Lectura: el escriba marcaba `,` cuando el espacio era ambiguo, y en su
mayoría el corte es real — pero existe una subpoblación de palabras
partidas (o compuestas) que merece análisis aparte.

## Idioma natural — evidencia mixta

- **[SOPORTA] cola Zipfiana**: 71% hapax (5.979/8.424 tipos) — la
  distribución léxica parece de lengua
- **[REFUTA] funcionales dominantes**: top-10 cubre solo 12,1% de tokens
  (lengua real ~15-25%+) — no hay equivalentes a "de/el/la/the"
- **[SOPORTA] longitudes variadas**: 38,8% fuera de media±1,5 (μ=5,06)

La lectura: superficie Zipfiana sin gramática de función — compatible con
un léxico real pero rígidamente templado por dentro (Timm), o con un
código donde cada "palabra" es una entrada de inventario.

## Orden de palabras libre — consistencia con codebook

Mill por barajado intra-línea (mismo vocabulario y frecuencias, orden
destruido): out-degree de los 50 tipos más frecuentes real/barajado =
**0,93** — indistinguible del azar. `daiin` (800 ocurrencias) admite 405
sucesores distintos.

Síntesis de las hipótesis: gramática rígida **dentro** de palabra
(Timm), orden libre **entre** palabras, léxico cerrado seleccionado, dos
sublenguajes Currier — el retrato de un sistema de inventario/código,
no de una lengua con sintaxis.
