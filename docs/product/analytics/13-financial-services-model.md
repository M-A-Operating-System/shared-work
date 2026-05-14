# 13 — Financial Services Semantic Model

## Overview

The platform ships a **Financial Services Reference Semantic Model** — a pre-built set of metric definitions, dimensions, hierarchies, and measure groups covering the principal analytical domains of wealth management, banking, investment management, and regulatory reporting.

Host applications seeding their SMR from `analyticalDomain: "wealth_management"`, `"banking"`, or `"investment_management"` receive the relevant subset of this reference model as their baseline. Definitions may be customised, extended, or superseded by tenant-specific definitions via the Admin API.

---

## Analytical domains

| Domain ID | Description | Applicable to |
|-----------|-------------|---------------|
| `portfolio` | Portfolio structure, positions, market values, cash flows | Wealth management, investment management |
| `performance` | Return metrics, attribution, benchmark comparison | Wealth management, investment management |
| `risk` | Market risk, credit risk, liquidity risk, VaR, factor exposures | All investment entities |
| `regulatory` | Capital adequacy, liquidity ratios, leverage ratios, reporting metrics | Banking, regulated investment firms |
| `counterparty` | Counterparty exposure, settlement risk, credit exposure | Banking, institutional trading |
| `benchmarks` | Index and benchmark data, benchmark decomposition | Wealth management, investment management |

---

## Portfolio domain

### Dimensions

| Dimension ID | Label | Type | Cardinality | Description |
|-------------|-------|------|-------------|-------------|
| `portfolio` | Portfolio | categorical | medium | Portfolio identifier |
| `asset_class` | Asset Class | categorical | low | Broad asset type (Equity, Fixed Income, Alternatives, Cash) |
| `sub_asset_class` | Sub-Asset Class | categorical | medium | Granular asset type |
| `security_type` | Security Type | categorical | medium | Instrument type (Common Stock, Corporate Bond, etc.) |
| `issuer` | Issuer | categorical | high | Issuer of the security |
| `geography` | Geography | categorical | medium | Country or region of domicile |
| `currency` | Currency | categorical | low | Instrument currency |
| `rating` | Credit Rating | categorical | low | External credit rating (AAA through D) |
| `date` | Date | temporal | unbounded | Valuation date |
| `sector` | Sector | categorical | medium | GICS or ICB sector |
| `benchmark` | Benchmark | categorical | low | Associated benchmark identifier |

### Core portfolio metrics

```yaml
# AUM — Assets Under Management
metric:
  id:          "aum"
  label:       "Assets Under Management"
  description: "Total market value of assets managed in the portfolio, expressed in the portfolio's base currency."
  formula:     "SUM(position_market_value)"
  unit:        "currency"
  aggregation:
    default:   "sum"
    allowed:   ["sum"]
    granularity: ["daily", "monthly", "quarterly", "annual"]
  dimensions:
    required:  ["portfolio", "date"]
    optional:  ["asset_class", "currency", "geography"]
  data:
    domain:    "portfolio"
    refresh_cadence: "daily"
  governance:
    classification: "INTERNAL"
```

```yaml
# Issuer Concentration
metric:
  id:          "issuer_concentration"
  label:       "Issuer Concentration"
  description: "Market value of positions in a given issuer as a percentage of total portfolio AUM."
  formula:     "SAFE_DIVIDE(SUM(position_market_value, FILTER(issuer = {{dim.issuer}})), SUM(position_market_value))"
  unit:        "percentage"
  aggregation:
    default:   "value_weighted_average"
    allowed:   ["value_weighted_average", "sum"]
    granularity: ["daily"]
  dimensions:
    required:  ["portfolio", "issuer", "date"]
  governance:
    classification: "INTERNAL"
```

---

## Performance domain

### Core performance metrics

```yaml
# Portfolio Return (Total Return, Net of Fees)
metric:
  id:          "portfolio_return"
  version:     "2.1.0"
  label:       "Portfolio Return"
  description: "Total return of the portfolio over the specified period, net of management and performance fees, expressed as a percentage. Calculated using the Modified Dietz method for sub-period returns, chain-linked for multi-period returns."
  formula:     "CHAIN_LINK(modified_dietz_return, time_period)"
  unit:        "percentage"
  aggregation:
    default:   "value_weighted_average"
    allowed:   ["value_weighted_average", "equal_weighted_average"]
    granularity: ["daily", "monthly", "quarterly", "annual", "since_inception"]
  display:
    format:    "percentage"
    decimals:  2
    benchmark_comparison: true

metric:
  id:          "benchmark_return"
  label:       "Benchmark Return"
  description: "Total return of the portfolio's designated benchmark index over the same period."
  formula:     "CHAIN_LINK(index_daily_return, time_period)"
  unit:        "percentage"
  dimensions:
    required:  ["portfolio", "benchmark", "date"]

metric:
  id:          "active_return"
  label:       "Active Return"
  description: "Portfolio return minus benchmark return (alpha). Positive active return indicates outperformance."
  formula:     "portfolio_return - benchmark_return"
  unit:        "percentage"
  lineage:
    upstream_metrics: ["portfolio_return", "benchmark_return"]

metric:
  id:          "tracking_error"
  label:       "Tracking Error"
  description: "Annualised standard deviation of the difference between portfolio returns and benchmark returns. Measures consistency of active return delivery."
  formula:     "ANNUALISE(STDDEV(portfolio_return - benchmark_return, time_period))"
  unit:        "percentage"
  aggregation:
    granularity: ["monthly", "quarterly", "annual"]

metric:
  id:          "information_ratio"
  label:       "Information Ratio"
  description: "Active return divided by tracking error. Measures risk-adjusted active return efficiency. Values above 0.5 indicate strong risk-adjusted outperformance."
  formula:     "SAFE_DIVIDE(active_return, tracking_error)"
  unit:        "ratio"
  display:
    decimals:  2
    sign_convention: "positive_is_good"

metric:
  id:          "sharpe_ratio"
  label:       "Sharpe Ratio"
  description: "Portfolio excess return above the risk-free rate divided by portfolio volatility. Measures risk-adjusted absolute return."
  formula:     "SAFE_DIVIDE(portfolio_return - risk_free_rate, portfolio_volatility)"
  unit:        "ratio"
```

---

## Risk domain

### Market risk metrics

```yaml
metric:
  id:          "var_95"
  label:       "Value at Risk (95%)"
  description: "The maximum expected loss over a 1-day horizon at a 95% confidence level, expressed as a percentage of portfolio AUM. Calculated using historical simulation over a 250-day lookback."
  formula:     "PERCENTILE(portfolio_daily_pnl_pct, 0.05) × -1"
  unit:        "percentage"
  aggregation:
    granularity: ["daily"]
  governance:
    classification: "INTERNAL"
    owner:       "head_of_risk"

metric:
  id:          "var_99"
  label:       "Value at Risk (99%)"
  description: "Maximum expected loss over a 1-day horizon at a 99% confidence level."
  formula:     "PERCENTILE(portfolio_daily_pnl_pct, 0.01) × -1"
  unit:        "percentage"

metric:
  id:          "cvar"
  label:       "Conditional Value at Risk (CVaR)"
  description: "Expected loss given that the loss exceeds the 95% VaR threshold. Also known as Expected Shortfall."
  formula:     "MEAN(portfolio_daily_pnl_pct, FILTER(portfolio_daily_pnl_pct < PERCENTILE(portfolio_daily_pnl_pct, 0.05))) × -1"
  unit:        "percentage"

metric:
  id:          "beta"
  label:       "Portfolio Beta"
  description: "Systematic risk of the portfolio relative to the benchmark. Beta of 1.0 means the portfolio moves in line with the benchmark."
  formula:     "COVARIANCE(portfolio_return, benchmark_return) / VARIANCE(benchmark_return)"
  unit:        "ratio"

metric:
  id:          "duration"
  label:       "Portfolio Duration"
  description: "Market-value-weighted average modified duration of the fixed income portfolio in years."
  formula:     "SAFE_DIVIDE(SUM(position_market_value × security_modified_duration), SUM(position_market_value))"
  unit:        "years"

metric:
  id:          "credit_spread_dv01"
  label:       "Credit Spread DV01"
  description: "Change in portfolio value for a 1 basis point parallel shift in credit spreads, expressed in base currency."
  formula:     "SUM(position_market_value × security_cs01)"
  unit:        "currency"
```

---

## Regulatory domain

### Liquidity metrics (Banking)

```yaml
metric:
  id:          "lcr"
  label:       "Liquidity Coverage Ratio"
  description: "High Quality Liquid Assets (HQLA) as a proportion of Net Cash Outflows (NCO) over a 30-day stress period. Basel III minimum: 100%. Expressed as a percentage."
  formula:     "SAFE_DIVIDE(hqla_total, net_cash_outflows_30d) × 100"
  unit:        "percentage"
  governance:
    classification:    "RESTRICTED"
    owner:             "treasury_risk_management"
  display:
    decimals:          1
    benchmark_comparison: false

metric:
  id:          "nsfr"
  label:       "Net Stable Funding Ratio"
  description: "Available Stable Funding (ASF) as a proportion of Required Stable Funding (RSF). Basel III minimum: 100%."
  formula:     "SAFE_DIVIDE(available_stable_funding, required_stable_funding) × 100"
  unit:        "percentage"

metric:
  id:          "leverage_ratio"
  label:       "Leverage Ratio"
  description: "Tier 1 Capital divided by Total Exposure. Basel III minimum: 3%."
  formula:     "SAFE_DIVIDE(tier1_capital, total_exposure) × 100"
  unit:        "percentage"
```

---

## Hierarchies reference

### Asset class hierarchy

```
Asset Class (Level 1)
├── Equity
│   ├── Developed Market Equity
│   │   ├── Large Cap
│   │   ├── Mid Cap
│   │   └── Small Cap
│   └── Emerging Market Equity
├── Fixed Income
│   ├── Government Bonds
│   │   ├── Developed Market Government
│   │   └── Emerging Market Government
│   ├── Corporate Bonds
│   │   ├── Investment Grade
│   │   └── High Yield
│   └── Securitised
├── Alternatives
│   ├── Private Equity
│   ├── Real Estate
│   ├── Infrastructure
│   └── Hedge Funds
└── Cash & Money Market
```

### Geography hierarchy

```
Geography (Level 1: Region)
├── Europe, Middle East & Africa
│   ├── Western Europe
│   │   └── [Country level]
│   ├── Eastern Europe
│   └── Middle East & Africa
├── Americas
│   ├── North America
│   ├── Latin America
│   └── Caribbean
└── Asia Pacific
    ├── Developed Asia
    ├── Emerging Asia
    └── Australasia
```

### Time hierarchy

```
Year (Level 1)
└── Quarter
    └── Month
        └── Week
            └── Day
```

---

## Measure groups reference

| Measure Group ID | Label | Metrics included |
|-----------------|-------|-----------------|
| `performance_metrics` | Performance Metrics | `portfolio_return`, `benchmark_return`, `active_return`, `tracking_error`, `information_ratio`, `sharpe_ratio` |
| `risk_metrics` | Risk Metrics | `var_95`, `var_99`, `cvar`, `beta`, `duration`, `credit_spread_dv01` |
| `portfolio_summary` | Portfolio Summary | `aum`, `portfolio_return`, `benchmark_return`, `active_return`, `var_95` |
| `concentration_metrics` | Concentration Metrics | `issuer_concentration`, `asset_class_weight`, `geography_weight`, `sector_weight` |
| `regulatory_metrics` | Regulatory Metrics | `lcr`, `nsfr`, `leverage_ratio` |
