#!/usr/bin/env bash
# One-shot demo: automated analysis (Phase 3) + executed PoC (Phase 5) on a
# deliberately vulnerable reentrancy vault.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Installing dependencies (solc-js + ethereumjs EVM)..."
npm install --no-audit --no-fund --silent

echo
echo "==> Phase 3: automated static analysis (Slither)"
# Slither needs a 'solc'. If a native solc is unavailable (restricted network),
# fall back to the bundled solc-js shim in offline-solc/.
if command -v solc >/dev/null 2>&1 && solc --version 2>/dev/null | grep -qi version; then
  slither contracts/ --solc-standard-json 2>&1 | tee slither-report.txt || true
else
  echo "   (no native solc; using offline-solc/ shim backed by solc-js)"
  PATH="$(pwd)/offline-solc:$PATH" slither contracts/ --solc-standard-json 2>&1 | tee slither-report.txt || true
fi

echo
echo "==> Phase 5: executed proof-of-concept (ethereumjs EVM)"
node exploit.mjs
