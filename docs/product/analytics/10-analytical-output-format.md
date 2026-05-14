# 10 — Analytical Output Format

## Overview

The AI Analytics Platform is headless. It produces no rendered output. Every successful analytical request returns a structured MCP tool response containing three output elements:

| Element | Field | Always present? | Description |
|---------|-------|----------------|-------------|
| Display specification | `display_spec` | Yes | A Semantic Charting Language (SCL) JSON object — either a chart specification or a table specification. Consumers render from this. |
| Narrative | `narrative` | When enabled | Governed prose produced by the Narrative Synthesis Engine, anchored to result values |
| Lineage reference | `result_id` + `lineage_url` | Yes | A unique result identifier and the URL of the full lineage record |

The platform determines the `display_spec` shape — chart or table, which chart contract, which colour assignments, which number formats — from the result schema and the matching Visualisation Ontology contract. Consumers receive this specification and render it using whichever library or component they choose.

---

## Chart contract selection rules

The Visualisation Ontology evaluates each assembled result in priority order to determine which chart contract to apply to the `display_spec`. **The first matching rule wins.** If no rule matches, the result is returned as a `type: "table"` specification.

| Priority | Trigger | `display_spec` produced |
|----------|---------|------------------------|
| 1 | Intent pattern is `ATTRIBUTION` and result schema matches waterfall contract | Chart — waterfall (attribution decomposition) |
| 2 | Intent pattern is `THRESHOLD` and result schema matches heatmap contract | Chart — heatmap (threshold matrix) |
| 3 | Intent pattern is `COMPOSITION` or `DISTRIBUTION` and result schema matches treemap contract | Chart — treemap (part-to-whole) |
| 4 | Intent pattern is `RELATIONSHIP` and exactly 2 numeric metrics present | Chart — scatter (risk-return or metric correlation) |
| 5 | Intent pattern is `TREND` and a temporal dimension is present | Chart — line (time series) |
| 6 | Intent pattern is `COMPARISON` and cardinality ≤ 50 | Chart — bar (multi-series comparison) |
| 7 | No chart contract matches | Table — `type: "table"` SCL specification |

The tenant's `visualisation.allowedChartTypes` config constrains which contracts are eligible. A contract not in the allowed list is skipped, and the next matching rule is evaluated.

---

## SCL display_spec — chart

When a chart contract matches, the `display_spec` field contains an SCL chart specification. The SCL contract includes:

- `type: "chart"` — discriminator for consumers
- `mark` — the chart geometry (`bar`, `line`, `area`, `scatter`, `heatmap`, `treemap`, `waterfall`, `gauge`, `sparkline`)
- `data.values` — the result rows, formatted per the SMR `display.format` and tenant `numberFormat` config
- `encoding` — axis, colour, and size encodings derived from the result schema and chart contract
- `colorScheme` — the tenant's configured `colorPalette`, resolved to a colour array
- `formatHints` — per-field number format and unit metadata from the SMR, for consumer rendering

Example (abbreviated):

```json
{
  "type":   "chart",
  "mark":   "bar",
  "data":   { "values": [ { "portfolio": "Global Equity", "tracking_error": 0.042 }, ... ] },
  "encoding": {
    "x": { "field": "portfolio",      "type": "nominal",      "title": "Portfolio"        },
    "y": { "field": "tracking_error", "type": "quantitative", "title": "Tracking Error"   }
  },
  "colorScheme": ["#003f5c", "#58508d", "#bc5090"],
  "formatHints": {
    "tracking_error": { "format": ".2%", "unit": "%" }
  }
}
```

The technical specification defines the exact SCL schema and the implementation library used to render it.

---

## SCL display_spec — table

When no chart contract matches, the `display_spec` field contains an SCL table specification. The `type: "table"` extension uses the same JSON envelope as chart specs and provides all the information a consumer needs to render a governed data grid:

```json
{
  "type": "table",
  "columns": [
    { "field": "portfolio",      "label": "Portfolio",      "type": "string"                              },
    { "field": "tracking_error", "label": "Tracking Error", "type": "number", "format": ".2%"            },
    { "field": "limit",          "label": "Limit",          "type": "number", "format": ".2%"            },
    { "field": "breached",       "label": "Breached",       "type": "boolean"                             }
  ],
  "data": [ ... ],
  "thresholds": [
    { "field": "tracking_error", "operator": "gt", "reference": "limit", "severity": "warning" }
  ]
}
```

The `thresholds` array carries registered threshold rules from the SMR. Consumers should apply these visually (e.g., highlight breached cells) when rendering. Column labels come from SMR metric and dimension `display.label` values — never from physical field names.

---

## Narrative synthesis

When `features.narrativeSynthesis` is enabled for the tenant and the result meets the synthesis threshold, the MCP response includes a `narrative` field containing governed prose:

```json
{
  "narrative": {
    "lead":     "Three of 14 equity portfolios are above their tracking error limit this quarter.",
    "detail":   "Global Equity (4.2% vs 3.5% limit), EM Growth (5.1% vs 4.0% limit), and Asia Pacific (3.8% vs 3.5% limit) are the breaching portfolios. The remaining 11 portfolios are within mandate.",
    "asOf":     "14 May 2026, Q2 2026 QTD",
    "anchoredTo": "res_20260514_093247_a1b2c3"
  }
}
```

### Narrative synthesis constraints

| Constraint | Enforcement |
|-----------|-------------|
| No metric values not in the result | Post-generation validation against result set — regenerated if violated |
| No figures from model training data | Prompt-level constraint: values may only come from the provided result set |
| No hedging language about data accuracy | Narrative anchored to SMR data currency metadata |
| No investment recommendations | Prompt-level constraint — describe findings, never recommend actions |
| Unit-correct formatting | Numbers formatted using SMR `display.format` before injection into narrative prompt |

`narrative.anchoredTo` carries the `result_id` of the execution result the narrative was derived from, providing a verifiable link between prose and governed data.

---

## Full MCP response structure

A complete MCP tool response:

```json
{
  "result_id":   "res_20260514_093247_a1b2c3",
  "lineage_url": "https://api.analytics-platform.io/v1/lineage/res_20260514_093247_a1b2c3",
  "display_spec": {
    "type": "chart",
    "mark": "bar",
    ...
  },
  "narrative": {
    "lead":   "...",
    "detail": "...",
    "asOf":   "14 May 2026",
    "anchoredTo": "res_20260514_093247_a1b2c3"
  },
  "meta": {
    "latencyMs":    1285,
    "cacheHit":     false,
    "rowCount":     14,
    "backendsUsed": ["primary-warehouse", "semantic-layer"],
    "costUnits":    500
  }
}
```

`meta` is provided for consumer-side observability. Consumers may surface latency and cache status in their UI or pass them to telemetry.

---

## Streaming behaviour

| Output element | Streaming behaviour |
|---------------|-------------------|
| `narrative` | Streams token-by-token; consumers may render incrementally |
| `display_spec` | Delivered as a complete JSON object after FQP result assembly — not streamed |
| `result_id` + `lineage_url` | Delivered with `display_spec` — not streamed |
| `meta` | Delivered as a complete object — not streamed |
| Governance-blocked errors | Returned immediately before any backend execution |

While the FQP is executing, the platform streams structured progress events that consumers may surface:

```json
{ "event": "intent_resolved",      "metrics": ["tracking_error", "tracking_error_limit"] }
{ "event": "entitlements_applied", "rowsFiltered": 3 }
{ "event": "plan_compiled",        "backends": ["primary-warehouse", "semantic-layer"] }
{ "event": "executing",            "elapsedMs": 890 }
```

---

## Error responses

When a request cannot be completed, the MCP response returns a structured error object rather than a `display_spec`:

| Error condition | `error.code` | `error.message` |
|----------------|-------------|----------------|
| Governance blocked — cost exceeded | `GOVERNANCE_COST_EXCEEDED` | "Estimated cost N units exceeds limit M. Narrow the query scope." |
| Governance blocked — classification | `GOVERNANCE_CLASSIFICATION_BLOCKED` | "Query touches restricted data classification [label]." |
| Out-of-scope query | `OUT_OF_SCOPE` | Tenant `scope.outOfScopeMessage` value |
| Unresolvable metric | `METRIC_NOT_FOUND` | "Metric [id] is not registered in this tenant's SMR." |
| Entitlement denied | `ENTITLEMENT_DENIED` | "Your role does not include access to [metric/dimension]." |
| Backend timeout | `EXECUTION_TIMEOUT` | "Query exceeded the [N]s timeout. Reduce scope or increase timeout config." |
| No matching chart contract | `NO_CHART_CONTRACT` | Returned with a `type: "table"` display_spec — not an error; this is a normal fallback |

All error responses include a `result_id` and `lineage_url` so that blocked and failed requests appear in the audit trail.
