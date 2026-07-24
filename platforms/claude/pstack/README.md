# pstack for Claude Code

Generated from the Cursor pstack source at version `0.11.8-1`.
Do not edit this directory directly; change `adapters/claude.json` or an
override and run `python scripts/build_adapters.py` from the repository root.

After installation, start with:

```text
/pstack:setup-pstack
/pstack:poteto-mode <your task>
```

The core skills are shared with Cursor. Platform-specific paths, subagent calls,
model defaults, and unavailable built-ins are translated by the adapter build.
Cursor-only Benny automations are intentionally not packaged.
