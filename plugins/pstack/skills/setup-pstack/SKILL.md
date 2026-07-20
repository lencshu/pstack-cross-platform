---
name: setup-pstack
description: Configure which Codex models and reasoning efforts pstack uses per role. Detects the models exposed by the current Codex subagent tools and writes a small pstack configuration file.
---

<!-- pstack-adapter:codex -->
> **Platform adapter.** This is the generated Codex edition. Before selecting a subagent model, read `~/.pstack/codex-models.md` when it exists. Use Codex subagent tools, spawn independent agents before waiting, and express read-only work as an explicit no-write instruction. If a source instruction names a Cursor-only primitive, use the closest capability exposed by the current Codex session.

# Setup pstack for Codex

Write `~/.pstack/codex-models.md`. This is an explicit pstack configuration file, not a Codex global rule. Generated Codex skills know to read it whenever they select a subagent model.

## Steps

1. Inspect the current subagent tool metadata and list only model and reasoning-effort values that the current Codex session accepts. Do not guess private or unavailable model identifiers.
2. If `~/.pstack/codex-models.md` exists, read it as the current configuration. Otherwise start from the defaults below.
3. Show every role and its current model/effort. Ask for input only when the user wants different choices or a configured value is unavailable.
4. Validate every selected model and reasoning effort against the current tool metadata.
5. Create `~/.pstack/` if necessary and overwrite `codex-models.md` atomically so reruns are idempotent.

```md
# pstack Codex model configuration
# Delete a line to use the generated skill's inline default.
feature, refactoring: gpt-5.6-terra / medium
bug-fix: gpt-5.6-sol / high
perf-issue: gpt-5.6-sol / high
hillclimb: gpt-5.6-sol / high
judgment and prose: gpt-5.6-sol / high
hardest tasks: gpt-5.6-sol / max
how explorer: gpt-5.6-terra / medium
how explainer: gpt-5.6-sol / high
how critics: gpt-5.6-sol / high, gpt-5.6-terra / medium
why investigators: gpt-5.6-terra / medium
why synthesizer: gpt-5.6-sol / high
reflect tooling: gpt-5.6-terra / medium
reflect judgment, divergent, synthesizer: gpt-5.6-sol / high
arena runners: gpt-5.6-sol / high, gpt-5.6-terra / medium
arena cross-judge pool: gpt-5.6-sol / high, gpt-5.6-terra / medium
architect runners: gpt-5.6-sol / high, gpt-5.6-terra / medium
interrogate reviewers: gpt-5.6-sol / high, gpt-5.6-terra / medium
```

6. Tell the user the file applies the next time a pstack skill delegates work. Re-running this skill updates it.
