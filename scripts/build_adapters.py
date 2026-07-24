#!/usr/bin/env python3
"""Build installable Codex and Claude Code packages from the Cursor source tree.

The repository root is the upstream-compatible Cursor source. Platform packages are
generated artifacts: never edit them directly. Put systematic differences in
adapters/<platform>.json and exceptional files in adapters/<platform>/overrides/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "adapters"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".tsv", ".sh", ".toml"}
PLATFORMS = ("codex", "claude")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def source_manifest() -> dict[str, Any]:
    return load_json(ROOT / ".cursor-plugin" / "plugin.json")


def skill_names() -> list[str]:
    return sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))


def platform_banner(config: dict[str, Any]) -> str:
    if config["platform"] == "codex":
        contract = (
            "This is the generated Codex edition. Before selecting a subagent model, read "
            f"`{config['config_path']}` when it exists. Use Codex subagent tools, spawn "
            "independent agents before waiting, and express read-only work as an explicit "
            "no-write instruction. If a source instruction names a Cursor-only primitive, "
            "use the closest capability exposed by the current Codex session."
        )
    else:
        contract = (
            "This is the generated Claude Code edition. Before selecting an Agent model, "
            f"read `{config['config_path']}` when it exists. Use the current `Agent` tool, "
            "run independent agents in parallel, and preserve MCP access by expressing "
            "read-only work as an explicit no-write instruction instead of a restrictive "
            "tool allowlist."
        )
    return f"\n<!-- pstack-adapter:{config['platform']} -->\n> **Platform adapter.** {contract}\n"


def inject_banner(text: str, config: dict[str, Any]) -> str:
    if not text.startswith("---\n"):
        return platform_banner(config).lstrip() + "\n" + text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not terminated")
    insertion = end + len("\n---\n")
    return text[:insertion] + platform_banner(config) + text[insertion:]


def replace_invocations(text: str, config: dict[str, Any]) -> str:
    prefix = config["invocation_prefix"]
    for name in skill_names():
        pattern = re.compile(rf"(?<![\w./-])/{re.escape(name)}(?![\w/-])")
        text = pattern.sub(prefix + name, text)
    return text


def transform_text(text: str, config: dict[str, Any]) -> str:
    replacements: dict[str, str] = {}
    replacements.update(config["model_replacements"])
    replacements.update(config["text_replacements"])
    for old in sorted(replacements, key=len, reverse=True):
        text = text.replace(old, replacements[old])

    text = replace_invocations(text, config)
    if config["platform"] == "codex":
        text = re.sub(
            r"Transcripts live at `~/.Codex/projects/<slug>/agent-transcripts/<uuid>/<uuid>\.jsonl`,.*?Every line is one chat message\.",
            "Codex does not expose a stable transcript filesystem contract to plugins. "
            "Prefer task or thread listing and reading tools exposed by the current client, "
            "scoped to the active workspace. If those tools are unavailable, reconstruct "
            "context from the current conversation and live repository state, disclose that "
            "older task history could not be queried, and never crawl unrelated task data.",
            text,
        )
        # Codex plugin ingestion currently requires plugin-bundled skills to remain
        # model-invocable even when the Cursor source marks a slash-only workflow.
        # Match only a real frontmatter line (bare key: value, nothing else on the
        # line) so prose that quotes the key inline — e.g. automate-me instructing
        # agents what to write into a *newly generated* skill's frontmatter — is
        # left untouched instead of being flipped into self-contradictory guidance.
        text = re.sub(
            r"^disable-model-invocation: true$",
            "disable-model-invocation: false",
            text,
            flags=re.MULTILINE,
        )
        text = text.replace(
            "different model family from the parent's",
            "different available model or reasoning profile from the parent's",
        )
        text = text.replace(
            "different model family from the one that did the work",
            "different available model or reasoning profile from the one that did the work",
        )
        text = text.replace(
            "different model family",
            "different available model or reasoning profile",
        )
        text = text.replace(
            "- Shipping UI / IDE / CLI → the matching control skill. equivalent Codex verification tooling publishes `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs).",
            "- Shipping UI / IDE / CLI → use the browser, image, terminal, or app-control capability exposed by the current Codex session.",
        )
        text = text.replace(
            "the `control-ui` skill from the environment's equivalent verification tooling",
            "the browser or app-control capability exposed by the current Codex session",
        )
        text = text.replace(
            "the `control-cli` skill from the environment's equivalent verification tooling",
            "the terminal-control capability exposed by the current Codex session",
        )
        text = text.replace(
            "Triage fix / dismiss / ask via the built-in **babysit** skill.",
            "Triage each finding as fix, dismiss, or ask; monitor follow-up checks with the available GitHub and wait tools.",
        )
        text = text.replace(
            "**Use a worker subagent explicitly instructed to read `$pstack:poteto-mode` before acting for any subagent you spawn inside a playbook step**",
            "**For every playbook subagent, use a worker and explicitly instruct it to read `$pstack:poteto-mode` before acting**",
        )
        text = text.replace(
            "`$pstack:poteto-mode` and `poteto-agent` route through the same wrapper.",
            "The main skill and primed worker follow the same workflow.",
        )
        text = text.replace("don't override to `poteto-agent`", "don't override their prescribed role")
        text = text.replace("`$pstack:setup-pstack` rule", "`$pstack:setup-pstack` configuration")
        text = text.replace("the `$pstack:setup-pstack` rule", "the `$pstack:setup-pstack` configuration")
        text = text.replace("Task tool's error message", "current `spawn_agent` tool metadata")
    else:
        text = re.sub(
            r"Transcripts live at `~/.Claude Code/projects/<slug>/agent-transcripts/<uuid>/<uuid>\.jsonl`,.*?Every line is one chat message\.",
            "Claude Code stores project sessions under "
            "`~/.claude/projects/<encoded-workspace>/<session-id>.jsonl`. Resolve only the "
            "active workspace directory, order sessions by real modification time, and never "
            "scan unrelated project directories.",
            text,
        )
        text = text.replace("different model family", "different available Claude model tier")
        text = text.replace("model family differs", "model tier differs")
        text = text.replace(
            "- Shipping UI / IDE / CLI → the matching control skill. equivalent Claude Code verification tooling publishes `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs).",
            "- Shipping UI / IDE / CLI → use Claude Code's browser/MCP tools for UI surfaces and Bash or PowerShell for CLIs and TUIs.",
        )
        text = text.replace(
            "the `control-ui` skill from equivalent Claude Code verification tooling",
            "the browser or MCP UI-control tools available in Claude Code",
        )
        text = text.replace(
            "the `control-cli` skill from equivalent Claude Code verification tooling",
            "Bash or PowerShell control in Claude Code",
        )
        text = text.replace(
            "Triage fix / dismiss / ask via the built-in **babysit** skill.",
            "Triage each finding as fix, dismiss, or ask; then monitor PR checks with available GitHub tools.",
        )
        text = text.replace(
            "**Use `agent type: \"poteto-agent\"` for any subagent you spawn inside a playbook step**",
            "**Use the plugin-provided `poteto-agent` for any subagent you spawn inside a playbook step**",
        )
        text = text.replace("`/pstack:setup-pstack` rule", "`/pstack:setup-pstack` configuration")
        text = text.replace("the `/pstack:setup-pstack` rule", "the `/pstack:setup-pstack` configuration")
        text = text.replace("Task tool's error message", "current `Agent` tool metadata")

    text = text.replace(
        "- `readonly`: `true`",
        "- posture: explicitly read-only in the subagent prompt; do not remove inherited tools",
    )
    text = text.replace(
        "- `readonly`: `false` (agent mode). **Do not use an overly restrictive tool allowlist.** It strips MCP access",
        "- posture: normal inherited tools with an explicit no-write instruction. Do not use an overly restrictive tool allowlist because it removes MCP access",
    )
    text = text.replace(
        "- `readonly`: `false` (agent mode). **Do not use a restrictive sandbox.** It strips MCP access",
        "- posture: normal inherited tools with an explicit no-write instruction. Do not use a restrictive sandbox because it may remove connector access",
    )
    text = text.replace(
        "- `readonly`: `false` (agent mode). The synthesizer's",
        "- posture: normal inherited tools with an explicit no-write instruction. The synthesizer's",
    )
    text = text.replace("a restrictive sandbox may remove required connector access and defeats that", "a restrictive sandbox may remove required connector access and defeat that")
    text = text.replace("an overly restrictive tool allowlist removes MCP access and defeats that", "an overly restrictive tool allowlist removes MCP access and defeats that check")
    return text


def copy_and_transform(source: Path, destination: Path, config: dict[str, Any]) -> None:
    if source.is_dir():
        for child in sorted(source.rglob("*")):
            if child.is_dir():
                continue
            relative = child.relative_to(source)
            copy_and_transform(child, destination / relative, config)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in TEXT_SUFFIXES or source.name == "SKILL.md":
        text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        text = transform_text(text, config)
        if source.name == "SKILL.md":
            text = inject_banner(text, config)
        destination.write_text(text, encoding="utf-8", newline="\n")
    else:
        shutil.copy2(source, destination)


def apply_overrides(output: Path, config: dict[str, Any]) -> None:
    override_root = ADAPTERS / config["platform"] / "overrides"
    if not override_root.exists():
        return
    for source in sorted(override_root.rglob("*")):
        if source.is_dir():
            continue
        destination = output / source.relative_to(override_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        if source.name == "SKILL.md":
            text = inject_banner(text, config)
        destination.write_text(text, encoding="utf-8", newline="\n")


def codex_manifest(upstream: dict[str, Any], distribution: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": upstream["name"],
        "version": upstream["version"],
        "description": upstream["description"],
        "author": upstream["author"],
        "homepage": distribution["homepage"],
        "repository": distribution["repository"],
        "license": upstream["license"],
        "keywords": upstream["keywords"] + ["codex"],
        "skills": "./skills/",
        "interface": {
            "displayName": "pstack",
            "shortDescription": "Rigorous, verifiable engineering workflows for Codex",
            "longDescription": (
                "A generated Codex edition of pstack with platform-aware subagent, model, "
                "skill-path, and monitoring instructions."
            ),
            "developerName": upstream["author"]["name"],
            "category": "Developer Tools",
            "capabilities": ["Skills", "Multi-agent", "Code review"],
            "websiteURL": distribution["homepage"],
            "defaultPrompt": [
                "Use pstack to handle this task with rigorous verification.",
                "Review this change with pstack and look for hidden risks."
            ],
        },
    }


def claude_manifest(upstream: dict[str, Any], distribution: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
        "name": upstream["name"],
        "version": upstream["version"],
        "description": upstream["description"],
        "author": upstream["author"],
        "homepage": distribution["homepage"],
        "repository": distribution["repository"],
        "license": upstream["license"],
        "keywords": upstream["keywords"] + ["claude-code"],
    }


def package_readme(config: dict[str, Any], upstream: dict[str, Any]) -> str:
    if config["platform"] == "codex":
        invoke = "$pstack:setup-pstack\n$pstack:poteto-mode <your task>"
    else:
        invoke = "/pstack:setup-pstack\n/pstack:poteto-mode <your task>"
    return f"""# pstack for {config['display_name']}

Generated from the Cursor pstack source at version `{upstream['version']}`.
Do not edit this directory directly; change `adapters/{config['platform']}.json` or an
override and run `python scripts/build_adapters.py` from the repository root.

After installation, start with:

```text
{invoke}
```

The core skills are shared with Cursor. Platform-specific paths, subagent calls,
model defaults, and unavailable built-ins are translated by the adapter build.
Cursor-only Benny automations are intentionally not packaged.
"""


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(config: dict[str, Any], upstream: dict[str, Any]) -> dict[str, Any]:
    tracked = [ROOT / ".cursor-plugin" / "plugin.json"]
    for include in config["include"]:
        source = ROOT / include
        if source.is_file():
            tracked.append(source)
        else:
            tracked.extend(path for path in source.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(tracked):
        relative = path.relative_to(ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_hash(path)))
    result = {
        "generated": True,
        "generator": "scripts/build_adapters.py",
        "platform": config["platform"],
        "source": "Cursor pstack tree at repository root",
        "sourceVersion": upstream["version"],
        "sourceDigest": digest.hexdigest(),
    }
    lock_path = ADAPTERS / "upstream-lock.json"
    if lock_path.exists():
        lock = load_json(lock_path)
        result["upstreamRepository"] = lock["repository"]
        result["upstreamCommit"] = lock["commit"]
    return result


def validate_generated(output: Path, config: dict[str, Any]) -> None:
    failures: list[str] = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in config["forbidden_patterns"]:
            if pattern in text:
                failures.append(f"{path.relative_to(output)} contains forbidden token {pattern!r}")
    if failures:
        raise ValueError("\n".join(failures))


def build_package(
    staging_root: Path,
    config: dict[str, Any],
    upstream: dict[str, Any],
    distribution: dict[str, Any],
) -> Path:
    output = staging_root / config["output"]
    for include in config["include"]:
        copy_and_transform(ROOT / include, output / include, config)
    apply_overrides(output, config)

    manifest = (
        codex_manifest(upstream, distribution)
        if config["platform"] == "codex"
        else claude_manifest(upstream, distribution)
    )
    manifest_path = output / config["manifest_dir"] / "plugin.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(dump_json(manifest), encoding="utf-8", newline="\n")
    (output / "README.md").write_text(
        package_readme(config, upstream), encoding="utf-8", newline="\n"
    )
    (output / "ADAPTER_SOURCE.json").write_text(
        dump_json(provenance(config, upstream)), encoding="utf-8", newline="\n"
    )
    validate_generated(output, config)
    return output


def marketplace_files(upstream: dict[str, Any]) -> dict[str, str]:
    codex = {
        "name": "pstack-cross-platform",
        "interface": {"displayName": "pstack cross-platform"},
        "plugins": [
            {
                "name": "pstack",
                "source": {"source": "local", "path": "./plugins/pstack"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            }
        ],
    }
    claude = {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": "pstack-cross-platform",
        "version": upstream["version"],
        "description": "Cross-platform pstack packages generated from the Cursor source",
        "owner": upstream["author"],
        "plugins": [
            {
                "name": "pstack",
                "source": "./platforms/claude/pstack",
                "description": upstream["description"],
                "version": upstream["version"],
                "author": upstream["author"],
                "category": "development",
            }
        ],
    }
    return {
        ".agents/plugins/marketplace.json": dump_json(codex),
        ".claude-plugin/marketplace.json": dump_json(claude),
    }


def snapshot(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def replace_tree(source: Path, destination: Path) -> None:
    resolved = destination.resolve()
    if ROOT.resolve() not in resolved.parents:
        raise ValueError(f"refusing to replace path outside repository: {resolved}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    parser.add_argument("--platform", choices=PLATFORMS, action="append")
    args = parser.parse_args()

    selected = tuple(args.platform or PLATFORMS)
    upstream = source_manifest()
    distribution = load_json(ADAPTERS / "distribution.json")
    with tempfile.TemporaryDirectory(prefix="pstack-adapters-") as temporary:
        staging = Path(temporary)
        built: dict[str, Path] = {}
        configs: dict[str, dict[str, Any]] = {}
        for platform in selected:
            config = load_json(ADAPTERS / f"{platform}.json")
            configs[platform] = config
            built[platform] = build_package(staging, config, upstream, distribution)

        marketplaces = marketplace_files(upstream)
        if args.check:
            stale: list[str] = []
            for platform in selected:
                destination = ROOT / configs[platform]["output"]
                if snapshot(built[platform]) != snapshot(destination):
                    stale.append(configs[platform]["output"])
            if set(selected) == set(PLATFORMS):
                for relative, expected in marketplaces.items():
                    path = ROOT / relative
                    actual = path.read_text(encoding="utf-8") if path.exists() else None
                    if actual != expected:
                        stale.append(relative)
            if stale:
                print("Generated adapter artifacts are stale:", file=sys.stderr)
                for item in stale:
                    print(f"  - {item}", file=sys.stderr)
                print("Run: python scripts/build_adapters.py", file=sys.stderr)
                return 1
            print("Generated adapter artifacts are current.")
            return 0

        for platform in selected:
            replace_tree(built[platform], ROOT / configs[platform]["output"])
        if set(selected) == set(PLATFORMS):
            for relative, content in marketplaces.items():
                path = ROOT / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
        print("Built: " + ", ".join(configs[p]["output"] for p in selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
