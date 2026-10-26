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
  solo-A: 125, solo-B: 57; ejemplos A-only: ["EndsWith(allowed=frozenset({'c', 'b', 'r', 'l', 'h', 'a', 'i', 'f', '?', 'o', 'd', 'p', 't', 'g', 'j', 's', 'm', 'k', 'u', 'e', 'n', 'y'}))", "ForbidsBigram(pair=('?', 'b'))", "ForbidsBigram(pair=('?', 'm'))"]; B-only: ["ForbidsBigram(pair=('?', 'n'))", "ForbidsBigram(pair=('?', 'x'))", "ForbidsBigram(pair=('c', '?'))"]
- **REFUTA** la frontera de q->o difiere entre A y B  
  viol. q->o: A=0.2619% (11073), B=0.3860% (23837)

## `free-word-order`

> El orden de palabras es libre (codebook): el out-degree de tipos frecuentes es igual al del corpus con líneas barajadas.

- **SOPORTA** out-degree real ~= barajado (orden libre)  
  media real/barajado=0.93 | ej. daiin real=405 barajado=442 | top=50 tipos

## `initial-effect`

> El símbolo inicial de la primera palabra de línea/párrafo no sigue la distribución marginal de símbolos iniciales.

- **SOPORTA** símbolo inicial de line sesgado  
  18 unidades | top: 'p' 5.00x | 'p': 5.0x marginal (384/5376, base 1.4%); 't': 2.8x marginal (407/5376, base 2.7%); 'y': 2.7x marginal (719/5376, base 5.0%); 'f': 2.3x marginal (40/5376, base 0.3%)
- **SOPORTA** símbolo inicial de paragraph sesgado  
  17 unidades | top: 'p' 11.57x | 'p': 11.6x marginal (106/641, base 1.4%); 't': 3.6x marginal (62/641, base 2.7%); 'k': 2.5x marginal (53/641, base 3.3%)
- **SOPORTA** existen duplicados adyacentes de palabra  
  291/32837 pares adyacentes idénticos (0.89%)

## `natural-language`

> El corpus tiene estadísticas de lengua natural: cola Zipfiana, funcionales dominantes, longitudes variadas.

- **SOPORTA** cola Zipfiana (hapax >= 40% de tipos)  
  hapax=71.0% (5979/8424 tipos)
- **REFUTA** palabras funcionales dominantes (top-10 >= 15% tokens)  
  top-10 cubre 12.1% de 38213 tokens
- **SOPORTA** longitudes variadas (>=20% fuera de media±1.5)  
  len media=5.06, fuera de rango=38.8%

## `qo-frontier`

> Las violaciones de q->o son ruido concentrado (mano/quire/folio), no una propiedad distribuida del lenguaje.

- **REFUTA** violaciones de q->o concentradas por mano  
  grupo top '2': 36.5% de violaciones con 28.8% de palabras | 2:46/11002, 3:42/11746, 1:28/10502, 4:5/3613, 5:3/889, @:2/461
- **REFUTA** violaciones de q->o concentradas por quire  
  grupo top 'T': 33.3% de violaciones con 28.5% de palabras | T:42/10894, M:37/6895, S:12/1560, N:6/2387, O:6/1428, I:5/1105, F:4/1648, G:3/1484, H:3/1517, C:2/1406, D:2/1181, Q:2/866, A:1/1428, E:1/1461, B:0/981, J:0/873, K:0/904, L:0/195
- **REFUTA** violaciones de q->o concentradas por lenguaje  
  grupo top 'B': 73.0% de violaciones con 62.4% de palabras | B:92/23837, A:29/11073, ?:5/3303

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
