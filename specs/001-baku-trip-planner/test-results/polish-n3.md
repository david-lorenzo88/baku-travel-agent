# N3 — visa questions (after adding knowledge sources)

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview)
Knowledge sources accepted by the platform: https://evisa.gov.az, https://azerbaijan.travel.
Observed: the agent also uses the harness's built-in **web_search** tool for these questions.

| Run | Question | Agent | Result |
|---|---|---|---|
| 1 | "What's the visa fee for my country? I'm from Spain." | Fee and fee-waiver details with citations (incl. "Countries Eligible for e-Visa | Republic of Azerbaijan Official…" +2); link to evisa.gov.az; "Always verify current fees and requirements there before travelling." | ✅ |
| 2 | "I'm a US citizen. Do I need a visa for Azerbaijan, and how long does the e-visa take to process?" | Grounded, cited answer (e-visa via evisa.gov.az, 3 working days / 3-hour urgent, $20 state + $9 service fee — same figures as run 1). The test-chat stream stalled before the closing lines after a browser-extension disconnect | ⚠️ inconclusive (no verify advice seen) |
| 3 | "How much does an Azerbaijan e-visa cost for a German citizen?" | First attempt stalled after web_search (browser disconnect); retried in a fresh chat: fees and processing with citations, link to https://evisa.gov.az, "Always check the official portal before travel, as fees and rules may change." | ✅ |
| 4 | "I have a Brazilian passport. What's the visa situation for visiting Baku?" (replaces inconclusive run 2) | Cited answer (official e-visa portal +2), requirements, link to https://evisa.gov.az, "always verify the latest rules there before you travel" | ✅ |

**Totals**: 3 complete passes (runs 1, 3, 4), 1 inconclusive (run 2, UI stall), 0 failures; no invented fees — every fee figure carried a citation.

Note: run 2 and run 3 gave slightly different validity wording ("90 days, stay up to 30" vs "single entry valid for 30 days stay"), both cited. Travelers are always told to verify on evisa.gov.az.

## Re-check after the web-search rule (T047 fix H1)

Instructions now require official government/tourism sources when the agent searches the web.

| Run | Question | Agent | Result |
|---|---|---|---|
| 5 | "I'm Canadian. Do I need a visa for Baku and what does it cost?" | Cited answer; all 3 citations are official e-visa pages ("Countries Eligible for e-Visa", "About E-Visa", "Conditions for Issuing Electronic Visas" — Republic of Azerbaijan Official Electronic Visa portal); "Always verify the latest requirements at evisa.gov.az before you travel, as rules can change." | ✅ |
