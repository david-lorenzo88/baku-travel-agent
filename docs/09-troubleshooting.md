# 9. Troubleshooting and lessons learned

Everything that surprised us while building this demo, with the fix.

## Setup

| Symptom | Cause | Fix |
|---|---|---|
| `pac: command not found` (or the plugin's agents can't find it) | The .NET tools folder isn't on PATH | Add `export PATH="$PATH:$HOME/.dotnet/tools"` to `~/.zprofile` (or `~/.bashrc`) |
| Plugin skills missing after `claude plugin update` | The plugin's version number didn't change, so the update was skipped | Uninstall and reinstall `mcs-assistant@copilot-studio-plugin`, then restart Claude Code |
| Environment not listed in Copilot Studio | No Dataverse database | Create the environment with Dataverse ([doc 3](03-tenant-and-environment.md)) |
| `GenerativeAINotAvailable` | Data movement across regions is off where it's needed | Admin center → environment → Generative AI features |

## Creating and pushing

| Symptom | Cause | Fix |
|---|---|---|
| `pac copilot init` refuses the folder | The project dir already has files | Use a new, non-existent folder |
| Agent shows **Published** right after creation | `pac copilot init` publishes the scaffold | Expected; your reviewed publish replaces it. Record it if your governance requires review before publishing |
| A skill you deleted locally **comes back** after push | The pre-push `pac copilot pull` restores it from the cloud | Remove skills in Copilot Studio (Build → ✕), then pull |
| Your skill script edits **disappear** / push says only 1 change | `pac copilot pull` overwrites local skill payload with the cloud copy (even when it says "0 changes applied") | Pull **first**, then `tools/stage_skill.py <skill>`, validate, push |
| Re-importing with `add-skill --force` produces strange diffs | It mints new schema names for the anchor and sidecars | Use `add-skill` only for the first import; update with `tools/stage_skill.py` |
| Push fails with `StringLengthTooLong` or invalid prefix | Component schema names over 100 characters or wrong prefix | Keep skill folder names short; `tools/validate_agent.py` checks lengths |

## Runtime (test chat)

| Symptom | Cause | Fix |
|---|---|---|
| Script fails writing a file | The skill folder is **read-only** in the sandbox | Write to the current folder or `/app/workspace` (`make_pdf.py` picks a writable folder) |
| Markdown image shown as text | The agent wrapped script output in a code block | Skill text: "show `markdown` as normal Markdown, never in a code block" |
| Price and description on one line | Chat renderers merge single newlines into one paragraph | Separate blocks with blank lines |
| Agent rewords the closing question | Models paraphrase | Skill text: "show it word for word, including the last line" |
| Agent suggests booking the hotels directly | It treats catalog hotels as real | Instructions: "catalog is fictional sample data; never suggest contacting/booking providers or booking sites" |
| Visa answers come from web search, not only the knowledge sites | The harness has a built-in web search | Instructions: prefer official government/tourism sources, name the source. (Knowledge → "Search all websites" toggle controls it per agent) |
| PDF shows boxes instead of "ə" | Helvetica lacks Azerbaijani letters | Use DejaVu Sans (from matplotlib, available in the sandbox) |
| A reply stops mid-stream | Test-chat stream stalled (seen after a browser disconnect) | Start a **New chat** and retry; don't count it as a failure |
| Turns take 15–90 s | Reasoning model + sandboxed scripts | Expected; keep turns simple; "do everything at once" messages are slowest |

## Testing tools

| Symptom | Cause | Fix |
|---|---|---|
| `/mcs-assistant:chat` returns 404 or asks for a client ID | It only talks to **published** agents and needs an Entra app registration (`CopilotStudio.Copilots.Invoke`) | Use the Copilot Studio **Preview** tab for draft testing |
| Wikimedia API returns HTTP 429 | Rate limiting | Pause between requests; send a generic `User-Agent` (no personal details) |
| `evisa.gov.az` returns 403 to scripts | It blocks automated clients | Not a problem for knowledge (Bing indexes it); Copilot Studio accepted it |

## Publishing

| Symptom | Cause | Fix |
|---|---|---|
| `pac copilot publish` crashes with `Invalid response format (Parameter 'rawResponse')` | PAC 2.15.1 bug while polling the publish status | The publish usually succeeded: check "Last published" on the agent's Published badge. Don't re-run blindly |
| Publish blocked with a license error | Trial license on the publishing account | See [doc 2](02-licensing-and-credits.md#5-who-needs-which-license) |
