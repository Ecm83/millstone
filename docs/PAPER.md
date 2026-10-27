# millstone — nota informal

> Versión de trabajo. Números medidos con `python -m millstone`; datos en
> `data/raw/`; detalle por corpus en `docs/corpora/`; veredictos
> regenerables con `report`.

## Resumen

Presentamos un instrumento determinista que caracteriza la estructura
gramatical de un corpus cerrado sin intentar descifrarlo. Aplicado a
nueve corpus (seis de escrituras indescifradas o históricas, un control
de lengua natural, un oráculo sintético y controles generativos), el
mismo motor asigna a cada uno una clase estructural sin código
específico. Sobre el Manuscrito Voynich el veredicto es: **inventario
combinatorio construido por selección y autocita** — plantilla rígida
dentro de palabra, orden libre entre palabras, vocabulario cerrado —
y la conclusión se sostiene sobre el núcleo robusto donde dos
transcripciones independientes coinciden.

## 1. El método

El corpus se modela como jerarquía de niveles (símbolo → palabra →
línea → …→ corpus) declarada por fuente. Sobre esa estructura:

- **`discover`** induce restricciones de un DSL regular deliberadamente
  limitado (posición, adjacencia, bigramas prohibidos) y reporta cada
  candidata con soporte y **cuenta de violaciones** — la frontera
  válido/inválido es el objeto, no el ruido.
- **`mdl.prune`** construye la base mínima: solo reglas exactas, sin
  restricciones entrañadas entre sí.
- **Batería pre-registrada** (`battery.yaml`, hash fijado): vector a
  N=10k tokens con bootstrap por bloques — hapax, Heaps β, familias a
  edición-1, out-degree, eco verbatim, todo contra nulos mecánicos.
- **Hipótesis** como objetos con predicciones y evidencia enlazada; cada
  veredicto lleva sus números.

Todo es determinista: mismo corpus, mismo resultado.

## 2. El panel comparativo

| Corpus | Firma | Clase |
|---|---|---|
| Voynich (ZL+Takahashi) | plantilla intra-palabra + orden libre + léxico cerrado | **inventario combinatorio** |
| Indo (ICIT) | marcadores posicionales + núcleos hapax | sello administrativo |
| Lineal A (GORILA) | tokens numéricos + hapax extremo | contabilidad palacial |
| Proto-elamita (CDLI) | dual M/N, "cosa:cantidad" | contabilidad palacial |
| Rongorongo (Barthel) | ecos n≤9 + fórmulas cross-tablilla | texto con refranes |
| Cuneiforme sumerio | hapax 61% + fórmulas legales | lengua administrativa |
| Culpeper 1653 | funcionales + vocabulario abierto | lengua natural |
| Sintético | gramática recuperada exacta | oráculo |

Ningún control clona la firma del Voynich: cae entre administrativo y
codebook en eco (24 vs 12 vs 128) y se señala en familias/hapax.

## 3. El caso Voynich

Dieciséis hipótesis evaluadas (`hypothesize`). Las que cargan peso:

- **`flow-across-lines` refutada**: los pares fin→inicio de línea son
  combinaciones al azar (1,2× el nulo). Cada línea es una celda.
- **`productive-grammar` refutada**: muestrear la gramática inducida no
  genera formas nuevas válidas — el léxico es *seleccionado*, no
  *generado*. Mata el argumento fuerte de Timm/Schinner.
- **`qo-frontier`**: las ~124 violaciones de `q→o` se distribuyen
  proporcionales a la masa — la frontera es señal, no ruido de escriba.
- **`drift-profile`**: deriva real a grano quire, por sección temática,
  no por corte Currier ni por mano.

### La descomposición del mecanismo

`model-compare` compite cuatro explicaciones en igualdad de condiciones:
A (bigrama de palabras), B (catálogo i.i.d. sobre el léxico), C
(generador libre bajo el FSA inducido), D (autocita: copiar+mutar).
Resultado:

- El DL held-out elige **C** (0,26 Mb) — comprime sin mecanismo.
- La firma se descompone: **coll2/coll4→B** (suelo i.i.d. del léxico),
  **hapax/coll3/repmass→D** (exceso de autocita), fam→A.
- Ningún mecanismo solo la explica: el Voynich es **catálogo+autocita**.

Esto es compatible con una *lingua ignota lexical* — un nomenclátor
construido — pero no con una lengua construida en uso, que dejaría
sintaxis entre palabras.

## 4. Robustez a prueba de transcripción

La comparación formal (`compare`) entre las transcripciones ZL y
Takahashi muestra que solo coinciden en el **74,3%** de las palabras
(confusión top a↔o; desacuerdo concentrado en f72). Es un cuarto de
ruido potencial. Consecuencias medidas:

- Filtrado al subcorpus consenso (`--consensus-with`), la firma se
  mantiene: timm 0,984, orden libre 0,93, familias 13,4.
- El eco baja (z3 22,8→17,7) y la base exacta cae 263→187 — ~76 reglas
  apoyaban en lecturas disputadas.
- **Las 16 hipótesis replican su veredicto sobre el consenso.**
- Borrar `?` (lecturas inciertas) mueve solo el eco (22,8→16,3) y ~18
  reglas exactas.

## 5. El testbed de descifrado

`--map` re-codifica el corpus con cualquier candidato (unidad→fonema,
maximal-munch con fusión y borrado) y `testbed` compara firma y base de
reglas, contra un nulo de `--nulls N` relabelings del mismo mapa.

Aplicado a las 14 asignaciones del Apéndice 1 de Bax (2014): la firma se
mueve poco en conjunto, pero cae **fuera del nulo** en eco (17,2 vs
[20,9,30,6]), familias y out-degree — la asignación particular de
clusters toca estructura real. Un mapa 1:1 sería indistinguible del
nulo: lo que discrimina un descifrado es si fusiona unidades o rompe la
plantilla, no si "suena".

## 6. Limitaciones

- El DSL es estrictamente local: no puede expresar concordancia a
  distancia ni nada contexto-libre. Es el precio de la decidibilidad.
- El testbed evalúa firmas, no propone mapeos; y un candidato con poca
  cobertura deja poca señal que medir.
- Las clases son estructurales, no semánticas: "inventario" no dice
  *para qué* se inventariaba.

## Reproducir

```bash
pip install -e .
python -m millstone data/raw/ZL3b-n.txt hypothesize
python -m millstone data/raw/ZL3b-n.txt compare data/raw/IT2a-n.txt --signature
python -m millstone data/raw/ZL3b-n.txt --map data/maps/bax2014.map testbed --nulls 4
```
