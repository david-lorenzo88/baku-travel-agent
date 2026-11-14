# US1 edge cases + N4 (new conversation, after formatting fix)

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview) · **Result**: ✅ PASS

| # | Traveler | Agent (summary) | Check |
|---|---|---|---|
| 1 | "Plan a Baku trip for 2 people: check-in 14 March 2027, check-out 10 March 2027." | Explained check-out is before check-in; asked for the right dates | check_out_before_check_in ✅ |
| 2 | "Sorry, I meant 1 March to 5 April 2027." | 35 nights exceeds the 30-night maximum; suggested shorter ranges | stay_too_long ✅ |
| 3 | "OK, 1 to 5 March 2027 then. But we are 11 people." | "I can plan for 1 to 10 travelers. How many people are traveling?" | travelers_out_of_range ✅ |
| 4 | "Fine, 4 people." | 5 hotels with photos; price line and description now on separate lines | formatting fix ✅ |
| 5 | "Can we stay at the Four Seasons instead?" | "The Four Seasons isn't in our catalog…"; pointed to catalog hotels | N4 ✅ |

Observations: in turn 5 the agent restated two catalog prices in its own words (AZN 140.00 and
AZN 110.00 — both correct). Not a failure (no invented price), but it is outside "prices only via
script output"; watch in later runs. Credits: ~19.
