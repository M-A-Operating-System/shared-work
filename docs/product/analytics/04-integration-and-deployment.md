# 4. Integration and Deployment

This chapter covers the complete integration surface of the AI Analytics Platform: how consumers authenticate and call it, how platform administrators configure it, the financial services reference model it ships with, and the complementary ecosystem services that extend its capabilities. The platform is deliberately narrow in its external interface: a single MCP endpoint governs all consumer access, and a single Admin API governs all configuration. Complexity lives inside the governance pipeline, not in the integration contract.

Component specifications (SMR, SIL, RAPL, SEG, FQP, VO, NSE, Lineage Store) are in [Chapter 3 — Core Platform Capabilities](./03-core-capabilities.md). The reference implementation stack is in [Chapter 5 — Proposed Technical Implementation](./05-technical-implementation.md).

---

## 4.1 Consumer Integration

The AI Analytics Platform is consumed exclusively via its MCP Capability Layer, exposed at a single endpoint:

```
POST https://api.analytics-platform.io/v1/mcp
Authorization: Bearer <host-issued-JWT>
Content-Type: application/json
```

There is no embeddable component, no client-side SDK, and no rendering layer. Any MCP-compatible consumer (a conversational AI assistant, an autonomous agent, a report pipeline, or a custom application) integrates identically. The platform is headless by design: it returns structured JSON results and display specifications; rendering is the consumer's responsibility.

### Authentication

Every request must carry a host-issued JWT in the `Authorization: Bearer <token>` header. The platform validates the JWT at the authentication boundary before any analytical processing begins. Expired tokens are rejected immediately. Tokens with no matching analytical role receive an `ENTITLEMENT_DENIED` error, or are served a public-access metric set if `defaultDenyAll: false` is configured.

**Required JWT claims**

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User's unique identifier within the tenant |
| `tenant_id` | string | Must match the tenant's registered `tenantId` |
| `exp` | number | JWT expiry timestamp |
| Any field matching `entitlements.roleClaimField` | `string[]` | Analytical role array — consumed by the Role-Aware Projection Layer to determine metric, dimension, and row-level access |

**Optional analytical claims**

| Claim | Type | Description |
|-------|------|-------------|
| `managed_portfolios` | `string[]` | Portfolio IDs managed by this user — resolved in row predicate templates |
| `entity_ids` | `string[]` | Legal entities the user is associated with |
| `display_name` | string | User's display name for lineage records and audit trail |
| Any claim referenced in role `rowPredicates` | any | Any value referenced by `{{user.claim_name}}` in predicate templates |

JWTs expire per the consuming application's standard session policy. When a token approaches expiry, the consuming application issues a refreshed JWT and includes it in the next request header. No platform-side re-authentication step is required. For long-running agentic consumers, the host must supply fresh JWTs before each preceding token's `exp` timestamp.

### Response Structure

A successful response returns a JSON object containing the result record, a display specification, an optional narrative, and execution metadata:

```json
{
  "result_id":   "res_20260514_093247_a1b2c3",
  "lineage_url": "https://api.analytics-platform.io/v1/lineage/res_...",
  "display_spec": {
    "type": "chart" | "table",
    "..."
  },
  "narrative": { "lead": "...", "detail": "...", "anchoredTo": ["..."] },
  "meta": {
    "latencyMs": 1285,
    "cacheHit":  false,
    "rowCount":  14,
    "costUnits": 500
  }
}
```

Consumers branch on `display_spec.type`. A value of `"chart"` indicates a Semantic Charting Language specification. The consumer renders it using a chart grammar library of its choosing, consuming the `mark`, `data.values`, `encoding`, `colorScheme`, and `formatHints` fields. A value of `"table"` indicates a data grid specification. The consumer renders it with `columns` (including labels and format hints), `data`, and optional `thresholds` for cell highlighting. The platform governs which contract is selected and how it is parameterised; the consumer governs how it is rendered. The `narrative` field is present when `features.narrativeSynthesis` is enabled and the result meets the synthesis threshold. Consumers may surface `narrative.lead` and `narrative.detail` as prose or pass them to a downstream document assembly pipeline. The `meta` field is available for consumer telemetry.

### Drilldown Continuity

When a consumer receives a result containing a `result_id`, it may pass that identifier to the `drilldown` tool to traverse analytical hierarchies without re-specifying the original query:

```json
{
  "tool": "drilldown",
  "input": {
    "result_id":      "res_20260514_093247_a1b2c3",
    "hierarchy":      "asset_class_hierarchy",
    "selected_value": "EQUITY"
  }
}
```

The platform retrieves the original result's projection scope, role filters, and entitlement context from the Analytical Lineage Store and applies them to the drilldown query. The consumer does not re-specify query parameters, dimensions, or time periods. Governance context is fully preserved across the drill chain.

### Error Handling

All errors return a structured response with `result_id` always present. This ensures every request, successful or not, appears in the audit trail and is reachable via the lineage API:

```json
{
  "error": {
    "code":      "GOVERNANCE_COST_EXCEEDED",
    "message":   "Estimated cost 1,400 units exceeds limit 1,000. Narrow the query scope.",
    "result_id": "res_20260514_094002_b3c4d5"
  }
}
```

The `message` field is human-readable and suitable for surfacing directly to end users or agentic decision loops.

### Agentic Consumers

Autonomous agents (scheduled pipelines, event-triggered monitors, report generators) integrate identically to interactive consumers. The host must provision service-level JWTs for agents, scoped to the agent's role rather than a user's identity. The Role-Aware Projection Layer applies identical entitlement enforcement to agent JWTs as to user JWTs. An agent cannot access data that a user with the same role cannot access. Every agent-initiated request is recorded in the Analytical Lineage Store under the agent's `sub` claim, making agent queries distinguishable from user queries via the audit trail.

### vite2img (Optional Rendering Service)

vite2img is a standalone MCP render service that may be registered directly with consumers as a peer MCP server, alongside the Analytics Platform. It accepts `display_spec` JSON and returns SVG or PNG. It is not part of the Analytics Platform and carries no governance or lineage obligations. It is a rendering utility for consumers that require image output rather than a chart grammar payload.

---

## 4.2 Platform Administration

Platform configuration is managed via the **Platform Admin API**, authenticated by a platform administrator credential. A web-based **Admin Console** provides a visual interface over the same API surface, suitable for administrators who prefer not to work with the API directly. All configuration changes made via the Admin Console are identical in effect to the corresponding API calls and appear in the platform audit log.

### Data Source Registration

Execution backends are registered in the Data Source Catalog via the Admin API. Each registration declares the backend's type, endpoint, authentication method, capabilities, and the logical data domains it serves. The Federated Query Planner uses this catalog to route sub-plans to the correct backend for each metric resolution.

```json
{
  "executionBackends": [
    {
      "id": "primary-warehouse", "name": "Primary Data Warehouse",
      "type": "sql_warehouse",
      "endpoint": "https://internal.api/analytics/backends/warehouse",
      "authType": "service-account",
      "capabilities": ["aggregate", "filter", "join", "window", "timeseries"],
      "dataAffinity": ["portfolio", "positions", "transactions", "benchmarks"],
      "priority": 1, "costTier": "standard", "enabled": true
    },
    {
      "id": "risk-semantic-layer", "name": "Risk Metrics Semantic Layer",
      "type": "semantic_layer",
      "endpoint": "https://internal.api/analytics/backends/risk",
      "authType": "service-account",
      "capabilities": ["metric", "dimension", "filter"],
      "dataAffinity": ["risk_metrics", "performance_attribution"],
      "priority": 1, "costTier": "low", "enabled": true
    }
  ]
}
```

**Backend registration fields**

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Backend adapter class: `sql_warehouse`, `opendata_api`, `graph_api`, `semantic_layer`, `olap_engine`, `custom` |
| `authType` | Yes | Authentication mode: `service-account` (platform-held credential), `api-key`, or `bearer` (forwards the calling user's JWT to the backend) |
| `dataAffinity` | Yes | Logical data domains this backend serves — the FQP routes sub-plans whose metric `data.domain` matches one of these values |
| `capabilities` | Yes | Operations the FQP may route to this backend: `aggregate`, `filter`, `join`, `window`, `timeseries`, `metric`, `traverse` |
| `costTier` | No | Relative execution cost: `minimal`, `low`, `standard`, `high`, `unrestricted` — used by the governance circuit breaker when estimating query cost |

Multiple backends may share the same `dataAffinity` value; the FQP selects among them based on `priority`, `capabilities`, and backend availability. If a backend declares `authType: "bearer"`, the user's own JWT is forwarded. Entitlement enforcement at the backend layer is then the consuming system's responsibility, and the platform's row-level predicate injection still applies upstream.

### Governance Settings

The governance block controls the circuit breakers and compliance mode applied to every query before execution:

```json
{
  "governance": {
    "maxQueryCostUnits": 1000,
    "maxConcurrentQueries": 5,
    "queryTimeoutSeconds": 60,
    "classificationGating": true,
    "blockedClassifications": ["TOP_SECRET", "RESTRICTED"],
    "requireLineageForExport": true,
    "auditAllQueries": true,
    "complianceMode": "mifid2"
  }
}
```

| Field | Description |
|-------|-------------|
| `maxQueryCostUnits` | Maximum estimated cost units a single query may consume. Queries whose estimated cost exceeds this value are blocked before execution. |
| `maxConcurrentQueries` | Maximum concurrent queries per user. Excess queries are held until a slot becomes available or the timeout budget is reached. |
| `queryTimeoutSeconds` | Maximum wall-clock time permitted for a single query's execution across all backends. |
| `classificationGating` | When `true`, queries involving metrics whose `data.classification` appears in `blockedClassifications` are rejected before execution. |
| `blockedClassifications` | List of classification labels that trigger blocking when `classificationGating` is enabled. |
| `requireLineageForExport` | When `true`, result export operations require a complete lineage record. Exports of results with incomplete lineage are blocked. |
| `auditAllQueries` | When `true`, every query — including governance-blocked and authentication-failed requests — is written to the audit log. Platform-recommended setting is `true`. |
| `complianceMode` | Activates compliance-specific behaviour: `mifid2` logs all queries involving client-related metrics; additional modes for `basel3` (covering both Basel III and the Basel IV final reforms), `aifmd`, and `esg_sfdr` are available. |

### Operational Settings

The scope, model, and feature blocks configure the platform's analytical domain, narrative synthesis model selection, and feature set:

```json
{
  "scope": {
    "analyticalDomain": "wealth_management",
    "regulatoryJurisdiction": "UK",
    "requiresIntentConfirmation": false
  },
  "models": {
    "narrativeSynthesisModel": "fast"
  },
  "features": {
    "naturalLanguageQuery": true, "governedDrilldown": true, "narrativeSynthesis": true,
    "resultDownload": true, "intentConfirmation": false, "benchmarkComparison": true,
    "regulatoryReporting": false
  }
}
```

`analyticalDomain` scopes the SMR seed template to the configured domain. `regulatoryJurisdiction` influences compliance mode defaults and regulatory threshold sourcing. When `requiresIntentConfirmation` is `true`, the platform returns a confirmation card to the consumer before executing any query. This is appropriate for high-stakes or irreversible analytical operations. The `models` block selects between available inference tiers for the Narrative Synthesis Engine: `"fast"` maps to Claude Haiku and reduces latency, `"standard"` maps to Claude Sonnet and is the balanced default for complex queries. Intent resolution is performed by the consuming AI client and is not configured here. Individual features in the `features` block may be toggled without affecting the governance pipeline. Disabling `narrativeSynthesis`, for example, removes the narrative field from responses but has no effect on lineage, entitlement enforcement, or result computation.

### SMR Administration Settings

The `metricRegistry` block configures governance over the Semantic Metrics Registry itself:

```json
{
  "metricRegistry": {
    "seedTemplate": ["wealth_management", "risk_management"],
    "approvalRequired": true,
    "ownershipRequired": true,
    "versionControl": true,
    "fiscalYearStartMonth": 1
  }
}
```

`seedTemplate` specifies one or more reference model domains to seed into the SMR at initialisation (see the Financial Services Reference Model section below). `approvalRequired` gates all new and modified metric definitions behind an Application Admin approval step before they become resolvable. `ownershipRequired` mandates that every metric definition carries an assigned owner. Unowned definitions cannot be promoted to `approved` status. `versionControl` enables automatic semantic versioning of all SMR definitions; changes that modify a metric's formula, dimension bindings, or data domain increment the definition's version and preserve the prior version in history. `fiscalYearStartMonth` sets the fiscal calendar anchor for time-relative metric expressions such as `YTD` and `FY`.

### Registration Validation

On submission of a backend registration or governance configuration change, the Admin API performs a set of validation checks before accepting the record:

| Validation | Description |
|------------|-------------|
| Backend reachability | The platform issues a connectivity probe to the registered `endpoint` and confirms it responds within the configured timeout |
| Data affinity consistency | Each value in `dataAffinity` is checked against the known logical domain registry — unrecognised domain labels generate a warning |
| Role claim field | The `entitlements.roleClaimField` value is verified to be a non-empty string; the Admin Console surfaces a warning if no issued JWT in the last 30 days contained that claim |
| Metric access references | Any metric definition referencing a backend via `data.domain` is checked for affinity alignment — a metric whose domain has no matching backend generates a resolution warning |
| Compliance mode compatibility | Where `complianceMode` is set, the platform verifies that the `regulatoryJurisdiction` and `blockedClassifications` configuration is consistent with the compliance mode's requirements |

Validation warnings do not block registration. They are surfaced in the Admin Console and available via the Admin API response. Validation errors (unreachable endpoint, invalid schema) block the registration until resolved.

---

## 4.3 Financial Services Reference Model

The platform ships with a pre-built **Financial Services Reference Model**: a curated set of metric definitions, dimension schemas, hierarchy definitions, and measure group collections covering the most common financial services analytical domains. Platform administrators activate the reference model by specifying one or more domain values in the `metricRegistry.seedTemplate` configuration field. Seeding occurs at initial platform setup and may be repeated after updates.

The reference model covers six primary domains:

| Domain | Key metrics | Typical consumers |
|--------|-------------|-------------------|
| **Wealth management** | Portfolio return, tracking error, Sharpe ratio, benchmark return, active return, information ratio | Portfolio managers, private bankers |
| **Risk management** | VaR 95/99, expected shortfall, beta, duration, convexity, issuer concentration | Risk officers, investment committees |
| **Performance attribution** | Brinson attribution, factor attribution, sector attribution, active weight | Portfolio managers, analysts |
| **Regulatory reporting** | LCR, NSFR, leverage ratio, capital ratios, RWA, concentration limits | Compliance teams, regulatory reporting |
| **Banking** | NIM, RWA density, provision coverage, cost-to-income, deposit beta | Finance, treasury, credit risk |
| **ESG** | Carbon intensity, ESG score, engagement coverage, exclusion exposure | Sustainability analysts, client reporting |

All reference model definitions enter the SMR in `proposed` status and require Application Admin approval before they become resolvable. This ensures that no reference definition is served to users before an authorised administrator has confirmed it reflects the organisation's calculation methodology. Approved definitions may subsequently be customised. Modified definitions are marked `source: "tenant"` and increment their version, preserving the original reference definition in version history. Tenant-modified definitions are not overwritten by future reference model updates.

The hierarchies shipped with the reference model (including the asset class hierarchy, geography hierarchy, and time hierarchy) are available for governed drilldown immediately upon approval of the associated dimension definitions.

---

## 4.4 Complementary Ecosystem Services

Three ecosystem services extend the platform's capabilities for financial services deployments. None is a hard dependency for platform operation. The platform functions with any combination of these services present or absent.

| Service | Type | Activation | Primary benefit |
|---------|------|------------|-----------------|
| **Semantic Registry Service** | Config-time resource | `POST /v1/smr/import` with package reference | Accelerated SMR setup from 480+ vetted metric definitions across 6 domain packages |
| **Regulatory Reference Service** | Runtime execution backend | Register in Data Source Catalog (`dataAffinity: ["regulatory"]`) | Authoritative, always-current regulatory metric values and thresholds without internal maintenance |
| **Benchmark Data Service** | Runtime execution backend | Register in Data Source Catalog (`dataAffinity: ["benchmarks"]`) | Licensed benchmark data for comparison queries across equity, fixed income, multi-asset, factor, and custom blend indices |

### Semantic Registry Service

The Semantic Registry Service is a curated, version-controlled library of pre-built metric definitions, dimension schemas, hierarchy definitions, measure group collections, formula documentation, and regulatory mappings. It is primarily a config-time resource: platform administrators use it when establishing their SMR baseline, importing packages via the Admin API rather than authoring definitions from scratch.

The service organises content into six domain packages:

| Package | Domain | Metric count |
|---------|--------|-------------|
| `fsi-wealth-v1` | Wealth management and private banking | 85 metric definitions |
| `fsi-investment-v1` | Institutional investment management | 120 metric definitions |
| `fsi-banking-v1` | Retail and wholesale banking | 95 metric definitions |
| `fsi-risk-v1` | Cross-domain risk management | 75 metric definitions |
| `fsi-regulatory-v1` | Regulatory reporting (Basel III/IV, MiFID II, AIFMD) | 60 metric definitions |
| `fsi-esg-v1` | ESG and sustainable investment metrics | 45 metric definitions |

Each package is imported via a single Admin API call referencing the package identifier and version. Imported definitions enter the SMR as `proposed` and follow the normal approval workflow. Administrators may modify imported definitions before or after approval. Modifications are tracked under `source: "tenant"`. When the Semantic Registry Service publishes an updated package version, administrators receive a notification and may selectively import the delta.

The `seedTemplate` configuration field seeds the SMR from a snapshot of the relevant Semantic Registry Service package pre-bundled at platform installation. The live Semantic Registry Service provides the most current definitions and access to packages beyond the core seed templates.

### Regulatory Reference Service

The Regulatory Reference Service is a runtime execution backend registered in the Data Source Catalog with `dataAffinity: ["regulatory"]`. Once registered, the Federated Query Planner routes all sub-plans carrying metrics whose `data.domain` is `regulatory` to the service. This ensures that threshold values for LCR, NSFR, leverage ratio, capital ratios, and equivalent metrics are always sourced from the authoritative service rather than from host-maintained tables that may lag regulatory publication schedules.

The service holds current threshold values for each registered regulatory regime, jurisdiction-specific where required, and publishes update notifications to registered tenants when threshold values change, for example when a jurisdiction's minimum LCR is revised or a Basel IV transition date is confirmed. If the Regulatory Reference Service is unavailable, the FQP falls back to the next registered backend with `regulatory` data affinity; if no fallback is configured, regulatory sub-plans fail with a structured error. The platform does not fabricate regulatory threshold values when the authoritative source is unavailable.

### Benchmark Data Service

The Benchmark Data Service is a runtime execution backend registered in the Data Source Catalog with `dataAffinity: ["benchmarks"]`. It provides market index and benchmark data across equity indices (MSCI World, MSCI ACWI, S&P 500, FTSE All-World), fixed income indices (Bloomberg Global Aggregate, ICE BofA Investment Grade), multi-asset indices, factor indices (MSCI Minimum Volatility, Value, Quality, Momentum), and administrator-configured custom benchmark blends.

The service operates under data licensing agreements with index providers. Tenants confirm their licensing entitlement per index. The service enforces licensing checks at the tenant level and blocks access to benchmarks for which the tenant has not confirmed entitlement. Custom benchmark blends may be configured by the platform administrator via the Benchmark Data Service Admin API, specifying component benchmark identifiers and weights; blended benchmarks are then accessible within queries using their registered identifier and subject to the same entitlement enforcement as component indices.
