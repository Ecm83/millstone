"""millstone — CLI que conecta ingest, engine e hypotheses.

    millstone stats <corpus>
    millstone discover <corpus> [--exact] [--min-support N]
    millstone check <corpus> <regla>          p.ej. followedby:q:o
    millstone frontier <corpus> <regla> <attr>  p.ej. attr=H (mano)
    millstone hypothesize <corpus> [nombre]
"""

from __future__ import annotations

import argparse
import sys

from millstone.engine.check import alphabet, check
from millstone.engine.constraints import (
    EndsWith,
    FollowedBy,
    ForbidsBigram,
    NextInSet,
    OnlyInPosition,
    PrevInSet,
    StartsWith,
)
from millstone.engine.discover import discover
from millstone.engine.frontier import frontier_by_attr
from millstone.engine.mdl import prune
from millstone.engine.view import MemoryCorpusView
from millstone.hypotheses.currier import CurrierAB
from millstone.hypotheses.qo import QoFrontier
from millstone.hypotheses.timm import TimmSlots
from millstone.hypotheses.initial import InitialEffect
from millstone.ingest import ivtff, plaintext

HYPOTHESES = {
    "currier-ab": CurrierAB,
    "qo-frontier": QoFrontier,
    "timm-slots": TimmSlots,
    "initial-effect": InitialEffect,
}


def load(path: str, fmt: str):
    if fmt == "ivtff":
        return ivtff.parse_file(path)
    return plaintext.parse_file(path)


def parse_constraint(spec: str):
    """DSL textual: 'tipo:args', conjuntos separados por comas."""
    kind, *args = spec.split(":")
    if kind == "followedby":
        return FollowedBy(*args)
    if kind == "nextin":
        return NextInSet(args[0], frozenset(args[1].split(",")))
    if kind == "previn":
        return PrevInSet(args[0], frozenset(args[1].split(",")))
    if kind == "startswith":
        return StartsWith(frozenset(args[0].split(",")))
    if kind == "endswith":
        return EndsWith(frozenset(args[0].split(",")))
    if kind == "forbids":
        return ForbidsBigram(tuple(args[0].split(",")))
    if kind == "onlyat":
        return OnlyInPosition(args[0], int(args[1]))
    raise SystemExit(f"regla desconocida: {spec}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="millstone")
    p.add_argument("corpus", help="fichero de corpus (IVTFF o texto plano)")
    p.add_argument("--format", choices=["ivtff", "plaintext"], default="ivtff")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats")
    d = sub.add_parser("discover")
    d.add_argument("--level", default="word")
    d.add_argument("--min-support", type=int, default=5)
    d.add_argument("--exact", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("rule")
    c.add_argument("--level", default="word")
    f = sub.add_parser("frontier")
    f.add_argument("rule")
    f.add_argument("attr", help="atributo de folio (H mano, Q quire, L lengua)")
    h = sub.add_parser("hypothesize")
    h.add_argument("name", nargs="?", choices=sorted(HYPOTHESES))

    args = p.parse_args(argv)
    corpus = load(args.corpus, args.format)
    view = MemoryCorpusView(corpus)

    if args.cmd == "stats":
        for lv in corpus.schema.levels:
            print(f"{lv:>10}: {sum(1 for _ in corpus.nodes(lv))}")
        print("   alfabeto:", "".join(sorted(alphabet(view))))
        return 0

    if args.cmd == "discover":
        ds = discover(view, args.level, min_support=args.min_support)
        if args.exact:
            ds = [x for x in ds if x.violations == 0]
        r = prune(view, args.level, ds)
        print(f"{len(ds)} candidatas, base MDL exacta: {len(r.basis)}")
        for x in ds[:60]:
            tag = "exacta" if x.violations == 0 else f"viol={x.violations}"
            print(f"  {x.support:>6}  [{tag:>8}]  {x.constraint}")
        return 0

    if args.cmd == "check":
        res = check(view, args.level, parse_constraint(args.rule))
        print(f"{res.constraint}")
        print(f"  {res.checked} secuencias, {len(res.violations)} violaciones "
              f"({res.violation_rate:.3%})")
        for v in res.violations[:20]:
            print(f"    {v.locus}: {''.join(v.sequence)}")
        return 0 if res.holds else 1

    if args.cmd == "frontier":
        cells = frontier_by_attr(
            view, corpus, "word", parse_constraint(args.rule), args.attr
        )
        for k, cell in sorted(cells.items(), key=lambda kv: -kv[1].violations):
            print(f"  {k:>4}: {cell.violations}/{cell.checked} "
                  f"({cell.rate:.3%})")
        return 0

    if args.cmd == "hypothesize":
        names = [args.name] if args.name else sorted(HYPOTHESES)
        for name in names:
            h = HYPOTHESES[name]()
            print(f"== {h.name}: {h.statement}")
            for e in h.evaluate(corpus):
                mark = {True: "SOPORTA", False: "REFUTA", None: "?"}[e.supported]
                print(f"  [{mark:>7}] {e.prediction}\n            {e.detail}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
