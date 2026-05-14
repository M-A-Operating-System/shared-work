# 06 — Federated Query Planning

## Overview

The **Federated Query Planner (FQP)** is the component that receives a validated Logical Query Plan (LQP) from the Analytical Intent Validator, decomposes it into backend-specific sub-plans, routes sub-plans to registered execution backends, manages result assembly, and handles caching and materialisation.

The FQP is the only component in the platform that has knowledge of physical execution backends. No other component — not the Analytical Intent Validator, not the Semantic Intent Layer, not the AI model — has access to backend connection details or physical schema information.

---

## FQP architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  Federated Query Planner                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  1. LQP Reception & Governance Validation                │ │
│  │  (validates cost estimate, complexity, classification)    │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  2. Cache Check                                          │ │
│  │  (exact match and approximate match on LQP signature)    │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │ cache miss                              │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  3. Sub-plan Decomposition                               │ │
│  │  (split LQP into sub-plans by data affinity)             │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  4. Backend Selection & Routing                          │ │
│  │  (match sub-plans to backends by affinity + capability)  │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  5. Physical Query Generation                            │ │
│  │  (translate sub-plans to engine-specific query dialect)  │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  6. Parallel Execution & Coordination                    │ │
│  │  (execute sub-plans concurrently; handle timeouts)       │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  7. Result Assembly & Reconciliation                     │ │
│  │  (join sub-results by shared dimensions; apply masks)    │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  8. Result Caching & Materialisation                     │ │
│  │  (write result to cache; update materialisation index)   │ │
│  └───────────────────┬──────────────────────────────────────┘ │
│                      │                                         │
│  ┌───────────────────▼──────────────────────────────────────┐ │
│  │  9. Lineage Record Writing                               │ │
│  │  (write complete execution trace to lineage store)       │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Sub-plan decomposition

The FQP decomposes an LQP into sub-plans by **data affinity** — the logical data domain declared by each metric in its SMR definition.

**Example LQP decomposition:**

LQP requesting `portfolio_return` (affinity: `portfolio`) and `var_95` (affinity: `risk_metrics`) by `portfolio` and `date`:

```
LQP
├── Sub-plan A: portfolio_return, aum BY portfolio, date
│   └── Affinity: portfolio → Engine: snowflake-primary
│
└── Sub-plan B: var_95, var_limit BY portfolio, date
    └── Affinity: risk_metrics → Engine: dbt-semantic
```

The shared dimensions (`portfolio`, `date`) become the join keys for result assembly.

### Sub-plan priority resolution

When multiple engines are registered for the same data affinity, the FQP selects the highest-priority available engine (lowest `priority` number in the config). If the highest-priority engine is unavailable or times out, the FQP automatically falls back to the next registered engine for the same affinity.

---

## Physical query generation

The FQP translates sub-plans into backend-specific query formats. This is the only point in the platform where backend-specific syntax is generated. The specific query dialect — SQL, semantic layer query API, OLAP query format, REST/OData, or graph query language — depends entirely on the registered backend type.

### SQL warehouse backend example

**Sub-plan (LQP fragment):**
```json
{
  "metrics": ["portfolio_return"],
  "dimensions": ["portfolio"],
  "time": { "period": "quarter_to_date", "as_of_date": "2026-05-14" },
  "filters": [
    { "predicate": "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC')" }
  ]
}
```

**Generated SQL (internal, never exposed to AI or user):**
```sql
SELECT
  p.portfolio_id,
  p.portfolio_name,
  SUM(pd.market_value * pd.daily_return) / SUM(pd.market_value) AS portfolio_return
FROM fact_portfolio_daily pd
JOIN dim_portfolio p ON pd.portfolio_id = p.portfolio_id
WHERE pd.price_date >= DATE_TRUNC('quarter', CURRENT_DATE)
  AND pd.price_date <= '2026-05-14'
  AND pd.portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC')
GROUP BY p.portfolio_id, p.portfolio_name
ORDER BY p.portfolio_name ASC
```

### Semantic layer backend example

**Sub-plan (LQP fragment):**
```json
{
  "metrics": ["var_95"],
  "dimensions": ["portfolio"],
  "time": { "period": "today", "as_of_date": "2026-05-14" }
}
```

**Generated semantic layer query (illustrative):**
```json
{
  "metrics": [{ "name": "var_95" }],
  "group_by": [{ "name": "Dimension('portfolio__portfolio_id')" }],
  "where": [{ "sql": "{{ Dimension('portfolio__portfolio_id') }} IN ('GLOB_EQ_OPP', 'UK_CORE_INC')" }],
  "limit": 1000
}
```

### OLAP backend example

**Sub-plan (LQP fragment):**
```json
{
  "metrics": ["aum"],
  "dimensions": ["portfolio", "asset_class"],
  "time": { "period": "quarter_to_date" }
}
```

**Generated OLAP query (illustrative):**
```json
{
  "measures": ["Portfolios.aum"],
  "dimensions": ["Portfolios.portfolioId", "Portfolios.portfolioName", "Securities.assetClass"],
  "timeDimensions": [{
    "dimension": "PortfolioDaily.priceDate",
    "dateRange": "this quarter"
  }],
  "filters": [
    {
      "member": "Portfolios.portfolioId",
      "operator": "equals",
      "values": ["GLOB_EQ_OPP", "UK_CORE_INC"]
    }
  ]
}
```

---

## Result assembly

The FQP assembles sub-results from multiple engines into a unified result set:

1. **Join key identification** — the shared dimensions across sub-plans (e.g. `portfolio_id`, `date`)
2. **In-memory join** — sub-results are joined in the FQP result assembler by shared keys. Physical joins across engines do not occur at the engine level.
3. **Missing value handling** — if a sub-result has no row for a shared key that exists in another sub-result, the missing metric values are represented as null with a provenance marker in the lineage record.
4. **Column mask application** — column masks declared in the Role-Aware Projection are applied to the assembled result before it leaves the FQP.
5. **Result validation** — assembled result is validated against the LQP specification (correct columns, expected cardinality range, data type conformance).

---

## Caching and materialisation

### Result cache

The FQP maintains a result cache keyed by the LQP signature (a deterministic hash of the metric set, dimensions, filters, time expression, and entitlement hash).

| Cache behaviour | Specification |
|----------------|--------------|
| Cache key | SHA-256 of (metric IDs + versions, dimension IDs, filter predicates, time expression, entitlement hash, tenant ID) |
| Cache TTL | Configurable per `data.refresh_cadence` in the metric definition. Default: `3600` seconds. |
| Cache invalidation | On metric definition version change; on execution engine data refresh signal (if the engine emits one); on explicit cache clear via Admin API |
| Cache scope | Per-tenant. Results from one tenant are never served to another. |
| Cache storage | Platform-managed result cache. Results over 10MB bypass the cache and are streamed directly. |
| Cache hit disclosure | Cache hits are disclosed in the lineage record and (optionally) to the user as a *"Result from cache (data as of [timestamp])"* indicator. |

### Materialised views

For high-frequency queries that consistently resolve to the same sub-plans, the FQP supports **materialised view registration** via the Admin API:

```json
{
  "materialised_view": {
    "id":            "portfolio_qtd_summary",
    "description":   "Pre-materialised portfolio QTD return and tracking error summary",
    "lqp_template":  { ... },
    "refresh_schedule": "0 6 * * *",
    "engines":       ["snowflake-primary"],
    "cost_offset":   -800
  }
}
```

Materialised views reduce the cost unit estimate for matching sub-plans, allowing queries that would otherwise trigger a cost circuit breaker to execute against the pre-materialised result.

---

## Adaptive planning

The FQP adapts routing decisions based on observed execution performance:

| Adaptive behaviour | Description |
|-------------------|-------------|
| Engine latency tracking | The FQP tracks p50/p95 latency per engine per data affinity over a rolling 1-hour window |
| Automatic fallback | If an engine's p95 latency exceeds twice its baseline, the FQP automatically routes to the next available engine for new queries |
| Cost estimate calibration | The FQP updates cost unit estimates based on observed execution cost data from completed queries |
| Partial result handling | If a sub-plan engine returns a partial result (e.g. timeout with partial rows), the FQP logs the partial result in the lineage record and surfaces a *"Result may be incomplete — [engine] timed out"* warning to the user |

---

## FQP execution record (in lineage)

The FQP writes a complete execution record to the lineage store for every query:

```json
{
  "fqp_execution_id": "fqp_exec_20260514_093247",
  "lqp_id":           "lqp_20260514_093247_a1b2c3",
  "cache_hit":        false,
  "sub_plans": [
    {
      "id":             "sp_a",
      "engine_id":      "snowflake-primary",
      "metrics":        ["portfolio_return"],
      "status":         "success",
      "latency_ms":     1240,
      "rows_returned":  14,
      "cost_units":     320
    },
    {
      "id":             "sp_b",
      "engine_id":      "dbt-semantic",
      "metrics":        ["tracking_error"],
      "status":         "success",
      "latency_ms":     890,
      "rows_returned":  14,
      "cost_units":     180
    }
  ],
  "assembly_latency_ms": 45,
  "total_latency_ms":    1285,
  "total_cost_units":    500,
  "result_rows":         14,
  "result_columns":      3,
  "cache_written":       true,
  "cache_ttl_seconds":   3600
}
```
