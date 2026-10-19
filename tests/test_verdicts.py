"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; ohne diese Datei überleben fast alle Mutanten der Verdikt-Arithmetik."""

import alk_evaluation as ev
import alk_scenario as S

from conftest import MINI


def _analysis(name, **kw):
    return ev.analyse_instance(S.from_adjacency(MINI[name]), ev.Settings(**kw))


# --- Kernfrage ---------------------------------------------------------------------------------------------------------------------------

def test_question_without_a_cycle():
    kind, text = ev.verdict_question(_analysis("raute"))
    assert kind == "success" and "kreisfrei" in text and "keine Beziehung" in text


def test_question_with_complete_count_names_edge_share_and_rest():
    kind, text = ev.verdict_question(_analysis("k3"))
    assert kind == "warning"
    assert "**Der Plan hat 5 Kreise** (kürzester 2, längster 3 Aufgaben)" in text
    assert "Die Beziehung 1 → 2 liegt auf 2 davon (40 %); streicht man sie, bleiben 3 Kreise." in text
    assert "Stück 3 der Reihe" in text and "Pfade" not in text                 # kein einzelner Widerspruch


def test_question_with_a_single_cycle_uses_singular():
    kind, text = ev.verdict_question(_analysis("dreieck"))
    assert "**Der Plan hat 1 Kreis**" in text and "liegt auf 1 davon (100 %); streicht man sie, bleibt kein Kreis." in text


def test_question_with_one_contradiction_adds_the_path_sentence():
    inst = S.make_instance(30, 3.0, 1, 5)
    a = ev.analyse_instance(inst, ev.Settings(30, 3.0, 1, 5))
    (bad,) = inst.reversed_edges
    text = ev.verdict_question(a)[1]
    assert f"die Zahl der Pfade von Aufgabe {bad[1] + 1} nach Aufgabe {bad[0] + 1} im Rest des Plans" in text


def test_question_with_an_aborted_run_names_the_reason_and_the_bound():
    kind, text = ev.verdict_question(_analysis("k4", budget=5))
    assert kind == "warning" and "**Der Plan hat mehr als 5 Kreise**" in text and "Kreisbudget von 5" in text and "untere Schranke" in text
    a = _analysis("k4")
    import dataclasses
    checks = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, aborted="pruefungen", count=12))
    text = ev.verdict_question(checks)[1]
    assert "mindestens 12 Kreise" in text and "Prüfungsbudget von 6.000.000 Kantenprüfungen" in text


# --- E1 Kreiszahl -------------------------------------------------------------------------------------------------------------------------

def _c(out, back, median, aborted=0, maximum=None, n=40, budget=20000):
    return {"out": out, "back": back, "instances": 30, "with_cycle": 30, "median": median, "max": maximum or median, "aborted": aborted, "budget": budget, "n": n}


def test_counts_names_three_points_of_the_dense_series_and_compares_with_the_sparse_one():
    rows = [_c(2.0, 1, 0), _c(2.0, 24, 100.5), _c(3.0, 1, 0), _c(3.0, 8, 103), _c(3.0, 24, 20001, aborted=17)]
    kind, text = ev.verdict_counts(rows)
    assert kind == "info"
    assert "Bei 40 Aufgaben und mittlerem Ausgangsgrad 3 liegt der Median bei 0 Kreisen mit 1 Widerspruch, bei 103 mit 8 Widersprüchen und bei mehr als 20.000 mit 24 Widersprüchen" in text
    assert "in 17 von 30 Plänen mit 24 Widersprüchen wurde das Budget von 20.000 Kreisen überschritten" in text
    assert "Bei Ausgangsgrad 2 sind es mit 24 Widersprüchen nur 100,5 Kreise." in text


def test_counts_warns_when_the_count_does_not_grow():
    assert ev.verdict_counts([_c(2.0, 1, 5), _c(3.0, 1, 5), _c(3.0, 24, 5)])[0] == "warning"


def test_counts_bound_is_strict_at_the_budget():
    text = ev.verdict_counts([_c(2.0, 1, 1), _c(3.0, 1, 1), _c(3.0, 2, 20000), _c(3.0, 4, 20001)])[1]
    assert "bei 20.000 mit 2 Widersprüchen und bei mehr als 20.000 mit 4" in text


# --- E2 ein Widerspruch --------------------------------------------------------------------------------------------------------------------

def test_single_names_every_row_and_the_worst_plan():
    rows = [{"n": 60, "out": 3.0, "instances": 100, "with_cycle": 25, "median": 3, "max": 32}, {"n": 100, "out": 4.0, "instances": 100, "with_cycle": 43, "median": 3.0, "max": 268}]
    kind, text = ev.verdict_single(rows)
    assert kind == "info"
    assert "bei 60 Aufgaben und Grad 3 schließt er in 25 von 100 Plänen einen Kreis (Median 3, Maximum 32)" in text
    assert "bei 100 Aufgaben und Grad 4 schließt er in 43 von 100 Plänen einen Kreis (Median 3, Maximum 268)" in text and "im ungünstigsten Plan sind es 268" in text


def test_single_warns_if_no_row_has_more_than_one_cycle():
    assert ev.verdict_single([{"n": 60, "out": 3.0, "instances": 10, "with_cycle": 0, "median": 0, "max": 1}])[0] == "warning"


# --- E3 Johnson gegen naiv ----------------------------------------------------------------------------------------------------------------

def _n(n, out, back, both, cycles, johnson, naive):
    return {"n": n, "out": out, "back": back, "instances": 20, "both": both, "cycles": cycles, "johnson": johnson, "naive": naive, "factor": (naive / johnson) if both else None}


def test_naive_names_the_factor_range_and_that_it_shrinks():
    rows = [_n(60, 3.0, 3, 18, 3, 17.5, 1694.5), _n(60, 3.0, 12, 20, 383.5, 6927.5, 36903.5)]
    kind, text = ev.verdict_naive(rows)
    assert kind == "info"
    assert "im Median 5,3 bis 96,8 mal so viele Kantenprüfungen wie Johnson" in text
    assert "zum Beispiel 36.904 gegen 6.928 bei 60 Aufgaben, 12 Widersprüchen und 383,5 Kreisen" in text and "Der Faktor sinkt" in text


def test_naive_has_no_shrink_sentence_when_the_factor_grows_and_warns_below_one():
    grows = ev.verdict_naive([_n(30, 2.0, 4, 10, 2, 9, 90), _n(30, 2.0, 24, 10, 86, 100, 5000)])[1]
    assert "Der Faktor sinkt" not in grows
    assert ev.verdict_naive([_n(30, 2.0, 4, 10, 2, 100, 50)])[0] == "warning"
    assert ev.verdict_naive([_n(30, 2.0, 4, 0, None, None, None)])[0] == "warning"


# --- E4 meistbelegte Kante ----------------------------------------------------------------------------------------------------------------

def _e(back, top, rest, shortest, med, longest, rev):
    return {"back": back, "instances": 57, "shortest": shortest, "median_length": med, "longest": longest, "reversed_on_cycle": rev, "top_share": top, "rest_share": rest}


def test_edges_names_share_rest_lengths_and_contradictions_on_cycles():
    kind, text = ev.verdict_edges([_e(8, 0.8846, 0.1154, 3, 8.0, 14, 0.75), _e(12, 0.862, 0.138, 3, 11.0, 17, 0.8333)])
    assert kind == "info"
    assert "bei 8 Widersprüchen liegt die meistbelegte Beziehung auf 88,5 % aller Kreise, danach bleiben 11,5 %" in text
    assert "kürzester Kreis 3, Median 8, längster 14 Aufgaben; 75 % der Widersprüche liegen auf einem Kreis" in text and "83,3 % der Widersprüche" in text


def test_edges_warns_when_a_share_is_not_above_half():
    assert ev.verdict_edges([_e(8, 0.5, 0.5, 3, 8.0, 14, 0.75)])[0] == "warning"
    assert ev.verdict_edges([{"back": 8, "instances": 0}])[0] == "warning"


# --- E5 Wachstum --------------------------------------------------------------------------------------------------------------------------

def _g(n, median, maximum):
    return {"n": n, "back": 3, "instances": 20, "median": median, "max": maximum, "aborted": 0, "budget": 20000}


def test_growth_compares_the_spread_with_the_growth():
    rows = [_g(20, 5.5, 93), _g(50, 63.5, 11492), _g(60, 39, 1043)]
    kind, text = ev.verdict_growth(rows)
    assert kind == "info"
    assert "Der Median steigt von 5,5 Kreisen bei 20 Aufgaben auf 39 bei 60, doch das Maximum liegt bei 11.492 (n = 50)" in text
    assert "(181-fach zwischen Maximum und Median)" in text and "(7,1-fach zwischen den Medianen)" in text


def test_growth_warns_when_the_median_grows_more_than_the_spread():
    assert ev.verdict_growth([_g(20, 1, 2), _g(60, 100, 150)])[0] == "warning"


# --- Zahlenformat ------------------------------------------------------------------------------------------------------------------------

def test_number_formats():
    assert ev._i(1234567) == "1.234.567" and ev._i(0) == "0"
    assert ev._dec(12.5) == "12,5" and ev._dec(12.0) == "12" and ev._dec(1234.5) == "1.234,5"
    assert ev._pct(0.885) == "88,5" and ev._pct(0.4) == "40" and ev._pct(1.0) == "100"
