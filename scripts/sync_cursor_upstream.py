#!/usr/bin/env python3
"""Compare or sync the canonical Cursor pstack tree, then rebuild adapters.

The default mode is read-only. Pass --apply to mirror only the declared upstream
paths; adapter configs, generated marketplaces, scripts, and tests are never touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_PATHS = (
    ".cursor-plugin",
    "agents",
    "automations",
    "skills",
    "LICENSE",
    "README.md",
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".sh", ".tsv", ".txt"}
README_START = "<!-- pstack-cross-platform:install:start -->"
README_END = "<!-- pstack-cross-platform:install:end -->"

# This fork republishes Cursor's upstream pstack as Codex and Claude Code
# packages. `stamp_fork_identity` marks that lineage on every --apply: the
# upstream semver gets a "-N" fork-revision suffix (reset to 1 whenever the
# upstream version itself changes, incremented otherwise), and the upstream
# author is credited alongside the fork maintainer.
FORK_MAINTAINER = "Sylvain"


def run(*args: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def files(root: Path, relative: str) -> dict[str, str]:
    target = root / relative
    if not target.exists():
        return {}
    candidates = [target] if target.is_file() else [p for p in target.rglob("*") if p.is_file()]
    result: dict[str, str] = {}
    for path in candidates:
        key = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if path.suffix.lower() in TEXT_SUFFIXES or path.name == "LICENSE":
            # Git's autocrlf may materialize the same upstream file differently on
            # Windows. Compare canonical LF bytes so check mode reports content drift.
            data = data.replace(b"\r\n", b"\n")
        if key == "README.md":
            text = data.decode("utf-8")
            if README_START in text and README_END in text:
                pattern = re.compile(
                    re.escape(README_START) + r".*?" + re.escape(README_END), re.DOTALL
                )
            else:
                pattern = re.compile(r"## install\n.*?(?=\n## get started)", re.DOTALL)
            text, count = pattern.subn("## install\n<cross-platform-install-overlay>", text, count=1)
            if count != 1:
                raise ValueError(f"README install section not found in {path}")
            data = text.encode("utf-8")
        result[key] = hashlib.sha256(data).hexdigest()
    return result


def diff(local: Path, upstream: Path) -> list[tuple[str, str]]:
    changes: list[tuple[str, str]] = []
    for relative in UPSTREAM_PATHS:
        before = files(local, relative)
        after = files(upstream, relative)
        for path in sorted(after.keys() - before.keys()):
            changes.append(("add", path))
        for path in sorted(before.keys() - after.keys()):
            changes.append(("delete", path))
        for path in sorted(before.keys() & after.keys()):
            if before[path] != after[path]:
                changes.append(("modify", path))
    return changes


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def stamp_fork_identity(
    root: Path, previous_upstream_version: str | None, previous_fork_revision: int
) -> tuple[str, int]:
    """Rewrite .cursor-plugin/plugin.json's version and author with fork lineage.

    Idempotent: safe to call whether plugin.json currently holds a bare
    upstream version (freshly mirrored) or an already-stamped one (the
    no-diff --apply path, where mirror() never ran this cycle).
    """
    plugin_path = root / ".cursor-plugin" / "plugin.json"
    text = plugin_path.read_text(encoding="utf-8")

    version_match = re.search(r'"version":\s*"([^"]+)"', text)
    if not version_match:
        raise ValueError("plugin.json is missing a version field")
    raw_version = version_match.group(1)
    upstream_version = re.sub(r"-\d+$", "", raw_version)

    if previous_upstream_version == upstream_version:
        fork_revision = previous_fork_revision + 1
    else:
        fork_revision = 1

    text = text.replace(
        f'"version": "{raw_version}"',
        f'"version": "{upstream_version}-{fork_revision}"',
        1,
    )

    author_pattern = re.compile(r'("author":\s*\{\s*\n\s*"name":\s*")([^"]+)(")')
    author_match = author_pattern.search(text)
    if not author_match:
        raise ValueError("plugin.json is missing an author.name field")
    upstream_author = re.sub(rf" - {re.escape(FORK_MAINTAINER)}$", "", author_match.group(2))
    text = author_pattern.sub(
        lambda m: f"{m.group(1)}{upstream_author} - {FORK_MAINTAINER}{m.group(3)}",
        text,
        count=1,
    )

    plugin_path.write_text(text, encoding="utf-8")
    return upstream_version, fork_revision


def mirror(upstream: Path) -> None:
    root_resolved = ROOT.resolve()
    for relative in UPSTREAM_PATHS:
        source = upstream / relative
        destination = ROOT / relative
        resolved = destination.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            raise ValueError(f"refusing to write outside repository: {resolved}")
        if not source.exists():
            raise FileNotFoundError(f"upstream path is missing: {relative}")
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="mirror upstream paths and rebuild")
    parser.add_argument("--repo", default="https://github.com/cursor/plugins.git")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--subdir", default="pstack")
    args = parser.parse_args()

    lock_path = ROOT / "adapters" / "upstream-lock.json"
    previous_lock = load_json(lock_path) if lock_path.exists() else {}

    with tempfile.TemporaryDirectory(prefix="pstack-upstream-") as temporary:
        checkout = Path(temporary) / "cursor-plugins"
        run(
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            "--branch",
            args.ref,
            args.repo,
            str(checkout),
        )
        run("git", "sparse-checkout", "set", args.subdir, cwd=checkout)
        upstream = checkout / args.subdir
        if not upstream.is_dir():
            raise FileNotFoundError(f"upstream subdirectory not found: {args.subdir}")
        commit = run("git", "rev-parse", "HEAD", cwd=checkout)
        changes = diff(ROOT, upstream)

        if not changes:
            print(f"Cursor source is current at {commit}.")
            if not args.apply:
                return 0
        else:
            print(f"Cursor source differs from {args.repo}@{commit}:")
            for operation, path in changes:
                print(f"  {operation:6} {path}")
            if not args.apply:
                print("No files changed. Re-run with --apply to sync and rebuild adapters.")
                return 1
            mirror(upstream)

        upstream_version, fork_revision = stamp_fork_identity(
            ROOT,
            previous_lock.get("upstreamVersion"),
            previous_lock.get("forkRevision", 0),
        )
        subprocess.run([sys.executable, str(ROOT / "scripts" / "update_readme.py")], check=True)
        lock = {
            "repository": args.repo,
            "ref": args.ref,
            "subdirectory": args.subdir,
            "commit": commit,
            "upstreamVersion": upstream_version,
            "forkRevision": fork_revision,
        }
        lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_adapters.py")], check=True)
        print(
            f"Synced Cursor source to {commit} "
            f"(pstack {upstream_version}-{fork_revision})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
