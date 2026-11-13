#!/bin/sh
# One command for coding-agent-kit + AvenoxBeyin.
# Updates on every run. After install, a daily cron updates only once 3 days have passed.
# The agent is detected from the machine; override with: install.sh --agent cursor
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
exec python3 "$ROOT/scripts/setup_kit.py" --kit-dir "$ROOT" "$@"
