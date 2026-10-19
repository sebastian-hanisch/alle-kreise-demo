"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Mediane über feste Pläne, nie ein einzelner Zufalls-Seed. Alle Zahlen sind Zählungen oder Mediane ganzer Zahlen (plattformrobust: nur `random.Random.random()`)."""

import pytest

import alk_algorithm as A
import alk_constants as C
import alk_evaluation as ev

from conftest import MINI, cached


def _row(rows, **keys):
    return next(r for r in rows if all(r[k] == v for k, v in keys.items()))


def test_count_grows_fast_with_the_number_of_contradictions():
    rows = cached("count_rows")
    assert {r["instances"] for r in rows} == {30} and {r["n"] for r in rows} == {40} and {r["budget"] for r in rows} == {20000}
    medians = {r["back"]: r["median"] for r in rows if r["out"] == 3.0}
    assert medians == {1: 0, 2: 1.5, 4: 6.5, 8: 103, 12: 312.5, 16: 2293.5, 24: 20001}      # 20001 = Budget + 1: mehr als 20 000
    assert _row(rows, out=3.0, back=1)["with_cycle"] == 14 and _row(rows, out=3.0, back=8)["max"] == 4397
    assert [_row(rows, out=3.0, back=b)["aborted"] for b in (8, 12, 16, 24)] == [0, 1, 4, 17]
    g2 = _row(rows, out=2.0, back=24)
    assert (g2["median"], g2["max"], g2["aborted"]) == (100.5, 801, 0)


def test_one_contradiction_cycle_count_is_the_path_count():
    rows = cached("single_rows")
    assert [(r["n"], r["out"], r["with_cycle"], r["median"], r["max"]) for r in rows] == [(60, 3.0, 25, 3, 32), (100, 4.0, 43, 3, 268), (200, 4.0, 23, 3, 157)]


def test_johnson_against_naive_search():
    rows = cached("naive_rows")
    got = [(r["n"], r["out"], r["back"], r["both"], r["cycles"], r["johnson"], r["naive"]) for r in rows]
    assert got == [(30, 2.0, 4, 15, 2, 9, 223), (30, 2.0, 24, 20, 86.0, 657.0, 3920.5), (60, 3.0, 3, 18, 3.0, 17.5, 1694.5), (60, 3.0, 12, 20, 383.5, 6927.5, 36903.5)]
    assert [round(r["factor"], 1) for r in rows] == [24.8, 6.0, 96.8, 5.3]


def test_the_most_covered_edge_and_the_cycle_lengths():
    rows = cached("edge_rows")
    r8, r12 = _row(rows, back=8), _row(rows, back=12)
    assert (r8["instances"], r12["instances"]) == (57, 59)
    assert (ev._pct(r8["top_share"]), ev._pct(r8["rest_share"]), ev._pct(r8["reversed_on_cycle"])) == ("88,5", "11,5", "75")
    assert (ev._pct(r12["top_share"]), ev._pct(r12["rest_share"]), ev._pct(r12["reversed_on_cycle"])) == ("86,2", "13,8", "83,3")
    assert (r8["shortest"], r8["median_length"], r8["longest"]) == (3, 8.0, 14) and (r12["shortest"], r12["median_length"], r12["longest"]) == (3, 11.0, 17)


def test_growth_with_the_number_of_tasks_is_erratic():
    rows = cached("growth_rows")
    assert [r["n"] for r in rows] == [20, 30, 40, 50, 60] and [r["back"] for r in rows] == [3, 4, 6, 8, 9]
    assert [r["median"] for r in rows] == [5.5, 19, 32, 63.5, 39] and [r["max"] for r in rows] == [93, 353, 1545, 11492, 1043]
    assert sum(r["aborted"] for r in rows) == 0


def test_verdict_texts_quote_the_readme_numbers():
    assert "bei 103 mit 8 Widersprüchen und bei mehr als 20.000 mit 24 Widersprüchen" in ev.verdict_counts(cached("count_rows"))[1]
    assert "im Median 5,3 bis 96,8 mal so viele" in ev.verdict_naive(cached("naive_rows"))[1]
    assert "(181-fach zwischen Maximum und Median)" in ev.verdict_growth(cached("growth_rows"))[1]


def test_complete_digraph_cycle_counts_follow_the_formula():
    """c(K_k) = Summe über j = 2..k von C(k, j) * (j - 1)!: 5 für k = 3, 20 für k = 4, 84 für k = 5."""
    import math
    for k, expected in ((3, 5), (4, 20), (5, 84)):
        assert sum(math.comb(k, j) * math.factorial(j - 1) for j in range(2, k + 1)) == expected
        adj = tuple(tuple(w for w in range(k) if w != v) for v in range(k))
        assert A.johnson(adj).count == A.naive_cycles(adj).count == expected


def test_diamond_chains_have_two_to_the_r_cycles():
    from conftest import diamond_chain
    for r in range(1, 7):
        assert A.johnson(diamond_chain(r)).count == 2 ** r


def test_slider_maximum_has_the_documented_edge_count():
    from alk_scenario import edge_count
    assert edge_count(C.N_MAX, C.OUT_MAX) == 240
    assert A.johnson(MINI["k4"]).count == 20
