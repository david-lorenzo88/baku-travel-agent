# Test Results Summary: Baku Trip Planner

**Baseline commit** (review gate compares against it): `03df43a` — docs: spec, plan and tasks
for 001-baku-trip-planner

## Unit tests

119 passed (pricing 29, trip_plan CLI 20, validator 20, shared sync 6, confirm CLI 36, PDF 8) — 2026-11-13.

## Conversation tests

| Scenario | Runs | Result | Transcript |
|---|---|---|---|
| Spike (T012) | 1 | ✅ all 4 checks | research.md "Spike results" |
| C1 | 1 | ✅ | us1-c1.md |
| US1 edge cases (dates, 31+ nights, 11 travelers) | 1 | ✅ | us1-edge-cases.md |
| N4 (hotel not in catalog) | 1 | ✅ | us1-edge-cases.md |
| C2 | 1 | ✅ | us2-c2-c3.md |
| C3 | 1 | ✅ | us2-c2-c3.md |
| E1 (incl. C4, C6 run 1) | 1 | ✅ incl. SC-004 PDF = screen | e1-run1.md |
| C4 (explicit confirm) | 3 | ✅ 3/3 | us3-safety-runs.md |
| C5 (no explicit yes → draft) | 3 | ✅ 3/3 | us3-safety-runs.md |
| N1 (book/pay request) | 3 | ✅ 3/3 | us3-safety-runs.md |
| N2 (passport/card volunteered) | 3 | ✅ 3/3 | us3-safety-runs.md |
| N5 (edit confirmed plan) | 1 | ✅ | us3-safety-runs.md |
| C7 (PDF before confirmation) | 1 | ✅ | us3-safety-runs.md |
| N3 (visa question, grounded) | 3 (+1 inconclusive) + 1 re-check | ✅ 4/4 complete runs | polish-n3.md |
| F1 re-check (fictional hotels) | 1 | ✅ | e1-run2-final.md |
| E1 final regression (T045) | 1 | ✅ | e1-run2-final.md |

Scope note (T045): the "full fresh pass" was run as one final E1 conversation after the last push
(covering C1, C2, C4, C5-style question, C6 and F1) plus the 3-run safety scenarios above, all on
the final agent version except C1–C3/edge cases (run earlier on the same skills; only the
instructions' fictional-catalog rule and the knowledge sources changed since).

## Timings (E1)

- SC-001: first message → confirmed plan ~3 min in both E1 runs (target < 10 min) ✅
- Plan goal "≤ 10 s per update": **not met** — single changes took ~15–25 s and one-message
  multi-step requests 40–90 s in the test chat (reasoning model + sandboxed script runs).
  Not a spec requirement; recommend relaxing the plan goal or accepting it as a known limitation.

## Findings

- F1 fictional-hotel advice — fixed and re-checked ✅
- F2 holder details requested twice in one reply (once) — cosmetic
- Agent sometimes restates catalog prices in its own words (always correct)
- Built-in `web_search` is used for travel questions in addition to the two knowledge sources — instructions now require official sources; re-check cited only official e-visa pages ✅
- Test-chat streams stalled twice after the browser extension disconnected (not an agent defect)

## Credits used in testing

About 380 Copilot Credits in total (spike, C1–C3, edge cases, two E1 runs, safety runs, N3).

## Usability check (SC-006)

_Pending (T046)._ Test kit ready in [../usability/](../usability/README.md); results go in [../usability/results.md](../usability/results.md).

## Analysis (T047)

Post-implementation `/speckit-analyze`: 1 critical (early publish by `pac copilot init`, now a recorded exception in plan.md Complexity Tracking), 1 high (built-in web search — documented and instructions tightened), 3 medium, 5 low — all resolved in docs; L5 (agent restating correct catalog prices) accepted.

## Review gate (T048)

**Approved by the user on 2026-11-13** ("Approve and publish") after reviewing: the diff since
baseline `03df43a`, 119 passing unit tests, YAML validation (29 files), all conversation results
above, and the post-implementation analysis. Approved with **SC-006 (5-person usability check,
T046) still open** — the user chose to publish before it; SC-006 remains unverified.

## Publish (T049)

- 2026-11-13 18:53 (Baku time): `pac copilot publish --bot <agent-id>
  --environment https://<your-org>.crm.dynamics.com/`, after the user's explicit final
  confirmation ("Yes, publish now").
- PAC 2.15.1 started the publish job, then crashed while polling its status
  (`System.ArgumentException: Invalid response format (Parameter 'rawResponse')` in
  `CopilotPublishStatus.FromJsonString`). Per the
  publish skill, no second publish was attempted.
- Verified in Copilot Studio (read-only): status **Published**, "Last published: 6:54 PM, 11/13/26",
  Publish button no longer shows pending changes. The live agent has the full instructions,
  3 skills (baku-trip-catalog, confirm-trip-plan, export-trip-plan-pdf) and 2 knowledge sources.
- Final `pac copilot pull`: no changes; YAML validation passes.
- Known gap: **SC-006** (5-person usability check, T046) not done before publishing.
