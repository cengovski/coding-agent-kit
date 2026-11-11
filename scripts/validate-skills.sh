#!/usr/bin/env bash
# Validates every skills/*/SKILL.md: YAML frontmatter with name + description,
# name matches the folder, name is lowercase-hyphenated, description <= 1024 chars.
set -euo pipefail
cd "$(dirname "$0")/.."
status=0
for f in skills/*/SKILL.md; do
  dir=$(basename "$(dirname "$f")")
  if [ "$(head -n1 "$f")" != "---" ]; then echo "FAIL $f: missing frontmatter"; status=1; continue; fi
  fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$f")
  name=$(printf '%s\n' "$fm" | sed -n 's/^name: *//p')
  desc=$(printf '%s\n' "$fm" | sed -n 's/^description: *//p')
  [ -n "$name" ] || { echo "FAIL $f: no name"; status=1; }
  [ -n "$desc" ] || { echo "FAIL $f: no description"; status=1; }
  [ "$name" = "$dir" ] || { echo "FAIL $f: name '$name' != folder '$dir'"; status=1; }
  [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "FAIL $f: name not lowercase-hyphenated"; status=1; }
  [ "${#desc}" -le 1024 ] || { echo "FAIL $f: description > 1024 chars"; status=1; }
  lines=$(wc -l < "$f")
  [ "$lines" -le 500 ] || { echo "WARN $f: $lines lines (keep skills short)"; }
done
[ $status -eq 0 ] && echo "OK: $(ls skills/*/SKILL.md | wc -l) skills valid"
exit $status
