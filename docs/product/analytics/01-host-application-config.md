# 01 — Host Application Configuration

Every tenant on the AI Analytics Platform is defined by a **JSON application config** provided by the host application at registration time. The config is the single source of truth for how the analytics layer behaves within that application — its semantic domain, execution engines, entitlement model, metric registry scope, visualisation preferences, and feature flags.

---

## Config delivery

Configs are registered and updated via the **Platform Admin API** (authenticated by a platform API key scoped to the tenant). A web-based **Config Editor UI** provides a visual wrapper over the same API for non-technical Application Admins. Both target the same config document.

Config takes effect on the **next new analytical session** after the update is applied. Active sessions are not interrupted by config changes.

---

## Config schema

```json
{
  "$schema": "https://analytics-platform.io/config/v1/schema.json",
  "version": "1.0.0",

  "identity":          { ... },
  "branding":          { ... },
  "scope":             { ... },
  "executionEngines":  [ ... ],
  "metricRegistry":    { ... },
  "entitlements":      { ... },
  "visualisation":     { ... },
  "drilldown":         { ... },
  "governance":        { ... },
  "models":            { ... },
  "conversations":     { ... },
  "features":          { ... }
}
```

---

## `identity`

```json
{
  "identity": {
    "tenantId":              "acme-wealth",
    "applicationName":       "Acme Wealth Management Platform",
    "analyticsName":         "Meridian Analytics",
    "analyticsDescription":  "Governed portfolio analytics for Acme Wealth Management.",
    "analyticalDomain":      "wealth_management",
    "regulatoryJurisdiction": "UK",
    "supportUrl":            "https://help.acme.com/meridian",
    "privacyPolicyUrl":      "https://acme.com/privacy"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `tenantId` | Yes | Unique slug identifier for this tenant on the platform |
| `applicationName` | Yes | Name of the host application — shown in platform admin UI |
| `analyticsName` | Yes | The name end users see for the analytics layer (e.g. "Meridian Analytics", "Apex Insights") |
| `analyticsDescription` | Yes | One-sentence description shown in the onboarding welcome state |
| `analyticalDomain` | Yes | Domain identifier used to seed pre-built metric registry templates. Accepted values: `wealth_management`, `banking`, `investment_management`, `institutional_analytics`, `risk_management`, `custom` |
| `regulatoryJurisdiction` | No | Primary regulatory jurisdiction — affects default compliance classification rules. Accepted: `UK`, `EU`, `US`, `SG`, `AU`, `HK`, or a comma-separated list for multi-jurisdictional deployments. |
| `supportUrl` | No | URL linked from error states for end-user support |
| `privacyPolicyUrl` | No | URL displayed in data access consent UI |

---

## `branding`

```json
{
  "branding": {
    "colorPrimary":        "#003366",
    "colorSurface":        "#FFFFFF",
    "colorSurfaceVariant": "#F2F5F8",
    "colorOnSurface":      "#111827",
    "colorAccent":         "#00875A",
    "fontFamily":          "Inter, system-ui, sans-serif",
    "borderRadius":        "6px",
    "logoUrl":             "https://cdn.acme.com/logo.svg"
  }
}
```

Design tokens applied to the `<ai-analytics>` web component. Platform defaults apply for any token not provided.

---

## `scope`

Defines the analytical assistant's domain, what queries it should serve, and how it handles out-of-scope requests.

```json
{
  "scope": {
    "systemPrompt":          "You are Meridian, the governed analytics assistant for Acme Wealth Management. You help portfolio managers, risk officers, and relationship managers access portfolio analytics, risk metrics, and performance data using governed semantic definitions...",
    "analyticalScope":       "Portfolio analytics, risk metrics, performance attribution, and regulatory reporting within Acme Wealth Management",
    "outOfScopeRedirect":    "I'm scoped to governed portfolio and risk analytics for Acme Wealth Management. For general market research, please use the research portal.",
    "language":              "en",
    "requiresIntentConfirmation": false
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `systemPrompt` | Yes | Base system prompt for the analytical assistant. The platform appends metric registry context, entitlement summaries, and governance instructions. |
| `analyticalScope` | Yes | Plain-language description of analytical scope — injected into user-facing scope descriptions and out-of-scope redirect messages. |
| `outOfScopeRedirect` | No | Custom message for out-of-scope queries. Platform uses a generic fallback if not set. |
| `language` | No | BCP 47 language tag (default: `en`). |
| `requiresIntentConfirmation` | No | When `true`, the platform surfaces a structured intent confirmation card to the user before executing any analytical plan. Recommended for high-governance environments. Default: `false`. |

---

## `executionEngines`

Registers the analytical execution engines available within this tenant. The platform's Federated Query Planner routes Logical Query Plan fragments to registered engines based on capability declarations and data affinity.

```json
{
  "executionEngines": [
    {
      "id":           "snowflake-primary",
      "name":         "Primary Data Warehouse",
      "type":         "snowflake",
      "endpoint":     "https://api.acme.com/analytics/engines/snowflake",
      "authType":     "bearer",
      "capabilities": ["aggregate", "filter", "join", "window", "timeseries"],
      "dataAffinity": ["portfolio", "positions", "transactions", "benchmarks"],
      "priority":     1,
      "costTier":     "standard",
      "enabled":      true
    },
    {
      "id":           "dbt-semantic",
      "name":         "dbt Semantic Layer",
      "type":         "dbt_semantic_layer",
      "endpoint":     "https://api.acme.com/analytics/engines/dbt",
      "authType":     "api-key",
      "capabilities": ["metric", "dimension", "filter"],
      "dataAffinity": ["risk_metrics", "performance_attribution"],
      "priority":     2,
      "costTier":     "low",
      "enabled":      true
    },
    {
      "id":           "cube-olap",
      "name":         "OLAP Cache Layer",
      "type":         "cube",
      "endpoint":     "https://api.acme.com/analytics/engines/cube",
      "authType":     "bearer",
      "capabilities": ["aggregate", "filter", "pre-aggregated"],
      "dataAffinity": ["summary_metrics", "dashboard_kpis"],
      "priority":     3,
      "costTier":     "minimal",
      "enabled":      true
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tenant |
| `name` | Yes | Display name shown in lineage records and admin UI |
| `type` | Yes | Engine type — determines the physical query dialect the FQP generates. Accepted: `snowflake`, `bigquery`, `databricks`, `trino`, `dbt_semantic_layer`, `cube`, `redshift`, `postgres`, `custom` |
| `endpoint` | Yes | Platform-facing HTTPS endpoint that accepts LQP fragments and returns result sets per the platform's engine adapter protocol |
| `authType` | Yes | `bearer` (user JWT forwarded), `api-key` (platform holds key per tenant), `service-account` |
| `capabilities` | Yes | Array of query capabilities this engine supports. Used by the FQP for sub-plan routing. Accepted: `aggregate`, `filter`, `join`, `window`, `timeseries`, `metric`, `dimension`, `pre-aggregated` |
| `dataAffinity` | Yes | Logical data domains this engine is the preferred source for. Used by the FQP to route sub-plans. Must reference domains declared in the SMR. |
| `priority` | No | Routing priority when multiple engines can serve a sub-plan (lower = higher priority). Default: `10`. |
| `costTier` | No | Execution cost tier — used by the governance circuit breaker. Accepted: `minimal`, `low`, `standard`, `high`, `unrestricted`. Default: `standard`. |
| `enabled` | No | Whether this engine is available for routing. Default: `true`. |

---

## `metricRegistry`

Configures the Semantic Metrics Registry (SMR) for this tenant.

```json
{
  "metricRegistry": {
    "seedTemplate":        "wealth_management",
    "customMetricsUrl":    "https://api.acme.com/analytics/metrics/registry",
    "refreshIntervalMins": 15,
    "versionControl":      true,
    "approvalRequired":    true,
    "ownershipRequired":   true,
    "maxMetrics":          500,
    "defaultAggregation":  "sum",
    "fiscalYearStartMonth": 1
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `seedTemplate` | No | Pre-built metric definitions to seed the registry from. Accepted: `wealth_management`, `banking`, `investment_management`, `risk_management`, `regulatory`. Multiple can be specified as an array. |
| `customMetricsUrl` | No | Host-provided endpoint from which the platform fetches the tenant's custom metric definitions (YAML or JSON, per the SMR schema in [04-semantic-metrics-registry.md](./04-semantic-metrics-registry.md)). Polled at `refreshIntervalMins`. |
| `refreshIntervalMins` | No | How often the platform re-fetches metric definitions from `customMetricsUrl`. Default: `60`. |
| `versionControl` | No | Whether metric definitions are version-controlled in the platform's registry store. Default: `true`. Highly recommended — version history enables lineage reconstruction. |
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
    "roleClaimField":     "analytics_roles",
    "defaultDenyAll":     true,
    "rowSecurityMode":    "predicate_injection",
    "columnMaskingMode":  "null_replacement",
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
| `rowSecurityMode` | No | How row-level security is applied. `predicate_injection` — SQL predicates injected into physical queries; `pre-filter` — result sets filtered after FQP assembly. Default: `predicate_injection`. |
| `columnMaskingMode` | No | How masked columns are handled. `null_replacement` — masked values replaced with null; `redacted_label` — replaced with `[REDACTED]`; `excluded` — column omitted from result. Default: `null_replacement`. |
| `roles` | Yes | Array of role definitions. Each role maps to a metric access list, dimension access list, row predicates, and column masks. |

### Role definition fields

| Field | Description |
|-------|-------------|
| `id` | Unique role identifier — must match values in user JWTs |
| `label` | Display name for admin UI and lineage records |
| `metricAccess` | Array of metric IDs (from the SMR) this role may query. Wildcard `["*"]` grants access to all registered metrics. |
| `dimensionAccess` | Array of dimension IDs this role may slice by. Wildcard `["*"]` grants all dimensions. |
| `rowPredicates` | SQL-like predicate fragments injected at execution time. Use `{{user.claim_name}}` to reference JWT claim values. |
| `columnMasks` | Array of physical column names to mask for this role. Applied by the FQP before result assembly. |

---

## `visualisation`

Configures the Visualisation Ontology and rendering preferences for this tenant.

```json
{
  "visualisation": {
    "defaultChartLibrary": "vega-lite",
    "allowedChartTypes":   ["bar", "line", "area", "scatter", "heatmap", "treemap", "waterfall", "gauge", "table", "sparkline"],
    "colorPalette":        "categorical_financial",
    "numberFormat": {
      "currency":   "GBP",
      "locale":     "en-GB",
      "decimals":   2,
      "largeNumbers": "abbreviated"
    },
    "thresholds": {
      "maxDataPoints": 10000,
      "maxSeriesPerChart": 20
    },
    "customRenderers": [
      {
        "id":          "risk-heatmap",
        "trigger":     "risk-heatmap",
        "name":        "Risk Heatmap",
        "moduleUrl":   "https://cdn.acme.com/analytics-renderers/risk-heatmap.js"
      }
    ]
  }
}
```

| Field | Description |
|-------|-------------|
| `defaultChartLibrary` | Rendering library for standard chart types. Accepted: `vega-lite`, `plotly`, `echarts`. Default: `vega-lite`. |
| `allowedChartTypes` | Chart types the Visualisation Ontology may select for this tenant. Restricting this set enforces consistency across analytical outputs. |
| `colorPalette` | Named colour scheme for chart series. Platform-provided options: `categorical_financial`, `sequential_blue`, `diverging_red_green`, `monochrome`. |
| `numberFormat` | Default number formatting applied to all metric values in visualisations and narrative synthesis. |
| `thresholds.maxDataPoints` | Maximum data points returned to the visualisation layer. Queries exceeding this threshold trigger the governance circuit breaker. |
| `thresholds.maxSeriesPerChart` | Maximum chart series. Queries resolving more series trigger automatic aggregation by the FQP. |
| `customRenderers` | Host-registered domain-specific visualisation renderers, loaded as ES modules. |

---

## `drilldown`

Configures the governed drilldown behaviour — how users and AI agents traverse analytical hierarchies.

```json
{
  "drilldown": {
    "enabled":           true,
    "maxDepth":          4,
    "allowedHierarchies": ["asset_class_hierarchy", "geography_hierarchy", "time_hierarchy", "organisational_hierarchy"],
    "requireConfirmation": false,
    "preserveFilters":   true
  }
}
```

| Field | Description |
|-------|-------------|
| `enabled` | Whether governed drilldown is available in this tenant. Default: `true`. |
| `maxDepth` | Maximum levels of hierarchy traversal per analytical session. Prevents runaway recursive queries. Default: `4`. |
| `allowedHierarchies` | Hierarchy IDs (defined in the SMR) that drilldown may traverse. Hierarchies not listed here cannot be traversed interactively. |
| `requireConfirmation` | When `true`, the platform presents a drilldown confirmation step before traversing. Default: `false`. |
| `preserveFilters` | Whether parent-level filters carry forward to child levels during drilldown. Default: `true`. |

---

## `governance`

Configures the Semantic Execution Governance layer for this tenant.

```json
{
  "governance": {
    "maxQueryCostUnits":          1000,
    "maxConcurrentQueries":       5,
    "queryTimeoutSeconds":        60,
    "classificationGating":       true,
    "blockedClassifications":     ["TOP_SECRET", "RESTRICTED"],
    "requireLineageForExport":    true,
    "auditAllQueries":            true,
    "complianceMode":             "mifid2"
  }
}
```

| Field | Description |
|-------|-------------|
| `maxQueryCostUnits` | Maximum estimated cost units for a single analytical query. Queries exceeding this limit are blocked and the user is prompted to narrow scope. |
| `maxConcurrentQueries` | Per-user concurrency limit. Default: `5`. |
| `queryTimeoutSeconds` | Maximum execution time before the FQP cancels the query. Default: `60`. |
| `classificationGating` | When `true`, data classification metadata is evaluated before execution — queries touching data at or above `blockedClassifications` are blocked. Default: `true`. |
| `blockedClassifications` | Data classification labels that block query execution. Sourced from the host's data classification taxonomy. |
| `requireLineageForExport` | When `true`, analytical results cannot be exported until the lineage record is fully written. Default: `true`. |
| `auditAllQueries` | When `true`, every query — including those that fail governance checks — is written to the audit trail. Default: `true`. |
| `complianceMode` | Named compliance profile that pre-configures governance defaults. Accepted: `mifid2`, `basel3`, `aifmd`, `sec_reg_bi`, `mas_faa`, `custom`. |

---

## `models`

```json
{
  "models": {
    "intentResolutionModel": "standard",
    "narrativeSynthesisModel": "standard",
    "allowedModels":          ["standard", "powerful"],
    "provider":               "anthropic"
  }
}
```

| Field | Description |
|-------|-------------|
| `intentResolutionModel` | Model tier used for semantic intent resolution (mapping natural language to analytical intent). Default: `standard`. |
| `narrativeSynthesisModel` | Model tier used for narrative synthesis. May differ from intent resolution — more complex narratives may warrant the `powerful` tier. Default: `standard`. |
| `allowedModels` | Model tiers available for this tenant. |
| `provider` | AI provider identifier. |

---

## `features`

```json
{
  "features": {
    "naturalLanguageQuery":    true,
    "governedDrilldown":       true,
    "narrativeSynthesis":      true,
    "exportResults":           true,
    "lineageInspector":        true,
    "intentConfirmation":      false,
    "benchmarkComparison":     true,
    "regulatoryReporting":     false,
    "starterQuestions": [
      "What is the portfolio return versus benchmark for the current quarter?",
      "Show me issuer concentration risk across all portfolios.",
      "Which portfolios have VaR exceeding their limit today?"
    ]
  }
}
```

| Flag | Default | Description |
|------|---------|-------------|
| `naturalLanguageQuery` | `true` | Enable natural language intent resolution |
| `governedDrilldown` | `true` | Enable hierarchy traversal |
| `narrativeSynthesis` | `true` | Enable LLM-generated prose anchored to results |
| `exportResults` | `true` | Enable result export (CSV, JSON, PDF) |
| `lineageInspector` | `true` | Enable the lineage trail inspector UI |
| `intentConfirmation` | `false` | Require user confirmation before plan execution |
| `benchmarkComparison` | `true` | Enable benchmark dimension access |
| `regulatoryReporting` | `false` | Enable regulatory metric domain (requires appropriate role) |
| `starterQuestions` | `[]` | Suggested analytical questions shown on the onboarding screen (up to 3) |

---

## Config validation

Submitting a config via the Admin API runs synchronous validation before applying:

| Check | Description |
|-------|-------------|
| Schema conformance | All required fields present; field types match schema |
| Execution engine reachability | Engine endpoints respond to a health check |
| Role claim field presence | `entitlements.roleClaimField` resolvable from test JWT |
| Metric access references | All metric IDs in role `metricAccess` arrays must exist in the seeded SMR or be declared as custom metrics |
| Hierarchy references in drilldown | All `allowedHierarchies` IDs must be defined in the SMR |
| Governance mode compatibility | `complianceMode` values compatible with `regulatoryJurisdiction` |
| Custom renderer reachability | Each `moduleUrl` must respond to a HEAD request |
| System prompt token count | Must be under 3,000 tokens |

Validation errors return a structured response with field-level detail. Config is not applied until all checks pass.
