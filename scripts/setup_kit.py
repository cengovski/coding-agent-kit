#!/usr/bin/env python3
"""Install coding-agent-kit and AvenoxBeyin for the agent that is present.

Every run updates both checkouts first. After install, a daily cron calls
--if-due, which updates only when the last check is at least 3 days old.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KIT_REPO = "https://github.com/cengovski/coding-agent-kit.git"
BEYIN_REPO = "https://github.com/avenoxai/avenoxbeyin.git"
STAMP_NAME = "last-check"
CRON_MARK = "# avenox-kit-3day"
CHECK_DAYS = 3

AGENTS = ("hermes", "claude", "cursor", "codex", "copilot", "opencode", "pi", "kiro")


def data_root(home: Path) -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base) if base else home / ".local" / "share"
    return root / "avenox-kit"


def say(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def git(repo: Path, *args: str) -> None:
    proc = run(["git", "-C", str(repo), *args])
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "git failed").strip()
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {detail}")


def ensure_clone(url: str, dest: Path, update: bool) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").is_dir():
        proc = run(["git", "clone", "--depth", "1", url, str(dest)])
        if proc.returncode != 0:
            raise SystemExit((proc.stderr or proc.stdout or "clone failed").strip())
    elif update:
        git(dest, "pull", "--ff-only")
    return dest


def detect_agents(home: Path, explicit: str | None) -> list[str]:
    if explicit and explicit != "auto":
        if explicit not in AGENTS:
            raise SystemExit(f"unknown agent {explicit!r}; choose from {', '.join(AGENTS)}")
        return [explicit]
    env = os.environ.get("AVENOX_AGENT", "").strip().lower()
    if env in AGENTS:
        return [env]
    found = []
    homes = {
        "hermes": Path(os.environ.get("HERMES_HOME", home / ".hermes")),
        "claude": home / ".claude",
        "cursor": home / ".cursor",
        "codex": home / ".codex",
        "copilot": home / ".copilot",
        "opencode": home / ".config" / "opencode",
        "pi": home / ".pi",
        "kiro": home / ".kiro",
    }
    for name, path in homes.items():
        if path.is_dir():
            found.append(name)
    return found or ["claude", "cursor", "codex", "copilot"]


def link(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() and dest.resolve() == src.resolve():
        return "unchanged"
    if dest.exists() and not dest.is_symlink():
        return "kept-existing"
    if dest.is_symlink() or dest.exists():
        dest.unlink()
    dest.symlink_to(src, target_is_directory=src.is_dir())
    return "linked"


def write_if_missing(path: Path, text: str) -> str:
    if path.exists():
        return "kept-existing"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return "wrote"


def append_marker(path: Path, marker: str, block: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_text() if path.exists() else ""
    if marker in current:
        return "unchanged"
    path.write_text((current.rstrip() + "\n\n" + block).lstrip("\n"))
    return "appended"


def install_kit(agent: str, kit: Path, target: Path, home: Path) -> list[str]:
    done = []
    skills = kit / "skills"
    pointer = (
        "Follow coding-agent-kit AGENTS.md and skills/. "
        "Persistent notes live in the AvenoxBeyin vault installed beside this kit.\n"
    )
    if agent == "hermes":
        # HERMES_HOME wins only for the real user home. Tests pass a temp --home.
        env_home = os.environ.get("HERMES_HOME")
        hermes = Path(env_home) if env_home and home == Path.home() else home / ".hermes"
        skill_root = hermes / "skills"
        for folder in sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()):
            done.append(f"hermes {folder.name}: {link(folder, skill_root / folder.name)}")
        umbrella = skill_root / "avenox-kit"
        umbrella.mkdir(parents=True, exist_ok=True)
        (umbrella / "SKILL.md").write_text(
            "---\nname: avenox-kit\n"
            "description: Use when coding or recalling notes. Follow the kit and Beyin.\n---\n\n"
            "# Avenox kit\n\n"
            f"Kit: `{kit}`\n\n"
            "Read `AGENTS.md`, then the skill for the current phase. "
            "Notes and tasks go through the AvenoxBeyin vault, not chat memory.\n"
        )
        done.append("hermes avenox-kit: wrote")
    elif agent == "claude":
        claude = home / ".claude" / "skills"
        for folder in sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()):
            done.append(f"claude {folder.name}: {link(folder, claude / folder.name)}")
        done.append("claude project: " + write_if_missing(target / "CLAUDE.md", (kit / "CLAUDE.md").read_text()))
        done.append("claude project skills: " + link(skills, target / ".claude" / "skills"))
    elif agent == "cursor":
        rule = (kit / ".cursor" / "rules" / "coding-agent-kit.mdc").read_text()
        for dest in (home / ".cursor" / "rules" / "coding-agent-kit.mdc", target / ".cursor" / "rules" / "coding-agent-kit.mdc"):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(rule)
            done.append(f"cursor rule: {dest}")
    elif agent == "codex":
        done.append("codex: " + append_marker(
            home / ".codex" / "AGENTS.md", "avenox-kit", "# avenox-kit\n\n" + pointer))
        done.append("codex project: " + append_marker(target / "AGENTS.md", "avenox-kit", pointer))
    elif agent == "copilot":
        text = (kit / ".github" / "copilot-instructions.md").read_text()
        dest = target / ".github" / "copilot-instructions.md"
        done.append("copilot: " + write_if_missing(dest, text))
    elif agent == "opencode":
        done.append("opencode: " + write_if_missing(home / ".config" / "opencode" / "AGENTS.md", pointer))
    elif agent == "pi":
        done.append("pi: " + write_if_missing(home / ".pi" / "AGENTS.md", pointer))
    elif agent == "kiro":
        done.append("kiro: " + write_if_missing(home / ".kiro" / "steering" / "avenox-kit.md", pointer))
    return done


def install_beyin(beyin: Path, vault: Path, agents: list[str], home: Path, dry_run: bool) -> str:
    vault.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(beyin / "scripts" / "install_v3.py"), "--vault", str(vault)]
    if dry_run:
        cmd.append("--plan")
    proc = run(cmd, cwd=beyin)
    if proc.returncode != 0:
        raise SystemExit((proc.stderr or proc.stdout or "beyin install failed").strip())
    if "hermes" in agents and not dry_run:
        plugin = vault / ".claude" / "hermes-plugin"
        if plugin.is_dir():
            hermes = Path(os.environ.get("HERMES_HOME", home / ".hermes"))
            dest = hermes / "plugins" / "beyin-v3"
            dest.parent.mkdir(parents=True, exist_ok=True)
            link(plugin, dest)
            enable = run(["hermes", "plugins", "enable", "beyin-v3"])
            if enable.returncode != 0:
                return "beyin installed; hermes plugin linked, enable it with: hermes plugins enable beyin-v3"
            return "beyin installed; hermes plugin enabled"
    return "beyin installed" if not dry_run else "beyin plan ok"


def stamp_path(home: Path) -> Path:
    return data_root(home) / STAMP_NAME


def is_due(home: Path, now: datetime | None = None) -> bool:
    path = stamp_path(home)
    if not path.is_file():
        return True
    raw = path.read_text().strip()
    try:
        last = datetime.fromisoformat(raw)
    except ValueError:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    return current - last >= timedelta(days=CHECK_DAYS)


def write_stamp(home: Path) -> None:
    path = stamp_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(datetime.now(timezone.utc).isoformat())


def schedule(home: Path, script: Path) -> str:
    cron = shutil.which("crontab")
    if not cron:
        return "no crontab; run this installer again or call --if-due yourself"
    listed = run([cron, "-l"])
    current = listed.stdout if listed.returncode == 0 else ""
    line = f"0 9 * * * {sys.executable} {script} --if-due {CRON_MARK}"
    kept = [row for row in current.splitlines() if CRON_MARK not in row and row.strip()]
    kept.append(line)
    proc = subprocess.run([cron, "-"], input="\n".join(kept) + "\n", text=True, capture_output=True)
    if proc.returncode != 0:
        return "crontab update failed: " + (proc.stderr or "").strip()
    return "update check scheduled daily; it updates only after 3 days"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install coding-agent-kit and AvenoxBeyin for the current agent.")
    parser.add_argument("--agent", default="auto", help="auto or one of: " + ", ".join(AGENTS))
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="project directory for project-local files")
    parser.add_argument("--vault", type=Path, help="AvenoxBeyin vault (default: ~/Beynim)")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--kit-dir", type=Path, help="existing coding-agent-kit checkout")
    parser.add_argument("--beyin-dir", type=Path, help="existing avenoxbeyin checkout")
    parser.add_argument("--no-update", action="store_true")
    parser.add_argument("--skip-beyin", action="store_true")
    parser.add_argument("--no-cron", action="store_true")
    parser.add_argument("--if-due", action="store_true", help="exit unless the last check is at least 3 days old")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    home = args.home.expanduser()
    if args.if_due and not is_due(home):
        say("not due")
        return 0

    kit = args.kit_dir.expanduser() if args.kit_dir else data_root(home) / "coding-agent-kit"
    beyin = args.beyin_dir.expanduser() if args.beyin_dir else data_root(home) / "avenoxbeyin"
    if not args.dry_run:
        if args.kit_dir is None:
            kit = ensure_clone(KIT_REPO, kit, update=not args.no_update)
        elif not args.no_update and (kit / ".git").is_dir():
            git(kit, "pull", "--ff-only")
        if not args.skip_beyin:
            if args.beyin_dir is None:
                beyin = ensure_clone(BEYIN_REPO, beyin, update=not args.no_update)
            elif not args.no_update and (beyin / ".git").is_dir():
                git(beyin, "pull", "--ff-only")

    agents = detect_agents(home, args.agent)
    say("agents: " + ", ".join(agents))
    target = args.target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        for line in install_kit(agent, kit, target, home):
            say(line)
    vault = (args.vault or (home / "Beynim")).expanduser()
    if not args.skip_beyin:
        say(install_beyin(beyin, vault, agents, home, args.dry_run))
        say(f"vault: {vault}")
    if not args.dry_run:
        write_stamp(home)
        if not args.no_cron:
            say(schedule(home, Path(__file__).resolve()))
    say("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
