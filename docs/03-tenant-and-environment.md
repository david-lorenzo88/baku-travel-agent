# 3. Tenant and environment setup

Done once, usually by a Power Platform admin. Checked against Microsoft Learn in November 2026.

## 1. Pick or create an environment with Dataverse

Copilot Studio agents are stored in **Dataverse**; an environment without a database doesn't even
appear in Copilot Studio, and `pac copilot init --environment` imports a solution into it.

| Type | Use it? | Notes |
|---|---|---|
| **Sandbox** | ✅ Recommended for this demo | Supports pay-as-you-go; can be reset |
| **Production** | ✅ | Supports pay-as-you-go |
| **Developer** | ⚠️ | Managed developer environments only (unmanaged ones can't be created from 15 Nov 2026 and are suspended from 15 Dec 2026); no pay-as-you-go |
| **Trial** | ❌ | Expires after 30 days and its agents are deleted |

Create it in the **Power Platform admin center** (<https://admin.powerplatform.microsoft.com>) →
**Manage → Environments → New**: type Sandbox or Production, **Add a Dataverse data store = Yes**,
pick a supported region. Production and sandbox need 1 GB of available database capacity.
Tenant settings can restrict who may create environments.

Sources:
[environment types](https://learn.microsoft.com/power-platform/admin/environments-overview) ·
[create an environment](https://learn.microsoft.com/power-platform/admin/create-environment) ·
[control creation](https://learn.microsoft.com/power-platform/admin/control-environment-creation) ·
[first-run environments](https://learn.microsoft.com/microsoft-copilot-studio/environments-first-run-experience)

Write down the environment's **URL** (`https://<your-org>.crm.dynamics.com/`) — every `pac`
command uses it.

## 2. Give the environment Copilot Credits

Choose one (see [doc 2](02-licensing-and-credits.md)):

- **Prepaid capacity**: admin center → **Licensing → Copilot Studio → Manage Copilot Credits** →
  select the environment → enter credits. Overage can draw from tenant capacity (default) or bill
  to a pay-as-you-go plan.
  <https://learn.microsoft.com/power-platform/admin/manage-copilot-studio-copilot-credits-capacity>
- **Pay-as-you-go**: admin center → **Licensing → Pay-as-you-go plans → New billing plan** →
  choose Azure subscription, resource group and product → select the environment. Environment,
  Power Platform, Dynamics 365 or Global admins can create plans.
  <https://learn.microsoft.com/power-platform/admin/pay-as-you-go-set-up>

Then set a **per-agent monthly limit** (Licensing → Copilot Studio) and, for pay-as-you-go, an
**Azure Cost Management budget**.

## 3. Give yourself the right role

In the environment (admin center → environment → **Settings → Users + permissions → Users**),
assign the maker the **Environment Maker** security role. It grants the create/read/write
privileges on the `bot` and `botcomponent` tables needed to create, push and publish agents.
System Customizer and System Administrator also work. Co-authors need Environment Maker too.

Sources:
[security and governance](https://learn.microsoft.com/microsoft-copilot-studio/guidance/sec-gov-phase3) ·
[author access](https://learn.microsoft.com/troubleshoot/power-platform/copilot-studio/licensing/authors-access) ·
[share with co-authors](https://learn.microsoft.com/microsoft-copilot-studio/admin-share-bots)

## 4. Check the generative AI settings

| Setting | Where | Needed for |
|---|---|---|
| **Move data across regions** and **Bing search** | Admin center → Manage → Environments → *your environment* → **Generative AI features → Edit** | Generative features outside supported regions, and web search. Bing search requires data movement when that checkbox is shown; it isn't shown for US environments. If needed but off, users see `GenerativeAINotAvailable`. [source](https://learn.microsoft.com/power-platform/admin/geographical-availability-copilot) |
| **Publish Copilots with AI features** | Admin center → Manage → **Tenant settings** | Publishing generative agents. [source](https://learn.microsoft.com/power-platform/admin/tenant-settings) |
| **Knowledge sources for agents** | Copilot Studio / admin data policies | Must allow **public websites** (this agent uses two). [source](https://learn.microsoft.com/microsoft-copilot-studio/choose-knowledge-sources) |
| **Showing images and URLs** | Admin center → Security → Threat detection | Must allow external images, or the hotel/activity photos won't render in chat. [source](https://learn.microsoft.com/microsoft-copilot-studio/image-render-embedded-url) |
| **Data policies (DLP)** | Admin center → Security → Data and privacy → Data policy | Must not block the channels you publish to. [source](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/publication-publish-agent) |

The harness itself has **no on/off switch**, and CLI-authored agents need no preview flag.
Code execution and file creation are native to the harness (built-in Python packages include
`reportlab`, `pandas` and `matplotlib`; files up to 10 MB, kept 28 days; file creation is in
preview). The `CopilotStudio_CodeInterpreter` environment setting is documented for *prompts*;
whether harness agents need it isn't documented — this demo worked without changing it.

Sources:
[harness overview](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/overview) ·
[created files](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/created-files-overview) ·
[PAC copilot reference](https://learn.microsoft.com/power-platform/developer/cli/reference/copilot)

## 5. Verify from the maker's side

1. Open <https://copilotstudio.microsoft.com>, pick the environment in the top-right switcher.
2. Home → **Agent** tile should be available (the new experience). You don't need to create an
   agent here — `pac copilot init` does it in [doc 6](06-deploy-the-agent.md).
3. From your machine: `pac auth create --environment https://<your-org>.crm.dynamics.com/` and
   `pac copilot list --environment https://<your-org>.crm.dynamics.com/` should succeed
   ([doc 4](04-dev-machine-setup.md#5-power-platform-cli)).

## Checklist to send to your admin

```text
For the Copilot Studio demo I need, in one Power Platform environment:
[ ] Sandbox (or production) environment WITH Dataverse — URL: ______________
[ ] Copilot Credits assigned (capacity or pay-as-you-go billing plan), per-agent limit ~2,000/month
[ ] Environment Maker role for: ______________
[ ] Generative AI features: data movement + Bing search allowed (if shown for our region)
[ ] Tenant setting "Publish Copilots with AI features" on
[ ] Public website knowledge sources allowed; external images/URLs allowed in chat
[ ] Data policy allows the Microsoft Copilot / Teams channels (only if we'll publish there)
```
