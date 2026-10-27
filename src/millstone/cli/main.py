"""millstone — CLI que conecta ingest, engine e hypotheses.

    millstone stats <corpus>
    millstone discover <corpus> [--exact] [--min-support N]
    millstone check <corpus> <regla>          p.ej. followedby:q:o
    millstone frontier <corpus> <regla> <attr>  p.ej. attr=H (mano)
    millstone hypothesize <corpus> [nombre]
    millstone <corpus> --map <mapa> testbed   candidato de descifrado
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
from millstone.hypotheses.lexicon import ClosedLexicon
from millstone.hypotheses.spaces import UncertainSpace
from millstone.hypotheses.natural import NaturalLanguage
from millstone.hypotheses.wordorder import FreeWordOrder
from millstone.hypotheses.families import ParadigmaticFamilies
from millstone.hypotheses.clustering import LineClustering
from millstone.hypotheses.flow import FlowAcrossLines
from millstone.hypotheses.replication import (
    HoldoutReplication,
    RegionalReplication,
)
from millstone.hypotheses.drift import DriftProfile
from millstone.hypotheses.echo import VerbatimEcho
from millstone.hypotheses.modelcompare import ModelCompare
from millstone.ingest import ivtff, plaintext

HYPOTHESES = {
    "currier-ab": CurrierAB,
    "qo-frontier": QoFrontier,
    "timm-slots": TimmSlots,
    "initial-effect": InitialEffect,
    "closed-lexicon": ClosedLexicon,
    "uncertain-space": UncertainSpace,
    "natural-language": NaturalLanguage,
    "free-word-order": FreeWordOrder,
    "paradigmatic-families": ParadigmaticFamilies,
    "line-clustering": LineClustering,
    "flow-across-lines": FlowAcrossLines,
    "holdout-replication": HoldoutReplication,
    "regional-replication": RegionalReplication,
    "drift-profile": DriftProfile,
    "verbatim-echo": VerbatimEcho,
    "model-compare": ModelCompare,
}


def load(path: str, fmt: str):
    if fmt == "ivtff":
        return ivtff.parse_file(path)
    if fmt == "protoelam":
        from millstone.ingest import protoelam

        return protoelam.parse_file(path)
    if fmt == "rongorongo":
        from millstone.ingest import rongorongo

        return rongorongo.parse_dir(path)
    if fmt == "cuneiform":
        from millstone.ingest import cuneiform

        return cuneiform.parse_file(path)
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
    p.add_argument(
        "--format",
        choices=["ivtff", "plaintext", "protoelam", "rongorongo", "cuneiform"],
        default="ivtff",
    )
    p.add_argument(
        "--map", dest="mapfile", metavar="FILE",
        help="mapeo unidad→fonema: re-codifica el corpus antes de correr",
    )
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
    r = sub.add_parser("report", help="corre todas las hipótesis y vuelca markdown")
    r.add_argument("--out", help="fichero de salida (stdout por defecto)")
    tb = sub.add_parser("testbed", help="evalúa un candidato de descifrado (--map)")
    tb.add_argument(
        "--nulls", type=int, default=0, metavar="N",
        help="N relabelings aleatorios del mismo mapa: nulo para la firma",
    )

    args = p.parse_args(argv)
    original = load(args.corpus, args.format)
    corpus = original
    remapped = None
    mapping = None
    if args.mapfile:
        from millstone.ingest import remap

        mapping = remap.parse_map(args.mapfile)
        remapped = remap.apply_map(corpus, mapping)
        corpus = remapped.corpus
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

    if args.cmd == "report":
        lines = ["# Reporte millstone\n"]
        for name in sorted(HYPOTHESES):
            h = HYPOTHESES[name]()
            lines.append(f"## `{h.name}`\n\n> {h.statement}\n")
            for e in h.evaluate(corpus):
                mark = {True: "SOPORTA", False: "REFUTA", None: "—"}[e.supported]
                lines.append(f"- **{mark}** {e.prediction}  \n  {e.detail}")
            lines.append("")
        text = "\n".join(lines)
        if args.out:
            from pathlib import Path

            Path(args.out).write_text(text, encoding="utf-8")
            print(f"escrito {args.out}")
        else:
            print(text)
        return 0

    if args.cmd == "testbed":
        if remapped is None:
            raise SystemExit("testbed requiere --map <fichero de mapeo>")
        from millstone.engine.battery import run_battery

        print(f"== testbed: {args.mapfile}")
        top = ", ".join(
            f"{k!r} x{n}" for k, n in remapped.unmapped.most_common(8)
        )
        print(
            f"cobertura: {remapped.coverage:.1%} de "
            f"{remapped.total_leaves} unidades"
            + (f" | sin mapear: {top}" if top else "")
        )

        group = corpus.schema.parent_level("word") or "word"
        METRICS = ("hapax", "heaps_beta", "timm", "families", "outdeg",
                   "echo_z3")

        def word_lines(c):
            v = MemoryCorpusView(c)
            return [
                list(s.symbols) for s in v.unit_sequences(group, "word")
                if s.symbols
            ]

        sigs = {}
        for label, c in (("original", original), ("descifrado", corpus)):
            v = MemoryCorpusView(c)
            ws = [w for l in word_lines(c) for w in l]
            ds = discover(v, "word")
            basis = prune(v, "word", ds)
            vec = run_battery(word_lines(c))
            sigs[label] = vec
            print(
                f"-- {label}: alfabeto {len(alphabet(v))} | "
                f"{len(ws)} palabras ({len(set(ws))} tipos) | "
                f"candidatas {len(ds)}, base exacta {len(basis.basis)}"
            )
            if vec is None:
                print("   batería: N insuficiente")
            else:
                print("   " + "  ".join(
                    f"{k}={vec[k]:.3g}" for k in METRICS
                ))

        if args.nulls and sigs["descifrado"]:
            import random

            rng = random.Random(0)
            keys, vals = list(mapping), list(mapping.values())
            nulls: dict[str, list[float]] = {k: [] for k in METRICS}
            for _ in range(args.nulls):
                pm = dict(zip(keys, rng.sample(vals, len(vals))))
                res = remap.apply_map(original, pm)
                vec = run_battery(word_lines(res.corpus))
                if vec:
                    for k in METRICS:
                        nulls[k].append(vec[k])
            print(f"-- nulos: {args.nulls} relabelings del mismo mapa")
            for k in METRICS:
                xs = nulls[k]
                if not xs:
                    continue
                real = sigs["descifrado"][k]
                m = sum(xs) / len(xs)
                sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5
                flag = "" if min(xs) <= real <= max(xs) else " *FUERA*"
                print(
                    f"   {k:>11}: real={real:.3g}  "
                    f"nulo={m:.3g}±{sd:.2g} "
                    f"[{min(xs):.3g},{max(xs):.3g}]{flag}"
                )

        for h in (NaturalLanguage(),):
            print(f"== {h.name}: {h.statement}")
            for e in h.evaluate(corpus):
                mark = {True: "SOPORTA", False: "REFUTA", None: "?"}[e.supported]
                print(f"  [{mark:>7}] {e.prediction}\n            {e.detail}")
        if "line" in corpus.schema.levels:
            h = FreeWordOrder()
            print(f"== {h.name}: {h.statement}")
            for e in h.evaluate(corpus):
                mark = {True: "SOPORTA", False: "REFUTA", None: "?"}[e.supported]
                print(f"  [{mark:>7}] {e.prediction}\n            {e.detail}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
