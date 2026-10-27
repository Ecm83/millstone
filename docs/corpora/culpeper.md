# Culpeper's Complete Herbal (1653) — control de lengua natural

**Fuente**: Project Gutenberg #49513 (`data/raw/culpeper.txt`).
**Adaptador**: `ingest/plaintext.py` ·
**Niveles**: `symbol → word → sentence → corpus`

Corpus de calibración de género: herbario médico-astrológico de la
época del Voynich — el mejor test de "¿se parece el MS a un texto
alquímico real de su siglo?".

## Firma vs Voynich

| métrica | Culpeper | Voynich |
|---|---|---|
| tipos / tokens | 10.052 / 250.482 | 8.424 / 38.213 |
| TTR | 0,040 | 0,220 |
| hapax | 42,8% | 71,0% |
| top-10 tokens | **28,5%** | 12,1% |
| familias 1-ed | 35,8% | **73,7%** |
| tipos con triples | 8 | **341** |

**Veredicto**: la firma del Voynich es incomparable con prosa real de
su época — Culpeper tiene funcionales dominantes y vocabulario abierto;
el MS es un objeto de otra clase (inventario/código, no texto sobre
plantas en otra lengua).

## Findings

## Control externo: Culpeper's Complete Herbal (1653)

La batería completa contra un herbario médico-astrológico real de la
época del manuscrito:

| métrica | Voynich | Culpeper |
|---|---|---|
| tipos / tokens | 8.424 / 38.213 | 10.052 / 250.482 |
| TTR | 0,220 | 0,040 |
| hapax | 71,0% | 42,8% |
| len media | 5,1 | 4,5 |
| top-10 | 12,1% | **28,5%** |
| familias 1-ed | **73,7%** | 35,8% |
| tipos con triples | **341** | 8 |

Un texto alquímico real es lengua natural completa: funcionales
dominantes, vocabulario abierto, casi sin triples, pocas familias. La
firma Voynich es incomparable con prosa de su época — el corpus no es
"texto sobre plantas en otro idioma", es otra clase de objeto.
