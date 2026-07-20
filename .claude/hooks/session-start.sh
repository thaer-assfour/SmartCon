#!/bin/bash
# SmartCon SessionStart hook — prepare the audit toolchain so scan.sh and the
# worked example are runnable immediately. Idempotent and non-interactive; never
# aborts the session if an optional install is blocked (e.g. egress policy).
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

log() { printf '[smartcon-hook] %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

# --- Slither (Phase 3 static analysis) ---------------------------------------
if have slither; then
  log "slither present ($(slither --version 2>/dev/null | tail -1))"
elif have pip3; then
  log "installing slither-analyzer..."
  pip3 install --quiet --user slither-analyzer >/dev/null 2>&1 \
    && log "slither installed" \
    || log "slither install failed (continuing; run tools/setup.sh manually)"
fi

# --- Worked-example deps (solc-js + ethereumjs EVM) --------------------------
# These come from the npm registry, which is reachable even on restricted
# networks, so the Phase-3 solc-js shim and the Phase-5 PoC runner work offline.
DEMO="$PROJECT_DIR/examples/reentrancy-demo"
if [ -f "$DEMO/package.json" ] && have npm; then
  if [ -d "$DEMO/node_modules" ]; then
    log "example deps already installed"
  else
    log "installing example deps (solc-js, @ethereumjs/vm)..."
    ( cd "$DEMO" && npm install --no-audit --no-fund --silent ) >/dev/null 2>&1 \
      && log "example deps installed" \
      || log "example npm install failed (continuing)"
  fi
fi

# --- Foundry (best effort; native download may be blocked on the web) --------
if have forge; then
  log "foundry present"
else
  log "foundry not installed — run tools/setup.sh (may be blocked on restricted networks)"
fi

log "ready. Audit with the /smartcon skill; methodology in CLAUDE.md."
exit 0
