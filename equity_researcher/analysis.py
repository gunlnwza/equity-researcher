import yfinance as yf
import numpy as np
import pandas as pd

# NOTE: too "quant-risk" flavored, Financial Engineering module should use the "accountant" method.

TRADING_DAYS = 252
CONFIDENCE = 0.95


def load_prices(tickers: list[str], period: str = "5y") -> pd.DataFrame:
    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        progress=False,
    )

    prices = data["Close"]

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    return prices.dropna()


def analyze_nke(prices: pd.DataFrame) -> dict:
    returns = prices.pct_change().dropna()

    nke = returns["NKE"]
    market = returns["SPY"]

    # -------------------------
    # Return / volatility
    # -------------------------

    annual_return = nke.mean() * TRADING_DAYS
    annual_vol = nke.std() * np.sqrt(TRADING_DAYS)

    # -------------------------
    # Market beta
    # -------------------------

    covariance = np.cov(nke, market, ddof=1)[0, 1]
    beta = covariance / market.var()

    # -------------------------
    # Historical VaR / ES
    # -------------------------

    var = -np.quantile(nke, 1 - CONFIDENCE)

    tail = nke[nke <= -var]
    expected_shortfall = -tail.mean()

    # -------------------------
    # Maximum drawdown
    # -------------------------

    nke_price = prices["NKE"]

    running_max = nke_price.cummax()
    drawdown = nke_price / running_max - 1

    max_drawdown = drawdown.min()

    return {
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "beta": beta,
        "VaR_95_daily": var,
        "ES_95_daily": expected_shortfall,
        "max_drawdown": max_drawdown,
    }


def monte_carlo(
    prices: pd.DataFrame,
    *,
    horizon_days: int = 252,
    simulations: int = 100_000,
) -> np.ndarray:

    log_returns = np.log(
        prices["NKE"] / prices["NKE"].shift(1)
    ).dropna()

    mu = log_returns.mean()
    sigma = log_returns.std()

    S0 = prices["NKE"].iloc[-1]

    rng = np.random.default_rng(42)

    z = rng.normal(size=simulations)

    terminal_prices = S0 * np.exp(
        (mu - 0.5 * sigma**2) * horizon_days
        + sigma * np.sqrt(horizon_days) * z
    )

    return terminal_prices


def main():
    prices = load_prices(["NKE", "SPY"])

    metrics = analyze_nke(prices)

    print("\n=== NKE Financial Engineering ===")

    for name, value in metrics.items():
        print(f"{name:25}: {value:.4f}")

    terminal = monte_carlo(prices)

    current_price = prices["NKE"].iloc[-1]

    print("\n=== 1-Year Monte Carlo ===")
    print(f"Current price       : ${current_price:.2f}")
    print(f"Expected terminal   : ${terminal.mean():.2f}")
    print(f"Median terminal     : ${np.median(terminal):.2f}")
    print(f"5th percentile      : ${np.quantile(terminal, 0.05):.2f}")
    print(f"95th percentile     : ${np.quantile(terminal, 0.95):.2f}")

    probability_profit = np.mean(terminal > current_price)

    print(
        f"P(S_T > S_0)        : "
        f"{probability_profit:.2%}"
    )


if __name__ == "__main__":
    main()