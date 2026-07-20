#!/usr/bin/env python3
"""Apply the cross-platform install section to the upstream Cursor README."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OVERLAY = ROOT / "adapters" / "readme-install.md"
START = "<!-- pstack-cross-platform:install:start -->"
END = "<!-- pstack-cross-platform:install:end -->"


def expected_readme() -> str:
    current = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    overlay = OVERLAY.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if START in current and END in current:
        pattern = re.compile(
            re.escape(START) + r".*?" + re.escape(END) + r"\s*(?=## get started)",
            re.DOTALL,
        )
    else:
        pattern = re.compile(r"## install\n.*?\s*(?=## get started)", re.DOTALL)
    updated, count = pattern.subn(overlay + "\n\n", current, count=1)
    if count != 1:
        raise ValueError("README install section or adapter markers were not found exactly once")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when README overlay is stale")
    args = parser.parse_args()
    expected = expected_readme()
    actual = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    if args.check:
        if actual != expected:
            print("README cross-platform install section is stale.", file=sys.stderr)
            print("Run: python scripts/update_readme.py", file=sys.stderr)
            return 1
        print("README cross-platform install section is current.")
        return 0
    README.write_text(expected, encoding="utf-8", newline="\n")
    print("Updated README cross-platform install section.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
