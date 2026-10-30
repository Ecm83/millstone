# Characterizing, not learning: a deterministic engine for closed corpora

*Enric Castelló March — draft for preprint/venue submission*

## Abstract

Closed corpora — undeciphered scripts, constructed languages, ciphers
without keys — cannot be *learned*: they lack ground truth and their
very object class is unknown. We present **millstone**, a deterministic
symbolic engine that instead *characterizes* such corpora: a
hierarchical corpus model, a deliberately limited regular constraint
DSL with decidable entailment, Pareto frontier discovery with MDL
accounting, a pre-registered signature battery, and null models.
Calibrated on 11 corpora spanning natural language, administrative
records, refrains, a real deciphered cipher, and a constructed
nomenclator, the engine classifies the Voynich Manuscript as a
**combinatorial inventory** — rigid intra-word templates, free word
order, a selected lexicon — and produces clean refutations of
connected prose, generative grammar, and substitution cipher
hypotheses. All measurements replicate on the ZL∩Takahashi
transcription consensus (74.3% word agreement).

## 1. Introduction

The literature on undeciphered texts is saturated with *readings* —
candidate decipherments argued on semantic plausibility. What is scarce
are instruments that can **fail**: measurements that would have come
out negative if the corpus were something else. Our thesis: a closed
corpus should first be *characterized* as an object type (running
text, inventory, cipher, refrain text) before any reading is
attempted — and characterization must be falsifiable by construction.

## 2. Method

**Corpus model.** A corpus is a rooted tree with a per-corpus level
schema (e.g., symbol→word→line→paragraph→folio→section→corpus).
`CorpusView` abstracts over backends (RAM, Neo4j).

**Constraint DSL.** Eight deliberately restricted types —
adjacent-symbol relations (`FollowedBy`, `NextInSet`, `PrevInSet`,
`ForbidsBigram`) and edge membership (`StartsWith`, `EndsWith`,
`SymbolAt`, `OnlyInPosition`). Each is a strictly-local regular
property: `holds` is O(L), `negatives` enumerable, `entails` decidable
by table — far below Turing completeness by design.

**Discovery.** `discover` emits candidates with
`(support, checked, violations)` and does not filter; `prune` admits
only zero-violation rules into the MDL basis, removes entailed rules,
and reports `model_bits`/`data_bits`. Almost-rules persist as
evidence, never as law.

**Pre-registered battery.** `battery.yaml` (hash-versioned in the repo)
fixes ~12 metrics before any corpus is examined: hapax ratio, Heaps
growth, template coverage, word-order out-degree vs shuffled null,
intra-line repetition mass, verbatim echo z-scores (n=2,3), echo decay
geometry (`echo_slope`, `echo_nlast`).

**Null models.** Every metric is paired with a mechanical null
(intra-line shuffle) and generative controls (Markov order 1–4,
autocite, codebook). A metric that cannot lose is not a metric.

## 3. Calibration panel

| Corpus | Signature | Verdict |
|---|---|---|
| Culpeper 1653 | function words, open vocabulary | natural language |
| Copiale German (deciphered) | idem | natural language (check) |
| Cuneiform (sux) | 60% hapax + legal formulas | administrative |
| Indus | positional markers + 84% hapax | administrative seal |
| Linear A | 40% numerals, 90% hapax | palatial accounting |
| Proto-Elamite | vacuous rules | inventory |
| Rongorongo | verbatim echoes to n=9 | refrain text |
| Latin litany | echo tail to n=6 | liturgical refrain |
| **Copiale cipher** | letter-echo **+47** | real cipher |
| Lingua Ignota | categorical suffixes, 10% fam | constructed nomenclator |
| **Voynich** | template + free order + closed lexicon | **combinatorial inventory** |

## 4. The Voynich case

- **Flow across lines refuted**: end-of-line→start-of-line word pairs
  behave near shuffled nulls (1.2×) — each line is a cell, not prose.
- **Productive grammar refuted**: sampling the induced grammar yields
  2/5,000 unattested forms — the lexicon is *selected*.
- **Echo is lexical, not memory**: word-level echo z≈20, invariant
  under type bijection (18.3), absent in Markov orders 1–4, and
  unaffordable for a Kneser-Ney trigram (worst DL of 5 models).
- **Unique echo geometry**: the only cliff in the panel — collisions
  die at n=4 (slope −3.9); everything else tails to n=9–10.
- **A real cipher signs opposite**: Copiale letter-stream echo +47 vs
  Voynich −189.
- **Model decomposition**: no single mechanism explains the signature
  — catalogue (B) supplies collisions, autocitation (D) the excess
  hapax and intra-line repeats. DL vs behavior diverge honestly.
- **Drift is structured**: deleting `o` doesn't remove drift (it
  migrates to `y`/`h`); per-quire drift profiles of sibling
  constraints anti-correlate at r=−0.74.
- **Transcription robust**: all hypotheses replicate on the 74.3%
  ZL∩TT consensus; the exact-rule basis shrinks 263→187 honestly.

**Reading.** The best-supported interpretation is a combinatorial
inventory built by *selection and autocitation* — compatible with a
constructed nomenclator or systematic list, incompatible with
ordinary running text or substitution of natural prose. We label this
an interpretation: the panel measures position, and FINDINGS marks
the boundary explicitly.

## 5. Limitations

- Semantic evaluation of candidate decipherments is out of scope —
  the testbed measures structural consequences only.
- Classes have 1–2 members; positions are stable, neighborhoods thin.
- Scribe-vs-layout attribution (Q vs hand) unresolved.
- Uncertain readings (`?`) inflate exact-rule counts mildly
  (18 rules dropped when excluded).
- The DSL cannot express non-local agreement — an accepted trade-off
  for decidability.

## 6. Related work

Timm & Schinner (self-similar text / copy-mutation — our autocite
control); Reddy & Knight (word structure statistics); Currier
(A/B languages — our drift hypothesis); Sterneck; Bax (2014 — tested
as a candidate map, outside its relabeling null but signature
invariant); Knight, Megyesi & Schaefer (Copiale — our cipher control);
Desset et al. (Linear Elamite — future work).

## 7. Reproducibility

MIT-licensed: github.com/Ecm83/millstone — `pip install -e .`,
`pytest` (79 pass with no external data), `scripts/fetch_data.ps1`
downloads the redistributable corpora, `scripts/reproduce.ps1`
reproduces the battery. Software archived at
https://doi.org/10.5281/zenodo.23804059 — the hash of `battery.yaml`
is recorded in the findings document.
