#!/bin/sh
# One command for coding-agent-kit + AvenoxBeyin.
#
#   curl -fsSL https://raw.githubusercontent.com/cengovski/coding-agent-kit/main/install.sh | bash
#   curl -fsSL .../install.sh | bash -s -- --agent cursor --vault ~/Beynim
#   bash install.sh --agent cursor            # from a checkout of this repo
#
# Piped from curl, it clones (or fast-forwards) the kit into a stable folder,
# $CODING_AGENT_KIT_DIR or ${XDG_DATA_HOME:-~/.local/share}/avenox-kit/coding-agent-kit,
# and runs scripts/setup_kit.py from there. Every run updates; after install a
# daily cron updates only once 3 days have passed. Options: setup_kit.py --help.
#
# Everything is inside main() so a piped shell reads the whole script before running it.
set -eu

die() {
  printf 'coding-agent-kit install: %s\n' "$*" >&2
  exit 1
}

main() {
  command -v git >/dev/null 2>&1 || die "git is required. Install git and run this command again."
  command -v python3 >/dev/null 2>&1 || die "python3 is required (3.11+ for AvenoxBeyin). Install it and run this command again."
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
    || die "python3 is too old ($(python3 -V 2>&1)); 3.9+ is needed, 3.11+ for AvenoxBeyin."

  # Run from a checkout: only when this file is really on disk next to scripts/setup_kit.py.
  # Piped into bash, $0 is "bash" (or "sh"), so this is skipped.
  case "$0" in
    */install.sh | install.sh)
      if [ -f "$0" ]; then
        root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
        if [ -f "$root/scripts/setup_kit.py" ]; then
          exec python3 "$root/scripts/setup_kit.py" --kit-dir "$root" "$@"
        fi
      fi
      ;;
  esac

  : "${HOME:?HOME is not set}"
  repo="${CODING_AGENT_KIT_REPO:-https://github.com/cengovski/coding-agent-kit.git}"
  kit="${CODING_AGENT_KIT_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/avenox-kit/coding-agent-kit}"

  if [ -d "$kit/.git" ]; then
    printf 'Updating coding-agent-kit in %s\n' "$kit"
    git -C "$kit" pull --ff-only --quiet </dev/null \
      || die "could not update $kit (local changes?). Fix it or delete the folder and rerun."
  elif [ -e "$kit" ]; then
    die "$kit exists but is not a git checkout. Move it away or set CODING_AGENT_KIT_DIR."
  else
    printf 'Cloning coding-agent-kit into %s\n' "$kit"
    mkdir -p "$(dirname -- "$kit")"
    git clone --depth 1 --quiet "$repo" "$kit" </dev/null || die "git clone $repo failed."
  fi

  exec python3 "$kit/scripts/setup_kit.py" --kit-dir "$kit" "$@" </dev/null
}

main "$@"
