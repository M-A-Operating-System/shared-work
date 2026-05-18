# 13 — Example Industry Model: Financial Services

## Overview

The platform ships a **Financial Services Reference Semantic Model** — an example industry model demonstrating how pre-built metric definitions, dimensions, hierarchies, and measure groups can be packaged for a specific domain. This is a reference implementation, not a prescriptive schema. It covers wealth management, banking, investment management, and regulatory reporting.

Host applications seeding their SMR from `analyticalDomain: "wealth_management"`, `"banking"`, or `"investment_management"` receive the relevant subset as their baseline. Definitions may be customised, extended, or superseded via the Admin API.

For full metric definition patterns, see [04-semantic-metrics-registry.md](./04-semantic-metrics-registry.md).

---

## Analytical domains

| Domain | Description | Representative metrics |
|--------|-------------|----------------------|
| **Portfolio** | Portfolio structure, positions, market values, cash flows | `aum`, `issuer_concentration`, `asset_class_weight`, `cash_balance`, `nav` |
| **Performance** | Return metrics, attribution, benchmark comparison | `portfolio_return`, `benchmark_return`, `active_return`, `tracking_error`, `information_ratio`, `sharpe_ratio` |
| **Risk** | Market risk, credit risk, liquidity risk, factor exposures | `var_95`, `var_99`, `cvar`, `beta`, `duration`, `credit_spread_dv01` |
| **Regulatory** | Capital adequacy, liquidity ratios, leverage, reporting metrics | `lcr`, `nsfr`, `leverage_ratio`, `tier1_capital_ratio`, `concentration_limit_utilisation` |
| **Counterparty** | Counterparty exposure, settlement risk, credit exposure | `counterparty_exposure`, `settlement_risk`, `credit_exposure_pfe`, `cva` |
| **Benchmarks** | Index and benchmark data, benchmark decomposition | `index_return`, `index_constituent_weight`, `benchmark_active_weight`, `tracking_difference` |

---

## Hierarchies

### Asset class hierarchy

```
Asset Class (Level 1)
├── Equity
│   ├── Developed Market Equity (Large Cap / Mid Cap / Small Cap)
│   └── Emerging Market Equity
├── Fixed Income
│   ├── Government Bonds (Developed / Emerging)
│   ├── Corporate Bonds (Investment Grade / High Yield)
│   └── Securitised
├── Alternatives (Private Equity / Real Estate / Infrastructure / Hedge Funds)
└── Cash & Money Market
```

### Geography hierarchy

```
Geography (Level 1: Region)
├── Europe, Middle East & Africa (Western Europe / Eastern Europe / MEA)
├── Americas (North America / Latin America / Caribbean)
└── Asia Pacific (Developed Asia / Emerging Asia / Australasia)
```

### Time hierarchy

```
Year → Quarter → Month → Week → Day
```
