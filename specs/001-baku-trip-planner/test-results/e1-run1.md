# E1 run 1 — full trip (covers C4 run 1 and C6 run 1)

**Date**: 2026-11-13 · **Where**: Copilot Studio test chat (Preview, unpublished draft)
**Result**: ✅ PASS

Fictional test holder: Ana Smith · ana@example.com · +34 600 000 000.

| # | Time | Traveler | Agent (summary) | Check |
|---|---|---|---|---|
| 1 | 17:38 | "Hi! I'm planning a trip to Baku from 10 to 14 March 2027 for 2 people." | 5 hotels with photos and AZN prices | US1 ✅ |
| 2 | 17:39 | "Caspian Courtyard Hotel, please. Then show me activities." | Selected hotel, listed 6 activities with photos | US1/US2 ✅ |
| 3 | 17:40 | "Add the Old City walking tour and the Gobustan day trip." | Hotel 480.00 + tour 50.00 + Gobustan 190.00 = **AZN 720.00**; asked "add more or continue?" | US2 ✅ |
| 4 | 17:40 | "That's all, let's continue to confirmation." | Asked for full name, email and phone only | US3-1 ✅ |
| 5 | 17:40 | "Ana Smith, ana@example, +34 600 000 000" | "That email address doesn't look right. Could you check it?" (asked only for the email) | US3-2 ✅ |
| 6 | 17:41 | "Sorry, it's ana@example.com" | Full summary (ready to confirm), holder line, confirm question; **not confirmed yet** | US3-3 ✅ |
| 7 | 17:41 | "Yes, confirm." | Confirmed plan, reference **BAK-20261113-VVN7ZJ**, holder, PDF offer | US3-4 ✅, FR-019 ✅ |
| 8 | 17:42 | "Yes, please export it as a PDF." | Attachment `Baku-Trip-BAK-20261113-VVN7ZJ.pdf` offered for download | US4-1/US4-2 ✅ |

**SC-001**: first message → confirmed in ~3 minutes (target < 10) ✅.
**Plan update response time**: each turn answered within the 20–30 s observation window; not
measured precisely (T045).
**SC-004 (PDF matches screen)**: ✅ The PDF generated in the cloud sandbox
(`Baku-Trip-BAK-20261113-VVN7ZJ.pdf`, 665,794 bytes, 2 pages, 3 embedded photos) was downloaded
with the user's approval and its text compared with the on-screen confirmed plan: all 24 values
(reference, confirmation time, holder name/email/phone, dates, nights, travelers, hotel and
both activities with unit prices, quantities and line totals, grand total AZN 720.00, catalog
version, "not a booking" note, photo credits) present and in contract order; no other personal
data. Azerbaijani letters (İçərişəhər) render, so the sandbox has the DejaVu font.
Credits for this conversation: ~58.
