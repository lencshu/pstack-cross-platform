---
name: setup-pstack
description: Configure which Claude Code models pstack uses per role. Detects supported model aliases and writes a small pstack configuration file.
---

<!-- pstack-adapter:claude -->
> **Platform adapter.** This is the generated Claude Code edition. Before selecting an Agent model, read `~/.pstack/claude-models.md` when it exists. Use the current `Agent` tool, run independent agents in parallel, and preserve MCP access by expressing read-only work as an explicit no-write instruction instead of a restrictive tool allowlist.

# Setup pstack for Claude Code

Write `~/.pstack/claude-models.md`. This is an explicit pstack configuration file. Generated Claude Code skills know to read it whenever they select an Agent model.

## Steps

1. Detect model aliases accepted by the current Claude Code `Agent` tool. Prefer the stable `opus`, `sonnet`, `haiku`, and `inherit` aliases when available. Never invent a full model ID.
2. If `~/.pstack/claude-models.md` exists, read it as the current configuration. Otherwise start from the defaults below.
3. Show every role and its current model. Ask with `AskUserQuestion` only when the user wants different choices or a configured value is unavailable.
4. Validate every selected alias against the current Claude Code session.
5. Create `~/.pstack/` if necessary and overwrite `claude-models.md` atomically so reruns are idempotent.

```md
# pstack Claude Code model configuration
# Delete a line to use the generated skill's inline default.
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: opus
how explorer: sonnet
how explainer: opus
how critics: opus, sonnet, haiku
why investigators: sonnet
why synthesizer: opus
reflect tooling: sonnet
reflect judgment, divergent, synthesizer: opus
arena runners: opus, sonnet, haiku
arena cross-judge pool: opus, sonnet, haiku
architect runners: opus, sonnet, haiku
interrogate reviewers: opus, sonnet, haiku
```

6. Tell the user the file applies the next time a pstack skill delegates work. Re-running this skill updates it.
