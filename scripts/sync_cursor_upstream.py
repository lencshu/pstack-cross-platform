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
            if args.apply:
                lock = {
                    "repository": args.repo,
                    "ref": args.ref,
                    "subdirectory": args.subdir,
                    "commit": commit,
                }
                lock_path = ROOT / "adapters" / "upstream-lock.json"
                lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
                subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "update_readme.py")], check=True
                )
                subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "build_adapters.py")], check=True
                )
                print(f"Cursor source is current at {commit}; rebuilt both adapters.")
            else:
                print(f"Cursor source is current at {commit}.")
            return 0

        print(f"Cursor source differs from {args.repo}@{commit}:")
        for operation, path in changes:
            print(f"  {operation:6} {path}")
        if not args.apply:
            print("No files changed. Re-run with --apply to sync and rebuild adapters.")
            return 1

        mirror(upstream)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "update_readme.py")], check=True)
        lock = {
            "repository": args.repo,
            "ref": args.ref,
            "subdirectory": args.subdir,
            "commit": commit,
        }
        lock_path = ROOT / "adapters" / "upstream-lock.json"
        lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_adapters.py")], check=True)
        print(f"Synced Cursor source to {commit} and rebuilt both adapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
