# Contract: What the traveler sees (Markdown rendering)

The scripts produce the Markdown; the agent shows it **verbatim** and may add one short sentence
before it. All amounts: `AZN 1,234.50` style (thousands separator, 2 decimals).

## Hotel option (repeated 3–5 times) — FR-005

```markdown
### 1. Caspian Courtyard Hotel
![Courtyard in Baku Old City](https://upload.wikimedia.org/...jpg)
*Old City (İçərişəhər)* · **AZN 60.00 per person per night**
Restored caravanserai-style rooms a short walk from the Maiden Tower.
```

Followed by: `Reply with the number or name of the hotel you'd like.`

## Activity option (repeated 3–6 times) — FR-009

```markdown
### 1. Old City walking tour
![Maiden Tower, Baku](https://upload.wikimedia.org/...jpg)
**AZN 25.00 per person** · 3 hours
Guided walk through İçərişəhər: Maiden Tower, Shirvanshahs' Palace and caravanserais.
```

Followed by: `Reply with the number or name of an activity to add it, or say "continue".`

## Plan block — FR-014 (shown after every change)

```markdown
**Your Baku trip plan** (draft)
10 Mar 2027 → 14 Mar 2027 · 4 nights · 2 travelers

| Item | Price | Qty | Total |
|---|---:|---|---:|
| 🏨 Caspian Courtyard Hotel | AZN 60.00 | 2 travelers × 4 nights | AZN 480.00 |
| 🎟️ Old City walking tour | AZN 25.00 | 2 travelers | AZN 50.00 |
| **Grand total** | | | **AZN 530.00** |

_Sample prices from the agent's catalog. This is a plan, not a booking._
```

Next-step line, by state:

- after hotel selected → `Would you like to see some activities in Baku?`
- after activity added/removed → `Would you like to add more activities, or continue to confirmation?`

## Confirmation summary — FR-018

Plan block (status `ready to confirm`) + holder block:

```markdown
**Plan holder**: Ana Smith · ana@example.com · +34 600 000 000

Shall I confirm this plan? Confirming creates a trip plan with a reference. It doesn't book
hotels or activities and no payment is taken.
```

## Final plan — FR-019

Plan block with status `confirmed`, plus:

```markdown
**Confirmation reference**: BAK-20261113-7KQ2MX · confirmed 13 Nov 2026, 16:40 (Baku time)
**Plan holder**: Ana Smith · ana@example.com · +34 600 000 000

Would you like me to export this plan as a PDF?
```

## Error messages

One sentence saying what's wrong and what to do, e.g.
`Check-out must be after check-in. What's your check-out date?` — never a stack trace or JSON.

## Channel note

Inline images are verified in the Copilot Studio test chat (spike). If a channel strips images,
the scripts switch to a `[View photo](url)` link via a `--photo-style link` flag.
