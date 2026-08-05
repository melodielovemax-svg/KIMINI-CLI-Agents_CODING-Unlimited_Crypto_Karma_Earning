"""Chain network presets. `local` is a real EVM (in-memory) producing real
transaction hashes & blocks; `sepolia` / `polygon_amoy` are real public
testnets reachable over RPC. Same contract addresses, same code paths.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Network:
    id: str
    name: str
    chain_id: int
    rpc_url: str | None   # None => embedded local EVM (EthereumTesterProvider)
    currency: str
    block_explorer: str | None
    is_testnet: bool = True
    faucet: bool = False  # can auto-fund new wallets from the admin faucet


NETWORKS = {
    # Embedded real-EVM: real hashes, instant blocks, pre-funded accounts.
    # NOTE: state does NOT persist across processes (tests use this).
    "local": Network("local", "Local EVM (embedded)", 1337, None, "ETH", None, True, True),
    # Persistent local dev chain: `node karma_ecosystem/scripts/localnode.mjs`
    # (Ganache, chainId 1337). Same chain across all CLI commands.
    "localnode": Network(
        "localnode", "Local Node (Ganache)", 1337,
        "http://127.0.0.1:8545", "ETH", None, True, True,
    ),
    # Public Ethereum Sepolia testnet (real chain, real hashes).
    "sepolia": Network(
        "sepolia",
        "Ethereum Sepolia (testnet)",
        11155111,
        "https://ethereum-sepolia-rpc.publicnode.com",
        "ETH",
        "https://sepolia.etherscan.io/tx/",
        True,
        False,
    ),
    # Public Polygon Amoy testnet (real chain, real hashes).
    "polygon_amoy": Network(
        "polygon_amoy",
        "Polygon Amoy (testnet)",
        80002,
        "https://rpc-amoy.polygon.technology",
        "POL",
        "https://www.oklink.com/amoy/tx/",
        True,
        False,
    ),
}


def get_network(network_id: str) -> Network:
    if network_id not in NETWORKS:
        raise KeyError(f"unknown network {network_id!r}; choose from {sorted(NETWORKS)}")
    return NETWORKS[network_id]
