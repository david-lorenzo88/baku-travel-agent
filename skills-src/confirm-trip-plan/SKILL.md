---
name: confirm-trip-plan
description: "Confirms a Baku trip plan: asks for the plan holder's full name, email and phone, validates them, shows the full plan summary, and confirms the plan only after the traveler explicitly agrees, issuing a reference. Use when the traveler wants to continue to confirmation or finalize the plan."
---

# Confirm the trip plan

## When to use

Use this skill when the traveler has a plan with a hotel and says "continue", "that's all",
"confirm", "finalize" or similar. Hotels and activities are handled by `baku-trip-catalog`;
the PDF by `export-trip-plan-pdf`.

## How to run the script

The script is `scripts/confirm.py` in this skill's folder. It prints exactly one JSON object
`{"ok": ..., "state": {...}, "markdown": "...", "errors": [...]}`. Run it from Python with an
argument list (no shell quoting):

```python
import json, subprocess, sys
SKILL_DIR = "<folder that contains this SKILL.md>"
def confirm(*args):
    out = subprocess.run([sys.executable, f"{SKILL_DIR}/scripts/confirm.py", *args],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)
```

| Command | Arguments |
|---|---|
| `validate-holder` | `--state JSON --full-name NAME --email EMAIL --phone PHONE` |
| `confirm` | `--state JSON` |

Always pass the latest `state` from the previous script call unchanged (`json.dumps(state)`),
and keep the new `state` each result returns.

## Procedure

1. Ask for the holder's **full name, email address and phone number** in one message. Ask for
   nothing else: no passport or ID number, no date of birth, no card or bank details.
2. Call `validate-holder`. If `ok` is false, show `markdown` and ask again **only** for the fields
   listed in `errors` (`invalid_name`, `invalid_email`, `invalid_phone`), keeping the others.
3. When `ok` is true, show `markdown` (the full summary and the question "Shall I confirm this
   plan? …") as normal Markdown, never in a code block, and wait for the answer.
4. Call `confirm` **only if the traveler's reply is an explicit yes** to that question — for
   example "yes", "confirm", "yes, confirm it", "go ahead". Anything else (no, not yet, a question,
   a change request, silence) keeps the plan as a draft: answer it and offer to change the hotel,
   activities or holder details, then show the summary again before asking once more.
5. After `confirm`, show its `markdown`: the confirmed plan, the confirmation reference, the holder
   and the offer to export a PDF. If the traveler wants the PDF, use `export-trip-plan-pdf`.

## Rules

- **Confirming is not booking.** It creates a trip plan with a reference. No hotel or activity is
  reserved, no payment is taken and nothing is sent to anyone. If the traveler asks to book or pay,
  say this agent can't do that. The catalog is sample data with fictional hotel names: never suggest
  contacting or booking a catalog hotel or provider, and never recommend booking websites.
- **Sensitive data.** Never ask for, repeat or keep passport/ID numbers, payment card or bank
  details or passwords. If the traveler shares them, do not repeat them, do not pass them to any
  script, and say they aren't needed for this plan.
- Show script `markdown` exactly as returned, including its last line, and add nothing after it.
  Never change names, prices or totals.
- A confirmed plan can't be changed (`already_confirmed`): offer to start a new plan with
  `baku-trip-catalog`.
- `hotel_required` → a hotel must be chosen first; go back to `baku-trip-catalog`.
- If a script can't run, say so plainly. Never invent a confirmation reference.
