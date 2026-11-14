"""Holder details and plan confirmation for the confirm-trip-plan skill.

Usage (one JSON object is printed to stdout; exit code 0 even for validation errors):

  python confirm.py validate-holder --state JSON --full-name NAME --email EMAIL --phone PHONE
  python confirm.py confirm --state JSON

Only these three holder fields exist. Passport/ID numbers, card or bank details and passwords
cannot be passed in (Constitution III). `confirm` must only be called after the traveler has
explicitly agreed to the summary. Confirming creates a plan with a reference: it does not book,
reserve or charge anything.
Contract: specs/001-baku-trip-planner/contracts/scripts-cli.md
"""
from __future__ import annotations

import argparse
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pricing  # noqa: E402  (synced copy in this folder)

REF_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9 ()\-]+$")
CONFIRM_QUESTION = (
    "Shall I confirm this plan? Confirming creates a trip plan with a reference. It doesn't book "
    "hotels or activities and no payment is taken."
)
PDF_OFFER = "Would you like me to export this plan as a PDF?"

pricing.MESSAGES.update({
    "invalid_name": "Please give the holder's full name (2 to 100 characters, letters only).",
    "invalid_email": "That email address doesn't look right. Could you check it?",
    "invalid_phone": "Please give a phone number with 7 to 15 digits, for example +994 12 345 67 89.",
    "holder_required": "I need the plan holder's full name, email and phone before I can confirm.",
    "already_confirmed": "This plan is already confirmed and can't be changed. Would you like to start a new plan?",
})


def check_name(name: str) -> str | None:
    name = " ".join(str(name).split())
    ok = 2 <= len(name) <= 100 and any(c.isalpha() for c in name) and all(
        c.isalpha() or c in " -'." for c in name
    )
    return name if ok else None


def check_email(email: str) -> str | None:
    email = str(email).strip()
    return email if len(email) <= 254 and EMAIL_RE.match(email) else None


def check_phone(phone: str) -> str | None:
    phone = " ".join(str(phone).split())
    if not PHONE_RE.match(phone) or phone.count("+") > 1:
        return None
    digits = sum(c.isdigit() for c in phone)
    return phone if 7 <= digits <= 15 else None


def validate_holder_fields(full_name, email, phone) -> tuple[dict | None, list[pricing.PlanError]]:
    errors = []
    name_v, email_v, phone_v = check_name(full_name), check_email(email), check_phone(phone)
    if name_v is None:
        errors.append(pricing.PlanError("invalid_name"))
    if email_v is None:
        errors.append(pricing.PlanError("invalid_email"))
    if phone_v is None:
        errors.append(pricing.PlanError("invalid_phone"))
    if errors:
        return None, errors
    return {"full_name": name_v, "email": email_v, "phone": phone_v}, []


def holder_line(holder: dict) -> str:
    return f"**Plan holder**: {holder['full_name']} · {holder['email']} · {holder['phone']}"


def require_confirmable(state: dict) -> None:
    if state.get("status") == "confirmed":
        raise pricing.PlanError("already_confirmed")
    if not state.get("hotel_id"):
        raise pricing.PlanError("hotel_required")


def multi_error(state, errors: list[pricing.PlanError]) -> dict:
    return {
        "ok": False,
        "state": state,
        "markdown": "\n\n".join(e.message for e in errors),
        "errors": [{"code": e.code, "message": e.message} for e in errors],
    }


def cmd_validate_holder(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    require_confirmable(state)
    holder, errors = validate_holder_fields(args.full_name, args.email, args.phone)
    if errors:
        return multi_error(state, errors)
    state["holder"] = holder
    md = "\n\n".join([
        pricing.render_plan(state, status_label="ready to confirm"),
        holder_line(holder),
        CONFIRM_QUESTION,
    ])
    return pricing.ok_envelope(state, md)


def new_reference(now: datetime) -> str:
    day = now.astimezone(pricing.BAKU_TZ).strftime("%Y%m%d")
    return f"BAK-{day}-" + "".join(secrets.choice(REF_ALPHABET) for _ in range(6))


def cmd_confirm(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    require_confirmable(state)
    h = state.get("holder")
    if not isinstance(h, dict):
        raise pricing.PlanError("holder_required")
    holder, errors = validate_holder_fields(h.get("full_name", ""), h.get("email", ""), h.get("phone", ""))
    if errors:
        return multi_error(state, errors)
    now = datetime.now(timezone.utc)
    state["holder"] = holder
    state["status"] = "confirmed"
    state["confirmation"] = {"reference": new_reference(now), "confirmed_at": pricing.now_baku_iso(now)}
    local = now.astimezone(pricing.BAKU_TZ)
    when = f"{local.day} {local.strftime('%b %Y, %H:%M')} (Baku time)"
    md = "\n\n".join([
        pricing.render_plan(state, status_label="confirmed"),
        f"**Confirmation reference**: {state['confirmation']['reference']} · confirmed {when}",
        holder_line(holder),
        PDF_OFFER,
    ])
    return pricing.ok_envelope(state, md)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="confirm.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("validate-holder")
    s.add_argument("--state", required=True)
    s.add_argument("--full-name", required=True)
    s.add_argument("--email", required=True)
    s.add_argument("--phone", required=True)
    s.set_defaults(func=cmd_validate_holder)
    s = sub.add_parser("confirm")
    s.add_argument("--state", required=True)
    s.set_defaults(func=cmd_confirm)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)  # unknown arguments -> exit 2
    catalog = pricing.load_catalog(pricing.default_catalog_path(__file__))
    try:
        incoming = pricing.parse_state(args.state)
    except pricing.PlanError:
        incoming = None
    try:
        envelope = args.func(args, catalog)
    except pricing.PlanError as err:
        envelope = pricing.error_envelope(incoming, err)
    pricing.emit(envelope)
    return 0


if __name__ == "__main__":
    sys.exit(main())
