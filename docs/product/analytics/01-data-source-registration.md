# 01 — Data Source Registration and Platform Administration

## Overview

Data sources and entitlement policies are registered via the **Platform Admin API** (authenticated by a platform administrator credential). A web-based **Admin Console** provides a visual interface over the same API.

---

## Data Source Catalog

The Data Source Catalog is the platform's registry of execution backends. The Federated Query Planner routes Logical Query Plan fragments to backends based on data domain affinity.

### Backend registration

```json
{
  "executionBackends": [
    {
      "id":           "primary-warehouse",
      "name":         "Primary Data Warehouse",
      "type":         "sql_warehouse",
      "endpoint":     "https://internal.api/analytics/backends/warehouse",
      "authType":     "service-account",
      "capabilities": ["aggregate", "filter", "join", "window", "timeseries"],
      "dataAffinity": ["portfolio", "positions", "transactions", "benchmarks"],
      "priority":     1,
      "costTier":     "standard",
      "enabled":      true
    },
    {
      "id":           "risk-semantic-layer",
      "name":         "Risk Metrics Semantic Layer",
      "type":         "semantic_layer",
      "endpoint":     "https://internal.api/analytics/backends/risk",
      "authType":     "service-account",
      "capabilities": ["metric", "dimension", "filter"],
      "dataAffinity": ["risk_metrics", "performance_attribution"],
      "priority":     1,
      "costTier":     "low",
      "enabled":      true
    },
    {
      "id":           "market-data-api",
      "name":         "Market Data Feed",
      "type":         "opendata_api",
      "endpoint":     "https://internal.api/analytics/backends/market-data",
      "authType":     "api-key",
      "capabilities": ["filter", "timeseries"],
      "dataAffinity": ["benchmark_prices", "fx_rates", "index_constituents"],
      "priority":     1,
      "costTier":     "low",
      "enabled":      true
    },
    {
      "id":           "entity-graph",
      "name":         "Entity Relationship Graph",
      "type":         "graph_api",
      "endpoint":     "https://internal.api/analytics/backends/entity-graph",
      "authType":     "service-account",
      "capabilities": ["filter", "traverse"],
      "dataAffinity": ["counterparty", "entity_relationships"],
      "priority":     1,
      "costTier":     "standard",
      "enabled":      true
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Determines how the FQP translates plan fragments. Accepted: `sql_warehouse`, `opendata_api`, `graph_api`, `semantic_layer`, `olap_engine`, `custom` |
| `endpoint` | Yes | HTTPS endpoint conforming to the backend adapter protocol for the declared `type` |
| `authType` | Yes | `service-account` — platform's own credentials; `api-key` — platform holds a secret key; `bearer` — forwards the calling user's JWT |
| `capabilities` | Yes | Operations the FQP may route to this backend. Accepted: `aggregate`, `filter`, `join`, `window`, `timeseries`, `metric`, `dimension`, `pre-aggregated`, `traverse` |
| `dataAffinity` | Yes | Logical data domains this backend is authoritative for. The FQP routes metrics whose `data.domain` matches. Must reference SMR-declared domains. Migrating data between backends requires updating this field, not metric definitions. |
| `priority` | No | Routing priority when multiple backends can serve a sub-plan — lower is higher priority. Default: `10`. |
| `costTier` | No | Cost contribution for the governance circuit breaker. Accepted: `minimal`, `low`, `standard`, `high`, `unrestricted`. Default: `standard`. |
| `enabled` | No | Disabled backends are skipped; query fails if no alternative covers the required data affinity. Default: `true`. |

---

## Entitlement Model

Entitlement policies are defined per role. See [09-role-aware-projections.md](./09-role-aware-projections.md) for the full schema. The Admin API accepts entitlement configs at `POST /v1/admin/entitlements`.

---

## Semantic Metrics Registry — administration settings

```json
{
  "metricRegistry": {
    "seedTemplate":         ["wealth_management", "risk_management"],
    "approvalRequired":     true,
    "ownershipRequired":    true,
    "versionControl":       true,
    "fiscalYearStartMonth": 1
  }
}
```

| Field | Description |
|-------|-------------|
| `seedTemplate` | Pre-built templates loaded on initialisation. Accepted: `wealth_management`, `banking`, `investment_management`, `risk_management`, `regulatory`. All definitions can be extended or superseded via the Admin API. |
| `approvalRequired` | New or modified metric definitions require administrator approval before becoming resolvable. Default: `true`. |
| `ownershipRequired` | Every metric must have an assigned owner before approval. Default: `true`. |
| `versionControl` | Records the definition version in each query's lineage record. Default: `true`. |
| `fiscalYearStartMonth` | Integer (1–12) for fiscal year calculations in time period expressions. Default: `1`. |

---

## Governance settings

```json
{
  "governance": {
    "maxQueryCostUnits":       1000,
    "maxConcurrentQueries":    5,
    "queryTimeoutSeconds":     60,
    "classificationGating":    true,
    "blockedClassifications":  ["TOP_SECRET", "RESTRICTED"],
    "requireLineageForExport": true,
    "auditAllQueries":         true,
    "complianceMode":          "mifid2"
  }
}
```

| Field | Description |
|-------|-------------|
| `maxQueryCostUnits` | Cost unit ceiling per query; queries exceeding this are blocked. |
| `maxConcurrentQueries` | Per-user concurrency limit. Default: `5`. |
| `queryTimeoutSeconds` | Execution time limit before the FQP cancels the query. Default: `60`. |
| `classificationGating` / `blockedClassifications` | When `true`, blocks queries touching data at or above any label in `blockedClassifications`. Default gating: `true`. |
| `requireLineageForExport` | Withholds result downloads until the full lineage record is written. Default: `true`. |
| `auditAllQueries` | Writes every request — including blocked requests — to the audit trail. Default: `true`. |
| `complianceMode` | Named compliance profile applying domain-specific governance rules. Accepted: `mifid2`, `basel3`, `aifmd`, `sec_reg_bi`, `mas_faa`, `custom`. See [12-governed-execution.md](./12-governed-execution.md). |

---

## Operational settings

```json
{
  "scope": {
    "analyticalDomain":           "wealth_management",
    "regulatoryJurisdiction":     "UK",
    "requiresIntentConfirmation": false
  },
  "models": {
    "intentResolutionModel":   "standard",
    "narrativeSynthesisModel": "fast"
  },
  "visualisation": {
    "allowedChartTypes": ["bar", "line", "area", "scatter", "heatmap", "treemap", "waterfall", "table"],
    "colorPalette":      "categorical_financial",
    "numberFormat":      { "currency": "GBP", "locale": "en-GB", "decimals": 2, "largeNumbers": "abbreviated" },
    "thresholds":        { "maxDataPoints": 10000, "maxSeriesPerChart": 20 }
  },
  "features": {
    "naturalLanguageQuery": true,  "governedDrilldown":   true,  "narrativeSynthesis":  true,
    "resultDownload":       true,  "intentConfirmation":  false, "benchmarkComparison": true,
    "regulatoryReporting":  false
  }
}
```

| Field | Description |
|-------|-------------|
| `scope.analyticalDomain` | Selects SMR seed templates; injects domain context into intent resolution. |
| `scope.regulatoryJurisdiction` | Default compliance classification rules. Accepted: `UK`, `EU`, `US`, `SG`, `AU`, `HK`, or comma-separated for multi-jurisdictional. |
| `scope.requiresIntentConfirmation` | Returns a structured intent confirmation before executing any plan. Recommended for high-governance environments. Default: `false`. |
| `models.intentResolutionModel` | `fast` / `standard` / `powerful`. Default: `standard`. |
| `models.narrativeSynthesisModel` | `fast` / `standard` / `powerful`. Default: `fast`. |
| `visualisation.allowedChartTypes` | Chart types the Visualisation Ontology may select; others fall back to `table`. |
| `visualisation.colorPalette` | Named colour scheme for chart series in SCL display specs. |
| `visualisation.numberFormat` | Currency, locale, decimal, and large-number formatting for display specs and narrative. |
| `visualisation.thresholds.maxDataPoints` | Maximum data points per result; queries exceeding this trigger the governance circuit breaker. |
| `visualisation.thresholds.maxSeriesPerChart` | Maximum chart series; queries exceeding this trigger automatic FQP aggregation. |
| `features.*` | Boolean flags — all default to `true` except `intentConfirmation` (`false`) and `regulatoryReporting` (`false`). `regulatoryReporting` additionally requires an appropriate role and `complianceMode`. See JSON above for the full set. |

---

## Registration validation

Configuration is validated synchronously before being applied. All checks must pass; errors return field-level detail.

| Check | Validates |
|-------|-----------|
| Backend reachability | Each endpoint responds to a health check |
| Data affinity consistency | All `dataAffinity` values reference SMR-declared domains or seed templates |
| Role claim field | `entitlements.roleClaimField` is resolvable from a test JWT |
| Metric access references | All metric IDs in role `metricAccess` arrays exist in the SMR |
| Compliance mode compatibility | `complianceMode` is compatible with `regulatoryJurisdiction` |
