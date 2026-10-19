"""Szenario: Erzeugung ist deterministisch, die Zahl der Beziehungen und Widersprüche stimmt, die Wunschreihenfolge erklärt die Richtungen."""

import alk_algorithm as A
import alk_scenario as S


def test_same_input_gives_the_same_instance_and_the_seed_matters():
    a = S.make_instance(30, 2.0, 3, 17)
    assert a == S.make_instance(30, 2.0, 3, 17)
    assert a != S.make_instance(30, 2.0, 3, 18)


def test_number_of_relations_is_n_times_degree_capped_by_all_pairs():
    assert S.make_instance(12, 2.0, 0, 1).m == 24
    assert S.make_instance(10, 3.0, 0, 1).m == 30
    assert S.edge_count(6, 6.0) == 15          # alle Paare: 6 * 5 / 2
    assert S.make_instance(6, 6.0, 0, 1).m == 15
    assert S.edge_count(400, 6.0) == 2400


def test_without_contradictions_every_relation_points_forward_in_the_plan():
    inst = S.make_instance(50, 3.0, 0, 4)
    pos = inst.position()
    assert all(pos[a] < pos[b] for a in range(inst.n) for b in inst.adj[a])
    assert inst.reversed_edges == frozenset() and not A.has_cycle(inst.adj)


def test_exactly_back_relations_point_backwards():
    for back in (1, 2, 7):
        inst = S.make_instance(60, 3.0, back, 9)
        pos = inst.position()
        backwards = {(a, b) for a in range(inst.n) for b in inst.adj[a] if pos[a] > pos[b]}
        assert len(backwards) == back and backwards == set(inst.reversed_edges)


def test_back_is_capped_at_the_number_of_relations_and_reversing_all_stays_acyclic():
    inst = S.make_instance(8, 1.0, 100, 3)          # 8 Beziehungen, alle umgedreht
    assert len(inst.reversed_edges) == inst.m == 8
    assert not A.has_cycle(inst.adj)
    pos = inst.position()
    assert all(pos[a] > pos[b] for a in range(inst.n) for b in inst.adj[a])


def test_plan_is_a_permutation_and_there_are_no_self_loops_or_duplicates():
    inst = S.make_instance(40, 4.0, 5, 2)
    assert sorted(inst.plan) == list(range(40))
    for a in range(inst.n):
        assert a not in inst.adj[a] and len(set(inst.adj[a])) == len(inst.adj[a]) and list(inst.adj[a]) == sorted(inst.adj[a])


def test_complete_instance_has_every_pair_related():
    inst = S.make_instance(8, 4.0, 0, 1)            # 28 Beziehungen = alle Paare
    assert inst.m == 28 and A.topological_order(inst.adj) is not None


def test_same_generator_as_the_first_piece_of_the_series():
    """Die Instanz (12 Aufgaben, Grad 2, ein Widerspruch, Seed 7) ist dieselbe wie im Lehrbeispiel von di-kreis-demo: Kreis (5, 7, 12) ab 1 gezählt."""
    inst = S.make_instance(12, 2.0, 1, 7)
    assert inst.m == 24 and len(inst.reversed_edges) == 1
    assert A.johnson(inst.adj).count >= 1 and (4, 6, 11) in {A.canonical(c) for c in A.johnson(inst.adj).cycles}


def test_from_adjacency_defaults_to_the_numbering():
    inst = S.from_adjacency([[2], [], []])
    assert inst.plan == (0, 1, 2) and inst.adj == ((2,), (), ())
