# 08 — MCP Capability Layer

## Overview

The **MCP Capability Layer** exposes the platform's governed analytical operations to AI orchestrators via an MCP-compatible interface. Each capability is a bounded, named operation enforcing the same governance pipeline as natural-language queries — AI agents interact with capabilities, not databases.

Each capability has a typed input schema, a governed execution path (Analytical Intent Validator → projection → governance → FQP), a typed output contract, and a semantic description injected into the AI model's context.

---

## Core analytical capabilities

### `analyse_metric`

Execute a governed query against one or more registered metrics.

| Parameter | Required | Type | Notes |
|-----------|----------|------|-------|
| `metrics` | Yes | string[] | SMR metric IDs |
| `dimensions` | No | string[] | Dimension IDs to slice by |
| `time_period` | Yes | string | `quarter_to_date`, `year_to_date`, `last_N_months`, `since_inception`, `today`, `RANGE:YYYY-MM-DD:YYYY-MM-DD` |
| `filters` | No | array | `{dimension, operator, value}` — operators: `eq neq gt lt gte lte in not_in` |
| `order_by` | No | string | `metric_id ASC\|DESC` |
| `limit` | No | integer | Default: 1000 |

```json
{
  "metrics":     ["portfolio_return", "tracking_error"],
  "dimensions":  ["portfolio"],
  "time_period": "quarter_to_date",
  "filters": [{ "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }],
  "order_by":    "tracking_error DESC"
}
```

---

### `compare_portfolios`

Compare metrics across two or more portfolios, optionally against a benchmark.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `portfolio_ids` | Yes | Array of portfolio IDs |
| `metrics` | Yes | SMR metric IDs |
| `time_period` | Yes | Same format as `analyse_metric` |
| `benchmark_id` | No | Optional benchmark comparison |

---

### `issuer_concentration`

Issuer-level exposure, concentration % of AUM, and limit utilisation where limits are defined.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `portfolio_ids` | Yes | |
| `as_of_date` | Yes | `date` |
| `asset_class_filter` | No | |
| `threshold_pct` | No | Highlight issuers above this concentration (0–1) |

---

### `risk_breakdown`

Decompose a risk metric (VaR, tracking error, beta) into factor contributions by dimension.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `portfolio_id` | Yes | |
| `risk_metric` | Yes | e.g. `var_95`, `tracking_error` |
| `attribution_by` | Yes | `asset_class \| factor \| issuer \| geography \| currency` |
| `as_of_date` | Yes | `date` |

---

### `performance_attribution`

BHB or Brinson-Fachler attribution decomposition — returns allocation, selection, and interaction effects.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `portfolio_id` | Yes | |
| `benchmark_id` | Yes | |
| `attribution_by` | Yes | `asset_class \| geography \| sector \| currency` |
| `time_period` | Yes | |
| `model` | No | `bhb` (default) or `bf` |

---

### `regulatory_metric`

Query a regulatory compliance metric (LCR, NSFR, leverage ratio). Requires `regulatory_reporting` feature flag and appropriate role. Returns metric value, regulatory minimum, and compliance status.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `metric_id` | Yes | |
| `entity_ids` | Yes | |
| `as_of_date` | Yes | `date` |
| `trend_days` | No | Trailing days as trend; `0` for current only |

---

### `list_metrics`

List all SMR metrics available to the current user's role, with IDs, labels, descriptions, and required dimensions.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `domain_filter` | No | Filter by data domain |
| `measure_group` | No | Filter by measure group |
| `include_deprecated` | No | Default: `false` |

---

### `drilldown`

Navigate into a dimension hierarchy from a prior result; parent-level filters are preserved.

| Parameter | Required | Notes |
|-----------|----------|-------|
| `result_id` | Yes | Result set ID from a prior `analyse_metric` call |
| `drilldown_into` | Yes | Hierarchy ID to traverse |
| `selected_value` | No | Dimension value to anchor the drilldown |

---

## Capability negotiation

Capabilities are declared in the MCP manifest. Consumers call `list_capabilities` to discover available tools. Capability availability is gated by feature flags and role entitlements — a capability not enabled by a feature flag or accessible to the user's role appears as `available: false` with a reason.

```json
{
  "manifest_version": "1.0",
  "tenant_id":        "acme-wealth",
  "as_of":            "2026-05-14T09:00:00Z",
  "capabilities": [
    { "name": "analyse_metric",          "available": true,  "reason": null },
    { "name": "compare_portfolios",      "available": true,  "reason": null },
    { "name": "issuer_concentration",    "available": true,  "reason": null },
    { "name": "risk_breakdown",          "available": true,  "reason": null },
    { "name": "performance_attribution", "available": true,  "reason": null },
    { "name": "regulatory_metric",       "available": false, "reason": "regulatory_reporting feature flag disabled" },
    { "name": "list_metrics",            "available": true,  "reason": null },
    { "name": "drilldown",               "available": true,  "reason": null }
  ],
  "entitlement_summary": {
    "role":                  "portfolio_manager",
    "accessible_metrics":    42,
    "accessible_dimensions": 12
  }
}
```

---

## Capability invocation governance

Every invocation passes through: input schema validation → capability availability check (feature flags + role) → Analytical Intent Validator → Semantic Execution Governance → FQP → result assembly → lineage record write. AI agents receive the same governance-validated results as human users. There is no privileged API path.

---

## MCP endpoint

```
POST https://api.analytics-platform.io/v1/mcp
     Authorization: Bearer {user_jwt}
     Content-Type: application/json
```

Following the MCP Streamable HTTP transport specification. Tool call results are returned as MCP `tool_result` content blocks with the result set as structured JSON.
