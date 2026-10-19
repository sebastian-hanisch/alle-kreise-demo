"""Experimente E1 bis E5 über feste Pläne (nie ein einzelner Zufalls-Seed). Jede Funktion liefert Zeilen für Tabelle, Diagramm und Verdikt.

E1 Kreiszahl über den Widersprüchen, E2 ein einziger Widerspruch (Pfadzahl), E3 Johnson gegen naives Absuchen, E4 die meistbelegte Kante und die
Kreislängen, E5 Schwankung der Kreiszahl mit n. Aufwand in Kantenprüfungen; Zahlen mit `aborted` sind untere Schranken."""

from statistics import median

import alk_algorithm as A
import alk_constants as C
import alk_scenario as S


def _hist_median(lengths: dict) -> float:
    """Median der Kreislängen aus dem Histogramm {Länge: Zahl}."""
    flat = sorted(length for length, k in lengths.items() for _ in range(k))
    mid = len(flat) // 2
    return flat[mid] if len(flat) % 2 else (flat[mid - 1] + flat[mid]) / 2


def count_rows(n=C.E1_N, outs=C.E1_OUT, backs=C.E1_BACKS, seeds=C.E1_SEEDS, budget=C.E1_BUDGET) -> list[dict]:
    """E1: Zahl der Kreise über der Zahl der Widersprüche (Median und Maximum über feste Pläne; abgebrochene Läufe zählen als untere Schranke budget + 1)."""
    rows = []
    for out in outs:
        for back in backs:
            counts, aborted = [], 0
            for s in seeds:
                run = A.johnson(S.make_instance(n, out, back, s).adj, max_cycles=budget, max_checks=C.CHECK_LIMIT)
                counts.append(run.count)
                aborted += run.aborted is not None
            rows.append({"out": out, "back": back, "instances": len(seeds), "with_cycle": sum(1 for c in counts if c), "median": median(counts),
                         "max": max(counts), "aborted": aborted, "budget": budget, "n": n})
    return rows


def single_rows(ns=C.E2_N, outs=C.E2_OUT, seeds=C.E2_SEEDS) -> list[dict]:
    """E2: Bei genau einem Widerspruch ist die Kreiszahl die Pfadzahl vom Ziel zum Anfang der umgedrehten Beziehung im Rest-DAG."""
    rows = []
    for n, out in zip(ns, outs):
        counts = []
        for s in seeds:
            inst = S.make_instance(n, out, 1, s)
            (edge,) = inst.reversed_edges
            counts.append(A.cycles_through_edge(inst.adj, edge))
        positive = [c for c in counts if c]
        rows.append({"n": n, "out": out, "instances": len(seeds), "with_cycle": len(positive), "median": median(positive) if positive else 0, "max": max(counts)})
    return rows


def naive_rows(cases=C.E3_CASES, seeds=C.E3_SEEDS, max_checks=C.E3_CHECKS) -> list[dict]:
    """E3: Kantenprüfungen von Johnson gegen das naive Absuchen auf denselben Plänen (Median über die Pläne mit Kreis, bei denen beide fertig wurden)."""
    rows = []
    for n, out, back in cases:
        both = []
        for s in seeds:
            adj = S.make_instance(n, out, back, s).adj
            j = A.johnson(adj, max_checks=max_checks)
            v = A.naive_cycles(adj, max_checks=max_checks)
            if j.aborted is None and v.aborted is None and j.count > 0:
                both.append((j.count, j.checks, v.checks))
        rows.append({"n": n, "out": out, "back": back, "instances": len(seeds), "both": len(both),
                     "cycles": median(b[0] for b in both) if both else None, "johnson": median(b[1] for b in both) if both else None,
                     "naive": median(b[2] for b in both) if both else None,
                     "factor": (median(b[2] for b in both) / median(b[1] for b in both)) if both else None})
    return rows


def edge_rows(n=C.E4_N, out=C.E4_OUT, backs=C.E4_BACKS, seeds=C.E4_SEEDS, budget=C.KEEP) -> list[dict]:
    """E4: Kreislängen, Anteil der Widersprüche auf einem Kreis, Belegung der meistbelegten Kante und der Rest nach ihrem Streichen (Pläne mit 2 bis `budget` Kreisen)."""
    rows = []
    for back in backs:
        mins, meds, maxs, rev_share, top_share, rest_share = [], [], [], [], [], []
        for s in seeds:
            inst = S.make_instance(n, out, back, s)
            run = A.johnson(inst.adj, max_cycles=budget)
            if run.aborted or run.count < 2:
                continue
            mins.append(min(run.lengths))
            meds.append(_hist_median(run.lengths))
            maxs.append(max(run.lengths))
            rev_share.append(sum(1 for e in inst.reversed_edges if e in run.coverage) / len(inst.reversed_edges))
            top = A.top_edges(run.coverage, limit=1)[0][1]
            top_share.append(top / run.count)
            rest_share.append((run.count - top) / run.count)
        rows.append({"back": back, "n": n, "out": out, "instances": len(mins), "shortest": median(mins), "median_length": median(meds), "longest": median(maxs),
                     "reversed_on_cycle": median(rev_share), "top_share": median(top_share), "rest_share": median(rest_share)})
    return rows


def growth_rows(ns=C.E5_NS, out=C.E5_OUT, share=C.E5_SHARE, seeds=C.E5_SEEDS, budget=C.E5_BUDGET) -> list[dict]:
    """E5: Kreiszahl über der Aufgabenzahl bei fester Dichte und festem Anteil an Widersprüchen (Median und Maximum über feste Pläne)."""
    rows = []
    for n in ns:
        back = round(share * S.edge_count(n, out))
        counts, aborted = [], 0
        for s in seeds:
            run = A.johnson(S.make_instance(n, out, back, s).adj, max_cycles=budget, max_checks=C.CHECK_LIMIT)
            counts.append(run.count)
            aborted += run.aborted is not None
        rows.append({"n": n, "back": back, "instances": len(seeds), "median": median(counts), "max": max(counts), "aborted": aborted, "budget": budget})
    return rows
