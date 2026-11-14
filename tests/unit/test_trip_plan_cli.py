"""T023/T028: CLI tests for skills-src/baku-trip-catalog/scripts/trip_plan.py.

The script runs as a separate process from its own folder, exactly as in the skill sandbox, so it
imports its own synced pricing.py and reads its own references/catalog.json.
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills-src" / "baku-trip-catalog" / "scripts"
SCHEMA = json.loads((ROOT / "specs/001-baku-trip-planner/contracts/plan-state.schema.json").read_text())
HOTEL_60 = "htl-caspian-courtyard"


def run(*args):
    proc = subprocess.run(
        [sys.executable, "trip_plan.py", *map(str, args)], cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    return proc


def call(*args):
    proc = run(*args)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)  # exactly one JSON object
    assert set(out) >= {"ok", "state", "markdown", "errors"}
    return out


def start(travelers=2):
    out = call("start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", travelers)
    assert out["ok"], out
    return out["state"]


def st(state):
    return json.dumps(state)


# --- start / set-trip ------------------------------------------------------------------------

def test_start_valid():
    out = call("start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", 2)
    assert out["ok"] is True and out["errors"] == []
    assert out["state"]["trip"]["nights"] == 4
    assert "10 Mar 2027 → 14 Mar 2027 · 4 nights · 2 travelers" in out["markdown"]
    jsonschema.validate(out["state"], SCHEMA)


def test_start_validation_errors_exit_zero():
    cases = [
        (("2027-02-30", "2027-03-02", 2), "invalid_date"),
        (("2027-03-14", "2027-03-10", 2), "check_out_before_check_in"),
        (("2020-01-01", "2020-01-03", 2), "check_in_in_past"),
        (("2027-03-01", "2027-04-01", 2), "stay_too_long"),
        (("2027-03-10", "2027-03-14", 11), "travelers_out_of_range"),
        (("2027-03-10", "2027-03-14", 0), "travelers_out_of_range"),
    ]
    for (ci, co, t), code in cases:
        out = call("start", "--check-in", ci, "--check-out", co, "--travelers", t)
        assert out["ok"] is False and out["errors"][0]["code"] == code, (ci, co, t, out)
        assert out["markdown"] and "Traceback" not in out["markdown"]


def test_set_trip_recalculates():
    state = call("select-hotel", "--state", st(start()), "--hotel-id", HOTEL_60)["state"]
    out = call("set-trip", "--state", st(state), "--travelers", 3)
    assert out["ok"] and out["state"]["grand_total"] == "720.00"
    assert "AZN 720.00" in out["markdown"]


# --- hotels ----------------------------------------------------------------------------------

def test_list_hotels_inline():
    out = call("list-hotels", "--state", st(start()))
    assert out["ok"]
    assert 3 <= len(out["options"]) <= 5
    md = out["markdown"]
    assert md.count("### ") == len(out["options"])
    assert md.count("![") == len(out["options"])
    assert md.count("per person per night") == len(out["options"])
    assert "### 1. Caspian Courtyard Hotel" in md
    assert "*Old City (İçərişəhər)* · **AZN 60.00 per person per night**" in md
    assert "Reply with the number or name of the hotel you'd like." in md
    assert out["options"][0] == {"n": 1, "id": HOTEL_60, "name": "Caspian Courtyard Hotel"}


def test_list_hotels_link_style():
    out = call("list-hotels", "--state", st(start()), "--photo-style", "link")
    assert "![" not in out["markdown"]
    assert out["markdown"].count("[View photo](") == len(out["options"])


def test_select_hotel_spec_example():
    out = call("select-hotel", "--state", st(start()), "--hotel-id", HOTEL_60)
    assert out["ok"]
    assert out["state"]["hotel_id"] == HOTEL_60
    assert out["state"]["lines"][0]["line_total"] == "480.00"
    assert out["state"]["grand_total"] == "480.00"
    assert "| **Grand total** | | | **AZN 480.00** |" in out["markdown"]
    assert out["markdown"].rstrip().endswith("Would you like to see some activities in Baku?")
    jsonschema.validate(out["state"], SCHEMA)


def test_select_second_hotel_replaces_first():
    state = call("select-hotel", "--state", st(start()), "--hotel-id", HOTEL_60)["state"]
    out = call("select-hotel", "--state", st(state), "--hotel-id", "htl-fountain-square-suites")
    hotels = [l for l in out["state"]["lines"] if l["kind"] == "hotel"]
    assert len(hotels) == 1 and hotels[0]["item_id"] == "htl-fountain-square-suites"
    assert out["state"]["grand_total"] == "680.00"


def test_unknown_hotel():
    out = call("select-hotel", "--state", st(start()), "--hotel-id", "htl-four-seasons")
    assert out["ok"] is False and out["errors"][0]["code"] == "unknown_item"


def test_show_plan():
    state = call("select-hotel", "--state", st(start()), "--hotel-id", HOTEL_60)["state"]
    out = call("show-plan", "--state", st(state))
    assert out["ok"] and "**Your Baku trip plan** (draft)" in out["markdown"]


def test_tampered_state_is_recomputed():
    state = call("select-hotel", "--state", st(start()), "--hotel-id", HOTEL_60)["state"]
    state["grand_total"] = "1.00"
    state["lines"][0]["unit_price"] = "1.00"
    out = call("show-plan", "--state", st(state))
    assert out["state"]["grand_total"] == "480.00"


def test_invalid_state_json():
    out = call("show-plan", "--state", "{not json")
    assert out["ok"] is False and out["errors"][0]["code"] == "invalid_state"


def test_unknown_command_is_programming_error():
    assert run("fly-to-moon").returncode == 2


# --- activities (T028, US2) ---------------------------------------------------------------------

WALK_25 = "act-old-city-walking-tour"


def with_hotel(travelers=2):
    return call("select-hotel", "--state", st(start(travelers)), "--hotel-id", HOTEL_60)["state"]


def test_list_activities_inline():
    out = call("list-activities", "--state", st(with_hotel()))
    assert out["ok"]
    assert 3 <= len(out["options"]) <= 6
    md = out["markdown"]
    assert md.count("### ") == len(out["options"]) and md.count("![") == len(out["options"])
    assert md.count(" per person** · ") == len(out["options"])
    assert "### 1. Old City walking tour" in md
    assert "**AZN 25.00 per person** · 3 hours" in md
    assert md.rstrip().endswith('Reply with the number or name of an activity to add it, or say "continue".')


def test_list_activities_link_style():
    out = call("list-activities", "--state", st(with_hotel()), "--photo-style", "link")
    assert "![" not in out["markdown"]
    assert out["markdown"].count("[View photo](") == len(out["options"])


def test_list_activities_requires_hotel():
    out = call("list-activities", "--state", st(start()))
    assert out["ok"] is False and out["errors"][0]["code"] == "hotel_required"


def test_list_activities_hides_ones_in_plan():
    state = call("add-activity", "--state", st(with_hotel()), "--activity-id", WALK_25)["state"]
    out = call("list-activities", "--state", st(state))
    assert WALK_25 not in [o["id"] for o in out["options"]]
    assert len(out["options"]) == 5


def test_add_activity_spec_example():
    out = call("add-activity", "--state", st(with_hotel()), "--activity-id", WALK_25)
    assert out["ok"]
    line = out["state"]["lines"][1]
    assert line["line_total"] == "50.00" and line["quantity_label"] == "2 travelers"
    assert out["state"]["grand_total"] == "530.00"
    assert out["markdown"].rstrip().endswith(
        "Would you like to add more activities, or continue to confirmation?"
    )
    jsonschema.validate(out["state"], SCHEMA)


def test_duplicate_activity():
    state = call("add-activity", "--state", st(with_hotel()), "--activity-id", WALK_25)["state"]
    out = call("add-activity", "--state", st(state), "--activity-id", WALK_25)
    assert out["ok"] is False and out["errors"][0]["code"] == "duplicate_activity"
    assert "Old City walking tour is already in your plan." == out["markdown"]


def test_remove_activity_recalculates():
    state = call("add-activity", "--state", st(with_hotel()), "--activity-id", WALK_25)["state"]
    out = call("remove-activity", "--state", st(state), "--activity-id", WALK_25)
    assert out["ok"] and out["state"]["grand_total"] == "480.00"
    assert out["markdown"].rstrip().endswith(
        "Would you like to add more activities, or continue to confirmation?"
    )


def test_changing_travelers_after_activities():
    state = call("add-activity", "--state", st(with_hotel()), "--activity-id", WALK_25)["state"]
    out = call("set-trip", "--state", st(state), "--travelers", 3)
    assert [l["line_total"] for l in out["state"]["lines"]] == ["720.00", "75.00"]
    assert out["state"]["grand_total"] == "795.00"
