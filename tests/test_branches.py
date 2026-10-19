"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einer festen Instanz vor.

Ein Preset, das seine Beschreibung nicht einlöst (z. B. „Das Budget reicht nicht“ ohne Abbruch), fällt hier auf."""

import pytest

import alk_algorithm as A
import alk_constants as C
import alk_evaluation as ev


def _a(name):
    p = C.PRESETS[name]
    return ev.analyse(ev.Settings(p["n"], p["out"], p["back"], p["seed"], p["budget"]), with_naive=p["view"] != "johnson")


def test_lehrbeispiel_has_a_few_cycles_through_one_contradiction():
    a = _a("Lehrbeispiel (12 Aufgaben, wenige Kreise)")
    assert a.complete and 2 <= a.count <= 10 and len(a.inst.reversed_edges) == 1 and a.by_paths == a.count


def test_ohne_kreis_has_an_empty_enumeration():
    a = _a("Ohne Kreis: nichts aufzuzählen")
    assert a.count == 0 and a.listing == () and a.top == () and a.after_strike is None and a.shortest is None


def test_one_contradiction_can_make_many_cycles():
    a = _a("Ein Widerspruch, viele Kreise")
    assert len(a.inst.reversed_edges) == 1 and a.count >= 100 and a.by_paths == a.count and a.top[0][1] == a.count   # die umgedrehte Beziehung liegt auf allen Kreisen


def test_dense_plan_has_hundreds_of_cycles():
    a = _a("Dicht: Hunderte Kreise")
    assert a.complete and 100 <= a.count <= 999


def test_the_budget_preset_aborts_with_a_lower_bound():
    a = _a("Das Budget reicht nicht")
    assert a.aborted == "kreise" and a.count == C.PRESETS["Das Budget reicht nicht"]["budget"] + 1 and a.after_strike is None
    assert "mehr als 1.000 Kreise" in ev.verdict_question(a)[1]


def test_one_edge_lies_on_almost_all_cycles():
    a = _a("Eine Kante löst fast alles")
    assert a.complete and a.count >= 50 and a.top[0][1] / a.count >= 0.95 and a.after_strike <= 0.05 * a.count


def test_naive_search_needs_many_times_the_checks_of_johnson():
    a = _a("Naiv gegen Johnson")
    assert a.naive is not None and a.naive.aborted is None and a.naive.count == a.count and a.naive.checks >= 20 * a.johnson.checks


def test_the_check_budget_aborts_johnson_with_its_own_reason():
    a = ev.analyse(ev.Settings(40, 3.0, 24, 1, 100000))
    small = A.johnson(a.inst.adj, max_checks=1000)
    assert small.aborted == "pruefungen" and "mindestens" in ev.count_text(small.count, small.aborted, 100000)


def test_a_naive_run_can_hit_its_own_check_budget():
    adj = ev.analyse(ev.Settings(40, 3.0, 24, 3, 100000)).inst.adj
    naive = A.naive_cycles(adj, max_checks=C.NAIVE_CHECK_LIMIT)
    assert naive.aborted == "pruefungen"


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_passes_the_validation(name):
    assert ev.validate(_a(name)) == []
