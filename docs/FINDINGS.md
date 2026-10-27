# Findings — millstone: hallazgos medidos sobre siete corpus

> Fichas por corpus en `docs/corpora/`. Voynich: `ZL3b-n.txt` (ZL) +
> `IT2a-n.txt` (Takahashi). Indo: `indus.csv` (ICIT). Lineal A:
> `linear_a.json` (GORILA/SigLA). Proto-Elamita: `protoelamite.atf`
> (CDLI/MDP). Rongorongo: `rongorongo/*.xml` (Barthel). Control:
> `culpeper.txt` (1653).

## Panel comparativo — millstone discrimina clases de corpus

| Corpus | Firma | Clase |
|---|---|---|
| Voynich | plantilla intra-palabra + orden libre + léxico cerrado | inventario combinatorio |
| Indo | marcadores posicionales + núcleos hapax | sello administrativo |
| Lineal A | tokens numéricos + hapax extremo | contabilidad palacial |
| **Proto-Elamita** | dual M/N + hapax 82,7% + sin eco | **contabilidad palacial** |
| **Rongorongo** | ecos verbatim n≤9 + fórmulas cross-tablilla | **texto con refranes** |
| **Cuneiforme (sux)** | hapax 60,6% + fórmulas legales masivas | **lengua natural administrativa** |
| **Copiale cifrado** | eco letra-línea +47, sin palabras | **cifrado real (control)** |
| **Lingua Ignota** | sufijos categóricos + fam 10% | **nomenclátor construido** |
| Culpeper | funcionales + vocabulario abierto | lengua natural |
| Sintético | gramática recuperada exacta | oráculo |

El mismo motor, sin código específico por corpus, asigna cada corpus a
su clase. Esa discriminación — no el descifrado del Voynich — es el
producto de millstone.

## Lecciones metodológicas acumuladas

- La frontera es el objeto: casi-reglas con excepciones contadas, no
  reglas perfectas.
- Los nulos mecánicos importan: tasas por palabra inventan y esconden
  efectos → tasas por ocurrencia de trigger.
- La textura suave del Voynich deriva por sección temática (quire N
  biológica +15,9%), no por mano ni por corte Currier.
- El instrumento es honesto: cuando las reglas son vacuas (alfabeto
  abierto), el control Mill lo dice (98% real = 98% barajado en
  proto-Elamita).
- En rongorongo, el echo-map separa tablillas refránicas
  (E=16,8%, C=12,9% — la tradición paralela/calendario) de texto
  corrido (A=3,1%). Cuidado: los glifos rotos `_` fabrican ecos
  falsos; hay que excluirlos.
- El núcleo robusto sostiene la clase: filtrado al 74,3% de palabras en
  las que ZL y Takahashi coinciden (`compare --signature`), la firma del
  Voynich se mantiene (timm 0,984, orden libre 0,93, familias 13,4); el
  eco baja (22,8→17,7) y la base exacta cae 263→187 — ~76 reglas
  "exactas" apoyaban en lecturas en disputa. La transcripción es un
  cuarto de ruido potencial; la clase no depende de él.
- Geometría del eco (`echo_decay_profile`): el Voynich es el único
  cliff del panel — colisiones mueren en n=4 (slope −3,89, r²=,97)
  mientras todo lo demás tiene cola hasta n=9-10 (Culpeper −0,76,
  cuneiforme −0,62 r²=1,0 fórmulas legales, Rongorongo −0,72,
  Copiale −0,84). La forma del decaimiento separa catálogo de
  refranes/copia mejor que el z a n fijo.
- Ancla fonotáctica (`phonotactic`): cv_alt de Culpeper 0,69 vs
  Voynich-EVA 0,57; en testbed, Bax sube alternancia sobre su nulo
  (0,525 vs [0,31,0,49]) — evidencia débil pero real de que su
  asignación toca estructura.
- La deriva no es un subsistema ni una textura única: borrar `o` no la
  elimina (migra a y/h), y los perfiles por quire correlacionan de
  forma estructurada — `o<-h` vs `h→{y,d}` anti-correlacionan a
  r=−0,74: regiones que relajan una restricción tensan la hermana.
- El cifrado real no firma como el Voynich: Copiale a nivel letra tiene
  eco_z3 **+47** (la homofonía filtra los n-gramas del plaintext); el
  Voynich tiene **−189** (supresión de colisiones). Signo opuesto —
  dato contra toda lectura "Voynich = texto natural sustituido".
- Blindaje total: las 16 hipótesis replican su veredicto sobre el
  consenso (`--consensus-with`): timm 99,6%, familias 74,9% (sube),
  replicación 42/42, eco z>7, flow-across-lines refutado igual. Nada de
  lo medido era ruido de lectura.
- Al comparar padre/hijo (proto-cuneiforme vs proto-elamita), la firma
  mide evolución de sistemas: el hijo rigidiza la dualidad
  ideograma/numeral del padre (mezcla interna 4,8% vs 17,5%).
- model-compare: el DL elige la descripción más barata (C) pero la
  autocita (D, copiar+mutar) reproduce mejor la firma. Divergencia
  resuelta por descomposición: ningún mecanismo solo explica la firma —
  coll2/coll4→B (suelo i.i.d. del léxico), hapax/coll3/repmass→D
  (exceso de autocita); con E (trigrama-KN, memoria variable) entra el
  quinto rival: **pierde mal en DL (0,63 Mb, el más caro)** — no hay
  memoria de palabras de orden ≤3 que se pague — aunque gana `fam`
  (aprende qué tipos siguen a qué tipos). El Voynich es catálogo +
  autocita, no un
  generador libre ni una lengua. "Léxico cerrado" caído: la razón FSA/tipos
  no discrimina (Culpeper sobre-genera 280× más); el rasgo real es
  crecimiento sub-lineal (Heaps β=0,66).

## Batería pre-registrada (battery.yaml, hash `5bed9fa18f0b`)

Spec v2: `echo_slope`/`echo_nlast` añadidos como ejes de eco;
`model_compare` sale del vector (diagnóstico de mecanismo, no posición);
controles poblados por familia — naturales [culpeper, copiale-de],
administrativos [cuneiform, indus, lineara, protoelam],
cifrados [copiale], refranes [rongorongo],
sintéticos [shuffled, markov1-4, autocite, codebook].
markov3/4 ya medidos: echo_z3 ≈ 0 — la memoria markoviana no produce
eco a ningún orden.

Vector a N=10k con nulos intra-línea — el panel ya es vectorial:

| corpus | hapax | heaps | fam | outdg | echo3 |
|---|---|---|---|---|---|
| Voynich | 0,63 | 0,68 | 11,8 | 0,92 | 24,4 |
| Culpeper | 0,55 | 0,61 | 13,0 | 0,63 | 249,1 |
| cuneif.sux | 0,65 | 0,68 | 7,4 | 1,01 | 11,9 |
| markov1/2 | ~0,63 | ~0,71 | ~10 | ~1,0 | ~0 |
| autocite | 0,49 | 0,66 | 8,4 | 0,98 | 2,1 |
| codebook (Culpeper recod.) | 0,49 | 0,56 | 14,5 | 0,73 | 127,8 |

El Voynich cae entre administrativo y codebook en eco (24 vs 12 vs
128), orden libre como todo lo no-sintáctico, y seña propia en
familias/hapax. Ningún control lo clona — firma única, no copia.

## Frontera medición / interpretación

El panel mide **posición vectorial** en ~5 dimensiones; las etiquetas de
clase ("inventario", "refranes", "contabilidad") son **interpretación**
de esa posición, no salida del instrumento. Igualmente, "catálogo +
autocita" es la lectura que mejor encaja la descomposición de
`model-compare` — una hipótesis apoyada, no un resultado directo del
vector. Las clases minoritarias siguen de un miembro: la posición está
medida, el vecindario está calibrado, la etiqueta es nuestra.

- Eco no es memoria corta: markov de orden 1-4 produce echo_z3 ≈ 0
  (0,7 / −0,1 / 2,4 / −0,8) vs Voynich 20 — ninguna memoria markoviana
  genera eco de palabras; la repetición es estructura, no proceso.
- El eco es 100% léxico: recodificar el propio Voynich a entradas
  opacas (biyección tipo→tipo) deja echo_z3=18,3 ≈ 20 — las colisiones
  son de tipos, no de posiciones.
