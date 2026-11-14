# Contract: Trip plan PDF — FR-020, FR-021, FR-022

File name: `Baku-Trip-<reference>.pdf` · Page size A4 · Only for `status = confirmed`.

## Content (in order)

1. **Header**: "Baku Trip Plan", confirmation reference, confirmation date/time (Baku time).
2. **Plan holder**: full name, email, phone.
3. **Trip**: check-in, check-out, nights, travelers.
4. **Hotel**: bundled photo, name, neighborhood, price per person per night, quantity label,
   stay total.
5. **Activities** (one block each, or "No activities selected"): bundled photo, name, price per
   person, quantity label, line total.
6. **Totals table**: same rows and grand total as the on-screen plan, currency AZN.
7. **Footer note**: "Sample prices from the agent's catalog (version <catalog_version>) at the time
   of confirmation. This is a trip plan, not a booking; no reservation or payment has been made."
8. **Photo credits**: author and license for each photo used.

## Rules

- Every value in sections 1–6 must equal the on-screen final plan (SC-004).
- No other personal data appears in the PDF.
- A missing bundled photo is replaced by a grey placeholder box labelled with the item name and
  reported in the script output; the PDF is still produced.
