"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Pläne, Grenzen inklusive, Gleichstände, Regler-Extreme."""

import alk_algorithm as A
import alk_constants as C
import alk_evaluation as ev
import alk_scenario as S

from conftest import MINI


def test_exactly_two_tasks_with_and_without_a_cycle():
    """n = 2: der kleinste Fall, in dem es etwas zu zählen gibt."""
    assert A.johnson(((1,), ())).count == 0
    assert A.johnson(MINI["gegeneinander"]).count == 1


def test_the_smallest_slider_plan_is_valid():
    a = ev.analyse(ev.Settings(C.N_MIN, C.OUT_MIN, C.BACK_MIN, 1))
    assert a.inst.n == 6 and a.inst.m == 3 and a.count == 0 and ev.validate(a) == []


def test_more_contradictions_than_relations_are_capped():
    a = ev.analyse(ev.Settings(C.N_MIN, C.OUT_MIN, C.BACK_MAX, 1))
    assert len(a.inst.reversed_edges) == a.inst.m == 3 and a.count == 0           # alle umgedreht: weiter kreisfrei


def test_the_largest_slider_plan_finishes_within_its_budget_and_validates():
    """Worst-Case am Regler-Maximum (n = 60, Ausgangsgrad 4, 40 Widersprüche, Budget 100 000): kein Hänger, alle Prüfungen bestehen. Keine Zeit-Assertion."""
    a = ev.analyse(ev.Settings(C.N_MAX, C.OUT_MAX, C.BACK_MAX, 3, C.BUDGETS[-1]), with_naive=True)
    assert a.aborted is not None or a.complete
    assert a.johnson.checks <= C.CHECK_LIMIT + 1 and ev.validate(a) == []


def test_every_budget_value_gives_a_valid_run():
    for budget in C.BUDGETS:
        a = ev.analyse(ev.Settings(30, 3.0, 12, 1, budget))
        assert ev.validate(a) == [] and (a.aborted is None or a.count == budget + 1)


def test_ties_in_the_top_edges_prefer_the_smaller_edge():
    cov = {(2, 3): 4, (0, 1): 4, (1, 2): 5}
    assert A.top_edges(cov) == [((1, 2), 5), ((0, 1), 4), ((2, 3), 4)] and A.top_edges(cov, limit=1) == [((1, 2), 5)]


def test_budget_equal_to_the_count_is_not_an_abort():
    assert A.johnson(MINI["k3"], max_cycles=5).aborted is None and A.johnson(MINI["k3"], max_cycles=4).aborted == "kreise"


def test_bounds_are_inclusive():
    """Reglergrenzen gelten inklusive: n = 6 und n = 60, Widersprüche 0 und 40 sind erlaubt."""
    for n in (C.N_MIN, C.N_MAX):
        for back in (C.BACK_MIN, C.BACK_MAX):
            assert S.make_instance(n, 2.0, back, 1).n == n


def test_degenerate_instances_do_not_break_the_enumerators():
    assert A.johnson(()).count == 0 and A.naive_cycles(()).count == 0
    assert A.johnson(((),)).count == 0 and A.naive_cycles(((),)).count == 0
