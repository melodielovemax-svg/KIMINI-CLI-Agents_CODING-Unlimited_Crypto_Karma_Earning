// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title KarmaTreasury
 * @notice Collects the automated revenue fee from every subscription payment
 *         and pays coding agents / app builders automatically (keeper role).
 * @dev    All fee inflows are recorded in a public on-chain ledger. Payouts
 *         are emitted with a deterministic payoutId hash for auditability.
 */
contract KarmaTreasury is AccessControl {
    bytes32 public constant AUTOMATOR_ROLE = keccak256("AUTOMATOR_ROLE");

    /// @notice Revenue automation fee in basis points (10000 = 100%).
    uint256 public revenueFeeBps = 2000; // 20% default
    uint256 public totalCollected;
    uint256 public totalDistributed;
    uint256 public payoutCount;

    event FeeUpdated(uint256 indexed oldBps, uint256 indexed newBps);
    event Deposit(address indexed from, uint256 amount, string source);
    event Payout(
        address indexed agent,
        uint256 amount,
        bytes32 indexed payoutId,
        uint256 payoutNumber
    );

    constructor(address _deployer) {
        _grantRole(DEFAULT_ADMIN_ROLE, _deployer);
        _grantRole(AUTOMATOR_ROLE, _deployer);
    }

    /// @notice Deposits fee revenue (e.g. from the subscription contract).
    function deposit(string calldata source) external payable {
        totalCollected += msg.value;
        emit Deposit(msg.sender, msg.value, source);
    }

    /// @notice Keeper automation: pays a batch of coding agents from the treasury.
    function automatePayout(
        address[] calldata agents,
        uint256[] calldata amounts
    ) external onlyRole(AUTOMATOR_ROLE) returns (bytes32 payoutId) {
        require(agents.length == amounts.length, "length mismatch");
        require(agents.length > 0, "empty batch");
        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        require(total <= address(this).balance, "insufficient treasury");

        for (uint256 i = 0; i < agents.length; i++) {
            require(agents[i] != address(0), "zero address");
            payable(agents[i]).transfer(amounts[i]);
            emit Payout(agents[i], amounts[i], keccak256(abi.encodePacked(agents, amounts, payoutCount)), payoutCount);
        }
        payoutCount++;
        totalDistributed += total;
        payoutId = keccak256(abi.encodePacked(agents, amounts, block.number));
        return payoutId;
    }

    /// @notice Admin adjusts the automation revenue fee.
    function setRevenueFeeBps(uint256 bps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(bps <= 5000, "max 50%");
        emit FeeUpdated(revenueFeeBps, bps);
        revenueFeeBps = bps;
    }

    /// @notice Grants keeper rights to an automation service.
    function grantAutomator(address keeper) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(AUTOMATOR_ROLE, keeper);
    }

    receive() external payable {
        emit Deposit(msg.sender, msg.value, "direct");
    }
}
