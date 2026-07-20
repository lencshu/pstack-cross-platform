<!-- pstack-cross-platform:install:start -->
## install

### cursor

```text
/add-plugin pstack
```

### codex

```bash
codex plugin marketplace add lencshu/pstack-cross-platform
codex plugin add pstack@pstack-cross-platform
```

start a new task, then run `$pstack:setup-pstack` once and use `$pstack:poteto-mode` for rigorous work.

### claude code

```bash
claude plugin marketplace add lencshu/pstack-cross-platform
claude plugin install pstack@pstack-cross-platform
```

restart claude code after installation, run `/pstack:setup-pstack` once, then use `/pstack:poteto-mode`.

the codex and claude code editions are generated from the cursor source. the rest of this readme preserves the upstream cursor terminology and slash-command examples; the generated editions translate them to their native syntax. see [the cross-platform implementation notes](./CROSS_PLATFORM.md) for the adapter design, limitations, validation, and upstream-sync workflow.
<!-- pstack-cross-platform:install:end -->
