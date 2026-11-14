# C1 — Spec US1 example (hotel + stay total)

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview, unpublished draft) · **Result**: ✅ PASS

| # | Traveler | Agent (summary) | Check |
|---|---|---|---|
| 1 | "Hi, I'm planning a trip to Baku." | Asked for check-in, check-out and number of travelers in one message | US1-1 ✅ |
| 2 | "10 to 14 March 2027, two of us." | Listed 5 hotels, each with photo (rendered), neighborhood, description, AZN price per person per night | US1-2 ✅ (3–5 options) |
| 3 | "The first one, please." | Plan: Caspian Courtyard Hotel · AZN 60.00 · 2 travelers × 4 nights · AZN 480.00; Grand total AZN 480.00; "Would you like to see some activities in Baku?" | US1-3 ✅, US1-5 ✅ |

Observations: price line and description ran together in one paragraph (single newlines) — fixed
in commit 7590af3 (blank lines between blocks) and verified in us1-edge-cases.md.
