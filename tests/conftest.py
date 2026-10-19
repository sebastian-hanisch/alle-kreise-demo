"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Mutationstests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def diamond_chain(k):
    """k Rauten hintereinander (3i -> 3i+1 und 3i+2 -> 3i+3) mit einer Rückkante vom Ende zum Anfang: 2^k Kreise der Länge 2k + 1."""
    n = 3 * k + 1
    adj = [[] for _ in range(n)]
    for i in range(k):
        adj[3 * i] += [3 * i + 1, 3 * i + 2]
        adj[3 * i + 1].append(3 * i + 3)
        adj[3 * i + 2].append(3 * i + 3)
    adj[3 * k].append(0)
    return tuple(tuple(sorted(w)) for w in adj)


# Von Hand gerechnete Mini-Instanzen: Name -> Adjazenz (adj[a] = Aufgaben nach a)
MINI = {
    "leer": (),
    "einzeln": ((),),
    "schleife": ((0,),),
    "gegeneinander": ((1,), (0,)),
    "dreieck": ((1,), (2,), (0,)),
    "zwei_kreise": ((1, 2), (0,), (0,)),                # Kreise (0, 1) und (0, 2) teilen die Aufgabe 0
    "kreis_dahinter": ((1,), (2,), (1, 3), (4,), ()),   # 0 -> 1, Kreis 1 <-> 2, dahinter 2 -> 3 -> 4
    "k3": ((1, 2), (0, 2), (0, 1)),                     # vollständiger Digraph: 3 Kreise der Länge 2, 2 der Länge 3 = 5
    "k4": ((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)),  # 6 + 8 + 6 = 20 Kreise
    "rauten3": diamond_chain(3),                        # 8 Kreise der Länge 7
    "raute": ((1, 2), (3,), (3,), ()),                  # DAG: zwei Pfade von 0 nach 3
}
MINI_COUNTS = {"leer": 0, "einzeln": 0, "schleife": 1, "gegeneinander": 1, "dreieck": 1, "zwei_kreise": 2, "kreis_dahinter": 1, "k3": 5, "k4": 20, "rauten3": 8, "raute": 0}


@pytest.fixture
def mini():
    return MINI


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in alk_experiments)."""
    import alk_experiments as ex
    return getattr(ex, name)()
