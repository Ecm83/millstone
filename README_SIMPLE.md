# millstone â€” explicado en cristiano

## Â¿QuÃ© es esto?
English: README_SIMPLE_EN.md

Es un programa que **analiza textos que nadie entiende** (como el famoso
Manuscrito Voynich) y te dice **cÃ³mo estÃ¡n construidos por dentro**, aunque
no sepas quÃ© dicen.

PiÃ©nsalo como una radiografÃ­a de textos: no te dice *quÃ© significa* el
mensaje, pero te muestra si el texto tiene huesos â€” reglas internas,
patrones, estructura â€” o si es un puÃ±ado de garabatos al azar.

## Lo que NO hace

- **No traduce** ni descifra nada. No te va a decir quÃ© dice el Voynich.
- **No usa IA de las de ahora** (ni ChatGPT ni nada parecido). Todo es
  contar, comparar y aplicar reglas deterministas. Mismo texto, mismo
  resultado, siempre.
- **No adivina**: si el texto no tiene estructura, el programa lo dice
  y ya estÃ¡. No se inventa reglas para quedar bien.

## Â¿CÃ³mo funciona, en tres ideas?

### 1. El texto es una caja dentro de otra caja

Cada corpus se organiza en pisos: sÃ­mbolos forman palabras, palabras
forman lÃ­neas, lÃ­neas forman pÃ¡rrafos, pÃ¡rrafos forman pÃ¡ginas...

```
sÃ­mbolo â†’ palabra â†’ lÃ­nea â†’ pÃ¡rrafo â†’ folio â†’ secciÃ³n â†’ corpus
```

### 2. El programa busca reglas de construcciÃ³n

Busca patrones del tipo:

- "la letra `q` casi siempre va seguida de `o`"
- "ninguna palabra empieza por `b` ni por `h`"
- "la letra `m` prÃ¡cticamente solo aparece al final de palabra"

La parte importante: el programa **tambiÃ©n cuenta las veces que cada
regla se rompe**. Una regla con 5.000 aciertos y 3 fallos no es lo mismo
que una con 5.000 aciertos y 400 fallos. Esa frontera entre "regla
exacta" y "casi-regla" es justo lo que interesa estudiar.

### 3. Pone a prueba teorÃ­as

El programa evalÃºa hipÃ³tesis (17 incluidas, por ejemplo "Â¿el Voynich es
una lengua natural?", "Â¿el orden de las palabras importa?", "Â¿las dos
'linguas' del manuscrito son realmente distintas?") y para cada una dice:
**se sostiene** o **se cae**, con los nÃºmeros delante.

## Â¿Y quÃ© ha encontrado? (lo interesante)

Se probÃ³ contra 6 corpus de verdad. El mismo programa, sin trucos,
clasificÃ³ cada uno:

| Corpus | Lo que es | QuÃ© encontrÃ³ |
|---|---|---|
| **Voynich** (manuscrito indescifrado) | Â¿? | Parece un **inventario combinatorio**: reglas rÃ­gidas *dentro* de cada palabra, pero orden libre *entre* palabras y vocabulario cerrado. No se comporta como una lengua con sintaxis. |
| **Escritura del Indo** | indescifrada | **Sellos administrativos**: marca al inicio, nombre en medio, marca al final. |
| **Lineal A** (Creta antigua) | indescifrada | **Contabilidad de palacio**: el 40% de los "tokens" son nÃºmeros. |
| **Proto-Elamita** (~3100 a.C.) | indescifrada | Igual: **contabilidad**. El patrÃ³n "cosa : cantidad" se recupera solo. |
| **Culpeper 1653** (inglÃ©s real) | lengua natural | Se comporta como debe: palabras funcionales frecuentes ("de", "el"...), vocabulario abierto. |
| **SintÃ©tico** | fabricado con reglas conocidas | Recupera la gramÃ¡tica exacta. Sirve de calibraciÃ³n: si el motor no recuperara esta, no valdrÃ­a para nada. |

La moraleja: **saber si un texto desconocido es "una lengua", "una
contabilidad" o "un catÃ¡logo" es ya una respuesta** â€” y eso es lo que
entrega esta herramienta.

## CÃ³mo se usa

Requiere Python 3.11 o superior. Sin dependencias obligatorias.

```bash
# instalar
pip install -e .

# Â¿de quÃ© estÃ¡ hecho el corpus? (conteos por nivel)
python -m millstone data/raw/ZL3b-n.txt stats

# encontrar las reglas gramaticales que el texto sigue
python -m millstone data/raw/ZL3b-n.txt discover

# comprobar una regla concreta: Â¿la 'q' va siempre seguida de 'o'?
python -m millstone data/raw/ZL3b-n.txt check followedby:q:o

# Â¿en quÃ© partes del manuscrito se rompe la regla? (por mano, quire, secciÃ³n)
python -m millstone data/raw/ZL3b-n.txt frontier followedby:q:o H

# evaluar una hipÃ³tesis (o todas, sin argumento)
python -m millstone data/raw/ZL3b-n.txt hypothesize natural-language

# generar un informe en markdown con todo
python -m millstone data/raw/ZL3b-n.txt report --out informe.md

# probar un candidato de descifrado (mapa glifoâ†’fonema)
python -m millstone data/raw/ZL3b-n.txt --map data/maps/toy-latin.map testbed
```

Los corpus de prueba estÃ¡n en `data/raw/` (Voynich, Indo, Lineal A,
Proto-Elamita, Culpeper). El formato por defecto es IVTFF; para texto
plano usa `--format plaintext`.

### Extra opcional: ver el grafo

Si tienes Docker, puedes levantar una base de datos Neo4j para pasear el
corpus visualmente:

```bash
docker compose up -d
# abre http://localhost:7474 (usuario neo4j / contraseÃ±a millstone)
```

Totalmente opcional: el motor funciona igual en memoria sin Neo4j.

## Â¿DÃ³nde estÃ¡ cada cosa?

```
src/millstone/
â”œâ”€â”€ model.py      las cajas: niveles del corpus (sÃ­mboloâ†’folio)
â”œâ”€â”€ ingest/       lectores: mete cada tipo de fuente en el modelo
â”œâ”€â”€ engine/       el cerebro: busca reglas, cuenta violaciones, poda
â”œâ”€â”€ hypotheses/   las 17 teorÃ­as a examen
â”œâ”€â”€ store/        Neo4j (opcional, solo para visualizar)
â””â”€â”€ cli/          los comandos de arriba
```

Tests: `pytest` (110 tests).

## DocumentaciÃ³n en serio

- `docs/PAPER.md` â€” la nota informal con todos los nÃºmeros
- `README.md` â€” la versiÃ³n tÃ©cnica de esto
- `docs/FINDINGS.md` â€” todos los hallazgos con nÃºmeros
- `docs/REPORT.md` â€” el informe generado
- `docs/ROADMAP.md` â€” el estado del proyecto
- `docs/corpora/` â€” una ficha por cada corpus
