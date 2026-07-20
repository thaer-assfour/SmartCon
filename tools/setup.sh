#!/usr/bin/env bash
#
# SmartCon toolchain installer.
# Installs the automated-analysis stack used in Phase 3.
# Idempotent: safe to re-run. Skips anything already present.
#
set -euo pipefail

log()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n'  "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

# --- Foundry (forge/cast/anvil) — core of PoC + fuzzing -----------------------
if have forge; then
  log "Foundry already installed ($(forge --version | head -1))"
else
  log "Installing Foundry..."
  curl -L https://foundry.paradigm.xyz | bash
  # shellcheck disable=SC1090
  export PATH="$HOME/.foundry/bin:$PATH"
  foundryup
fi

# --- Python tooling: Slither, Mythril, Semgrep --------------------------------
if have pipx; then
  PYINSTALL="pipx install"
elif have pip3; then
  PYINSTALL="pip3 install --user"
else
  warn "No pip3/pipx found — install Python 3 to get Slither/Mythril/Semgrep."
  PYINSTALL=""
fi

if [ -n "$PYINSTALL" ]; then
  for pkg in slither-analyzer mythril semgrep; do
    if have "${pkg%%-*}" || { [ "$pkg" = "slither-analyzer" ] && have slither; }; then
      log "$pkg already available"
    else
      log "Installing $pkg..."
      $PYINSTALL "$pkg" || warn "Failed to install $pkg (continuing)"
    fi
  done
fi

# --- Aderyn (Rust static analyzer, by Cyfrin) ---------------------------------
if have aderyn; then
  log "Aderyn already installed"
elif have cargo; then
  log "Installing Aderyn via cargo..."
  cargo install aderyn || warn "Aderyn install failed (continuing)"
else
  warn "cargo not found — install Rust to get Aderyn (https://github.com/Cyfrin/aderyn)."
fi

# --- Optional: Echidna / Medusa (fuzzers) -------------------------------------
have echidna && log "Echidna present" || warn "Echidna not installed (optional fuzzer) — see https://github.com/crytic/echidna"
have medusa  && log "Medusa present"  || warn "Medusa not installed (optional fuzzer) — see https://github.com/crytic/medusa"

log "Done. Verify with: forge --version, slither --version, aderyn --version"
log "Set ETHERSCAN_API_KEY before running scripts/recon.sh on mainnet targets."
