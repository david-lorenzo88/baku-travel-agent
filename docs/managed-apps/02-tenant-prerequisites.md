# 2. Tenant prerequisites

Checked against Microsoft Learn in November 2026 (preview).

## At a glance

| Who / what | Needs |
|---|---|
| **Tenant** | Commercial cloud, eligible for Copilot Managed Runtime (no install needed) |
| **Makers** (build apps in Copilot Studio) | Access to Copilot Studio; **Copilot Credits** for their environment; no Microsoft 365 Copilot license required |
| **App users** (run the app) | **Power Apps Premium** license, *or* inclusion in a Microsoft 365 admin center **spending policy** for Copilot Managed Runtime |
| **Environment** | Created automatically: each maker's **personal developer environment** (managed, no Dataverse by default) |
| **Data** | A **SharePoint site** the users can access (for this demo), and connector policy allowing SharePoint |
| **Admins** | Global Admin or Power Platform Admin (app creation settings); Global Admin or Billing Admin (spending policies) |

## Makers: building costs Copilot Credits

- Generating, previewing and testing an app consumes **Copilot Credits**, billed through Copilot
  Studio environment billing — from the first prompt, not only after publishing.
- Credits come from the Power Platform admin center (**Licensing → Copilot Studio → Manage Copilot
  Credits**, per environment), from pay-as-you-go, or — if the environment has moved there — a
  Microsoft 365 admin center spending policy. **Manage capacity** in the Power Platform admin
  center shows which applies. By default an environment with no allocation draws from tenant
  capacity.
- Developer environments (where apps are built) moved to usage-based billing on 1 September 2026.
- No Microsoft 365 Copilot license is required to build. Whether a Copilot Studio user license or
  trial is required isn't documented beyond "access to Copilot Studio".

Sources:
[get started](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/get-started) ·
[licensing FAQ](https://learn.microsoft.com/microsoft-365/admin/manage/apps/licensing-faq) ·
[harness billing](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/billing-credit-overview) ·
[manage harness usage](https://learn.microsoft.com/power-platform/admin/manage-usage-github-copilot-harness)

## App users: running costs need coverage

Running an app is billed separately from building it:

- **Option A — Power Apps Premium** license per user.
- **Option B — Microsoft 365 admin center spending policy** that selects the **Copilot Managed
  Runtime** service. Usage is metered at **0.1 Copilot Credit per API call** — each static asset
  loaded at launch, each connector call and each publish counts.

Not enough on their own: Microsoft 365 / Dynamics 365 Power Apps use rights (E3/E5), a Microsoft
365 Copilot license, or Copilot Studio environment credits. **Users without coverage are blocked
after 20 operations or 5 minutes.**

Source: [licensing and credits](https://learn.microsoft.com/microsoft-365/admin/manage/apps/licensing-credits)

## Environment

Apps are built in each maker's **personal developer environment**, created automatically through
environment routing. It's a managed environment **without Dataverse** by default — you don't need
to create one. Makers who only build CMR apps don't trigger premium license auto-claim.

Source: [default environment routing for CMR](https://learn.microsoft.com/power-platform/admin/default-environment-routing-copilot-managed-runtime) ·
[apps FAQ](https://learn.microsoft.com/microsoft-365/admin/manage/apps/faq-about-apps)

## Connectors and data

- The default environment group's **advanced connector policy** allows 18 Microsoft connectors,
  **including SharePoint**. Open-ended actions (for example SharePoint "Send an HTTP request") are
  blocked.
- If the environment group has an advanced connector policy and **Advanced connector policies
  only** is off, classic data policies apply too — the most restrictive wins. Make sure SharePoint
  isn't blocked.
- **SharePoint permissions are separate**: sharing the app doesn't grant access to the site or
  lists. App users need at least read access to catalog lists and edit access to the lists where
  trips are saved.

Sources: [governance](https://learn.microsoft.com/microsoft-365/admin/manage/apps/governance) ·
[publish and share](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/publish-share-app)

## Not documented (as of November 2026)

- Supported regions beyond "eligible tenants in the commercial cloud", and whether the generative
  AI / data movement settings matter.
- The exact credit cost of generating an app.
- Solution-based ALM (export/import, pipelines) for apps built in Copilot Studio.
