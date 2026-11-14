# Contract: Skill scripts (command-line interface)

The agent calls these scripts from inside the skills. Every command:

- takes arguments on the command line and, where noted, the current plan state as a JSON string
  in `--state` (schema: [plan-state.schema.json](plan-state.schema.json));
- prints **one JSON object** to stdout and exits `0`, even for validation errors;
- never reads the network; reads only files bundled in its own skill.

Common output envelope:

```json
{
  "ok": true,
  "state": { "...plan state..." },
  "markdown": "...text the agent shows verbatim...",
  "errors": []
}
```

On a validation problem: `"ok": false`, `state` = the unchanged input state (or `null`),
`markdown` = a short user-facing explanation, `errors` = list of `{ "code": "...", "message": "..." }`.
Exit code `2` is used only for programming errors (bad JSON, unknown command).

## `baku-trip-catalog/scripts/trip_plan.py`

| Command | Arguments | Result | Spec |
|---|---|---|---|
| `start` | `--check-in YYYY-MM-DD --check-out YYYY-MM-DD --travelers N` | New draft state with trip details; `markdown` = trip summary | FR-001–003 |
| `set-trip` | `--state JSON` + any of `--check-in/--check-out/--travelers` | State with new trip details; all lines recalculated; `markdown` = updated plan | Edge case "trip details change" |
| `list-hotels` | `--state JSON` | `markdown` = 3–5 hotel options (see [rendering.md](rendering.md)); `options` = `[{"n":1,"id":"htl-..."}]` | FR-004, FR-005 |
| `select-hotel` | `--state JSON --hotel-id ID` | Hotel set/replaced; `markdown` = updated plan + next-step prompt | FR-006, FR-007, FR-014 |
| `list-activities` | `--state JSON` | `markdown` = 3–6 activity options not yet in the plan; `options` list | FR-008, FR-009 |
| `add-activity` | `--state JSON --activity-id ID` | Activity added; `markdown` = updated plan + "add more or continue?" | FR-010–012, FR-014 |
| `remove-activity` | `--state JSON --activity-id ID` | Activity removed; `markdown` = updated plan + same prompt | FR-011, FR-014 |
| `show-plan` | `--state JSON` | `markdown` = current plan | FR-014 |

Error codes: `invalid_date`, `check_out_before_check_in`, `check_in_in_past`, `stay_too_long`,
`travelers_out_of_range`, `unknown_item`, `hotel_required`, `duplicate_activity`,
`plan_confirmed` (any change to a confirmed plan), `invalid_state`.

## `confirm-trip-plan/scripts/confirm.py`

| Command | Arguments | Result | Spec |
|---|---|---|---|
| `validate-holder` | `--state JSON --full-name S --email S --phone S` | Valid → state with `holder`; `markdown` = full summary + explicit confirmation question. Invalid → field errors | FR-016, FR-017, FR-018 |
| `confirm` | `--state JSON` | Requires draft + hotel + valid holder; sets `status=confirmed`, `confirmation`; `markdown` = final plan (FR-019) + PDF offer | FR-018, FR-019 |

Error codes: `invalid_name`, `invalid_email`, `invalid_phone`, `hotel_required`,
`holder_required`, `already_confirmed`, `invalid_state`. `validate-holder` (and `confirm`, which
re-validates the stored holder) reports **all** invalid fields at once: `errors` may contain up to
three entries and `markdown` lists each message.

`confirm` is called **only** after the traveler's explicit confirmation in the conversation; the
script cannot tell, so this rule is enforced by the skill instructions and tested in the
conversation tests (SC-007).

## `export-trip-plan-pdf/scripts/make_pdf.py`

| Command | Arguments | Result | Spec |
|---|---|---|---|
| `build` | `--state JSON [--out DIR] [--photos-dir DIR]` | Requires `status=confirmed`. Recomputes lines from the bundled catalog copy, writes `Baku-Trip-<reference>.pdf`, prints `{"ok":true,"file":"<path>","markdown":"..."}` | FR-020–022 |

Error codes: `not_confirmed`, `invalid_state`, `pdf_failed` (no writable output folder),
`photo_missing` (non-fatal: PDF is built with a placeholder box, `ok` stays true and the error is
reported). Output folder: `--out` if writable, else the current folder, `/app/workspace`, then the
system temp folder (the skill folder is read-only at runtime). `--photos-dir` overrides the bundled
`../assets/photos` (used by tests).

## Shared code and catalog

Each skill package must be self-contained, but all three scripts must price identically. So:

- The single sources are `skills-src/_shared/catalog.json` and `skills-src/_shared/pricing.py`
  (validation, Decimal arithmetic, plan recomputation, Markdown rendering of the plan).
- `tools/sync_shared.py` copies them into each skill (`references/catalog.json`,
  `scripts/pricing.py`) before import. Copies are never edited by hand.
- A unit test fails if any copy differs from the shared source.

`confirm.py` and `make_pdf.py` therefore recompute lines and totals from their own catalog copy,
following the same authority rule as `trip_plan.py`.
