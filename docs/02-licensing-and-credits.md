# 2. Licensing and Copilot Credits

> Licensing changes often. Everything below was checked against Microsoft Learn in **November
> 2026**; follow the links for the current terms. Where the documentation is silent or
> contradictory, it says so.

## 1. Which Copilot Studio "experience" this demo uses

This agent is a **CLI-authored agent** (`pac copilot init --authoring-mode cli-copilot`) that runs
on the **Microsoft Copilot harness** — the agentic-loop runtime of the new Copilot Studio
experience (skills, built-in Python sandbox and file creation, built-in web search). In the Power
Platform admin center its harness shows as "GitHub Copilot". Microsoft lists the new experience as
a **production-ready preview** (What's new, June 2026); no GA announcement was found.

- New experience and harness FAQ: <https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/faqs-copilot-harness>
- What's new: <https://learn.microsoft.com/microsoft-copilot-studio/whats-new>

This matters because the harness is **billed differently** from classic (standard harness) agents.

## 2. Ways to get Copilot Credits

| Option | How it works | Good for |
|---|---|---|
| **Copilot Studio capacity pack** (prepaid) | Tenant license, **25,000 Copilot Credits per pack per month**; buy several; unused credits **don't roll over**. Assign credits to environments in the admin center. | Steady use, many agents |
| **Pay-as-you-go** | Link the environment to a **billing plan** backed by an Azure subscription. No commitment; billed monthly for credits used, **USD 0.01 per credit**. Production and sandbox environments only. | Demos, pilots, unpredictable use |
| **Prepurchase plan (P3)** | One-year pool of Copilot Credit Commit Units bought in the Azure portal; needs a pay-as-you-go billing policy. | Larger committed use with discount |
| **Copilot Studio trial** | Self-service trial license; can be extended 30 days after expiry; a trial user can build and test but **can't publish**. Admins can block self-service sign-up. Initial length not documented. | Kicking the tyres |

Sources:
[capacity packs](https://learn.microsoft.com/copilot/implement/copilot-capacity-packs) ·
[billing and licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) ·
[buy credits for the new experience](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/billing-manage-buy-credits) ·
[pay-as-you-go meters](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-meters) ·
[P3](https://learn.microsoft.com/azure/cost-management-billing/reservations/copilot-credit-p3) ·
[trials](https://learn.microsoft.com/microsoft-copilot-studio/requirements-licensing-subscriptions)

**Microsoft 365 Copilot licenses don't cover harness usage.** An M365 Copilot license lets a user
build harness agents, but "creation and runtime activities consume Copilot Credits regardless of
the user's license" —
<https://learn.microsoft.com/power-platform/admin/manage-usage-microsoft-copilot-harness>.

## 3. What consumes credits on the harness

- **Billing starts while you build.** Natural-language authoring, **Preview / test chat**,
  evaluations and runtime conversations all consume credits — unlike classic agents, which are
  billed after publishing.
- Credits cover model reasoning (tokens), tools (including knowledge, web search, code execution
  and file creation) and the harness itself. **No per-feature rate card is published** for the
  harness — only estimate ranges and the
  [Copilot Credits estimator](https://nptnlopppecostweb.azurewebsites.net/#/estimator).
- Credits are charged to the **environment** where the agent runs, not to makers or end users.
- When credits run out, agents stop responding and makers can't preview or test (a small grace
  overage applies).

Sources:
[usage-based billing overview](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/billing-credit-overview) ·
[preview](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/preview-overview) ·
[enforcement](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/enforcement-policy-credits)

**Monitoring**: the running estimate is in the Preview pane header; final numbers on the agent's
**Monitor** page (refreshed a few times a day). Tenant view: Power Platform admin center →
**Licensing → Copilot Studio** (per environment and per agent, downloadable reports, per-agent
monthly limits with **Stop usage**). For pay-as-you-go, set **Azure Cost Management budgets**
(they alert; they don't stop usage).
<https://learn.microsoft.com/power-platform/admin/manage-copilot-studio-copilot-credits-capacity>

## 4. What this demo consumed

Measured from the Preview pane's credit counter while building and testing (November 2026):

| Activity | Conversations | Approx. credits |
|---|---|---|
| Runtime spike (scripts, images, PDF) | 1 | 15 |
| Hotel + activities tests (C1–C3), edge cases | 2 | 60 |
| End-to-end runs (hotel → activities → confirm → PDF) | 2 | 110 |
| Safety repeat runs (confirm/decline, booking, sensitive data) | 6 | 150 |
| Visa questions with knowledge/web search | 5 | 45 |
| **Total** | **16** | **≈ 380** (≈ USD 3.80 pay-as-you-go) |

Rules of thumb for this agent: a simple turn costs ~3–8 credits; a turn that runs a skill script
~5–10; a one-message "build the whole plan" request 20–40; a full end-to-end conversation ~50.
Budget **~50 credits per usability-test session**.

## 5. Who needs which license

| Role | What the docs say |
|---|---|
| **Maker** (builds the agent) | For the new experience: "You don't need an individually assigned Copilot Studio user license"; access depends on environment permissions and Dataverse roles ([source](https://learn.microsoft.com/troubleshoot/power-platform/copilot-studio/licensing/authors-access)). Classic docs require the free Copilot Studio User License. |
| **Publisher** | A troubleshooting page says publishing needs a Copilot Studio per-user license and that a viral trial on the same account can block publishing ([source](https://learn.microsoft.com/troubleshoot/power-platform/copilot-studio/licensing/publish-license-error)). Not stated whether this applies to harness agents — we published with a licensed account. |
| **End users** | Classic docs: no special license; with pay-as-you-go, users don't need separate licenses ([source](https://learn.microsoft.com/power-platform/admin/manage-copilot-studio-copilot-credits-capacity)). The new experience's *share* page lists a per-user license or trial as a prerequisite for recipients ([source](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/authoring-share-agent)). **The docs conflict** — check with your Microsoft contact before a wide rollout. |

## 6. Recommendation for a demo

Use a **sandbox** environment linked to a **pay-as-you-go billing plan**, set a per-agent monthly
limit (e.g. 2,000 credits) and an Azure budget alert. You pay only for what you test, and the
spend is capped.
