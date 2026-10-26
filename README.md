# millstone

Motor determinista de análisis lingüístico sobre el Manuscrito Voynich.

No es un LLM ni un analizador estadístico. Es una **IA simbólica** que caracteriza
la topología gramatical del corpus: grafo de conocimiento jerárquico + motor de
restricciones + validación por generación de negativos (métodos de Mill /
identificación de Gold / MDL).

## La idea

El Voynich es un corpus cerrado (~38k tokens) sin ground truth. No se puede
"aprender"; se puede *caracterizar*. millstone trata la gramática como un objeto
matemático:

- **Grafo jerárquico**: Glifo → Slot → Palabra → Línea → Párrafo → Folio → Sección
- **Restricciones**: reglas deterministas (posición de `q`, slots de sufijo,
  restricciones entre niveles) registradas como nodos con su evidencia enlazada
- **Negativos**: cada restricción define qué cadenas son inválidas → la frontera
  válido/inválido es el objeto de estudio
- **Hipótesis**: nodos de teoría (Currier A/B, generador tipo Timm, idioma
  natural, cifrado) con predicciones y refutaciones registradas en el grafo
- **Criterio**: MDL — la gramática correcta es la que comprime mejor el corpus

## Arquitectura

Capas desacopladas. Ninguna capa conoce la implementación de la de abajo, solo el
contrato:

```
millstone/
├── ingest/      IVTFF → modelo de corpus (dataclasses, sin dependencias de grafo)
├── store/       modelo → Neo4j (almacén + exploración visual; NO razona)
├── engine/      motor: unificación, restricciones, negativos, MDL
│                opera sobre CorpusView (interfaz abstracta; Neo4j o RAM)
├── hypotheses/  hipótesis como objetos: predicciones, refutaciones, geometrías
└── cli/         punto de entrada que conecta todo
```

Regla de oro: **desacoplado ≠ distribuido**. Un repo, módulos con fronteras
claras. `engine` funciona sobre un corpus en memoria en tests — Neo4j es
intercambiable.

## Estado

Esqueleto inicial. Próximos pasos:

- [ ] Elegir transcripción (Takahashi / Zandbergen-Landini, formato IVTFF)
- [ ] `ingest`: parser IVTFF → modelo de corpus
- [ ] `store`: persistencia Neo4j del grafo físico
- [ ] `engine`: primera restricción de validación (`q` → `o` en posición inicial)
- [ ] `hypotheses`: registro de teorías con evidencia
