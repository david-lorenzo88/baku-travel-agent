# E1 run 2 — final regression after the last push (T045) + F1 re-check

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview, unpublished draft)
**Agent state**: instructions with fictional-catalog rule, 3 skills, 2 website knowledge sources.
**Result**: ✅ PASS

| # | Time | Traveler | Agent (summary) | Check |
|---|---|---|---|---|
| 1 | 18:34 | "Hi, I'm planning a trip to Baku, 10 to 14 March 2027, two of us." | 5 hotels with photos and AZN prices; closing prompt word for word | C1 ✅ |
| 2 | 18:35 | "Number 1." | Caspian Courtyard 2 × 4 × 60 = AZN 480.00; "Would you like to see some activities in Baku?" | C1 ✅ |
| 3 | 18:35 | "Yes. Add the Old City walking tour and the Gobustan day trip." | 480 + 50 + 190 = **AZN 720.00**; add-more-or-continue question | C2 ✅ |
| 4 | 18:36 | "Continue to confirmation. Holder: Ana Smith, ana@example.com, +34 600 000 000." | Summary (ready to confirm) + confirm question | US3 ✅ |
| 5 | 18:36 | "Before I confirm: how can I book the Caspian Courtyard Hotel directly?" | "This agent creates trip plans only… the hotels in the catalog are fictional sample data. I'm not able to suggest contacting or booking any catalog hotel or recommend booking websites." Not confirmed | **F1 fixed ✅**, C5 ✅ |
| 6 | 18:37 | "Yes, confirm." | Confirmed, BAK-20261113-2HL347 | C4 ✅ |
| 7 | 18:38 | "Yes, the PDF please." | `Baku-Trip-BAK-20261113-2HL347.pdf` offered for download | C6 ✅ |

SC-001: first message → confirmed in ~3 minutes ✅. Credits: ~51.
