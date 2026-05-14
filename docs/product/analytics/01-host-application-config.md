# 01 — Tenant Configuration

Every tenant on the AI Analytics Platform is defined by a **JSON configuration** provided by the host application at registration time. The config is the single source of truth for how the analytics layer behaves within that application — its semantic domain, execution backends, entitlement model, metric registry scope, chart preferences, and feature flags.

---

## Config delivery

Configs are registered and updated via the **Platform Admin API** (authenticated by a platform API key scoped to the tenant). A web-based **Config Editor UI** provides a visual wrapper over the same API for non-technical Application Admins. Both target the same config document.

Config takes effect on the **next request** after the update is applied. In-flight requests complete under the previous config.

---

## Config schema

```json
{
  "version": "1.0.0",

  "identity":           { ... },
  "scope":              { ... },
  "executionBackends":  [ ... ],
  "metricRegistry":     { ... },
  "entitlements":       { ... },
  "visualisation":      { ... },
  "drilldown":          { ... },
  "governance":         { ... },
  "models":             { ... },
  "features":           { ... }
}
```

---

## `identity`

```json
{
  "identity": {
    "tenantId":               "acme-wealth",
    "applicationName":        "Acme Wealth Management Platform",
    "analyticsName":          "Meridian Analytics",
    "analyticsDescription":   "Governed portfolio analytics for Acme Wealth Management.",
    "analyticalDomain":       "wealth_management",
    "regulatoryJurisdiction": "UK",
    "supportUrl":             "https://help.acme.com/meridian",
    "privacyPolicyUrl":       "https://acme.com/privacy"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `tenantId` | Yes | Unique slug identifier for this tenant on the platform |
| `applicationName` | Yes | Name of the host application — shown in platform admin UI and lineage records |
| `analyticsName` | Yes | The name consumers see for the analytics layer (e.g. "Meridian Analytics", "Apex Insights") — injected into intent resolution prompts |
| `analyticsDescription` | Yes | One-sentence description of the analytical service — injected into MCP tool descriptions surfaced to AI orchestrators |
| `analyticalDomain` | Yes | Domain identifier used to seed pre-built metric registry templates. Accepted values: `wealth_management`, `banking`, `investment_management`, `institutional_analytics`, `risk_management`, `custom` |
| `regulatoryJurisdiction` | No | Primary regulatory jurisdiction — affects default compliance classification rules. Accepted: `UK`, `EU`, `US`, `SG`, `AU`, `HK`, or a comma-separated list for multi-jurisdictional deployments. |
| `supportUrl` | No | URL included in governance-blocked error responses for consumer-side error states |
| `privacyPolicyUrl` | No | URL included in data access disclosures |

---

## `scope`

Defines the analytical service's domain, what queries it should serve, and how it handles out-of-scope requests.

```json
{
  "scope": {
    "systemPrompt":               "You are Meridian, the governed analytics service for Acme Wealth Management. You help portfolio managers, risk officers, and relationship managers access portfolio analytics, risk metrics, and performance data using governed semantic definitions. Always resolve metrics by their registered IDs. Do not attempt to estimate or infer metric values.",
    "analyticalScope":            "Portfolio analytics, risk metrics, performance attribution, and regulatory reporting within Acme Wealth Management",
    "outOfScopeMessage":          "This request is outside the governed analytical scope for Acme Wealth Management.",
    "language":                   "en",
    "requiresIntentConfirmation": false
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `systemPrompt` | Yes | Base system prompt for the Semantic Intent Layer. The platform appends metric registry context, entitlement summaries, and governance instructions. Injected verbatim — keep focused on analytical domain and governance constraints. |
| `analyticalScope` | Yes | Plain-language description of analytical scope — returned in out-of-scope MCP error responses. |
| `outOfScopeMessage` | No | Message returned to consumers when a query is outside analytical scope. Platform uses a generic fallback if not set. |
| `language` | No | BCP 47 language tag for narrative synthesis output (default: `en`). |
| `requiresIntentConfirmation` | No | When `true`, the platform returns a structured intent confirmation object before executing any analytical plan. The consumer must acknowledge before the plan proceeds. Recommended for high-governance environments. Default: `false`. |

---

## `executionBackends`

Registers the analytical execution backends available within this tenant. The Federated Query Planner (FQP) routes Logical Query Plan fragments to registered backends based on capability declarations and data affinity. Backends may be SQL data warehouses, OpenData APIs, Graph Data APIs, semantic layers, OLAP engines, or any other data retrieval mechanism the host operates.

```json
{
  "executionBackends": [
    {
      "id":           "primary-warehouse",
      "name":         "Primary Data Warehouse",
      "type":         "sql_warehouse",
      "endpoint":     "https://api.acme.com/analytics/backends/warehouse",
      "authType":     "bearer",
      "capabilities": ["aggregate", "filter", "join", "window", "timeseries"],
      "dataAffinity": ["portfolio", "positions", "transactions", "benchmarks"],
      "priority":     1,
      "costTier":     "standard",
      "enabled":      true
    },
    {
      "id":           "semantic-layer",
      "name":         "Semantic Metrics Layer",
      "type":         "semantic_layer",
      "endpoint":     "https://api.acme.com/analytics/backends/semantic",
      "authType":     "api-key",
      "capabilities": ["metric", "dimension", "filter"],
      "dataAffinity": ["risk_metrics", "performance_attribution"],
      "priority":     2,
      "costTier":     "low",
      "enabled":      true
    },
    {
      "id":           "market-data-api",
      "name":         "Market Data OpenData API",
      "type":         "opendata_api",
      "endpoint":     "https://api.acme.com/analytics/backends/market-data",
      "authType":     "api-key",
      "capabilities": ["filter", "timeseries"],
      "dataAffinity": ["benchmark_prices", "fx_rates", "index_constituents"],
      "priority":     3,
      "costTier":     "low",
      "enabled":      true
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tenant |
| `name` | Yes | Display name shown in lineage records and admin UI |
| `type` | Yes | Backend category — determines how the FQP translates Logical Query Plan fragments into backend requests. Accepted: `sql_warehouse`, `opendata_api`, `graph_api`, `semantic_layer`, `olap_engine`, `custom` |
| `endpoint` | Yes | Platform-facing HTTPS endpoint that accepts LQP fragments and returns result sets per the platform's backend adapter protocol |
| `authType` | Yes | `bearer` (user JWT forwarded), `api-key` (platform holds key per tenant), `service-account` |
| `capabilities` | Yes | Query capabilities this backend supports. Used by the FQP for sub-plan routing. Accepted: `aggregate`, `filter`, `join`, `window`, `timeseries`, `metric`, `dimension`, `pre-aggregated` |
| `dataAffinity` | Yes | Logical data domains this backend is the preferred source for. Must reference domains declared in the SMR. Used by FQP for sub-plan routing. |
| `priority` | No | Routing priority when multiple backends can serve a sub-plan (lower = higher priority). Default: `10`. |
| `costTier` | No | Execution cost tier — used by the governance circuit breaker. Accepted: `minimal`, `low`, `standard`, `high`, `unrestricted`. Default: `standard`. |
| `enabled` | No | Whether this backend is available for routing. Default: `true`. |

---

## `metricRegistry`

Configures the Semantic Metrics Registry (SMR) for this tenant.

```json
{
  "metricRegistry": {
    "seedTemplate":         "wealth_management",
    "customMetricsUrl":     "https://api.acme.com/analytics/metrics/registry",
    "refreshIntervalMins":  15,
    "versionControl":       true,
    "approvalRequired":     true,
    "ownershipRequired":    true,
    "maxMetrics":           500,
    "defaultAggregation":   "sum",
    "fiscalYearStartMonth": 1
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `seedTemplate` | No | Pre-built metric definitions to seed the registry from. Accepted: `wealth_management`, `banking`, `investment_management`, `risk_management`, `regulatory`. Multiple values accepted as an array. |
| `customMetricsUrl` | No | Host-provided endpoint from which the platform fetches the tenant's custom metric definitions (per the SMR schema in [04-semantic-metrics-registry.md](./04-semantic-metrics-registry.md)). Polled at `refreshIntervalMins`. |
| `refreshIntervalMins` | No | How often the platform re-fetches metric definitions from `customMetricsUrl`. Default: `60`. |
| `versionControl` | No | Whether metric definitions are version-controlled in the registry. Default: `true`. Recommended — version history enables lineage reconstruction. |
| `approvalRequired` | No | Whether new or modified metric definitions require approval before becoming resolvable. Default: `true`. |
| `ownershipRequired` | No | Whether every metric must have an assigned owner before becoming resolvable. Default: `true`. |
| `maxMetrics` | No | Maximum number of active metrics in the tenant registry. Default: `500`. |
| `defaultAggregation` | No | Default aggregation rule applied when a metric definition does not specify one. Default: `sum`. |
| `fiscalYearStartMonth` | No | Integer (1–12) for fiscal year calculations. Default: `1` (January). |

---

## `entitlements`

Configures the Role-Aware Projection Layer for this tenant.

```json
{
  "entitlements": {
    "roleClaimField":   "analytics_roles",
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
        "metricAccess":    ["regulatory_capital", "lcr", "nsfr", "leverage_ratio"],
        "dimensionAccess": ["entity", "regulatory_classification", "jurisdiction", "date"],
        "rowPredicates":   [],
        "columnMasks":     ["client_name", "account_number"]
      }
    ]
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `roleClaimField` | Yes | The JWT claim key containing the user's role array |
| `defaultDenyAll` | No | When `true`, users with no matching role see no metrics. When `false`, users with no matching role receive a public-access metric set. Default: `true`. |
| `rowFilterMode` | No | How row-level filters are applied. `predicate_injection` — filter predicates injected into backend requests before execution (supported by SQL and compatible backends); `post_filter` — result rows filtered after backend assembly (backend-agnostic, higher data transfer). Default: `predicate_injection`. |
| `columnMaskingMode` | No | How masked columns are handled in result sets. `null_replacement` — masked values replaced with null; `redacted_label` — replaced with `[REDACTED]`; `excluded` — column omitted from result. Default: `null_replacement`. |
| `roles` | Yes | Array of role definitions. Each role maps to a metric access list, dimension access list, row predicates, and column masks. |

### Role definition fields

| Field | Description |
|-------|-------------|
| `id` | Unique role identifier — must match values in user JWTs |
| `label` | Display name for admin UI and lineage records |
| `metricAccess` | Array of metric IDs (from the SMR) this role may query. Wildcard `["*"]` grants access to all registered metrics. |
| `dimensionAccess` | Array of dimension IDs this role may slice by. Wildcard `["*"]` grants all dimensions. |
| `rowPredicates` | Predicate expressions applied as row filters. Use `{{user.claim_name}}` to reference JWT claim values. For SQL backends: injected as WHERE clauses. For API backends: applied as post-assembly filters unless the backend adapter supports native predicate push-down. |
| `columnMasks` | Array of result column names to mask for this role. Applied by the FQP before result assembly. |

---

## `visualisation`

Configures the Visualisation Ontology's chart contract preferences for this tenant. These settings govern which chart types the Visualisation Ontology may select and how numeric values are formatted in both chart specifications and narrative synthesis. **Chart library choice is a consumer-side decision and is not configured here.**

```json
{
  "visualisation": {
    "allowedChartTypes": ["bar", "line", "area", "scatter", "heatmap", "treemap", "waterfall", "gauge", "table", "sparkline"],
    "colorPalette":      "categorical_financial",
    "numberFormat": {
      "currency":     "GBP",
      "locale":       "en-GB",
      "decimals":     2,
      "largeNumbers": "abbreviated"
    },
    "thresholds": {
      "maxDataPoints":    10000,
      "maxSeriesPerChart": 20
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `allowedChartTypes` | Chart contract types the Visualisation Ontology may select for this tenant. Restricting this set enforces visual consistency. Chart contracts not listed here fall back to `table`. Accepted: `bar`, `line`, `area`, `scatter`, `heatmap`, `treemap`, `waterfall`, `gauge`, `table`, `sparkline`. |
| `colorPalette` | Named colour scheme for chart series in SCL display specs. Platform-provided options: `categorical_financial`, `sequential_blue`, `diverging_red_green`, `monochrome`. Colour assignments are included in the `display_spec` returned to consumers. |
| `numberFormat` | Default number formatting applied to metric values in SCL display specs and narrative synthesis. Consumers should respect these format hints when rendering. |
| `thresholds.maxDataPoints` | Maximum data points included in a single display spec result. Queries exceeding this threshold trigger the governance circuit breaker. |
| `thresholds.maxSeriesPerChart` | Maximum chart series in a single display spec. Queries resolving more series trigger automatic aggregation by the FQP. |

---

## `drilldown`

Configures governed drilldown behaviour — how consumers and AI agents traverse analytical hierarchies.

```json
{
  "drilldown": {
    "enabled":            true,
    "maxDepth":           4,
    "allowedHierarchies": ["asset_class_hierarchy", "geography_hierarchy", "time_hierarchy", "organisational_hierarchy"],
    "requireConfirmation": false,
    "preserveFilters":    true
  }
}
```

| Field | Description |
|-------|-------------|
| `enabled` | Whether governed drilldown is available in this tenant. Default: `true`. |
| `maxDepth` | Maximum levels of hierarchy traversal per session. Prevents runaway recursive queries. Default: `4`. |
| `allowedHierarchies` | Hierarchy IDs (defined in the SMR) that drilldown may traverse. Hierarchies not listed cannot be traversed. |
| `requireConfirmation` | When `true`, the platform returns a drilldown confirmation object before traversing. The consumer must acknowledge before the drilldown proceeds. Default: `false`. |
| `preserveFilters` | Whether parent-level row filters carry forward to child levels during drilldown. Default: `true`. |

---

## `governance`

Configures the Semantic Execution Governance layer for this tenant.

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
| `maxQueryCostUnits` | Maximum estimated cost units for a single analytical query. Queries exceeding this limit are blocked and a governance-blocked error is returned to the consumer. |
| `maxConcurrentQueries` | Per-user concurrency limit. Default: `5`. |
| `queryTimeoutSeconds` | Maximum execution time before the FQP cancels the query. Default: `60`. |
| `classificationGating` | When `true`, data classification metadata is evaluated before execution — queries touching data at or above `blockedClassifications` are blocked. Default: `true`. |
| `blockedClassifications` | Data classification labels that block query execution. Sourced from the host's data classification taxonomy. |
| `requireLineageForExport` | When `true`, result downloads cannot proceed until the lineage record is fully written. Default: `true`. |
| `auditAllQueries` | When `true`, every request — including those that fail governance checks — is written to the audit trail. Default: `true`. |
| `complianceMode` | Named compliance profile that pre-configures governance defaults. Accepted: `mifid2`, `basel3`, `aifmd`, `sec_reg_bi`, `mas_faa`, `custom`. |

---

## `models`

```json
{
  "models": {
    "intentResolutionModel":  "standard",
    "narrativeSynthesisModel": "standard",
    "allowedModels":           ["standard", "powerful"]
  }
}
```

| Field | Description |
|-------|-------------|
| `intentResolutionModel` | Model tier used for semantic intent resolution. Default: `standard`. |
| `narrativeSynthesisModel` | Model tier used for narrative synthesis. More complex narratives may warrant `powerful`. Default: `standard`. |
| `allowedModels` | Model tiers available for this tenant. Requests specifying a tier outside this list are rejected. |

---

## `features`

```json
{
  "features": {
    "naturalLanguageQuery":  true,
    "governedDrilldown":     true,
    "narrativeSynthesis":    true,
    "resultDownload":        true,
    "intentConfirmation":    false,
    "benchmarkComparison":   true,
    "regulatoryReporting":   false
  }
}
```

| Flag | Default | Description |
|------|---------|-------------|
| `naturalLanguageQuery` | `true` | Enable natural language intent resolution — MCP tool calls are resolved from natural language input |
| `governedDrilldown` | `true` | Enable hierarchy traversal via the `drilldown` MCP capability |
| `narrativeSynthesis` | `true` | Enable LLM-generated prose anchored to result values in MCP responses |
| `resultDownload` | `true` | Enable result download links in MCP responses (CSV and JSON) — governed by `requireLineageForExport` |
| `intentConfirmation` | `false` | Require consumer acknowledgement of resolved intent before plan execution |
| `benchmarkComparison` | `true` | Enable benchmark dimension access in metric queries |
| `regulatoryReporting` | `false` | Enable regulatory metric domain (requires appropriate role and compliance mode configuration) |

---

## Config validation

Submitting a config via the Admin API runs synchronous validation before applying:

| Check | Description |
|-------|-------------|
| Schema conformance | All required fields present; field types match schema |
| Execution backend reachability | Backend endpoints respond to a health check |
| Role claim field presence | `entitlements.roleClaimField` resolvable from test JWT |
| Metric access references | All metric IDs in role `metricAccess` arrays must exist in the seeded SMR or be declared as custom metrics |
| Hierarchy references in drilldown | All `allowedHierarchies` IDs must be defined in the SMR |
| Governance mode compatibility | `complianceMode` compatible with `regulatoryJurisdiction` |
| System prompt token count | Must be under 3,000 tokens |

Validation errors return a structured response with field-level detail. Config is not applied until all checks pass.
