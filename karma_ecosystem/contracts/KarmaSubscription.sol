// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "./KarmaTreasury.sol";

/**
 * @title KarmaSubscription
 * @notice "Ultimate Pays" subscription plans for app builder / coding agents.
 * @dev    Every subscription payment is a real on-chain transaction. A share
 *         of each payment (revenueFeeBps, managed by the treasury) is
 *         automatically split to the KarmaTreasury; the rest goes to the
 *         protocol wallet. No manual bookkeeping required — it is enforced
 *         by the smart contract itself.
 */
contract KarmaSubscription is AccessControl {
    struct Plan {
        uint256 priceWei;        // price in native token (wei)
        uint256 durationSeconds; // plan length
        bool active;
    }

    KarmaTreasury public immutable treasury;
    address public immutable protocolWallet;

    mapping(uint256 => Plan) public plans;
    mapping(address => uint256) public activeUntil; // unix timestamp

    uint256 public planCount;
    uint256 public totalSubscriptions;
    uint256 public totalRevenueWei;
    uint256 public totalFeesCollectedWei;

    event PlanCreated(
        uint256 indexed planId,
        uint256 priceWei,
        uint256 durationSeconds
    );
    event PlanToggled(uint256 indexed planId, bool active);
    event Subscribed(
        address indexed subscriber,
        uint256 indexed planId,
        uint256 amountWei,
        uint256 feeWei,
        uint256 activeUntilTimestamp
    );

    constructor(address _treasury, address _protocolWallet, address _deployer) {
        require(_treasury != address(0), "no treasury");
        require(_protocolWallet != address(0), "no protocol wallet");
        treasury = KarmaTreasury(payable(_treasury));
        protocolWallet = _protocolWallet;
        _grantRole(DEFAULT_ADMIN_ROLE, _deployer);
    }

    function createPlan(
        uint256 priceWei,
        uint256 durationSeconds
    ) external onlyRole(DEFAULT_ADMIN_ROLE) returns (uint256 planId) {
        require(priceWei > 0, "price must be > 0");
        require(durationSeconds > 0, "duration must be > 0");
        planId = planCount;
        plans[planId] = Plan(priceWei, durationSeconds, true);
        planCount++;
        emit PlanCreated(planId, priceWei, durationSeconds);
        return planId;
    }

    function setPlanActive(uint256 planId, bool active) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(planId < planCount, "no such plan");
        plans[planId].active = active;
        emit PlanToggled(planId, active);
    }

    /**
     * @notice Subscribe (or renew) — payment is msg.value (real tx, real hash).
     * @dev    The automation revenue fee is split on-chain:
     *         fee = msg.value * treasury.revenueFeeBps() / 10000  -> treasury
     *         remainder -> protocol wallet.
     */
    function subscribe(uint256 planId) external payable {
        Plan storage p = plans[planId];
        require(planId < planCount, "no such plan");
        require(p.active, "plan inactive");
        require(msg.value >= p.priceWei, "payment below plan price");

        uint256 feeWei = (msg.value * treasury.revenueFeeBps()) / 10000;
        uint256 restWei = msg.value - feeWei;

        treasury.deposit{value: feeWei}("subscription");
        if (restWei > 0) {
            (bool ok, ) = payable(protocolWallet).call{value: restWei}("");
            require(ok, "protocol transfer failed");
        }

        uint256 until = block.timestamp + p.durationSeconds;
        activeUntil[msg.sender] = until;

        totalSubscriptions++;
        totalRevenueWei += msg.value;
        totalFeesCollectedWei += feeWei;

        emit Subscribed(msg.sender, planId, msg.value, feeWei, until);
    }

    function isActive(address user) external view returns (bool) {
        return activeUntil[user] > block.timestamp;
    }

    function getActiveUntil(address user) external view returns (uint256) {
        return activeUntil[user];
    }
}
