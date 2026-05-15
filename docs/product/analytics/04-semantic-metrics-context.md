# 04 — Semantic Metrics Context

## Overview

The **Semantic Metrics Context (SMC)** defines the governing catalogue of every analytical concept resolvable on the platform — what can be queried, how metrics are computed, what dimensions are available, how hierarchies are structured, who owns each definition, and what lineage metadata applies. This document describes the metric definition schema and semantic model. The physical store that holds these definitions is the Semantic Data Context Store (DCS), a pre-existing general-purpose registry; see [17-proposed-technical-architecture.md](./17-proposed-technical-architecture.md) for how the SMC is implemented on top of the DCS.

Nothing is queryable that is not registered in the SMR. This is an architectural constraint, not a policy. The Analytical Intent Validator rejects any metric identifier not present in the SMR for the active tenant.

---

## Registry structure

The SMR is composed of five interconnected concept types:

| Concept type | Description |
|-------------|-------------|
| **Metric** | A quantitative measure with a governed formula, aggregation rule, and unit |
| **Dimension** | A categorical or temporal attribute by which metrics can be sliced and filtered |
| **Hierarchy** | An ordered set of dimensions forming a navigable analytical hierarchy (for drilldown) |
| **Measure Group** | A named collection of related metrics grouped for analytical coherence |
| **Domain** | A logical grouping of metrics, dimensions, and hierarchies sharing a common business subject area |

---

## Metric definition schema

Every metric in the SMR conforms to the following schema:

```yaml
metric:
  id:               "portfolio_return"
  version:          "2.1.0"
  label:            "Portfolio Return"
  description:      "Total return of a portfolio over the specified period, net of fees, expressed as a percentage."
  formula:          "(end_market_value - start_market_value + cash_flows) / start_market_value"
  unit:             "percentage"
  aggregation:
    default:        "value_weighted_average"
    allowed:        ["value_weighted_average", "equal_weighted_average", "sum"]
    granularity:    ["daily", "monthly", "quarterly", "annual", "since_inception"]
  dimensions:
    required:       ["portfolio", "date"]
    optional:       ["asset_class", "currency", "benchmark"]
  data:
    domain:         "portfolio"
    sub_domain:     "performance"
    source_tables:  ["fact_portfolio_daily", "dim_portfolio"]
    refresh_cadence: "daily"
    latency_sla:    "T+1"
  governance:
    owner:          "head_of_performance_analytics"
    steward:        "performance_analytics_team"
    classification: "INTERNAL"
    approved:       true
    approved_by:    "cdo_office"
    approved_at:    "2025-11-15T09:00:00Z"
    effective_from: "2025-11-15"
    deprecated:     false
  lineage:
    upstream_metrics: []
    upstream_sources: ["positions_service", "pricing_service", "cash_flow_service"]
    downstream_metrics: ["active_return", "information_ratio"]
  access:
    roles:          ["portfolio_manager", "risk_officer", "application_admin"]
    public:         false
  display:
    format:         "percentage"
    decimals:       2
    sign_convention: "positive_is_gain"
    benchmark_comparison: true
```

### Metric schema field reference

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique metric identifier within the tenant. Lowercase, underscores. Used in MCP tool call parameters. |
| `version` | Yes | Semantic version. Increment on formula changes (major), aggregation changes (minor), documentation changes (patch). |
| `label` | Yes | Human-readable metric name. Used in UI, narrative synthesis, and chart axis labels. |
| `description` | Yes | Full prose definition. Must be unambiguous — this definition is injected into the AI model context. |
| `formula` | Yes | Business-logic formula expressed in the platform's formula language (see below). Does not reference physical table columns directly — references other SMR metrics or canonical data source identifiers. |
| `unit` | Yes | Value unit. Accepted: `percentage`, `currency`, `basis_points`, `ratio`, `count`, `years`, `days`, `custom`. |
| `aggregation.default` | Yes | Default aggregation rule when the metric is rolled up across a dimension. |
| `aggregation.allowed` | Yes | All permitted aggregation rules for this metric. Requests using non-allowed rules are rejected at intent validation. |
| `aggregation.granularity` | Yes | Time granularities at which this metric is calculable. Requests at unsupported granularities are rejected. |
| `dimensions.required` | Yes | Dimensions that must be present in any query using this metric. Missing required dimensions cause a validation error. |
| `dimensions.optional` | No | Dimensions that may optionally be applied. |
| `data.domain` | Yes | The logical data domain this metric belongs to. Must match a domain registered in the SMR. |
| `data.refresh_cadence` | Yes | How frequently the underlying data is updated. Displayed in the lineage inspector and narrative synthesis. |
| `governance.owner` | Yes | Identifier of the metric owner. Must be a registered owner in the platform. |
| `governance.classification` | Yes | Data classification level. Used by the governance classification gate. |
| `governance.approved` | Yes | Whether this metric has been approved and is resolvable. Unapproved metrics are not returned by SMR queries. |
| `lineage.upstream_metrics` | No | Other SMR metrics this metric is derived from. Used for lineage graph construction. |
| `lineage.downstream_metrics` | No | SMR metrics that depend on this metric. Used for impact analysis when metric definitions change. |
| `access.roles` | Yes | Role IDs from the entitlement config that may query this metric. |

---

## Dimension definition schema

```yaml
dimension:
  id:          "asset_class"
  version:     "1.0.0"
  label:       "Asset Class"
  description: "Broad classification of securities by asset type."
  type:        "categorical"
  values:
    source:    "reference_data"
    endpoint:  "dim_asset_class"
    cacheable: true
  cardinality: "low"
  governance:
    owner:          "data_management_office"
    classification: "PUBLIC"
    approved:       true
  display:
    sort_order: "label_ascending"
    default_filter: null
```

| Field | Description |
|-------|-------------|
| `type` | `categorical`, `temporal`, `numeric_range`, `geographic`, `hierarchical_node` |
| `cardinality` | `low` (< 20 values), `medium` (20–500), `high` (500+), `unbounded`. Used by the FQP for result size estimation. |

---

## Hierarchy definition schema

```yaml
hierarchy:
  id:          "asset_class_hierarchy"
  version:     "1.0.0"
  label:       "Asset Class Hierarchy"
  description: "Navigable hierarchy from broad asset class through sub-asset class to security type."
  levels:
    - id:    "asset_class"
      label: "Asset Class"
      depth: 1
    - id:    "sub_asset_class"
      label: "Sub-Asset Class"
      depth: 2
    - id:    "security_type"
      label: "Security Type"
      depth: 3
  drilldown:
    enabled:   true
    max_depth: 3
  governance:
    owner:     "data_management_office"
    approved:  true
```

---

## Measure Group definition schema

```yaml
measure_group:
  id:          "performance_metrics"
  label:       "Performance Metrics"
  description: "Standard portfolio performance measures for client reporting and investment committee use."
  metrics:
    - "portfolio_return"
    - "benchmark_return"
    - "active_return"
    - "tracking_error"
    - "information_ratio"
    - "sharpe_ratio"
  default_dimensions:
    - "portfolio"
    - "date"
  governance:
    owner:    "head_of_performance_analytics"
    approved: true
```

---

## Formula language

The SMR formula language is used to define metric computation logic. It references:
- Other SMR metrics (by `id`)
- Canonical data source identifiers (abstract references resolved by the FQP to physical columns)
- Standard mathematical and financial functions from the platform's function library

**Formula language examples:**

```
# Simple ratio metric
active_return = portfolio_return - benchmark_return

# Information Ratio
information_ratio = active_return / tracking_error

# Weighted average with null protection
weighted_avg_duration = SAFE_DIVIDE(
  SUM(position_market_value * security_modified_duration),
  SUM(position_market_value)
)

# Conditional metric
issuer_concentration = SAFE_DIVIDE(
  SUM(position_market_value, FILTER(issuer = {{dim.issuer}})),
  SUM(position_market_value)
)

# Time-windowed metric
rolling_90d_return = CUMULATIVE_RETURN(daily_return, WINDOW(90, 'days'))
```

**Built-in function library (selected):**

| Function | Description |
|----------|-------------|
| `SUM(metric, [filter])` | Aggregated sum with optional dimensional filter |
| `SAFE_DIVIDE(numerator, denominator)` | Division returning null (not error) when denominator is zero |
| `CUMULATIVE_RETURN(period_return, window)` | Compounded return over a time window |
| `PERCENTILE(metric, pct)` | Percentile aggregation |
| `CONDITIONAL(condition, true_val, false_val)` | Conditional value selection |
| `BENCHMARK_RELATIVE(metric, benchmark_id)` | Metric expressed relative to a benchmark dimension |
| `WINDOW(n, unit)` | Defines a sliding time window |
| `DATE_TRUNC(dimension, granularity)` | Truncates a temporal dimension to a specified granularity |

---

## Registry governance workflow

```
Draft → Proposed → In Review → Approved (Active) → Deprecated → Retired
```

| Transition | Trigger | Effect |
|-----------|---------|--------|
| Draft → Proposed | Metric owner submits a new definition | Visible in admin UI; not resolvable |
| Proposed → In Review | Application Admin opens for review | Downstream impact analysis runs automatically |
| In Review → Approved | Application Admin approves | Metric becomes resolvable from next refresh cycle |
| Approved → Deprecated | Owner or Admin marks deprecated | Metric resolves with a deprecation warning; removed from SMR browsing defaults |
| Deprecated → Retired | Admin retires after deprecation period | Metric no longer resolvable; lineage records preserved |

### Impact analysis on metric change

When a metric definition is proposed for change, the platform automatically runs an impact analysis:

1. Identify all downstream metrics referencing this metric via `lineage.upstream_metrics`
2. Identify all saved analytical sessions and scheduled queries using this metric
3. Identify all dashboards and visualisations embedding results derived from this metric
4. Produce an impact report for the Application Admin to review before approving the change

Approval of a change that has downstream impacts requires the Application Admin to acknowledge the impact report. This acknowledgement is recorded in the lineage store.

---

## SMR API

The SMR is accessible via the Platform Admin API and via the MCP Capability Layer (for AI agents):

```
GET  /v1/smr/metrics              — list all approved metrics
GET  /v1/smr/metrics/{id}         — get metric definition by ID
GET  /v1/smr/metrics/{id}/lineage — get full lineage graph for metric
GET  /v1/smr/dimensions           — list all approved dimensions
GET  /v1/smr/hierarchies          — list all approved hierarchies
GET  /v1/smr/measure-groups       — list all measure groups
POST /v1/smr/metrics              — propose a new metric definition
PUT  /v1/smr/metrics/{id}         — propose a change to an existing metric
POST /v1/smr/metrics/{id}/approve — approve a proposed metric (Application Admin only)
```

---

## Registry browsing in the UI

Authenticated users (within their entitlement scope) can browse the SMR from the analytics interface:

- Searchable metric catalogue with full definitions, formulas, owners, and lineage
- Dimension reference with value previews
- Hierarchy visualisation showing navigable levels
- Measure group collections for common analytical workflows
- Metric change history and version comparison

Users may only browse metrics within their `access.roles` entitlement. Metrics they are not entitled to are not visible in the browser.
