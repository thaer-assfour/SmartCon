#!/usr/bin/env bash
#
# Run the automated-analysis toolchain (Phase 3) over a target directory and
# collect a combined report. Each tool's raw output is written under
# <target>/smartcon-scan/ and a summary index is printed at the end.
#
# Usage:
#   ./tools/scan.sh <path-to-target-project>
#   MYTHRIL=1 ./tools/scan.sh <path-to-target-project>      # also run Mythril (slow, opt-in)
#
# The target should be a Foundry/Hardhat project or a directory of .sol files.
#
# Stages: Slither, Aderyn, Semgrep (always, when installed); Mythril symbolic execution
# per source file when MYTHRIL=1 (MYTHRIL_TIMEOUT seconds per file, default 300;
# MYTHRIL_DIRS overrides the source directories, default "src contracts"); Foundry
# build + tests when the target is a Foundry project.
#
set -uo pipefail   # NOTE: not -e; we want every tool to run even if one fails

TARGET="${1:-}"
if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
  echo "Usage: $0 <path-to-target-project>" >&2
  exit 1
fi

TARGET="$(cd "$TARGET" && pwd)"
OUT="$TARGET/smartcon-scan"
mkdir -p "$OUT"

log()  { printf '\033[1;34m[scan]\033[0m %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

log "Target : $TARGET"
log "Output : $OUT"

# --- Slither ------------------------------------------------------------------
if have slither; then
  log "Running Slither..."
  ( cd "$TARGET" && slither . --json "$OUT/slither.json" ) > "$OUT/slither.txt" 2>&1 || true
  ( cd "$TARGET" && slither . --print human-summary )      > "$OUT/slither-summary.txt" 2>&1 || true
  ( cd "$TARGET" && slither . --print function-summary )   > "$OUT/function-summary.txt" 2>&1 || true
else
  log "Slither not found — skipping (run tools/setup.sh)"
fi

# --- Aderyn -------------------------------------------------------------------
if have aderyn; then
  log "Running Aderyn..."
  ( cd "$TARGET" && aderyn . -o "$OUT/aderyn-report.md" ) > "$OUT/aderyn.txt" 2>&1 || true
else
  log "Aderyn not found — skipping"
fi

# --- Semgrep (Solidity rulesets) ----------------------------------------------
if have semgrep; then
  log "Running Semgrep (p/smart-contracts)..."
  ( cd "$TARGET" && semgrep --config p/smart-contracts --sarif -o "$OUT/semgrep.sarif" . ) \
      > "$OUT/semgrep.txt" 2>&1 || true
else
  log "Semgrep not found — skipping"
fi

# --- Mythril (symbolic execution; opt-in because it is slow) -------------------
# setup.sh installs Mythril, but a whole-project run can take hours, so it only runs
# when MYTHRIL=1. Each .sol file under the source dirs is analysed on its own with a
# per-file timeout; imports are resolved through the project's remappings when present.
if [ "${MYTHRIL:-0}" = "1" ]; then
  if have myth; then
    MYTHRIL_TIMEOUT="${MYTHRIL_TIMEOUT:-300}"
    MYTHRIL_DIRS="${MYTHRIL_DIRS:-src contracts}"
    mkdir -p "$OUT/mythril"
    MYTH_ARGS=()
    if [ -f "$TARGET/remappings.txt" ] && have python3; then
      python3 - "$TARGET/remappings.txt" > "$OUT/mythril/solc-settings.json" <<'PY'
import json, sys
maps = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
print(json.dumps({"remappings": maps}))
PY
      MYTH_ARGS+=(--solc-json "$OUT/mythril/solc-settings.json")
    fi
    for d in $MYTHRIL_DIRS; do
      [ -d "$TARGET/$d" ] || continue
      while IFS= read -r -d '' f; do
        rel="${f#"$TARGET"/}"
        log "Mythril: $rel (timeout ${MYTHRIL_TIMEOUT}s)"
        ( cd "$TARGET" && timeout "$((MYTHRIL_TIMEOUT + 60))" \
            myth analyze "$rel" --execution-timeout "$MYTHRIL_TIMEOUT" "${MYTH_ARGS[@]}" ) \
            > "$OUT/mythril/$(echo "$rel" | tr '/' '_').txt" 2>&1 || true
      done < <(find "$TARGET/$d" -name '*.sol' -not -path '*/test/*' -not -path '*/lib/*' -not -path '*/node_modules/*' -print0)
    done
  else
    log "MYTHRIL=1 but myth not found — skipping (run tools/setup.sh)"
  fi
elif have myth; then
  log "Mythril installed but not enabled — set MYTHRIL=1 to run symbolic execution (slow)"
fi

# --- Foundry build + tests (if a Foundry project) -----------------------------
if have forge && [ -f "$TARGET/foundry.toml" ]; then
  log "Foundry project detected — building & testing..."
  ( cd "$TARGET" && forge build )               > "$OUT/forge-build.txt" 2>&1 || true
  ( cd "$TARGET" && forge test -vv )             > "$OUT/forge-test.txt"  2>&1 || true
fi

# --- Index --------------------------------------------------------------------
{
  echo "# SmartCon automated scan index"
  echo
  echo "Target: \`$TARGET\`"
  echo
  echo "## Artifacts"
  for f in "$OUT"/*; do
    [ "$f" = "$OUT/INDEX.md" ] && continue
    if [ -d "$f" ]; then
      echo "- \`$(basename "$f")/\` ($(find "$f" -type f | wc -l) files)"
    else
      echo "- \`$(basename "$f")\`"
    fi
  done
  echo
  echo "## Next steps"
  echo "1. Triage every finding: true positive / false positive / needs manual check."
  echo "2. Map each real signal to a checklist item ID (methodology/checklist.md) and record it in the coverage matrix."
  echo "3. Proceed to Phase 4 manual review; the tools covered the known patterns only."
} > "$OUT/INDEX.md"

log "Done. See $OUT/INDEX.md"
