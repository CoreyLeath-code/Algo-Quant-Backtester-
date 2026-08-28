# Quantitative metric definitions

The canonical v0.1 engine computes descriptive metrics from **net bar returns after configured turnover costs**. These are research statistics, not trading recommendations or evidence of predictive skill.

| Metric | Definition used in v0.1 |
|---|---|
| Total return | `prod(1 + net_return_t) - 1` |
| CAGR | Total compounded growth annualized using the configured bars-per-year factor |
| Annualized volatility | Sample standard deviation of net bar returns × `sqrt(trading_days)` |
| Sharpe ratio | Mean excess bar return ÷ sample standard deviation × `sqrt(trading_days)` |
| Sortino ratio | Mean excess bar return ÷ downside RMS deviation × `sqrt(trading_days)` |
| Max drawdown | Minimum of `equity / running_max(equity) - 1` |
| Calmar ratio | CAGR ÷ absolute max drawdown when drawdown is non-zero |
| Win rate | Fraction of non-zero net-return bars that are positive |
| Profit factor | Sum of positive net returns ÷ absolute sum of negative net returns |
| Expectancy | Mean net bar return |

## Interpretation boundary

The implementation treats returns as bar-level observations, so `win_rate`, `profit_factor`, and `expectancy` are **bar-return statistics**, not trade-ledger statistics. A future execution-ledger model should separate fills/trades from bars before these metrics are labeled as per-trade statistics.

The v0.1 benchmark records a deterministic metric snapshot for reproducibility. Those values come from seeded synthetic prices and must not be interpreted as an estimated live return, alpha, or model-quality result.
