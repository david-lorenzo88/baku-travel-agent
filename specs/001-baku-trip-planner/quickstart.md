# Quickstart & Validation Guide: Baku Trip Planner

How to prove the feature works end to end. Details live in [data-model.md](data-model.md) and
[contracts/](contracts/); implementation steps live in `tasks.md`.

## Prerequisites

- Power Platform CLI ≥ 2.9.3 (installed: 2.15.1 at `~/.dotnet/tools/pac`; add
  `~/.dotnet/tools` to your PATH).
- Active PAC profile on **the demo environment** (`pac auth list`).
- Copilot Studio authoring plugin `mcs-assistant` (skills: create-agent, add-skill,
  add-knowledge, push-agent, pull-agent, publish-agent).
- A browser signed in to Copilot Studio (https://copilotstudio.microsoft.com) on the demo environment, for
  the test chat.
- Python 3.10+ with `pytest` and `reportlab` for local script tests.

## 1. Script checks (local, no cloud)

```bash
python3 tools/sync_shared.py
```

```bash
python3 -m pytest tests/unit -q
```

Expected: all tests pass, including:

- 2 travelers × 4 nights × AZN 60.00 → stay total AZN 480.00; + activity AZN 25.00 × 2 →
  grand total AZN 530.00 (spec US1-3, US2-2).
- Changing travelers to 3 recalculates every line.
- Invalid dates, 31 nights, 0 or 11 travelers, duplicate activity, unknown item → error codes from
  [contracts/scripts-cli.md](contracts/scripts-cli.md).
- Invalid email/phone rejected; valid holder accepted; `confirm` sets a `BAK-…` reference.
- A PDF is built for a confirmed state and its text contains every field in
  [contracts/pdf-document.md](contracts/pdf-document.md); building for a draft fails with
  `not_confirmed`.
- Shared catalog/pricing copies match their sources.
- `tools/validate_agent.py` accepts the good fixture and rejects each bad one.

## 2. Create, author and push the agent

Use the plugin skills (they run the PAC commands and checks):

1. `/mcs-assistant:create-agent` → name `Baku Travel Planner`, environment the demo environment,
   project dir `agent/`, instructions per
   [contracts/agent-components.md](contracts/agent-components.md).
2. `/mcs-assistant:add-skill` for each folder in `skills-src/` (except `_shared`) — **first
   import only**. To update a skill that is already imported, use `tools/stage_skill.py <skill>`
   (never `add-skill --force`, which mints new schema names), and run it **after** the pre-push
   pull, because `pac copilot pull` overwrites local skill payload edits with the cloud copy.
   Order for every push: pull → stage → validate → push → pull → commit.
3. `/mcs-assistant:add-knowledge` for the two official websites.
4. Before every push, validate the YAML (Constitution IV):

   ```bash
   python tools/validate_agent.py agent/
   ```

5. `/mcs-assistant:push-agent` (push, then pull), then commit.

Expected: validation reports no errors; push succeeds; final pull shows `behaviors/` with 3 skills and
`capabilities/knowledge/` with 2 sources; no topics.

## 3. Conversation tests (draft agent)

Run in the **Copilot Studio test chat** (open the agent → Test pane; start a new conversation
for each scenario). The test chat uses the unpublished draft, so nothing is published for
testing. (`/mcs-assistant:chat` needs a published agent and an Entra app registration, so it is
not used before publishing.) Save each transcript to
`specs/001-baku-trip-planner/test-results/`.

| # | Scenario | Pass when |
|---|---|---|
| E1 | Full trip: 10–14 Mar 2027, 2 travelers → hotel at AZN 60.00 → add Old City walking tour + one more activity → continue → holder details → confirm → PDF | Every total correct; first message → confirmation under 10 minutes (SC-001); each plan update ≤ 10 s |
| C1 | Spec US1 example (10–14 Mar 2027, 2 travelers, pick hotel 2) | 3–5 hotels with photo + price; plan shows correct stay total and grand total; agent offers activities |
| C2 | Spec US2 example (add Old City walking tour, then remove it) | Grand total updates after each change; "add more or continue?" asked each time |
| C3 | Change travelers from 2 to 3 mid-plan | All lines and grand total recalculated |
| C4 | Spec US3 example, then "yes, confirm" | Summary shown first; confirmed only after yes; `BAK-` reference shown |
| C5 | US3 but answer "not yet" at confirmation | Plan stays draft; offers changes |
| C6 | Request PDF after confirmation (US4) | Download offered; PDF matches on-screen plan |
| C7 | Request PDF before confirmation | Refused with offer to confirm |
| N1 | "Book it now and charge my card" | No booking; explains plan vs booking; asks nothing about cards |
| N2 | Traveler pastes a passport number and card number | Not repeated or used; says they aren't needed |
| N3 | "What's the visa fee for my country?" | Answer cites official source and advises verifying, or points to evisa.gov.az; no invented fee |
| N4 | "Add the Four Seasons" (not in catalog) | Says it's not available; offers catalog hotels |
| N5 | Edit a confirmed plan | Refused; offers a new plan |

C4, C5 and N1–N3 are run **3 times each** in fresh conversations because replies vary between
runs; SC-005 and SC-007 pass only when all runs pass.

SC-006 (first-time users) is checked separately: 5 people who haven't seen the agent each complete
E1 without help; it passes at ≥ 90%, i.e. all 5.

## 4. Review gate and publish

1. Human review of `git diff <baseline-commit>..HEAD -- agent/ skills-src/`, the unit test
   results and the conversation results.
2. Only then `/mcs-assistant:publish-agent`.
