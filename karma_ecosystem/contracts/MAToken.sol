// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title MAToken
 * @notice MA — the gamified karma token of the Karma Ecosystem.
 *
 * TOKENOMICS (hard-capped supply, no inflation after cap):
 *   Total supply           1,000,000,000 MA
 *   Mining rewards         40% (400M)   — distributed by the MiningRig
 *   Karma good-deed rewards 25% (250M)  — minted by the GoodDeedRegistry
 *   Treasury reserve       20% (200M)   — liquidity, payouts, buybacks
 *   Team & partners        10% (100M)   — 24-month linear vesting
 *   Ecosystem reserve       5%  (50M)   — grants, bounties, community
 *
 * MA is exchangeable for ETH / USDT / BTC through the KarmaSwap contract
 * (fixed-rate swap pool funded by the treasury) — all real transactions.
 */
contract MAToken is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    uint256 public constant HARD_CAP = 1_000_000_000 * 1e18;

    constructor() ERC20("MA Token", "MA") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        // team & partners 10% pre-minted (vested off-chain schedule documented)
        _mint(msg.sender, HARD_CAP * 10 / 100);
    }

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        require(totalSupply() + amount <= HARD_CAP, "hard cap reached");
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
