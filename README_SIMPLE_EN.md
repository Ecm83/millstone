# millstone, explained simply

**What is this?** A program that looks at a text nobody can read (like
the Voynich Manuscript) and answers a different question: not "what does
it say?" but "**what kind of thing is it?**" — is it a real language, a
list, a cipher, a chanted text, a catalog?

## How it works (the short version)

1. **It counts things** in the text: which symbols can follow which
   others, where inside a word a symbol appears, which words repeat,
   how long the repetitions are.
2. **It writes rules**: "in this corpus, `q` is always followed by `o`",
   "this symbol never appears at the end of a word". Each rule is kept
   with its exact evidence — how many times it holds, how many times it
   fails.
3. **It compares against dummies**: it also analyzes shuffled versions
   of the text and fake texts built by known mechanisms (random,
   copy-and-mutate, dictionary-style). If the real text looks like a
   dummy, the "discovery" was noise.
4. **It gives a verdict**: the Voynich comes out as a **combinatorial
   inventory** — a list of entries built with a rigid internal template,
   with free word order and a hand-picked vocabulary. Like a seed
   catalog or an inventory, not like a novel or a conversation.

## Why it's trustworthy

- **Deterministic**: same corpus in, same answer out. No guessing.
- **Self-refuting**: the rules are tested against shuffled texts. If a
  rule would also hold on random text, it doesn't count.
- **Triple-checked**: it holds up when you only keep the 74% of words
  that two independent transcribers agree on.
- **It has been wrong on purpose**: we fed it fake corpora, real
  ciphers, and known languages to see if it tells them apart. It does.

## What it does NOT do

- It doesn't translate or decipher anything.
- It doesn't use AI models or GPT: it's pure counting and logic.
- It doesn't claim the Voynich is "solved" — it characterizes what kind
  of object it is.

## Files

- `README.md` / `README_EN.md` — the technical version
- `docs/FINDINGS.md` — all measured results with numbers
- `docs/PAPER.md` — the informal paper

Plain-language original: `README_SIMPLE.md` (Spanish).
