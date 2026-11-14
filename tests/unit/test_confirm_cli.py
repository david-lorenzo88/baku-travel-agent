"""T033: CLI tests for skills-src/confirm-trip-plan/scripts/confirm.py (run as a separate process)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
CONFIRM_DIR = ROOT / "skills-src" / "confirm-trip-plan" / "scripts"
TRIP_DIR = ROOT / "skills-src" / "baku-trip-catalog" / "scripts"
SCHEMA = json.loads((ROOT / "specs/001-baku-trip-planner/contracts/plan-state.schema.json").read_text())
HOLDER = ("--full-name", "Ana Smith", "--email", "ana@example.com", "--phone", "+34 600 000 000")


def run(folder, script, *args):
    proc = subprocess.run([sys.executable, script, *map(str, args)], cwd=folder, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def trip(*args):
    return run(TRIP_DIR, "trip_plan.py", *args)


def confirm(*args):
    return run(CONFIRM_DIR, "confirm.py", *args)


def st(state):
    return json.dumps(state)


@pytest.fixture
def draft():
    s = trip("start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", 2)["state"]
    s = trip("select-hotel", "--state", st(s), "--hotel-id", "htl-caspian-courtyard")["state"]
    return trip("add-activity", "--state", st(s), "--activity-id", "act-old-city-walking-tour")["state"]


@pytest.fixture
def with_holder(draft):
    return confirm("validate-holder", "--state", st(draft), *HOLDER)["state"]


# --- validate-holder ------------------------------------------------------------------------

def test_valid_holder_and_summary(draft):
    out = confirm("validate-holder", "--state", st(draft), *HOLDER)
    assert out["ok"], out
    assert out["state"]["holder"] == {"full_name": "Ana Smith", "email": "ana@example.com", "phone": "+34 600 000 000"}
    assert out["state"]["status"] == "draft"
    md = out["markdown"]
    assert "**Your Baku trip plan** (ready to confirm)" in md
    assert "| 🏨 Caspian Courtyard Hotel | AZN 60.00 | 2 travelers × 4 nights | AZN 480.00 |" in md
    assert "| 🎟️ Old City walking tour | AZN 25.00 | 2 travelers | AZN 50.00 |" in md
    assert "**AZN 530.00**" in md
    assert "**Plan holder**: Ana Smith · ana@example.com · +34 600 000 000" in md
    assert md.rstrip().endswith(
        "Shall I confirm this plan? Confirming creates a trip plan with a reference. It doesn't book "
        "hotels or activities and no payment is taken."
    )
    jsonschema.validate(out["state"], SCHEMA)


@pytest.mark.parametrize("name", ["José Pérez-López", "Aynur Məmmədova", "O'Brien J.", "李雷", "Al"])
def test_names_accepted(draft, name):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", name, "--email", "a@b.az", "--phone", "+994 12 345 67 89")
    assert out["ok"], (name, out)


@pytest.mark.parametrize("name", ["A", "Ana2", "x" * 101, "  ", "Ana_Smith", "<script>"])
def test_names_rejected(draft, name):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", name, "--email", "a@b.az", "--phone", "+994123456789")
    assert not out["ok"] and [e["code"] for e in out["errors"]] == ["invalid_name"]


@pytest.mark.parametrize("email", ["ana@example", "ana.example.com", "ana@@example.com", "a b@example.com", "a@" + "b" * 250 + ".az"])
def test_emails_rejected(draft, email):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", "Ana Smith", "--email", email, "--phone", "+994123456789")
    assert not out["ok"] and [e["code"] for e in out["errors"]] == ["invalid_email"]


@pytest.mark.parametrize("phone", ["123456", "+1234567890123456", "phone 12345678", "++34600000000", "34-600"])
def test_phones_rejected(draft, phone):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", "Ana Smith", "--email", "a@b.az", "--phone", phone)
    assert not out["ok"] and [e["code"] for e in out["errors"]] == ["invalid_phone"]


@pytest.mark.parametrize("phone", ["+34 600 000 000", "(012) 345-6789", "0123456", "+994501234567"])
def test_phones_accepted(draft, phone):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", "Ana Smith", "--email", "a@b.az", "--phone", phone)
    assert out["ok"], (phone, out)


def test_several_field_errors_reported_together(draft):
    out = confirm("validate-holder", "--state", st(draft), "--full-name", "A", "--email", "nope", "--phone", "1")
    assert {e["code"] for e in out["errors"]} == {"invalid_name", "invalid_email", "invalid_phone"}
    assert out["state"]["holder"] is None


def test_no_other_holder_fields(draft):
    proc = subprocess.run(
        [sys.executable, "confirm.py", "validate-holder", "--state", st(draft), *HOLDER, "--passport", "X1234567"],
        cwd=CONFIRM_DIR, capture_output=True, text=True,
    )
    assert proc.returncode == 2  # unknown argument: there is no way to pass other personal data


def test_holder_requires_hotel():
    s = trip("start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", 2)["state"]
    out = confirm("validate-holder", "--state", st(s), *HOLDER)
    assert out["errors"][0]["code"] == "hotel_required"


# --- confirm ----------------------------------------------------------------------------------

def test_confirm_sets_reference(with_holder):
    out = confirm("confirm", "--state", st(with_holder))
    assert out["ok"], out
    s = out["state"]
    assert s["status"] == "confirmed"
    assert re.fullmatch(r"BAK-[0-9]{8}-[A-HJ-NP-Z2-9]{6}", s["confirmation"]["reference"])
    assert s["confirmation"]["confirmed_at"].endswith("+04:00")
    md = out["markdown"]
    assert "**Your Baku trip plan** (confirmed)" in md
    assert f"**Confirmation reference**: {s['confirmation']['reference']} · confirmed " in md
    assert "(Baku time)" in md
    assert "**Plan holder**: Ana Smith · ana@example.com · +34 600 000 000" in md
    assert md.rstrip().endswith("Would you like me to export this plan as a PDF?")
    jsonschema.validate(s, SCHEMA)


def test_confirm_without_holder(draft):
    out = confirm("confirm", "--state", st(draft))
    assert out["errors"][0]["code"] == "holder_required"


def test_confirm_without_hotel():
    s = trip("start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", 2)["state"]
    s["holder"] = {"full_name": "Ana Smith", "email": "ana@example.com", "phone": "+34 600 000 000"}
    out = confirm("confirm", "--state", st(s))
    assert out["errors"][0]["code"] == "hotel_required"


def test_confirm_twice(with_holder):
    s = confirm("confirm", "--state", st(with_holder))["state"]
    out = confirm("confirm", "--state", st(s))
    assert out["errors"][0]["code"] == "already_confirmed"
    out = confirm("validate-holder", "--state", st(s), *HOLDER)
    assert out["errors"][0]["code"] == "already_confirmed"


def test_confirm_revalidates_tampered_holder(with_holder):
    with_holder["holder"]["email"] = "not-an-email"
    out = confirm("confirm", "--state", st(with_holder))
    assert not out["ok"] and out["errors"][0]["code"] == "invalid_email"


def test_trip_plan_refuses_confirmed_state(with_holder):
    s = confirm("confirm", "--state", st(with_holder))["state"]
    for args in (("select-hotel", "--hotel-id", "htl-boulevard-bay"),
                 ("add-activity", "--activity-id", "act-cooking-class"),
                 ("set-trip", "--travelers", "3"),
                 ("list-hotels",)):
        out = trip(args[0], "--state", st(s), *args[1:])
        assert out["errors"][0]["code"] == "plan_confirmed", args


def test_references_are_unique(with_holder):
    refs = {confirm("confirm", "--state", st(with_holder))["state"]["confirmation"]["reference"] for _ in range(5)}
    assert len(refs) == 5
