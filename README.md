# Alle Kreise: aufzählen und zählen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-alle-kreise-demo.streamlit.app/)** -->

Zweites Stück der Reihe **Ordnung und Abhängigkeit** (Arbeitstitel der Linie `dag-abhaengigkeiten`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Nachfolger von `di-kreis-demo` (Stück 1: ein Kreis als Beleg); derselbe Generator, dieselbe Nummerierung. Vehikel: **Aufgabenabhängigkeiten** („A vor B“) mit verdeckter Wunschreihenfolge, bei der ein einstellbarer Teil der Beziehungen umgedreht wird (Widersprüche). Die Demo fragt: Wie viele gerichtete Kreise hat der Plan, wie zählt man sie, ohne sich in Sackgassen zu verlaufen (**Johnson** gegen naives Absuchen), und welche Beziehung liegt auf den meisten Kreisen?

Nachbarn: `scc-demo` (Graphen und Netzwerke) zerlegt Graphen in starke Zusammenhangskomponenten; `di-kreis-demo` belegt einen Kreis. Das **Auflösen** der Kreise (Stück 3 der Reihe) ist noch nicht gebaut.

## Warum dieses Problem

Wer einen widersprüchlichen Plan reparieren soll, fragt nach dem einen Zeugen aus Stück 1 sofort weiter: Gibt es noch mehr Kreise, und wie viele? Die Zahl der Kreise ist erstaunlich groß und springt von Plan zu Plan; schon ein einziger Widerspruch kann Hunderte Kreise erzeugen. Darum braucht die Aufzählung ein Budget, und darum lohnt die Frage, ob eine einzige Beziehung fast alle Kreise trägt.

## Befunde und Korrekturen gegenüber dem Plan

- **Zahlen des Einzelplans neu gemessen.** Der Einzelplan nannte für Johnson gegen naiv den Faktor 6 bis 137 aus einer Vormessung mit anderen Seeds und anderem Prüfungsbudget. Mit dem Demo-Code und den festen Plänen der Demo (Experiment 3) sind es **5,3 bis 96,8**; die Aussage („Johnson spart Sackgassen, der Faktor sinkt mit der Kreiszahl“) bleibt.
- **Kreisbudget im Experiment 1: 20 000 statt 200 000**, damit die einmalige Rechnung auf der Cloud nur einige Sekunden braucht. Folge: bei 24 Widersprüchen (Grad 3) ist der Median „mehr als 20 000“ statt 25 193,5; die Aussage (Explosion zwischen 8 und 24 Widersprüchen) bleibt.
- **Regler „Widersprüche“ als Anzahl** (0 bis 40) wie in Stück 1; die Experimente 1, 4 und 5 rechnen mit Anteilen oder Zählungen auf festen Plänen.

## Modell

Aufgaben 0 bis n−1 mit zufälligen Nummern; eine **verdeckte Wunschreihenfolge** ordnet sie. Es gibt m = n · (mittlerer Ausgangsgrad) Beziehungen (höchstens alle Paare), jede zunächst von früh nach spät. Danach werden die einstellbaren **Widersprüche** umgedreht (nie mehr als Beziehungen). Der Zufall kommt aus `random.Random(seed).random()`. Aufgaben sind in der Anzeige ab 1 nummeriert. Der Aufwand wird in **Kantenprüfungen** gezählt, nicht in Sekunden. Gezählt werden **Elementarkreise** (keine Aufgabe zweimal); jeder wird genau einmal gefunden, von seiner kleinsten Aufgabe aus. Details und Sätze: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Johnson (1975):** für jede Startaufgabe s nur der Teilgraph ab s und darin die Komponente von s; eine Aufgabe ohne Weg zurück zu s wird **blockiert** und erst freigegeben, wenn durch sie ein Kreis gefunden wurde. Zeit höchstens O((n + m)(c + 1)).
- **Naives Absuchen** (Tiernan-Art): dieselbe Suche ohne Blockierung; findet dieselben Kreise, läuft aber für jeden Zugang erneut in jede Sackgasse.
- **Budget:** Kreisbudget (100 bis 100 000) und Prüfungsbudget; wird es überschritten, ist die Zahl eine **untere Schranke** („mehr als …“).
- **Zweiter Weg bei genau einem Widerspruch:** die Kreise sind die Pfade vom Ziel zum Anfang der umgedrehten Beziehung im Rest des Plans; die **Pfadzahl** wird per DP über eine topologische Ordnung berechnet.
- **Belegung einer Beziehung:** Zahl der Kreise, die sie enthalten; Streichen entfernt genau diese. Die App prüft jedes Ergebnis vor der Anzeige (Kreise, Duplikate, Kreislängen, Belegung, Pfadzahl, Johnson gegen naiv).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Mediane über feste Pläne, nie ein einzelner Zufalls-Seed.

| Frage | Befund |
|---|---|
| Wie schnell wächst die Zahl der Kreise? (40 Aufgaben, Grad 3, 30 Pläne je Zelle, Kreisbudget 20 000) | Median **0 / 1,5 / 6,5 / 103 / 312,5 / 2 293,5 / mehr als 20 000** bei 1 / 2 / 4 / 8 / 12 / 16 / 24 Widersprüchen; bei 24 Widersprüchen überschreiten **17 von 30** Plänen das Budget. Bei Grad 2 sind es mit 24 Widersprüchen nur 100,5 (Maximum 801). |
| Was erzeugt ein einziger Widerspruch? | Bei 100 Aufgaben und Grad 4 schließt er in **43 von 100** Plänen einen Kreis, im Median 3 und im Maximum **268** Kreise (60 Aufgaben, Grad 3: 25 von 100, Maximum 32; 200 Aufgaben, Grad 4: 23 von 100, Maximum 157). Die Zahl stimmt mit der Pfadzahl im Rest des Plans überein. |
| Johnson gegen naives Absuchen? | Das naive Absuchen braucht im Median **5,3 bis 96,8** mal so viele Kantenprüfungen: 223 gegen 9 (30 Aufgaben, 4 Widersprüche), 1 694,5 gegen 17,5 (60 Aufgaben, 3 Widersprüche) bis 36 903,5 gegen 6 927,5 (60 Aufgaben, 12 Widersprüche, 383,5 Kreise). Der Faktor sinkt, wenn die Kreiszahl wächst. |
| Wie fest sitzt eine einzige Beziehung auf den Kreisen? (40 Aufgaben, Grad 3, Pläne mit 2 bis 20 000 Kreisen) | Die meistbelegte Beziehung liegt bei 8 / 12 Widersprüchen auf **88,5 / 86,2 %** aller Kreise; nach ihrem Streichen bleiben 11,5 / 13,8 %. **75 / 83,3 %** der Widersprüche liegen auf einem Kreis. |
| Wie lang sind die Kreise? | Kürzester / Median / längster Kreis **3 / 8 / 14** (8 Widersprüche) und **3 / 11 / 17** (12 Widersprüche): die meisten Kreise sind deutlich länger als der kürzeste. |
| Wächst die Kreiszahl mit der Plangröße? (Grad 3, 5 % umgedreht, 20 Pläne je Größe) | Median bei n = 20 / 30 / 40 / 50 / 60: **5,5 / 19 / 32 / 63,5 / 39**, Maximum **93 / 353 / 1 545 / 11 492 / 1 043**: das Maximum liegt bis zum 181-fachen über dem Median, die Mediane wachsen nur 7,1-fach. |
| Stimmen die Verfahren mit einer Bibliothek überein? | Kreismengen und Kreiszahlen stimmen mit `networkx.simple_cycles` auf **240** festen Plänen überein (0 Abweichungen), Kreislängen und die Belegung jeder Beziehung auf 100; dazu Aufzählung aller Folgen (120 kleine Pläne) und Pfadzahl (150 Pläne mit einem Widerspruch), `tests/test_oracle_alle_kreise.py`. |

## Ehrliche Grenzen

- **Synthetische Pläne.** Verdeckte Zufallsordnung, keine echten Bau- oder Umschlagpläne; wie viele Kreise echte Abhängigkeiten (Stufen, Gruppen, Knoten mit vielen Nachfolgern) haben, zeigt die Demo nicht.
- **Aufzählen nur bis zum Budget.** Ab einer gewissen Zahl von Widersprüchen ist die Aufzählung nicht mehr vollständig möglich; die Demo meldet „mehr als“ das Budget und zählt nicht weiter. Das ist Absicht, kein Fehler.
- **Aufwand in Kantenprüfungen.** Sekunden werden nicht gemessen.
- **Die meistbelegte Beziehung ist nur ein Hinweis.** Sie ist nicht immer die beste zum Streichen; die kleinste Menge zu streichender Beziehungen ist ein eigenes Problem (Stück 3).
- **Der Faktor Johnson gegen naiv** sinkt mit der Kreiszahl; in den gemessenen Plänen ist Johnson immer sparsamer, aber nicht immer um ein Vielfaches.
- **Größe:** bis 60 Aufgaben und 40 Widersprüche.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 142 Tests (Laufzeit unter einer Minute auf dem Entwicklungsrechner):

- **Kern:** jede Einheit an von Hand gerechneten Mini-Instanzen (Eigenschleife, zwei gegeneinander, Dreieck, zwei Kreise mit gemeinsamer Aufgabe, vollständige Digraphen mit 5 und 20 Kreisen, Kette aus Rauten mit 2^r Kreisen, Kreis hinter einem Vorlauf); Budgets, Abbrüche, kanonische Kreise.
- **Orakel** (`test_oracle_alle_kreise.py`): `networkx.simple_cycles`, Aufzählung aller Folgen verschiedener Aufgaben und die Pfadzahl-DP auf festen Plänen; Belegung und Kreislängen gegen networkx; Streichen entfernt genau die Kreise durch die Beziehung.
- **Invarianten:** Antwort unabhängig von der Nummerierung; Kreiszahl null genau dann, wenn der Plan kreisfrei ist; jeder Kreis ist ein Kreis, kanonisch und einmalig.
- **Zweige** (`test_branches.py`): jedes Preset löst seine Beschreibung ein (ohne Kreis, viele Kreise bei einem Widerspruch, Hunderte Kreise, Budget reicht nicht, eine Beziehung auf fast allen Kreisen, naiv gegen Johnson); Prüfungsbudget von Johnson und naiv.
- **Verdikte** (`test_verdicts.py`) an handgesetzten Werten; **Befunde** (`test_claims.py`) für jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe, Worst-Case am Reglermaximum (n = 60, Grad 4, 40 Widersprüche, Budget 100 000) ohne Zeit-Assertion.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Aufzählen, Zählen, Welche Beziehung?, fünf Experimente |
| `alk_algorithm.py` | Kern: Johnson, naives Absuchen, Pfadzahl, Belegung, Streichen, Prüfer |
| `alk_constants.py` | Regler-Grenzen, Budgets, Raster der Experimente, Farben, Presets |
| `alk_evaluation.py` | Analyse, Prüfung vor der Anzeige, Verdikte |
| `alk_experiments.py` | Experimente über feste Pläne |
| `alk_layout.py` | Fester Kopf (Stylesheet) |
| `alk_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `alk_scenario.py` | Pläne mit verdeckter Wunschreihenfolge (derselbe Generator wie in Stück 1) |
| `alk_visualization.py` | Plotly-Abbildungen (Bogendiagramm mit Belegung, Experimente; Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenprobe) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Orakel, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Kreise auflösen** (kleinste Menge zu streichender Beziehungen, Feedback Arc Set): Stück 3 der Reihe.
- **Kürzester Kreis als eigenes Thema:** Stück 1; hier nur als Kennzahl.
- **Zusammenhangskomponenten und Kondensation:** `scc-demo`.
- **Zeitmessung in Sekunden:** Aufwand wird in Kantenprüfungen gezählt.
- **Echte Pläne oder Dateiimport:** die Pläne sind synthetisch.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
