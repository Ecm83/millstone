# millstone — explicado en cristiano

## ¿Qué es esto?

Es un programa que **analiza textos que nadie entiende** (como el famoso
Manuscrito Voynich) y te dice **cómo están construidos por dentro**, aunque
no sepas qué dicen.

Piénsalo como una radiografía de textos: no te dice *qué significa* el
mensaje, pero te muestra si el texto tiene huesos — reglas internas,
patrones, estructura — o si es un puñado de garabatos al azar.

## Lo que NO hace

- **No traduce** ni descifra nada. No te va a decir qué dice el Voynich.
- **No usa IA de las de ahora** (ni ChatGPT ni nada parecido). Todo es
  contar, comparar y aplicar reglas deterministas. Mismo texto, mismo
  resultado, siempre.
- **No adivina**: si el texto no tiene estructura, el programa lo dice
  y ya está. No se inventa reglas para quedar bien.

## ¿Cómo funciona, en tres ideas?

### 1. El texto es una caja dentro de otra caja

Cada corpus se organiza en pisos: símbolos forman palabras, palabras
forman líneas, líneas forman párrafos, párrafos forman páginas...

```
símbolo → palabra → línea → párrafo → folio → sección → corpus
```

### 2. El programa busca reglas de construcción

Busca patrones del tipo:

- "la letra `q` casi siempre va seguida de `o`"
- "ninguna palabra empieza por `b` ni por `h`"
- "la letra `m` prácticamente solo aparece al final de palabra"

La parte importante: el programa **también cuenta las veces que cada
regla se rompe**. Una regla con 5.000 aciertos y 3 fallos no es lo mismo
que una con 5.000 aciertos y 400 fallos. Esa frontera entre "regla
exacta" y "casi-regla" es justo lo que interesa estudiar.

### 3. Pone a prueba teorías

El programa evalúa hipótesis (17 incluidas, por ejemplo "¿el Voynich es
una lengua natural?", "¿el orden de las palabras importa?", "¿las dos
'linguas' del manuscrito son realmente distintas?") y para cada una dice:
**se sostiene** o **se cae**, con los números delante.

## ¿Y qué ha encontrado? (lo interesante)

Se probó contra 6 corpus de verdad. El mismo programa, sin trucos,
clasificó cada uno:

| Corpus | Lo que es | Qué encontró |
|---|---|---|
| **Voynich** (manuscrito indescifrado) | ¿? | Parece un **inventario combinatorio**: reglas rígidas *dentro* de cada palabra, pero orden libre *entre* palabras y vocabulario cerrado. No se comporta como una lengua con sintaxis. |
| **Escritura del Indo** | indescifrada | **Sellos administrativos**: marca al inicio, nombre en medio, marca al final. |
| **Lineal A** (Creta antigua) | indescifrada | **Contabilidad de palacio**: el 40% de los "tokens" son números. |
| **Proto-Elamita** (~3100 a.C.) | indescifrada | Igual: **contabilidad**. El patrón "cosa : cantidad" se recupera solo. |
| **Culpeper 1653** (inglés real) | lengua natural | Se comporta como debe: palabras funcionales frecuentes ("de", "el"...), vocabulario abierto. |
| **Sintético** | fabricado con reglas conocidas | Recupera la gramática exacta. Sirve de calibración: si el motor no recuperara esta, no valdría para nada. |

La moraleja: **saber si un texto desconocido es "una lengua", "una
contabilidad" o "un catálogo" es ya una respuesta** — y eso es lo que
entrega esta herramienta.

## Cómo se usa

Requiere Python 3.11 o superior. Sin dependencias obligatorias.

```bash
# instalar
pip install -e .

# ¿de qué está hecho el corpus? (conteos por nivel)
python -m millstone data/raw/ZL3b-n.txt stats

# encontrar las reglas gramaticales que el texto sigue
python -m millstone data/raw/ZL3b-n.txt discover

# comprobar una regla concreta: ¿la 'q' va siempre seguida de 'o'?
python -m millstone data/raw/ZL3b-n.txt check followedby:q:o

# ¿en qué partes del manuscrito se rompe la regla? (por mano, quire, sección)
python -m millstone data/raw/ZL3b-n.txt frontier followedby:q:o H

# evaluar una hipótesis (o todas, sin argumento)
python -m millstone data/raw/ZL3b-n.txt hypothesize natural-language

# generar un informe en markdown con todo
python -m millstone data/raw/ZL3b-n.txt report --out informe.md

# probar un candidato de descifrado (mapa glifo→fonema)
python -m millstone data/raw/ZL3b-n.txt --map data/maps/toy-latin.map testbed
```

Los corpus de prueba están en `data/raw/` (Voynich, Indo, Lineal A,
Proto-Elamita, Culpeper). El formato por defecto es IVTFF; para texto
plano usa `--format plaintext`.

### Extra opcional: ver el grafo

Si tienes Docker, puedes levantar una base de datos Neo4j para pasear el
corpus visualmente:

```bash
docker compose up -d
# abre http://localhost:7474 (usuario neo4j / contraseña millstone)
```

Totalmente opcional: el motor funciona igual en memoria sin Neo4j.

## ¿Dónde está cada cosa?

```
src/millstone/
├── model.py      las cajas: niveles del corpus (símbolo→folio)
├── ingest/       lectores: mete cada tipo de fuente en el modelo
├── engine/       el cerebro: busca reglas, cuenta violaciones, poda
├── hypotheses/   las 17 teorías a examen
├── store/        Neo4j (opcional, solo para visualizar)
└── cli/          los comandos de arriba
```

Tests: `pytest` (110 tests).

## Documentación en serio

- `docs/PAPER.md` — la nota informal con todos los números
- `README.md` — la versión técnica de esto
- `docs/FINDINGS.md` — todos los hallazgos con números
- `docs/REPORT.md` — el informe generado
- `docs/ROADMAP.md` — el estado del proyecto
- `docs/corpora/` — una ficha por cada corpus
