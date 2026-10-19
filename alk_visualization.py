"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben.

Hauptbild ist das Bogendiagramm aus Stück 1: die Aufgaben stehen in ihrer verdeckten Wunschreihenfolge auf einer Linie, Beziehungen nach vorn laufen als
Bögen darüber, Widersprüche (gegen die Reihenfolge) als Bögen darunter; die Pfeilrichtung folgt daraus (oben nach rechts, unten nach links)."""

import math

import plotly.graph_objects as go

import alk_constants as C
from alk_evaluation import format_edge, label

ARC_POINTS = 14
# Belegung einer Kante (Anteil der Kreise, die sie enthalten) in vier Stufen: Farbe und Linienbreite
COVERAGE_STEPS = ((0.10, "rgba(255,159,28,0.55)", 1.6), (0.40, "rgba(240,110,20,0.75)", 2.4), (0.70, "rgba(214,60,30,0.85)", 3.2), (1.01, "rgba(160,10,10,0.95)", 4.2))
COVERAGE_NAMES = ("bis 10 % der Kreise", "bis 40 %", "bis 70 %", "über 70 %")


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _arc(xa, xb, n, upward, points=ARC_POINTS):
    span = abs(xb - xa)
    h = max(0.07, span / max(1, n - 1)) * (1 if upward else -1)
    xs = [xa + (xb - xa) * i / points for i in range(points + 1)]
    ys = [h * math.sin(math.pi * i / points) for i in range(points + 1)]
    return xs, ys


def _trace(edges, pos, n, color, width, name=None):
    xs, ys = [], []
    for a, b in edges:
        ax, ay = _arc(pos[a], pos[b], n, pos[a] < pos[b])
        xs += ax + [None]
        ys += ay + [None]
    if not xs:
        return None
    return go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width), hoverinfo="skip", name=name or "", showlegend=False)


def build_arc_figure(inst, cycle=None, coverage=None, count=0, struck=None, height=None):
    """Bogendiagramm der Aufgaben in Wunschreihenfolge.

    `cycle`: ein gewählter Kreis in Rot; `coverage`: Belegung der Kanten ({(a, b): Zahl der Kreise}) färbt die Kanten orange bis dunkelrot nach dem Anteil an `count`;
    `struck`: eine gestrichene Kante, gestrichelt gezeichnet."""
    n = inst.n
    pos = inst.position()
    fig = go.Figure()
    edges = [(a, b) for a in range(n) for b in inst.adj[a]]
    cyc_edges = {(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))} if cycle else set()
    width = 1.2 if n <= 40 else 0.8
    covered: dict[int, list] = {i: [] for i in range(len(COVERAGE_STEPS))}
    plain = []
    for e in edges:
        if e in cyc_edges or e == struck:
            continue
        share = (coverage.get(e, 0) / count) if (coverage and count) else 0
        if share <= 0:
            plain.append(e)
        else:
            step = next(i for i, (limit, _, _) in enumerate(COVERAGE_STEPS) if share <= limit)
            covered[step].append(e)
    for up in (True, False):
        tr = _trace([e for e in plain if (pos[e[0]] < pos[e[1]]) == up], pos, n, C.COLOR_FORWARD if up else C.COLOR_BACKWARD, width)
        if tr:
            fig.add_trace(tr)
    for i, (limit, color, w) in enumerate(COVERAGE_STEPS):
        tr = _trace(covered[i], pos, n, color, w)
        if tr:
            fig.add_trace(tr)
    if struck:
        tr = _trace([struck], pos, n, "rgba(60,60,60,0.9)", 2.4)
        if tr:
            tr.line.dash = "dot"
            fig.add_trace(tr)
    tr = _trace(sorted(cyc_edges), pos, n, C.COLOR_CYCLE, 3.4)
    if tr:
        fig.add_trace(tr)
    labelled = n <= 40
    nodes = list(range(n))
    on_cycle = set(cycle or ())
    fig.add_trace(go.Scatter(
        x=[pos[v] for v in nodes], y=[0] * n, mode="markers+text" if labelled else "markers",
        marker=dict(size=22 if labelled else (9 if n <= 100 else 5), color=C.COLOR_NODE,
                    line=dict(color=[C.COLOR_CYCLE if v in on_cycle else "#333" for v in nodes], width=[3 if v in on_cycle else 1 for v in nodes])),
        text=[label(v) for v in nodes] if labelled else None, textposition="middle center", textfont=dict(color="#222", size=11),
        hovertext=[f"Aufgabe {label(v)}: Platz {pos[v] + 1} der Wunschreihenfolge" for v in nodes], hoverinfo="text", showlegend=False))
    fig.update_xaxes(title_text="Wunschreihenfolge (verdeckt) →", range=[-0.8, n - 0.2], showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(range=[-1.12, 1.12], showticklabels=False, showgrid=False, zeroline=True, zerolinecolor="rgba(128,128,128,0.35)")
    _base(fig, height or 380)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=40))
    return fig


def build_lengths_figure(lengths: dict):
    """Zahl der Kreise je Länge (Aufgaben im Kreis)."""
    xs = sorted(lengths)
    fig = go.Figure(go.Bar(x=[str(x) for x in xs], y=[lengths[x] for x in xs], marker_color=C.COLOR_BAR, hovertemplate="Länge %{x}: %{y} Kreise<extra></extra>"))
    fig.update_xaxes(title_text="Aufgaben im Kreis", type="category")
    fig.update_yaxes(title_text="Zahl der Kreise")
    return _base(fig, 320)


def build_checks_figure(johnson_checks, naive_checks, naive_aborted):
    """Kantenprüfungen von Johnson und dem naiven Absuchen (logarithmisch, damit beide lesbar bleiben)."""
    names = ["Johnson", "Naives Absuchen" + (" (abgebrochen)" if naive_aborted else "")]
    fig = go.Figure(go.Bar(x=names, y=[max(1, johnson_checks), max(1, naive_checks)], marker_color=[C.COLOR_BAR, C.COLOR_BAR2],
                           text=[f"{johnson_checks:,}".replace(",", "."), f"{naive_checks:,}".replace(",", ".")], textposition="outside", cliponaxis=False))
    fig.update_yaxes(title_text="Kantenprüfungen (logarithmisch)", type="log")
    fig.update_xaxes(type="category")
    return _base(fig, 320)


def build_top_edges_figure(top, count):
    """Die meistbelegten Beziehungen: Zahl der Kreise, die sie enthalten."""
    xs = [format_edge(e) for e, _ in top]
    fig = go.Figure(go.Bar(x=xs, y=[k for _, k in top], marker_color=C.COLOR_CYCLE, hovertemplate="%{x}: %{y} Kreise<extra></extra>",
                           text=[f"{100 * k / count:.0f} %" for _, k in top], textposition="outside", cliponaxis=False))
    fig.update_xaxes(title_text="Beziehung (von → nach)", type="category")
    fig.update_yaxes(title_text="Kreise, die sie enthalten")
    return _base(fig, 340)


def build_counts_figure(rows):
    """E1: Median und Maximum der Kreiszahl über der Zahl der Widersprüche, je Dichte (logarithmisch; abgebrochene Läufe stehen auf Budget + 1)."""
    fig = go.Figure()
    colors = {2.0: C.COLOR_LINE, 3.0: C.COLOR_LINE2}
    for out in sorted({r["out"] for r in rows}):
        sel = [r for r in rows if r["out"] == out]
        color = colors.get(out, "#59a14f")
        fig.add_trace(go.Scatter(x=[r["back"] for r in sel], y=[max(0.5, r["median"]) for r in sel], mode="lines+markers", name=f"Median, Grad {out:g}", line=dict(color=color, width=3),
                                 customdata=[[r["median"], r["aborted"], r["instances"]] for r in sel],
                                 hovertemplate="%{x} Widersprüche: Median %{customdata[0]}, %{customdata[1]} von %{customdata[2]} Plänen über dem Budget<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["back"] for r in sel], y=[max(0.5, r["max"]) for r in sel], mode="lines+markers", name=f"Maximum, Grad {out:g}", line=dict(color=color, width=2, dash="dot"),
                                 hovertemplate="%{x} Widersprüche: Maximum %{y}<extra></extra>"))
    fig.update_xaxes(title_text="Widersprüche (umgedrehte Beziehungen)", type="log", tickvals=sorted({r["back"] for r in rows}))
    fig.update_yaxes(title_text="Zahl der Kreise (logarithmisch)", type="log")
    return _base(fig, 400)


def build_single_figure(rows):
    """E2: Bei einem Widerspruch Maximum und Median der Kreiszahl (Pläne mit Kreis) je Plangröße."""
    xs = [f"{r['n']} Aufgaben, Grad {r['out']:g}" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[r["median"] for r in rows], name="Median (Pläne mit Kreis)", marker_color=C.COLOR_BAR))
    fig.add_trace(go.Bar(x=xs, y=[r["max"] for r in rows], name="Maximum", marker_color=C.COLOR_BAR2))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Zahl der Kreise")
    return _base(fig, 340)


def build_naive_figure(rows):
    """E3: Kantenprüfungen von Johnson und dem naiven Absuchen je Fall (logarithmisch)."""
    use = [r for r in rows if r["both"] > 0]
    xs = [f"{r['n']} Aufgaben, {r['back']} Wid." for r in use]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[r["johnson"] for r in use], name="Johnson", marker_color=C.COLOR_BAR))
    fig.add_trace(go.Bar(x=xs, y=[r["naive"] for r in use], name="Naives Absuchen", marker_color=C.COLOR_BAR2))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Kantenprüfungen (Median, logarithmisch)", type="log")
    return _base(fig, 360)


def build_edges_figure(rows):
    """E4: Anteil der Kreise auf der meistbelegten Kante und Rest nach ihrem Streichen, je Zahl der Widersprüche."""
    use = [r for r in rows if r["instances"] > 0]
    xs = [f"{r['back']} Widersprüche" for r in use]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[100 * r["top_share"] for r in use], name="auf der meistbelegten Beziehung", marker_color=C.COLOR_CYCLE))
    fig.add_trace(go.Bar(x=xs, y=[100 * r["rest_share"] for r in use], name="bleiben nach dem Streichen", marker_color=C.COLOR_BAR))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Anteil der Kreise (%, Median)", range=[0, 100])
    return _base(fig, 340)


def build_growth_figure(rows):
    """E5: Median und Maximum der Kreiszahl über der Aufgabenzahl (logarithmisch)."""
    xs = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[max(0.5, r["median"]) for r in rows], mode="lines+markers", name="Median", line=dict(color=C.COLOR_LINE, width=3)))
    fig.add_trace(go.Scatter(x=xs, y=[max(0.5, r["max"]) for r in rows], mode="lines+markers", name="Maximum", line=dict(color=C.COLOR_LINE2, width=2, dash="dot")))
    fig.update_xaxes(title_text="Aufgaben n", tickvals=xs)
    fig.update_yaxes(title_text="Zahl der Kreise (logarithmisch)", type="log")
    return _base(fig, 340)
