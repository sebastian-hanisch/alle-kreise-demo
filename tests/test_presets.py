"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Spezifikationen."""

import alk_constants as C
import alk_evaluation as ev
import alk_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, p in C.PRESETS.items():
        assert C.N_MIN <= p["n"] <= C.N_MAX, name
        assert C.OUT_MIN <= p["out"] <= C.OUT_MAX and abs(p["out"] / C.OUT_STEP - round(p["out"] / C.OUT_STEP)) < 1e-9, name   # auf dem Reglerraster
        assert C.BACK_MIN <= p["back"] <= C.BACK_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert p["budget"] in C.BUDGETS and p["view"] in C.VIEWS, name


def test_default_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(first["n"], first["out"], first["back"], first["seed"], first["budget"]) == ev.Settings()
    assert first["view"] == C.DEFAULT_VIEW


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_choice_specs_name_their_allowed_values():
    assert P.SETTING_SPECS["budget_select"].choices == C.BUDGETS and P.SETTING_SPECS["view_select"].choices == C.VIEWS
    assert C.DEFAULT_BUDGET in C.BUDGETS and set(C.VIEW_NAMES) == set(C.VIEWS)


def test_budgets_are_ascending_and_the_prompt_limits_are_positive():
    assert list(C.BUDGETS) == sorted(C.BUDGETS) and C.CHECK_LIMIT > 0 and C.NAIVE_CHECK_LIMIT > 0 and C.KEEP >= C.E4_BACKS[0]
