# Data Model: Baku Trip Planner

**Feature**: [spec.md](spec.md) | **Date**: 2026-11-13

All money is AZN, stored as decimal strings with 2 decimals (e.g. `"60.00"`) and computed with
`decimal.Decimal`, rounding half-up. Dates are ISO `YYYY-MM-DD`, evaluated in Baku time (UTC+4).

## Catalog (static, bundled in `baku-trip-catalog/references/catalog.json`)

### Hotel

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique, `htl-` prefix, kebab-case (e.g. `htl-old-city-courtyard`) |
| `name` | string | 1–80 chars; fictional sample name |
| `neighborhood` | string | Real Baku area (e.g. Old City / İçərişəhər, Fountain Square, Baku Boulevard, Port Baku) |
| `description` | string | 1–300 chars |
| `price_per_person_per_night` | decimal string | > 0, 2 decimals |
| `photos` | Photo[] | ≥ 1 (FR-024) |

### Activity

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique, `act-` prefix, kebab-case |
| `name` | string | 1–80 chars |
| `description` | string | 1–400 chars |
| `duration` | string | Informational, e.g. `"3 hours"` |
| `price_per_person` | decimal string | > 0, 2 decimals |
| `photos` | Photo[] | ≥ 1 (FR-024) |

### Photo

| Field | Type | Rules |
|---|---|---|
| `url` | string | Public HTTPS URL, verified HTTP 200 at implementation time (chat rendering) |
| `file` | string | File name of the bundled copy in `export-trip-plan-pdf/assets/photos/` (PDF) |
| `alt` | string | Alt text, 1–120 chars |
| `credit` | string | Author and license, e.g. `"Jane Doe, CC BY-SA 4.0, Wikimedia Commons"` |
| `source_page` | string | Commons file page URL (license and attribution details) |

Catalog-level fields: `currency: "AZN"`, `catalog_version` (date string), `sample_data: true`.
Catalog size for v1: 5 hotels, 6 activities (FR-004 shows 3–5 hotels; FR-008 shows 3–6
activities).

## Conversation state (carried as Plan State JSON; see [contracts/plan-state.schema.json](contracts/plan-state.schema.json))

### TripDetails

| Field | Type | Rules (FR-001–FR-003) |
|---|---|---|
| `check_in` | date | Not before today (Baku time) |
| `check_out` | date | After `check_in`; `nights` ≤ 30 |
| `travelers` | integer | 1–10 |
| `nights` | integer | Derived: `check_out − check_in` in days |

### PlanLine

| Field | Type | Rules |
|---|---|---|
| `kind` | `"hotel"` \| `"activity"` | |
| `item_id` | string | Must exist in the catalog |
| `name` | string | Copied from catalog at pricing time (display only) |
| `unit_price` | decimal string | From catalog, never from input |
| `quantity` | integer | Hotel: `travelers × nights`; activity: `travelers` |
| `quantity_label` | string | e.g. `"2 travelers × 4 nights"` |
| `line_total` | decimal string | `unit_price × quantity` (FR-006, FR-010) |

### TripPlan

| Field | Type | Rules |
|---|---|---|
| `schema_version` | `"1"` | |
| `catalog_version` | string | Catalog used for this pricing |
| `currency` | `"AZN"` | FR-015 |
| `trip` | TripDetails | Required before any item |
| `hotel_id` | string \| null | At most one (FR-007) |
| `activity_ids` | string[] | Unique (FR-011); allowed only when `hotel_id` is set |
| `lines` | PlanLine[] | Recomputed on every call; inputs are ignored |
| `grand_total` | decimal string | Sum of `line_total` (FR-013) |
| `status` | `"draft"` \| `"confirmed"` | |
| `holder` | PlanHolder \| null | Required when `confirmed` |
| `confirmation` | Confirmation \| null | Set only when `confirmed` |

**Authority rule**: only `trip`, `hotel_id`, `activity_ids`, `status`, `holder` and `confirmation`
are inputs. `lines`, `grand_total`, names and prices are always recomputed from the catalog, so an
edited or stale value in the state can't change a total.

### PlanHolder (collected only at confirmation — Constitution III)

| Field | Type | Rules (FR-016, FR-017) |
|---|---|---|
| `full_name` | string | 2–100 chars; letters (any script), spaces, `-`, `'`, `.` |
| `email` | string | Basic address format `local@domain.tld`, ≤ 254 chars |
| `phone` | string | Optional leading `+`; 7–15 digits after removing spaces, `-`, `(`, `)` |

No other personal fields exist in the model. Passport/ID, card and bank fields are not
representable.

### Confirmation

| Field | Type | Rules |
|---|---|---|
| `reference` | string | `BAK-YYYYMMDD-XXXXXX` (6 chars from an unambiguous base32 alphabet) |
| `confirmed_at` | datetime | ISO 8601 with `+04:00` offset |

### PlanDocument (PDF)

Generated from a `confirmed` TripPlan; contents defined in
[contracts/pdf-document.md](contracts/pdf-document.md). Not stored after the session.

## State transitions

```text
(empty) ──set trip──▶ draft(trip) ──select hotel──▶ draft(hotel) ──add/remove activity──▶ draft(hotel, activities)
   ▲                     │  ▲                          │   ▲                                   │
   └── new plan ─────────┘  └── change trip/hotel ─────┘   └────── change trip/hotel/acts ─────┘
                                                                                               │
draft(hotel, ≥0 activities) ──holder valid + explicit "confirm"──▶ confirmed ──▶ PDF export (any number of times)
confirmed ──any edit request──▶ rejected (offer "start a new plan")
```

- `set trip` with changed dates/travelers on an existing draft recalculates all lines (edge case).
- Removing the hotel is not offered; replacing is (FR-007).
- `confirmed` is terminal for edits (edge case "change after confirmation").
