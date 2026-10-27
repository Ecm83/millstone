# Reporte millstone

## `closed-lexicon`

> El vocabulario es un léxico cerrado: el modelo posicional inducido sobre-genera por órdenes de magnitud -> las palabras son un inventario seleccionado, no producidas libremente.

- **SOPORTA** el modelo secuencial sobre-genera el vocabulario  
  |lenguaje bigrama| = 4.74e+16 vs vocab 8424 -> ratio 6e+12x
- **SOPORTA** el modelo posicional sigue sobre-generando (léxico cerrado)  
  |lenguaje slots| = 2.10e+12 vs vocab 8424 -> ratio 2e+08x; log2: 28 bits de selección por tipo

## `currier-ab`

> Los folios etiquetados $L=A y $L=B siguen gramáticas distintas: no es ruido de transcripción sino estructura.

- **SOPORTA** particiones A/B no vacías  
  A=11073 palabras, B=23837
- **SOPORTA** los conjuntos de reglas exactas difieren  
  solo-A: 125, solo-B: 57; ejemplos A-only: ["EndsWith(allowed=frozenset({'b', 'n', 'd', 's', 'p', '?', 'a', 'f', 'o', 'i', 'm', 'e', 'u', 'h', 'g', 'l', 'y', 't', 'k', 'r', 'c', 'j'}))", "ForbidsBigram(pair=('?', 'b'))", "ForbidsBigram(pair=('?', 'm'))"]; B-only: ["ForbidsBigram(pair=('?', 'n'))", "ForbidsBigram(pair=('?', 'x'))", "ForbidsBigram(pair=('c', '?'))"]
- **REFUTA** la frontera de q->o difiere entre A y B  
  viol. q->o: A=0.2619% (11073), B=0.3860% (23837)

## `drift-profile`

> La deriva de las casi-reglas entre regiones sigue el corte Currier A/B (salto categórico entre sublenguajes) más que una evolución gradual a lo largo de los quires.

- **REFUTA** la deriva se alinea con el corte Currier ($L)  
  0/10 reglas con gap entre lenguas > dispersión intra-lengua | mediana Δlengua=19.4% vs intra=34.9% | PrevInSet(symbol='o', allowed=frozenset({'h'})): Δlengua=26.4% vs intra=35.1%; PrevInSet(symbol='o', allowed=frozenset({'q', 'd', 'h', 'n', 's', 'l', 'p', 'y', 'f', 't', 'k', 'o', 'i', 'r', 'm', 'e'})): Δlengua=19.9% vs intra=29.6%; PrevInSet(symbol='o', allowed=frozenset({'q', 'd', 't', 'h', 'k', 's', 'l', 'e'})): Δlengua=20.3% vs intra=30.6%
- **SOPORTA** residual gradual dentro de lengua, por encima del nulo mecánico  
  dispersión intra-lengua mediana real=34.9% vs barajado=11.3% sobre 10 reglas
- **SOPORTA** el gap Currier supera al corpus barajado (Mill: diferencia)  
  Δlengua mediana real=19.4% vs barajado=0.9%

## `flow-across-lines`

> El texto fluye entre líneas (prosa continua): los pares fin-de-línea → inicio-de-línea se comportan como bigramas de palabra atestiguados, no como combinaciones al azar.

- **REFUTA** los pares cross-line son bigramas atestiguados (flujo)  
  5.7% de 4735 pares cross-line son bigramas internos vs nulo 4.9% (1.2x)

## `free-word-order`

> El orden de palabras es libre (codebook): el out-degree de tipos frecuentes es igual al del corpus con líneas barajadas.

- **SOPORTA** out-degree real ~= barajado (orden libre)  
  media real/barajado=0.93 | ej. daiin real=405 barajado=442 | top=50 tipos

## `holdout-replication`

> Las restricciones inducidas sobre la mitad A del corpus son propiedades estables del lenguaje: se replican con tasa de violación similar sobre la mitad B reservada, y no sobre B barajada.

- **SOPORTA** reglas exactas de A replican en B  
  41/41 reglas exactas en A con tasa <= 2% en B
- **SOPORTA** casi-reglas mantienen su frontera en B  
  59/59 dentro de tolerancia (4 sigma)
- **SOPORTA** la replicación supera al corpus barajado (Mill: diferencia)  
  real=100.0% vs barajado=37.0% sobre 100 reglas

## `initial-effect`

> El símbolo inicial de la primera palabra de línea/párrafo no sigue la distribución marginal de símbolos iniciales.

- **SOPORTA** símbolo inicial de line sesgado  
  18 unidades | top: 'p' 5.00x | 'p': 5.0x marginal (384/5376, base 1.4%); 't': 2.8x marginal (407/5376, base 2.7%); 'y': 2.7x marginal (719/5376, base 5.0%); 'f': 2.3x marginal (40/5376, base 0.3%)
- **SOPORTA** símbolo inicial de paragraph sesgado  
  17 unidades | top: 'p' 11.57x | 'p': 11.6x marginal (106/641, base 1.4%); 't': 3.6x marginal (62/641, base 2.7%); 'k': 2.5x marginal (53/641, base 3.3%)
- **SOPORTA** existen duplicados adyacentes de palabra  
  291/32837 pares adyacentes idénticos (0.89%)

## `line-clustering`

> Las palabras se agrupan por línea más que bajo azar (estructura temática/catalográfica); si no, orden libre total.

- **SOPORTA** repetición intra-línea supera el barajado global  
  masa repetida: real=7.2% vs nulo=2.9% (2.5x) en 5376 líneas

## `natural-language`

> El corpus tiene estadísticas de lengua natural: cola Zipfiana, funcionales dominantes, longitudes variadas.

- **SOPORTA** cola Zipfiana (hapax >= 40% de tipos)  
  hapax=71.0% (5979/8424 tipos)
- **REFUTA** palabras funcionales dominantes (top-10 >= 15% tokens)  
  top-10 cubre 12.1% de 38213 tokens
- **SOPORTA** longitudes variadas (>=20% fuera de media±1.5)  
  len media=5.06, fuera de rango=38.8%

## `paradigmatic-families`

> El vocabulario forma familias a 1 edición por encima de lo que permite el azar: las palabras son variantes de plantillas.

- **SOPORTA** fracción con vecino a 1 edición > vocabulario barajado  
  real=73.7% vs nulo=23.3% (3.2x)

## `qo-frontier`

> Las violaciones de q->o son ruido concentrado (mano/quire/folio), no una propiedad distribuida del lenguaje.

- **REFUTA** violaciones de q->o concentradas por mano  
  grupo top '2': 36.5% de violaciones con 28.8% de palabras | 2:46/11002, 3:42/11746, 1:28/10502, 4:5/3613, 5:3/889, @:2/461
- **REFUTA** violaciones de q->o concentradas por quire  
  grupo top 'T': 33.3% de violaciones con 28.5% de palabras | T:42/10894, M:37/6895, S:12/1560, N:6/2387, O:6/1428, I:5/1105, F:4/1648, G:3/1484, H:3/1517, C:2/1406, D:2/1181, Q:2/866, A:1/1428, E:1/1461, B:0/981, J:0/873, K:0/904, L:0/195
- **REFUTA** violaciones de q->o concentradas por lenguaje  
  grupo top 'B': 73.0% de violaciones con 62.4% de palabras | B:92/23837, A:29/11073, ?:5/3303

## `regional-replication`

> Las restricciones inducidas sobre la primera mitad del documento se mantienen en la segunda mitad: la gramática caracterizada es estacionaria entre regiones del corpus, no solo entre muestras intercaladas.

- **SOPORTA** reglas exactas de A replican en B  
  48/48 reglas exactas en A con tasa <= 2% en B
- **REFUTA** casi-reglas mantienen su frontera en B  
  30/52 dentro de tolerancia (4 sigma) | peores: PrevInSet(symbol='o', allowed=frozenset({'h'})): 44.50% -> 53.67%; PrevInSet(symbol='o', allowed=frozenset({'h', 'q'})): 35.13% -> 39.45%; PrevInSet(symbol='o', allowed=frozenset({'k', 'q', 'h', 'd', 't', 'e'})): 25.67% -> 28.46%
- **SOPORTA** la replicación supera al corpus barajado (Mill: diferencia)  
  real=78.0% vs barajado=42.0% sobre 100 reglas

## `timm-slots`

> El vocabulario se genera por composición de slots: bigramas inducidos en train aceptan casi todo held-out, y mucho más que sobre el corpus barajado.

- **SOPORTA** cobertura held-out alta (estructura de plantilla)  
  99.8% de 7643 palabras held-out aceptadas (364 bigramas de 30570 train)
- **SOPORTA** la cobertura supera al corpus barajado (Mill: diferencia)  
  real=99.8% vs barajado=51.6% (error x247 menor)

## `uncertain-space`

> Los espacios inciertos `,` son en su mayoría cortes de palabra reales: su distribución de pares se parece a `.`, no a bigramas internos — con una subpoblación continuadora (l/r/o elevados).

- **SOPORTA** los `,` se distribuyen como cortes de palabra, no como continuaciones  
  TV(`,`, `.`)=0.385 < TV(`,`, interno)=0.676
- **—** perfil de los espacios inciertos  
  2743 casos | top pares: 'ra'(286), 'lk'(147), 'lc'(145), 'ls'(125), 'sa'(124), 'yk'(101), 'ol'(94), 'ld'(89) | primer símbolo: `,` mezcla final(77%) con elevación interna en l/r/o

## `verbatim-echo`

> Las colisiones verbatim entre líneas (n=2..5) se desvían del nulo combinatorio intra-línea: hay eco estructurado (exceso) o supresión de repeticiones (defecto).

- **SOPORTA** los conteos verbatim se desvían del nulo combinatorio (|z| > 2 en algún n)  
  n=2: real=2389 vs nulo=2115±32 [2065-2183] z=+8.6 | n=3: real=155 vs nulo=38±6 [24-50] z=+20.0 | n=4: real=1 vs nulo=0±1 [0-2] z=+1.4 | n=5: real=0 vs nulo=0±0 [0-0] z=+0.0
- **REFUTA** la colisión n=4 comparte contexto en ambos loci (eco más largo que el propio n-grama)  
  0 vecinos compartidos | ol shedy qokedy qokeedy @ f75v.47: «dar ol shedy qokedy qokeedy qotar» | ol shedy qokedy qokeedy @ f84r.22: «qokal ol shedy qokedy qokeedy qokeedy»
- **SOPORTA** la colisión es intra-mano/quire (eco local de escriba, no cita global)  
  loci: f75v.47, f84r.22 | atributos compartidos: Q=M, L=B, H=2
