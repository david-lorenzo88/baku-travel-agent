# Implementation Plan: Baku Trip Planner (Hotel, Activities, Confirmation & PDF)

**Branch**: `001-baku-trip-planner` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-baku-trip-planner/spec.md`

## Summary

Build **Baku Travel Planner**, a Copilot Studio agent on the Microsoft Copilot harness (agentic
loop, no topics) that guides a traveler through trip details → hotel → activities → holder
details → explicit confirmation → final plan → PDF. All prices come from a bundled sample catalog
(AZN) and every total is computed by deterministic Python scripts inside three focused skills
(`baku-trip-catalog`, `confirm-trip-plan`, `export-trip-plan-pdf`). The plan is carried between
turns as a plan state JSON that the scripts recompute from the catalog on every call. Global
instructions hold the flow and safety rules; two official websites ground off-topic answers.
Authored as YAML with the mcs-assistant plugin and PAC CLI, deployed to the demo environment.
See [research.md](research.md) for the decisions behind this design.

## Technical Context

**Language/Version**: Python ≥ 3.10 (skill scripts; developed and tested with 3.13); YAML
(Copilot Studio MCS2 component files); Markdown (skill manifests)

**Primary Dependencies**: Copilot Studio Microsoft Copilot harness (CLI agent, template
`cliagent-*`); mcs-assistant plugin 1.0.2 (create-agent, add-skill, add-knowledge, push/pull,
publish, chat); Power Platform CLI 2.15.1; Python stdlib (`decimal`, `datetime`, `json`,
`argparse`, `secrets`, `re`); `reportlab` (provided by the harness) for PDFs

**Storage**: None. Catalog is a bundled JSON file; plan state lives in the conversation; the PDF
is a session-only download

**Testing**: `pytest` unit tests for all scripts and the YAML validator (local); YAML validation
(`tools/validate_agent.py`) before every push; conversation tests E1, C1–C7 and negative tests
N1–N5 in the Copilot Studio test chat against the unpublished draft (browser), with C4, C5 and N1–N3 run 3 times each;
a 5-person usability check for SC-006 ([quickstart.md](quickstart.md))

**Target Platform**: Copilot Studio, environment the demo environment; validated first in the Copilot Studio
test chat (Teams/Microsoft 365 Copilot channels are out of scope for v1)

**Project Type**: Conversational AI agent (Copilot Studio CLI agent project + skill packages)

**Performance Goals**: ≤ 30 s from the traveler's message to the updated plan for a single
change, measured in quickstart scenario E1; full flow (hotel + 2 activities → confirmed) under
10 minutes (SC-001), also measured in E1. (Revised from ≤ 10 s after testing: the Microsoft Copilot
harness took ~15–25 s per single change and 40–90 s for multi-step messages; SC-001 was met at
~3 minutes.)

**Constraints**: No topics, variables or Power Fx (agentic loop); sandbox has restricted network
access (photos for PDF must be bundled); totals exact to 2 decimals (SC-002); no ID/payment data;
generated files exist only during the session; component schema names ≤ 100 chars

**Scale/Scope**: 5 hotels, 6 activities, 1–10 travelers, stays up to 30 nights; English only;
3 skills, 2 knowledge sources, 0 tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Constitution v1.1.0.

| Principle | Gate | Pre-research | Post-design |
|---|---|---|---|
| I. Spec-first | Every component maps to spec requirements | ✅ | ✅ Mapping in [Requirement traceability](#requirement-traceability) |
| II. Grounded & honest | No invented options/prices; facts from sources; say when unknown | ✅ | ✅ Catalog-only scripts (FR-023); 2 official knowledge sites; instructions rule 7 |
| III. Safety & privacy | No booking/payment; confirm explicitly; holder contact only at confirmation; no ID/payment data | ✅ | ✅ No tools exist that book or pay; `confirm` only after explicit yes; holder model has 3 fields only |
| IV. Copilot Studio native | Generative orchestration, no classic topics, YAML in repo, validate before push, review before publish | ✅ | ✅ CLI agent, 0 topics; `agent/` + `skills-src/` in a git repo with commits after every push/pull; `tools/validate_agent.py` before every push; review of the git diff before publish (quickstart §4) |
| V. Testable conversations | Example conversations per story + negative tests run before publish | ✅ | ✅ C1–C7, N1–N5 in quickstart |
| VI. Simplicity | Minimal agent; integrations later; justify each component | ✅ | ✅ 0 tools, 0 connectors; 3 skills each justified in research R8 |
| Platform constraints | the demo environment, PAC ≥ 2.9.3, ALM via pull/push/publish, no secrets, English | ✅ | ✅ |

**Result**: PASS — no violations; Complexity Tracking not needed.

## Requirement traceability

| Requirement | Implemented by |
|---|---|
| FR-001–003 (trip details) | `trip_plan.py start/set-trip` + `pricing.py` validation; skill `baku-trip-catalog` |
| FR-004–007 (hotels) | `trip_plan.py list-hotels/select-hotel`; catalog hotels |
| FR-008–012 (activities) | `trip_plan.py list-activities/add-activity/remove-activity`; skill loop prompt |
| FR-013–015 (totals, AZN) | `pricing.py` (Decimal, half-up, recompute-from-catalog authority rule) |
| FR-016–018 (holder, confirm) | `confirm.py validate-holder/confirm`; skill `confirm-trip-plan`; instructions rules 5–6 |
| FR-019 (final plan) | `confirm.py confirm` Markdown ([rendering.md](contracts/rendering.md)) |
| FR-020–022 (PDF) | `make_pdf.py build`; skill `export-trip-plan-pdf` ([pdf-document.md](contracts/pdf-document.md)) |
| FR-023–024 (catalog, photos) | `_shared/catalog.json`; bundled photos; instructions rule 3 |
| Edge: off-topic questions | Knowledge sources + instructions rule 7 |

## Project Structure

### Documentation (this feature)

```text
specs/001-baku-trip-planner/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── agent-components.md
│   ├── scripts-cli.md
│   ├── rendering.md
│   ├── pdf-document.md
│   └── plan-state.schema.json
├── checklists/requirements.md
├── test-results/        # conversation test transcripts (implementation phase)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
agent/                              # Copilot Studio CLI project, created by `pac copilot init`
├── settings.mcs.yml                # instructions, model, identity (PAC-managed identity fields)
├── agent.sync.yaml                 # PAC-managed
├── behaviors/                      # skills imported by /mcs-assistant:add-skill
│   ├── baku-trip-catalog/
│   ├── confirm-trip-plan/
│   └── export-trip-plan-pdf/
├── capabilities/knowledge/         # 2 WebsiteKnowledgeSource components
└── .mcs/                           # PAC-managed, never hand-edited

skills-src/                         # source of truth for skill packages
├── _shared/
│   ├── catalog.json                # 5 hotels, 6 activities, photo URLs + credits, AZN
│   └── pricing.py                  # validation, Decimal pricing, plan recompute, Markdown
├── baku-trip-catalog/
│   ├── SKILL.md
│   ├── scripts/trip_plan.py        # + scripts/pricing.py (synced copy)
│   └── references/catalog.json     # synced copy
├── confirm-trip-plan/
│   ├── SKILL.md
│   ├── scripts/confirm.py          # + scripts/pricing.py (synced copy)
│   └── references/catalog.json     # synced copy
└── export-trip-plan-pdf/
    ├── SKILL.md
    ├── scripts/make_pdf.py         # + scripts/pricing.py (synced copy)
    ├── references/catalog.json     # synced copy
    └── assets/photos/*.jpg         # resized stock photos (≤ 200 KB each)

tools/
├── sync_shared.py                  # copies _shared files into each skill
├── fetch_photos.py                 # downloads + resizes catalog photos, checks URLs (dev only)
├── stage_skill.py                  # copies an updated skill's payload into agent/behaviors/
└── validate_agent.py               # YAML/skill checks, run before every push

tests/
├── fixtures/                       # agent-ok/ and agent-bad-*/ workspaces for the validator
└── unit/
    ├── test_pricing.py
    ├── test_trip_plan_cli.py
    ├── test_confirm_cli.py
    ├── test_make_pdf.py
    ├── test_shared_sync.py
    └── test_validate_agent.py
```

**Structure Decision**: Two source trees. `agent/` is the PAC-managed Copilot Studio project (the
deployable YAML, per Principle IV). `skills-src/` holds the human-edited skill packages and is
imported into `agent/behaviors/` with the plugin's `add-skill` importer, which generates the
anchor and sidecar YAML. Shared catalog and pricing code have a single source in
`skills-src/_shared/` and are copied into each self-contained package by `tools/sync_shared.py`.

## Implementation phases (for /speckit-tasks)

0. **Setup**: folders, dev requirements, `git init` with a baseline commit (the review gate
   compares against it).
1. **Spike** (de-risk research open items): a throwaway skill package with one script, one image
   and a reportlab PDF, pushed to a scratch agent or the new agent → verify script execution,
   image acceptance in packages, Markdown image rendering, PDF download. Apply documented
   fallbacks if any fail.
2. **Foundation**: YAML validator, `_shared/catalog.json` (photos found via the Wikimedia
   Commons API), `pricing.py`, sync tool, photo fetch, unit tests.
3. **US1 (P1)**: `trip_plan.py` trip + hotel commands; `baku-trip-catalog` SKILL.md (hotel part).
4. **US2 (P2)**: activity commands; SKILL.md activity loop.
5. **US3 (P3)**: `confirm.py`; `confirm-trip-plan` SKILL.md.
6. **US4 (P4)**: `make_pdf.py`; `export-trip-plan-pdf` SKILL.md; bundled photos.
7. **Agent**: create agent, instructions, import skills, add knowledge, push/pull.
8. **Validation**: conversation tests E1, C1–C7, N1–N5 (C4, C5, N1–N3 three runs each);
   5-person usability check; record results; review gate on the git diff; publish on approval.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Skill scripts don't execute in the harness | Low–Med | Spike first; fallback: agent runs the same code via the harness's Python sandbox from the skill's reference file |
| Images not accepted in skill packages | Med | Fallback: base64-embedded photos in a JSON resource |
| Markdown images not rendered in chat | Med | `--photo-style link` fallback |
| Model edits or recomputes totals itself | Med | Instructions + skill rules "show verbatim"; scripts ignore input totals; tests C1–C3 |
| Knowledge site not indexed / rejected | Low | Drop source, rely on "point to official site" rule |
| Schema name length (> 100 chars) | Low | Short skill folder names (≤ 22 chars) |

## Complexity Tracking

| Violation | Why it happened | Resolution |
|---|---|---|
| Constitution IV ("nothing is published without the review gate"): the agent was published before review | `pac copilot init` (T007) published the initial scaffold automatically — a documented PAC side effect the create-agent skill warns about, not an explicit publish. The published version contains only the first instructions: no skills, knowledge or holder data. | Recorded exception. All later changes stayed draft-only and were tested in the Preview chat. The reviewed publish in T049 replaces the scaffold version. For future features, check the agent's published state right after `pac copilot init`. |
