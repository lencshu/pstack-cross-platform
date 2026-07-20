from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class AdapterBuildTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_adapters.py"), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_versions_follow_cursor_manifest(self) -> None:
        cursor = load(ROOT / ".cursor-plugin" / "plugin.json")
        codex = load(ROOT / "plugins" / "pstack" / ".codex-plugin" / "plugin.json")
        claude = load(ROOT / "platforms" / "claude" / "pstack" / ".claude-plugin" / "plugin.json")
        self.assertEqual(cursor["name"], codex["name"])
        self.assertEqual(cursor["name"], claude["name"])
        self.assertEqual(cursor["version"], codex["version"])
        self.assertEqual(cursor["version"], claude["version"])

    def test_every_source_skill_is_packaged(self) -> None:
        source = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        for package in (ROOT / "plugins" / "pstack", ROOT / "platforms" / "claude" / "pstack"):
            packaged = {path.parent.name for path in (package / "skills").glob("*/SKILL.md")}
            self.assertEqual(source, packaged)

    def test_platform_component_boundaries(self) -> None:
        codex = ROOT / "plugins" / "pstack"
        claude = ROOT / "platforms" / "claude" / "pstack"
        self.assertFalse((codex / "agents").exists())
        self.assertTrue((claude / "agents" / "poteto-agent.md").is_file())
        self.assertFalse((codex / "automations").exists())
        self.assertFalse((claude / "automations").exists())

    def test_codex_frontmatter_and_adapter_contract(self) -> None:
        for path in (ROOT / "plugins" / "pstack" / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("<!-- pstack-adapter:codex -->", text, path)
            self.assertNotIn("disable-model-invocation: true", text, path)

    def test_marketplaces_resolve_to_packages(self) -> None:
        codex = load(ROOT / ".agents" / "plugins" / "marketplace.json")
        claude = load(ROOT / ".claude-plugin" / "marketplace.json")
        self.assertEqual(codex["plugins"][0]["name"], "pstack")
        self.assertEqual(claude["plugins"][0]["name"], "pstack")
        self.assertTrue((ROOT / codex["plugins"][0]["source"]["path"]).is_dir())
        self.assertTrue((ROOT / claude["plugins"][0]["source"]).is_dir())


if __name__ == "__main__":
    unittest.main()
