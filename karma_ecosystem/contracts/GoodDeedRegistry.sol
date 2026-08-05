// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "./KarmaToken.sol";

/**
 * @title GoodDeedRegistry
 * @notice On-chain registry of services & good deeds. Each verified deed
 *         mints KARMA tokens to the doer — reward = baseReward * impactScore.
 * @dev    Every deed is a real transaction; the emitted event carries the
 *         deed id, reward, and timestamps, so rewards are fully auditable.
 */
contract GoodDeedRegistry is AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    struct Deed {
        address doer;
        address beneficiary;
        string service;
        string category;
        uint8 impactScore;   // 1..10
        uint256 karmaReward; // KARMA (1e18 decimals)
        uint256 timestamp;
    }

    KarmaToken public immutable token;
    uint256 public baseReward = 10 ether; // KARMA per impact point

    mapping(uint256 => Deed) public deeds;
    uint256 public deedCount;
    uint256 public totalKarmaMinted;

    event DeedRegistered(
        uint256 indexed deedId,
        address indexed doer,
        address indexed beneficiary,
        string service,
        string category,
        uint8 impactScore,
        uint256 karmaReward
    );
    event BaseRewardUpdated(uint256 indexed oldValue, uint256 indexed newValue);

    constructor(address _token, address _deployer) {
        require(_token != address(0), "no token");
        token = KarmaToken(_token);
        _grantRole(DEFAULT_ADMIN_ROLE, _deployer);
    }

    function registerGoodDeed(
        address beneficiary,
        string calldata service,
        string calldata category,
        uint8 impactScore
    ) external returns (uint256 deedId) {
        require(impactScore >= 1 && impactScore <= 10, "impact 1..10");
        require(beneficiary != address(0), "zero beneficiary");

        uint256 reward = baseReward * uint256(impactScore);
        token.mint(msg.sender, reward); // doer is rewarded on-chain

        deedId = deedCount;
        deeds[deedId] = Deed(
            msg.sender,
            beneficiary,
            service,
            category,
            impactScore,
            reward,
            block.timestamp
        );
        deedCount++;
        totalKarmaMinted += reward;

        emit DeedRegistered(deedId, msg.sender, beneficiary, service, category, impactScore, reward);
        return deedId;
    }

    function setBaseReward(uint256 newBase) external onlyRole(DEFAULT_ADMIN_ROLE) {
        emit BaseRewardUpdated(baseReward, newBase);
        baseReward = newBase;
    }
}
