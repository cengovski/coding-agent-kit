#!/usr/bin/env python3
"""File-placement checks for the unified installer. No network."""

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
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
            self.assertTrue(all(line.endswith("unchanged") for line in again), again)

    def test_no_project_files_without_target(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            for agent in setup_kit.AGENTS:
                setup_kit.install_kit(agent, ROOT, None, home)
            self.assertFalse((home / "CLAUDE.md").exists())
            self.assertFalse((home / "AGENTS.md").exists())
            self.assertFalse((home / ".github").exists())
            rule = (home / ".cursor" / "rules" / "coding-agent-kit.mdc").read_text()
            self.assertIn(str(ROOT / "AGENTS.md"), rule)
            self.assertIn(str(ROOT / "AGENTS.md"), (home / ".codex" / "AGENTS.md").read_text())

    def test_project_files_with_target(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            target = home / "proj"
            for agent in ("claude", "codex", "copilot", "cursor"):
                setup_kit.install_kit(agent, ROOT, target, home)
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".github" / "copilot-instructions.md").is_file())
            self.assertTrue((target / ".cursor" / "rules" / "coding-agent-kit.mdc").is_file())
            first = (target / "AGENTS.md").read_text()
            setup_kit.install_kit("codex", ROOT, target, home)
            self.assertEqual(first, (target / "AGENTS.md").read_text())


class BeyinPackageTests(unittest.TestCase):
    def make_zip(self, path, entries, symlink=None):
        with zipfile.ZipFile(path, "w") as zf:
            for name in entries:
                zf.writestr(name, "x")
            if symlink:
                info = zipfile.ZipInfo(symlink)
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                zf.writestr(info, "/etc/passwd")

    def test_safe_extract_accepts_release_layout(self):
        with tempfile.TemporaryDirectory() as raw:
            z = Path(raw) / "p.zip"
            self.make_zip(z, ["manifest.json", "scripts/install_v3.py"])
            out = setup_kit.safe_extract(z, Path(raw) / "out")
            self.assertTrue((out / "scripts" / "install_v3.py").is_file())

    def test_safe_extract_rejects_escape_and_symlink(self):
        with tempfile.TemporaryDirectory() as raw:
            for bad in (dict(entries=["manifest.json", "../evil"]), dict(entries=["manifest.json"], symlink="s")):
                z = Path(raw) / "bad.zip"
                self.make_zip(z, **bad)
                with self.assertRaises(SystemExit):
                    setup_kit.safe_extract(z, Path(raw) / "out2")

    def test_checksum(self):
        with tempfile.TemporaryDirectory() as raw:
            z = Path(raw) / "p.zip"
            z.write_bytes(b"abc")
            good = hashlib.sha256(b"abc").hexdigest()
            setup_kit.verify_sha256(z, f"{good}  p.zip\n")
            with self.assertRaises(SystemExit):
                setup_kit.verify_sha256(z, "0" * 64 + "  p.zip")


class CronTests(unittest.TestCase):
    def test_cron_points_at_kit_and_vault(self):
        home = Path("/home/u")
        kit = Path("/home/u/.local/share/avenox-kit/coding-agent-kit")
        line = setup_kit.cron_line(home, kit, Path("/home/u/My Notes"), "cursor", False)
        self.assertIn(str(kit / "scripts" / "setup_kit.py"), line)
        self.assertIn("--if-due", line)
        self.assertIn("'/home/u/My Notes'", line)
        self.assertIn("--agent cursor", line)
        self.assertTrue(line.endswith(setup_kit.CRON_MARK))


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
