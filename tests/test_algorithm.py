"""Jede Einheit an den von Hand gerechneten Mini-Instanzen (conftest.MINI), DEMO-PLAYBOOK §1b.

Handrechnungen stehen als Kommentar neben dem erwarteten Wert."""

import pytest

import alk_algorithm as A

from conftest import MINI, MINI_COUNTS, diamond_chain


def _set(run):
    return {A.canonical(c) for c in run.cycles}


@pytest.mark.parametrize("name", list(MINI))
def test_both_enumerators_find_the_hand_counted_number_of_cycles(name):
    adj = MINI[name]
    assert A.johnson(adj).count == A.naive_cycles(adj).count == MINI_COUNTS[name]


def test_empty_and_acyclic_graphs_have_no_cycle():
    for name in ("leer", "einzeln", "raute"):
        run = A.johnson(MINI[name])
        assert run.count == 0 and run.cycles == () and run.aborted is None


def test_self_loop_is_a_cycle_of_length_one():
    run = A.johnson(MINI["schleife"])
    assert run.cycles == ((0,),) and run.lengths == {1: 1} and run.coverage == {(0, 0): 1}


def test_two_tasks_against_each_other():
    run = A.johnson(MINI["gegeneinander"])
    assert run.cycles == ((0, 1),) and run.coverage == {(0, 1): 1, (1, 0): 1}


def test_two_cycles_sharing_a_task():
    run = A.johnson(MINI["zwei_kreise"])
    assert _set(run) == {(0, 1), (0, 2)}
    assert run.coverage == {(0, 1): 1, (1, 0): 1, (0, 2): 1, (2, 0): 1}


def test_complete_digraph_on_three_tasks_has_five_cycles():
    run = A.johnson(MINI["k3"])
    assert _set(run) == {(0, 1), (0, 2), (1, 2), (0, 1, 2), (0, 2, 1)}
    assert run.lengths == {2: 3, 3: 2}
    assert set(run.coverage.values()) == {2} and len(run.coverage) == 6        # jede Kante liegt im 2-Kreis und in genau einem 3-Kreis


def test_complete_digraph_on_four_tasks_has_twenty_cycles_by_length():
    run = A.johnson(MINI["k4"])
    assert run.count == 20 and run.lengths == {2: 6, 3: 8, 4: 6}                # 6 Paare, 4 Tripel mal 2 Richtungen, 3! Rundwege


def test_chain_of_diamonds_has_two_to_the_k_cycles_of_equal_length():
    run = A.johnson(MINI["rauten3"])
    assert run.count == 8 and run.lengths == {7: 8}
    assert A.cycles_through_edge(MINI["rauten3"], (9, 0)) == 8
    four = diamond_chain(4)
    assert A.johnson(four).count == 16 and A.naive_cycles(four).count == 16 and A.cycles_through_edge(four, (12, 0)) == 16


def test_cycle_behind_a_prefix_is_found_once():
    run = A.johnson(MINI["kreis_dahinter"])
    assert run.cycles == ((1, 2),) and run.count == 1


def test_naive_search_finds_the_same_cycles_but_looks_at_more_edges():
    adj = MINI["k4"]
    j, n = A.johnson(adj), A.naive_cycles(adj)
    assert {A.canonical(c) for c in n.cycles} == _set(j) and n.checks >= j.checks


def test_naive_search_wastes_checks_on_dead_ends():
    """Eine Sackgasse hinter vielen Zugängen: das naive Absuchen läuft für jeden Zugang erneut hinein, Johnson blockiert sie nach dem ersten Mal."""
    # Kreis 0 <-> 1; 1 und 0 führen beide in eine Kette 2 -> 3 -> ... -> 8, die nie zurückführt
    adj = ((1, 2), (0, 2), (3,), (4,), (5,), (6,), (7,), (8,), ())
    j, n = A.johnson(adj), A.naive_cycles(adj)
    assert j.count == n.count == 1 and n.checks > j.checks


def test_budget_on_cycles_aborts_with_a_lower_bound():
    run = A.johnson(MINI["k4"], max_cycles=10)
    assert run.aborted == "kreise" and run.count == 11                         # abgebrochen beim elften Kreis: „mehr als 10“
    assert A.naive_cycles(MINI["k4"], max_cycles=10).aborted == "kreise"
    assert A.johnson(MINI["k4"], max_cycles=20).aborted is None                 # genau so viele wie erlaubt: kein Abbruch


def test_budget_on_checks_aborts():
    run = A.johnson(MINI["k4"], max_checks=5)
    assert run.aborted == "pruefungen" and run.checks == 6
    assert A.naive_cycles(MINI["k4"], max_checks=5).aborted == "pruefungen"
    assert A.johnson(MINI["k4"], max_checks=10**6).aborted is None


def test_keep_limits_the_stored_cycles_but_not_the_count():
    run = A.johnson(MINI["k4"], keep=3)
    assert len(run.cycles) == 3 and run.count == 20 and sum(run.lengths.values()) == 20


def test_canonical_rotates_the_smallest_task_to_the_front():
    assert A.canonical((2, 0, 1)) == (0, 1, 2) and A.canonical((0, 1, 2)) == (0, 1, 2) and A.canonical(()) == ()


def test_cycle_checker_rejects_wrong_answers():
    adj = MINI["dreieck"]
    assert A.is_cycle(adj, (0, 1, 2)) and A.is_cycle(adj, (1, 2, 0))
    assert not A.is_cycle(adj, (0, 2, 1)) and not A.is_cycle(adj, ()) and not A.is_cycle(adj, (0, 1, 2, 0))


def test_path_count_in_a_dag_and_its_preconditions():
    assert A.count_paths_dag(MINI["raute"], 0, 3) == 2 and A.count_paths_dag(MINI["raute"], 3, 0) == 0
    assert A.count_paths_dag(MINI["raute"], 1, 1) == 1
    with pytest.raises(ValueError):
        A.count_paths_dag(MINI["dreieck"], 0, 1)


def test_cycles_through_an_edge_count_paths_in_the_rest_dag():
    assert A.cycles_through_edge(MINI["kreis_dahinter"], (2, 1)) == 1          # Pfade 1 -> 2 ohne die Kante 2 -> 1: ein Pfad
    with pytest.raises(ValueError):
        A.cycles_through_edge(MINI["raute"], (3, 0))                           # keine Kante des Graphen


def test_strike_edge_and_top_edges():
    adj = MINI["k3"]
    struck = A.strike_edge(adj, (0, 1))
    assert struck == ((2,), (0, 2), (0, 1)) and A.johnson(struck).count == 3   # 5 Kreise minus die 2 durch (0, 1)
    cov = A.johnson(adj).coverage
    assert A.top_edges(cov, limit=2) == [((0, 1), 2), ((0, 2), 2)]             # Gleichstand: kleinere Kante zuerst


def test_shortest_cycle_nodes_on_cycles_and_closure():
    assert A.shortest_cycle(MINI["kreis_dahinter"]) == (1, 2) and A.shortest_cycle(MINI["raute"]) is None
    assert A.nodes_on_cycles(MINI["kreis_dahinter"]) == (1, 2) and A.nodes_on_cycles(MINI["raute"]) == ()
    assert A.has_cycle(MINI["dreieck"]) and not A.has_cycle(MINI["raute"])
    assert A.topological_order(MINI["raute"]) is not None and A.topological_order(MINI["dreieck"]) is None
