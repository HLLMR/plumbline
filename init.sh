#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: MIT-0
# Plumbline scaffolder. Creates the governance directory and copies templates,
# the reference adapter, and the pre-dispatch validator into a target repository.
#
# It does not inventory, does not birth-test, does not write an adoption
# record, and does not commit. It makes no claim that any wall works. See
# ADOPTING.md section 4 and Doctrine 6.4.1.
#
# CREATE-ONLY BY DEFAULT. Every existing file is left untouched and reported
# as skipped. Nothing is ever deleted or recursively replaced.
#
# Usage:
#   ./init.sh /path/to/project
#   ./init.sh --force-templates /path/to/project
#   ./init.sh --force-adapter   /path/to/project
#
#   --force-templates  Overwrite ONLY governance/templates/[A-E]-*.md, which are
#                      verbatim doctrine appendices and carry no local content.
#   --force-adapter    Overwrite ONLY .claude/hooks/wo_capability_wall.py.
#
# Neither force option touches a charter, a work order, a decision record, a
# log, or a hook registration. Those are refused unconditionally: they hold
# local content or enforcement configuration that this script cannot merge.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

force_templates=0
force_adapter=0
TARGET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --force-templates) force_templates=1 ;;
    --force-adapter)   force_adapter=1 ;;
    -h|--help)
      sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    -*)
      echo "unknown option: $1" >&2
      echo "usage: init.sh [--force-templates] [--force-adapter] /path/to/project" >&2
      exit 2
      ;;
    *)
      if [ -n "$TARGET" ]; then
        echo "unexpected extra argument: $1" >&2
        exit 2
      fi
      TARGET="$1"
      ;;
  esac
  shift
done

if [ -z "$TARGET" ]; then
  echo "usage: init.sh [--force-templates] [--force-adapter] /path/to/project" >&2
  exit 2
fi

# Python and other native-Windows callers commonly pass `C:/...` paths to
# Git Bash. Once such a value is expanded from a shell variable, MSYS argument
# conversion does not reliably rewrite it for core utilities. Normalize it
# explicitly when Git Bash provides cygpath; native POSIX paths are unchanged.
case "$TARGET" in
  [A-Za-z]:/*)
    if command -v cygpath >/dev/null 2>&1; then
      TARGET="$(cygpath -u "$TARGET")"
    fi
    ;;
esac

if [ ! -d "$TARGET" ]; then
  echo "not a directory: $TARGET" >&2
  exit 1
fi

# A normal repository has a .git directory; a worktree or submodule has a .git
# file containing a gitdir: pointer. Accept both.
if [ ! -d "$TARGET/.git" ] && [ ! -f "$TARGET/.git" ]; then
  echo "not a git repository or worktree: $TARGET" >&2
  exit 1
fi

created=()
skipped=()
refused=()

note_created() { created+=("$1"); }
note_skipped() { skipped+=("$1"); }
note_refused() { refused+=("$1 -- $2"); }

# create_file <relative-path> <<<content, create-only.
create_file() {
  local rel="$1" abs="$TARGET/$1"
  if [ -e "$abs" ]; then
    note_skipped "$rel"
    cat >/dev/null
    return 0
  fi
  mkdir -p "$(dirname "$abs")"
  cat >"$abs"
  note_created "$rel"
}

# copy_file <source> <relative-dest> <force-flag> <kind>
copy_file() {
  local src="$1" rel="$2" force="$3" kind="$4" abs="$TARGET/$2"
  if [ -e "$abs" ]; then
    if [ "$force" = "1" ]; then
      mkdir -p "$(dirname "$abs")"
      cp "$src" "$abs"
      note_created "$rel (overwritten by --force-$kind)"
      return 0
    fi
    note_skipped "$rel"
    return 0
  fi
  mkdir -p "$(dirname "$abs")"
  cp "$src" "$abs"
  note_created "$rel"
}

for d in decisions work-orders reports briefs rfis history archive scratch templates; do
  if [ -d "$TARGET/governance/$d" ]; then
    note_skipped "governance/$d/"
  else
    mkdir -p "$TARGET/governance/$d"
    note_created "governance/$d/"
  fi
  if [ ! -e "$TARGET/governance/$d/.gitkeep" ]; then
    : >"$TARGET/governance/$d/.gitkeep"
  fi
done

for t in "$HERE"/templates/*.md; do
  [ -e "$t" ] || continue
  copy_file "$t" "governance/templates/$(basename "$t")" "$force_templates" "templates"
done

# The pre-dispatch validator is adopter-facing (WO-PL-016): install it
# create-only, with no force option. It carries no local content to merge
# and no enforcement configuration, so an existing target copy is always
# left untouched rather than offered an overwrite path.
copy_file "$HERE/checks/check_work_order_dispatch.py" \
          "checks/check_work_order_dispatch.py" "0" "checker"

create_file "governance/LOG.md" <<'LOGHEADER'
| WO | Denials (9.2.1) | RFIs (9.2.2) | Drift caught same-WO / later (9.2.3) | Rework cycles (9.2.4) | Live corpus size, routing gaps (9.2.5) | Declared vs enforced surfaces (9.2.6) | Owner load, words, brief / escalation (9.2.7) | Instrument disagreements (9.2.8) | Notes |
|---|---|---|---|---|---|---|---|---|---|
LOGHEADER

if [ -e "$TARGET/governance/LOG-denials.jsonl" ]; then
  note_skipped "governance/LOG-denials.jsonl"
else
  : >"$TARGET/governance/LOG-denials.jsonl"
  note_created "governance/LOG-denials.jsonl"
fi

# The charter is never written by this script: it carries project-specific
# content (Appendix A.1.4 kill list) that no scaffolder can supply.
for charter in CHARTER.md CLAUDE.md; do
  if [ -e "$TARGET/$charter" ]; then
    note_refused "$charter" "existing charter candidate; prune it to Appendix A by hand (Doctrine 5.2, 8.1.2)"
  fi
done

if [ -d "$TARGET/.claude" ]; then
  copy_file "$HERE/adapters/claude-code/wo_capability_wall.py" \
            ".claude/hooks/wo_capability_wall.py" "$force_adapter" "adapter"
  if [ -e "$TARGET/.claude/settings.json" ]; then
    note_refused ".claude/settings.json" \
      "existing hook registration; merge matcher \"*\", native py -3/python3, \${CLAUDE_PROJECT_DIR}, and explicit timeout by hand (adapters/claude-code/README.md)"
  else
    note_refused ".claude/settings.json" \
      "not written by this script; register native py -3/python3 with matcher \"*\", \${CLAUDE_PROJECT_DIR}, and explicit timeout (adapters/claude-code/README.md)"
  fi
else
  note_refused ".claude/" "absent; adapter not installed. Create it, then re-run, or copy the adapter by hand"
fi

printf '\n== created ==\n'
if [ ${#created[@]} -eq 0 ]; then echo "  (nothing)"; else printf '  %s\n' "${created[@]}"; fi
printf '\n== skipped (already present, left untouched) ==\n'
if [ ${#skipped[@]} -eq 0 ]; then echo "  (nothing)"; else printf '  %s\n' "${skipped[@]}"; fi
printf '\n== refused (needs a human) ==\n'
if [ ${#refused[@]} -eq 0 ]; then echo "  (nothing)"; else printf '  %s\n' "${refused[@]}"; fi

cat <<'MSG'

Scaffolded. NOT adopted. No commit was made, no adoption record was written,
and no birth test has run. Doctrine 6.4.1 sequence, all yours:
  1 confirm the doctrine revision is ratified   2 record the baseline commit
  3 adoption mapping                            4 materialize PLAN.md
  5 charter to Appendix A                       6 ROUTING.md
  7 bootstrap STATE.md                          8 install adapter + birth test
  9 write DR-001                               10 adoption commit
MSG
