# 5. Build it yourself

Reproduce the [Baku Travel app](04-baku-travel-app.md) in your own tenant, in about 30–60 minutes.

**Before you start**: your admin has done [3. Enable it in a fresh tenant](03-enable-in-a-fresh-tenant.md)
— app creation allowed, Copilot Credits for your environment, and runtime coverage for whoever
will use the app.

## 1. Choose: let the generator create the site, or prepare it

At the Baku AI Summit the generator **created the site and lists itself** (see
[the data model](04-baku-travel-app.md#where-the-data-lives)) — the simplest path: skip to step 2.
Microsoft notes, though, that creating a new site "isn't available in all preview releases". If
it isn't offered to you, or you want the same data as the agent in this repo, prepare the site:

1. SharePoint → **+ Create site** → **Team site** (or Communication site) → name it
   **Baku Travel** → note its URL, e.g. `https://<tenant>.sharepoint.com/sites/BakuTravel`.
2. *Optional — same data as this repo*: create the **Hotels** and **Activities** lists (same
   column names as the generated app) from the CSV files in [`managed-app/sharepoint-seed/`](../../managed-app/sharepoint-seed/README.md)
   (**+ New → List → From CSV**). Otherwise the app generator fills the lists with test data it
   finds about Baku.

Who can use the data: everyone who'll run the app needs at least **read** access to the catalog
lists and **edit** access to the lists where trips are saved — sharing the app doesn't grant it.

## 2. Create the app

1. Open <https://copilotstudio.microsoft.com>, turn on **New experience** on Home.
2. **Apps (Preview) → New app** (or the **App** tile on Home).
3. Paste the prompt. If you prepared a site, add a line pointing at it:

```text
Create a travel agent app for helping users traveling to Baku. I need a section to choose hotels,
find activities. Then we want to create a travel plan, where I can add the hotel and several
activities.

Every hotel must have a price per person and per day, when you add the hotel, it must calculate the
total price of the stay and show it in the plan.

For activities, we want to show price, description, name, photos (you can use stock photos).

When we add hotel or activity to the plan, you must recalculate the grand total.

Then a checkout page where we can add holder data and confirm the plan.

Finally, a confirmation page that shows all plan detail with all the information.

Use a new sharepoint site to hold all the information, add test information you can find on the
internet, eberything about Baku.
```

> If you prepared the site in step 1, replace the last paragraph with: *"Store all the information
> in the SharePoint site https://&lt;tenant&gt;.sharepoint.com/sites/BakuTravel. Use the Hotels and
> Activities lists if they exist; create a TravelPlans list for confirmed trips."*

4. **Answer the clarifying questions** Copilot Studio asks (for example: which SharePoint site,
   currency, whether the number of travelers is part of the plan). For consistency with the agent,
   answer **AZN** for currency and ask for a **number of travelers** and **check-in/check-out
   dates** in the plan.
5. **Approve the SharePoint connection** when asked; you'll sign in with your own account.

## 3. Test it in preview

Use the preview pane. If you imported the seed lists, these are the expected numbers; with
generated test data (as in [our app](04-baku-travel-app.md), in USD), check the same formulas:
stay = price × travelers × nights, grand total = stay + Σ(activity price × travelers).

| Check | Expected (with the seed data) |
|---|---|
| Hotels list shows prices per person per night | Caspian Courtyard Hotel AZN 60.00, … |
| Add hotel, 2 travelers, 10–14 March 2027 | Stay total **AZN 480.00** (60 × 2 × 4) |
| Add Old City walking tour | Grand total **AZN 530.00** (480 + 25 × 2) |
| Add Gobustan day trip | Grand total **AZN 720.00** (530 + 95 × 2) |
| Remove an activity | Grand total recalculated |
| Checkout with holder details, confirm | Confirmation page with all plan details |
| SharePoint | A new row in **TravelPlans** with holder, dates, hotel, `ActivitiesDetail` and totals |

Use **fictional** holder details (e.g. Ana Smith · ana@example.com · +34 600 000 000).

If something's wrong, describe it in the chat — e.g. *"the stay total must be price per person per
night × travelers × nights"* — or attach a screenshot and annotate it.

## 4. Add the trips screen

Second prompt:

```text
add a new screen to list and view the current trips
```

Check that saved trips are listed and that opening one shows its hotel, activities and totals.

## 5. Publish and share

1. **Publish** — creates the stable version users run. Later changes need a new publish.
2. **Share** with people, Microsoft 365 groups or security groups ("Play" = run, "Edit" = change
   source). Sharing doesn't grant edit rights or SharePoint access.
3. Grant those users access to the **SharePoint site/lists**.
   **Privacy**: `TravelPlans` holds every holder's name, email and phone, and anyone with read
   access to that list can see all trips. For real use, restrict it (e.g. item-level permissions
   "read/edit items that were created by the user" in the list's advanced settings).
4. Make sure they have **runtime coverage** (Power Apps Premium or the spending policy), or
   they're blocked after 20 operations or 5 minutes.
5. Users open the app from <https://managedapps.cloud.microsoft> or the shared link; on first run
   they may need to consent to the SharePoint connection.

Source: [publish and share an app](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/publish-share-app)

## Costs

- **Building**: generating, previewing and every refinement prompt consume Copilot Credits from
  your environment (no published rate; watch the counter and the admin center).
- **Running**: 0.1 Copilot Credit per API call under a spending policy (asset loads, connector
  calls, publishes), or covered by Power Apps Premium.

## Troubleshooting

| Symptom | Fix |
|---|---|
| No **App** tile / Apps (Preview) | Turn on New experience; ask the admin to check app creation spaces and routing rules |
| "Can't create site" or no new site | Create the SharePoint site yourself (step 1) and point the prompt at it |
| Users see empty lists | Give them access to the SharePoint site/lists |
| Users blocked after a few minutes | They have no runtime coverage — Power Apps Premium or spending policy |
| SharePoint not offered as a data source | Connector policy blocks it — admin checks environment group and data policies |
| Guests can't open the app | Known preview issue |
