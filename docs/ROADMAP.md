# Roadmap

millstone es un motor genérico de caracterización gramatical. El Voynich es el
caso de estudio estrella, no el sistema. Prioridades de arriba abajo.

## Fase 0 — Fundaciones

- [x] Skeleton: `pyproject.toml`, layout `src/`, pytest
- [x] Modelo de corpus genérico: jerarquía de niveles declarada por corpus.
      "Glifo/Folio/Línea" son instancias, no el esquema fijo.

## Fase 1 — `ingest`: adaptadores de fuente → modelo

Formato canónico interno (dataclasses puras) + adaptadores:

- [x] `synthetic.py` — genera corpus desde una gramática regular/CFG conocida.
      Clave para validación. Prioridad alta dentro de la fase.
- [x] `plaintext.py` — texto tokenizado genérico (lenguas conocidas).
- [x] `ivtff.py` — transcripción Voynich.
- [x] Transcripción: **Zandbergen-Landini** `ZL3b-n.txt` (EVA, IVTFF 2.0,
      voynich.nu). Takahashi queda como segunda fuente para comparar lecturas.
- [x] Test de humo Voynich: ~38k tokens, counts por folio contra literatura.

## Fase 2 — `engine` genérico

- [x] `CorpusView`: interfaz abstracta (iterar unidades, filtrar por nivel,
      n-gramas, contextos) + implementación en RAM.
- [x] DSL de restricciones: reglas como datos, no código. La regla `q → o`
      inicial se *expresa* en el DSL, no vive hardcodeada.
- [ ] Generación de negativos por restricción: frontera válido/inválido como
      dato consultable.
- [x] MDL: longitud de descripción de gramática + coste de codificar el corpus.
      Evita la trampa de "gramática que acepta todo".
- [ ] **Batería de calibración** (prioridad alta):
      - corpus sintético con gramática conocida → el motor la recupera
      - lengua real → recupera restricciones conocidas (p.ej. `ŋ` nunca
        inicia palabra en inglés)

## Fase 3 — Aplicación al Voynich

- [x] Ingest IVTFF + restricciones Voynich en el DSL. Ver `docs/FINDINGS.md`:
      `q→o` es casi-regla (~2% violaciones), `h` solo tras ligaduras EVA,
      `c` solo dentro de ligaduras, `b`/`h` nunca iniciales.
- [ ] Analizar la frontera de `q→o`: ¿las ~124 excepciones se concentran en
      folios/mano/sección concretos?
- [x] `hypotheses`: framework Evidence/Hypothesis + CurrierAB evaluada
      (gramáticas A/B difieren; frontera q→o es compartida — ver FINDINGS).
- [ ] Más hipótesis: generador tipo Timm, idioma natural, cifrado.
- [ ] Opción de excluir `?` (lecturas inciertas) del alfabeto en análisis.

## Fase 4 — `store` + `cli`

- [ ] Neo4j: persistencia del grafo físico + nodos de restricción/hipótesis con
      evidencia enlazada. Docker compose. Opcional e intercambiable.
- [x] CLI: `millstone <corpus> stats|discover|check|frontier|hypothesize`
      (`python -m millstone` o `pip install -e .`).

## Lógica del orden

- `ingest` primero: sin corpus no hay nada que caracterizar.
- `synthetic` y la calibración son prioritarias: son lo único que dice si el
  motor detecta gramática real o solo ruido. El Voynich no puede validar nada
  por sí solo.
- `engine` antes que `store`: el motor es el valor del proyecto y debe funcionar
  en RAM; Neo4j solo añadiría fricción.
- El DSL convierte la lógica específica de lengua de "código" a "datos".
