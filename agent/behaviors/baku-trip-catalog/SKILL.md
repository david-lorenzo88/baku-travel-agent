---
name: baku-trip-catalog
description: "Plans a Baku trip: collects check-in, check-out and number of travelers; lists hotels and activities from the catalog with photos and AZN prices; adds, replaces or removes them; and recalculates and shows the trip plan and grand total. Use for any trip-detail, hotel, activity or plan-total request before confirmation."
---

# Baku trip catalog and plan

## When to use

Use this skill for everything before confirmation: trip dates and party size, showing hotels,
choosing or changing the hotel, showing activities, adding or removing activities, changing
dates or travelers, and showing the current plan with its grand total.
For holder details and confirmation use `confirm-trip-plan`; for the PDF use `export-trip-plan-pdf`.

## How to run the script

The script is `scripts/trip_plan.py` in this skill's folder. It prints exactly one JSON object:
`{"ok": ..., "state": {...}, "markdown": "...", "errors": [...], "options": [...]}`.

Always run it from Python with an argument list (no shell quoting), for example:

```python
import json, subprocess, sys
SKILL_DIR = "<folder that contains this SKILL.md>"
def trip_plan(*args):
    out = subprocess.run([sys.executable, f"{SKILL_DIR}/scripts/trip_plan.py", *args],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)

r = trip_plan("select-hotel", "--state", json.dumps(state), "--hotel-id", "htl-caspian-courtyard")
```

Commands:

| Command | Arguments |
|---|---|
| `start` | `--check-in YYYY-MM-DD --check-out YYYY-MM-DD --travelers N` |
| `set-trip` | `--state JSON` plus any of `--check-in`, `--check-out`, `--travelers` |
| `list-hotels` | `--state JSON` |
| `select-hotel` | `--state JSON --hotel-id ID` |
| `list-activities` | `--state JSON` |
| `add-activity` | `--state JSON --activity-id ID` |
| `remove-activity` | `--state JSON --activity-id ID` |
| `show-plan` | `--state JSON` |

## State

- Every result has a `state`. Keep the **latest** `state` and pass it, unchanged, as `--state` on
  the next call (`json.dumps(state)`). Never edit it, never build one yourself.
- If the conversation already has a state from `confirm-trip-plan`, use that one.

## Output rules

- Show `markdown` to the traveler **as normal Markdown, never inside a code block**, exactly as
  returned — including its last line (the question or reply prompt), word for word. You may add
  one short sentence before it, but nothing after it. Do not add prices, totals or options of
  your own, and do not recalculate anything.
- Only offer hotels and activities that the script returned. If the traveler asks for something
  else (another hotel, a different tour), say it isn't in our catalog and show the catalog options.
- Map the traveler's choice to an id using the `options` list from the last `list-…` call
  (`n` = number shown, `name`, `id`). If the reply matches more than one option (e.g. "the cheap
  one" when two are similar), ask which one they mean.

## Procedure — trip and hotel

1. Get check-in date, check-out date and number of travelers. Ask for everything that is missing
   in **one** question. Convert dates the traveler gives (e.g. "10 to 14 March") to `YYYY-MM-DD`;
   if the year is not given, use the next occurrence of that date.
2. Call `start`. If `ok` is false, show `markdown` (it explains the problem) and ask again.
3. Call `list-hotels` straight away and show its `markdown`.
4. When the traveler chooses, call `select-hotel` with the matching id and show the `markdown`
   (the plan plus a question about activities).
5. If the traveler changes dates or travelers at any point, call `set-trip` and show the updated
   plan.

## Procedure — activities

1. When the traveler wants activities (or says yes to the question), call `list-activities` and
   show its `markdown`.
2. To add one, call `add-activity`; to remove one, call `remove-activity`. Show the `markdown`
   after every change: it contains the updated plan and the question "Would you like to add more
   activities, or continue to confirmation?".
3. If they want more, call `list-activities` again (it hides activities already in the plan).
4. When the traveler says "continue", "that's all", "no more" or similar, switch to the
   `confirm-trip-plan` skill with the latest state. Continuing with no activities is fine.

## Errors and edge cases

- `ok: false` → show `markdown` and help the traveler fix it. Error codes: `invalid_date`,
  `check_out_before_check_in`, `check_in_in_past`, `stay_too_long` (over 30 nights),
  `travelers_out_of_range` (1–10), `unknown_item`, `hotel_required`, `duplicate_activity`,
  `plan_confirmed`, `invalid_state`.
- Activities before a hotel → explain a hotel comes first and show the hotels.
- `plan_confirmed` → the plan can't change; offer to start a new plan (call `start` again).
- `invalid_state` → apologize and start a new plan from the trip details.
- If the script can't run, say so plainly. Never invent options, prices or totals.
