"""Baku trip plan commands for the baku-trip-catalog skill.

Usage (one JSON object is printed to stdout; exit code 0 even for validation errors):

  python trip_plan.py start --check-in YYYY-MM-DD --check-out YYYY-MM-DD --travelers N
  python trip_plan.py set-trip --state JSON [--check-in D] [--check-out D] [--travelers N]
  python trip_plan.py list-hotels --state JSON [--photo-style inline|link]
  python trip_plan.py select-hotel --state JSON --hotel-id ID
  python trip_plan.py list-activities --state JSON [--photo-style inline|link]
  python trip_plan.py add-activity --state JSON --activity-id ID
  python trip_plan.py remove-activity --state JSON --activity-id ID
  python trip_plan.py show-plan --state JSON

Output: {"ok": bool, "state": {...}, "markdown": "...", "errors": [...], "options": [...]}
Show `markdown` to the traveler as normal Markdown. Pass `state` unchanged to the next call.
Contract: specs/001-baku-trip-planner/contracts/scripts-cli.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pricing  # noqa: E402  (synced copy in this folder)

NEXT_AFTER_HOTEL = "Would you like to see some activities in Baku?"
NEXT_AFTER_ACTIVITY = "Would you like to add more activities, or continue to confirmation?"
HOTEL_PROMPT = "Reply with the number or name of the hotel you'd like."
ACTIVITY_PROMPT = 'Reply with the number or name of an activity to add it, or say "continue".'


def photo_md(item: dict, style: str) -> str:
    photo = item["photos"][0]
    if style == "link":
        return f"[View photo]({photo['url']})"
    return f"![{photo['alt']}]({photo['url']})"


def hotel_option(n: int, h: dict, style: str) -> str:
    price = pricing.fmt_azn(pricing.dec(h["price_per_person_per_night"]))
    return "\n\n".join([
        f"### {n}. {h['name']}",
        photo_md(h, style),
        f"*{h['neighborhood']}* · **{price} per person per night**",
        h["description"],
    ])


def activity_option(n: int, a: dict, style: str) -> str:
    price = pricing.fmt_azn(pricing.dec(a["price_per_person"]))
    return "\n\n".join([
        f"### {n}. {a['name']}",
        photo_md(a, style),
        f"**{price} per person** · {a['duration']}",
        a["description"],
    ])


def trip_line(state: dict) -> str:
    t = state["trip"]
    return (
        f"**Trip details**: {pricing.fmt_date(t['check_in'])} → {pricing.fmt_date(t['check_out'])} · "
        f"{pricing.plural(t['nights'], 'night')} · {pricing.plural(t['travelers'], 'traveler')}"
    )


def cmd_start(args, catalog):
    trip = pricing.validate_trip(args.check_in, args.check_out, args.travelers)
    state = pricing.new_state(trip, catalog)
    return pricing.ok_envelope(state, trip_line(state))


def cmd_set_trip(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    state = pricing.set_trip(state, catalog, args.check_in, args.check_out, args.travelers)
    return pricing.ok_envelope(state, pricing.render_plan(state))


def cmd_list_hotels(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    pricing.ensure_editable(state)
    hotels = catalog["hotels"][:5]
    blocks = [hotel_option(i, h, args.photo_style) for i, h in enumerate(hotels, 1)]
    options = [{"n": i, "id": h["id"], "name": h["name"]} for i, h in enumerate(hotels, 1)]
    return pricing.ok_envelope(state, "\n\n".join(blocks + [HOTEL_PROMPT]), options=options)


def cmd_select_hotel(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    state = pricing.set_hotel(state, args.hotel_id, catalog)
    return pricing.ok_envelope(state, pricing.render_plan(state) + "\n\n" + NEXT_AFTER_HOTEL)


def cmd_list_activities(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    pricing.ensure_editable(state)
    if not state["hotel_id"]:
        raise pricing.PlanError("hotel_required")
    taken = set(state["activity_ids"])
    acts = [a for a in catalog["activities"] if a["id"] not in taken][:6]
    if not acts:
        md = "You've added every activity in our catalog.\n\n" + NEXT_AFTER_ACTIVITY
        return pricing.ok_envelope(state, md, options=[])
    blocks = [activity_option(i, a, args.photo_style) for i, a in enumerate(acts, 1)]
    options = [{"n": i, "id": a["id"], "name": a["name"]} for i, a in enumerate(acts, 1)]
    return pricing.ok_envelope(state, "\n\n".join(blocks + [ACTIVITY_PROMPT]), options=options)


def cmd_add_activity(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    state = pricing.add_activity(state, args.activity_id, catalog)
    return pricing.ok_envelope(state, pricing.render_plan(state) + "\n\n" + NEXT_AFTER_ACTIVITY)


def cmd_remove_activity(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    state = pricing.remove_activity(state, args.activity_id, catalog)
    return pricing.ok_envelope(state, pricing.render_plan(state) + "\n\n" + NEXT_AFTER_ACTIVITY)


def cmd_show_plan(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    return pricing.ok_envelope(state, pricing.render_plan(state))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trip_plan.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("start")
    s.add_argument("--check-in", required=True)
    s.add_argument("--check-out", required=True)
    s.add_argument("--travelers", required=True)
    s.set_defaults(func=cmd_start)

    s = sub.add_parser("set-trip")
    s.add_argument("--state", required=True)
    s.add_argument("--check-in")
    s.add_argument("--check-out")
    s.add_argument("--travelers")
    s.set_defaults(func=cmd_set_trip)

    for name, func in (("list-hotels", cmd_list_hotels), ("list-activities", cmd_list_activities)):
        s = sub.add_parser(name)
        s.add_argument("--state", required=True)
        s.add_argument("--photo-style", choices=("inline", "link"), default="inline")
        s.set_defaults(func=func)

    s = sub.add_parser("select-hotel")
    s.add_argument("--state", required=True)
    s.add_argument("--hotel-id", required=True)
    s.set_defaults(func=cmd_select_hotel)

    for name, func in (("add-activity", cmd_add_activity), ("remove-activity", cmd_remove_activity)):
        s = sub.add_parser(name)
        s.add_argument("--state", required=True)
        s.add_argument("--activity-id", required=True)
        s.set_defaults(func=func)

    s = sub.add_parser("show-plan")
    s.add_argument("--state", required=True)
    s.set_defaults(func=cmd_show_plan)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)  # bad command/arguments -> exit 2
    catalog = pricing.load_catalog(pricing.default_catalog_path(__file__))
    incoming = None
    if getattr(args, "state", None):
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
