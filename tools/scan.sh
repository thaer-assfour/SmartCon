#!/usr/bin/env bash
#
# Run the automated-analysis toolchain (Phase 3) over a target directory and
# collect a combined report. Each tool's raw output is written under
# <target>/smartcon-scan/ and a summary index is printed at the end.
#
# Usage:
#   ./tools/scan.sh <path-to-target-project>
#
# The target should be a Foundry/Hardhat project or a directory of .sol files.
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
    echo "- \`$(basename "$f")\`"
  done
  echo
  echo "## Next steps"
  echo "1. Triage every finding: true positive / false positive / needs manual check."
  echo "2. Map each real signal to a checklist category (methodology/checklist.md)."
  echo "3. Proceed to Phase 4 manual review; the tools covered the known patterns only."
} > "$OUT/INDEX.md"

log "Done. See $OUT/INDEX.md"
