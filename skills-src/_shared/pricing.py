"""Shared pricing, validation and plan rendering for the Baku Trip Planner skills.

Single source: skills-src/_shared/pricing.py. tools/sync_shared.py copies it into each skill's
scripts/ folder. Stdlib only, Python >= 3.10.

Authority rule (data-model.md): only trip, hotel_id, activity_ids, status, holder and
confirmation are read from an incoming plan state. Names, prices, lines and totals are always
recomputed from the catalog, so an edited or stale value can never change a total.
"""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

SCHEMA_VERSION = "1"
CURRENCY = "AZN"
BAKU_TZ = timezone(timedelta(hours=4), "Asia/Baku")  # Azerbaijan: UTC+4, no DST
MAX_NIGHTS = 30
MIN_TRAVELERS, MAX_TRAVELERS = 1, 10
CENT = Decimal("0.01")

MESSAGES = {
    "invalid_date": "I couldn't read that date. Please give it like 10 March 2027.",
    "check_out_before_check_in": "Check-out must be after check-in. What's your check-out date?",
    "check_in_in_past": "Check-in can't be in the past. What date do you arrive in Baku?",
    "stay_too_long": f"I can plan stays of up to {MAX_NIGHTS} nights. Could you choose shorter dates?",
    "travelers_out_of_range": (
        f"I can plan for {MIN_TRAVELERS} to {MAX_TRAVELERS} travelers. How many people are traveling?"
    ),
    "unknown_item": "That option isn't in our catalog. Please choose one of the options shown.",
    "hotel_required": "Please choose a hotel first. Then I can show you activities.",
    "duplicate_activity": "That activity is already in your plan.",
    "plan_confirmed": (
        "This plan is already confirmed and can't be changed. Would you like to start a new plan?"
    ),
    "invalid_state": "Something went wrong with the plan details. Let's start the plan again.",
}


class PlanError(Exception):
    """A validation problem the traveler can fix. `code` is stable; `message` is user-facing."""

    def __init__(self, code: str, message: str | None = None):
        self.code = code
        self.message = message or MESSAGES.get(code, "Something went wrong.")
        super().__init__(f"{code}: {self.message}")


# --- catalog --------------------------------------------------------------------------------

def default_catalog_path(script_file: str | Path) -> Path:
    """Catalog bundled with a skill: <skill>/references/catalog.json next to <skill>/scripts/."""
    return Path(script_file).resolve().parent.parent / "references" / "catalog.json"


def load_catalog(path: str | Path) -> dict:
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    catalog["_hotels"] = {h["id"]: h for h in catalog["hotels"]}
    catalog["_activities"] = {a["id"]: a for a in catalog["activities"]}
    return catalog


# --- money ----------------------------------------------------------------------------------

def dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise PlanError("invalid_state") from exc


def q2(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def money_str(value: Decimal) -> str:
    return f"{q2(value):.2f}"


def fmt_azn(value: Decimal) -> str:
    return f"{CURRENCY} {q2(value):,.2f}"


# --- dates ----------------------------------------------------------------------------------

def today_baku(now: datetime | None = None) -> date:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(BAKU_TZ).date()


def now_baku_iso(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(BAKU_TZ).replace(microsecond=0).isoformat()


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise PlanError("invalid_date") from exc


def fmt_date(value: str) -> str:
    d = date.fromisoformat(value)
    return f"{d.day} {d.strftime('%b')} {d.year}"


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


# --- trip -----------------------------------------------------------------------------------

def validate_trip(check_in, check_out, travelers, today: date | None = None, check_past: bool = True) -> dict:
    ci, co = parse_date(check_in), parse_date(check_out)
    try:
        n_travelers = int(travelers)
    except (TypeError, ValueError) as exc:
        raise PlanError("travelers_out_of_range") from exc
    if str(travelers).strip() != str(n_travelers):
        raise PlanError("travelers_out_of_range")
    if co <= ci:
        raise PlanError("check_out_before_check_in")
    if check_past and ci < (today or today_baku()):
        raise PlanError("check_in_in_past")
    nights = (co - ci).days
    if nights > MAX_NIGHTS:
        raise PlanError("stay_too_long")
    if not MIN_TRAVELERS <= n_travelers <= MAX_TRAVELERS:
        raise PlanError("travelers_out_of_range")
    return {"check_in": ci.isoformat(), "check_out": co.isoformat(), "travelers": n_travelers, "nights": nights}


# --- state ------------------------------------------------------------------------------------

def new_state(trip: dict, catalog: dict) -> dict:
    state = {
        "schema_version": SCHEMA_VERSION,
        "catalog_version": catalog.get("catalog_version", ""),
        "currency": CURRENCY,
        "trip": trip,
        "hotel_id": None,
        "activity_ids": [],
        "status": "draft",
        "holder": None,
        "confirmation": None,
    }
    return recompute(state, catalog)


def parse_state(raw) -> dict:
    """Parse the --state argument (JSON string or dict) and check its basic shape."""
    try:
        state = json.loads(raw) if isinstance(raw, str) else deepcopy(raw)
    except json.JSONDecodeError as exc:
        raise PlanError("invalid_state") from exc
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise PlanError("invalid_state")
    if not isinstance(state.get("trip"), dict) or not isinstance(state.get("activity_ids", []), list):
        raise PlanError("invalid_state")
    if state.get("status", "draft") not in ("draft", "confirmed"):
        raise PlanError("invalid_state")
    return state


def recompute(state: dict, catalog: dict) -> dict:
    """Rebuild a clean plan state from its authoritative inputs and the catalog."""
    trip_in = state.get("trip") or {}
    try:
        trip = validate_trip(trip_in["check_in"], trip_in["check_out"], trip_in["travelers"], check_past=False)
    except KeyError as exc:
        raise PlanError("invalid_state") from exc

    hotel_id = state.get("hotel_id")
    activity_ids = list(state.get("activity_ids") or [])
    if hotel_id is not None and hotel_id not in catalog["_hotels"]:
        raise PlanError("unknown_item")
    if activity_ids and hotel_id is None:
        raise PlanError("hotel_required")
    if len(set(activity_ids)) != len(activity_ids):
        raise PlanError("duplicate_activity")
    for aid in activity_ids:
        if aid not in catalog["_activities"]:
            raise PlanError("unknown_item")

    t, n = trip["travelers"], trip["nights"]
    lines = []
    if hotel_id:
        h = catalog["_hotels"][hotel_id]
        unit = dec(h["price_per_person_per_night"])
        lines.append({
            "kind": "hotel", "item_id": hotel_id, "name": h["name"],
            "unit_price": money_str(unit), "quantity": t * n,
            "quantity_label": f"{plural(t, 'traveler')} × {plural(n, 'night')}",
            "line_total": money_str(unit * t * n),
        })
    for aid in activity_ids:
        a = catalog["_activities"][aid]
        unit = dec(a["price_per_person"])
        lines.append({
            "kind": "activity", "item_id": aid, "name": a["name"],
            "unit_price": money_str(unit), "quantity": t,
            "quantity_label": plural(t, "traveler"),
            "line_total": money_str(unit * t),
        })
    grand = sum((dec(l["line_total"]) for l in lines), Decimal("0"))

    status = state.get("status", "draft")
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_version": catalog.get("catalog_version", ""),
        "currency": CURRENCY,
        "trip": trip,
        "hotel_id": hotel_id,
        "activity_ids": activity_ids,
        "lines": lines,
        "grand_total": money_str(grand),
        "status": status,
        "holder": deepcopy(state.get("holder")),
        "confirmation": deepcopy(state.get("confirmation")),
    }


def ensure_editable(state: dict) -> None:
    if state.get("status") == "confirmed":
        raise PlanError("plan_confirmed")


def set_trip(state: dict, catalog: dict, check_in=None, check_out=None, travelers=None, today=None) -> dict:
    ensure_editable(state)
    cur = state["trip"]
    trip = validate_trip(
        check_in if check_in is not None else cur["check_in"],
        check_out if check_out is not None else cur["check_out"],
        travelers if travelers is not None else cur["travelers"],
        today=today,
    )
    return recompute({**state, "trip": trip}, catalog)


def set_hotel(state: dict, hotel_id: str, catalog: dict) -> dict:
    ensure_editable(state)
    if hotel_id not in catalog["_hotels"]:
        raise PlanError("unknown_item", "That hotel isn't in our catalog. Please choose one of the hotels shown.")
    return recompute({**state, "hotel_id": hotel_id}, catalog)


def add_activity(state: dict, activity_id: str, catalog: dict) -> dict:
    ensure_editable(state)
    if not state.get("hotel_id"):
        raise PlanError("hotel_required")
    if activity_id not in catalog["_activities"]:
        raise PlanError("unknown_item", "That activity isn't in our catalog. Please choose one of the activities shown.")
    if activity_id in (state.get("activity_ids") or []):
        name = catalog["_activities"][activity_id]["name"]
        raise PlanError("duplicate_activity", f"{name} is already in your plan.")
    return recompute({**state, "activity_ids": [*state.get("activity_ids", []), activity_id]}, catalog)


def remove_activity(state: dict, activity_id: str, catalog: dict) -> dict:
    ensure_editable(state)
    ids = list(state.get("activity_ids") or [])
    if activity_id not in ids:
        raise PlanError("unknown_item", "That activity isn't in your plan.")
    ids.remove(activity_id)
    return recompute({**state, "activity_ids": ids}, catalog)


# --- rendering --------------------------------------------------------------------------------

def render_plan(state: dict, status_label: str | None = None) -> str:
    """Plan block exactly as contracts/rendering.md."""
    trip = state["trip"]
    label = status_label or state.get("status", "draft")
    # Blank lines between blocks: chat renderers join single newlines into one paragraph.
    head = [
        f"**Your Baku trip plan** ({label})",
        "",
        f"{fmt_date(trip['check_in'])} → {fmt_date(trip['check_out'])} · "
        f"{plural(trip['nights'], 'night')} · {plural(trip['travelers'], 'traveler')}",
        "",
    ]
    if not state["lines"]:
        return "\n".join(head + ["_No hotel or activities yet._"])
    rows = ["| Item | Price | Qty | Total |", "|---|---:|---|---:|"]
    for line in state["lines"]:
        icon = "🏨" if line["kind"] == "hotel" else "🎟️"
        rows.append(
            f"| {icon} {line['name']} | {fmt_azn(dec(line['unit_price']))} | "
            f"{line['quantity_label']} | {fmt_azn(dec(line['line_total']))} |"
        )
    rows.append(f"| **Grand total** | | | **{fmt_azn(dec(state['grand_total']))}** |")
    foot = ["", "_Sample prices from the agent's catalog. This is a plan, not a booking._"]
    return "\n".join(head + rows + foot)


# --- output envelopes ---------------------------------------------------------------------------

def ok_envelope(state, markdown: str, **extra) -> dict:
    return {"ok": True, "state": state, "markdown": markdown, "errors": [], **extra}


def error_envelope(state, err: PlanError, **extra) -> dict:
    return {
        "ok": False,
        "state": state,
        "markdown": err.message,
        "errors": [{"code": err.code, "message": err.message}],
        **extra,
    }


def emit(envelope: dict) -> None:
    print(json.dumps(envelope, ensure_ascii=False))
