# 01 — Data Source Registration and Platform Administration

## Overview

The AI Analytics Platform is a **shared backend service**. Before any analytical query can be served, a platform administrator must register two things:

1. **Data sources** — what data exists, where it lives, and how the Federated Query Planner reaches it
2. **Entitlement policies** — who is permitted to access which metrics, dimensions, and data rows

These are not per-consumer configurations. They are platform-level administrative declarations that apply to all consumers of the shared service — whether those consumers are interactive users, conversational AI assistants, autonomous agents, or report pipelines.

Data source registration tells the platform's Semantic Metrics Registry (SMR) what is queryable and where it lives. Entitlements determine who gets to see what. The two are independent — the same data source can serve queries from multiple roles, each receiving only the portion they are entitled to.

Both are managed via the **Platform Admin API**, authenticated by a platform administrator credential. A web-based **Admin Console** provides a visual interface over the same API for non-technical administrators.

---

## Data Source Catalog

The Data Source Catalog is the platform's registry of all available execution backends. The Federated Query Planner uses it to route Logical Query Plan fragments to the correct backend based on data domain affinity.

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
| `id` | Yes | Unique identifier for this backend within the platform |
| `name` | Yes | Display name shown in lineage records and the Admin Console |
| `type` | Yes | Backend category — determines how the FQP translates Logical Query Plan fragments. Accepted: `sql_warehouse`, `opendata_api`, `graph_api`, `semantic_layer`, `olap_engine`, `custom` |
| `endpoint` | Yes | HTTPS endpoint the platform calls. Must conform to the platform's backend adapter protocol for the declared `type`. |
| `authType` | Yes | How the platform authenticates to this backend. `service-account` — platform uses its own service credentials; `api-key` — platform holds a secret key per backend; `bearer` — forwards the calling user's JWT to the backend. |
| `capabilities` | Yes | Query operations this backend supports, used by the FQP for sub-plan routing. Accepted: `aggregate`, `filter`, `join`, `window`, `timeseries`, `metric`, `dimension`, `pre-aggregated`, `traverse` |
| `dataAffinity` | Yes | Logical data domains this backend is the authoritative source for. Must reference domains declared in the SMR. The FQP routes metrics whose `data.domain` matches one of these values to this backend. |
| `priority` | No | Routing priority when multiple backends can serve a sub-plan — lower number is higher priority. Used for failover ordering. Default: `10`. |
| `costTier` | No | Execution cost contribution used by the governance circuit breaker. Accepted: `minimal`, `low`, `standard`, `high`, `unrestricted`. Default: `standard`. |
| `enabled` | No | Whether this backend is available for routing. Disabled backends are skipped; if no alternative serves the required data affinity, the query fails with a backend-unavailable error. Default: `true`. |

### Data domain mapping

Each metric in the SMR declares a `data.domain` value — the logical domain it belongs to. The Data Source Catalog maps domains to backends:

```
Metric SMR definition
  └── data.domain: "risk_metrics"

Data Source Catalog
  └── executionBackend "risk-semantic-layer"
        └── dataAffinity: ["risk_metrics", "performance_attribution"]

FQP routing:
  metric "var_95" → data.domain "risk_metrics" → backend "risk-semantic-layer"
```

This separation is intentional. Metric definitions describe business meaning. Backend registrations describe physical availability. Migrating data from one backend to another requires updating the backend's `dataAffinity` declaration — not changing metric definitions or consumer queries.

---

## Entitlement Model

The entitlement model defines who can access which metrics, dimensions, and data rows. It is enforced by the Role-Aware Projection Layer at the semantic tier — before any backend is contacted.

```json
{
  "entitlements": {
    "roleClaimField":    "analytics_roles",
    "defaultDenyAll":   true,
    "rowFilterMode":    "predicate_injection",
    "columnMaskingMode": "null_replacement",
    "roles": [
      {
        "id":              "portfolio_manager",
        "label":           "Portfolio Manager",
        "metricAccess":    ["aum", "portfolio_return", "benchmark_return", "tracking_error", "sharpe_ratio"],
        "dimensionAccess": ["portfolio", "asset_class", "geography", "currency", "date"],
        "rowPredicates":   ["portfolio_id IN ({{user.managed_portfolios}})"],
        "columnMasks":     []
      },
      {
        "id":              "risk_officer",
        "label":           "Risk Officer",
        "metricAccess":    ["var_95", "var_99", "cvar", "beta", "duration", "credit_spread_dv01", "issuer_concentration"],
        "dimensionAccess": ["portfolio", "asset_class", "issuer", "rating", "date"],
        "rowPredicates":   [],
        "columnMasks":     []
      },
      {
        "id":              "compliance_analyst",
        "label":           "Compliance Analyst",
        "metricAccess":    ["lcr", "nsfr", "leverage_ratio"],
        "dimensionAccess": ["entity", "regulatory_classification", "jurisdiction", "date"],
        "rowPredicates":   [],
        "columnMasks":     ["client_name", "account_number"]
      },
      {
        "id":              "platform_admin",
        "label":           "Platform Administrator",
        "metricAccess":    ["*"],
        "dimensionAccess": ["*"],
        "rowPredicates":   [],
        "columnMasks":     []
      }
    ]
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `roleClaimField` | Yes | The JWT claim key from which the user's role array is extracted |
| `defaultDenyAll` | No | When `true`, users with no matching role see no metrics. When `false`, users with no role match receive a public-access metric set. Default: `true`. |
| `rowFilterMode` | No | How row-level restrictions are applied. `predicate_injection` — filter predicates are pushed into backend requests before execution (efficient; supported by SQL and most compatible backends). `post_filter` — result rows are filtered after backend assembly (backend-agnostic; higher data transfer overhead). Default: `predicate_injection`. |
| `columnMaskingMode` | No | How masked column values are represented in results. `null_replacement` — replaced with null; `redacted_label` — replaced with `[REDACTED]`; `excluded` — column omitted from result entirely. Default: `null_replacement`. |
| `roles` | Yes | Array of role definitions. |

### Role definition fields

| Field | Description |
|-------|-------------|
| `id` | Unique role identifier — must match values appearing in user JWTs under `roleClaimField` |
| `label` | Display name for audit records and the Admin Console |
| `metricAccess` | Metric IDs from the SMR this role may query. Wildcard `["*"]` grants access to all approved metrics. |
| `dimensionAccess` | Dimension IDs this role may slice by. Wildcard `["*"]` grants all dimensions. |
| `rowPredicates` | Row-level filter expressions applied before result delivery. `{{user.claim_name}}` templates are resolved from the calling user's JWT claims at query time. For SQL backends: injected as WHERE clause predicates. For API backends: applied as post-assembly filters unless the backend adapter supports native push-down. |
| `columnMasks` | Result column names to mask for this role. Applied by the FQP after result assembly, before delivery to the consumer. |

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
| `seedTemplate` | Pre-built metric definition templates to load on initialisation. Accepted: `wealth_management`, `banking`, `investment_management`, `risk_management`, `regulatory`. Templates are a starting point — all definitions can be extended or superseded via the Admin API. |
| `approvalRequired` | Whether new or modified metric definitions require administrator approval before becoming resolvable. Default: `true`. |
| `ownershipRequired` | Whether every metric must have an assigned owner before it is approved. Default: `true`. |
| `versionControl` | Whether metric definitions are version-controlled. Enabling this preserves the definition version used at each query's execution time in the lineage record. Default: `true`. |
| `fiscalYearStartMonth` | Integer (1–12) for fiscal year calculations in time period expressions. Default: `1` (January). |

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
| `maxQueryCostUnits` | Maximum estimated cost units allowed for a single analytical query. Queries exceeding this are blocked. |
| `maxConcurrentQueries` | Per-user concurrency limit. Default: `5`. |
| `queryTimeoutSeconds` | Maximum execution time before the FQP cancels the query. Default: `60`. |
| `classificationGating` | When `true`, queries touching data classified at or above any value in `blockedClassifications` are blocked before execution. Default: `true`. |
| `blockedClassifications` | Data classification labels that prevent query execution. |
| `requireLineageForExport` | When `true`, result downloads are withheld until the full lineage record is written. Default: `true`. |
| `auditAllQueries` | When `true`, every request — including governance-blocked requests — is written to the audit trail. Default: `true`. |
| `complianceMode` | Named compliance profile that applies domain-specific governance rules. Accepted: `mifid2`, `basel3`, `aifmd`, `sec_reg_bi`, `mas_faa`, `custom`. See [12-governed-execution.md](./12-governed-execution.md) for each profile's rules. |

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
    "numberFormat": {
      "currency":     "GBP",
      "locale":       "en-GB",
      "decimals":     2,
      "largeNumbers": "abbreviated"
    },
    "thresholds": {
      "maxDataPoints":     10000,
      "maxSeriesPerChart": 20
    }
  },
  "features": {
    "naturalLanguageQuery":  true,
    "governedDrilldown":     true,
    "narrativeSynthesis":    true,
    "resultDownload":        true,
    "intentConfirmation":    false,
    "benchmarkComparison":   true,
    "regulatoryReporting":   true
  }
}
```

### `scope`

| Field | Description |
|-------|-------------|
| `analyticalDomain` | Identifies the primary analytical domain. Used to select pre-built SMR seed templates and inject domain context into intent resolution. |
| `regulatoryJurisdiction` | Primary regulatory jurisdiction — affects default compliance classification rules. Accepted: `UK`, `EU`, `US`, `SG`, `AU`, `HK`, or a comma-separated list for multi-jurisdictional deployments. |
| `requiresIntentConfirmation` | When `true`, the platform returns a structured intent confirmation response before executing any analytical plan. The consumer must acknowledge before execution proceeds. Recommended for high-governance environments. Default: `false`. |

### `models`

| Field | Description |
|-------|-------------|
| `intentResolutionModel` | Model tier used for semantic intent resolution. `fast` / `standard` / `powerful`. Default: `standard`. |
| `narrativeSynthesisModel` | Model tier for narrative synthesis. Default: `fast`. |

### `visualisation`

Governs which chart contracts the Visualisation Ontology may select and how numeric values are formatted in returned display specifications. Consumer-side rendering library choice is not configured here.

| Field | Description |
|-------|-------------|
| `allowedChartTypes` | Chart contract types the Visualisation Ontology may select. Contracts outside this set fall back to `table`. |
| `colorPalette` | Named colour scheme for chart series in SCL display specs. Colour assignments are included in the `display_spec` returned to consumers. |
| `numberFormat` | Default number formatting applied to metric values in display specifications and narrative synthesis. Consumers should respect these format hints when rendering. |
| `thresholds.maxDataPoints` | Maximum data points in a single result. Queries exceeding this trigger the governance circuit breaker. |
| `thresholds.maxSeriesPerChart` | Maximum series in a single chart display spec. Queries exceeding this trigger automatic aggregation by the FQP. |

### `features`

| Flag | Default | Description |
|------|---------|-------------|
| `naturalLanguageQuery` | `true` | Enable natural language intent resolution in MCP tool calls |
| `governedDrilldown` | `true` | Enable hierarchy traversal via the `drilldown` MCP capability |
| `narrativeSynthesis` | `true` | Enable LLM-generated prose anchored to result values |
| `resultDownload` | `true` | Enable result download links (CSV and JSON) in MCP responses |
| `intentConfirmation` | `false` | Require consumer acknowledgement of resolved intent before plan execution |
| `benchmarkComparison` | `true` | Enable benchmark dimension access in metric queries |
| `regulatoryReporting` | `false` | Enable the regulatory metric domain (requires appropriate role and `complianceMode`) |

---

## Registration validation

Submitting configuration via the Admin API runs synchronous validation before applying:

| Check | Description |
|-------|-------------|
| Backend reachability | Each registered backend endpoint responds to a health check |
| Data affinity consistency | All `dataAffinity` values reference domains declared in the SMR or seed templates |
| Role claim field | `entitlements.roleClaimField` is resolvable from a test JWT |
| Metric access references | All metric IDs in role `metricAccess` arrays exist in the SMR or seed templates |
| Compliance mode compatibility | `complianceMode` compatible with `regulatoryJurisdiction` |

Configuration is not applied until all checks pass. Validation errors return a structured response with field-level detail.
