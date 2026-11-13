#!/usr/bin/env python3
"""File-placement checks for the unified installer. No network."""

import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import setup_kit  # noqa: E402


class InstallTests(unittest.TestCase):
    def test_detects_only_existing_homes(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            (home / ".cursor").mkdir()
            (home / ".hermes").mkdir()
            self.assertEqual(setup_kit.detect_agents(home, None), ["hermes", "cursor"])

    def test_explicit_agent(self):
        self.assertEqual(setup_kit.detect_agents(Path("/tmp"), "codex"), ["codex"])

    def test_due_after_three_days(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            os.environ["XDG_DATA_HOME"] = str(home / "xdg")
            try:
                self.assertTrue(setup_kit.is_due(home))
                setup_kit.write_stamp(home)
                self.assertFalse(setup_kit.is_due(home))
                old = datetime.now(timezone.utc) - timedelta(days=3, minutes=1)
                setup_kit.stamp_path(home).write_text(old.isoformat())
                self.assertTrue(setup_kit.is_due(home))
            finally:
                os.environ.pop("XDG_DATA_HOME", None)

    def test_cursor_and_hermes_files(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            target = home / "proj"
            kit = ROOT
            for agent in ("cursor", "hermes"):
                setup_kit.install_kit(agent, kit, target, home)
            self.assertTrue((home / ".cursor" / "rules" / "coding-agent-kit.mdc").is_file())
            self.assertTrue((home / ".hermes" / "skills" / "using-this-kit" / "SKILL.md").is_file())
            self.assertTrue((home / ".hermes" / "skills" / "avenox-kit" / "SKILL.md").is_file())
            again = setup_kit.install_kit("hermes", kit, target, home)
            self.assertTrue(any(line.endswith("unchanged") for line in again))


class CliTests(unittest.TestCase):
    def test_if_due_exits_quietly(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            stamp = home / ".local" / "share" / "avenox-kit"
            stamp.mkdir(parents=True)
            (stamp / "last-check").write_text(datetime.now(timezone.utc).isoformat())
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "setup_kit.py"), "--if-due", "--home", str(home), "--no-cron", "--skip-beyin", "--no-update"],
                text=True, capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("not due", proc.stdout)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
