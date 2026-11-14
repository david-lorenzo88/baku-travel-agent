# Usability check — facilitator guide (T046, SC-006)

**Goal**: show that first-time users can plan a full trip with Baku Travel Planner without help.
**SC-006**: 90% of first-time test users complete the full flow (hotel → confirmation → PDF)
without help. With 5 testers, that means **all 5 must succeed**.

Kit: this guide · [tester-cards.md](tester-cards.md) (one card per tester) ·
[observation-sheet.md](observation-sheet.md) (one copy per tester) · [results.md](results.md).

---

## 1. Before the sessions

**Recruit 5 testers** who have never seen or heard a demo of the agent. Aim for a mix: at least one
person who rarely uses chat assistants and at least one who travels often.

**Decide where testers will chat.** The agent is published, but it hasn't been added to Teams or
Microsoft 365 Copilot (out of scope for v1). The simplest setup:

- **In person**: the tester sits at your computer, signed in to Copilot Studio, on the agent's
  **Preview** tab.
- **Remote**: share your screen in Teams and give the tester control of the browser tab with the
  Preview chat.

Either way, the tester types; you only watch.

**Per session, check:**

- [ ] Agent opens in Copilot Studio → **Preview**, status **Published**
- [ ] Click **New chat** so the tester starts from the greeting
- [ ] Debug mode **off** (the tester shouldn't see the agent's "thought process")
- [ ] A timer ready (phone stopwatch is fine)
- [ ] A fresh copy of the observation sheet, and the tester's card
- [ ] Budget: about **50 Copilot Credits per session** (≈ 250 for all five)

## 2. Introduce the session (2 minutes) — read aloud

> "Thanks for helping. We're testing a travel-planning assistant, not you — there are no wrong
> answers. I'll give you a card with a short trip scenario. Please complete it using the
> assistant, thinking out loud as you go. I'm not allowed to help, so if you get stuck, just tell
> me what you're thinking and try what seems right. Please use only the details on the card —
> don't type any of your own personal information. The conversation is logged in our test
> environment. It should take about 10 minutes."

Hand over the card and start the timer when they start typing.

## 3. During the task (≈ 10–15 minutes)

**You may**: re-read the card aloud; say "please try what you think is right"; restart the chat
**once** if the agent visibly freezes (no reply for 2 minutes) — note it as a technical incident.

**You may not**: suggest words to type, point at buttons, explain what the agent means, or confirm
whether they're "doing it right". If the tester asks you directly, reply: "What would you try?"

**Counts as help (= task not completed without help)**: any hint about what to type, where to
click, or what the agent expects; taking over the keyboard; telling them they're done or not done.

**Stop** when the tester has the PDF, gives up, or reaches **20 minutes**.

Note on the sheet, as it happens:

- time of first message, time the plan is **confirmed** (reference shown), time the PDF appears;
- every moment of hesitation, confusion, re-phrasing or error, with what the agent showed;
- any wrong or surprising agent behavior (wrong total, invented option, asking for personal data,
  confirming without an explicit yes).

## 4. After the task (5 minutes)

1. **Download the PDF** from the chat and keep it with the sheet (it holds only fictional data).
2. **Check the totals** with the price table below (the formula on the observation sheet).
3. Ask the three questions on the observation sheet and write down the answers word for word.
4. Click **New chat** before the next tester.

## 5. Price table for checking totals (catalog version 2026-11-13)

| Hotel | Neighborhood | AZN per person per night |
|---|---|---:|
| Caspian Courtyard Hotel | Old City (İçərişəhər) | 60.00 |
| Fountain Square Suites | Fountain Square | 85.00 |
| Boulevard Bay Hotel | Baku Boulevard | 110.00 |
| Flame View Residence | Flame Towers / Highland Park | 140.00 |
| Port Baku Lofts | Port Baku | 95.00 |

| Activity | Duration | AZN per person |
|---|---|---:|
| Old City walking tour | 3 hours | 25.00 |
| Gobustan & mud volcanoes day trip | 7 hours | 95.00 |
| Ateshgah & Yanar Dag evening tour | 4 hours | 70.00 |
| Baku Boulevard boat ride | 40 minutes | 15.00 |
| Heydar Aliyev Center visit | 2 hours | 20.00 |
| Azerbaijani cooking class | 3 hours | 65.00 |

**Grand total** = hotel price × travelers × nights + Σ (activity price × travelers).
Nights = check-out date − check-in date.

## 6. When all five are done

Fill in [results.md](results.md), then in `tasks.md` mark **T046** done and add the outcome to
`test-results/summary.md` (section "Usability check (SC-006)"). If SC-006 fails, list the
sticking points in results.md — they become the input for the next `/speckit-specify` round.
