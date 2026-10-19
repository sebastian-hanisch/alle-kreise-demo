"""Alle Kreise: aufzählen und zählen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Reihe „Ordnung und Abhängigkeit“: Wie viele gerichtete Kreise hat ein widersprüchlicher Plan, wie zählt man sie, ohne sich in Sackgassen zu
verlaufen (Johnson gegen naives Absuchen), und welche Beziehung liegt auf den meisten Kreisen?

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import alk_algorithm as A
import alk_constants as C
import alk_evaluation as ev
import alk_experiments as ex
from alk_layout import dunkles_design, kopf_css
from alk_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from alk_visualization import (
    COVERAGE_NAMES,
    build_arc_figure,
    build_checks_figure,
    build_counts_figure,
    build_edges_figure,
    build_growth_figure,
    build_lengths_figure,
    build_naive_figure,
    build_single_figure,
    build_top_edges_figure,
)

st.set_page_config(page_title="Alle Kreise: aufzählen und zählen – Sebastian Hanisch", layout="wide")

_i = ev._i


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


@st.cache_data(show_spinner=False)
def _analysis(settings, with_naive):
    return ev.analyse(settings, with_naive)


@st.cache_data(show_spinner=False)
def _strike_count(n, out, back, seed, edge, budget):
    from alk_scenario import make_instance
    adj = A.strike_edge(make_instance(n, out, back, seed).adj, edge)
    return A.johnson(adj, max_cycles=budget, max_checks=C.CHECK_LIMIT, keep=0)


@st.cache_data(show_spinner=False)
def _counts():
    return ex.count_rows()


@st.cache_data(show_spinner=False)
def _single():
    return ex.single_rows()


@st.cache_data(show_spinner=False)
def _naive():
    return ex.naive_rows()


@st.cache_data(show_spinner=False)
def _edges():
    return ex.edge_rows()


@st.cache_data(show_spinner=False)
def _growth():
    return ex.growth_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in alk_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🌀 Alle Kreise: aufzählen und zählen")
st.markdown(
    """
Stück 1 hat **einen** Kreis als Beleg geliefert. Wer einen widersprüchlichen Plan reparieren soll, fragt weiter: **Wie viele Kreise gibt es überhaupt**, und lohnt es sich, sie alle aufzuzählen? Die Antwort überrascht:
**Wenige Widersprüche erzeugen sehr viele Kreise**, die Zahl springt von Plan zu Plan, und das naive Absuchen verläuft sich in Sackgassen, die **Johnson** (1975) mit einer **Blockierung** umgeht.
Am Ende steht die Frage, welche **Beziehung** auf den meisten Kreisen liegt: ein Vorgriff auf das Auflösen der Kreise in Stück 3.

Das ist das zweite Stück der Reihe **Ordnung und Abhängigkeit**. Einen Kreis belegen zeigt Stück 1 (**di-kreis-demo**), die Zerlegung in Zusammenhangskomponenten die Demo **scc-demo**.
Weiter unten: die Experimente **🔬**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So zählt man alle Kreise", expanded=True):
    st.markdown(
        """
1. **Aufzählen:** Jeder Kreis wird genau einmal gefunden, und zwar von seiner **kleinsten Aufgabe** aus. Für jede Startaufgabe s sucht man Pfade, die nur Aufgaben mit größerer Nummer benutzen und zu s zurückführen.
2. **Johnson:** Eine Aufgabe, von der aus **kein Weg zurück** zu s führt, wird **blockiert** und erst wieder freigegeben, wenn auf einem Pfad durch sie ein Kreis gefunden wurde. So läuft die Suche nie zweimal in dieselbe Sackgasse; die Zeit bleibt proportional zu (Aufgaben + Beziehungen) mal (Kreise + 1).
3. **Naiv:** Dasselbe Absuchen **ohne** Blockierung findet dieselben Kreise, geht aber für jeden Zugang erneut in jede Sackgasse.
4. **Budget:** Weil die Zahl der Kreise schnell wächst, zählt die App nur bis zum **Kreisbudget**. Wird es überschritten, ist die Zahl eine **untere Schranke** („mehr als …“).
5. **Welche Beziehung?** Die **Belegung** einer Beziehung ist die Zahl der Kreise, die sie enthalten. Streicht man sie, verschwinden genau diese Kreise.

| Begriff | Bedeutung |
|---|---|
| **Elementarkreis** | ein Kreis, der keine Aufgabe zweimal besucht (die App zählt nur solche) |
| **Blockierung** | Merker bei Johnson: von dieser Aufgabe führt jetzt kein Weg zurück zum Start |
| **Budget** | Höchstzahl der Kreise (und Kantenprüfungen), bis zu der die App aufzählt |
| **Belegung** | Zahl der Kreise, die eine Beziehung enthalten |
| **Pfadzahl** | Bei genau einem Widerspruch: Zahl der Pfade von seinem Ziel zu seinem Anfang im Rest des Plans; sie ist die Zahl der Kreise |
| **Kantenprüfung** | jede Beziehung, die ein Verfahren ansieht; so wird der Aufwand gezählt, nicht in Sekunden |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Plan**")
    n = st.slider("Aufgaben n", *bounds("n_slider"), key="n_slider", help="Wie viele Aufgaben der Plan hat. Bis 60: darüber wäre das Aufzählen kaum noch sinnvoll.")
    out = st.slider("Beziehungen je Aufgabe", *bounds("out_slider"), key="out_slider", step=C.OUT_STEP,
                    help="Mittlerer Ausgangsgrad: Zahl der Beziehungen „A vor B“ geteilt durch die Zahl der Aufgaben (höchstens alle Paare).")
    back = st.slider("Widersprüche", *bounds("back_slider"), key="back_slider",
                     help="Wie viele Beziehungen gegen die Wunschreihenfolge umgedreht werden (höchstens so viele, wie es Beziehungen gibt).")
    seed = st.number_input("Zufalls-Seed des Plans", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Plan erzeugen", width="stretch", on_click=randomize_seed)
    st.markdown("**Aufzählung**")
    budget = st.selectbox("Kreisbudget", list(C.BUDGETS), format_func=lambda b: f"höchstens {_i(b)} Kreise", key="budget_select",
                          help="Die Aufzählung bricht ab, sobald mehr Kreise gefunden sind. Dann ist die Zahl nur eine untere Schranke.")
    view = st.selectbox("Anzeige", list(C.VIEWS), format_func=C.VIEW_NAMES.get, key="view_select",
                        help="Welches Verfahren läuft. „Beide“ lässt zusätzlich das naive Absuchen laufen (mit eigenem Prüfungsbudget) und vergleicht die Kantenprüfungen.")

sync_query_params({"n_slider": int(n), "out_slider": float(out), "back_slider": int(back), "seed_input": int(seed), "budget_select": int(budget), "view_select": view})

settings = ev.Settings(int(n), float(out), int(back), int(seed), int(budget))
with st.spinner("Zähle die Kreise..."):
    a = _analysis(settings, view in ("naiv", "beide"))
inst, run = a.inst, a.johnson
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{inst.n}_{settings.out}_{settings.back}_{settings.seed}_{settings.budget}"

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
real_back = len(inst.reversed_edges)
st.caption(f"{_i(inst.n)} Aufgaben, {_i(inst.m)} Beziehungen, davon {_i(real_back)} gegen die Wunschreihenfolge umgedreht"
           + (f" (gewünscht: {_i(settings.back)}, es gibt nicht mehr Beziehungen)." if real_back < settings.back else ".") + " Aufgaben sind ab 1 nummeriert.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kreise im Plan", ev.count_text(a.count, a.aborted, settings.budget), delta="vollständig gezählt" if a.complete else "untere Schranke", delta_color="off")
m2.metric("Kürzester / längster", f"{min(run.lengths)} / {max(run.lengths)}" if run.lengths else "–", delta="Aufgaben im Kreis" if run.lengths else "kein Kreis", delta_color="off")
if a.top:
    m3.metric("Meistbelegte Beziehung", ev.format_edge(a.top[0][0]), delta=f"auf {ev._pct(a.top[0][1] / a.count)} % der Kreise", delta_color="off")
else:
    m3.metric("Meistbelegte Beziehung", "–", delta="kein Kreis", delta_color="off")
if a.naive is not None:
    # Delta immer „mein Wert minus Referenz“; weniger Kantenprüfungen sind besser, deshalb delta_color="inverse".
    diff_checks = run.checks - a.naive.checks
    m4.metric("Prüfungen (Johnson)", _i(run.checks), delta=f"{diff_checks:+,} gegen naiv".replace(",", ".") if diff_checks else "gleich viele wie naiv", delta_color="inverse" if diff_checks else "off")
else:
    m4.metric("Prüfungen (Johnson)", _i(run.checks), delta="Anzeige „beide“ vergleicht", delta_color="off")

tab_list, tab_count, tab_edge = st.tabs(["📜 Aufzählen", "🔢 Zählen", "🎯 Welche Beziehung?"])

# --- Tab 1: Aufzählen ----------------------------------------------------------------------------------------------------------------------

with tab_list:
    if a.count == 0:
        st.success("Der Plan ist kreisfrei: Es gibt nichts aufzuzählen. Mit einem Widerspruch mehr oder mehr Beziehungen je Aufgabe entstehen Kreise; die Schnellstart-Szenarien zeigen Fälle.")
        st.plotly_chart(build_arc_figure(inst), width="stretch", key="arc_none")
    else:
        shown = a.listing[: C.LIST_ROWS]
        if a.aborted:
            st.warning(f"Die Aufzählung brach bei {ev.count_text(a.count, a.aborted, settings.budget)} Kreisen ab; die Liste zeigt die kürzesten der bis dahin gefundenen.")
        picked = st.selectbox("Kreis ansehen", list(range(len(shown))), key=f"pick_{signature}",
                              format_func=lambda i: f"{i + 1}. Kreis, {len(shown[i])} Aufgaben: {ev.format_cycle(shown[i], limit=8)}",
                              help="Wählt einen der aufgezählten Kreise (kürzeste zuerst); er wird im Bild rot gezeichnet.")
        left, right = st.columns([3, 2])
        with left:
            st.plotly_chart(build_arc_figure(inst, cycle=shown[picked]), width="stretch", key="arc_pick")
            st.caption("Der gewählte Kreis in Rot. Oben blau die Beziehungen in Richtung der Wunschreihenfolge (Pfeile von links nach rechts), unten violett die Widersprüche (von rechts nach links).")
        with right:
            table = pd.DataFrame({"Nr.": range(1, len(shown) + 1), "Länge": [len(c) for c in shown], "Kette": [ev.format_cycle(c, limit=40) for c in shown]})
            st.dataframe(table, hide_index=True, width="stretch", height=380)
            more = len(a.listing) - len(shown)
            st.caption(f"Die kürzesten {_i(len(shown))} Kreise" + (f"; {_i(more)} weitere sind aufgezählt, aber nicht abgebildet." if more > 0 else "."))
        st.plotly_chart(build_lengths_figure(run.lengths), width="stretch", key="chart_lengths")
        st.caption("Zahl der Kreise je Länge: die meisten Kreise sind deutlich länger als der kürzeste, den Stück 1 liefert.")

# --- Tab 2: Zählen -------------------------------------------------------------------------------------------------------------------------

with tab_count:
    if a.count == 0:
        st.success("Kein Kreis, also nichts zu zählen. Johnson hat trotzdem jede Beziehung einer Startkomponente geprüft.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Johnson (mit Blockierung)")
            st.metric("Kantenprüfungen", _i(run.checks))
            st.caption("Aufwand höchstens proportional zu (Aufgaben + Beziehungen) mal (Kreise + 1).")
        with c2:
            st.markdown("#### Naives Absuchen")
            if a.naive is None:
                st.info("Die Anzeige „Johnson“ lässt das naive Absuchen nicht laufen. Wählen Sie „Beide gegenübergestellt“ oder „Naives Absuchen“ in der Seitenleiste.")
            else:
                nv = a.naive
                st.metric("Kantenprüfungen", _i(nv.checks) + (" (abgebrochen)" if nv.aborted else ""),
                          delta=(f"{nv.checks / run.checks:.1f}-mal so viele wie Johnson".replace(".", ",") if run.checks else None), delta_color="off")
                if nv.aborted:
                    st.caption(f"Das naive Absuchen erreichte sein Budget ({_i(C.NAIVE_CHECK_LIMIT)} Kantenprüfungen oder das Kreisbudget) und zählt {ev.count_text(nv.count, nv.aborted, settings.budget)} Kreise.")
                else:
                    st.caption("Dieselben Kreise, aber jede Sackgasse wird für jeden Zugang erneut durchlaufen.")
        if a.naive is not None:
            st.plotly_chart(build_checks_figure(run.checks, a.naive.checks, bool(a.naive.aborted)), width="stretch", key="chart_checks")
        if a.by_paths is not None:
            (bad,) = inst.reversed_edges
            st.markdown("#### Ein einziger Widerspruch: die Kreise sind Pfade")
            st.markdown(f"Genau eine Beziehung läuft gegen die Wunschreihenfolge: **{ev.format_edge(bad)}**. Jeder Kreis besteht aus dieser Beziehung und einem Pfad von Aufgabe {ev.label(bad[1])} nach Aufgabe {ev.label(bad[0])} im Rest des Plans. "
                        f"Dieser Rest ist kreisfrei; die **Pfadzahl** lässt sich dort ohne Aufzählung ausrechnen (Summe über eine topologische Ordnung): **{_i(a.by_paths)}** Pfade, und {_i(a.count)} Kreise zählt Johnson.")
        if a.aborted:
            st.warning("Das Budget wurde erreicht: Die Zahl der Kreise ist nur eine untere Schranke. Mit weniger Widersprüchen oder einem größeren Budget wird sie vollständig; "
                       "für große Pläne sind Kreise meist nicht mehr aufzählbar, man braucht dann Stück 3 (Kreise auflösen).")

# --- Tab 3: Welche Beziehung? --------------------------------------------------------------------------------------------------------------

with tab_edge:
    if a.count == 0:
        st.success("Kein Kreis, also keine Beziehung, die man ändern müsste.")
    else:
        if a.aborted:
            st.warning("Die Belegung beruht nur auf den bis zum Abbruch gefundenen Kreisen.")
        st.plotly_chart(build_top_edges_figure(list(a.top), run.count), width="stretch", key="chart_top")
        st.caption(f"Die {len(a.top)} meistbelegten Beziehungen; über den Balken der Anteil an allen gefundenen Kreisen.")
        options = [e for e, _ in a.top]
        chosen = st.selectbox("Beziehung streichen", list(range(len(options))), key=f"strike_{signature}",
                              format_func=lambda i: f"{ev.format_edge(options[i])} (liegt auf {_i(a.top[i][1])} Kreisen)",
                              help="Streicht die gewählte Beziehung und zählt die Kreise neu.")
        edge = options[chosen]
        after = _strike_count(inst.n, settings.out, settings.back, settings.seed, edge, settings.budget)
        s1, s2, s3 = st.columns(3)
        s1.metric("Kreise vorher", ev.count_text(run.count, run.aborted, settings.budget))
        s2.metric("Kreise nachher", ev.count_text(after.count, after.aborted, settings.budget), delta=None if (run.aborted or after.aborted) else f"{after.count - run.count:+,}".replace(",", "."), delta_color="inverse")
        rev_on = sum(1 for e in inst.reversed_edges if e in run.coverage)
        s3.metric("Widersprüche auf einem Kreis", f"{rev_on} von {real_back}" if real_back else "–", delta=None)
        st.plotly_chart(build_arc_figure(inst, coverage=run.coverage, count=run.count, struck=edge), width="stretch", key="arc_edges")
        st.caption("Die Beziehungen sind nach ihrer Belegung gefärbt (" + ", ".join(f"{name}" for name in COVERAGE_NAMES) + ": hell bis dunkel); die gewählte Beziehung ist gepunktet gezeichnet. "
                   "Ob die Beziehung mit der höchsten Belegung auch die **beste** zum Streichen ist, beantwortet Stück 3 der Reihe.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Kreise hat der Plan, und welche Beziehung löst die meisten?")
_show(ev.verdict_question(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

with st.spinner("Rechne die Experimente (einmalig, einige Sekunden)..."):
    rows_c, rows_s, rows_n, rows_e, rows_g = _counts(), _single(), _naive(), _edges(), _growth()

st.subheader("🔬 Experiment 1: Wie schnell wächst die Zahl der Kreise?")
st.caption(f"{C.E1_N} Aufgaben, je Zelle {len(C.E1_SEEDS)} feste Pläne, Kreisbudget {_i(C.E1_BUDGET)} je Plan; abgebrochene Pläne zählen als Budget + 1. Median (durchgezogen) und Maximum (gepunktet).")
st.plotly_chart(build_counts_figure(rows_c), width="stretch", key="chart_counts")
_show(ev.verdict_counts(rows_c))

st.subheader("🔬 Experiment 2: Ein einziger Widerspruch")
st.caption(f"Genau eine umgedrehte Beziehung, je Plangröße {len(C.E2_SEEDS)} feste Pläne; die Kreiszahl ist die Pfadzahl im Rest des Plans (zweiter Rechenweg, ohne Aufzählung).")
st.plotly_chart(build_single_figure(rows_s), width="stretch", key="chart_single")
_show(ev.verdict_single(rows_s))

st.subheader("🔬 Experiment 3: Johnson gegen naives Absuchen")
st.caption(f"Je Fall {len(C.E3_SEEDS)} feste Pläne mit Kreis, beide Verfahren bis {_i(C.E3_CHECKS)} Kantenprüfungen; Median über die Pläne, die beide fertig zählen.")
st.plotly_chart(build_naive_figure(rows_n), width="stretch", key="chart_naive")
_show(ev.verdict_naive(rows_n))

st.subheader("🔬 Experiment 4: Die meistbelegte Beziehung")
st.caption(f"{C.E4_N} Aufgaben, mittlerer Ausgangsgrad {C.E4_OUT:g}, je Zeile {len(C.E4_SEEDS)} feste Pläne mit mindestens zwei und höchstens {_i(C.KEEP)} Kreisen; Median über die Pläne.")
st.plotly_chart(build_edges_figure(rows_e), width="stretch", key="chart_edges")
_show(ev.verdict_edges(rows_e))

st.subheader("🔬 Experiment 5: Wächst die Kreiszahl mit der Plangröße?")
st.caption(f"Mittlerer Ausgangsgrad {C.E5_OUT:g}, {int(C.E5_SHARE * 100)} % der Beziehungen umgedreht, je Größe {len(C.E5_SEEDS)} feste Pläne, Kreisbudget {_i(C.E5_BUDGET)}.")
st.plotly_chart(build_growth_figure(rows_g), width="stretch", key="chart_growth")
_show(ev.verdict_growth(rows_g))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Synthetische Pläne mit verdeckter Wunschreihenfolge** | Echte Abhängigkeiten haben Stufen und Gruppen; wie viele Kreise dort entstehen, zeigt diese Demo nicht. | - |
| **Aufzählen bis zum Budget** | Ab einer gewissen Zahl von Widersprüchen (Experiment 1) ist die Aufzählung nicht mehr vollständig möglich; die Demo meldet dann „mehr als“ das Budget und zählt nicht weiter. | Stück 3 der Reihe (Kreise auflösen, ohne alle aufzuzählen) |
| **Aufwand in Kantenprüfungen** | Sekunden hängen von Sprache und Datenstruktur ab; die Verhältnisse der Verfahren gelten als Zählung. | - |
| **Elementarkreise sind nicht unabhängig** | Viele Kreise teilen sich Beziehungen (Experiment 4); die Zahl der Kreise ist deshalb kein Maß für die Zahl der nötigen Änderungen. | Stück 3 der Reihe |
| **Belegung als Hinweis** | Die am häufigsten belegte Beziehung ist nicht immer die beste zum Streichen; die kleinste Menge zu streichender Beziehungen ist NP-schwer und ein eigenes Stück. | Stück 3 der Reihe |
| **Nur gerichtete Pläne** | Ungerichtete Kreise (Kreisraum, Fundamentalkreise) sind ein anderes Thema und nicht Teil dieser Reihe. | - |
| **Größe** | Bis {C.N_MAX} Aufgaben und {C.BACK_MAX} Widersprüche; Prüfungsbudget Johnson {_i(C.CHECK_LIMIT)}, naiv {_i(C.NAIVE_CHECK_LIMIT)} Kantenprüfungen. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein gerichteter Graph $G = (V, E)$ mit $n = |V|$ Aufgaben und $m = |E|$ Beziehungen. **Gesucht:** die Menge $\mathcal{C}$ aller Elementarkreise (Kreise ohne Wiederholung einer Aufgabe), ihre Zahl $c = |\mathcal{C}|$ und für jede Beziehung $e$ die Belegung $\beta(e)$.

| Symbol | Bedeutung |
|---|---|
| $\mathcal{C}$, $c$ | Menge der Elementarkreise und ihre Zahl |
| $\beta(e)$ | Zahl der Kreise, die die Beziehung $e$ enthalten |
| $G - e$ | der Plan ohne die Beziehung $e$ |
| $P_{G}(u, v)$ | Zahl der Pfade von $u$ nach $v$ in $G$ |

**Johnson.** Jeder Kreis wird genau einmal gefunden, von seiner kleinsten Aufgabe aus; mit der Blockierung ist die Zeit höchstens

$$\mathcal{O}\big((n + m)\,(c + 1)\big).$$

**Belegung und Streichen.** Streicht man eine Beziehung $e$, verschwinden genau die Kreise durch $e$:

$$c(G - e) = c(G) - \beta(e).$$

**Ein einziger Widerspruch.** Ist $G - e$ kreisfrei für $e = (a, b)$, dann sind die Kreise von $G$ genau die Kreise durch $e$, also die Pfade von $b$ nach $a$ in $G - e$, und diese Zahl lässt sich per Dynamik über eine topologische Ordnung berechnen:

$$c(G) = P_{G - e}(b, a).$$

**Vollständiger Digraph.** Auf $k$ Aufgaben, die alle paarweise in beide Richtungen verbunden sind, gibt es

$$c(K_k) = \sum_{j=2}^{k} \binom{k}{j}\,(j - 1)!$$

Kreise (für $k = 3$ sind es 5, für $k = 4$ sind es 20). Eine Kette aus $r$ Rauten mit einer Rückkante hat $2^{r}$ Kreise.

**Literatur.** D. B. Johnson: *Finding all the elementary circuits of a directed graph*, SIAM Journal on Computing 4 (1), 1975, S. 77–84. J. C. Tiernan: *An efficient search algorithm to find the elementary circuits of a graph*, Communications of the ACM 13 (12), 1970, S. 722–726 (Vorläufer ohne Blockierung). Die Aussagen oben sind Lehrbuchwissen; die Tests belegen sie an Mini-Instanzen und gegen networkx.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
