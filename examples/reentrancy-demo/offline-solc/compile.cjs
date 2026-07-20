// solc 'standard-json' compiler backed by the solc-js API, used as a drop-in
// 'solc' replacement when a native solc binary cannot be downloaded (restricted
// networks). Reads standard-json on stdin, resolves {urls:[...]} to file content,
// compiles with solc-js, writes clean standard-json to stdout.
const fs = require('fs');
const path = require('path');
// solc is installed in the demo root (one level up from offline-solc/)
const solc = require(path.resolve(__dirname, '..', 'node_modules', 'solc'));
let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (c) => (raw += c));
process.stdin.on('end', () => {
  const input = JSON.parse(raw);
  for (const src of Object.values(input.sources || {})) {
    if (src && src.urls && !src.content) {
      const p = src.urls.find((u) => fs.existsSync(u)) || src.urls[0];
      src.content = fs.readFileSync(p, 'utf8');
      delete src.urls;
    }
  }
  process.stdout.write(solc.compile(JSON.stringify(input)));
});
