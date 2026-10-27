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
| Replicación holdout | 100/100 reglas A→B vs 37% barajado | gramática estable |
| Deriva regional | intra-lengua 34,9% vs nulo 11,3% | textura de quire |
| Corte Currier en deriva | 19,4% vs nulo 0,9% | real pero < intra |
| Eco verbatim | n=2 z=+8,6; n=3 z=+20; n=4 en nulo | fragmentos de 2-3 |

**Veredicto**: artefacto combinatorio / inventario estructurado — no
lengua natural, no ruido, no sustitución monoalfabética. El límite del
formalismo documentado: glosolalia y catálogo deliberado comparten la
misma firma.

## Verificación en vivo

`python -m millstone data\raw\ZL3b-n.txt report` regenera `REPORT.md`.
Neo4j (`docker compose up -d`): 237k nodos, `(:Constraint)-[:VIOLATED_AT]
→(:Word)`, `(:Hypothesis)-[:SUPPORTS|REFUTES]→(:Evidence)`.

## Findings

## Voynich (ZL3b-n, EVA)

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
**Corrección posterior**: la razón FSA/tipos NO discrimina — Culpeper
sobre-genera 280× más (7e10 vs 2,5e8). Y a N fijo (`engine/metrics.py`,
20 reps por bloques): a 30k tokens el Voynich es MÁS abierto que
Culpeper — hapax 46,6%≈46,7%, TTR 0,18>0,12, Heaps β=0,58>0,52,
96 vs 63 tipos nuevos/1k. La comparación anterior sin igualar N decía
lo contrario. Lo que queda de la intuición "cerrado": la PLANTILLA
interna (Timm 99,8%) y el hapax inflado por autocita — no el tamaño
del léxico.

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

Síntesis de las hipótesis — formulación cauta:

El Voynich presenta una estructura léxica y combinatoria que, **bajo los
modelos probados**, resulta más compatible con un inventario finito
fuertemente restringido que con un modelo sencillo de texto lingüístico
ordinario: gramática rígida **dentro** de palabra (Timm), orden **débil** (no libre) entre palabras
con repetición local fuerte, vocabulario restringido de crecimiento
sub-lineal (Heaps β=0,66, no saturado), textura que deriva por
sección temática.

Separación explícita de tres cierres — el motor solo informa de dos:

- **Cierre formal** (cuántas cadenas admite el modelo): medido — el FSA
  posicional admite 2,1×10¹² cadenas vs 8.424 tipos.
- **Cierre empírico** (cómo se distribuye el vocabulario observado):
  medido — masa concentradísima, 99,8% held-out por slots.
- **Cierre semántico** (si las entradas son palabras, códigos o
  elementos de inventario): **fuera del alcance del instrumento**.

Un orden flexible puede venir de la tipología o del género (catálogo,
tabla); las triples pueden ser artefacto de transcripción. La
discriminación por clases es comparativa — proximidad a referencias
calibradas, no prueba de pertenencia.

## Familias paradigmáticas — vocabulario de variantes de plantilla

`hypotheses/families.py`: 73,7% de los 8.424 tipos tienen un vecino a
distancia de Hamming 1 vs 24,2% del vocabulario barajado por posición
(3,1×). El vocabulario no son palabras atómicas: son **variantes
mínimas de plantillas** (`daiin`/`daiiin`/`aiin`, `chol`/`chor`...).

## Control de artefacto de codificación (sesgo EVA)

`ingest/render.py` + experimento: una gramática sintética con glifos
atómicos `C`/`S` renderizada como dígrafos `ch`/`sh` hace que el engine
"descubra" `FollowedBy(c→h)`, `PrevInSet(h,{c,s})` y una riada de
bigramas prohibidos — **todos artefactos puros de la codificación**, la
gramática real no los contenía.

Implicación honesta: la clase de hallazgos "ligaduras EVA" del Voynich
(`h` solo tras `{c,s,t,k,p,f}`, `c→{h,t,k,p,f}`) vive en el nivel
**ortográfico** — mide cómo EVA escribe glifos del manuscrito con varias
letras, no la gramática. El resto de hallazgos (q→o, orden libre, léxico
cerrado, gallows, familias) no es explicable por la codificación.

Resolución implementada: `engine/glyphs.py` (`GlyphView` + `to_glyphs`)
resegmenta a nivel glifo — los bancos `ch|sh|cth|ckh|cph|cfh` pasan a ser
símbolos atómicos vía maximal-munch. A ese nivel el artefacto desaparece
y queda la gramática real: `q→o` mantiene sus 126 violaciones, y los
bancos muestran sus propias reglas (`cph`→`{o,e,ch,d,y,k,a,h}` exacta,
`ckh`/`cfh` casi-exactas).

## ¿Catálogo sin sintaxis? — agrupación intra-línea

`hypotheses/clustering.py`: la masa de palabras repetidas dentro de su
línea es **7,2% vs 2,9% del barajado global (2,5×)** — existe agrupación
débil a nivel de línea. El orden libre no es total: hay estructura
temática o catalográfica residual. Compatible con tablas/listas
(astrológicas, alquímicas, enciclopédicas) donde las líneas agrupan
conceptos relacionados sin sintaxis de frase.

## Síntesis revisada

La lectura "lengua natural con sintaxis" queda descartada por el orden
libre + ausencia de funcionales. La lectura que mejor encaja **toda** la
evidencia — plantilla intra-palabra rígida, léxico cerrado seleccionado,
orden libre, agrupación por línea, dos registros Currier — es un
**inventario estructurado** (catálogo/tabla generativa), o un proceso
productivo de escritura artificial. El motor caracteriza la estructura;
la intencionalidad es una pregunta que la estructura sola no decide.

## El límite formal: ¿flujo de texto o cuadrícula?

`hypotheses/flow.py`: los pares (fin de línea → inicio de siguiente) son
bigramas atestiguados solo **5,7% vs 4,9% del nulo** (1,2×) — REFUTADO el
flujo continuo. Cada línea es una celda independiente: la serialización
del manuscrito confirma la lectura de matriz/tabla, no de prosa.

Sobre la simetría glosolalia-vs-catálogo: bajo MDL y restricciones
topológicas son indistinguibles **porque su firma formal es idéntica por
construcción** — ambas son estructura sin dependencias semánticas
observables. La única ruptura posible de esa simetría requiere un ancla
externa: una correspondencia con contenido conocido (un crib, un item de
la tabla identificado). El formalismo llega hasta "hay un sistema";
"hay un mensaje" está fuera de su alcance — y millstone lo dice como
resultado, no como fracaso.

## La anomalía buscada: repeticiones de cadenas largas

Búsqueda de n-gramas de palabras repetidos en líneas distintas
(candidatos a "rotura de la regla estadística"): n=2→2389, n=3→155,
**n=4→exactamente uno**, n≥5→cero.

La única colisión verbatim de longitud 4 en todo el manuscrito:
`ol shedy qokedy qokeedy` en **f75v.47 y f84r.22** (ambas sección
biológica). Si el corpus fuera un proceso combinatorio frío, esa
repetición no debería existir. Es el único punto donde la matriz "se
rompe" — posible cita literal, parche de copia, o entrada de catálogo con
identidad propia.

> Auditada por `verbatim-echo` (ver más abajo): la colisión cae dentro
> del rango combinatorio una vez contadas las repeticiones cortas —
> cruce de fragmentos echoy del mismo escriba (quire M, mano 2), no
> unidad citada.

## Letras triples: sustitución monoalfabética refutada — **resegmentado**:
colapsando runs `e`/`i` (trazos EVA), las triples caen de 616 a ~33
(`?`×25 ruido de lectura, `o`×7, `r`×1). La refutación se debilita a
~33 casos — sigue siendo raro, pero ya no es el argumento fuerte.
Bonus: Timm aguanta resegmentado (98,2% vs 98,7%) — la plantilla no
es artefacto de trazos.

649+ palabras contienen símbolo triplicado (`eee`=433, `iii`=183:
`daiiin`, `seees`, `qoteeey`...). Ninguna lengua europea tiene triples a
esa frecuencia (~1,7% de tokens); los que existen (alemán, ruso, yurok)
son compuestos marginales. **No es sustitución letra-a-letra** de lengua
europea — los triples son marcas (numerales/abreviaturas/inventario).

## Validación out-of-sample: la gramática inducida es estable

`hypotheses/replication.py`: `discover` induce las 100 reglas top sobre
la mitad A del corpus (palabras en posición par) y cada regla se evalúa
sobre la mitad B (impares), que el motor nunca vio:

- **41/41 reglas exactas en A** mantienen tasa ≤2% en B.
- **59/59 casi-reglas** mantienen su tasa de violación dentro de 4σ —
  la frontera es una propiedad del corpus, no de la submuestra.
- **Control Mill**: sobre B con símbolos barajados intra-palabra, solo
  el 37% de las mismas reglas "replicaría" vs 100% real.

Resultado: las restricciones reportadas en este documento no son
sobreajuste a la muestra — son medidas estables del objeto. Lo que el
motor dice del Voynich, lo diría igual habiendo visto solo la mitad.

## Split contiguo: núcleo duro estacionario, textura suave regional

La versión fuerte del holdout divide por **posición en el documento**
(primera mitad del manuscrito vs segunda), no intercalada — testea
estacionariedad regional, no solo muestreo:

- **48/48 reglas exactas** replican entre mitades — el esqueleto de la
  gramática es igual en todo el manuscrito.
- **30/52 casi-reglas REFUTAN** — y el fallo es estructurado: las peores
  son todas variantes de `PrevInSet(o, ...)` (`o` tras `h`: 44,5% →
  53,7%; `o` tras `{q,h}`: 35,1% → 39,5%). La distribución de contextos
  de `o` — el subsistema `qo`/bancos — deriva entre mitades.
- Control Mill: real 78% vs barajado 42% — el instrumento sigue midiendo.

## Geometría de la deriva: el confounder de longitud, medido y corregido

`hypotheses/drift.py` descompone la deriva regional por celda
(quire $Q, lengua $L) contra el mismo cálculo sobre el corpus barajado.

**Primera medición (tasas por palabra)**: gap Currier real 6,3% < nulo
9,9% e intra-lengua 25,7% vs 20,7% — "casi todo artefacto". **Falso.**
El artefacto era la métrica: las tasas por secuencia crecen con la
longitud de palabra, y esa varianza mecánica *tapaba* la señal real.

**Medición corregida** (`events()`: tasas por ocurrencia de trigger):

- **Gap Currier: real 19,4% vs nulo 0,9%** — existe y es grande; pero
- **Dispersión intra-lengua: real 34,9% vs nulo 11,3%** — la variación
  quire-a-quire *dentro* de una misma lengua es mayor que el gap A/B.
- 0/10 reglas con gap de lengua dominante → el marco "dos dialectos"
  sigue refutado: la textura regional es **de grano quire**, más fina
  que el corte Currier.

Lección metodológica (la más importante de la batería): **toda tasa de
violación a nivel secuencia está confundida por la composición de la
región** — y el sesgo no solo inventa efectos, también los esconde.
Dos correcciones hacen falta siempre: medir por ocurrencia de trigger
(`Constraint.events`) y contrastar contra el nulo barajado.

## La "rotura de la matriz" auditada: eco corto real, colisión esperada

`hypotheses/echo.py` cuantifica las colisiones verbatim entre líneas
contra el nulo barajado intra-línea (mismo vocabulario, mismas
longitudes, orden libre):

- **n=2: real 2.389 vs nulo 2.115±32 (z=+8,6)** — los bigramas que
  cruzan líneas están inflados: hay eco fraseológico corto real
  (`s aiin`×56 líneas, `or aiin`×54, `ol shedy`×24).
- **n=3: real 155 vs nulo 38±6 (z=+20)** — el exceso es aún más claro.
- **n=4: real 1 vs nulo 0±1** — la colisión única `ol shedy qokedy
  qokeedy` cae **dentro del rango combinatorio**. No es anomalía: es la
  cola esperada de una distribución donde los fragmentos cortos ya se
  repiten.
- Sus piezas recurren por separado: `ol shedy qokedy` en 5 líneas,
  `shedy qokedy qokeedy` en 3 — el 4-grama es un **cruce de fragmentos
  echoy**, no una unidad citada.
- Contexto refutado: 0 vecinos compartidos (f75v continúa `qotar`,
  f84r con otro `qokeedy`).
- Intra-escriba: ambos loci en **quire M, Currier B, mano 2** — eco
  local del mismo escriba en el mismo cuaderno, no cita global.

Síntesis: el manuscrito **sí repite** — pero solo fragmentos de 2-3
palabras (fórmulas, adjacencias frecuentes), nunca unidades largas. La
única colisión de longitud 4 es el evento de cola esperado de ese
proceso, en el lugar menos misterioso posible: el mismo escriba, el
mismo quire. La "rotura" se disuelve en estructura ordinaria.

Lectura: hay **dos escalas de regularidad**. El núcleo duro (qué puede
seguir a qué, qué abre y cierra) es idéntico en todo el códice; la
textura suave (con qué frecuencia) deriva por región — y esa deriva es
real, aunque de grano más fino que el corte Currier (ver
`drift-profile`, siguiente sección).

## model-compare: el DL elige C, la firma no elige a nadie

`hypotheses/modelcompare.py` + `engine/generative.py`: tres mecanismos
generativos compiten en igualdad de condiciones (mismo FSA de forma de
palabra, misma longitud de línea, mismo suelo de tipo nuevo):

| modelo | DL held-out (intercalada) | contigua |
|---|---|---|
| A lingüístico (bigrama de palabras) | 0,47 Mb | 0,49 Mb |
| B catálogo (i.i.d. léxico enumerado) | 0,33 Mb | 0,35 Mb |
| C combinatorio (i.i.d. bajo P_FSA) | **0,26 Mb** | **0,29 Mb** |
| **D autocita** (copia reciente + mutación) | 0,32 Mb | 0,35 Mb |

C gana en ambas particiones — la descripción más barata del Voynich es
la máquina generativa sin léxico. **Pero** la reproducción de firmas
(pre-registradas: hapax, colisiones n=2..4) refuta a los tres:

- real: hapax=70,8%, coll2=969
- A: hapaxΔ0,29, coll2Δ1313 — inventa correlaciones de orden
- B: hapaxΔ0,29, coll2Δ274 — cerca del eco, no emite tipos nuevos
- C: hapaxΔ0,63, coll2Δ762 — genera de más, concentra de menos
- **D: hapaxΔ0,12, coll2Δ493** — el que MEJOR se comporta

**Conclusión (el quinto escenario)**: ningún modelo solo explica el
corpus. Pero la divergencia es informativa: el DL elige C (la máquina
sin léxico es la descripción más barata) mientras que **D — autocita
Timm/Schinner, copiar+mutar recientes — es el que mejor se comporta**
(hapaxΔ0,12, casi dentro de umbral). El mecanismo más parecido al
manuscrito no es el más barato. El vocabulario es *selección* dentro
del espacio generativo, y la deriva regional sigue sin modelo.

## Auditoría de cabos sueltos (ronda del revisor)

- **Triples resegmentadas**: `eee`/`iii` son trazos EVA — las triples
  caen de 616 a ~33 tras colapsar runs de e/i. La refutación
  monoalfabética se debilita a ~33 casos. Timm aguanta (98,2%).
- **Deriva = subsistema `o`**: 22/22 reglas que derivan entre mitades
  mencionan `o` — la textura regional NO es global, es el sistema de
  enlace vocálico `qo`/bancos. Reformulación: deriva localizada, no
  "textura suave del corpus".
- **Quire × mano**: dispersión de medias QUIRE=7,6% vs MANO=6,6% —
  gana sección sobre escriba, pero Q y H confundidas (cada quire ≈
  una mano). No separable del todo con este corpus.
- **`?` contamina 153/917 reglas** (17%) — las lecturas inciertas
  inflan el conjunto de restricciones; pendiente flag de exclusión
  en análisis serios.
- **Potencia de q→o**: con n=124 violaciones, solo se detecta
  concentración fuerte (>~40% de enriquecimiento); "distribuida" es
  la afirmación correcta, no "uniforme".
