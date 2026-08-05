// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title KarmaToken
 * @notice KARMA — the reward token of the Karma Ecosystem.
 * @dev   Minted only by the GoodDeedRegistry (MINTER_ROLE) when a good deed
 *        or paid service is verified on-chain. Burnable by holders.
 */
contract KarmaToken is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    constructor() ERC20("Karma Ecosystem Token", "KARMA") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
