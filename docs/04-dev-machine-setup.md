# 4. Developer machine setup

Commands are for **macOS with Homebrew**; Windows/Linux equivalents are noted. Versions are the
ones this demo was built with.

## 1. Git and the repo

```bash
brew install git
```

```bash
git clone https://github.com/david-lorenzo88/baku-travel-agent.git
```

```bash
cd baku-travel-agent
```

## 2. Python and the test environment

Python 3.10+ (3.13 used locally; the agent's sandbox runs 3.12).

```bash
brew install python@3.13
```

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

```bash
.venv/bin/python -m pytest -q
```

All 119 tests should pass. `requirements-dev.txt` includes `reportlab` (PDF) and `matplotlib`
(ships the DejaVu Sans font the PDF uses for Azerbaijani letters — the agent sandbox has it too).

## 3. Node.js

The Copilot Studio plugin's helper scripts (skill import, chat) run on Node.js.

```bash
brew install node
```

## 4. .NET SDK

The Power Platform CLI .NET tool needs the .NET SDK; Microsoft recommends **.NET 10**.

```bash
brew install --cask dotnet-sdk
```

Windows: install the .NET 10 SDK from <https://dotnet.microsoft.com/download>.

## 5. Power Platform CLI

```bash
dotnet tool install --global Microsoft.PowerApps.CLI.Tool
```

Add the tools folder to your PATH (macOS/Linux) — the plugin's agents need to find `pac`:

```bash
echo 'export PATH="$PATH:$HOME/.dotnet/tools"' >> ~/.zprofile && source ~/.zprofile
```

```bash
pac
```

You need **2.9.3 or later** (2.15.1 used). Other install options: the Windows MSI or the
Power Platform Tools extension for VS Code.
<https://learn.microsoft.com/power-platform/developer/howto/install-cli-net-tool>

Sign in to your environment (opens a browser; add `--deviceCode` on machines without one):

```bash
pac auth create --environment https://<your-org>.crm.dynamics.com/
```

```bash
pac auth list
```

## 6. uv and Spec Kit

```bash
brew install uv
```

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.4.0
```

```bash
specify --version
```

This repo is already initialized for Spec Kit (`.specify/`, `.claude/skills/speckit-*`). For a new
project you'd run `specify init --here --integration claude` — see [doc 5](05-spec-kit-workflow.md).

## 7. Claude Code and plugins

Install Claude Code (CLI, desktop app or IDE extension) from <https://claude.com/claude-code> and
sign in. Then, inside Claude Code:

```text
/plugin marketplace add microsoft/copilot-studio-plugin
/plugin install mcs-assistant@copilot-studio-plugin
```

Restart Claude Code so the plugin's skills load. You should then see skills such as
`mcs-assistant:create-agent`, `add-skill`, `add-knowledge`, `push-agent`, `pull-agent`,
`publish-agent` and the `/mcs-assistant:chat` command, plus the Spec Kit skills
(`/speckit-specify`, `/speckit-plan`, …) when you open this folder.

> **Plugin updates**: the plugin's version number doesn't always change when its content does
> (we hit 1.0.2 with and without the newer skills). If skills are missing, uninstall and
> reinstall it:
> `claude plugin uninstall mcs-assistant@copilot-studio-plugin --scope user` then
> `claude plugin install mcs-assistant@copilot-studio-plugin --scope user`.

## 8. Optional: let Claude drive the test chat

Install the **Claude in Chrome** extension and sign in, then sign in to Copilot Studio in that
Chrome profile. Claude can then run the test-chat scenarios in [doc 7](07-testing.md) for you.
The plugin's `/mcs-assistant:chat` command is an alternative **only for published agents** and
needs an Entra app registration with the delegated `CopilotStudio.Copilots.Invoke` permission.

## 9. Sanity check

```bash
git --version && python3 --version && node --version && dotnet --version && pac 2>&1 | grep Version && specify --version
```
