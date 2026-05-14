# 10 — Content Rendering

## Overview

The content rendering layer receives the assembled analytical result, applies the Visualisation Ontology, and produces rendered output — charts, tables, and narrative prose — for display in the `<ai-analytics>` web component. Every output type has a governed rendering path; no output is generated without a registered contract or rule.

---

## Rendering decision rules

The rendering engine evaluates each analytical result in priority order. **The first matching rule wins.**

| Priority | Trigger | Rendered as |
|----------|---------|------------|
| 1 | Custom host renderer registered and ontology selects it | **Custom host renderer** — host-provided ES module |
| 2 | Intent pattern is `ATTRIBUTION` and waterfall contract matches | **Waterfall chart** — attribution decomposition |
| 3 | Intent pattern is `THRESHOLD` and heatmap contract matches | **Heatmap** — threshold matrix |
| 4 | Intent pattern is `COMPOSITION` or `DISTRIBUTION` and treemap matches | **Treemap** — part-to-whole |
| 5 | Intent pattern is `RELATIONSHIP` and exactly 2 numeric metrics | **Scatter plot** — risk-return or metric correlation |
| 6 | Intent pattern is `TREND` and temporal dimension present | **Line chart** — time series |
| 7 | Intent pattern is `COMPARISON` and cardinality ≤ 50 | **Bar chart** — multi-series comparison |
| 8 | Narrative synthesis requested and result rows ≤ threshold | **Narrative card** — governed prose anchored to result |
| 9 | All other results | **Governed data table** — sortable, filterable, exportable |

---

## Rendering output types

### Chart rendering

Charts are rendered using the library specified in the tenant's `visualisation.defaultChartLibrary` config. The platform supports three libraries:

| Library | Format | Strengths | Host configuration |
|---------|--------|-----------|-------------------|
| Vega-Lite | JSON spec | Declarative, composable, excellent for grammar-of-graphics patterns | `"vega-lite"` |
| Plotly | JSON spec | Financial chart types (candlestick, OHLC), 3D support | `"plotly"` |
| ECharts | JSON spec | High-performance for large datasets, heatmaps, treemaps | `"echarts"` |

All three libraries render from a JSON specification produced by the rendering pipeline. The pipeline populates the specification template from the matching Visualisation Ontology contract and the result schema.

### Governed data table

Every chart rendering also produces a **secondary data table** view accessible via a *"Show as table"* toggle. This ensures analytical data is always accessible in raw tabular form regardless of chart type.

| Table feature | Specification |
|-------------|--------------|
| Column headers | SMR metric labels and dimension labels — never physical column names |
| Number formatting | From metric `display.format` and `display.decimals` in the SMR definition |
| Sorting | Click column header — ascending/descending |
| Filtering | Inline per-column filter |
| Pagination | 25 rows per page; configurable up to 1,000 |
| Export | CSV and JSON — exports include lineage reference |
| Sparklines | Inline sparklines for temporal metrics (when a date dimension is present alongside other dimensions) |
| Threshold highlighting | Cells where a metric exceeds a registered threshold are highlighted per the `sign_convention` in the SMR definition |

### Narrative card

Narrative synthesis produces a structured prose card composed of:

1. **Lead sentence** — the primary finding: *"Across 14 portfolios, 9 outperformed their benchmark this quarter."*
2. **Supporting detail** — the two or three most analytically significant observations from the result set
3. **Notable outliers** — dimension values at the extreme ends of the metric distribution
4. **Data provenance** — *"Data as of 14 May 2026, Q2 2026 QTD."*
5. **Anchoring disclosure** — a collapsed inspector showing the source result values the narrative was derived from

**Narrative synthesis constraints:**

| Constraint | Enforcement mechanism |
|-----------|----------------------|
| No metric values not in the result | Post-generation validation against result set — regenerate if violated |
| No LLM training data figures | Prompt-level constraint: *"You may only reference values from the provided result set."* |
| No hedging language about data accuracy | Narrative anchored to governance metadata (data refresh cadence, SLA) in the SMR |
| No recommendation or investment advice | Prompt-level constraint — describe, do not recommend |
| Unit-correct formatting | Numbers formatted using SMR metric `display.format` before injection into narrative prompt |

### Lineage inspector

The lineage inspector is a collapsible disclosure available on every analytical result, accessible to Power Analysts and above:

```
┌────────────────────────────────────────────────────────┐
│ 🔍 Query Lineage  [Expand ▼]                           │
└────────────────────────────────────────────────────────┘
```

On expansion:

```
┌────────────────────────────────────────────────────────────┐
│ 🔍 Query Lineage  [Collapse ▲]                             │
├────────────────────────────────────────────────────────────┤
│ Your question                                              │
│ "Show portfolio returns vs benchmark for Q2 2026"          │
├────────────────────────────────────────────────────────────┤
│ Resolved metrics                                           │
│  • portfolio_return v2.1.0  — Performance › Portfolio      │
│    Owner: Head of Performance Analytics                    │
│  • benchmark_return v1.4.0  — Performance › Benchmark      │
│    Owner: Head of Performance Analytics                    │
├────────────────────────────────────────────────────────────┤
│ Applied filters                                            │
│  • Row: portfolio_id IN ('GLOB_EQ_OPP', ...)  [Role filter]│
├────────────────────────────────────────────────────────────┤
│ Execution                                                  │
│  • Engine: snowflake-primary  (1,240 ms)                   │
│  • Engine: dbt-semantic  (890 ms)                          │
│  • Total: 1,285 ms  •  Cost: 500 units                     │
├────────────────────────────────────────────────────────────┤
│ Data currency                                              │
│  • portfolio_return: Daily refresh, data as of T+1         │
│  • benchmark_return: Daily refresh, data as of T+1         │
├────────────────────────────────────────────────────────────┤
│ Lineage ID: lqp_20260514_093247_a1b2c3  [Copy]             │
└────────────────────────────────────────────────────────────┘
```

---

## Streaming behaviour

| Content type | Streaming behaviour |
|-------------|-------------------|
| Narrative prose | Streams token-by-token; renders incrementally |
| Chart rendering | Rendered after FQP result assembly completes — not streamed |
| Data table | Rendered after FQP result assembly completes — not streamed |
| Lineage inspector | Rendered after lineage record is written — not streamed |
| Governance warnings | Displayed immediately when triggered (before execution) |

While the FQP is executing, the rendering layer displays a **progress indicator** with live status:

```
Resolving metrics…   ✓
Applying entitlements…   ✓
Planning query…   ✓
Executing (2 engines)…   ⏳ 890 ms
```

---

## Analytical result artefact

Every analytical result produces an **artefact** stored in the session artefact tray:

| Artefact element | Content |
|-----------------|---------|
| Chart image | SVG export of the rendered chart |
| Data table | CSV of the underlying result set |
| Lineage document | JSON lineage record |
| Narrative text | Plain text of the narrative synthesis |
| DSL expression | The internal DSL expression that produced the result |

Artefacts are downloadable from the tray individually or as a zip archive. Exports are governed by the `requireLineageForExport` setting — if enabled, the lineage document is automatically bundled with every export.

---

## Custom host renderers

Host applications may register custom rendering modules for domain-specific visualisations not covered by the standard chart contracts:

```json
{
  "id":       "risk-gauge",
  "trigger":  "risk-gauge",
  "name":     "Risk Gauge",
  "moduleUrl": "https://cdn.acme.com/analytics-renderers/risk-gauge.js",
  "systemPromptGuidance": "Use the risk-gauge renderer when presenting a single VaR utilisation figure as a dial. The result must contain exactly: { score: 0–100, label: string, threshold: number }."
}
```

Custom renderers receive the result set and the selected chart contract from the Visualisation Ontology. They are loaded as ES modules and rendered in an isolated shadow DOM, following the same renderer contract as the AI Chat Platform.

---

## Error states in rendering

| Error | User-facing message | Rendering fallback |
|-------|--------------------|--------------------|
| No matching chart contract | *"This result cannot be represented as a chart — showing as table."* | Governed data table |
| Chart library render failure | *"Chart rendering failed — showing raw data."* | Governed data table |
| Custom renderer load failure | *"[Renderer name] could not load — showing standard chart."* | Standard ontology chart |
| Result cardinality exceeds threshold | *"Result has N rows — chart limited to first 10,000. Download the full dataset below."* | Chart with sampled data + full CSV download |
| Narrative synthesis constraint violation | *(Narrative regenerated internally — user sees second-attempt narrative or, if two attempts fail, no narrative is shown)* | Chart + table only; no narrative |
