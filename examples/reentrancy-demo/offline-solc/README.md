# offline-solc — a `solc` shim backed by solc-js

Slither / crytic-compile need a `solc` executable. On restricted networks the native
solc binary (from `binaries.soliditylang.org` or GitHub releases) may be blocked. This
directory provides a drop-in `solc` shim backed by the **`solc-js`** npm package, which
ships the compiler as pure JavaScript/WASM and installs from the npm registry.

## How it works

- `solc` (bash) answers `--version` and otherwise pipes the standard-json request to…
- `compile.cjs`, which reads the solc standard-json on stdin, resolves any
  `{"urls": [...]}` sources to file `content` (solc-js has no file-import callback),
  compiles in-process with `require('solc')`, and writes clean standard-json to stdout.

## Usage

```bash
# from the demo root, with `npm install` already run:
PATH="$PWD/offline-solc:$PATH" slither contracts/ --solc-standard-json
```

`--solc-standard-json` is required: it makes crytic-compile drive the compiler through
standard-json (stdin/stdout) instead of the `--combined-json` CLI, which solc-js
doesn't support.

## When you don't need this

If `tools/setup.sh` succeeded and `solc --version` reports a real native compiler, use
that directly — this shim is only a fallback for constrained environments.
