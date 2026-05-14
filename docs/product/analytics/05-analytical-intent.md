# 05 — Analytical Intent and LQP Generation

## Overview

When a consumer submits an MCP tool call, the parameters it provides — metric IDs, dimension IDs, time period, filters — are the **analytical intent** expressed in structured form. There is no separate query language. The MCP tool call parameter schema is the query format; the platform's role is to validate, project, and compile that intent into an engine-agnostic Logical Query Plan (LQP).

This layer sits between the MCP Capability Layer and the Federated Query Planner:

```
MCP tool call (JSON params)
        │
        ▼
Analytical Intent Validator
  ├── SMR resolution (validate all metric/dimension IDs)
  ├── Role-Aware Projection (filter to entitled scope)
  ├── Semantic validation (required dimensions, aggregation rules)
  └── LQP generation (engine-agnostic DAG)
        │
        ▼
Logical Query Plan → Federated Query Planner
```

The analytical intent format deliberately excludes:
- Physical table or column references
- Backend-specific syntax or functions
- JOIN operations (resolved by the FQP from data affinity declarations)
- Raw query passthrough of any kind

All identifiers — metric IDs, dimension IDs, hierarchy IDs — must resolve against the tenant's active SMR. Unresolvable IDs are rejected before any execution planning begins.

---

## Analytical intent format

The intent is expressed as the JSON parameters of an MCP tool call. The full parameter schemas are defined in [08-mcp-capability-layer.md](./08-mcp-capability-layer.md). The core parameters shared across analytical capabilities are:

| Parameter | Type | Description |
|-----------|------|-------------|
| `metrics` | `string[]` | Metric IDs from the SMR. The platform resolves each to its definition, aggregation rule, required dimensions, and data affinity. |
| `dimensions` | `string[]` | Dimension IDs to slice by. Must be permitted for the requested metrics and within the user's entitlement scope. |
| `time_period` | string | Time expression. Semantic values: `quarter_to_date`, `year_to_date`, `since_inception`, `today`, `last_N_months`, `fiscal_year_YYYY`, `RANGE:YYYY-MM-DD:YYYY-MM-DD`. |
| `filters` | object[] | Dimension or metric predicates: `{ dimension, operator, value }`. Applied at the semantic tier; translated to backend-appropriate filter expressions by the FQP. |
| `order_by` | string | `metric_id ASC\|DESC` |
| `limit` | integer | Maximum result rows. Default: 1000. |
| `compare_to` | object | Optional comparison target: benchmark, peer group, or prior period. |

**Example — the same intent expressed as an MCP tool call and as what it resolves to:**

```json
// MCP tool call input (what the AI produces)
{
  "metrics":     ["portfolio_return", "tracking_error"],
  "dimensions":  ["portfolio", "asset_class"],
  "time_period": "quarter_to_date",
  "filters": [
    { "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }
  ],
  "order_by": "tracking_error DESC"
}
```

```json
// After SMR resolution and role projection — what enters the LQP generator
{
  "resolved_metrics": [
    {
      "id":            "portfolio_return",
      "version":       "2.1.0",
      "aggregation":   "value_weighted_average",
      "data_affinity": "portfolio",
      "required_dims": ["portfolio"]
    },
    {
      "id":            "tracking_error",
      "version":       "1.3.0",
      "aggregation":   "value_weighted_average",
      "data_affinity": "risk_metrics",
      "required_dims": ["portfolio"]
    }
  ],
  "dimensions": [
    { "id": "portfolio",   "entitled": true },
    { "id": "asset_class", "entitled": true }
  ],
  "row_predicates": [
    "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"
  ],
  "filters": [
    { "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }
  ],
  "time": { "type": "period", "period": "quarter_to_date", "as_of_date": "2026-05-14" },
  "order_by": { "field": "tracking_error", "direction": "DESC" }
}
```

---

## Validation stages

The Analytical Intent Validator processes every MCP tool call in five stages before releasing an LQP to the Federated Query Planner:

```
┌─────────────────────────────────────────┐
│  Stage 1: Schema validation              │
│  JSON parameters conform to tool schema  │
│  Required fields present and typed       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Stage 2: SMR resolution                 │
│  Resolve metric IDs → definitions        │
│  Resolve dimension IDs → definitions     │
│  Resolve hierarchy refs → definitions    │
│  Reject unregistered IDs                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Stage 3: Role-Aware Projection          │
│  Filter metric set to entitled scope     │
│  Filter dimension set to entitled scope  │
│  Inject row predicates from role config  │
│  Apply column masks                      │
│  Reject entitlement violations           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Stage 4: Semantic validation            │
│  Required dimensions present per metric  │
│  Aggregation rules compatible            │
│  Time granularity compatible per metric  │
│  Filter predicates reference valid fields│
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Stage 5: LQP generation                 │
│  Produce engine-agnostic DAG             │
│  Assign data affinity hints per metric   │
│  Estimate result cardinality             │
│  Estimate execution cost units           │
└────────────────┬────────────────────────┘
                 │
        Logical Query Plan (LQP)
```

---

## Validation errors

| Error code | Trigger | Consumer-facing message |
|-----------|---------|------------------------|
| `METRIC_NOT_FOUND` | Metric ID not in SMR | "The metric '[id]' is not defined in the analytics registry." |
| `METRIC_NOT_ENTITLED` | Metric in SMR but not in user's role | "You do not have access to the metric '[id]'." |
| `DIMENSION_NOT_FOUND` | Dimension ID not in SMR | "The dimension '[id]' is not defined in the analytics registry." |
| `REQUIRED_DIMENSION_MISSING` | `portfolio_return` queried without `portfolio` | "The metric '[id]' requires the '[dim]' dimension." |
| `INVALID_AGGREGATION` | Aggregation not in metric's `allowed` list | "The aggregation '[agg]' is not supported for metric '[id]'." |
| `UNSUPPORTED_GRANULARITY` | Daily granularity for a monthly-only metric | "The metric '[id]' is only calculable at monthly or lower frequency." |
| `HIERARCHY_NOT_ALLOWED` | Drilldown hierarchy not in tenant config | "Drilldown into '[id]' is not enabled for this application." |
| `SCHEMA_INVALID` | Malformed tool call parameters | "Analytical query could not be parsed — please rephrase your question." |

All validation errors are returned as structured MCP error responses and written to the audit trail with a `result_id`.

---

## Logical Query Plan (LQP) schema

The LQP is the output of the Analytical Intent Validator and the input to the Federated Query Planner. It is an engine-agnostic JSON representation of the validated, projected analytical request:

```json
{
  "lqp_id":      "lqp_20260514_093247_a1b2c3",
  "tenant_id":   "acme-wealth",
  "version":     "1.0",
  "created_at":  "2026-05-14T09:32:47Z",
  "source_tool": "analyse_metric",
  "metrics": [
    {
      "id":          "portfolio_return",
      "version":     "2.1.0",
      "aggregation": "value_weighted_average",
      "period":      "quarter_to_date"
    },
    {
      "id":          "tracking_error",
      "version":     "1.3.0",
      "aggregation": "value_weighted_average",
      "period":      "quarter_to_date"
    }
  ],
  "dimensions": [
    { "id": "portfolio",   "required": true  },
    { "id": "asset_class", "required": false }
  ],
  "filters": [
    {
      "type":      "row_predicate",
      "source":    "role_projection",
      "predicate": "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"
    },
    {
      "type":      "user_filter",
      "dimension": "asset_class",
      "operator":  "eq",
      "value":     "EQUITY"
    }
  ],
  "time": {
    "type":       "period",
    "period":     "quarter_to_date",
    "as_of_date": "2026-05-14"
  },
  "data_affinity": {
    "portfolio_return": "portfolio",
    "tracking_error":   "risk_metrics"
  },
  "cost_estimate": {
    "units":      450,
    "confidence": "medium"
  },
  "cardinality_estimate": {
    "rows":    14,
    "columns": 3
  }
}
```

The LQP is stored in the Analytical Lineage Store as part of the full lineage record for every query, linking the original tool call parameters to the physical execution result.
