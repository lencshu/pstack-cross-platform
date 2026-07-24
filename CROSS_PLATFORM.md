# pstack cross-platform adapter

This repository treats the Cursor edition of pstack as its single upstream source and produces installable Codex and Claude Code plugins. The adapters are not three hand-maintained copies. The root `skills/`, `agents/`, `automations/`, and `.cursor-plugin/` directories retain the Cursor upstream layout. Scripts generate the other platform packages.

## Installation

### Prepare the terminal

Run the setup for your operating system before using the `codex` or `claude` commands below.

#### macOS

Codex Desktop includes a CLI at `/Applications/Codex.app/Contents/Resources/codex`; use that full path if `codex` is unavailable. Claude Desktop does not install the `claude` command, so install Claude Code CLI and add its location to zsh:

```bash
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Linux

Use the standalone CLIs. Claude's installer writes its binary to `~/.local/bin`:

```bash
npm install --global @openai/codex
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)

Install both standalone CLIs, then open a new PowerShell window so the updated `PATH` is loaded:

```powershell
npm install --global @openai/codex
irm https://claude.ai/install.ps1 | iex
```

If either command is still not recognized, confirm the installation with `Get-Command codex` or `Get-Command claude`; rerun the relevant installer if it is absent.

### Cursor

```text
/add-plugin pstack
```

### Codex

Install from a local checkout:

```powershell
codex plugin marketplace add .
codex plugin add pstack@pstack-cross-platform
```

Install from GitHub:

```powershell
codex plugin marketplace add lencshu/pstack-cross-platform
codex plugin add pstack@pstack-cross-platform
```

In a new task, run `$pstack:setup-pstack` first, then use `$pstack:poteto-mode`.

### Claude Code

Install from a local checkout:

```powershell
claude plugin marketplace add .
claude plugin install pstack@pstack-cross-platform
```

Install from GitHub:

```powershell
claude plugin marketplace add lencshu/pstack-cross-platform
claude plugin install pstack@pstack-cross-platform
```

In a new session, run `/pstack:setup-pstack` first, then use `/pstack:poteto-mode`.

## Desktop app integration

The adapter packages do not create a separate sidebar, Webview, or settings page. On desktop, pstack is an installable plugin with skills and subagents. Invoke its skills from the chat input after installation. The UI paths below follow the client documentation available on 2026-07-20.

### Cursor desktop

Cursor uses the upstream source at the repository root directly. It does not use output from `adapters/`. For normal use, install the official pstack plugin from Cursor Marketplace.

1. Open Cursor and run `/add-plugin pstack` in the Agent input. You can also search for `pstack` in [Cursor Marketplace](https://cursor.com/marketplace).
2. Start a new Agent conversation after installation.
3. Run `/setup-pstack` once and choose models for the different roles.
4. For a non-trivial task, run `/poteto-mode <task description>`. Invoke other skills as `/<skill>`.
5. Disable, update, or uninstall the plugin from Customize or the plugin manager in Cursor.

To develop this repository, point Cursor's local plugin directory at the repository root:

```text
~/.cursor/plugins/local/pstack/
```

`.cursor-plugin/plugin.json` must be at the plugin root. Create a directory link to this repository instead of copying its source. After changing it, run `Developer: Reload Window` or restart Cursor completely. Local verification then always reads the Cursor upstream directory. The generated Codex and Claude Code packages do not affect Cursor.

See the official Cursor [Plugins](https://cursor.com/docs/plugins) documentation.

### Codex desktop

Codex desktop reads this repository's marketplace from `.agents/plugins/marketplace.json`. Register the repository once, then install and manage the plugin in the app.

1. Register the marketplace in a system terminal. On macOS, use the Codex command bundled with the desktop app:

   ```bash
   /Applications/Codex.app/Contents/Resources/codex plugin marketplace add lencshu/pstack-cross-platform
   ```

   On Linux, after completing the terminal setup above, use `codex` instead:

   ```bash
   codex plugin marketplace add lencshu/pstack-cross-platform
   ```

   On Windows PowerShell:

   ```powershell
   codex plugin marketplace add lencshu/pstack-cross-platform
   ```

   When developing local changes, use the repository root instead:

   ```bash
   /Applications/Codex.app/Contents/Resources/codex plugin marketplace add .
   ```

   On Linux:

   ```bash
   codex plugin marketplace add .
   ```

   On Windows PowerShell:

   ```powershell
   codex plugin marketplace add .
   ```

2. Quit and reopen the ChatGPT or Codex desktop app. Closing its window alone may not refresh the marketplace.
3. Select `Codex` in the desktop app and open `Plugins`.
4. Select the `pstack cross-platform` marketplace source, open `pstack`, and select the plus button to install it. If you already ran `codex plugin add pstack@pstack-cross-platform`, confirm that it appears under `Installed` and is enabled.
5. Start a new task. Run `$pstack:setup-pstack` once, then use `$pstack:poteto-mode` or another `$pstack:<skill>` skill.

For a full command-line installation and troubleshooting flow:

```bash
/Applications/Codex.app/Contents/Resources/codex plugin add pstack@pstack-cross-platform
/Applications/Codex.app/Contents/Resources/codex plugin marketplace list
/Applications/Codex.app/Contents/Resources/codex plugin list
```

On Linux, replace the full macOS path with `codex`. On Windows, run the same `codex plugin` subcommands from PowerShell.

After updating the GitHub marketplace, run `/Applications/Codex.app/Contents/Resources/codex plugin marketplace upgrade pstack-cross-platform`, reinstall the plugin, and start a new task. When a generated package changes during development, refresh the cached package version and reinstall it. Do not expect an existing task to load a changed skill file.

If `codex` is not recognized in macOS Terminal, use the full `/Applications/Codex.app/Contents/Resources/codex` command above. It is the CLI bundled with Codex desktop. If that path does not exist, update or reinstall Codex desktop. To use the shorter `codex` command instead, install the standalone CLI (for example, `npm install --global @openai/codex`) and ensure its installation directory is on your `PATH`.

Codex desktop shows this package as a skills plugin. It has no `.app.json` or MCP server, so it does not add a custom interface or external account authorization. See the official [Plugins](https://learn.chatgpt.com/docs/plugins) and [Build plugins](https://learn.chatgpt.com/docs/build-plugins#build-your-own-curated-plugin-list) guides.

### Claude Desktop Code tab

Claude Desktop and the Claude Code CLI share plugin configuration. Register the marketplace, then install it from the Code tab plugin manager.

1. Claude Desktop does not install the `claude` Terminal command. Install Claude Code CLI first, then register the marketplace. On macOS and Linux, the installer uses `~/.local/bin/claude`:

   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ~/.local/bin/claude plugin marketplace add lencshu/pstack-cross-platform
   ```

   On Windows PowerShell, use:

   ```powershell
   claude plugin marketplace add lencshu/pstack-cross-platform
   ```

   For local development, use:

   ```bash
   ~/.local/bin/claude plugin marketplace add .
   ```

   On Windows PowerShell:

   ```powershell
   claude plugin marketplace add .
   ```

2. Open Claude Desktop, select the `Code` tab, and create a `Local` session. SSH sessions also support plugins.
3. Select the `+` button beside the input, then choose `Plugins` and `Add plugin`.
4. Select `pstack` in the `pstack-cross-platform` marketplace. Choose User scope for personal use, Project scope to write the enabled configuration to the repository, or Local scope for personal use in only the current repository.
5. Run `/reload-plugins` after installation, or start a new Code session.
6. Run `/pstack:setup-pstack` once, then use `/pstack:poteto-mode <task description>`. Select `+` and `Slash commands` to browse every pstack skill.
7. Use `+`, `Plugins`, and `Manage plugins` to enable, disable, or uninstall the plugin.

You can also install it entirely from the command line:

```bash
~/.local/bin/claude plugin install pstack@pstack-cross-platform
~/.local/bin/claude plugin marketplace list
```

On Windows PowerShell:

```powershell
claude plugin install pstack@pstack-cross-platform
claude plugin marketplace list
```

If `claude` is not recognized, first use `~/.local/bin/claude` as shown above. If that file is missing, rerun the installer. To make `claude` work in future zsh sessions, run:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

On Linux, add the same line to `~/.bashrc` and run `source ~/.bashrc`. On Windows, reopen PowerShell after installation; if `claude` remains unavailable, rerun `irm https://claude.ai/install.ps1 | iex`.

A team repository or Claude Desktop cloud session cannot rely on a local installation from one computer. Add this configuration to the repository's `.claude/settings.json` to install and enable the plugin when a trusted repository session starts:

```json
{
  "extraKnownMarketplaces": {
    "pstack-cross-platform": {
      "source": {
        "source": "github",
        "repo": "lencshu/pstack-cross-platform"
      }
    }
  },
  "enabledPlugins": {
    "pstack@pstack-cross-platform": true
  }
}
```

Claude Desktop currently offers the plugin browser only in Local and SSH sessions. A locally installed plugin does not automatically appear in Cloud sessions. Cloud sessions need the repository configuration above. WSL sessions do not support plugins. Desktop also does not support Agent Teams. pstack uses ordinary plugin skills and subagents, so it does not require Agent Teams.

See the official [Claude Desktop](https://code.claude.com/docs/en/desktop), [plugin discovery and installation](https://code.claude.com/docs/en/discover-plugins), and [marketplace configuration](https://code.claude.com/docs/en/plugin-marketplaces) documentation.

### Unified post-installation checks

All three desktop clients should meet these conditions:

1. The plugin manager shows `pstack` as installed and enabled.
2. A new task or session can find the platform-specific `setup-pstack` and `poteto-mode` skills.
3. Initial setup creates `~/.pstack/<platform>-models.md`.
4. A mode skill can read project files, use the terminal, and launch subagents within the configured permissions.

If the first check fails, confirm that the marketplace is registered. If the second fails, restart the app and start a new task. For the third, check write access to the user directory. For the fourth, check the current project's terminal, file, and subagent permissions.

## How the adapter works

pstack has no resident process or conventional runtime code. `SKILL.md` files drive it. The client reads the name and description in the frontmatter, loads the body when needed, and the model follows that body to use file, terminal, MCP, and subagent tools. A discoverable manifest solves installation only. Full compatibility also requires translating the platform-specific meaning in the skill body.

The adapter layer handles five differences:

1. Plugin manifests. Cursor uses `.cursor-plugin/plugin.json`, Codex uses `.codex-plugin/plugin.json`, and Claude Code uses `.claude-plugin/plugin.json`.
2. Marketplace manifests. Codex finds `plugins/pstack` through `.agents/plugins/marketplace.json`. Claude Code finds `platforms/claude/pstack` through `.claude-plugin/marketplace.json`.
3. Skill invocation names. Codex generates `$pstack:<skill>`. Claude Code generates `/pstack:<skill>`.
4. Subagent protocols. The adapter translates Cursor's `Task`, `subagent_type`, `readonly`, and model slugs to Codex subagent and reasoning-effort semantics, or to Claude Code's `Agent`, model aliases, and explicit read-only prompts.
5. Client capabilities. Cursor-only `/loop`, `babysit`, `cursor-team-kit` control skills, rules directories, and transcript paths map to the target platform's available waiting, GitHub, browser, terminal, configuration, and task-history capabilities.

The generator injects a small platform contract into each target `SKILL.md`. `$pstack:setup-pstack` or `/pstack:setup-pstack` writes model selection to `~/.pstack/<platform>-models.md`. It does not modify the global rules of Codex or Claude Code.

## Directory boundaries

```text
skills/                              Cursor upstream skills and the sole source of behavior
agents/                              Cursor upstream agents
automations/                         Cursor-only Benny automation
adapters/codex.json                  Codex declarative substitutions and constraints
adapters/claude.json                 Claude Code declarative substitutions and constraints
adapters/*/overrides/                Files that cannot use a safe general substitution
scripts/build_adapters.py            Builds target packages and marketplace manifests
scripts/sync_cursor_upstream.py      Checks or synchronizes the Cursor upstream subdirectories
plugins/pstack/                      Generated Codex plugin. Do not edit by hand
platforms/claude/pstack/             Generated Claude Code plugin. Do not edit by hand
```

Claude Code can package `agents/poteto-agent.md` directly. The current Codex plugin manifest cannot distribute custom agent files. The Codex adapter therefore reduces it to a protocol that starts a worker and tells it to read Poteto Mode first. The core workflow remains intact.

Benny depends on Cursor Automations and Cursor Slack actions. It remains in the Cursor source and is not presented as a compatible component. Migrating it requires separate mappings to Codex Automations and Claude Code monitors or agent teams. That is a separate feature project.

## Synchronizing Cursor upstream

The default command compares files without writing them:

```powershell
python scripts/sync_cursor_upstream.py
```

Synchronize only after reviewing the differences:

```powershell
python scripts/sync_cursor_upstream.py --apply
```

`--apply` mirrors only `.cursor-plugin/`, `agents/`, `automations/`, `skills/`, `LICENSE`, and `README.md`. It does not overwrite `adapters/`, `scripts/`, tests, or generated marketplaces. It rebuilds the two target packages and records the upstream commit.

Every `--apply` run also stamps `.cursor-plugin/plugin.json` with this fork's lineage: the upstream `version` gets a `-N` fork-revision suffix, and `author.name` becomes `<upstream author> - Sylvain`. `N` resets to `1` when the upstream version itself changed since the last `--apply`, and increments otherwise (e.g. running `--apply` again for an adapter-only fix with no upstream version bump). The prior state lives in `adapters/upstream-lock.json`'s `upstreamVersion`/`forkRevision` fields, which `build_adapters.py` then reads through `.cursor-plugin/plugin.json`'s `version`/`author` into both generated manifests and marketplace files.

When upstream introduces a stable platform-coupled expression, add the rule to `adapters/<platform>.json` first. Put an override in `overrides/` only when a single file cannot be translated reliably. This keeps later sync conflicts in the adapter layer instead of spreading them through the skills.

## Build and verification

```powershell
python scripts/build_adapters.py
python scripts/build_adapters.py --check
python -m unittest discover -s tests -v
claude plugin validate platforms/claude/pstack --strict
claude plugin validate .claude-plugin/marketplace.json --strict
```

The Codex package uses the validator supplied by Codex `plugin-creator`. CI can call the same validator or the plugin validation entry point provided by the installed Codex client.
