# 17 — Proposed Technical Architecture

One reference implementation of the AI Analytics Platform. Stack choices are concrete but not prescriptive — the product specification is intentionally stack-agnostic. Any conformant implementation that satisfies the specified behaviours, governance guarantees, and interface contracts is valid. Technology substitutions at any layer require no changes to the product spec.

This document assumes the existence of a **Semantic Data Context Store (DCS)** — a pre-existing platform component that maintains the authoritative store of semantic definitions across the organisation. The Analytics Platform extends the DCS to also manage analytical metric definitions, making the DCS the single authoritative source for the SMR rather than introducing a separate definition store.

---

## Architecture overview

```mermaid
flowchart TD
    Consumer["Consumer\nAI Chat Platform · autonomous agent · custom application"]

    subgraph analytics["AI Analytics Platform"]
        MCP["MCP Capability Layer\nCloudflare Workers · MCP Streamable HTTP"]
        SIL["Semantic Intent Layer\nAnthropic Claude · Sonnet / Opus"]
        RAPL["Role-Aware Projection Layer\nCustom middleware · TypeScript"]
        AIV["Analytical Intent Validator\nJSON schema + SMR resolution → LQP · TypeScript"]
        SEG["Semantic Execution Governance\nCost estimation · classification · circuit breakers"]
        FQP["Federated Query Planner\nApache Calcite + backend adapters"]
        VO["Visualisation Ontology\nSCL generation · Vega-Lite v5"]
        NSE["Narrative Synthesis Engine\nAnthropic Claude · Haiku / Sonnet"]
        LS[("Analytical Lineage Store")]
        Result(["MCP tool response\ndisplay_spec + narrative + result_id"])
    end

    vite2img["vite2img (optional)\nStandalone MCP render service · SCL → SVG / PNG\nRegistered directly with consumers — not part of Analytics Platform"]

    subgraph dcr["Data Context Repository"]
        SMC["Semantic Metrics Context\nGovernance workflow + metric schema · extends DCS"]
        DCS[("Semantic Data Context Store\nPre-existing · general-purpose common registry")]
        SMC -. backed by .-> DCS
    end

    subgraph backends["Execution Backends"]
        SQL["SQL Warehouse\nSnowflake · BigQuery · Databricks · Starburst"]
        ODA["OpenData API\nREST / OData"]
        GDA["Graph Data API\nNeo4j · Neptune / SPARQL"]
    end

    Consumer -->|"POST /v1/mcp (JWT + MCP tool call)"| MCP
    Consumer -->|"MCP tool call + user JWT"| vite2img
    MCP -->|"natural language query"| SIL
    MCP -->|"JWT claims"| RAPL
    SIL -->|"metric name resolution"| SMC
    SIL -->|"structured intent"| AIV
    RAPL -->|"row predicates + column masks"| AIV
    AIV -->|"metric + dimension validation"| SMC
    AIV -->|"Logical Query Plan"| SEG
    SEG -->|"approved LQP"| FQP
    SEG -->|"governance decision"| LS
    FQP -->|"physicalMapping lookup"| SMC
    FQP --> SQL & ODA & GDA
    FQP -->|"execution record"| LS
    FQP -->|"assembled result"| VO
    FQP -->|"assembled result"| NSE
    VO -->|"SCL display spec"| Result
    NSE -->|"narrative"| Result
```

---

## Pre-existing components

### Semantic Data Context Store (DCS)

The DCS is a pre-existing, general-purpose platform component — not built or owned by the Analytics Platform. It is the organisation's common registry for semantic definitions of all kinds: data entities, data products, business glossary terms, domain concepts, and data source schemas. The Analytics Platform reuses the DCS as the authoritative store for analytical metric definitions, registering them as a new definition type (`analytical_metric`) alongside the data definitions already managed there. This avoids a parallel semantic registry and keeps metric definitions discoverable alongside the data they describe.

| Capability provided by DCS | How the Analytics Platform uses it |
|---------------------------|-----------------------------------|
| Versioned definition document storage | Metric definitions stored as `type: "analytical_metric"` documents, versioned by the DCS natively |
| Full-text search and fuzzy discovery | `list_metrics` MCP capability queries the DCS search index; no separate Elasticsearch needed |
| Cross-definition relationships | Dimensions, entities, and benchmarks referenced by metric definitions resolve as DCS entity links to existing data definitions |
| Tenant-scoped access control | DCS enforces tenant isolation on all definition reads and writes |

The SMR layer adds what the DCS does not natively provide: the **governance workflow** (proposed → approved → deprecated), **metric-specific schema validation** (formula, physicalMapping, costWeight), and the **Admin API surface** for metric authoring. When a metric transitions to `approved`, the canonical definition is written to the DCS. At query time, the Analytical Intent Validator reads definitions directly from the DCS.

#### DCS extension schema (governance tracking — platform-owned PostgreSQL)

The platform maintains a lightweight governance tracking table alongside the DCS. This table holds workflow state and approval metadata that the DCS does not natively manage; the DCS holds the definition document itself.

```sql
CREATE TABLE analytics.smr_governance (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     TEXT        NOT NULL,
  dcs_def_id    TEXT        NOT NULL,  -- DCS definition document ID
  metric_id     TEXT        NOT NULL,  -- stable identifier, e.g. "portfolio_return"
  version       INT         NOT NULL,
  status        TEXT        NOT NULL,  -- "proposed" | "approved" | "deprecated"
  source        TEXT        NOT NULL DEFAULT 'tenant',  -- "reference" | "tenant"
  created_by    TEXT        NOT NULL,
  approved_by   TEXT,
  approved_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  superseded_at TIMESTAMPTZ,
  CONSTRAINT uq_smr_version UNIQUE (tenant_id, metric_id, version)
);

-- One approved version per metric per tenant at any time
CREATE UNIQUE INDEX idx_smr_one_approved
  ON analytics.smr_governance (tenant_id, metric_id)
  WHERE status = 'approved';
```

#### Metric definition document (stored in DCS as `type: "analytical_metric"`)

```json
{
  "dcsType":     "analytical_metric",
  "metricId":    "portfolio_return",
  "version":     2,
  "displayName": "Portfolio Return",
  "description": "Time-weighted return for the portfolio over the selected period, expressed as a percentage.",
  "category":    "performance",
  "dataAffinity": ["portfolio"],
  "formula": {
    "type":        "time_weighted_return",
    "inputs":      ["daily_return", "market_value"],
    "aggregation": "chain_link"
  },
  "dimensions": [
    { "id": "portfolio",   "required": true  },
    { "id": "date",        "required": true  },
    { "id": "asset_class", "required": false },
    { "id": "currency",    "required": false }
  ],
  "timePeriods": ["day","week","month","quarter_to_date","year_to_date","trailing_12m"],
  "physicalMapping": {
    "backendId":   "snowflake-primary",
    "table":       "fact_portfolio_daily",
    "valueColumn": "portfolio_return",
    "dateColumn":  "price_date",
    "joinKeys":    { "portfolio": "portfolio_id" }
  },
  "formatting": { "unit": "percent", "decimalPlaces": 2, "suffix": "%" },
  "governance": {
    "costWeight":          1.0,
    "classificationLevel": "internal",
    "entitledRoles":       ["portfolio_manager", "analyst", "risk_officer"],
    "complianceNotes":     "For MiFID II cost disclosure use cost_adjusted_return."
  },
  "narrativeTemplate": "{{portfolio_name}} returned {{value}}% {{period_label}}, {{direction}} its benchmark by {{tracking_error}}%.",
  "aliases": ["return", "twr", "portfolio_twr"],
  "tags":    ["performance", "core", "reference-model"]
}
```

`governance.costWeight` feeds the Semantic Execution Governance estimator: `estimated_cost = Σ(metric.costWeight × dimensionCardinality × timeRangeMultiplier)`.

---

## Layer-by-layer stack decisions

### Platform Admin API

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Runtime** | Node.js (Express / Fastify) on Kubernetes | Low-frequency, latency-tolerant operations; standard service pattern suits complex admin workflows better than edge deployment |
| **Auth** | JWT with `platform_admin` or `app_admin` role claim | Reuses platform JWT infrastructure; validated at API gateway |
| **API style** | REST (JSON) | Admin operations map cleanly to CRUD on named resources |
| **Data store** | PostgreSQL (shared primary database) | Co-located with lineage store and SMR; shared RLS tenant isolation |

| Alternative | Why not chosen |
|------------|---------------|
| Cloudflare Workers | Long-running validations (SMR consistency checks) exceed Workers CPU budget |
| Separate admin database | Unnecessary — admin and operational state share the same RLS model |
| GraphQL | No benefit over REST CRUD for these resource patterns |

---

### Admin Console

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | React + TypeScript (SPA) | Rich ecosystem for YAML editors, form handling, and data tables |
| **Hosting** | CDN (Cloudflare Pages or S3 + CloudFront) | No SSR requirement |
| **YAML editor** | Monaco Editor | VS Code engine; built-in YAML validation; familiar to SMR authors |
| **Auth** | Same JWT as Platform Admin API | No separate session management |

| Alternative | Why not chosen |
|------------|---------------|
| Next.js | SSR not required |
| Low-code admin builder (Retool, AdminJS) | Insufficient control over SMR editor and governance config workflows |

---

### Data Source Catalog

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Storage** | PostgreSQL (`analytics.execution_backends`) | Strongly-typed; shares RLS tenant isolation |
| **Runtime access** | In-memory cache in FQP (refreshed on `CATALOG_UPDATED` message queue event) | Eliminates per-query database round-trips |
| **Change propagation** | `CATALOG_UPDATED` published by Admin API on any catalog change | Decouples Admin API from FQP |

#### `analytics.execution_backends` (DDL)

```sql
CREATE TABLE analytics.execution_backends (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      TEXT        NOT NULL,
  backend_id     TEXT        NOT NULL,  -- e.g. "snowflake-primary"
  display_name   TEXT        NOT NULL,
  backend_type   TEXT        NOT NULL,  -- "sql_warehouse" | "semantic_layer" | "opendata_api" | "graph_api" | "olap_engine" | "custom"
  data_affinity  TEXT[]      NOT NULL,  -- e.g. ARRAY['portfolio','performance']
  priority       INT         NOT NULL DEFAULT 100,  -- lower = higher priority
  config         JSONB       NOT NULL,  -- credentials stored as secret_ref pointers only
  enabled        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_backend_per_tenant UNIQUE (tenant_id, backend_id)
);

CREATE INDEX idx_backends_affinity ON analytics.execution_backends USING GIN (data_affinity);
```

#### Backend registration (Admin API `POST /v1/backends`)

```json
{
  "backendId":    "snowflake-primary",
  "displayName":  "Snowflake Production Warehouse",
  "backendType":  "sql_warehouse",
  "dataAffinity": ["portfolio", "performance", "risk"],
  "priority": 10,
  "config": {
    "dialect":    "snowflake",
    "account":    "myorg.us-east-1",
    "database":   "ANALYTICS_DB",
    "schema":     "FACT",
    "warehouse":  "COMPUTE_WH",
    "role":       "ANALYTICS_READ",
    "secret_ref": "vault://analytics/backends/snowflake-primary"
  }
}
```

The FQP filters by `data_affinity @> ARRAY[requiredAffinity]` and selects the lowest-priority healthy backend at query time.

---

### MCP Capability Layer

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Runtime** | Cloudflare Workers | Sub-10ms cold start; global anycast |
| **Protocol** | MCP Streamable HTTP | Standard MCP interoperability; supports request/response and streaming |
| **Auth** | JWT validation at edge | Stateless; validated before any platform computation |

| Alternative | Why not chosen |
|------------|---------------|
| AWS Lambda + API Gateway | Higher cold start; regional by default |
| Fastly Compute@Edge | Viable; less mature ecosystem |
| Traditional Node.js server | Operational overhead; wrong pattern for an edge API |

#### `analyse_metric` input JSON schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "analyse_metric input",
  "type": "object",
  "required": ["metrics"],
  "additionalProperties": false,
  "properties": {
    "metrics":    { "type": "array", "items": { "type": "string" }, "minItems": 1, "maxItems": 10 },
    "dimensions": { "type": "array", "items": { "type": "string" } },
    "time": {
      "type": "object",
      "properties": {
        "period":     { "type": "string", "enum": ["today","week_to_date","month_to_date","quarter_to_date","year_to_date","trailing_12m","trailing_36m","custom"] },
        "as_of_date": { "type": "string", "format": "date" },
        "from":       { "type": "string", "format": "date" },
        "to":         { "type": "string", "format": "date" }
      }
    },
    "filters": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["dimension", "operator", "values"],
        "properties": {
          "dimension": { "type": "string" },
          "operator":  { "type": "string", "enum": ["in","not_in","eq","gt","lt","gte","lte"] },
          "values":    { "type": "array" }
        }
      }
    },
    "sort": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["metric", "direction"],
        "properties": {
          "metric":    { "type": "string" },
          "direction": { "type": "string", "enum": ["asc","desc"] }
        }
      }
    },
    "limit": { "type": "integer", "minimum": 1, "maximum": 1000, "default": 100 }
  }
}
```

---

### Semantic Intent Layer

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Provider** | Anthropic Claude | Strong instruction following and tool-use reliability for constrained analytical domains |
| **Intent resolution** | Sonnet | Good speed/accuracy balance for metric name resolution |
| **Complex queries** | Opus | Multi-metric attribution and ambiguous intent |

| Alternative | Why not chosen |
|------------|---------------|
| OpenAI GPT-4o | Viable; Anthropic preferred for instruction-following quality in governed contexts |
| Google Gemini | Viable; GCP integration complexity |
| Fine-tuned domain model | High maintenance cost; prompt-based injection preferred |

---

### Semantic Metrics Registry (SMR)

The SMR is the Analytics Platform's governed catalogue of all resolvable analytical concepts — what metrics can be queried, how they are computed, what dimensions are permissible, and who owns each definition. It is not a standalone store: definition documents live in the DCS, and the SMR is the governance and administration layer on top of it.

#### What a metric semantic definition contains

Each metric definition registered in the DCS captures the full semantic contract for that metric:

| Field group | Purpose |
|-------------|---------|
| **Identity** — `metricId`, `displayName`, `description`, `aliases`, `tags` | Stable identifier, human-readable labels, and search terms used by the Semantic Intent Layer for name resolution |
| **Formula** — `formula.type`, `formula.inputs`, `formula.aggregation` | The computation rule (time-weighted return, ratio, standard deviation, etc.) — what the metric means, independent of any backend |
| **Dimensions** — `dimensions[]` with `required` flag | Which groupings the metric supports; required dimensions are enforced by the Analytical Intent Validator |
| **Time periods** — `timePeriods[]` | Which time granularities the metric can be resolved at |
| **Physical mapping** — `physicalMapping` | How the formula maps to a specific backend: which `backendId`, table, column, date column, and join keys to use. Resolved by the FQP; never exposed to AI or consumers |
| **Formatting** — `unit`, `decimalPlaces`, `suffix` | How values should be presented — passed through to the SCL display spec |
| **Governance** — `costWeight`, `classificationLevel`, `entitledRoles`, `complianceNotes` | Controls query cost estimation, access control, and compliance mode routing |
| **Narrative template** | A parameterised prose template used by the Narrative Synthesis Engine when summarising this metric |

The full definition document structure is shown in the [Pre-existing components — DCS](#semantic-data-context-store-dcs) section above.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Definition storage** | DCS (pre-existing) | Metric definitions live alongside data definitions in the common registry; no duplicate semantic store |
| **Governance tracking** | PostgreSQL (`analytics.smr_governance`) | Lightweight approval workflow state owned by the platform; the DCS does not manage approval workflows |
| **Runtime reads** | Direct DCS API query by Analytical Intent Validator | Definitions read from the authoritative source at resolution time |
| **Search** | DCS native search index | `list_metrics` queries DCS directly; no separate search infrastructure needed |

| Alternative | Why not chosen |
|------------|---------------|
| Standalone PostgreSQL + Elasticsearch | Duplicates DCS capabilities; creates two sources of truth for semantic definitions |
| dbt + Git | Poor UX for business owners; no runtime query path |
| Apache Atlas | Heavy; DCS already fulfils this role |

---

### Financial Services Reference Model

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Packaging** | Versioned YAML bundles (one per domain) | Human-readable; idempotently importable; selective per-domain activation |
| **Distribution** | Bundled at installation; updatable from Semantic Registry Service | Air-gapped deployments supported |
| **Activation** | `analyticalDomain` config triggers SMR import at tenant setup | Bundles import as `proposed`; Application Admin approves before metrics become resolvable |
| **Customisation** | Full edit/override via Admin API after import | Customised definitions marked `source: "tenant"` |

| Alternative | Why not chosen |
|------------|---------------|
| Embedded in binary | YAML is easier to inspect, diff, and update without a rebuild |
| External registry only | Air-gapped deployments need a local snapshot |
| SQL seed scripts | Less portable; YAML re-imports idempotently |

#### Reference model bundle (performance domain, excerpt)

```yaml
# bundles/performance/v1.0.yaml — imports as status: "proposed"
bundle:
  domain:  performance
  version: "1.0"
  metrics:

    - metricId:    portfolio_return
      displayName: Portfolio Return
      description: Time-weighted return over the selected period.
      category:    performance
      dataAffinity: [portfolio]
      formula:
        type: time_weighted_return
        inputs: [daily_return, market_value]
        aggregation: chain_link
      dimensions:
        - { id: portfolio,   required: true  }
        - { id: date,        required: true  }
        - { id: asset_class, required: false }
        - { id: currency,    required: false }
      timePeriods: [day, week, month, quarter_to_date, year_to_date, trailing_12m]
      formatting:  { unit: percent, decimalPlaces: 2, suffix: "%" }
      governance:
        costWeight: 1.0
        classificationLevel: internal
        entitledRoles: [portfolio_manager, analyst, risk_officer]
      aliases: [return, twr, portfolio_twr]
      tags: [performance, core]

    - metricId:    tracking_error
      displayName: Tracking Error
      description: Annualised standard deviation of excess returns relative to benchmark.
      category:    performance
      dataAffinity: [portfolio, benchmarks]
      formula:
        type: annualised_std_dev
        inputs: [active_return]
        window: rolling_252d
      dimensions:
        - { id: portfolio,  required: true }
        - { id: benchmark,  required: true }
        - { id: date,       required: true }
      timePeriods: [trailing_12m, trailing_36m, trailing_60m]
      formatting:  { unit: percent, decimalPlaces: 2, suffix: "%" }
      governance:
        costWeight: 2.0
        classificationLevel: internal
        entitledRoles: [portfolio_manager, analyst, risk_officer]
      aliases: [te, active_risk]
      tags: [performance, risk-adjusted]

    - metricId:    information_ratio
      displayName: Information Ratio
      description: Ratio of annualised active return to tracking error.
      category:    performance
      dataAffinity: [portfolio, benchmarks]
      formula:
        type:        ratio
        numerator:   active_return_annualised
        denominator: tracking_error
      dimensions:
        - { id: portfolio,  required: true }
        - { id: benchmark,  required: true }
        - { id: date,       required: true }
      timePeriods: [trailing_12m, trailing_36m, trailing_60m]
      formatting:  { unit: ratio, decimalPlaces: 2 }
      governance:
        costWeight: 2.5
        classificationLevel: internal
        entitledRoles: [portfolio_manager, analyst]
      aliases: [ir]
      tags: [performance, risk-adjusted]
```

The `risk` domain bundle follows the same structure (`var_95`, `var_99`, `expected_shortfall`, `beta`, `duration`, `convexity`). The `regulatory` bundle (`lcr`, `nsfr`, `leverage_ratio`) uses `classificationLevel: restricted` with regime-specific compliance metadata.

---

### Analytical Intent Validator and LQP Generator

No custom query language. The MCP tool call JSON (metric IDs, dimension IDs, time period, filters) is the analytical intent representation — consistent with Cube.js and MetricFlow conventions. The validator performs JSON schema validation + SMR resolution + LQP generation.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Intent format** | MCP tool call JSON | Standard AI tool-use format; no separate language needed |
| **Implementation** | TypeScript (JSON schema + SMR resolution) | Lightweight; no grammar or parser required |
| **LQP format** | Custom DAG (JSON) | Engine-agnostic across SQL, OpenData, and Graph backends |

| Alternative | Why not chosen |
|------------|---------------|
| Custom textual DSL | MCP JSON already expresses the same intent; grammar adds maintenance burden |
| MetricFlow query language | Tied to SQL/dbt; does not cover OpenData/Graph backends |
| PRQL | SQL target only |
| Apache Calcite SQL dialect | Cannot represent OpenData or Graph operations |

#### MCP input → LQP transformation

```json
// Input: MCP tool call
{
  "tool": "analyse_metric",
  "input": {
    "metrics":    ["portfolio_return", "tracking_error"],
    "dimensions": ["portfolio"],
    "time":       { "period": "quarter_to_date", "as_of_date": "2026-05-14" },
    "filters":    [{ "dimension": "portfolio", "operator": "in", "values": ["GLOB_EQ_OPP", "UK_CORE_INC"] }],
    "sort":       [{ "metric": "portfolio_return", "direction": "desc" }]
  }
}
```

```json
// Output: Logical Query Plan (LQP) — no backend-specific syntax
{
  "lqp_id":    "lqp_20260514_093247_a1b2c3",
  "tenant_id": "acme-wealth",
  "resolved_metrics": [
    {
      "metricId": "portfolio_return", "version": 2,
      "dataAffinity": ["portfolio"], "costWeight": 1.0,
      "physicalMapping": {
        "backendId": "snowflake-primary", "table": "fact_portfolio_daily",
        "valueColumn": "portfolio_return", "dateColumn": "price_date",
        "joinKeys": { "portfolio": "portfolio_id" }
      }
    },
    {
      "metricId": "tracking_error", "version": 1,
      "dataAffinity": ["portfolio", "benchmarks"], "costWeight": 2.0,
      "physicalMapping": {
        "backendId": "benchmark-data-service",
        "endpoint":  "/odata/v1/TrackingError",
        "joinKeys":  { "portfolio": "portfolio_id" }
      }
    }
  ],
  "dimensions": [{ "id": "portfolio", "physicalKey": "portfolio_id" }],
  "time": {
    "period": "quarter_to_date", "as_of_date": "2026-05-14",
    "resolved_range": { "from": "2026-04-01", "to": "2026-05-14" }
  },
  "filters": [{
    "dimension": "portfolio", "operator": "in",
    "values": ["GLOB_EQ_OPP", "UK_CORE_INC"],
    "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')"
  }],
  "sort": [{ "metric": "portfolio_return", "direction": "desc" }],
  "limit": 100,
  "governance": {
    "estimated_cost_units": 480,
    "classification":       "internal",
    "entitlement_hash":     "sha256:a3f91c..."
  }
}
```

---

### Role-Aware Projection Layer

Extracts JWT claims, resolves them against the tenant's role policy, and injects row predicates and column masks into the LQP before it reaches the FQP.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom middleware (TypeScript) | Thin and stateless; operates on the LQP before any backend query is generated |
| **Role resolution** | JWT claim extraction + PostgreSQL role config | Role claim field name is configurable per tenant (`entitlements.roleClaimField`) |
| **Row predicates** | `{{user.claim_name}}` template interpolation at LQP build time | Resolved from JWT claims; injected into LQP `filters` |
| **Column masking** | Applied post-assembly in FQP result assembler | Post-assembly supports cross-backend result sets |
| **Default policy** | `defaultDenyAll: true` | No access unless a matching role is found |

#### `analytics.role_policies` (DDL)

```sql
CREATE TABLE analytics.role_policies (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        TEXT        NOT NULL,
  role_name        TEXT        NOT NULL,  -- matches JWT role claim value
  allowed_metrics  TEXT[],               -- NULL = all approved metrics
  denied_metrics   TEXT[],               -- takes precedence over allowed_metrics
  row_predicates   JSONB,                -- per-dimension predicate templates
  column_masks     JSONB,                -- per-metric suppression rules
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_role_per_tenant UNIQUE (tenant_id, role_name)
);
```

#### Role policy example

```json
{
  "roleId":   "regional_analyst",
  "tenantId": "acme-wealth",
  "allowedMetrics": null,
  "deniedMetrics":  ["var_99", "expected_shortfall"],
  "rowPredicates": {
    "portfolio": "portfolio_id IN ({{user.managed_portfolios}})",
    "entity":    "legal_entity_id IN ({{user.entity_ids}})"
  },
  "columnMasks": {
    "aum": {
      "condition":   "{{user.roles}} NOT CONTAINS 'senior_analyst'",
      "action":      "suppress",
      "replacement": null
    }
  }
}
```

A `regional_analyst` with `managed_portfolios: ["GLOB_EQ_OPP"]` has `portfolio_id IN ('GLOB_EQ_OPP')` injected as a filter. The FQP sees only the resolved predicate, never the source claim.

---

### Semantic Execution Governance

Enforces cost budgets, classification gates, and compliance mode constraints between LQP generation and FQP submission.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom rules engine (TypeScript) | Deterministic; config-driven; no ML inference |
| **Cost estimation** | `Σ(metric.costWeight × dimensionCardinality × timeRangeMultiplier)` | Pre-execution; calibrated against actual cost data |
| **Circuit breaker** | Per-request ceiling + per-user hourly budget | Hard ceiling prevents runaway queries |
| **Config store** | PostgreSQL (`analytics.governance_config`) | Per-tenant thresholds; not hardcoded |

#### `analytics.governance_config` (DDL)

```sql
CREATE TABLE analytics.governance_config (
  tenant_id                   TEXT        PRIMARY KEY,
  cost_ceiling_per_query      INT         NOT NULL DEFAULT 2000,
  cost_budget_per_user_hourly INT         NOT NULL DEFAULT 10000,
  max_concurrent_queries      INT         NOT NULL DEFAULT 20,
  max_metrics_per_query       INT         NOT NULL DEFAULT 10,
  max_dimensions              INT         NOT NULL DEFAULT 5,
  classification_gate         TEXT        NOT NULL DEFAULT 'internal',
  compliance_modes            TEXT[]      NOT NULL DEFAULT '{}',
  updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Governance decision record

```json
{
  "governance_decision_id": "gov_20260514_093247_a1b2",
  "lqp_id": "lqp_20260514_093247_a1b2c3",
  "tenant_id": "acme-wealth", "user_sub": "user_pm_001",
  "checks": [
    { "check": "cost_ceiling",        "estimated_cost": 480, "ceiling": 2000,   "passed": true },
    { "check": "user_hourly_budget",  "consumed": 1240,      "limit": 10000,    "passed": true },
    { "check": "concurrent_limit",    "active_queries": 3,   "limit": 20,       "passed": true },
    { "check": "classification_gate", "level": "internal",   "gate": "internal","passed": true },
    { "check": "compliance_mifid2",   "triggered": false,                        "passed": true }
  ],
  "decision": "approved",
  "decided_at": "2026-05-14T09:32:47.112Z"
}
```

---

### Federated Query Planner (FQP)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Plan optimiser** | Apache Calcite | Battle-tested SQL plan optimisation; used by Trino, Flink, Beam |
| **Backend adapters** | Custom adapter per backend type | Calcite handles SQL; custom adapters cover REST/OpenData/GraphQL/SPARQL |
| **Result assembly** | Custom (TypeScript) | Simple fan-out/fan-in; no off-the-shelf library needed |

| Alternative | Why not chosen |
|------------|---------------|
| Trino | Excellent SQL federation; does not query REST/Graph APIs natively |
| Starburst Galaxy | Managed Trino; same API backend limitation |
| Custom from scratch | Reinventing Calcite's optimiser is unjustified |

#### Sub-plan decomposition

The FQP splits the LQP by `dataAffinity`. The two-metric, two-affinity LQP above produces:

```json
{
  "fqp_plan_id": "fqp_plan_20260514_093247",
  "lqp_id":      "lqp_20260514_093247_a1b2c3",
  "sub_plans": [
    {
      "id": "sp_a", "metrics": ["portfolio_return"], "dimensions": ["portfolio_id"],
      "time": { "from": "2026-04-01", "to": "2026-05-14" },
      "filters": [{ "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')" }],
      "data_affinity": "portfolio", "assigned_backend": "snowflake-primary",
      "generated_query": {
        "dialect": "snowflake",
        "sql": "SELECT p.portfolio_id, p.portfolio_name, SUM(pd.market_value * pd.daily_return) / SUM(pd.market_value) AS portfolio_return FROM fact_portfolio_daily pd JOIN dim_portfolio p ON pd.portfolio_id = p.portfolio_id WHERE pd.price_date BETWEEN '2026-04-01' AND '2026-05-14' AND pd.portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC') GROUP BY p.portfolio_id, p.portfolio_name ORDER BY portfolio_return DESC"
      }
    },
    {
      "id": "sp_b", "metrics": ["tracking_error"], "dimensions": ["portfolio_id", "benchmark_id"],
      "time": { "period": "trailing_12m", "as_of_date": "2026-05-14" },
      "filters": [{ "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')" }],
      "data_affinity": "benchmarks", "assigned_backend": "benchmark-data-service",
      "generated_query": {
        "dialect": "odata",
        "url": "/odata/v1/TrackingError",
        "params": {
          "$filter": "portfolio_id in ('GLOB_EQ_OPP','UK_CORE_INC') and as_of_date eq 2026-05-14",
          "$select": "portfolio_id,benchmark_id,tracking_error_annualised"
        }
      }
    }
  ],
  "join_keys": ["portfolio_id"],
  "assembly_strategy": "left_join_on_portfolio_id"
}
```

#### Backend adapter interface

```typescript
interface FQPBackendAdapter {
  readonly backendType: BackendType;
  ping(): Promise<{ healthy: boolean; latencyMs: number }>;
  executeSubPlan(subPlan: SubPlanFragment, credentials: BackendCredentials): Promise<SubPlanResult>;
}

interface SubPlanFragment {
  id: string; metrics: string[]; dimensions: string[];
  time: ResolvedTimeRange; filters: PhysicalPredicate[];
  dataAffinity: string;
}

interface SubPlanResult {
  subPlanId:       string;
  status:          "success" | "partial" | "error";
  rows:            Record<string, unknown>[];
  rowCount:        number;
  latencyMs:       number;
  costUnits:       number;
  warningMessage?: string;
  errorCode?:      string;
}
```

---

### Execution backends (supported adapters)

| Backend type | Adapter | Protocols |
|-------------|---------|-----------|
| **SQL warehouse** | Calcite SQL adapter | Snowflake, BigQuery, Databricks, Redshift, Trino, Starburst Enterprise, PostgreSQL |
| **Semantic layer** | Semantic layer adapter | dbt Semantic Layer (MetricFlow), Cube.js |
| **OpenData API** | REST/OData adapter | REST JSON, OData v4, SOAP (via shim) |
| **Graph Data API** | Graph adapter | Neo4j Bolt, Amazon Neptune SPARQL, OpenCypher REST |
| **OLAP engine** | OLAP adapter | Apache Druid, ClickHouse, Pinot |
| **Custom** | Custom adapter interface | Any backend conforming to `FQPBackendAdapter` |

---

### Ecosystem complementary services

| Service | Integration | Implementation |
|---------|------------|----------------|
| **Semantic Registry Service** | Config-time — `POST /v1/smr/import` | REST client in Platform Admin API |
| **Regulatory Reference Service** | Runtime backend (`dataAffinity: ["regulatory"]`) | OpenData API FQP adapter |
| **Benchmark Data Service** | Runtime backend (`dataAffinity: ["benchmarks"]`) | OpenData API FQP adapter |

Both runtime services are routed via `dataAffinity` matching with no FQP special-casing. On unavailability the FQP falls back to the next registered backend or returns a partial result with a structured warning. Benchmark Data Service licensing errors propagate as `BENCHMARK_NOT_LICENSED` sub-plan failures.

---

### Visualisation Ontology — SCL

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Chart spec** | Vega-Lite v5 JSON | Industry-standard chart grammar; wide ecosystem for web, server-side, and image rendering |
| **Table spec** | Platform-defined `type: "table"` extension | Vega-Lite has no native table mark; same `data` + `columns` convention |
| **SCL abstraction** | "Semantic Charting Language (SCL)" | Decouples product spec from the format library |

| Alternative | Why not chosen |
|------------|---------------|
| Plotly JSON | Larger spec; less portable to SSR environments |
| Apache ECharts | Less standard outside enterprise BI |
| Observable Plot | Less mature; smaller SSR ecosystem |
| Custom schema | Vega-Lite is widely understood and tooled |

#### SCL chart spec (line chart)

```json
{
  "type": "chart", "mark": "line",
  "data": {
    "values": [
      { "date": "2026-04-01", "portfolio": "GLOB_EQ_OPP", "portfolio_return": 1.24 },
      { "date": "2026-04-30", "portfolio": "GLOB_EQ_OPP", "portfolio_return": 2.87 },
      { "date": "2026-05-14", "portfolio": "GLOB_EQ_OPP", "portfolio_return": 3.42 },
      { "date": "2026-04-01", "portfolio": "UK_CORE_INC",  "portfolio_return": 0.91 },
      { "date": "2026-04-30", "portfolio": "UK_CORE_INC",  "portfolio_return": 1.54 },
      { "date": "2026-05-14", "portfolio": "UK_CORE_INC",  "portfolio_return": 2.10 }
    ]
  },
  "encoding": {
    "x":     { "field": "date",             "type": "temporal",     "title": "Date",               "axis": { "format": "%b %d" } },
    "y":     { "field": "portfolio_return", "type": "quantitative", "title": "Portfolio Return (%)", "axis": { "format": ".2f"  } },
    "color": { "field": "portfolio",        "type": "nominal",      "legend": { "title": "Portfolio" } }
  },
  "colorScheme": "category10",
  "title":       "Portfolio Return — Quarter to Date (as of 14 May 2026)",
  "formatHints": { "yUnit": "percent", "yDecimals": 2, "suffix": "%" }
}
```

#### SCL table spec

```json
{
  "type": "table",
  "columns": [
    { "field": "portfolio_name",   "label": "Portfolio",          "width": 200 },
    { "field": "portfolio_return", "label": "Return (%)",         "format": { "type": "percent", "decimals": 2 } },
    { "field": "tracking_error",   "label": "Tracking Error (%)", "format": { "type": "percent", "decimals": 2 } }
  ],
  "data": [
    { "portfolio_name": "Global Equity Opportunities", "portfolio_return": 3.42, "tracking_error": 2.11 },
    { "portfolio_name": "UK Core Income",              "portfolio_return": 2.10, "tracking_error": 1.87 }
  ],
  "thresholds": [
    { "column": "tracking_error", "condition": "gt", "value": 2.0,
      "style": { "backgroundColor": "#FFF3CD", "fontWeight": "bold" } }
  ],
  "title": "Portfolio Return and Tracking Error — Quarter to Date"
}
```

---

### Static image rendering (vite2img)

vite2img is a **standalone MCP render service** — it is not part of the AI Analytics Platform. Consumers that need static image output (the AI Chat Platform for PDF/export workflows, agentic report pipelines) register vite2img as a peer MCP server alongside the Analytics Platform, using the same `mcpServers` registration pattern. It receives a `display_spec` JSON object directly from the consumer and returns SVG or PNG. It has no connection to the Analytics Platform's governance pipeline.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Integration pattern** | Standalone MCP server registered directly with consumers | Keeps rendering concerns outside the Analytics Platform; consumers decide when to call it |
| **Implementation** | Vite + vega-embed + headless Chromium (Playwright) | Pixel-accurate SVG/PNG from Vega-Lite specs; handles charts and tables |
| **Table rendering** | Custom HTML template | Styled HTML table via Playwright screenshot |

| Alternative | Why not chosen |
|------------|---------------|
| Analytics Platform MCP tool | Rendering is a consumer concern — the platform returns governed SCL specs; static image conversion is outside its governance scope |
| Node.js vega-lite CLI | No browser rendering; limited CSS for table specs |
| Puppeteer | Viable; Playwright preferred for API ergonomics |

---

### Consumer-side rendering

The platform does not mandate a rendering library. Reference implementations:

| Consumer | Chart | Table | Static image |
|---------|-------|-------|------|
| AI Chat Platform | vega-embed | Native data table | vite2img (direct MCP call) |
| Custom UI | vega-embed (recommended) or any Vega-Lite-compatible library | Host's own grid | vite2img |
| Agentic consumers | vite2img | vite2img | vite2img |

vega-embed is the only library with direct Vega-Lite v5 compatibility. ECharts, Plotly.js, and D3 all require a translation layer. For static image output, vite2img is the reference implementation regardless of consumer type.

---

### Narrative Synthesis Engine

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Provider** | Anthropic Claude | Consistent with intent layer; strong constrained prose |
| **Default tier** | Haiku | Low-latency; sufficient quality for narrative prose |
| **Complex narratives** | Sonnet | Multi-portfolio attribution; complex regulatory narratives |

---

### Analytical Lineage Store

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Lineage records** | PostgreSQL | Structured; queryable; ACID audit integrity |
| **Result artefacts** | S3-compatible object storage | Large result sets stored as blobs; referenced by URL |
| **Retention** | Default 7 years (configurable per compliance mode) | MiFID II and equivalent regimes |

| Alternative | Why not chosen |
|------------|---------------|
| Apache Atlas | Heavy; over-engineered for query result lineage |
| OpenLineage + Marquez | Better suited to ETL pipeline lineage |
| Graph database | Relational model is sufficient |

#### `analytics.lineage_records` (DDL)

```sql
CREATE TABLE analytics.lineage_records (
  result_id            TEXT        PRIMARY KEY,       -- e.g. "res_20260514_093247_a1b2c3"
  tenant_id            TEXT        NOT NULL,
  user_sub             TEXT        NOT NULL,          -- JWT sub claim
  lqp_id               TEXT        NOT NULL,
  fqp_execution_id     TEXT,                          -- null on cache hit
  cache_hit            BOOLEAN     NOT NULL DEFAULT FALSE,
  request_payload      JSONB       NOT NULL,          -- full MCP tool call input
  resolved_metrics     JSONB       NOT NULL,          -- metric IDs + versions
  governance_decision  JSONB       NOT NULL,
  sub_plans            JSONB,                         -- FQP execution records per sub-plan
  result_summary       JSONB       NOT NULL,          -- latency, cost, row count
  error_code           TEXT,
  compliance_mode      TEXT,                          -- "mifid2" | "basel3" | "sec_reg_bi" | null
  compliance_meta      JSONB,
  result_artefact_url  TEXT,                          -- S3 URL; null for small/cached results
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at           TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_lineage_tenant_user ON analytics.lineage_records (tenant_id, user_sub, created_at DESC);
CREATE INDEX idx_lineage_tenant_time ON analytics.lineage_records (tenant_id, created_at DESC);
CREATE INDEX idx_lineage_compliance  ON analytics.lineage_records (tenant_id, compliance_mode) WHERE compliance_mode IS NOT NULL;
```

#### Lineage record example

```json
{
  "result_id":        "res_20260514_093247_a1b2c3",
  "tenant_id":        "acme-wealth",
  "user_sub":         "user_pm_001",
  "lqp_id":           "lqp_20260514_093247_a1b2c3",
  "fqp_execution_id": "fqp_exec_20260514_093247",
  "cache_hit":        false,
  "resolved_metrics": [
    { "metricId": "portfolio_return", "version": 2 },
    { "metricId": "tracking_error",   "version": 1 }
  ],
  "governance_decision": { "decision": "approved", "estimated_cost_units": 480 },
  "sub_plans": [
    { "id": "sp_a", "engine_id": "snowflake-primary",      "metrics": ["portfolio_return"], "status": "success", "latency_ms": 1240, "rows_returned": 2, "cost_units": 300 },
    { "id": "sp_b", "engine_id": "benchmark-data-service", "metrics": ["tracking_error"],   "status": "success", "latency_ms":  890, "rows_returned": 2, "cost_units": 180 }
  ],
  "result_summary": {
    "row_count": 2, "column_count": 3,
    "assembly_latency_ms": 45, "total_latency_ms": 1285,
    "total_cost_units": 480, "cache_written": true, "cache_ttl_seconds": 3600
  }
}
```

Lineage records are immutable. Post-hoc compliance annotations are written to `analytics.lineage_amendments` referencing the original `result_id`.

---

## Infrastructure

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Edge runtime | Cloudflare Workers | Global low-latency MCP surface |
| Backend services | Kubernetes (cloud-agnostic) | FQP, governance, SMR as independently scalable pods |
| Primary database | PostgreSQL (Neon or RDS) | SMR, lineage, tenant config, governance config |
| Search | Elasticsearch / OpenSearch | SMR metric search index |
| Object storage | S3-compatible | Result artefacts, large cached result sets |
| Message queue | SQS / Pub/Sub | Async lineage writes, catalog change events |
| Secrets | HashiCorp Vault or cloud-native | Backend credentials, platform service keys |

---

## Version compatibility matrix

| Platform version | Vega-Lite (SCL) | MCP protocol | Node.js |
|-----------------|----------------|-------------|---------|
| v1.0 | 5.x | MCP 1.x (Streamable HTTP) | 22 LTS |
