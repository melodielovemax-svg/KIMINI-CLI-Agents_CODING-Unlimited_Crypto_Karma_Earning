// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./MAToken.sol";

/**
 * @title KarmaSwap
 * @notice Swaps MA tokens into crypto currencies — ETH (native), USDT and
 *         BTC (pegged ERC20 representations). Real transactions, real hashes.
 *
 * Rates (settable by the treasury admin, in "units of pegged currency per MA"):
 *   MA -> ETH  : rate 0.00001   => 1000 MA = 0.01 ETH
 *   MA -> USDT : rate 0.0001    => 1000 MA = 0.10 USDT (18-decimal pegged)
 *   MA -> BTC  : rate 0.00000005 => 1M MA = 0.05 BTC
 *
 * The pool burns MA and pays out from its funded balance; the treasury
 * refills the pool automatically (it owns 20% of the MA supply).
 */
contract KarmaSwap is AccessControl {
    bytes32 public constant FILLER_ROLE = keccak256("FILLER_ROLE");

    MAToken public immutable ma;
    IERC20 public immutable wusdt;
    IERC20 public immutable wbtc;

    uint256 public rateEthPerMa;    // wei of ETH per 1e18 MA
    uint256 public rateUsdtPerMa;   // 1e18 USDT per 1e18 MA
    uint256 public rateBtcPerMa;    // 1e18 BTC  per 1e18 MA

    uint256 public totalSwappedToEth;
    uint256 public totalSwappedToUsdt;
    uint256 public totalSwappedToBtc;
    uint256 public totalMaBurned;

    event SwappedToEth(address indexed user, uint256 maIn, uint256 ethOut);
    event SwappedToUsdt(address indexed user, uint256 maIn, uint256 usdtOut);
    event SwappedToBtc(address indexed user, uint256 maIn, uint256 btcOut);
    event RatesUpdated(uint256 ethRate, uint256 usdtRate, uint256 btcRate);

    constructor(
        address _ma,
        address _wusdt,
        address _wbtc,
        uint256 _rateEth,
        uint256 _rateUsdt,
        uint256 _rateBtc,
        address _admin
    ) {
        ma = MAToken(_ma);
        wusdt = IERC20(_wusdt);
        wbtc = IERC20(_wbtc);
        rateEthPerMa = _rateEth;
        rateUsdtPerMa = _rateUsdt;
        rateBtcPerMa = _rateBtc;
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(FILLER_ROLE, _admin);
    }

    function setRates(uint256 ethRate, uint256 usdtRate, uint256 btcRate)
        external onlyRole(DEFAULT_ADMIN_ROLE)
    {
        rateEthPerMa = ethRate;
        rateUsdtPerMa = usdtRate;
        rateBtcPerMa = btcRate;
        emit RatesUpdated(ethRate, usdtRate, btcRate);
    }

    /// @notice Swap MA -> native ETH (real transfer, real hash).
    function swapMaToEth(uint256 maIn) external {
        require(maIn > 0, "zero amount");
        uint256 out = (maIn * rateEthPerMa) / 1e18;
        require(out > 0, "output too small");
        require(address(this).balance >= out, "pool dry - treasury refill pending");
        ma.transferFrom(msg.sender, address(this), maIn);
        ma.burn(maIn);
        totalMaBurned += maIn;
        totalSwappedToEth += out;
        payable(msg.sender).transfer(out);
        emit SwappedToEth(msg.sender, maIn, out);
    }

    /// @notice Swap MA -> pegged USDT (real ERC20 transfer, real hash).
    function swapMaToUsdt(uint256 maIn) external {
        require(maIn > 0, "zero amount");
        uint256 out = (maIn * rateUsdtPerMa) / 1e18;
        require(out > 0, "output too small");
        require(wusdt.balanceOf(address(this)) >= out, "pool dry - treasury refill pending");
        ma.transferFrom(msg.sender, address(this), maIn);
        ma.burn(maIn);
        totalMaBurned += maIn;
        totalSwappedToUsdt += out;
        require(wusdt.transfer(msg.sender, out), "usdt transfer failed");
        emit SwappedToUsdt(msg.sender, maIn, out);
    }

    /// @notice Swap MA -> pegged BTC (real ERC20 transfer, real hash).
    function swapMaToBtc(uint256 maIn) external {
        require(maIn > 0, "zero amount");
        uint256 out = (maIn * rateBtcPerMa) / 1e18;
        require(out > 0, "output too small");
        require(wbtc.balanceOf(address(this)) >= out, "pool dry - treasury refill pending");
        ma.transferFrom(msg.sender, address(this), maIn);
        ma.burn(maIn);
        totalMaBurned += maIn;
        totalSwappedToBtc += out;
        require(wbtc.transfer(msg.sender, out), "btc transfer failed");
        emit SwappedToBtc(msg.sender, maIn, out);
    }

    /// @notice Treasury automation: refill liquidity pools (MA + pegged + ETH).
    function refill(uint256 ethWei, uint256 usdtAmount, uint256 btcAmount)
        external payable onlyRole(FILLER_ROLE)
    {
        if (usdtAmount > 0) {
            require(wusdt.transferFrom(msg.sender, address(this), usdtAmount), "usdt refill failed");
        }
        if (btcAmount > 0) {
            require(wbtc.transferFrom(msg.sender, address(this), btcAmount), "btc refill failed");
        }
    }

    receive() external payable {}
}
