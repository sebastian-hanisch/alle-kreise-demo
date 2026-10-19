"""Auswertung: Analyse von Mini-Instanzen, Prüfung vor der Anzeige, Formate."""

import dataclasses

import alk_algorithm as A
import alk_evaluation as ev
import alk_scenario as S

from conftest import MINI


def _analysis(name, with_naive=False, **kw):
    return ev.analyse_instance(S.from_adjacency(MINI[name]), ev.Settings(**kw), with_naive)


def test_analysis_of_the_complete_digraph_on_three_tasks():
    a = _analysis("k3", with_naive=True)
    assert a.count == 5 and a.complete and a.naive.count == 5
    assert [len(c) for c in a.listing] == [2, 2, 2, 3, 3]                       # kürzeste zuerst
    assert a.shortest is not None and len(a.shortest) == 2 and a.on_cycle == (0, 1, 2)
    assert a.top[0] == ((0, 1), 2) and a.after_strike == 3 and a.by_paths is None
    assert ev.validate(a) == []


def test_analysis_of_a_dag_has_nothing_to_list():
    a = _analysis("raute")
    assert a.count == 0 and a.listing == () and a.top == () and a.after_strike is None and a.shortest is None and a.on_cycle == () and ev.validate(a) == []


def test_analysis_of_an_aborted_run_has_no_strike_count():
    a = _analysis("k4", budget=5)
    assert a.aborted == "kreise" and a.count == 6 and a.after_strike is None and ev.validate(a) == []


def test_validate_names_every_kind_of_error():
    a = _analysis("k3", with_naive=True)
    fake = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, cycles=((0, 2, 1, 0),) + a.johnson.cycles[1:]))
    assert any("kein Kreis" in p for p in ev.validate(fake))
    dup = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, cycles=a.johnson.cycles + (a.johnson.cycles[0],)))
    assert any("doppelt" in p for p in ev.validate(dup))
    zero = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, count=0, cycles=(), coverage={}, lengths={}))
    assert any("widerspricht" in p for p in ev.validate(zero))
    bad_len = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, lengths={2: 1}))
    assert any("Kreislängen" in p for p in ev.validate(bad_len))
    bad_cov = dataclasses.replace(a, johnson=dataclasses.replace(a.johnson, coverage={(0, 1): 1}))
    assert any("Belegung" in p for p in ev.validate(bad_cov))
    bad_nodes = dataclasses.replace(a, on_cycle=(0, 1))
    assert any("Erreichbarkeit" in p for p in ev.validate(bad_nodes))
    bad_naive = dataclasses.replace(a, naive=dataclasses.replace(a.naive, count=4))
    assert any("naive" in p for p in ev.validate(bad_naive))
    bad_strike = dataclasses.replace(a, after_strike=2)
    assert any("Streichen" in p for p in ev.validate(bad_strike))


def test_validate_names_a_wrong_path_count():
    inst = S.make_instance(30, 3.0, 1, 5)
    a = ev.analyse_instance(inst, ev.Settings(30, 3.0, 1, 5))
    assert a.by_paths == a.count and ev.validate(a) == []
    assert any("Pfadzahl" in p for p in ev.validate(dataclasses.replace(a, by_paths=a.count + 1)))


def test_labels_start_at_one_and_cycles_are_formatted_as_chains():
    assert ev.label(0) == "1" and ev.format_edge((3, 8)) == "4 → 9"
    assert ev.format_cycle((3, 8, 1)) == "4 → 9 → 2 → 4" and ev.format_cycle((0,)) == "1 → 1"


def test_long_cycles_are_shortened_and_the_limit_is_inclusive():
    cyc = tuple(range(14))
    assert ev.format_cycle(cyc) == " → ".join(str(i + 1) for i in range(14)) + " → 1"        # genau 14: ungekürzt
    assert ev.format_cycle(tuple(range(15))) == "1 → 2 → 3 → 4 → 5 → 6 → … → 14 → 15 → 1"
    assert ev.format_cycle(tuple(range(15)), limit=40).count("→") == 15


def test_count_text_and_plurals():
    assert ev.count_text(7, None) == "7" and ev.count_text(1001, "kreise", 1000) == "mehr als 1.000" and ev.count_text(52, "pruefungen") == "mindestens 52"
    assert ev.kreise(1) == "1 Kreis" and ev.kreise(5) == "5 Kreise" and ev.kreise(1001, "kreise", 1000) == "mehr als 1.000 Kreise" and ev.kreise(0) == "0 Kreise"
    assert ev.bleiben(0) == "bleibt kein Kreis" and ev.bleiben(1) == "bleibt 1 Kreis" and ev.bleiben(18) == "bleiben 18 Kreise"
    assert ev.widersprueche(1) == "1 Widerspruch" and ev.widersprueche(8) == "8 Widersprüchen"


def test_the_strike_count_equals_count_minus_coverage_for_every_listed_top_edge():
    a = ev.analyse(ev.Settings(30, 3.0, 8, 10))
    for edge, covered in a.top:
        assert A.johnson(A.strike_edge(a.inst.adj, edge)).count == a.count - covered
