"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Aufgaben sind in der Anzeige ab 1 nummeriert (`label`); im Kern ab 0. Läufe, die ihr Budget erreichen, heißen „abgebrochen“: ihre Zahl ist nur eine untere Schranke."""

from dataclasses import dataclass

import alk_algorithm as A
import alk_constants as C
from alk_scenario import Instance, make_instance


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    out: float = C.DEFAULT_OUT
    back: int = C.DEFAULT_BACK
    seed: int = C.DEFAULT_SEED
    budget: int = C.DEFAULT_BUDGET


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: Instance
    johnson: A.CycleRun
    naive: A.CycleRun | None                 # nur, wenn die Anzeige das naive Absuchen verlangt
    shortest: tuple[int, ...] | None
    on_cycle: tuple[int, ...]                # Aufgaben auf mindestens einem Kreis
    listing: tuple[tuple[int, ...], ...]     # gefundene Kreise, kürzeste zuerst
    top: tuple[tuple[tuple[int, int], int], ...]   # meistbelegte Kanten (Kante, Zahl der Kreise)
    after_strike: int | None                 # Kreise nach dem Streichen der meistbelegten Kante (None: nicht berechenbar)
    by_paths: int | None                     # Pfadzahl-Deutung bei genau einem Widerspruch

    @property
    def count(self) -> int:
        return self.johnson.count

    @property
    def aborted(self) -> str | None:
        return self.johnson.aborted

    @property
    def complete(self) -> bool:
        return self.johnson.aborted is None


def label(v: int) -> str:
    return str(v + 1)


def format_cycle(cycle, limit=14) -> str:
    """Kreis als Kette „4 → 9 → 2 → 4“; ab `limit` Aufgaben gekürzt."""
    nodes = [label(v) for v in cycle] + [label(cycle[0])]
    if len(cycle) > limit:
        nodes = nodes[:6] + ["…"] + nodes[-3:]
    return " → ".join(nodes)


def format_edge(edge) -> str:
    return f"{label(edge[0])} → {label(edge[1])}"


def analyse(settings: Settings, with_naive: bool = False) -> Analysis:
    return analyse_instance(make_instance(settings.n, settings.out, settings.back, settings.seed), settings, with_naive)


def analyse_instance(inst: Instance, settings: Settings, with_naive: bool = False) -> Analysis:
    """Beide Aufzähler und alle Kennzahlen auf einer gegebenen Instanz (Tests bauen Mini-Instanzen von Hand)."""
    adj = inst.adj
    run = A.johnson(adj, max_cycles=settings.budget, max_checks=C.CHECK_LIMIT, keep=C.KEEP)
    naive = A.naive_cycles(adj, max_cycles=settings.budget, max_checks=C.NAIVE_CHECK_LIMIT, keep=C.KEEP) if with_naive else None
    listing = tuple(sorted(run.cycles, key=lambda c: (len(c), c)))
    cyclic = run.count > 0
    shortest = A.shortest_cycle(adj, hint=listing[0] if listing else None) if cyclic else None
    on_cycle = A.nodes_on_cycles(adj) if cyclic else ()
    top = tuple(A.top_edges(run.coverage, C.TOP_EDGES))
    after = None
    if top and run.aborted is None:
        after = A.johnson(A.strike_edge(adj, top[0][0]), max_cycles=settings.budget, max_checks=C.CHECK_LIMIT, keep=0).count
    by_paths = None
    if len(inst.reversed_edges) == 1:
        (edge,) = inst.reversed_edges
        by_paths = A.cycles_through_edge(adj, edge)
    return Analysis(settings, inst, run, naive, shortest, on_cycle, listing, top, after, by_paths)


def validate(a: Analysis) -> list[str]:
    """Unabhängige Prüfung vor der Anzeige: leere Liste, wenn alles stimmt; sonst die verletzten Regeln."""
    adj, problems = a.inst.adj, []
    cycles = a.johnson.cycles
    if any(not A.is_cycle(adj, c) or c[0] != min(c) for c in cycles):
        problems.append("Ein aufgezählter Kreis ist kein Kreis des Plans oder nicht kanonisch.")
    if len(set(cycles)) != len(cycles):
        problems.append("Ein Kreis wurde doppelt aufgezählt.")
    if A.has_cycle(adj) != (a.count > 0):
        problems.append("Die Zahl der Kreise widerspricht der Frage, ob der Plan einen Kreis hat.")
    if a.complete:
        if sum(a.johnson.lengths.values()) != a.count:
            problems.append("Die Verteilung der Kreislängen passt nicht zur Zahl der Kreise.")
        if sum(a.johnson.coverage.values()) != sum(length * k for length, k in a.johnson.lengths.items()):
            problems.append("Die Belegung der Kanten passt nicht zu den Kreislängen.")
        nodes = {v for c in cycles for v in c}
        if a.count <= C.KEEP and tuple(sorted(nodes)) != a.on_cycle:
            problems.append("Die Aufgaben auf Kreisen stimmen nicht mit der Erreichbarkeit überein.")
        if a.naive is not None and a.naive.aborted is None and a.naive.count != a.count:
            problems.append("Johnson und das naive Absuchen zählen verschieden viele Kreise.")
        if a.after_strike is not None and a.top and a.after_strike != a.count - a.top[0][1]:
            problems.append("Nach dem Streichen der meistbelegten Kante bleibt nicht die erwartete Zahl von Kreisen.")
    if a.by_paths is not None and a.complete and a.by_paths != a.count:
        problems.append("Bei einem Widerspruch weicht die Kreiszahl von der Pfadzahl im Rest-DAG ab.")
    return problems


# --- Zahlenformat --------------------------------------------------------------------------------------------------------------------------

def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    return _i(x) if x == int(x) else f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(share) -> str:
    return _dec(round(100.0 * share, 1))


def count_text(count: int, aborted: str | None, budget: int | None = None) -> str:
    """Kreiszahl als Text: exakt, „mehr als B“ (Kreisbudget) oder „mindestens N“ (Prüfungsbudget)."""
    if aborted == "kreise" and budget is not None:
        return f"mehr als {_i(budget)}"
    if aborted == "pruefungen":
        return f"mindestens {_i(count)}"
    return _i(count)


def kreise(count: int, aborted: str | None = None, budget: int | None = None) -> str:
    """„1 Kreis“, „18 Kreise“, „mehr als 1.000 Kreise“."""
    return "1 Kreis" if count == 1 and not aborted else f"{count_text(count, aborted, budget)} Kreise"


def bleiben(count: int) -> str:
    """„bleibt kein Kreis“, „bleibt 1 Kreis“, „bleiben 18 Kreise“."""
    return "bleibt kein Kreis" if count == 0 else ("bleibt 1 Kreis" if count == 1 else f"bleiben {_i(count)} Kreise")


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------

def verdict_question(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Wie viele Kreise hat der Plan, und welche Kante löst die meisten?"""
    if a.count == 0:
        return "success", "**Der Plan ist kreisfrei:** Es gibt keinen Kreis, also auch keine Beziehung, die man ändern müsste."
    s = a.settings
    lengths = a.johnson.lengths
    base = f"**Der Plan hat {kreise(a.count, a.aborted, s.budget)}** (kürzester {min(lengths)}, längster {max(lengths)} Aufgaben)"
    if a.aborted:
        reason = f"das Kreisbudget von {_i(s.budget)}" if a.aborted == "kreise" else f"das Prüfungsbudget von {_i(C.CHECK_LIMIT)} Kantenprüfungen"
        return "warning", (f"{base}: Die Aufzählung brach ab, weil sie {reason} erreicht hat; die Zahl ist nur eine untere Schranke, "
                           f"und die Belegung der Kanten beruht auf den bis dahin gefundenen Kreisen. Mit einem größeren Budget oder weniger Widersprüchen wird sie vollständig.")
    (edge, covered) = a.top[0]
    paths = ""
    if a.by_paths is not None:
        (bad,) = a.inst.reversed_edges
        paths = f" Weil genau ein Widerspruch vorliegt, ist das zugleich die Zahl der Pfade von Aufgabe {label(bad[1])} nach Aufgabe {label(bad[0])} im Rest des Plans."
    return "warning", (f"{base}. Die Beziehung {format_edge(edge)} liegt auf {_i(covered)} davon ({_pct(covered / a.count)} %); streicht man sie, {bleiben(a.after_strike)}.{paths} "
                       f"Das Streichen einer Beziehung ist aber nur ein Hinweis, welche Kante wichtig ist: die kleinste Menge zu streichender Beziehungen sucht Stück 3 der Reihe.")


def widersprueche(k: int) -> str:
    return "1 Widerspruch" if k == 1 else f"{_i(k)} Widersprüchen"


def _bound(x, budget):
    """Wert aus einer Zeile: liegt er über dem Budget, ist er nur eine untere Schranke."""
    return f"mehr als {_i(budget)}" if x > budget else _dec(x)


def verdict_counts(rows: list[dict]) -> tuple[str, str]:
    """E1: Kreiszahl über den Widersprüchen; Aussage zur dichtesten Zeilengruppe und Vergleich mit der dünnsten."""
    outs = sorted({r["out"] for r in rows})
    dense = [r for r in rows if r["out"] == outs[-1]]
    sparse = [r for r in rows if r["out"] == outs[0]]
    first, mid, last = dense[0], dense[len(dense) // 2], dense[-1]
    budget = last["budget"]
    text = (f"Bei {_i(last['n'])} Aufgaben und mittlerem Ausgangsgrad {_dec(outs[-1])} liegt der Median bei {_bound(first['median'], budget)} Kreisen mit {widersprueche(first['back'])}, "
            f"bei {_bound(mid['median'], budget)} mit {widersprueche(mid['back'])} und bei {_bound(last['median'], budget)} mit {widersprueche(last['back'])}; "
            f"in {last['aborted']} von {last['instances']} Plänen mit {widersprueche(last['back'])} wurde das Budget von {_i(budget)} Kreisen überschritten. "
            f"Bei Ausgangsgrad {_dec(outs[0])} sind es mit {widersprueche(sparse[-1]['back'])} nur {_bound(sparse[-1]['median'], budget)} Kreise.")
    return ("info" if last["median"] > first["median"] else "warning"), text


def verdict_single(rows: list[dict]) -> tuple[str, str]:
    """E2: Ein einziger Widerspruch; die Kreiszahl ist die Pfadzahl vom Ziel zum Anfang der Beziehung im Rest-DAG."""
    best = max(rows, key=lambda r: r["max"])
    parts = "; ".join(f"bei {_i(r['n'])} Aufgaben und Grad {_dec(r['out'])} schließt er in {r['with_cycle']} von {r['instances']} Plänen einen Kreis (Median {_dec(r['median'])}, Maximum {_i(r['max'])})" for r in rows)
    text = (f"Ein einziger umgedrehter Widerspruch erzeugt oft gleich mehrere Kreise: {parts}. Ihre Zahl ist die Zahl der Pfade vom Ziel zum Anfang der Beziehung im Rest des Plans; "
            f"im ungünstigsten Plan sind es {_i(best['max'])}.")
    return ("info" if best["max"] > 1 else "warning"), text


def verdict_naive(rows: list[dict]) -> tuple[str, str]:
    """E3: Kantenprüfungen von Johnson gegen das naive Absuchen."""
    use = [r for r in rows if r["both"] > 0]
    if not use:
        return "warning", "In diesem Raster wurde kein Plan von beiden Verfahren fertig aufgezählt."
    lo, hi = min(r["factor"] for r in use), max(r["factor"] for r in use)
    text = (f"Das naive Absuchen braucht im Median {_dec(round(lo, 1))} bis {_dec(round(hi, 1))} mal so viele Kantenprüfungen wie Johnson "
            f"(zum Beispiel {_i(use[-1]['naive'])} gegen {_i(use[-1]['johnson'])} bei {_i(use[-1]['n'])} Aufgaben, {use[-1]['back']} Widersprüchen und {_dec(use[-1]['cycles'])} Kreisen).")
    shrinks = any(a["n"] == b["n"] and a["out"] == b["out"] and a["back"] < b["back"] and a["factor"] > b["factor"] for a in use for b in use)
    if shrinks:
        text += " Der Faktor sinkt, wenn die Kreiszahl wächst: Johnson spart das Verlaufen in Sackgassen, nicht das Aufzählen selbst."
    return ("info" if lo > 1 else "warning"), text


def verdict_edges(rows: list[dict]) -> tuple[str, str]:
    """E4: meistbelegte Kante, Rest nach ihrem Streichen, Kreislängen."""
    use = [r for r in rows if r["instances"] > 0]
    if not use:
        return "warning", "In diesem Raster entsteht kein Plan mit mindestens zwei Kreisen."
    parts = "; ".join(f"bei {r['back']} Widersprüchen liegt die meistbelegte Beziehung auf {_pct(r['top_share'])} % aller Kreise, danach bleiben {_pct(r['rest_share'])} % "
                      f"(kürzester Kreis {_dec(r['shortest'])}, Median {_dec(r['median_length'])}, längster {_dec(r['longest'])} Aufgaben; {_pct(r['reversed_on_cycle'])} % der Widersprüche liegen auf einem Kreis)" for r in use)
    text = f"Im Median über die Pläne: {parts}."
    return ("info" if all(r["top_share"] > 0.5 for r in use) else "warning"), text


def verdict_growth(rows: list[dict]) -> tuple[str, str]:
    """E5: Kreiszahl über der Aufgabenzahl bei fester Dichte und festem Anteil an Widersprüchen."""
    first, last = rows[0], rows[-1]
    top = max(rows, key=lambda r: r["max"])
    ratio_spread = max(r["max"] / r["median"] for r in rows if r["median"] > 0) if any(r["median"] > 0 for r in rows) else 0
    ratio_growth = last["median"] / first["median"] if first["median"] > 0 else 0
    text = (f"Der Median steigt von {_dec(first['median'])} Kreisen bei {first['n']} Aufgaben auf {_dec(last['median'])} bei {last['n']}, doch das Maximum liegt bei {_i(top['max'])} (n = {top['n']}): "
            f"Die Kreiszahl schwankt von Plan zu Plan stärker ({_dec(round(ratio_spread, 1))}-fach zwischen Maximum und Median) als mit der Aufgabenzahl ({_dec(round(ratio_growth, 1))}-fach zwischen den Medianen).")
    return ("info" if ratio_spread > ratio_growth else "warning"), text
