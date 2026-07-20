#!/usr/bin/env bash
#
# Phase 1 helper: pull verified source code for an on-chain contract into a local
# directory so you can review it and build a fork-based PoC.
#
# Requires: Foundry (cast), and ETHERSCAN_API_KEY for the relevant explorer.
#
# Usage:
#   export ETHERSCAN_API_KEY=your_key
#   ./scripts/recon.sh <address> <output-dir> [chain]
#
#   chain defaults to "mainnet". Examples: mainnet, arbitrum, optimism, base, bsc, polygon
#
set -euo pipefail

ADDR="${1:-}"
OUTDIR="${2:-}"
CHAIN="${3:-mainnet}"

if [ -z "$ADDR" ] || [ -z "$OUTDIR" ]; then
  echo "Usage: $0 <address> <output-dir> [chain]" >&2
  exit 1
fi

if ! command -v cast >/dev/null 2>&1; then
  echo "cast (Foundry) not found — run tools/setup.sh first." >&2
  exit 1
fi

if [ -z "${ETHERSCAN_API_KEY:-}" ]; then
  echo "Warning: ETHERSCAN_API_KEY not set; source download may fail." >&2
fi

mkdir -p "$OUTDIR"
log() { printf '\033[1;34m[recon]\033[0m %s\n' "$*"; }

log "Address : $ADDR"
log "Chain   : $CHAIN"
log "Output  : $OUTDIR"

# Fetch verified source via Foundry's etherscan integration.
log "Downloading verified source..."
cast etherscan-source --chain "$CHAIN" -d "$OUTDIR/src" "$ADDR" \
  || { echo "Source download failed — is the contract verified on $CHAIN?" >&2; exit 1; }

# Basic on-chain facts for the recon notes.
{
  echo "# Recon: $ADDR ($CHAIN)"
  echo
  echo "- Fetched: (record block/date manually — Date is not available in scripts)"
  echo "- Code size (bytes): $(cast codesize "$ADDR" 2>/dev/null || echo 'n/a — set an RPC via --rpc-url or ETH_RPC_URL')"
  echo
  echo "## TODO (Phase 1)"
  echo "- [ ] Read docs / whitepaper; write intended invariants"
  echo "- [ ] Map architecture (proxies, factories, dependencies)"
  echo "- [ ] Identify money-flow entry/exit points"
  echo "- [ ] Note TVL / value at risk and compiler version"
  echo "- [ ] Confirm program scope & rules (PoC location, known issues)"
} > "$OUTDIR/RECON.md"

log "Wrote $OUTDIR/RECON.md and $OUTDIR/src/"
log "Next: ./tools/scan.sh $OUTDIR  (Phase 3), then work the checklist (Phase 4)."
