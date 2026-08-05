#!/usr/bin/env node
/* Compiles the Karma Ecosystem contracts with solc + OpenZeppelin.
 * Usage: node compile.js <path-to-solc-package-dir> <output-dir>
 */
const path = require("path");
const fs = require("fs");

const SOLC_DIR = process.argv[2] || "/tmp/solcwork/node_modules";
const OUT_DIR = process.argv[3] || path.join(__dirname, "build");

const solc = require(path.join(SOLC_DIR, "solc"));

function findImports(p) {
  try {
    let file;
    if (p.startsWith("@openzeppelin/")) {
      file = path.join(SOLC_DIR, p);
    } else {
      file = path.join(__dirname, "contracts", p);
    }
    return { contents: fs.readFileSync(file, "utf8") };
  } catch (e) {
    return { error: e.message };
  }
}

const CONTRACTS_DIR = path.join(__dirname, ".");
const sources = {};
for (const f of fs.readdirSync(CONTRACTS_DIR)) {
  if (f.endsWith(".sol")) {
    sources[`contracts/${f}`] = {
      content: fs.readFileSync(path.join(CONTRACTS_DIR, f), "utf8"),
    };
  }
}

const input = {
  language: "Solidity",
  sources,
  settings: {
    optimizer: { enabled: true, runs: 200 },
    evmVersion: "shanghai",  // PUSH0 ok; avoids Cancun TSTORE/MCOPY (ganache-safe)
    outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } },
  },
};

const output = JSON.parse(solc.compile(JSON.stringify(input), { import: findImports }));
if (output.errors) {
  for (const e of output.errors) {
    console.error(e.formattedMessage || e.message);
  }
  if (output.errors.some((e) => e.severity === "error")) process.exit(1);
}

fs.mkdirSync(OUT_DIR, { recursive: true });
for (const [file, contracts] of Object.entries(output.contracts)) {
  for (const [name, artifact] of Object.entries(contracts)) {
    const json = {
      contractName: name,
      abi: artifact.abi,
      bytecode: artifact.evm.bytecode.object,
      sourceFile: file,
      compiler: `solc ${solc.version()}`,
    };
    fs.writeFileSync(
      path.join(OUT_DIR, `${name}.json`),
      JSON.stringify(json, null, 2)
    );
    console.log(`built: ${name} -> build/${name}.json`);
  }
}
console.log("OK");
