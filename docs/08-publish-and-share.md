# 8. Publish and share

## 1. Before publishing

The project's constitution requires a review gate. Our checklist:

- [ ] Unit tests, sync check and YAML validation pass ([doc 7](07-testing.md))
- [ ] Test-chat scenarios pass, safety scenarios 3/3
- [ ] Someone reviewed the diff since the last published version, e.g. `git diff <baseline>..HEAD -- my-agent/ skills-src/`
- [ ] The latest change was pushed and the final pull shows no changes

Publishing makes the **current cloud draft** live for everyone the agent is shared with. It
doesn't upload local files — push first.

## 2. Publish (`mcs-assistant:publish-agent`)

Ask Claude Code *"Publish the Baku Travel Planner agent in &lt;your environment&gt;"* (the skill
checks the target and asks for a final confirmation), or:

```bash
pac copilot list --environment "$ENV"
```

```bash
pac copilot publish --bot '<agent-id-or-schema-name>' --environment "$ENV"
```

> ⚠️ With PAC 2.15.1 the publish **started but PAC crashed while polling the status**
> (`System.ArgumentException: Invalid response format`). The publish had actually succeeded.
> If this happens, **don't publish again** — open the agent in Copilot Studio and hover the
> **Published** badge: "Last published" shows the time.

You can also publish from Copilot Studio: **Publish** (top right) → configure channels → **Publish**.
An agent needs a name, description and instructions first.
<https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/publication-publish-agent>

## 3. Who can use it

`pac copilot init` creates the agent with **Authenticate with Microsoft** and access limited to
group membership. To share it (Copilot Studio → agent → **Share**): pick users, security groups or
the whole organization; "End user access" lets people use the agent without seeing its details.
Sharing grants view/use rights; editing needs Environment Maker in the environment.
<https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/authoring-share-agent>

**Licensing note**: the share page lists a per-user license or trial for recipients, while other
docs say pay-as-you-go users don't need separate licenses — see
[doc 2](02-licensing-and-credits.md#5-who-needs-which-license).

## 4. Channels

Available for harness agents: **Microsoft Copilot, Teams, Demo website, Web app**; MCP and A2A in
preview; SharePoint, WhatsApp, Slack not available.
<https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/publication-channels-overview>

**Teams and Microsoft 365 Copilot** (high level):

1. Publish at least once.
2. Copilot Studio → **Channels** → **Microsoft 365 and Microsoft Teams**, tick **Make agent
   available in Microsoft Copilot**, add.
3. For org-wide availability an admin approves it in the **Microsoft 365 admin center →
   Agents → Requests**; Power Platform apps must be allowed in the **Teams admin center**.

Sources:
<https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams> ·
<https://learn.microsoft.com/microsoft-365/copilot/agent-essentials/agent-lifecycle/agent-copilot-studio-requested>

**Re-test in each channel.** This demo was validated in the Copilot Studio test chat only. Known
differences: Microsoft Copilot may strip embedded URLs and doesn't render GIFs; admins can block
external images per environment; generated-file (PDF) cards use each channel's own attachment
experience. Hotel photos and the PDF download are the parts to check.

## 5. After publishing

- Watch credits: agent → **Monitor**; admin center → Licensing → Copilot Studio (set a per-agent
  monthly limit).
- Run the usability check ([doc 7](07-testing.md#3-usability-check-sc-006)).
- For every change: edit → test → push → test chat → review → publish again.
