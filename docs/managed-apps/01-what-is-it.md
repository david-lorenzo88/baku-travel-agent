# 1. What it is

## Copilot Managed Runtime

**Copilot Managed Runtime (CMR)** is Microsoft's hosted runtime for business web apps built with
AI. Microsoft hosts the app and handles sign-in with Microsoft Entra ID, loading, and governance:
Conditional Access, data loss prevention, connector policies and sharing limits. You don't manage
servers, hosting or deployment.

Apps can be created four ways — Copilot Studio, Cowork, Copilot Code, or the SDK/CLI — and all of
them produce the same kind of app. This guide uses **Copilot Studio**.

Sources:
[Copilot Managed Runtime overview](https://learn.microsoft.com/microsoft-365/copilot-managed-runtime/) ·
[architecture](https://learn.microsoft.com/microsoft-365/copilot-managed-runtime/developer/apps/architecture)

## Apps in Copilot Studio

In Copilot Studio it appears as **Apps (Preview)** in the left navigation and an **App** tile on
Home ("Build a custom app with screens, data, and logic"). You describe the app; Copilot Studio may
ask a few clarifying questions, then generates the **data model, logic and user interface**. You
refine it in the chat — with more prompts, files, screenshots or annotations. The generated code is
visible but read-only.

App creation is powered by the **Microsoft Copilot harness** — the same runtime family as the
agent in this repo.

Sources:
[apps overview](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/apps-overview) ·
[create an app](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/create-app) ·
[apps FAQ](https://learn.microsoft.com/microsoft-copilot-studio/faq-apps)

## What's underneath

- A **TypeScript/JavaScript single-page app** (React + Vite in Microsoft's examples) using the CMR
  SDK, with generated connector models and services, and a Git repository managed by the platform.
- Data through **connectors** (SharePoint lists, existing Dataverse tables, Excel, SQL…), sample
  data, or browser storage.
- Each user signs in to connectors **with their own account** — the maker's credentials are never
  shared, and users only see data they already have access to.

Source: [architecture](https://learn.microsoft.com/microsoft-365/copilot-managed-runtime/developer/apps/architecture) ·
[data and connections](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/data-and-connections)

## Where it runs

Users open apps from the app portal at **<https://managedapps.cloud.microsoft>** or a direct link.
Admins see them in the Microsoft 365 admin center under **Apps → All apps**.

Source: [share and run apps](https://learn.microsoft.com/microsoft-365/copilot-managed-runtime/partner-integration/share-run-apps)

## Not Power Apps

These apps are **not** canvas, model-driven or code apps. Power Apps are governed in the Power
Platform admin center; CMR apps are inventoried in the Microsoft 365 admin center (and show in the
Power Platform inventory as item type "Copilot Managed Runtime").

Source: [apps inventory](https://learn.microsoft.com/microsoft-365/admin/manage/apps/inventory)

## Status

**Preview**, under supplemental preview terms, for eligible tenants in the **commercial cloud**.
The Copilot Studio path is **on by default**.

Source: [apps admin overview](https://learn.microsoft.com/microsoft-365/admin/manage/apps/)

## Agent or app?

| Choose an **agent** when… | Choose an **app** when… |
|---|---|
| The experience is a conversation | Users browse, filter, enter data and press buttons |
| Strict rules must hold in every reply (privacy, confirmation) | The logic is mainly forms, lists and calculations |
| You need conversational channels (Teams, Microsoft 365 Copilot) | You want a standalone web app on business data |

This repo has both for the same scenario — compare them in [the Baku Travel app](04-baku-travel-app.md#agent-vs-app--same-scenario-two-approaches).
