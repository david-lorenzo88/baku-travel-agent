# 6. Deploy the agent to your environment

The fast path: create **your own** agent and load this repo's skills, instructions and knowledge
into it. Prerequisites: docs [3](03-tenant-and-environment.md) and [4](04-dev-machine-setup.md).

> **Why not reuse `agent/`?** The `agent/` folder is a snapshot of the original workspace. Its
> identity (`schemaName`, sync metadata in the git-ignored `.mcs/`) belongs to the original
> environment. You'll create a new workspace, `my-agent/`, connected to yours, and copy the content
> into it.

Throughout: `ENV=https://<your-org>.crm.dynamics.com/` and `PLUGIN=` the plugin folder, for
example `~/.claude/plugins/cache/copilot-studio-plugin/mcs-assistant/1.0.2`.

You can do every step either by **asking Claude Code** (the plugin skill named in each step does it
safely, with checks) or with the **commands** shown.

## 1. Check the local build

```bash
.venv/bin/python tools/sync_shared.py --check && .venv/bin/python -m pytest -q
```

## 2. Create the agent (`mcs-assistant:create-agent`)

Ask Claude Code: *"Create a Copilot Studio agent named Baku Travel Planner in
https://&lt;your-org&gt;.crm.dynamics.com/, project dir `my-agent`, publisher prefix `catmgr`,
instructions-only."* Or:

```bash
pac copilot init --name 'Baku Travel Planner' --environment "$ENV" --project-dir "$PWD/my-agent" --publisher-prefix 'catmgr' --authoring-mode cli-copilot --instructions 'You are Baku Travel Planner.'
```

- `--project-dir` must not exist yet (PAC refuses non-empty folders).
- Use your organization's publisher prefix if it has one (2–8 letters/digits).
- ⚠️ `pac copilot init` **publishes the initial scaffold** automatically. That version has only
  the placeholder instructions; your reviewed publish later replaces it.

Check `my-agent/settings.mcs.yml`: `template: cliagent-…`, `authoringModel: CliCopilot`,
recognizer `CLICopilotRecognizer`. Add `my-agent/.mcs/` to `.gitignore` (it's CLI-managed state).

## 3. Copy in the full instructions

Replace the `instructions → segments → StaticSegment → value` block of
`my-agent/settings.mcs.yml` with the one in [`agent/settings.mcs.yml`](../agent/settings.mcs.yml).
Keep everything else in your file (display name, schema name, model, recognizer, template).
Then validate:

```bash
.venv/bin/python tools/validate_agent.py my-agent/
```

## 4. Import the three skills (`mcs-assistant:add-skill`)

The importer writes the skill package plus the `.mcs.yml` companion files with schema names based
on **your** agent:

```bash
for s in baku-trip-catalog confirm-trip-plan export-trip-plan-pdf; do node "$PLUGIN/scripts/add-skill.js" import --src "$PWD/skills-src/$s" --workspace "$PWD/my-agent"; done
```

Each import should report `"ok": true` and no warnings. Use the importer **only for the first
import** of a skill — to update one later, see step 7.

## 5. Add the knowledge sources (`mcs-assistant:add-knowledge`)

Ask Claude Code: *"Add public website knowledge `https://evisa.gov.az` and
`https://azerbaijan.travel` to my-agent"* with these descriptions:

- `https://evisa.gov.az` — "Official Republic of Azerbaijan e-visa portal (ASAN Visa): visa
  requirements, e-visa application, fees and processing times for visitors to Azerbaijan."
- `https://azerbaijan.travel` — "Official Azerbaijan Tourism Board site: Baku sights,
  neighborhoods, events, transport and practical travel information for visitors."

The skill writes `my-agent/capabilities/knowledge/<schemaName>.<slug>_<id>.mcs.yml` files like the
two in [`agent/capabilities/knowledge/`](../agent/capabilities/knowledge/).

## 6. Validate and push (`mcs-assistant:push-agent`)

The push procedure used for every change in this project:

```bash
pac copilot pull --project-dir "$PWD/my-agent"
```

```bash
.venv/bin/python tools/validate_agent.py my-agent/
```

```bash
pac copilot push --project-dir "$PWD/my-agent"
```

```bash
pac copilot pull --project-dir "$PWD/my-agent"
```

Then commit. The first push should report around 25 changes (3 skills with scripts, catalog and
photos, 2 knowledge sources, instructions). Open the agent in Copilot Studio → **Build**: you
should see the three skills and the two websites.

## 7. Updating later (important)

- **Change a skill**: edit `skills-src/` (or `skills-src/_shared/` then
  `tools/sync_shared.py`), run the tests, then **pull first**, then copy the payload into the
  workspace, validate and push:

  ```bash
  pac copilot pull --project-dir "$PWD/my-agent" && .venv/bin/python tools/stage_skill.py baku-trip-catalog --agent my-agent
  ```

  Never re-import with `add-skill --force`: it generates new schema names, and the next pull
  reverts your files. And a pull **overwrites local skill payload edits** with the cloud copy —
  that's why you stage *after* pulling.
- **Remove a skill or knowledge source**: delete it in Copilot Studio (Build → ✕), then pull.
  Deleting the folder locally and pushing does not remove it from the cloud.
- **Change instructions**: edit `settings.mcs.yml`, validate, push.

## 8. Next

Test in the Copilot Studio test chat ([doc 7](07-testing.md)), then publish
([doc 8](08-publish-and-share.md)).
