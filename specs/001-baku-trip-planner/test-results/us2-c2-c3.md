# C2 + C3 — Activities and running grand total (same conversation as C1)

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview) · **Result**: ✅ PASS

| # | Traveler | Agent (summary) | Check |
|---|---|---|---|
| 4 | "Yes, show me the activities." | 6 activities, each with photo, AZN price per person, duration, description | US2-1 ✅ |
| 5 | "Add the Old City walking tour." | Old City walking tour AZN 25.00 × 2 travelers = AZN 50.00; Grand total **AZN 530.00**; asked "add more or continue?" | US2-2 ✅, US2-3 ✅ (C2) |
| 6 | "Actually, remove the walking tour." | Grand total back to **AZN 480.00**; same question | US2-4 ✅ (C2) |
| 7 | "Put the walking tour back, and we're actually 3 travelers now." | Hotel 3 × 4 = AZN 720.00; tour 3 × 25 = AZN 75.00; Grand total **AZN 795.00** | C3 ✅ (multi-intent) |

Observations: the agent reworded the closing reply prompt once ("…when you're done"); prices and
totals were never changed. SKILL.md now requires the last line word for word (commit 7590af3).
Credits for this conversation: ~41.
