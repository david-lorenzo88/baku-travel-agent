"""T018: tests for skills-src/_shared/pricing.py (written before the implementation)."""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import jsonschema
import pytest

import pricing

ROOT = Path(__file__).resolve().parents[2]
CATALOG = pricing.load_catalog(ROOT / "skills-src/_shared/catalog.json")
SCHEMA = json.loads((ROOT / "specs/001-baku-trip-planner/contracts/plan-state.schema.json").read_text())
TODAY = date(2026, 11, 13)
HOTEL_60 = "htl-caspian-courtyard"
WALK_25 = "act-old-city-walking-tour"


def new_plan(check_in="2027-03-10", check_out="2027-03-14", travelers=2):
    trip = pricing.validate_trip(check_in, check_out, travelers, today=TODAY)
    return pricing.new_state(trip, CATALOG)


def codes(fn, *args, **kwargs):
    with pytest.raises(pricing.PlanError) as exc:
        fn(*args, **kwargs)
    return exc.value.code


# --- catalog sanity -----------------------------------------------------------------------

def test_catalog_has_spec_example_prices():
    hotels = {h["id"]: h for h in CATALOG["hotels"]}
    acts = {a["id"]: a for a in CATALOG["activities"]}
    assert hotels[HOTEL_60]["price_per_person_per_night"] == "60.00"
    assert acts[WALK_25]["price_per_person"] == "25.00"
    assert CATALOG["currency"] == "AZN"
    assert len(CATALOG["hotels"]) == 5 and len(CATALOG["activities"]) == 6


# --- money ----------------------------------------------------------------------------------

def test_money_formatting():
    assert pricing.fmt_azn(Decimal("1234.5")) == "AZN 1,234.50"
    assert pricing.fmt_azn(Decimal("60")) == "AZN 60.00"
    assert pricing.money_str(Decimal("480")) == "480.00"


def test_half_up_rounding():
    assert pricing.q2(Decimal("0.005")) == Decimal("0.01")
    assert pricing.q2(Decimal("2.675")) == Decimal("2.68")
    assert pricing.q2(Decimal("1.004")) == Decimal("1.00")


# --- trip validation ------------------------------------------------------------------------

def test_nights_are_days_between_dates():
    trip = pricing.validate_trip("2027-03-10", "2027-03-14", 2, today=TODAY)
    assert trip == {"check_in": "2027-03-10", "check_out": "2027-03-14", "travelers": 2, "nights": 4}


@pytest.mark.parametrize(
    "check_in,check_out,travelers,code",
    [
        ("2027-02-30", "2027-03-02", 2, "invalid_date"),
        ("10/03/2027", "2027-03-14", 2, "invalid_date"),
        ("2027-03-14", "2027-03-14", 2, "check_out_before_check_in"),
        ("2027-03-14", "2027-03-10", 2, "check_out_before_check_in"),
        ("2026-11-12", "2026-11-15", 2, "check_in_in_past"),
        ("2027-03-01", "2027-04-01", 2, "stay_too_long"),
        ("2027-03-10", "2027-03-14", 0, "travelers_out_of_range"),
        ("2027-03-10", "2027-03-14", 11, "travelers_out_of_range"),
    ],
)
def test_trip_validation_errors(check_in, check_out, travelers, code):
    assert codes(pricing.validate_trip, check_in, check_out, travelers, today=TODAY) == code


def test_check_in_today_and_30_nights_are_allowed():
    trip = pricing.validate_trip("2026-11-13", "2026-12-13", 10, today=TODAY)
    assert trip["nights"] == 30


def test_today_is_baku_time():
    from datetime import datetime, timezone

    # 22:30 UTC on 12 Nov is 02:30 on 13 Nov in Baku (UTC+4)
    assert pricing.today_baku(datetime(2026, 11, 12, 22, 30, tzinfo=timezone.utc)) == date(2026, 11, 13)


# --- pricing ---------------------------------------------------------------------------------

def test_spec_example_hotel_then_activity():
    state = new_plan()
    state = pricing.set_hotel(state, HOTEL_60, CATALOG)
    hotel_line = state["lines"][0]
    assert hotel_line["kind"] == "hotel"
    assert hotel_line["unit_price"] == "60.00"
    assert hotel_line["quantity"] == 8
    assert hotel_line["quantity_label"] == "2 travelers × 4 nights"
    assert hotel_line["line_total"] == "480.00"
    assert state["grand_total"] == "480.00"

    state = pricing.add_activity(state, WALK_25, CATALOG)
    act_line = state["lines"][1]
    assert act_line["quantity"] == 2 and act_line["quantity_label"] == "2 travelers"
    assert act_line["line_total"] == "50.00"
    assert state["grand_total"] == "530.00"


def test_grand_total_is_sum_of_lines():
    state = pricing.set_hotel(new_plan(travelers=3), "htl-boulevard-bay", CATALOG)
    for act in CATALOG["activities"][:3]:
        state = pricing.add_activity(state, act["id"], CATALOG)
    total = sum(Decimal(l["line_total"]) for l in state["lines"])
    assert Decimal(state["grand_total"]) == total


def test_replacing_hotel_keeps_one_hotel():
    state = pricing.set_hotel(new_plan(), HOTEL_60, CATALOG)
    state = pricing.set_hotel(state, "htl-fountain-square-suites", CATALOG)
    hotels = [l for l in state["lines"] if l["kind"] == "hotel"]
    assert len(hotels) == 1 and hotels[0]["item_id"] == "htl-fountain-square-suites"
    assert state["grand_total"] == "680.00"  # 85 × 2 × 4


def test_recompute_ignores_input_prices_and_totals():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    tampered = json.loads(json.dumps(state))
    tampered["grand_total"] = "1.00"
    tampered["lines"][0]["unit_price"] = "1.00"
    tampered["lines"][0]["line_total"] = "1.00"
    tampered["lines"][0]["name"] = "Free Palace"
    again = pricing.recompute(tampered, CATALOG)
    assert again["grand_total"] == "530.00"
    assert again["lines"][0]["name"] == "Caspian Courtyard Hotel"


def test_changing_travelers_recalculates_every_line():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    state = pricing.set_trip(state, CATALOG, travelers=3, today=TODAY)
    assert [l["line_total"] for l in state["lines"]] == ["720.00", "75.00"]
    assert state["grand_total"] == "795.00"


def test_unknown_items():
    state = new_plan()
    assert codes(pricing.set_hotel, state, "htl-four-seasons", CATALOG) == "unknown_item"
    state = pricing.set_hotel(state, HOTEL_60, CATALOG)
    assert codes(pricing.add_activity, state, "act-skydiving", CATALOG) == "unknown_item"
    assert codes(pricing.remove_activity, state, WALK_25, CATALOG) == "unknown_item"


def test_activity_requires_hotel():
    assert codes(pricing.add_activity, new_plan(), WALK_25, CATALOG) == "hotel_required"


def test_duplicate_activity():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    assert codes(pricing.add_activity, state, WALK_25, CATALOG) == "duplicate_activity"


def test_remove_activity():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    state = pricing.remove_activity(state, WALK_25, CATALOG)
    assert state["activity_ids"] == [] and state["grand_total"] == "480.00"


def test_confirmed_plan_cannot_change():
    state = pricing.set_hotel(new_plan(), HOTEL_60, CATALOG)
    state["status"] = "confirmed"
    state["holder"] = {"full_name": "Ana Smith", "email": "ana@example.com", "phone": "+34 600 000 000"}
    state["confirmation"] = {"reference": "BAK-20261113-7KQ2MX", "confirmed_at": "2026-11-13T16:40:00+04:00"}
    assert codes(pricing.add_activity, state, WALK_25, CATALOG) == "plan_confirmed"
    assert codes(pricing.set_hotel, state, "htl-boulevard-bay", CATALOG) == "plan_confirmed"
    assert codes(pricing.set_trip, state, CATALOG, travelers=3, today=TODAY) == "plan_confirmed"


def test_invalid_state():
    assert codes(pricing.parse_state, "{not json") == "invalid_state"
    assert codes(pricing.parse_state, json.dumps({"schema_version": "9"})) == "invalid_state"


# --- schema & rendering ------------------------------------------------------------------------

def test_state_matches_schema():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    jsonschema.validate(state, SCHEMA)
    jsonschema.validate(new_plan(), SCHEMA)


def test_plan_block_markdown():
    state = pricing.add_activity(pricing.set_hotel(new_plan(), HOTEL_60, CATALOG), WALK_25, CATALOG)
    md = pricing.render_plan(state)
    assert "**Your Baku trip plan** (draft)" in md
    assert "10 Mar 2027 → 14 Mar 2027 · 4 nights · 2 travelers" in md
    assert "| 🏨 Caspian Courtyard Hotel | AZN 60.00 | 2 travelers × 4 nights | AZN 480.00 |" in md
    assert "| 🎟️ Old City walking tour | AZN 25.00 | 2 travelers | AZN 50.00 |" in md
    assert "| **Grand total** | | | **AZN 530.00** |" in md
    assert "This is a plan, not a booking." in md


def test_singular_labels():
    state = pricing.set_hotel(new_plan("2027-03-10", "2027-03-11", 1), HOTEL_60, CATALOG)
    assert state["lines"][0]["quantity_label"] == "1 traveler × 1 night"
    assert "· 1 night · 1 traveler" in pricing.render_plan(state)


def test_envelopes():
    ok = pricing.ok_envelope({"x": 1}, "hi", options=[1])
    assert ok == {"ok": True, "state": {"x": 1}, "markdown": "hi", "errors": [], "options": [1]}
    err = pricing.error_envelope(None, pricing.PlanError("hotel_required"))
    assert err["ok"] is False and err["errors"][0]["code"] == "hotel_required"
    assert err["markdown"] == err["errors"][0]["message"]
