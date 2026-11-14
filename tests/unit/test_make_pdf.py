"""T038: tests for skills-src/export-trip-plan-pdf/scripts/make_pdf.py."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "skills-src" / "export-trip-plan-pdf" / "scripts"
TRIP_DIR = ROOT / "skills-src" / "baku-trip-catalog" / "scripts"
CONFIRM_DIR = ROOT / "skills-src" / "confirm-trip-plan" / "scripts"


def run(folder, script, *args):
    proc = subprocess.run([sys.executable, script, *map(str, args)], cwd=folder, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def st(s):
    return json.dumps(s)


def draft_state(activities=("act-old-city-walking-tour", "act-gobustan-mud-volcanoes")):
    s = run(TRIP_DIR, "trip_plan.py", "start", "--check-in", "2027-03-10", "--check-out", "2027-03-14", "--travelers", 2)["state"]
    s = run(TRIP_DIR, "trip_plan.py", "select-hotel", "--state", st(s), "--hotel-id", "htl-caspian-courtyard")["state"]
    for a in activities:
        s = run(TRIP_DIR, "trip_plan.py", "add-activity", "--state", st(s), "--activity-id", a)["state"]
    return s


def confirmed_state(activities=("act-old-city-walking-tour", "act-gobustan-mud-volcanoes")):
    s = draft_state(activities)
    s = run(CONFIRM_DIR, "confirm.py", "validate-holder", "--state", st(s), "--full-name", "Aynur Məmmədova",
            "--email", "aynur@example.az", "--phone", "+994 50 123 45 67")["state"]
    return run(CONFIRM_DIR, "confirm.py", "confirm", "--state", st(s))["state"]


def pdf_text(path):
    return "\n".join(page.extract_text() for page in PdfReader(path).pages)


def norm(text):
    return " ".join(text.split())


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("pdf")
    state = confirmed_state()
    result = run(PDF_DIR, "make_pdf.py", "build", "--state", st(state), "--out", out_dir)
    return state, result


def test_build_writes_named_file(built):
    state, result = built
    ref = state["confirmation"]["reference"]
    assert result["ok"], result
    assert result["errors"] == []
    path = Path(result["file"])
    assert path.name == f"Baku-Trip-{ref}.pdf" and path.is_file()
    assert path.stat().st_size > 50_000  # photos are embedded
    assert f"Baku-Trip-{ref}.pdf" in result["markdown"]


def test_pdf_contains_all_sections_in_order(built):
    state, result = built
    text = norm(pdf_text(result["file"]))
    ref = state["confirmation"]["reference"]
    markers = [
        "Baku Trip Plan", ref,
        "Plan holder", "Aynur Məmmədova", "aynur@example.az", "+994 50 123 45 67",
        "Trip", "10 Mar 2027", "14 Mar 2027", "4 nights", "2 travelers",
        "Hotel", "Caspian Courtyard Hotel", "Old City (İçərişəhər)", "AZN 60.00 per person per night",
        "2 travelers × 4 nights", "AZN 480.00",
        "Activities", "Old City walking tour", "AZN 25.00 per person", "AZN 50.00",
        "Gobustan & mud volcanoes day trip", "AZN 95.00 per person", "AZN 190.00",
        "Totals", "Grand total", "AZN 720.00",
        "catalog (version 2026-11-13)", "This is a trip plan, not a booking",
        "Photo credits", "Wikimedia Commons",
    ]
    pos = -1
    for m in markers:
        nxt = text.find(norm(m), pos + 1)
        assert nxt > pos, f"{m!r} missing or out of order"
        pos = nxt


def test_no_other_personal_data(built):
    _, result = built
    text = pdf_text(result["file"]).lower()
    for word in ("passport", "card number", "iban", "password", "date of birth"):
        assert word not in text


def test_no_activities():
    state = confirmed_state(activities=())
    with_tmp = Path(subprocess.check_output(["mktemp", "-d"], text=True).strip())
    result = run(PDF_DIR, "make_pdf.py", "build", "--state", st(state), "--out", with_tmp)
    assert result["ok"]
    assert "No activities selected" in pdf_text(result["file"])


def test_draft_is_refused(tmp_path):
    result = run(PDF_DIR, "make_pdf.py", "build", "--state", st(draft_state()), "--out", tmp_path)
    assert result["ok"] is False and result["errors"][0]["code"] == "not_confirmed"
    assert not list(tmp_path.glob("*.pdf"))


def test_tampered_totals_are_recomputed(tmp_path):
    state = confirmed_state()
    state["grand_total"] = "1.00"
    state["lines"][0]["line_total"] = "1.00"
    result = run(PDF_DIR, "make_pdf.py", "build", "--state", st(state), "--out", tmp_path)
    text = norm(pdf_text(result["file"]))
    assert "AZN 720.00" in text and "AZN 1.00" not in text


def test_missing_photo_is_non_fatal(tmp_path):
    empty = tmp_path / "nophotos"
    empty.mkdir()
    result = run(PDF_DIR, "make_pdf.py", "build", "--state", st(confirmed_state()), "--out", tmp_path, "--photos-dir", empty)
    assert result["ok"] is True
    assert {e["code"] for e in result["errors"]} == {"photo_missing"}
    assert Path(result["file"]).is_file()


def test_output_dir_falls_back_when_not_writable(tmp_path):
    spec = importlib.util.spec_from_file_location("make_pdf", PDF_DIR / "make_pdf.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        chosen = mod.pick_out_dir(None, candidates=[locked, tmp_path / "ok"])
        assert chosen == tmp_path / "ok"
    finally:
        locked.chmod(0o700)
