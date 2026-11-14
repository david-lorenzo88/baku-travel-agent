# SharePoint seed data for the Baku Travel app

The agent's catalog (`skills-src/_shared/catalog.json`) — 5 fictional hotels and 6 real activity
types with indicative AZN prices and Wikimedia Commons photos — as CSV files you can turn into
SharePoint lists. Column names match the lists the app generator created at the Baku AI Summit
(see [the data model](../../docs/managed-apps/04-baku-travel-app.md#where-the-data-lives)).

| File | List | Columns |
|---|---|---|
| [Hotels.csv](Hotels.csv) | Hotels | Title, District, PricePerPersonNight, Description, PhotoUrl, PhotoCredit |
| [Activities.csv](Activities.csv) | Activities | Title, Category, Description, Price, Duration, Location, PhotoUrl, PhotoCredit |

The generated app's Hotels list also has `Stars`, `GuestRating`, `Amenities` and `ImageKey`
(and Activities has `ImageKey`); the generator can add and fill those itself.

## Create the lists

In your SharePoint site: **+ New → List → From CSV** → upload the file → set the price column to
**Currency** (or Number with 2 decimals) and `PhotoUrl` to **Hyperlink or Picture** (or single
line of text) → **Create**. Repeat for the second file. Then tell the app generator to use these
lists (see [Build it yourself](../../docs/managed-apps/05-build-it-yourself.md)).

## Notes

- Prices are **AZN** sample prices. The app we built at the summit used generated **USD** test
  data instead — tell the generator which currency you want.
- Hotel names are **fictional**; activities are real types of tours with indicative prices.
- Photos are Wikimedia Commons images under Creative Commons licenses; keep `PhotoCredit` visible
  where photos are shown. See [ATTRIBUTION.md](../../ATTRIBUTION.md).
- Regenerate after changing the catalog: `python tools/export_sharepoint_seed.py`.
