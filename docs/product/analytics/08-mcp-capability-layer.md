# 08 — MCP Capability Layer

## Overview

The **MCP Capability Layer** exposes the AI Analytics Platform's governed analytical operations to AI orchestrators via an MCP-compatible interface. It is the primary integration point for AI agents — including the platform's own Semantic Intent Layer — that need to compose analytical queries programmatically.

The MCP Capability Layer does not expose raw query interfaces. Every capability is a bounded, named analytical operation that enforces the same governance pipeline as natural-language queries. AI agents interact with analytical capabilities, not with databases.

---

## Capability model

Each MCP capability is a named analytical operation with:
- A typed input schema (parameters the AI agent provides)
- A governed execution path (routes through Analytical Intent Validator, projection layer, governance, FQP)
- A typed output contract (the result schema the agent can expect)
- A semantic description (the context injected into the AI model when this capability is available)

---

## Core analytical capabilities

### `analyse_metric`

Execute a governed analytical query against one or more registered metrics.

```json
{
  "name":        "analyse_metric",
  "description": "Execute a governed analytical query against one or more registered metrics from the Semantic Metrics Registry. Use this to answer quantitative questions about portfolio performance, risk, or other financial metrics. Always specify the metric IDs you need — do not attempt to construct SQL or use unregistered identifiers.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "metrics": {
        "type":        "array",
        "items":       { "type": "string" },
        "description": "Array of metric IDs from the Semantic Metrics Registry (e.g. ['portfolio_return', 'tracking_error'])"
      },
      "dimensions": {
        "type":        "array",
        "items":       { "type": "string" },
        "description": "Dimension IDs to slice by (e.g. ['portfolio', 'asset_class'])"
      },
      "time_period": {
        "type":        "string",
        "description": "Time expression. Accepted: 'quarter_to_date', 'year_to_date', 'last_N_months', 'since_inception', 'today', or 'RANGE:YYYY-MM-DD:YYYY-MM-DD'"
      },
      "filters": {
        "type":        "array",
        "items": {
          "type":      "object",
          "properties": {
            "dimension": { "type": "string" },
            "operator":  { "type": "string", "enum": ["eq", "neq", "gt", "lt", "gte", "lte", "in", "not_in"] },
            "value":     {}
          }
        }
      },
      "order_by": {
        "type":        "string",
        "description": "metric_id ASC|DESC"
      },
      "limit": {
        "type":        "integer",
        "description": "Maximum rows to return. Default: 1000."
      }
    },
    "required": ["metrics", "time_period"]
  }
}
```

**Example invocation:**
```json
{
  "metrics":     ["portfolio_return", "tracking_error"],
  "dimensions":  ["portfolio"],
  "time_period": "quarter_to_date",
  "filters": [
    { "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }
  ],
  "order_by":    "tracking_error DESC"
}
```

---

### `compare_portfolios`

Compare a set of metrics across two or more portfolios, optionally against a benchmark.

```json
{
  "name":        "compare_portfolios",
  "description": "Compare governed metrics across multiple portfolios. Optionally includes benchmark comparison. Returns a structured comparison result suitable for tabular or chart rendering.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "portfolio_ids": {
        "type":  "array",
        "items": { "type": "string" },
        "description": "Portfolio identifiers to compare"
      },
      "metrics": {
        "type":  "array",
        "items": { "type": "string" }
      },
      "time_period": { "type": "string" },
      "benchmark_id": {
        "type":        "string",
        "description": "Benchmark ID to compare against (optional)"
      }
    },
    "required": ["portfolio_ids", "metrics", "time_period"]
  }
}
```

---

### `issuer_concentration`

Calculate issuer concentration metrics across specified portfolios.

```json
{
  "name":        "issuer_concentration",
  "description": "Calculate issuer concentration risk metrics. Returns issuer-level exposure, concentration percentage of total AUM, and limit utilisation where limits are defined. Use for regulatory concentration checks and investment committee reporting.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "portfolio_ids":      { "type": "array", "items": { "type": "string" } },
      "asset_class_filter": { "type": "string", "description": "Optional asset class filter" },
      "threshold_pct":      { "type": "number",  "description": "Highlight issuers above this concentration percentage (0–1)" },
      "as_of_date":         { "type": "string",  "format": "date" }
    },
    "required": ["portfolio_ids", "as_of_date"]
  }
}
```

---

### `risk_breakdown`

Decompose risk metrics into contributing factors.

```json
{
  "name":        "risk_breakdown",
  "description": "Decompose a risk metric (VaR, tracking error, beta) into factor contributions. Returns a structured attribution of the total risk figure to its contributing dimensions. Use for risk reporting and limit breach investigation.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "portfolio_id":  { "type": "string" },
      "risk_metric":   { "type": "string", "description": "Risk metric ID (e.g. 'var_95', 'tracking_error')" },
      "attribution_by": {
        "type":        "string",
        "enum":        ["asset_class", "factor", "issuer", "geography", "currency"],
        "description": "Dimension to attribute risk contribution to"
      },
      "as_of_date": { "type": "string", "format": "date" }
    },
    "required": ["portfolio_id", "risk_metric", "attribution_by", "as_of_date"]
  }
}
```

---

### `performance_attribution`

Brinson-Hood-Beebower (or Brinson-Fachler) performance attribution decomposition.

```json
{
  "name":        "performance_attribution",
  "description": "Run a governed performance attribution decomposition (BHB or BF model) for a portfolio versus its benchmark. Returns allocation effect, selection effect, and interaction effect by dimension. Use for investment committee reporting and mandate compliance.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "portfolio_id":    { "type": "string" },
      "benchmark_id":    { "type": "string" },
      "attribution_by":  { "type": "string", "enum": ["asset_class", "geography", "sector", "currency"] },
      "time_period":     { "type": "string" },
      "model":           { "type": "string", "enum": ["bhb", "bf"], "description": "Attribution model. Default: bhb" }
    },
    "required": ["portfolio_id", "benchmark_id", "attribution_by", "time_period"]
  }
}
```

---

### `regulatory_metric`

Query a regulatory compliance metric.

```json
{
  "name":        "regulatory_metric",
  "description": "Query a regulatory compliance metric (LCR, NSFR, leverage ratio, etc.). Requires the regulatory_reporting feature flag and appropriate role. Returns the metric value, regulatory minimum, and compliance status.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "metric_id":   { "type": "string", "description": "Regulatory metric ID from the SMR" },
      "entity_ids":  { "type": "array", "items": { "type": "string" } },
      "as_of_date":  { "type": "string", "format": "date" },
      "trend_days":  { "type": "integer", "description": "Number of trailing days to include as trend. 0 for current only." }
    },
    "required": ["metric_id", "entity_ids", "as_of_date"]
  }
}
```

---

### `list_metrics`

Retrieve the list of metrics available to the current user from the SMR.

```json
{
  "name":        "list_metrics",
  "description": "List all metrics in the Semantic Metrics Registry available to the current user based on their role. Use this to understand what analytical concepts are resolvable before attempting a query. Returns metric IDs, labels, descriptions, and required dimensions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "domain_filter":    { "type": "string", "description": "Optional: filter to a specific data domain" },
      "measure_group":    { "type": "string", "description": "Optional: filter to a named measure group" },
      "include_deprecated": { "type": "boolean", "default": false }
    }
  }
}
```

---

### `drilldown`

Navigate into a dimension hierarchy from a previous result.

```json
{
  "name":        "drilldown",
  "description": "Navigate into an analytical hierarchy from a prior result. Takes the result set ID and a dimension to drill into, and returns a new result at the next hierarchy level with the parent-level filters preserved.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "result_id":       { "type": "string", "description": "The result set ID from a prior analyse_metric call" },
      "drilldown_into":  { "type": "string", "description": "Hierarchy ID to traverse into" },
      "selected_value":  { "description": "The dimension value to anchor the drilldown to (e.g. 'EQUITY')" }
    },
    "required": ["result_id", "drilldown_into"]
  }
}
```

---

## Capability manifest

The MCP Capability Layer exposes a capability manifest that AI orchestrators retrieve to understand what operations are available for the authenticated user and tenant:

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
    "role":            "portfolio_manager",
    "accessible_metrics": 42,
    "accessible_dimensions": 12
  }
}
```

---

## Capability invocation governance

Every MCP capability invocation passes through the full governance pipeline:

```
Capability invocation
→ Input schema validation
→ Capability availability check (feature flags + role)
→ Analytical intent construction from capability inputs
→ Analytical Intent Validator (SMR resolution + role-aware projection)
→ Semantic Execution Governance
→ Federated Query Planner
→ Result assembly
→ Lineage record writing
→ Result returned to AI agent
```

AI agents receive the same lineage-backed, role-aware, governance-validated results as human users. There is no privileged API path.

---

## MCP endpoint

The MCP Capability Layer is exposed at:

```
POST https://api.analytics-platform.io/v1/mcp
     Authorization: Bearer {user_jwt}
     Content-Type: application/json
```

Following the MCP Streamable HTTP transport specification. Tool call results are returned as MCP `tool_result` content blocks with the result set as structured JSON.
