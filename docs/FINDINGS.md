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
- Al comparar padre/hijo (proto-cuneiforme vs proto-elamita), la firma
  mide evolución de sistemas: el hijo rigidiza la dualidad
  ideograma/numeral del padre (mezcla interna 4,8% vs 17,5%).
- model-compare: el DL elige la descripción más barata (C) pero la
  autocita (D, copiar+mutar) reproduce mejor la firma — divergencia
  DL-vs-comportamiento. "Léxico cerrado" caído: la razón FSA/tipos
  no discrimina (Culpeper sobre-genera 280× más); el rasgo real es
  crecimiento sub-lineal (Heaps β=0,66).

## Batería pre-registrada (battery.yaml, hash fijado)

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
