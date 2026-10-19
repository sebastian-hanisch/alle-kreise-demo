"""Konstanten: Regler-Grenzen, Budgets, Raster der Experimente, Farben und Presets."""

# Rechenbudget am Regler-Maximum (n = 60, Ausgangsgrad 4, also m = 240 Beziehungen):
#   Johnson O((n + m) * (c + 1)) Kantenprüfungen bei c Kreisen; naives Absuchen ohne Schranke, deshalb ein Prüfungsbudget;
#   Kreisbudget und Prüfungsbudget begrenzen jeden Lauf (Abbruch heißt: die Zahl der Kreise ist nur eine untere Schranke).
N_MIN, N_MAX, DEFAULT_N = 6, 60, 12
OUT_MIN, OUT_MAX, OUT_STEP, DEFAULT_OUT = 0.5, 4.0, 0.5, 2.0   # mittlerer Ausgangsgrad
BACK_MIN, BACK_MAX, DEFAULT_BACK = 0, 40, 1                    # umgedrehte Beziehungen (Widersprüche)
SEED_MAX, DEFAULT_SEED = 999999, 22
BUDGETS = (100, 1000, 10000, 100000)                           # höchstens so viele Kreise werden gezählt
DEFAULT_BUDGET = 10000
CHECK_LIMIT = 6_000_000                                        # Prüfungsbudget von Johnson (Schutz gegen Hänger)
NAIVE_CHECK_LIMIT = 1_500_000                                  # Prüfungsbudget des naiven Absuchens
KEEP = 20000                                                   # so viele Kreise bleiben als Liste erhalten
LIST_ROWS = 200                                                # Zeilen der Kreisliste in der App
VIEWS = ("johnson", "naiv", "beide")
VIEW_NAMES = {"johnson": "Johnson (mit Blockierung)", "naiv": "Naives Absuchen", "beide": "Beide gegenübergestellt"}
DEFAULT_VIEW = "beide"
TOP_EDGES = 15

# Feste Instanzen und Raster der Experimente (nie ein einzelner Zufalls-Seed als Befund)
E1_N, E1_OUT, E1_BACKS, E1_SEEDS, E1_BUDGET = 40, (2.0, 3.0), (1, 2, 4, 8, 12, 16, 24), tuple(range(7000, 7030)), 20000
E2_N, E2_OUT, E2_SEEDS = (60, 100, 200), (3.0, 4.0, 4.0), tuple(range(9000, 9100))
E3_CASES = ((30, 2.0, 4), (30, 2.0, 24), (60, 3.0, 3), (60, 3.0, 12))
E3_SEEDS, E3_CHECKS = tuple(range(8000, 8020)), 3_000_000
E4_N, E4_OUT, E4_BACKS, E4_SEEDS = 40, 3.0, (8, 12), tuple(range(11000, 11060))
E5_NS, E5_OUT, E5_SHARE, E5_SEEDS, E5_BUDGET = (20, 30, 40, 50, 60), 3.0, 0.05, tuple(range(12000, 12020)), 20000

# Farben
COLOR_CYCLE = "#d62728"
COLOR_FORWARD = "rgba(76,120,168,0.45)"
COLOR_BACKWARD = "rgba(148,103,189,0.65)"
COLOR_NODE = "#f2f2f2"
COLOR_LINE = "#4c78a8"
COLOR_LINE2 = "#e45756"
COLOR_BAR = "#2F6B65"
COLOR_BAR2 = "#ff9f1c"

PRESETS = {
    "Lehrbeispiel (12 Aufgaben, wenige Kreise)": {"n": DEFAULT_N, "out": DEFAULT_OUT, "back": DEFAULT_BACK, "seed": DEFAULT_SEED, "budget": DEFAULT_BUDGET, "view": "beide"},
    "Ohne Kreis: nichts aufzuzählen": {"n": 12, "out": 2.0, "back": 0, "seed": 1, "budget": DEFAULT_BUDGET, "view": "beide"},
    "Ein Widerspruch, viele Kreise": {"n": 60, "out": 4.0, "back": 1, "seed": 43, "budget": DEFAULT_BUDGET, "view": "beide"},
    "Dicht: Hunderte Kreise": {"n": 30, "out": 3.0, "back": 8, "seed": 10, "budget": DEFAULT_BUDGET, "view": "beide"},
    "Das Budget reicht nicht": {"n": 40, "out": 3.0, "back": 24, "seed": 1, "budget": 1000, "view": "johnson"},
    "Eine Kante löst fast alles": {"n": 40, "out": 3.0, "back": 8, "seed": 21, "budget": DEFAULT_BUDGET, "view": "johnson"},
    "Naiv gegen Johnson": {"n": 60, "out": 3.0, "back": 3, "seed": 63, "budget": DEFAULT_BUDGET, "view": "beide"},
}
PRESET_HELP = {
    "Lehrbeispiel (12 Aufgaben, wenige Kreise)": "Zwölf Aufgaben, ein Widerspruch: wenige Kreise, jeden kann man einzeln ansehen. Das ist die Voreinstellung.",
    "Ohne Kreis: nichts aufzuzählen": "Kein Widerspruch: der Plan ist kreisfrei, die Aufzählung ist leer.",
    "Ein Widerspruch, viele Kreise": "Eine einzige umgedrehte Beziehung, aber mehrere Kreise: ihre Zahl ist die Zahl der Pfade vom Ziel zum Anfang der Beziehung.",
    "Dicht: Hunderte Kreise": "Acht Widersprüche auf 30 Aufgaben mit drei Beziehungen je Aufgabe: die Kreise gehen in die Hunderte.",
    "Das Budget reicht nicht": "24 Widersprüche auf 40 Aufgaben, aber höchstens 1 000 Kreise: die Aufzählung bricht ab, die Zahl ist nur eine untere Schranke.",
    "Eine Kante löst fast alles": "Eine einzige Beziehung liegt auf fast allen Kreisen; streicht man sie, bleibt nur ein kleiner Rest.",
    "Naiv gegen Johnson": "Wenige Kreise, aber das naive Absuchen läuft in unzählige Sackgassen und braucht ein Vielfaches an Kantenprüfungen.",
}
