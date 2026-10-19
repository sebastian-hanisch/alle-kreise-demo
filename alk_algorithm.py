"""Kern der Demo (nur Standardbibliothek): alle Elementarkreise eines gerichteten Graphen aufzählen, zählen und die meistbelegte Kante finden.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b); `adj[v]` sind die Aufgaben, die nach v kommen sollen.
Zwei Aufzähler: `johnson` (Johnson 1975, mit Blockierung) und `naive_cycles` (Absuchen ohne Blockierung, Tiernan-Art). Beide nennen jeden
Elementarkreis genau einmal, kanonisch mit der kleinsten Aufgabe zuerst. Zweiter Weg zur Kreiszahl bei genau einem Widerspruch:
`cycles_through_edge` zählt die Pfade im Rest-DAG. Unabhängige Prüfer: `is_cycle`, `has_cycle_by_closure`, `nodes_on_cycles`.

Aufwand wird in Kantenprüfungen gezählt (jede Kante, die ein Verfahren ansieht), nicht in Sekunden. Ein Budget begrenzt Kreise und Prüfungen:
wird es überschritten, ist `aborted` gesetzt und `count` nur eine untere Schranke."""

from collections import deque
from dataclasses import dataclass, field

WHITE, GREY, BLACK = 0, 1, 2


@dataclass(frozen=True)
class CycleRun:
    count: int                              # Zahl der gefundenen Kreise; bei `aborted` nur eine untere Schranke
    checks: int                             # Kantenprüfungen
    aborted: str | None                     # None, "kreise" (Kreisbudget) oder "pruefungen" (Prüfungsbudget)
    cycles: tuple[tuple[int, ...], ...]     # die ersten `keep` Kreise, kanonisch (kleinste Aufgabe zuerst), in Fundreihenfolge
    coverage: dict = field(default_factory=dict)   # Kante (a, b) -> Zahl der gefundenen Kreise, die sie enthalten (nur Johnson)
    lengths: dict = field(default_factory=dict)    # Länge -> Zahl der gefundenen Kreise dieser Länge (nur Johnson)


class _Stop(Exception):
    def __init__(self, reason):
        self.reason = reason


def _component(adj, s, allowed):
    """Aufgaben der starken Komponente von s im Teilgraphen aus `allowed`: vorwärts erreichbar und rückwärts erreichbar."""
    fwd = {s}
    stack = [s]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w in allowed and w not in fwd:
                fwd.add(w)
                stack.append(w)
    pred: dict[int, list[int]] = {}
    for v in fwd:
        for w in adj[v]:
            if w in fwd:
                pred.setdefault(w, []).append(v)
    bwd = {s}
    stack = [s]
    while stack:
        v = stack.pop()
        for u in pred.get(v, ()):
            if u not in bwd:
                bwd.add(u)
                stack.append(u)
    return fwd & bwd


def johnson(adj, max_cycles=None, max_checks=None, keep=20000) -> CycleRun:
    """Alle Elementarkreise nach Johnson (1975).

    Für jede Startaufgabe s (aufsteigend) wird nur der Teilgraph der Aufgaben ab s betrachtet und darin die Komponente von s. Eine Aufgabe, von der aus
    kein Weg zurück zu s führt, wird **blockiert** und erst wieder freigegeben, wenn auf einem Pfad durch sie ein Kreis gefunden wird: so läuft die Suche nie
    zweimal in dieselbe Sackgasse. Zeit höchstens proportional zu (n + m) mal (Zahl der Kreise + 1).
    `max_cycles`: bricht ab, sobald mehr Kreise gefunden sind (count = max_cycles + 1); `max_checks`: bricht nach so vielen Kantenprüfungen ab."""
    n = len(adj)
    checks = 0
    count = 0
    kept: list[tuple[int, ...]] = []
    coverage: dict = {}
    lengths: dict = {}
    reason = None
    try:
        for s in range(n):
            comp = _component(adj, s, set(range(s, n)))
            if len(comp) < 2 and s not in adj[s]:
                continue
            blocked: set[int] = set()
            blist = {v: set() for v in comp}
            path = [s]

            def unblock(u):
                stack = [u]
                while stack:
                    x = stack.pop()
                    if x in blocked:
                        blocked.discard(x)
                        stack.extend(blist[x])
                        blist[x].clear()

            def circuit(v):
                nonlocal checks, count
                found = False
                blocked.add(v)
                for w in adj[v]:
                    if w not in comp:
                        continue
                    checks += 1
                    if max_checks is not None and checks > max_checks:
                        raise _Stop("pruefungen")
                    if w == s:
                        count += 1
                        if max_cycles is not None and count > max_cycles:
                            raise _Stop("kreise")
                        if count <= keep:
                            kept.append(tuple(path))
                        lengths[len(path)] = lengths.get(len(path), 0) + 1
                        for i in range(len(path)):
                            e = (path[i], path[(i + 1) % len(path)])
                            coverage[e] = coverage.get(e, 0) + 1
                        found = True
                    elif w not in blocked:
                        path.append(w)
                        if circuit(w):
                            found = True
                        path.pop()
                if found:
                    unblock(v)
                else:
                    for w in adj[v]:
                        if w in comp:
                            blist[w].add(v)
                return found

            circuit(s)
    except _Stop as stop:
        reason = stop.reason
    return CycleRun(count, checks, reason, tuple(kept), coverage, lengths)


def naive_cycles(adj, max_cycles=None, max_checks=None, keep=20000) -> CycleRun:
    """Alle Elementarkreise durch Absuchen ohne Blockierung (Tiernan-Art): von s aus alle einfachen Pfade durch Aufgaben mit größerer Nummer.

    Jeder Kreis wird genau einmal gefunden (von seiner kleinsten Aufgabe aus), aber die Suche läuft in jede Sackgasse so oft hinein, wie es Wege dorthin gibt."""
    n = len(adj)
    checks = 0
    count = 0
    kept: list[tuple[int, ...]] = []
    reason = None
    try:
        for s in range(n):
            path = [s]
            on_path = {s}
            iters = [iter(adj[s])]
            while iters:
                descended = False
                for w in iters[-1]:
                    checks += 1
                    if max_checks is not None and checks > max_checks:
                        raise _Stop("pruefungen")
                    if w == s:
                        count += 1
                        if max_cycles is not None and count > max_cycles:
                            raise _Stop("kreise")
                        if count <= keep:
                            kept.append(tuple(path))
                    elif w > s and w not in on_path:
                        path.append(w)
                        on_path.add(w)
                        iters.append(iter(adj[w]))
                        descended = True
                        break
                if not descended:
                    iters.pop()
                    on_path.discard(path.pop())
    except _Stop as stop:
        reason = stop.reason
    return CycleRun(count, checks, reason, tuple(kept))


def canonical(cycle) -> tuple[int, ...]:
    """Kreis so drehen, dass die kleinste Aufgabe vorn steht (gleiche Kreise werden gleich)."""
    cycle = tuple(cycle)
    if not cycle:
        return cycle
    i = cycle.index(min(cycle))
    return cycle[i:] + cycle[:i]


def is_cycle(adj, cycle) -> bool:
    """Unabhängiger Prüfer: aufeinanderfolgende Aufgaben (und zuletzt wieder die erste) sind durch Kanten verbunden, keine Wiederholung."""
    cycle = tuple(cycle)
    if not cycle or len(set(cycle)) != len(cycle):
        return False
    return all(cycle[(i + 1) % len(cycle)] in adj[cycle[i]] for i in range(len(cycle)))


def topological_order(adj):
    """Kahn-Abbau; None, wenn der Graph einen Kreis hat."""
    n = len(adj)
    indeg = [0] * n
    for v in range(n):
        for w in adj[v]:
            indeg[w] += 1
    queue = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for w in adj[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    return order if len(order) == n else None


def has_cycle(adj) -> bool:
    return topological_order(adj) is None


def count_paths_dag(adj, src, dst) -> int:
    """Zahl der Pfade von src nach dst in einem DAG, per DP über eine topologische Ordnung (Python-Ganzzahlen, kein Überlauf)."""
    order = topological_order(adj)
    if order is None:
        raise ValueError("Der Graph hat einen Kreis")
    ways = [0] * len(adj)
    ways[src] = 1
    for v in order:
        if ways[v]:
            for w in adj[v]:
                ways[w] += ways[v]
    return ways[dst] if src != dst else 1


def strike_edge(adj, edge):
    """Graph ohne die Kante `edge` = (a, b)."""
    a, b = edge
    return tuple(tuple(w for w in adj[v] if not (v == a and w == b)) for v in range(len(adj)))


def cycles_through_edge(adj, edge) -> int:
    """Zahl der Kreise durch die Kante (a, b), wenn der Graph ohne diese Kante kreisfrei ist: die Pfade von b nach a im Rest-DAG.

    Bei genau einem Widerspruch ist das die Zahl aller Kreise des Plans: zweiter Weg zu `johnson`."""
    a, b = edge
    if b not in adj[a]:
        raise ValueError("Die Kante gehört nicht zum Graphen")
    return count_paths_dag(strike_edge(adj, edge), b, a)


def top_edges(coverage, limit=15):
    """Die meistbelegten Kanten (Kante, Zahl der Kreise); Gleichstand: kleinere Kante zuerst."""
    return sorted(coverage.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]


def shortest_cycle(adj, hint=None) -> tuple[int, ...] | None:
    """Kürzester gerichteter Kreis: Breitensuche von jeder Aufgabe aus (Stück 1 der Reihe)."""
    n = len(adj)
    limit = len(hint) if hint else n + 1
    best = None
    best_len = limit + 1
    for s in range(n):
        dist = {s: 0}
        parent = {s: -1}
        queue = deque([s])
        found = None
        while queue and found is None:
            v = queue.popleft()
            if dist[v] + 1 >= best_len:
                break
            for w in adj[v]:
                if w == s:
                    found = v
                    break
                if w not in dist:
                    dist[w] = dist[v] + 1
                    parent[w] = v
                    queue.append(w)
        if found is not None:
            cycle = [found]
            while cycle[-1] != s:
                cycle.append(parent[cycle[-1]])
            cycle.reverse()
            if len(cycle) < best_len:
                best, best_len = tuple(cycle), len(cycle)
    return best


def reachability(adj) -> list[int]:
    """Erreichbarkeit nach Warshall in Bitmengen: reach[v] hat Bit w, wenn von v aus w über mindestens eine Kante erreichbar ist."""
    n = len(adj)
    reach = [0] * n
    for v in range(n):
        for w in adj[v]:
            reach[v] |= 1 << w
    for k in range(n):
        bit_k = 1 << k
        rk = reach[k]
        for i in range(n):
            if reach[i] & bit_k:
                reach[i] |= rk
    return reach


def nodes_on_cycles(adj) -> tuple[int, ...]:
    """Aufgaben auf mindestens einem Kreis (v erreicht sich selbst): zweiter Weg zu den Kreisen."""
    reach = reachability(adj)
    return tuple(v for v in range(len(adj)) if reach[v] >> v & 1)
