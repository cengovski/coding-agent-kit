#!/usr/bin/env python3
"""Install coding-agent-kit and AvenoxBeyin for the agent that is present.

Every run updates the kit checkout and AvenoxBeyin first. After install, a
daily cron calls --if-due, which updates only when the last check is at least
3 days old.

AvenoxBeyin is never vendored. It is installed the way its own guide
(https://github.com/avenoxai/avenoxbeyin/blob/main/beyin.md) says: download the
latest stable release ZIP, verify its SHA-256, run scripts/install_v3.py for a
new vault, or `beyin.py update --package <zip>` for an existing V3 vault.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

KIT_REPO = "https://github.com/cengovski/coding-agent-kit.git"
KIT_SLUG = "cengovski/coding-agent-kit"
BEYIN_SLUG = "avenoxai/avenoxbeyin"
BEYIN_API = f"https://api.github.com/repos/{BEYIN_SLUG}/releases/latest"
BEYIN_LATEST = f"https://github.com/{BEYIN_SLUG}/releases/latest"
BEYIN_MIN_PYTHON = (3, 11)
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
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, stdin=subprocess.DEVNULL)


def git(repo: Path, *args: str) -> str:
    proc = run(["git", "-C", str(repo), *args])
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "git failed").strip()
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {detail}")
    return proc.stdout.strip()


def ensure_clone(url: str, dest: Path, update: bool) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").is_dir():
        proc = run(["git", "clone", "--depth", "1", url, str(dest)])
        if proc.returncode != 0:
            raise SystemExit((proc.stderr or proc.stdout or "clone failed").strip())
    elif update:
        git(dest, "pull", "--ff-only", "--quiet")
    return dest


def is_kit_checkout(path: Path) -> bool:
    """True only for a git checkout whose origin is this kit (not an app made from the template)."""
    if not (path / ".git").exists():
        return False
    proc = run(["git", "-C", str(path), "remote", "get-url", "origin"])
    url = proc.stdout.strip().lower().removesuffix(".git")
    return proc.returncode == 0 and url.endswith(KIT_SLUG)


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
        "hermes": hermes_home(home),
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


def hermes_home(home: Path) -> Path:
    # HERMES_HOME wins only for the real user home. Tests pass a temp --home.
    env_home = os.environ.get("HERMES_HOME")
    return Path(env_home) if env_home and home == Path.home() else home / ".hermes"


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


def write_managed(path: Path, text: str) -> str:
    """Overwrite a file this installer owns; report whether it changed."""
    if path.is_file() and path.read_text() == text:
        return "unchanged"
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


def pointer_text(kit: Path) -> str:
    return (
        f"Follow the coding-agent-kit rules in `{kit / 'AGENTS.md'}` and load skills from "
        f"`{kit / 'skills'}/<name>/SKILL.md` as each phase needs them. "
        "Persistent notes and tasks live in the AvenoxBeyin vault installed beside this kit.\n"
    )


def skill_dirs(kit: Path) -> list[Path]:
    return sorted(p for p in (kit / "skills").iterdir() if (p / "SKILL.md").is_file())


def install_kit(agent: str, kit: Path, target: Path | None, home: Path) -> list[str]:
    """Write user-level files for one agent; project files only when target is given."""
    done = []
    pointer = pointer_text(kit)
    if agent == "hermes":
        skill_root = hermes_home(home) / "skills"
        for folder in skill_dirs(kit):
            done.append(f"hermes {folder.name}: {link(folder, skill_root / folder.name)}")
        umbrella = (
            "---\nname: avenox-kit\n"
            "description: Use when coding or recalling notes. Follow the kit and Beyin.\n---\n\n"
            "# Avenox kit\n\n"
            f"Kit: `{kit}`\n\n"
            "Read `AGENTS.md`, then the skill for the current phase. "
            "Notes and tasks go through the AvenoxBeyin vault, not chat memory.\n"
        )
        done.append("hermes avenox-kit: " + write_managed(skill_root / "avenox-kit" / "SKILL.md", umbrella))
    elif agent == "claude":
        for folder in skill_dirs(kit):
            done.append(f"claude {folder.name}: {link(folder, home / '.claude' / 'skills' / folder.name)}")
        if target:
            done.append("claude project: " + write_if_missing(target / "CLAUDE.md", (kit / "CLAUDE.md").read_text()))
            done.append("claude project skills: " + link(kit / "skills", target / ".claude" / "skills"))
    elif agent == "cursor":
        rule = (
            "---\ndescription: coding-agent-kit operating rules. Always applies.\nalwaysApply: true\n---\n"
            + pointer
        )
        done.append("cursor user rule: " + write_managed(home / ".cursor" / "rules" / "coding-agent-kit.mdc", rule))
        if target:
            project_rule = (kit / ".cursor" / "rules" / "coding-agent-kit.mdc").read_text()
            done.append("cursor project rule: " + write_if_missing(
                target / ".cursor" / "rules" / "coding-agent-kit.mdc", project_rule))
    elif agent == "codex":
        done.append("codex: " + append_marker(
            home / ".codex" / "AGENTS.md", "avenox-kit", "# avenox-kit\n\n" + pointer))
        if target:
            done.append("codex project: " + append_marker(target / "AGENTS.md", "avenox-kit", "<!-- avenox-kit -->\n" + pointer))
    elif agent == "copilot":
        if target:
            text = (kit / ".github" / "copilot-instructions.md").read_text()
            done.append("copilot: " + write_if_missing(target / ".github" / "copilot-instructions.md", text))
        else:
            done.append("copilot: project-only; rerun with --target <project> to add .github/copilot-instructions.md")
    elif agent == "opencode":
        done.append("opencode: " + write_if_missing(home / ".config" / "opencode" / "AGENTS.md", pointer))
    elif agent == "pi":
        done.append("pi: " + write_if_missing(home / ".pi" / "agent" / "AGENTS.md", pointer))
    elif agent == "kiro":
        done.append("kiro: " + write_if_missing(home / ".kiro" / "steering" / "avenox-kit.md", pointer))
    return done


# ---------------------------------------------------------------- AvenoxBeyin

def http_get(url: str, accept: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "coding-agent-kit-installer"})
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def latest_beyin_tag() -> str:
    """Latest stable release tag: GitHub API first, the /releases/latest redirect if rate limited."""
    try:
        data = json.loads(http_get(BEYIN_API, "application/vnd.github+json"))
        if not data.get("draft") and not data.get("prerelease") and data.get("tag_name"):
            return data["tag_name"]
    except (urllib.error.URLError, ValueError, OSError):
        pass
    req = urllib.request.Request(BEYIN_LATEST, method="HEAD", headers={"User-Agent": "coding-agent-kit-installer"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            final = resp.geturl()
    except (urllib.error.URLError, OSError) as exc:
        raise SystemExit(f"could not reach GitHub to find the latest AvenoxBeyin release: {exc}")
    tag = final.rstrip("/").rsplit("/", 1)[-1]
    if "/releases/tag/" not in final or not tag.startswith("v"):
        raise SystemExit(f"could not read the latest AvenoxBeyin release tag from {final}")
    return tag


def verify_sha256(zip_path: Path, sha_text: str) -> None:
    fields = sha_text.split()
    expected = fields[0].lower() if fields else ""
    actual = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if expected != actual:
        raise SystemExit(f"AvenoxBeyin checksum mismatch for {zip_path.name}; not installing")


def safe_extract(zip_path: Path, dest: Path) -> Path:
    """Extract, refusing absolute paths, '..' escapes and symlinks."""
    dest = dest.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            name = info.filename
            mode = info.external_attr >> 16
            target = (dest / name).resolve()
            if name.startswith(("/", "\\")) or ".." in Path(name).parts or stat.S_ISLNK(mode):
                raise SystemExit(f"unsafe entry in AvenoxBeyin package: {name}")
            if target != dest and dest not in target.parents:
                raise SystemExit(f"unsafe entry in AvenoxBeyin package: {name}")
        zf.extractall(dest)
    if not (dest / "manifest.json").is_file() or not (dest / "scripts" / "install_v3.py").is_file():
        raise SystemExit("AvenoxBeyin package is missing manifest.json or scripts/install_v3.py")
    return dest


def fetch_beyin_release(work: Path) -> tuple[str, Path, Path]:
    tag = latest_beyin_tag()
    version = tag.removeprefix("v")
    name = f"beyin-v3-{version}.zip"
    base = f"https://github.com/{BEYIN_SLUG}/releases/download/{tag}/{name}"
    zip_path = work / name
    try:
        zip_path.write_bytes(http_get(base))
        sha_text = http_get(base + ".sha256").decode()
    except (urllib.error.URLError, OSError) as exc:
        raise SystemExit(f"could not download AvenoxBeyin {tag}: {exc}")
    verify_sha256(zip_path, sha_text)
    return version, zip_path, safe_extract(zip_path, work / "package")


def json_status(text: str) -> str:
    try:
        return str(json.loads(text).get("status", "ok"))
    except (ValueError, AttributeError):
        return "ok"


def install_beyin(vault: Path, agents: list[str], home: Path, package: Path | None = None) -> list[str]:
    """Install or update AvenoxBeyin in the vault. package: an unpacked release/checkout (offline)."""
    if sys.version_info < BEYIN_MIN_PYTHON:
        raise SystemExit(
            "AvenoxBeyin needs Python 3.11+; this is "
            f"{sys.version.split()[0]}. Install a newer python3 and rerun, or pass --skip-beyin."
        )
    vault.mkdir(parents=True, exist_ok=True)
    version_file = vault / ".beyin-version"
    installed = version_file.read_text().strip() if version_file.is_file() else ""
    out = []
    with tempfile.TemporaryDirectory(prefix="avenox-beyin-") as raw:
        zip_path = None
        if package is None:
            version, zip_path, package = fetch_beyin_release(Path(raw))
            out.append(f"beyin release: v{version} (sha256 verified)")
        if installed.startswith("3.") and zip_path is not None:
            cmd = [sys.executable, "beyin.py", "update", "--package", str(zip_path)]
            proc = run(cmd, cwd=vault)
            action = "update"
        else:
            cmd = [sys.executable, str(package / "scripts" / "install_v3.py"), "--vault", str(vault)]
            proc = run(cmd, cwd=package)
            action = "install"
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "failed").strip()
            raise SystemExit(f"AvenoxBeyin {action} failed (exit {proc.returncode}): {detail}")
        out.append(f"beyin {action}: {json_status(proc.stdout)}")
    now = version_file.read_text().strip() if version_file.is_file() else "?"
    doctor = run([sys.executable, "beyin.py", "doctor"], cwd=vault)
    out.append(f"beyin version: {now}; doctor exit {doctor.returncode}")
    if "hermes" in agents:
        plugin = vault / ".claude" / "hermes-plugin"
        if plugin.is_dir():
            out.append("hermes plugin: " + link(plugin, hermes_home(home) / "plugins" / "beyin-v3"))
            hermes = shutil.which("hermes")
            if hermes and run([hermes, "plugins", "enable", "beyin-v3"]).returncode == 0:
                out.append("hermes plugin enabled; restart Hermes")
            else:
                out.append("hermes plugin linked; enable it with: hermes plugins enable beyin-v3")
    return out


# ---------------------------------------------------------------- update schedule

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


def cron_line(home: Path, kit: Path, vault: Path, agent: str, skip_beyin: bool) -> str:
    script = kit / "scripts" / "setup_kit.py"
    args = [sys.executable, str(script), "--if-due", "--kit-dir", str(kit), "--vault", str(vault)]
    if agent != "auto":
        args += ["--agent", agent]
    if skip_beyin:
        args.append("--skip-beyin")
    log = data_root(home) / "update.log"
    cmd = " ".join(shlex.quote(a) for a in args)
    return f"0 9 * * * cd {shlex.quote(str(home))} && {cmd} >> {shlex.quote(str(log))} 2>&1 {CRON_MARK}"


def schedule(line: str) -> str:
    cron = shutil.which("crontab")
    if not cron:
        return "no crontab; run this installer again or call --if-due yourself"
    listed = run([cron, "-l"])
    current = listed.stdout if listed.returncode == 0 else ""
    kept = [row for row in current.splitlines() if CRON_MARK not in row and row.strip()]
    kept.append(line)
    proc = subprocess.run([cron, "-"], input="\n".join(kept) + "\n", text=True, capture_output=True)
    if proc.returncode != 0:
        return "crontab update failed: " + (proc.stderr or "").strip()
    return "update check scheduled daily at 09:00; it updates only after 3 days"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install coding-agent-kit and AvenoxBeyin for the current agent.")
    parser.add_argument("--agent", default="auto", help="auto or one of: " + ", ".join(AGENTS))
    parser.add_argument("--target", type=Path, help="also write project-local files into this project directory")
    parser.add_argument("--vault", type=Path, help="AvenoxBeyin vault (default: ~/Beynim)")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--kit-dir", type=Path, help="coding-agent-kit checkout to use (default: stable clone under ~/.local/share/avenox-kit)")
    parser.add_argument("--beyin-dir", type=Path, help="unpacked AvenoxBeyin release or checkout to install from (offline)")
    parser.add_argument("--no-update", action="store_true", help="do not pull the kit")
    parser.add_argument("--skip-beyin", action="store_true")
    parser.add_argument("--no-cron", action="store_true")
    parser.add_argument("--if-due", action="store_true", help="exit unless the last check is at least 3 days old")
    parser.add_argument("--dry-run", action="store_true", help="show what would be installed; change nothing")
    args = parser.parse_args(argv)

    home = args.home.expanduser()
    if args.if_due and not is_due(home):
        say("not due")
        return 0

    kit = (args.kit_dir.expanduser() if args.kit_dir else data_root(home) / "coding-agent-kit").resolve()
    vault = (args.vault or (home / "Beynim")).expanduser().resolve()
    target = args.target.expanduser().resolve() if args.target else None
    agents = detect_agents(home, args.agent)
    if args.dry_run:
        say(f"kit: {kit}\nagents: {', '.join(agents)}\nproject: {target or 'none'}")
        say("vault: " + ("skipped" if args.skip_beyin else str(vault)))
        say("cron: " + ("none" if args.no_cron else cron_line(home, kit, vault, args.agent, args.skip_beyin)))
        return 0

    if args.kit_dir is None:
        ensure_clone(KIT_REPO, kit, update=not args.no_update)
    elif not args.no_update and is_kit_checkout(kit):
        git(kit, "pull", "--ff-only", "--quiet")
    if not (kit / "AGENTS.md").is_file() or not (kit / "skills").is_dir():
        raise SystemExit(f"{kit} is not a coding-agent-kit checkout")

    say(f"kit: {kit}")
    say("agents: " + ", ".join(agents))
    if target:
        target.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        for line in install_kit(agent, kit, target, home):
            say(line)
    if not args.skip_beyin:
        package = args.beyin_dir.expanduser().resolve() if args.beyin_dir else None
        for line in install_beyin(vault, agents, home, package):
            say(line)
        say(f"vault: {vault}")
    write_stamp(home)
    if not args.no_cron:
        say(schedule(cron_line(home, kit, vault, args.agent, args.skip_beyin)))
    say("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
