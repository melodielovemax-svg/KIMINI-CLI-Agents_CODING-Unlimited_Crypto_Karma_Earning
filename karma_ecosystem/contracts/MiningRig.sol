// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "./MAToken.sol";

/**
 * @title MiningRig
 * @notice On-chain crypto mining automation for the Karma Ecosystem.
 *
 * Every `mine()` call is a REAL transaction with a REAL hash and block —
 * the miner earns MA rewards emitted by the rig (backed by the 40% mining
 * allocation of the MA supply, minted only up to the hard cap).
 *
 * Each miner has a cooldown between mines. The keeper can `mine()` on
 * behalf of subscribers (fully automated loop), and miners can `sweep()`
 * their earned MA directly to any wallet (e.g. a MetaMask address).
 */
contract MiningRig is AccessControl {
    bytes32 public constant KEEPER_ROLE = keccak256("KEEPER_ROLE");

    MAToken public immutable ma;
    uint256 public rewardPerMine = 100 * 1e18; // 100 MA per mine
    uint256 public cooldownSeconds = 60;

    mapping(address => uint256) public lastMineAt;
    uint256 public totalMined;
    uint256 public mineCount;

    event Mined(address indexed miner, uint256 reward, uint256 blockNumber);
    event Swept(address indexed miner, address indexed to, uint256 amount);
    event ConfigUpdated(uint256 rewardPerMine, uint256 cooldownSeconds);

    constructor(address _ma, address _admin) {
        ma = MAToken(_ma);
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(KEEPER_ROLE, _admin);
    }

    /// @notice Mine one block — real tx, real hash, MA minted to miner.
    function mine() external returns (uint256 reward) {
        require(block.timestamp - lastMineAt[msg.sender] >= cooldownSeconds,
                "mining cooldown active");
        reward = _payout(msg.sender);
        lastMineAt[msg.sender] = block.timestamp;
    }

    /// @notice Keeper automation mines on behalf of many miners in one tx.
    function mineBatch(address[] calldata miners) external onlyRole(KEEPER_ROLE) {
        for (uint256 i = 0; i < miners.length; i++) {
            if (block.timestamp - lastMineAt[miners[i]] >= cooldownSeconds) {
                lastMineAt[miners[i]] = block.timestamp;
                _payout(miners[i]);
            }
        }
    }

    function _payout(address miner) internal returns (uint256 reward) {
        reward = rewardPerMine;
        ma.mint(miner, reward);
        totalMined += reward;
        mineCount++;
        emit Mined(miner, reward, block.number);
    }

    /**
     * @notice Send the miner's MA to an external wallet (e.g. MetaMask).
     * @dev    Uses transferFrom: the miner approves the rig, then the rig
     *         pulls the MA and forwards it — msg.sender of the ERC20
     *         transfer is the rig, so an allowance is required.
     */
    function sweep(address payable to) external returns (uint256 amount) {
        require(to != address(0), "zero address");
        amount = ma.allowance(msg.sender, address(this));
        require(amount > 0, "no allowance - approve the rig first");
        uint256 max = ma.balanceOf(msg.sender);
        if (amount > max) amount = max;
        require(amount > 0, "nothing to sweep");
        ma.transferFrom(msg.sender, to, amount);
        emit Swept(msg.sender, to, amount);
    }

    function setConfig(uint256 reward, uint256 cooldown)
        external onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(reward > 0, "reward must be > 0");
        rewardPerMine = reward;
        cooldownSeconds = cooldown;
        emit ConfigUpdated(reward, cooldown);
    }
}
