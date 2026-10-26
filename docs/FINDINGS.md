# Findings — millstone: hallazgos medidos sobre cinco corpus

> Fichas por corpus en `docs/corpora/`. Voynich: `ZL3b-n.txt` (ZL) +
> `IT2a-n.txt` (Takahashi). Indo: `indus.csv` (ICIT). Lineal A:
> `linear_a.json` (GORILA/SigLA). Control: `culpeper.txt` (1653).

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

## Letras triples: sustitución monoalfabética refutada

649+ palabras contienen símbolo triplicado (`eee`=433, `iii`=183:
`daiiin`, `seees`, `qoteeey`...). Ninguna lengua europea tiene triples a
esa frecuencia (~1,7% de tokens); los que existen (alemán, ruso, yurok)
son compuestos marginales. **No es sustitución letra-a-letra** de lengua
europea — los triples son marcas (numerales/abreviaturas/inventario).

## Control externo: Culpeper's Complete Herbal (1653)

La batería completa contra un herbario médico-astrológico real de la
época del manuscrito:

| métrica | Voynich | Culpeper |
|---|---|---|
| tipos / tokens | 8.424 / 38.213 | 10.052 / 250.482 |
| TTR | 0,220 | 0,040 |
| hapax | 71,0% | 42,8% |
| len media | 5,1 | 4,5 |
| top-10 | 12,1% | **28,5%** |
| familias 1-ed | **73,7%** | 35,8% |
| tipos con triples | **341** | 8 |

Un texto alquímico real es lengua natural completa: funcionales
dominantes, vocabulario abierto, casi sin triples, pocas familias. La
firma Voynich es incomparable con prosa de su época — el corpus no es
"texto sobre plantas en otro idioma", es otra clase de objeto.

## Escritura del Indo — sello administrativo

`ingest/indus.py` sobre el corpus ICIT/Mahadevan (4.449 inscripciones,
672 signos, longitud media 3,9):

- **Normalización de dirección**: el CSV guarda orden físico; los sellos
  se leen R/L mayormente → `normalize_direction` invierte para obtener
  el orden de lectura. Sin esto, el signo terminal aparece al principio.
- **Marcadores posicionales**: signo 740 ("jar") es final el 66% de las
  veces en orden de lectura — marcador terminal. Signo 700 inicial el
  76% — marcador inicial.
- **Núcleos con hapax 84%** — cada inscripción lleva una secuencia
  central casi única (nombre/identificador).
- Estructura: `marcador inicial + núcleo + marcador terminal` — el
  patrón de un sello administrativo (heráldico/toponímico/de propiedad),
  no de una lengua corrida.

## Lineal A — contabilidad palacial

`ingest/lineara.py` sobre el corpus Navarre-AI (GORILA+SigLA, 1.637 docs
con texto, 3.767 palabras):

- Inventario de soportes: **913 nódulos + 489 tablillas + 194 roundels**
  ≈ 80% archivo administrativo.
- **40% de tokens contienen números egeos** (U+101xx); 42% de "palabras"
  son un solo signo → líneas de partida `commodity: cantidad`.
- **hapax 89,7%** — cada "palabra" es casi única (nombres propios);
  solo 24 secuencias multi-signo reaparecen en >1 doc.
- `U+1076B` abre 1.284 palabras — ideograma de producto dominante.

Firma: **listas contables con nombres** — la estructura de un archivo de
palacio, no de textos sagrados. El mismo perfil formal que Lineal B
(descifrado porque era griego contando ganado); aquí la lengua base es
eteocretense, pero la forma del corpus es idéntica: burocracia de
almacén.

## Panel comparativo — millstone discrimina clases de corpus

| Corpus | Firma | Clase |
|---|---|---|
| Voynich | plantilla intra-palabra + orden libre + léxico cerrado | inventario combinatorio |
| Indo | marcadores posicionales + núcleos hapax | sello administrativo |
| Lineal A | tokens numéricos + hapax extremo | contabilidad palacial |
| Culpeper | funcionales + vocabulario abierto | lengua natural |
| Sintético | gramática recuperada exacta | oráculo |

El mismo motor, sin código específico por corpus, asigna cada corpus a
su clase. Esa discriminación — no el descifrado del Voynich — es el
producto de millstone.
