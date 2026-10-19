"""Orakel-Test alle-kreise-demo: Kreismengen, Kreiszahlen, Pfadzahl-Deutung und Kantenbelegung gegen networkx und gegen Aufzählung (DEMO-PLAYBOOK §12).

Unabhängiger Rechenweg: `networkx.simple_cycles`, die Aufzählung aller Folgen verschiedener Aufgaben (Brute Force) und die Pfadzahl-DP für genau
einen Widerspruch. Feste Instanzen (range, kein Zufall), zusammen weit unter 10 Sekunden."""

import itertools
import random

import pytest

import alk_algorithm as A
import alk_scenario as S

nx = pytest.importorskip("networkx")


def _graph(adj):
    g = nx.DiGraph()
    g.add_nodes_from(range(len(adj)))
    g.add_edges_from((a, b) for a in range(len(adj)) for b in adj[a])
    return g


def _nx_cycles(adj):
    return {A.canonical(c) for c in nx.simple_cycles(_graph(adj))}


def _instances(count=240):
    """Feste Instanzen: kleine Pläne, dünn bis dicht, ein bis viele Widersprüche."""
    for s in range(count):
        n = 4 + s % 9
        out = (1.0, 2.0, 3.0)[s % 3]
        back = (1, 2, 4, 8)[s % 4]
        yield S.make_instance(n, out, back, 100 + s).adj


def test_johnson_finds_exactly_the_networkx_cycles():
    seen = 0
    for adj in _instances():
        ref = _nx_cycles(adj)
        run = A.johnson(adj)
        assert run.count == len(ref) == len(run.cycles) and {A.canonical(c) for c in run.cycles} == ref, adj
        seen += bool(ref)
    assert seen >= 100                                                       # genug Pläne mit Kreis, damit der Test etwas prüft


def test_naive_search_finds_exactly_the_networkx_cycles():
    for adj in _instances(120):
        ref = _nx_cycles(adj)
        run = A.naive_cycles(adj)
        assert {A.canonical(c) for c in run.cycles} == ref and run.count == len(ref), adj


def test_every_listed_cycle_is_a_cycle_canonical_and_distinct():
    for adj in _instances(80):
        run = A.johnson(adj)
        assert all(A.is_cycle(adj, c) and c[0] == min(c) for c in run.cycles)
        assert len(set(run.cycles)) == len(run.cycles)


def _brute_force_count(adj):
    """Alle Folgen verschiedener Aufgaben mit der kleinsten zuerst, die sich schließen (n <= 6)."""
    n = len(adj)
    total = 0
    for k in range(1, n + 1):
        for subset in itertools.combinations(range(n), k):
            first, rest = subset[0], subset[1:]
            for perm in itertools.permutations(rest):
                if A.is_cycle(adj, (first,) + perm):
                    total += 1
    return total


def test_count_against_brute_force_on_tiny_graphs():
    nonzero = 0
    for s in range(120):
        n = 3 + s % 4
        adj = S.make_instance(n, (1.0, 2.0, 3.0)[s % 3], (1, 2, 3)[s % 3], 700 + s).adj
        count = _brute_force_count(adj)
        assert A.johnson(adj).count == A.naive_cycles(adj).count == count, adj
        nonzero += count > 0
    assert nonzero >= 30


def test_one_contradiction_cycle_count_equals_the_path_count_in_the_rest_dag():
    positive = 0
    for s in range(150):
        inst = S.make_instance(30 + s % 40, (2.0, 3.0, 4.0)[s % 3], 1, 300 + s)
        (edge,) = inst.reversed_edges
        by_paths = A.cycles_through_edge(inst.adj, edge)
        assert A.johnson(inst.adj).count == by_paths, (s, edge)
        positive += by_paths > 0
    assert positive >= 30


def test_coverage_equals_the_count_of_networkx_cycles_through_each_edge():
    for adj in _instances(100):
        cycles = list(nx.simple_cycles(_graph(adj)))
        expected = {}
        for c in cycles:
            for i in range(len(c)):
                e = (c[i], c[(i + 1) % len(c)])
                expected[e] = expected.get(e, 0) + 1
        assert A.johnson(adj).coverage == expected


def test_lengths_histogram_equals_the_networkx_lengths():
    for adj in _instances(100):
        expected = {}
        for c in nx.simple_cycles(_graph(adj)):
            expected[len(c)] = expected.get(len(c), 0) + 1
        assert A.johnson(adj).lengths == expected


def test_cycle_nodes_are_exactly_the_tasks_on_cycles():
    for adj in _instances(100):
        nodes = {v for c in A.johnson(adj).cycles for v in c}
        assert tuple(sorted(nodes)) == A.nodes_on_cycles(adj)


def test_zero_cycles_exactly_if_the_graph_is_acyclic():
    for adj in _instances(100):
        assert (A.johnson(adj).count == 0) == nx.is_directed_acyclic_graph(_graph(adj)) == (not A.has_cycle(adj))


def test_striking_an_edge_removes_exactly_the_cycles_through_it_and_never_adds_one():
    rng = random.Random(3)
    checked = 0
    for adj in _instances(100):
        run = A.johnson(adj)
        if not run.coverage:
            continue
        edge = rng.choice(sorted(run.coverage))
        after = A.johnson(A.strike_edge(adj, edge)).count
        assert after == run.count - run.coverage[edge]
        checked += 1
    assert checked >= 50


def test_the_most_covered_edge_leaves_at_most_as_many_cycles_as_any_other_edge():
    for adj in _instances(60):
        run = A.johnson(adj)
        if not run.coverage:
            continue
        best = A.top_edges(run.coverage, limit=1)[0]
        assert all(run.coverage[e] <= best[1] for e in run.coverage)


def test_the_answer_does_not_depend_on_the_numbering_of_tasks():
    rng = random.Random(5)
    for adj in _instances(60):
        n = len(adj)
        perm = list(range(n))
        rng.shuffle(perm)
        renamed = [[] for _ in range(n)]
        for a in range(n):
            for b in adj[a]:
                renamed[perm[a]].append(perm[b])
        renamed = tuple(tuple(sorted(w)) for w in renamed)
        j1, j2 = A.johnson(adj), A.johnson(renamed)
        assert j1.count == j2.count and j1.lengths == j2.lengths


def test_shortest_cycle_has_the_minimum_length_of_all_cycles_with_and_without_a_hint():
    seen = 0
    for adj in _instances(120):
        run = A.johnson(adj)
        if not run.count:
            assert A.shortest_cycle(adj) is None
            continue
        best = min(len(c) for c in run.cycles)
        plain = A.shortest_cycle(adj)
        assert len(plain) == best and A.is_cycle(adj, plain)
        assert A.shortest_cycle(adj, hint=run.cycles[-1]) == plain             # der Hinweis ändert nur die Stutzung
        seen += 1
    assert seen >= 60


def test_shortest_cycle_starts_at_every_task_including_the_last_one():
    assert A.shortest_cycle(((), (1,))) == (1,)                                  # Eigenschleife an der letzten Aufgabe
    assert A.shortest_cycle(((1,), (0, 2), ())) == (0, 1) and A.shortest_cycle(((1,), (2,), (1,))) == (1, 2) and A.shortest_cycle(((1,), (0, 2), (2,))) == (2,)
