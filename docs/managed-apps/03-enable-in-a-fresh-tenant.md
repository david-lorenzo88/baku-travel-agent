# 3. Enable it in a fresh tenant

For admins. In most commercial tenants app creation in Copilot Studio is **already on**; the work
is mainly paying for build and run, and checking governance.

## 1. Check app creation is allowed

Microsoft 365 admin center → **Apps → Overview → Set up app creation spaces**. The Copilot Studio
path is on by default (public preview and Frontier); only the Cowork path needs the Frontier
program.

Optional — restrict or disable it with the Power Platform CLI (as a Global or Power Platform admin):

```bash
pac admin update-tenant-settings --setting-name powerPlatform.powerapps.enableManagedAppsMcsPreview --setting-value 'off'
```

To allow only some people, set `powerPlatform.powerapps.enabledGroupsManagedAppsMcsPreview` to a
comma-separated list of security group object IDs. Open Copilot Studio tabs pick up changes within
about 15 minutes.

Source: [apps admin overview](https://learn.microsoft.com/microsoft-365/admin/manage/apps/)

## 2. Let routing create the makers' environments

Nothing to do: CMR environment routing is always on. In a tenant with no routing rules, an
**Everyone** rule and a default environment group are created the first time someone builds an
app (or an admin opens the CMR admin pages). The Everyone rule can't be deleted afterwards.

> If your tenant **already has routing rules without an Everyone rule**, makers outside the
> targeted groups are **blocked** — add them to a targeted group.

Source: [default environment routing](https://learn.microsoft.com/power-platform/admin/default-environment-routing-copilot-managed-runtime)

## 3. Give makers Copilot Credits (build)

Power Platform admin center → **Licensing → Copilot Studio → Manage Copilot Credits**: allocate
credits (or pay-as-you-go) to the makers' environments. Without an allocation, an environment
draws from tenant capacity. Check **Manage capacity** to see whether the environment is billed
there or through a Microsoft 365 spending policy.

Source: [manage harness usage](https://learn.microsoft.com/power-platform/admin/manage-usage-github-copilot-harness)

## 4. Cover app users (run)

Pick one:

- **Power Apps Premium** licenses for the users, or
- **Spending policy**: Microsoft 365 admin center → **Copilot → Cost management → Get started**
  (choose the billing method) → **Configuration → + Add spending policy** → scope (e.g. All users
  or a security group) → select **Copilot Managed Runtime** → set a limit, e.g. **100 credits per
  user per month**.

Without coverage, users are blocked after 20 operations or 5 minutes.

Source: [licensing and credits](https://learn.microsoft.com/microsoft-365/admin/manage/apps/licensing-credits)

## 5. Review governance

Microsoft 365 admin center → **Apps → Settings → Environment groups**: routing, connectors and MCP
servers, sharing limits ("everyone in org", guests), content security policy. For this demo:

- **SharePoint** must be allowed (it is in the default advanced connector policy).
- Check classic data policies don't block SharePoint.
- Known issue: guests can't open apps even if guest sharing is allowed.

Source: [governance](https://learn.microsoft.com/microsoft-365/admin/manage/apps/governance)

## 6. Maker check

At <https://copilotstudio.microsoft.com>: turn on **New experience** on Home, then confirm the
**App** tile or **Apps (Preview) → New app** is available.

Source: [create an app](https://learn.microsoft.com/microsoft-copilot-studio/apps-experience/create-app)

## Checklist to send to your admin

```text
For the Copilot Studio app demo (Copilot Managed Runtime) I need:
[ ] App creation in Copilot Studio allowed for me (M365 admin center > Apps > Set up app creation spaces)
[ ] Copilot Credits for my developer environment (PPAC > Licensing > Copilot Studio)
[ ] Runtime coverage for testers: Power Apps Premium OR an M365 spending policy for
    "Copilot Managed Runtime" (e.g. 100 credits/user/month)
[ ] SharePoint connector allowed for apps (environment group + data policies)
[ ] A SharePoint site I own (or permission to create one) for the app's lists
```
