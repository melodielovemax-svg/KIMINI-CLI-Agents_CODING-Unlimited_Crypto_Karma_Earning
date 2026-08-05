#!/usr/bin/env node
/* Karma Ecosystem local blockchain node.
 * Exposes a persistent Ganache EVM (chainId 1337) over HTTP JSON-RPC so that
 * every `karma-eco` CLI command talks to the SAME chain across processes.
 *   Usage: node localnode.mjs            (default port 8545)
 *   Env:   KARMA_NODE_PORT, KARMA_NODE_MNEMONIC
 */
import http from "http";
import ganache from "ganache";

const PORT = parseInt(process.env.KARMA_NODE_PORT || "8545", 10);
const MNEMONIC =
  process.env.KARMA_NODE_MNEMONIC ||
  "test test test test test test test test test test test junk"; // dev only

const provider = ganache.provider({
  wallet: { mnemonic: MNEMONIC, totalAccounts: 10 },
  chain: { chainId: 1337, hardfork: "shanghai" },
  logging: { quiet: true },
});

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", async () => {
    let parsed;
    try {
      parsed = JSON.parse(body || "{}");
    } catch {
      res.writeHead(400, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ jsonrpc: "2.0", error: "bad json" }));
    }
    try {
      if (parsed.method === "web3_clientVersion") {
        return res.end(
          JSON.stringify({ jsonrpc: "2.0", id: parsed.id, result: "karma-eco-localnode/ganache" })
        );
      }
      const result = await provider.request({ method: parsed.method, params: parsed.params || [] });
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", id: parsed.id, result }));
    } catch (e) {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          jsonrpc: "2.0",
          id: parsed.id,
          error: { code: -32000, message: String((e && e.message) || e) },
        })
      );
    }
  });
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`[karma-eco] local blockchain node listening on http://0.0.0.0:${PORT} (chainId 1337)`);
});
