# 1. Prerequisites

Everything you need before you start. Details and links are in the following docs; this page is
the checklist.

## Accounts and access

| You need | Why | Details |
|---|---|---|
| A **Microsoft Entra ID (work or school) tenant** where you can sign in to Copilot Studio | Copilot Studio and Dataverse live there | [doc 3](03-tenant-and-environment.md) |
| A **Power Platform environment with Dataverse** (production or sandbox recommended) | Agents are stored in Dataverse; `pac copilot init` imports a solution | [doc 3](03-tenant-and-environment.md) |
| The **Environment Maker** security role in that environment (or System Customizer / System Administrator) | Create, push and publish agents | [doc 3](03-tenant-and-environment.md#3-give-yourself-the-right-role) |
| **Copilot Credits** for the environment: a capacity pack, pay-as-you-go billing plan, or trial | The new Copilot Studio experience bills from the first test message | [doc 2](02-licensing-and-credits.md) |
| Generative AI settings allowed by your admin (data movement / Bing search where applicable, publishing agents with AI features) | Web search, knowledge and publishing | [doc 3](03-tenant-and-environment.md#4-check-the-generative-ai-settings) |
| A **Claude** account with access to **Claude Code** | The AI coding agent that drives Spec Kit and the Copilot Studio plugin | [doc 4](04-dev-machine-setup.md#7-claude-code-and-plugins) |
| A **GitHub** account (optional) | Clone this repo; Spec Kit itself is installed from GitHub | — |

If you're not a Power Platform admin, ask your admin for: an environment with Dataverse,
the Environment Maker role, Copilot Credits assigned to the environment, and the generative AI
settings in [doc 3](03-tenant-and-environment.md). A ready-to-send checklist is at the end of
that doc.

## Machine and tools

Built and tested on **macOS 26 (Apple silicon)**; everything also runs on Windows and Linux.

| Tool | Version used | Required for |
|---|---|---|
| Git | 2.54 | Version control (the constitution requires commits) |
| Python | 3.13 (3.10+ works; the agent sandbox runs 3.12) | Skill scripts, tests, tools |
| .NET SDK | 10.0 | Power Platform CLI as a .NET tool |
| Power Platform CLI (`pac`) | 2.15.1 (2.9.3+ required by the plugin) | Create, push, pull, publish agents |
| Node.js | 24 | The Copilot Studio plugin's helper scripts (skill import, chat) |
| uv | 0.11 | Installing Spec Kit |
| Spec Kit (`specify`) | 1.4.0 | Spec-driven workflow |
| Claude Code | 2.1 | AI coding agent |
| Copilot Studio authoring plugin (`mcs-assistant`) | 1.0.2 (commit 4014ae6) | Agent authoring skills for Claude Code |
| Chrome + Claude in Chrome extension (optional) | — | Letting Claude drive the Copilot Studio test chat |

Install steps: [doc 4](04-dev-machine-setup.md).

## Budget and time

- **Copilot Credits**: building and testing this demo used about **380 credits** (≈ USD 3.80 at
  the pay-as-you-go rate of USD 0.01 per credit). A single test conversation used 15–60 credits.
  See [doc 2](02-licensing-and-credits.md#4-what-this-demo-consumed).
- **Time**: about 1–2 hours to deploy the finished agent (docs 4, 6, 7, 8) once the tenant is
  ready; a full day to rebuild it from scratch with Spec Kit (doc 5).

## Knowledge that helps

Basic command line and Git; reading YAML and Python; familiarity with the Power Platform admin
center. No prior Copilot Studio YAML experience is needed — the plugin and the guide cover it.
