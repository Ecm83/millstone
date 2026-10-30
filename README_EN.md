# millstone

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23804059.svg)](https://doi.org/10.5281/zenodo.23804059)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Deterministic grammatical-characterization engine for closed corpora.

Not an LLM, not a statistical analyzer. A **language-agnostic symbolic
system** that characterizes the grammatical topology of a corpus:
hierarchical knowledge graph + constraint engine + validation through
negative generation (Mill's methods / Gold identification / MDL).

Flagship case study: the **Voynich Manuscript** — the most famous
undeciphered closed corpus in the world. But the engine knows nothing
about Voynich: it works identically on Latin, English phonemes, or a
synthetic grammar.

## How to cite

Castelló March, E. (2026). *millstone: a deterministic symbolic engine
for grammatical characterization of closed corpora* (v0.1.1). Zenodo.
https://doi.org/10.5281/zenodo.23804059

## The idea

A closed corpus with no ground truth cannot be "learned" — it can be
*characterized*. millstone treats grammar as a mathematical object:

- **Hierarchical graph**: levels declared per corpus, e.g.
  Symbol → Word → Line → Paragraph → Folio → Section
- **Constraints**: deterministic rules in a generic DSL (positional,
  slot-based, cross-level), registered as nodes with linked evidence
- **Negatives**: every constraint defines which strings are invalid →
  the valid/invalid frontier is the object of study
- **Hypotheses**: theory nodes with predictions and refutations
  recorded in the graph
- **Criterion**: MDL — the correct grammar is the one that compresses
  the corpus best

## Calibration

Voynich has no ground truth, so it cannot validate the engine. millstone
calibrates first on corpora **with** known grammar:

- synthetic corpora generated from a given regular/CFG grammar → the
  engine must recover it
- real languages → the engine must recover known phonotactic constraints

Only a calibrated instrument is then applied to the Voynich.

## Architecture

Decoupled layers. No layer knows the implementation of the one below,
only the contract:

```
millstone/
├── model.py     generic corpus model (level schema + nodes)
├── ingest/      source adapters → model: ivtff (Voynich),
│                plaintext, synthetic, render + remap (recoding
│                and decipherment testbed), indus (ICIT), lineara
│                (GORILA), protoelam (CDLI), rongorongo (Barthel),
│                cuneiform (CDLI), copiale (cipher + deciphered German)
├── store/       model → Neo4j (storage + visual exploration; no reasoning)
├── engine/      engine: view, constraints (8 types), check, discover
│                (Pareto), mdl, frontier, induce, glyphs, metrics,
│                battery (pre-registered signature), generative (5 models),
│                transcription (ZL↔TT comparison + consensus)
│                runs on CorpusView (abstract interface; Neo4j or RAM)
├── hypotheses/  18 evaluated hypotheses: predictions, refutations,
│                frontier geometries — all with linked evidence
└── cli/         entry point wiring it all together
```

Golden rule: **decoupled ≠ distributed**. One repo, modules with clear
boundaries. `engine` runs on an in-memory corpus in tests — Neo4j is
interchangeable.

## Status

Working end-to-end, calibrated on **11 corpora** (see `docs/corpora/`
and `docs/FINDINGS.md` for measured results; `docs/PAPER.md` for the
informal write-up):

| Corpus | Detected signature | Verdict |
|---|---|---|
| **Voynich** (ZL + Takahashi) | intra-word template + free word order + closed lexicon | combinatorial inventory |
| **Indus** (ICIT/Mahadevan) | positional markers + 84% hapax cores | administrative seal |
| **Linear A** (GORILA/SigLA) | 40% numeric tokens + 90% hapax | palatial accounting |
| **Proto-Elamite** (CDLI) | vacuous rules on open alphabets | inventory / dark jargons |
| **Rongorongo** (Barthel) | verbatim echoes n≤9 across consecutive lines | refrain text |
| **Cuneiform** (sux, CDLI) | 60% hapax + legal formulas | administrative language |
| **Copiale** | letter-level echo +47 (opposite sign to Voynich) | real deciphered cipher (control) |
| **Culpeper 1653** | dominant function words, open vocabulary | natural language ✓ |
| **Lingua Ignota** (Hildegard) | categorical suffixes + 10% families | constructed nomenclator |
| **Latin litany** | echo tail to n=6 | liturgical refrain |
| **Synthetic** | grammar recovered exactly | oracle ✓ |

Data: corpora are not in the repo — `docs/data.md` lists sources and
download commands. `pytest` runs without data (synthetic controls).

CLI: `python -m millstone <corpus> stats|discover|check|frontier|
hypothesize|report|testbed|compare|battery|push`. Global options:
`--map FILE` (apply a decipherment candidate before any command),
`--consensus-with FILE` (robust core of two transcriptions),
`--with FILE` (second corpus, e.g. for `transcription-robust`),
`--format` (ivtff, plaintext, protoelam, rongorongo, cuneiform,
copiale, copiale-de). `testbed` compares original vs deciphered
signature including `--nulls N` randomized relabelings; `battery`
emits the pre-registered signature vector; `compare` measures
transcription agreement. Optional Neo4j: `docker compose up -d` +
`push` → navigable graph including the induced FSA.

## Key findings on Voynich

- **Flow across lines refuted**: line-end→line-start word pairs behave
  like shuffled nulls — each line is a cell, not prose.
- **Productive grammar refuted**: sampling the induced grammar yields
  2/5,000 unattested forms — the lexicon is *selected*, not *generated*.
- **Echo is lexical, not Markov**: word-level verbatim echo z≈20,
  unchanged by type-level recoding, absent in Markov models of any
  order (1–4) and unaffordable for a Kneser-Ney trigram (worst DL).
- **Echo geometry is unique**: the only "cliff" in the panel —
  collisions die at n=4, while everything else (natural language,
  ciphers, refrains, legal formulas) shows tails to n=9–10.
- **Transcription-robust**: all 18 hypotheses replicate on the 74.3%
  ZL∩Takahashi consensus subset.
- **A real cipher signs differently**: Copiale's letter stream has
  echo +47 vs Voynich's −189 — evidence against "Voynich = substituted
  natural text".

Best-supported reading: **a combinatorial inventory built by selection
and autocitation** — not a natural language in use, not a cipher of
plain text.
