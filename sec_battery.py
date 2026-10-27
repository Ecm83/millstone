import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from millstone.ingest import ivtff
from millstone.model import subcorpus
from millstone.engine.view import MemoryCorpusView
from millstone.engine.battery import run_battery

corpus = ivtff.parse_file("data/raw/ZL3b-n.txt")
secs = [(n.locus or str(i), n) for i, n in enumerate(corpus.nodes("section"))]
print(len(secs), "secciones")
for name, _ in secs:
    sub = subcorpus(corpus, "section", lambda n, k=name: (n.locus or "") == k)
    v = MemoryCorpusView(sub)
    lines = [list(s.symbols) for s in v.unit_sequences("line", "word") if s.symbols]
    n_tok = sum(len(l) for l in lines)
    vec = run_battery(lines, n_tokens=min(2000, n_tok), reps=10)
    if vec is None:
        print(f"{name:>12}: {n_tok} tokens — insuficiente")
        continue
    print(f"{name:>12}: {n_tok} tok | hapax={vec['hapax']:.3g} "
          f"heaps={vec['heaps_beta']:.3g} timm={vec['timm']:.3g} "
          f"fam={vec['families']:.3g} outdg={vec['outdeg']:.3g} "
          f"echo3={vec['echo_z3']:.3g}")
