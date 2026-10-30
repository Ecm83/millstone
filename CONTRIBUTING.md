# Contribuir a millstone

Reglas de oro del proyecto:

- **Determinista**: mismo corpus → mismo resultado. Nada de aleatoriedad
  sin `seed` explícita.
- **Nulos primero**: toda métrica se contrasta contra controles
  (barajado, modelos generativos). Una métrica que no puede perder no
  es una métrica.
- **Desacoplado ≠ distribuido**: cada capa solo conoce el contrato de
  la de abajo.

## Añadir un corpus nuevo

1. Escribe `src/millstone/ingest/<tufichero>.py` con `parse_file(path)`
   (o `parse_dir`) que devuelva un `Corpus` — declara un
   `CorpusSchema` con tus niveles (p.ej. `symbol→word→line→corpus`) y
   usa `Node`. Mira `ingest/copiale.py` como ejemplo mínimo.
2. Regístralo: añade el formato a `--format` en `cli/main.py` (`load()`).
3. Documenta: `docs/corpora/<nombre>.md` con fuente, schema y medidas.
4. Datos: NO subas `data/raw/` al repo (gitignored). Añade la fuente y
   el comando de descarga a `docs/data.md` (y a `scripts/fetch_data.ps1`
   si hay URL estable).
5. Test: `tests/test_<nombre>.py` — estructura del corpus, `validate()`.

## Añadir un tipo de restricción al DSL

El DSL es deliberadamente limitado (regular + bordes, para mantener
decidibilidad). Un tipo nuevo debe conservar:

- `holds(symbols) -> bool` en O(L)
- `negatives(alphabet)` enumerable
- implicación decidible: añade su entrada a `ENTAILS` en
  `engine/constraints.py`
- coste MDL bien definido: `model_bits`

Regístralo en `CONSTRAINT_TYPES` y en el dispatch de `discover` si
quieren candidatas de él. Con test de `holds`/`negatives`/`entails`.

Si tu idea no es local/regular (concordancia a distancia, conteo,
anidamiento) — discútela primero: la decisión de mantener el DSL por
debajo de Turing-completo es de diseño, no de pereza.

## Añadir una hipótesis

`hypotheses/<nombre>.py` con una clase que exponga `name`, `statement`
y `evaluate(corpus) -> list[Evidence]` (`supported` True/False/None).
Regístrala en `HYPOTHESES` en `cli/main.py`. Si necesita un segundo
corpus, marca `needs_two = True` y toma `--with FILE`.

## Tests

```bash
pip install -e .[dev]
python -m pytest -x -q      # 79+ verdes sin datos externos
python -m pytest tests -k <nombre> -q
```

Los tests de corpus reales se saltan si falta `data/raw/` — los
sintéticos (`ingest/synthetic.py`) calibran el motor siempre.

## Estilo

Código compacto, español en docs/comentarios, inglés también aceptado
en código. Nada de comentarios que repiten lo que dice la línea de al
lado.
