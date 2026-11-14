---

description: "Task list for the Baku Trip Planner Copilot Studio agent"
---

# Tasks: Baku Trip Planner (Hotel, Activities, Confirmation & PDF)

**Input**: Design documents from `/specs/001-baku-trip-planner/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Included. Constitution Principle V requires example-conversation tests and negative
tests before publishing, and the plan specifies `pytest` unit tests for every script (SC-002).
Write unit tests first and confirm they fail before implementing.

**Organization**: Tasks are grouped by user story so each story can be built, pushed and tested on
its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story the task belongs to (US1–US4)

## Path Conventions

- `agent/` — Copilot Studio CLI project created by `pac copilot init` (PAC-managed identity,
  `.mcs/` never hand-edited)
- `skills-src/` — skill package sources; `skills-src/_shared/` is the single source for
  `catalog.json` and `pricing.py`
- `tools/` — dev scripts; `tests/unit/` — pytest
- PAC is at `~/.dotnet/tools/pac` (add `~/.dotnet/tools` to PATH)
- Plugin skills: `/mcs-assistant:create-agent`, `/mcs-assistant:add-skill`,
  `/mcs-assistant:add-knowledge`, `/mcs-assistant:push-agent`, `/mcs-assistant:pull-agent`,
  `/mcs-assistant:publish-agent`. Conversation tests run in the **Copilot Studio test chat** (Test pane, driven in the browser), which talks to the unpublished draft; `/mcs-assistant:chat` only works with a published agent and an Entra app registration, so it is not used before T049

### Standard push procedure (used by every "push" step below)

1. `pac copilot pull` (pre-push pull — it overwrites local skill **payload** edits with the cloud copy)
2. For a skill that is already imported: `python tools/stage_skill.py <skill>` to copy its payload
   from `skills-src/` (never `add-skill --force`: it mints new schema names and the next pull reverts
   the payload). New skills are imported with the add-skill importer instead.
3. `python tools/validate_agent.py agent/` — fix every reported error first (Constitution IV)
4. `pac copilot push`, then a final `pac copilot pull` (as `/mcs-assistant:push-agent` does)
5. Commit `agent/`, `skills-src/`, `tools/`, `tests/` and
   `specs/001-baku-trip-planner/test-results/` with a message `feat(<scope>): <what changed>`

### Repeat-run rule

Replies vary between runs, so C4, C5, N1, N2 and N3 are run **3 times each** in fresh
conversations; a scenario passes only if every run passes. Save each run as
`<phase>-<scenario>-run<k>.md`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository layout, version control and local tooling

- [X] T001 Create the folders from plan.md: `skills-src/_shared/`, `skills-src/baku-trip-catalog/{scripts,references}/`, `skills-src/confirm-trip-plan/{scripts,references}/`, `skills-src/export-trip-plan-pdf/{scripts,references,assets/photos}/`, `tools/`, `tests/unit/`, `specs/001-baku-trip-planner/test-results/`. Do NOT create `agent/` (`pac copilot init` refuses a non-empty destination)
- [X] T002 [P] Create `requirements-dev.txt` at repo root with `pytest`, `reportlab`, `pypdf` (PDF text extraction in tests), `Pillow` (photo resizing in `tools/fetch_photos.py`), `PyYAML` (YAML validation in `tools/validate_agent.py`) `jsonschema` (plan-state schema checks in tests) and `matplotlib` (ships the DejaVu Sans font the PDF uses, as in the sandbox)
- [X] T003 [P] Create `.gitignore` at repo root ignoring `__pycache__/`, `.pytest_cache/`, `*.pyc`, `.venv/`, `agent/.mcs/`, `*.pdf` outside `tests/fixtures/`, and `.claude/settings.local.json`
- [X] T004 [P] Create `pytest.ini` at repo root with `testpaths = tests/unit` and `pythonpath = skills-src/_shared` only. Script tests run each script as a separate process from its own folder, so each one imports its own synced `pricing.py`
- [X] T005 Create a local virtual environment `.venv/` and install `requirements-dev.txt`; confirm `python -m pytest --version` runs
- [X] T006 Initialize git at the repo root (`git init -b main`) and commit a baseline of `.specify/`, `.claude/skills/`, `specs/`, `.gitignore`, `requirements-dev.txt` and `pytest.ini` with message `docs: spec, plan and tasks for 001-baku-trip-planner`; record the baseline commit hash in `specs/001-baku-trip-planner/test-results/summary.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cloud agent, YAML validation, runtime spike, catalog, shared pricing module and sync
tooling that every story needs

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Cloud agent and validation

- [X] T007 Create the cloud agent with `/mcs-assistant:create-agent`: display name `Baku Travel Planner`, environment `https://<your-org>.crm.dynamics.com/`, project dir `<repo>/agent`, publisher prefix `catmgr` (unless the user gives another), instructions-only path, instructions = a minimal version of rules 1–8 in contracts/agent-components.md (T022 writes the authoritative version). Verify `agent/settings.mcs.yml` has `template: cliagent-*`, `authoringModel: CliCopilot`, and no topics exist; commit `agent/`
- [X] T008 [P] Write `tools/validate_agent.py <agent-dir>` that exits non-zero listing every problem: parse every `*.mcs.yml` and `settings.mcs.yml` with `yaml.safe_load` (YAML 1.1); every component except `settings.mcs.yml` has `mcs.metadata.componentName`; `kind` present except in metadata-only sidecars (uploaded-knowledge and skill payload sidecars); `settings.mcs.yml` keeps a `template` starting with `cliagent-` and `configuration.authoringModel: CliCopilot`; no `topics/` folder or topic components; every `behaviors/*/SKILL.md` has frontmatter `name` equal to its folder (max 64 chars, lowercase letters, digits and single hyphens) and a one-line `description` ≤ 1,024 chars; no `schemaName`/derived schema name over 100 chars
- [X] T009 [P] Write `tests/unit/test_validate_agent.py` with one passing fixture workspace under `tests/fixtures/agent-ok/` and one failing case per rule in T008 (implemented by copying `agent-ok` to a temp folder and breaking one rule per test, instead of on-disk `agent-bad-*` folders); make it pass against T008

### Runtime spike (de-risks research.md "Open items")

- [X] T010 Create spike skill `skills-src/_spike/spike-check/` with `SKILL.md` (frontmatter `name: spike-check`, description "Runtime check for script execution, bundled images and PDF output. Use only when the user says 'run spike check'."), `scripts/spike.py` (prints Python version, whether `reportlab` imports, lists `../assets/`, writes `spike.pdf` embedding `../assets/test.jpg`, prints a Markdown line with an inline image from a Wikimedia Commons HTTPS URL) and `assets/test.jpg` (≤ 100 KB)
- [X] T011 Import the spike skill into `agent/behaviors/spike-check/` with `/mcs-assistant:add-skill`, then follow the standard push procedure
- [X] T012 Run "run spike check" in the Copilot Studio test chat (browser, unpublished draft); record in `specs/001-baku-trip-planner/research.md` (new section "Spike results") whether (1) the script ran, (2) the bundled image was readable, (3) the Markdown image rendered, (4) a PDF download link appeared. For each failure, record the fallback chosen from research.md R5/R7 and plan.md Risks, and update the affected contract (contracts/rendering.md or contracts/scripts-cli.md)
- [X] T013 Remove the spike skill: delete `agent/behaviors/spike-check/`, follow the standard push procedure, then confirm with `/mcs-assistant:pull-agent` that `agent/behaviors/spike-check/` stays absent AND that `spike-check` is no longer listed in Copilot Studio (Build → Skills). If it is still listed, remove it in the portal, then `/mcs-assistant:pull-agent` and commit. Delete `skills-src/_spike/`

### Catalog and photos

- [X] T014 Find 1 photo per catalog item (5 hotels' neighborhoods, 6 activities) with the Wikimedia Commons API: `https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch=<term>` to find files, then `prop=imageinfo&iiprop=url|extmetadata` for the direct URL, `Artist` and `LicenseShortName`. Keep only CC BY, CC BY-SA or public-domain files. Send a generic `User-Agent: baku-travel-agent-dev/1.0` with no personal details. Write the chosen `url`, `credit` ("<Artist>, <License>, Wikimedia Commons") and `alt` into a working list for T015
- [X] T015 Write `skills-src/_shared/catalog.json` with `currency: "AZN"`, `catalog_version: "2026-11-13"`, `sample_data: true`, 5 hotels and 6 activities per data-model.md, using the photos from T014. Hotels: `id` "Unique, `htl-` prefix, kebab-case"; `name` "1–80 chars; fictional sample name"; `neighborhood` "Real Baku area (e.g. Old City / İçərişəhər, Fountain Square, Baku Boulevard, Port Baku)"; `description` "1–300 chars"; `price_per_person_per_night` "> 0, 2 decimals" as a string; `photos` "≥ 1". Activities: `id` "Unique, `act-` prefix, kebab-case"; Old City walking tour, Gobustan & mud volcanoes day trip, Ateshgah & Yanar Dag evening tour, Baku Boulevard boat ride, Heydar Aliyev Center visit, Azerbaijani cooking class; `description` "1–400 chars"; `duration`; `price_per_person` "> 0, 2 decimals". Each Photo: `url`, `file`, `alt` "1–120 chars", `credit`. Include one hotel at AZN 60.00 and an "Old City walking tour" at AZN 25.00 so the spec examples hold
- [X] T016 [P] Write `tools/fetch_photos.py`: for every photo in `skills-src/_shared/catalog.json`, using the same generic `User-Agent: baku-travel-agent-dev/1.0`, check the URL returns HTTP 200 with an image content type, download it, resize to max 800 px wide JPEG ≤ 200 KB with Pillow, save as `skills-src/export-trip-plan-pdf/assets/photos/<file>`, and exit non-zero listing any failed URL
- [X] T017 Run `tools/fetch_photos.py`; replace any failing photo in `skills-src/_shared/catalog.json` (repeat T014 for that item) and re-run until all photos pass

### Shared pricing and sync

- [X] T018 [P] Write failing tests in `tests/unit/test_pricing.py` for: money formatting `AZN 1,234.50`; Decimal half-up rounding; nights = days between dates; validation errors `invalid_date`, `check_out_before_check_in`, `check_in_in_past` (Baku time UTC+4), `stay_too_long` (> 30 nights), `travelers_out_of_range` (outside 1–10); recompute ignores input `lines`/`grand_total`/prices; hotel line `unit_price × travelers × nights`; activity line `unit_price × travelers`; grand total = sum of lines; 2 travelers × 4 nights × 60.00 = 480.00 and + 25.00 × 2 = 530.00; `unknown_item`, `hotel_required`, `duplicate_activity`, `plan_confirmed`; state validates against `contracts/plan-state.schema.json`
- [X] T019 Implement `skills-src/_shared/pricing.py` (stdlib only, Python ≥ 3.10): catalog loading from `../references/catalog.json` relative to the calling script, trip validation, `recompute(state, catalog)` applying the authority rule in data-model.md (only `trip`, `hotel_id`, `activity_ids`, `status`, `holder`, `confirmation` are inputs), money formatting, plan-block Markdown exactly as contracts/rendering.md "Plan block", the common JSON output envelope and error codes from contracts/scripts-cli.md. Make T018 pass
- [X] T020 [P] Write `tools/sync_shared.py` copying `skills-src/_shared/catalog.json` → `skills-src/<skill>/references/catalog.json` and `skills-src/_shared/pricing.py` → `skills-src/<skill>/scripts/pricing.py` for `baku-trip-catalog`, `confirm-trip-plan`, `export-trip-plan-pdf`, adding a header comment "GENERATED by tools/sync_shared.py — edit skills-src/_shared/ instead" to the `.py` copy
- [X] T021 [P] Write `tests/unit/test_shared_sync.py` failing when any synced copy differs from its `_shared` source (ignoring the generated header line)
- [X] T022 Edit the StaticSegment in `agent/settings.mcs.yml` so instructions cover all 8 rules in contracts/agent-components.md verbatim in intent (flow order, scripts-only prices shown verbatim, carry latest plan state, privacy, confirmation ≠ booking, off-topic grounding, AZN/English/tone). Keep `displayName`, `schemaName`, template, model and recognizer unchanged; run `python tools/validate_agent.py agent/` and commit

**Checkpoint**: Agent exists in the demo environment with full instructions; runtime capabilities verified;
`pytest` passes for pricing, sync and validation

---

## Phase 3: User Story 1 - Choose a hotel and see the stay total (Priority: P1) 🎯 MVP

**Goal**: Traveler gives dates and party size, sees 3–5 hotels with photo and price, picks one,
and sees the plan with the stay total and grand total.

**Independent Test**: quickstart.md conversation C1; unit tests for `start`, `set-trip`,
`list-hotels`, `select-hotel`, `show-plan`.

### Tests for User Story 1 ⚠️

- [X] T023 [P] [US1] Write failing CLI tests in `tests/unit/test_trip_plan_cli.py` (run `trip_plan.py` via subprocess from its folder) for: `start` with valid input returns `ok: true` and `nights`; each trip validation error code; `list-hotels` returns 3–5 options each with name, neighborhood, description, image, "per person per night" price; `list-hotels --photo-style link` renders `[View photo](url)` instead of an image; `select-hotel` sets `hotel_id`, line total 480.00 for 2 × 4 × 60.00 and grand total 480.00; selecting a second hotel replaces the first (FR-007); `unknown_item` for a bad id; `set-trip --travelers 3` recalculates; output always one JSON object with exit code 0 on validation errors

### Implementation for User Story 1

- [X] T024 [US1] Implement `skills-src/baku-trip-catalog/scripts/trip_plan.py` commands `start`, `set-trip`, `list-hotels`, `select-hotel`, `show-plan` with argparse, importing `pricing.py` from the same folder; `list-hotels` accepts `--photo-style {inline,link}` (default `inline`); hotel option Markdown exactly as contracts/rendering.md "Hotel option" plus the "Reply with the number or name…" line; `options` list `[{"n":1,"id":"htl-..."}]`; next-step line "Would you like to see some activities in Baku?" after `select-hotel`. Make T023 pass
- [X] T025 [US1] Write `skills-src/baku-trip-catalog/SKILL.md`: frontmatter `name: baku-trip-catalog` and the description from contracts/agent-components.md; body sections "When to use", "Required inputs" (check-in, check-out, travelers — ask for all missing ones in one question), "Procedure — trip and hotel" (call `start` or `set-trip`, then `list-hotels`, map the traveler's reply by number or name, ask when ambiguous, call `select-hotel`), "State" (always pass the latest `state` from the previous output; never edit it), "Output rules" (show `markdown` verbatim; never compute or change prices; never offer items not returned by the script; pass `--photo-style link` only if T012 recorded that images don't render), "Errors" (show the script's message and ask again), "Edge cases" (hotel not in catalog, activities before hotel)
- [X] T026 [US1] Run `tools/sync_shared.py` and `python -m pytest`; import `skills-src/baku-trip-catalog/` into `agent/behaviors/baku-trip-catalog/` with `/mcs-assistant:add-skill`, then follow the standard push procedure (`feat(us1): hotel selection`)
- [X] T027 [US1] Run conversation C1 (spec US1 example) and the "invalid dates", "31 nights", "11 travelers" and "Four Seasons not in catalog" (N4) cases in the Copilot Studio test chat (browser, unpublished draft); save transcripts to `specs/001-baku-trip-planner/test-results/us1-*.md` with pass/fail per quickstart.md criteria; fix SKILL.md or instructions and repeat until all pass; commit the results

**Checkpoint**: MVP — hotel selection with exact stay total works in the draft agent

---

## Phase 4: User Story 2 - Add activities and keep the grand total up to date (Priority: P2)

**Goal**: After the hotel, traveler adds/removes activities; grand total updates after every
change; agent asks "add more or continue?".

**Independent Test**: quickstart.md C2 and C3; unit tests for activity commands.

### Tests for User Story 2 ⚠️

- [X] T028 [P] [US2] Add failing tests to `tests/unit/test_trip_plan_cli.py` for: `list-activities` returns 3–6 options not already in the plan, each with name, description, image, price per person; `list-activities --photo-style link` renders links; `list-activities` without hotel → `hotel_required`; `add-activity` 25.00 × 2 travelers = 50.00 and grand total 530.00; adding the same activity twice → `duplicate_activity`; `remove-activity` recalculates; next-step line "Would you like to add more activities, or continue to confirmation?" after add/remove; changing travelers after activities recalculates every line

### Implementation for User Story 2

- [X] T029 [US2] Add commands `list-activities` (with `--photo-style {inline,link}`, default `inline`), `add-activity`, `remove-activity` to `skills-src/baku-trip-catalog/scripts/trip_plan.py`; activity option Markdown exactly as contracts/rendering.md "Activity option" plus the "Reply with the number or name… or say 'continue'" line. Make T028 pass. *Note:* this code was written together with T024 (same file and helpers); T028's tests were written afterwards and pass against it
- [X] T030 [US2] Add section "Procedure — activities" to `skills-src/baku-trip-catalog/SKILL.md`: after the hotel, offer activities via `list-activities`; add/remove on request; after every change show the plan and the add-more-or-continue question; on "continue" (or "no more"), hand over to confirmation (the `confirm-trip-plan` skill); continuing with zero activities is allowed
- [X] T031 [US2] Run `tools/sync_shared.py` and `python -m pytest`; re-import `skills-src/baku-trip-catalog/` with `/mcs-assistant:add-skill` (replace the existing skill only after confirming the overwrite), then follow the standard push procedure (`feat(us2): activities and running total`)
- [X] T032 [US2] Run conversations C2 and C3 in the Copilot Studio test chat (browser, unpublished draft); save to `specs/001-baku-trip-planner/test-results/us2-*.md` with pass/fail; fix and repeat until all pass; commit the results

**Checkpoint**: US1 + US2 work; the plan always shows the correct grand total

---

## Phase 5: User Story 3 - Provide holder details and confirm the plan (Priority: P3)

**Goal**: Agent collects holder name, email and phone, shows the full summary, and confirms only
after an explicit yes, issuing a reference.

**Independent Test**: quickstart.md C4, C5, N1, N2, N5; unit tests for `confirm.py`.

### Tests for User Story 3 ⚠️

- [X] T033 [P] [US3] Write failing CLI tests in `tests/unit/test_confirm_cli.py` for: `validate-holder` accepts `full_name` "2–100 chars; letters (any script), spaces, `-`, `'`, `.`", `email` "Basic address format `local@domain.tld`, ≤ 254 chars", `phone` "Optional leading `+`; 7–15 digits after removing spaces, `-`, `(`, `)`"; rejects each with `invalid_name`/`invalid_email`/`invalid_phone`; no other holder fields are accepted; summary Markdown contains every plan line, grand total and the "Shall I confirm this plan?… no payment is taken." text from contracts/rendering.md; `confirm` without hotel → `hotel_required`, without holder → `holder_required`, twice → `already_confirmed`; `confirm` sets `status: "confirmed"`, `reference` matching `^BAK-[0-9]{8}-[A-HJ-NP-Z2-9]{6}$`, `confirmed_at` with `+04:00`; final-plan Markdown matches contracts/rendering.md "Final plan"; `trip_plan.py` commands on a confirmed state → `plan_confirmed`

### Implementation for User Story 3

- [X] T034 [US3] Implement `skills-src/confirm-trip-plan/scripts/confirm.py` commands `validate-holder` and `confirm` per contracts/scripts-cli.md, importing `pricing.py` from the same folder and recomputing lines from `../references/catalog.json`; reference via `secrets.choice` over `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`; Baku time UTC+4. Make T033 pass
- [X] T035 [US3] Write `skills-src/confirm-trip-plan/SKILL.md`: frontmatter `name: confirm-trip-plan` and the description from contracts/agent-components.md; body: ask for full name, email and phone in one message; call `validate-holder`; on a field error ask again for that field only; show the summary verbatim; call `confirm` ONLY after an explicit yes ("yes", "confirm", "go ahead"); anything else keeps the plan as a draft and offers to change hotel, activities or holder details; never ask for or repeat passport/ID, card, bank or password data and say they aren't needed if offered; explain that confirming creates a plan with a reference, not a booking or payment; after confirmation show the final plan and offer the PDF; a confirmed plan can't be edited — offer a new plan
- [X] T036 [US3] Run `tools/sync_shared.py` and `python -m pytest`; import `skills-src/confirm-trip-plan/` with `/mcs-assistant:add-skill`, then follow the standard push procedure (`feat(us3): holder details and confirmation`)
- [X] T037 [US3] Run C4, C5, N1 and N2 **3 times each** in fresh conversations (repeat-run rule) and N5 once in the Copilot Studio test chat (browser, unpublished draft); save each run to `specs/001-baku-trip-planner/test-results/us3-<scenario>-run<k>.md` with pass/fail; a scenario passes only if all its runs pass; fix and repeat until all pass; commit the results

**Checkpoint**: Plans can be confirmed safely; negative tests for booking and sensitive data pass

---

## Phase 6: User Story 4 - View the final plan and export it as PDF (Priority: P4)

**Goal**: After confirmation, the traveler downloads a PDF with the same information as the
on-screen plan, including photos.

**Independent Test**: quickstart.md C6 and C7; unit tests for `make_pdf.py`.

### Tests for User Story 4 ⚠️

- [X] T038 [P] [US4] Write failing tests in `tests/unit/test_make_pdf.py`: `build` on a confirmed state writes `Baku-Trip-<reference>.pdf`; text extracted with `pypdf` contains, in order, the header and reference, holder name/email/phone, check-in/check-out/nights/travelers, hotel name/neighborhood/price/quantity/stay total, each activity, the totals table with grand total in AZN, the footer note with `catalog_version`, and photo credits (contracts/pdf-document.md); `build` on a draft → `not_confirmed`; a missing photo file → PDF still built and `photo_missing` reported

### Implementation for User Story 4

- [X] T039 [US4] Implement `skills-src/export-trip-plan-pdf/scripts/make_pdf.py` with reportlab (A4) following contracts/pdf-document.md sections 1–8, recomputing lines via `pricing.py` from `../references/catalog.json`, loading photos from `../assets/photos/`, grey placeholder box for a missing photo. Make T038 pass
- [X] T040 [US4] Write `skills-src/export-trip-plan-pdf/SKILL.md`: frontmatter `name: export-trip-plan-pdf` and the description from contracts/agent-components.md; body: only for a confirmed plan (otherwise explain and offer confirmation); call `build` with the latest state; return the generated file to the traveler; if the file can't be produced, say so and show the final plan again
- [X] T041 [US4] Run `tools/sync_shared.py` and `python -m pytest`; import `skills-src/export-trip-plan-pdf/` (including `assets/photos/`) with `/mcs-assistant:add-skill`, then follow the standard push procedure (`feat(us4): PDF export`)
- [X] T042 [US4] Run conversations C6 and C7 in the Copilot Studio test chat (browser, unpublished draft) (download the PDF and compare every field with the on-screen final plan); save to `specs/001-baku-trip-planner/test-results/us4-*.md` with pass/fail; fix and repeat until all pass; commit the results

**Checkpoint**: All four user stories work end to end in the draft agent

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Grounding for off-topic questions, full regression, usability, review gate and publish

- [X] T043 [P] Add the two website knowledge sources with `/mcs-assistant:add-knowledge` into `agent/capabilities/knowledge/`, using the componentName and description values from contracts/agent-components.md (`https://evisa.gov.az`, `https://azerbaijan.travel`); drop a source that the plugin rejects and record it as a gap in `specs/001-baku-trip-planner/research.md`
- [X] T044 Follow the standard push procedure (`feat: official knowledge sources`), then run N3 ("What's the visa fee for my country?") 3 times (repeat-run rule) in the Copilot Studio test chat (browser, unpublished draft); save to `specs/001-baku-trip-planner/test-results/polish-n3-run<k>.md`; pass when every answer cites an official source and advises verifying, or points to evisa.gov.az, with no invented fee
- [X] T045 Run the full quickstart.md validation in one fresh pass: section 1 unit tests, `tools/validate_agent.py`, then E1, C1–C7 and N1–N5 (repeat-run rule for C4, C5, N1–N3). In E1 record the time from the first message to confirmation (SC-001, < 10 minutes) and the response time of each plan update (target ≤ 10 s). Write `specs/001-baku-trip-planner/test-results/summary.md` with pass/fail per scenario and these timings; commit. *Executed scope:* one final E1 conversation on the final draft (covering C1, C2, C4, a C5-style question, C6 and the F1 re-check) plus the 3-run C4/C5/N1/N2/N3 scenarios; C1–C3 and the US1 edge cases ran earlier on the same skills (only the fictional-catalog instruction and knowledge sources changed since) — see summary.md
- [ ] T046 Usability check for SC-006 (kit: `specs/001-baku-trip-planner/usability/` — facilitator guide, tester cards, observation sheet, results): 5 people who haven't seen the agent each complete E1 in the Copilot Studio test chat without help; record completions and where anyone got stuck in `specs/001-baku-trip-planner/test-results/summary.md`. SC-006 passes at ≥ 90%, which with 5 people means all 5
- [X] T047 [P] Run `/speckit-analyze` and resolve any inconsistencies between spec.md, plan.md and tasks.md
- [X] T048 Review gate (Constitution, Development Workflow step 7): present `git diff <baseline-commit>..HEAD -- agent/ skills-src/` (baseline from T006), the unit test results and `test-results/summary.md` to the user for human review; record approval or requested changes in `specs/001-baku-trip-planner/test-results/summary.md` and commit
- [X] T049 Only after explicit user approval in T048: publish with `/mcs-assistant:publish-agent` (it asks for its own final confirmation), then `/mcs-assistant:pull-agent`, record the published state in `specs/001-baku-trip-planner/test-results/summary.md` and commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T006 after T001–T004 (files to commit)
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS all user stories
  - T007 → T011 (needs the agent and T008 validator) → T012 → T013 (spike)
  - T008 → T009; T008 must be done before the first push (T011)
  - T014 → T015 → T016 → T017; T018 → T019; T020 and T021 after T019; T022 after T007 and T008
- **US1 (Phase 3)**: Depends on Phase 2
- **US2 (Phase 4)**: Depends on US1 (extends `trip_plan.py` and the same SKILL.md; activities need a hotel in the plan)
- **US3 (Phase 5)**: Depends on Phase 2 for code (T033–T035 can be written in parallel with US1/US2); its conversation tests (T037) need US1 deployed
- **US4 (Phase 6)**: Depends on Phase 2 for code (T038–T040 parallel with US1–US3); conversation tests (T042) need US3 deployed
- **Polish (Phase 7)**: Depends on all user stories; T046 after T045; T049 depends on T048 approval

### User Story Dependencies

- **US1 (P1)**: Independent after Foundational
- **US2 (P2)**: Builds on US1's script and skill (same files) — sequential after US1
- **US3 (P3)**: Script and skill independent; end-to-end test needs a plan with a hotel (US1)
- **US4 (P4)**: Script and skill independent; end-to-end test needs a confirmed plan (US3)

### Within Each User Story

- Unit tests written and failing → script → SKILL.md → sync + pytest → import → validate → push → commit → conversation tests
- Each push is followed by the plugin's final pull (PAC layout is canonical)

### Parallel Opportunities

- Setup: T002, T003, T004 together
- Foundational: T008, T009, T016, T018, T020, T021 are different files (T009 waits for T008; T017 for T015/T016; T019 for T018)
- After Foundational: script + SKILL.md work for US3 (T033–T035) and US4 (T038–T040) can proceed alongside US1/US2 because they touch different skill folders
- Cloud steps (`add-skill`, push procedure, conversation tests) are sequential: one workspace, one push at a time

---

## Parallel Example: after Phase 2

```bash
# Different skill folders, no shared files:
Task: "T023 [US1] CLI tests in tests/unit/test_trip_plan_cli.py"
Task: "T033 [US3] CLI tests in tests/unit/test_confirm_cli.py"
Task: "T038 [US4] PDF tests in tests/unit/test_make_pdf.py"

# Then, in parallel:
Task: "T024 [US1] trip_plan.py in skills-src/baku-trip-catalog/scripts/"
Task: "T034 [US3] confirm.py in skills-src/confirm-trip-plan/scripts/"
Task: "T039 [US4] make_pdf.py in skills-src/export-trip-plan-pdf/scripts/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup → Phase 2 Foundational (agent created, validator ready, spike passed, pricing tested)
2. Phase 3 US1 → **STOP and VALIDATE** with C1 and the US1 edge cases
3. Demo the hotel-selection agent in the Copilot Studio test chat

### Incremental Delivery

1. Foundation → US1 (MVP) → push + test
2. US2 → push + test (activities and running grand total)
3. US3 → push + test (confirmation, privacy negative tests)
4. US4 → push + test (PDF)
5. Polish → knowledge, full regression, usability check, review gate, publish on approval

---

## Notes

- Never run `pac copilot publish` outside T049; never hand-edit `agent/.mcs/` or `agent/agent.sync.yaml`
- Any change made in the portal must be pulled (`/mcs-assistant:pull-agent`) and committed before further local work (Constitution IV)
- Never push without a clean `tools/validate_agent.py` run (Constitution IV)
- Edit `skills-src/_shared/` only; regenerate copies with `tools/sync_shared.py`
- Re-importing a skill overwrites `agent/behaviors/<skill>/` — confirm before replacing
- Deleting `agent/behaviors/<skill>/` locally does not remove a skill from the cloud (the pre-push pull restores it); remove it in Copilot Studio, then pull (found in T013)
- If T012 changes a design decision, update research.md and the affected contract before continuing
