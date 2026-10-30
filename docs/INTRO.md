# What millstone measures (and what it doesn't)

*A plain-language introduction to the engine and its results.*

millstone is a deterministic engine that characterizes the **internal
structure** of a closed corpus — what kind of object it is — without
translating it or inventing meanings. Given a text nobody can read,
it doesn't ask "what does it say?" but "does it behave like language,
a list, a cipher, a chant?"

## The instrument

Every finding is produced by the same loop:

1. **Constraints**: 8 deliberately limited rule types (adjacent-symbol
   relations, edge positions). Every candidate rule ships with its
   violation count — rules that fail are kept as evidence, not hidden.
2. **A pre-registered signature battery**: ~12 metrics fixed in
   `battery.yaml` *before* looking at a new corpus — hapax ratio,
   Heaps growth, template coverage, word-order freedom, verbatim echo
   z-scores, echo decay geometry.
3. **Null models**: every metric is compared against shuffled versions
   and generative controls (Markov, autocite, codebook). A metric that
   can't lose isn't a metric.
4. **Hypotheses**: 18 explicit theories with registered predictions —
   including ones designed to *fail* (that's how you learn what the
   corpus is not).

Nothing is learned by a neural net. Same corpus → same result.

## The panel — 11 corpora, one space

| Corpus | Signature | Reading |
|---|---|---|
| Culpeper 1653 | function words dominate, open vocabulary | natural language |
| German deciphered Copiale | same shape | natural language (check) |
| Cuneiform (sux) | 60% hapax + legal formulas | administrative language |
| Indus | positional markers, 84% hapax cores | administrative seal |
| Linear A | 40% numerals, 90% hapax | palatial accounting |
| Proto-Elamite | vacuous rules on open alphabets | inventory |
| **Voynich** | word template + free order + closed lexicon | **combinatorial inventory** |
| Lingua Ignota | categorical suffixes, 10% families | constructed nomenclator |
| Rongorongo | verbatim echoes to n=9 | refrain text |
| Latin litany | echo tail to n=6 | liturgical refrain |
| Copiale cipher | letter-echo **+47** | real cipher |

## The three results worth knowing

- **Voynich signs like nothing else** — it's the only corpus whose
  verbatim echo dies at n=4 (a cliff, slope −3.9) while everything
  else tails out to n=9–10. Not prose, not a refrain, not a cipher.
- **A real cipher signs *opposite* to the Voynich**: Copiale's letter
  stream carries the plaintext's n-gram statistics (echo +47); the
  Voynich *suppresses* collisions (−189). "Voynich = substituted
  natural text" is measurably weak.
- **The lexicon is selected, not generated**: sampling the induced
  grammar produces 2/5,000 unattested forms. It behaves like a
  catalogue built by selection and autocitation — not a language in
  use, not a free combinatorial generator.

## What it doesn't do

- It doesn't decipher anything and can't validate proposed readings —
  its decipherment testbed only measures *structural* consequences of
  a candidate mapping (Bax 2014 tested: outside its null, but the
  signature stays "inventory").
- It characterizes object types, not authorial intent. "Combinatorial
  inventory" is compatible with a constructed nomenclator or a
  systematic fake — the engine can't tell honest work from hoax.
- Classes are small (1–2 members each). The position is measured;
  the labels are interpretation, and FINDINGS.md says so explicitly.

## Reproduce it

`pip install -e .` → `pytest` (79 green without data) →
`scripts/fetch_data.ps1` + `scripts/reproduce.ps1` for real corpora.
MIT licensed, DOI-citable: https://doi.org/10.5281/zenodo.23804059
