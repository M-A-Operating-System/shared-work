# 07 — Visualisation Ontology

## Overview

The **Visualisation Ontology** is the governing schema that maps result characteristics and analytical intent patterns to specific, parameterised chart contracts. It ensures that the same analytical pattern always produces the same chart type — across users, sessions, and time — regardless of which AI model is in use or how the question was phrased.

The Visualisation Ontology makes chart selection **deterministic and governed**. The AI model does not select chart types. It may express an intent preference (e.g. *"show me a breakdown"*), which the ontology treats as an intent signal alongside the result schema — but the ontology makes the final binding decision.

---

## Chart contract model

Each entry in the Visualisation Ontology is a **chart contract** — a named, versioned specification that defines:

1. **Match conditions** — what result schema and intent pattern this contract applies to
2. **Chart type** — the chart class to render
3. **Axis mappings** — how result columns map to visual axes and encodings
4. **Interaction semantics** — what click, hover, and drilldown interactions are available
5. **Rendering parameters** — default visual parameters (colours, labels, thresholds)

---

## Intent pattern taxonomy

The ontology classifies every analytical result into one of seven intent patterns, derived from the analytical intent and result schema:

| Intent pattern | Description | Typical trigger phrases |
|---------------|-------------|------------------------|
| `COMPARISON` | Comparing a metric across discrete categories | "compare", "by", "across", "ranked by", "top N" |
| `TREND` | Showing how a metric changes over time | "over time", "trend", "history", "30-day", "since" |
| `DISTRIBUTION` | Showing the spread or concentration of a metric | "distribution", "breakdown", "composition", "concentration" |
| `THRESHOLD` | Comparing a metric against a limit or benchmark | "exceeding", "within limit", "versus benchmark", "breach" |
| `ATTRIBUTION` | Decomposing a metric into contributing factors | "attribution", "contribution", "drivers", "breakdown by" |
| `RELATIONSHIP` | Showing correlation or dependency between metrics | "versus", "correlation", "scatter", "risk-return" |
| `COMPOSITION` | Showing part-to-whole relationships | "proportion", "weight", "allocation", "share" |

---

## Ontology contract definitions

### Contract 1 — Multi-series bar (COMPARISON)

**Contract ID:** `BAR_MULTI_SERIES_COMPARISON`

**Match conditions:**
- Intent pattern: `COMPARISON`
- Metric count: 1–3
- Primary dimension: categorical, cardinality: low–medium (< 50)
- Time dimension: absent OR single point in time

**Axis mappings:**
- X-axis: primary categorical dimension (sorted by primary metric DESC by default)
- Y-axis: metric value
- Colour encoding: metric series (for multi-metric) OR secondary dimension if present
- Tooltip: all metrics for the hovered category

**Example SCL contract (abbreviated):**
```json
{
  "contract_id":    "BAR_MULTI_SERIES_COMPARISON",
  "version":        "1.2.0",
  "chart_type":     "bar",
  "spec_template": {
    "mark":    { "type": "bar", "tooltip": true },
    "encoding": {
      "x": {
        "field":  "{{primary_dimension}}",
        "type":   "ordinal",
        "sort":   "-y",
        "axis":   { "labelAngle": -30 }
      },
      "y": {
        "field":    "{{primary_metric}}",
        "type":     "quantitative",
        "axis":     { "format": "{{metric_format}}" }
      },
      "color": {
        "field":    "{{series_dimension}}",
        "type":     "nominal",
        "scale":    { "scheme": "{{color_palette}}" }
      }
    }
  },
  "interaction": {
    "click":       "drilldown",
    "hover":       "tooltip",
    "selection":   "multi_point"
  }
}
```

---

### Contract 2 — Time series line (TREND)

**Contract ID:** `LINE_TIME_SERIES_TREND`

**Match conditions:**
- Intent pattern: `TREND`
- Time dimension: present, cardinality: multiple points
- Metric count: 1–5

**Axis mappings:**
- X-axis: temporal dimension
- Y-axis: metric value
- Colour: metric series or secondary categorical dimension
- Reference line: injected if comparison target (`compare_to`) is present in the query

**Interaction semantics:**
- Hover: crosshair tooltip showing all series values at hovered date
- Click on a data point: surface lineage for that specific time period
- Brush selection: zooms X-axis to selected range

---

### Contract 3 — Heatmap (THRESHOLD)

**Contract ID:** `HEATMAP_THRESHOLD_MATRIX`

**Match conditions:**
- Intent pattern: `THRESHOLD`
- Two categorical dimensions present
- Metric count: 1 (the threshold metric)
- Threshold value available (from `var_limit`, `budget`, etc.)

**Axis mappings:**
- X-axis: first categorical dimension (e.g. date)
- Y-axis: second categorical dimension (e.g. portfolio)
- Colour encoding: metric value expressed as % of threshold (diverging colour scale)
- Threshold boundary: colour scale midpoint anchored at 100% of limit

**Interaction semantics:**
- Click on cell: drilldown into that dimension intersection
- Colour scale: red (> 100% limit) → amber (80–100%) → green (< 80%)

---

### Contract 4 — Treemap (COMPOSITION)

**Contract ID:** `TREEMAP_COMPOSITION`

**Match conditions:**
- Intent pattern: `COMPOSITION` OR `DISTRIBUTION`
- One categorical dimension, cardinality: medium–high
- One metric representing a positive quantity (AUM, market value, weight)

**Axis mappings:**
- Area: proportional to metric value
- Colour: secondary metric (e.g. return) — diverging scale
- Label: dimension value + metric value

**Interaction semantics:**
- Click on tile: drilldown into next hierarchy level
- Hover: tooltip showing all metrics for the tile

---

### Contract 5 — Waterfall (ATTRIBUTION)

**Contract ID:** `WATERFALL_ATTRIBUTION`

**Match conditions:**
- Intent pattern: `ATTRIBUTION`
- Metrics include a total metric and one or more contribution metrics
- Contribution metrics sum to total metric

**Axis mappings:**
- X-axis: contribution dimension (factors, asset classes, etc.)
- Y-axis: contribution value (positive and negative)
- Colour: positive contribution (green), negative contribution (red), total (grey)

---

### Contract 6 — Scatter / risk-return (RELATIONSHIP)

**Contract ID:** `SCATTER_RISK_RETURN`

**Match conditions:**
- Intent pattern: `RELATIONSHIP`
- Exactly two numeric metrics
- One categorical dimension (e.g. portfolio, asset class)

**Axis mappings:**
- X-axis: first metric (conventionally risk measure)
- Y-axis: second metric (conventionally return measure)
- Colour: categorical dimension
- Size: optional third metric (e.g. AUM)
- Reference lines: quadrant boundaries from benchmark values (if present)

---

### Contract 7 — Data table (fallback and high-cardinality)

**Contract ID:** `TABLE_GOVERNED`

**Match conditions (any of):**
- Metric count > 5
- Primary dimension cardinality: high (> 50)
- No clear intent pattern match
- `LIMIT` clause present with no ordering by a visualisable metric
- User explicitly requested tabular output

**Table features:**
- Column headers from SMR metric labels and dimension labels
- Column-level sorting
- Column-level filtering
- Number formatting from metric `display.format` and `display.decimals`
- Inline sparklines for temporal metrics
- Export to CSV and JSON

---

## Ontology evaluation algorithm

The ontology evaluator receives:
1. The LQP (metrics, dimensions, time, filters)
2. The intent pattern classification (from the Semantic Intent Layer)
3. The result schema (actual column types and cardinalities from the FQP result)

It evaluates contracts in order of specificity and returns the highest-specificity matching contract:

```python
def evaluate_ontology(lqp, intent_pattern, result_schema, allowed_charts):
    candidates = []
    for contract in ONTOLOGY_CONTRACTS:
        if not all(c in allowed_charts for c in [contract.chart_type]):
            continue
        score = contract.match_score(lqp, intent_pattern, result_schema)
        if score > 0:
            candidates.append((score, contract))
    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates:
        return candidates[0][1]
    else:
        return TABLE_GOVERNED  # deterministic fallback
```

---

## Chart ontology override

Power Analysts may override the ontology's chart selection for a single result via an explicit intent in their query:

```
Show me portfolio returns as a line chart over the last 12 months
```

The override is logged in the lineage record as an analyst-requested deviation from the governing ontology. Overrides are subject to:
- The chart type being in the tenant's `allowedChartTypes` list
- The result schema being compatible with the requested chart type (incompatible overrides are rejected with an explanation)

---

## Rendering pipeline

After the ontology selects a chart contract, the rendering pipeline:

1. Populates the contract's `spec_template` with values derived from the result schema (field names, metric formats, axis labels from SMR labels)
2. Applies the tenant's colour palette and number format settings
3. Injects benchmark reference lines or threshold markers if present in the LQP
4. Produces a final SCL display specification ready to return to the consumer
5. Produces a data table as a secondary view for all chart types (always available via a "Show as table" toggle)

---

## Narrative anchoring to visualisation

The Narrative Synthesis Engine receives:
- The chart contract selected by the ontology
- The chart's axis mappings (so it knows what is on each axis)
- The result set values
- The SMR metric definitions (label, unit, description)

It uses this structured context to produce prose that directly references the chart's visual elements: *"The chart shows quarterly return on the Y-axis against portfolio on the X-axis, sorted by highest return. Global Equity Opportunities leads at 4.2%, followed by..."*

The narrative never introduces values or comparisons not visible in the chart or derivable from the result set.
