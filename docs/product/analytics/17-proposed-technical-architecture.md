# 17 — Reference Implementation: One Possible Technical Stack

This document describes **one reference implementation** of the AI Analytics Platform — a specific set of technology choices that satisfies the product specification. It is not the only valid stack. The product specification (all other documents in this folder) is intentionally stack-agnostic; any implementation that fulfils the specified behaviours, governance guarantees, and interface contracts is conformant.

This reference stack is presented to make architectural trade-offs concrete and to give implementers a starting point. Each layer maps to a chosen technology, explains the rationale for that choice, and compares credible alternatives — any of which could be substituted without changing the product specification.

A decision to adopt a different technology at any layer should be documented here as a replacement or alternative to the reference choice. Changes to technology choices never require changes to the product spec.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Capability Layer                         │
│        Cloudflare Workers / Fastly Compute @ Edge               │
│        MCP Streamable HTTP transport                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   Semantic Intent Layer                          │
│     Anthropic Claude (Sonnet tier for intent resolution;        │
│     Opus tier for complex multi-metric queries)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               Semantic Metrics Registry (SMR)                    │
│           PostgreSQL (primary store, RLS enforced)              │
│           + Elasticsearch (metric search index)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Role-Aware Projection Layer                         │
│              Custom middleware (TypeScript / Go)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Analytical Intent Validator                          │
│    MCP JSON params → SMR validation → LQP generator             │
│    (TypeScript — JSON schema validation + SMR resolution)        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Semantic Execution Governance                       │
│    Cost estimation, classification gating, circuit breakers     │
│    Custom rules engine (TypeScript)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               Federated Query Planner (FQP)                      │
│   Apache Calcite (query plan optimisation and routing engine)   │
│   + custom backend adapter layer                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Visualisation Ontology (SCL generation)             │
│   Vega-Lite v5 as the SCL chart specification format            │
│   + platform-defined table spec extension                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               Narrative Synthesis Engine                         │
│   Anthropic Claude (Haiku tier default; Sonnet for complex)     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               Analytical Lineage Store                           │
│   PostgreSQL (structured lineage records, queryable)            │
│   + object storage (large result set artefacts)                 │
└─────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼──────────┐ ┌──────▼────────┐ ┌────────▼──────────┐
│  SQL Warehouse     │ │ OpenData API  │ │  Graph Data API   │
│  Snowflake /       │ │  REST / OData │ │  Neo4j / Neptune  │
│  BigQuery /        │ │  endpoints    │ │  / SPARQL         │
│  Databricks        │ │               │ │                   │
└────────────────────┘ └───────────────┘ └───────────────────┘
```

---

## Layer-by-layer stack decisions

### Platform Admin API

The Platform Admin API is the authenticated management surface for the entire platform — backend registration, SMR management, entitlement policy configuration, and governance threshold controls. It is a separate service from the MCP Capability Layer (which serves consumers) and runs as a standard backend service rather than at the edge.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Runtime** | Node.js (Express / Fastify) on Kubernetes | Admin operations are low-frequency and latency-tolerant — edge deployment not required; standard backend service pattern is simpler and more flexible for complex admin workflows |
| **Auth** | JWT with `platform_admin` or `app_admin` role claim | Reuses the same JWT infrastructure as the MCP Capability Layer; admin role claims are validated at the API gateway before any admin operation executes |
| **API style** | REST (JSON) | Admin operations are well-modelled as CRUD on named resources (backends, metrics, entitlement policies, governance config); REST is simpler than GraphQL for these patterns |
| **Data store** | PostgreSQL (shared primary database) | Admin state (Data Source Catalog, SMR definitions, entitlement policies, governance config) lives in the same PostgreSQL instance as the lineage store and preference store — one managed instance |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Cloudflare Workers for Admin API | Admin operations include long-running validations (SMR consistency checks, impact analysis) that exceed the Workers CPU budget |
| Separate database for admin state | Unnecessary operational overhead — admin state and operational state are naturally co-located and share the same RLS tenant isolation |
| GraphQL | Admin operations don't benefit from graph-style query composition; REST CRUD is simpler to implement and document |

---

### Admin Console (web UI)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | React + TypeScript (SPA) | Standard choice for data-heavy admin UIs; rich ecosystem for form handling, table rendering, and YAML editors |
| **Hosting** | Static assets on CDN (Cloudflare Pages or S3 + CloudFront) | Single-page app with no server-side rendering requirement; CDN hosting is simple and globally fast |
| **YAML editor** | Monaco Editor (embedded) | VS Code's editor engine; built-in YAML syntax highlighting and validation; familiar to the metric owners and engineers who write SMR definitions |
| **Auth** | Same JWT as Platform Admin API | Console authenticates via the same identity provider as the rest of the platform; no separate session management |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Server-side rendered (Next.js) | Not required — admin console does not need SEO or first-paint optimisation; SPA is simpler to deploy |
| Low-code admin builder (Retool, AdminJS) | Insufficient control over the SMR definition editor, consistency checker UI, and governance configuration workflows |

---

### Data Source Catalog

The Data Source Catalog is the platform's registry of all registered execution backends. It is stored in the primary PostgreSQL database and managed exclusively via the Platform Admin API — it is not a separate service.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Storage** | PostgreSQL table (`analytics.execution_backends`) | Structured; strongly-typed; shares RLS tenant isolation with the rest of the platform |
| **Runtime access** | In-memory cache in the FQP service (refreshed on catalog change events via message queue) | The FQP reads the catalog on every query; caching in-process eliminates per-query database round-trips; cache invalidated on any catalog mutation via the message queue |
| **Change propagation** | Message queue event (`CATALOG_UPDATED`) published by Admin API on any backend registration change | Decouples Admin API from FQP; FQP subscribes and refreshes its in-memory cache; no direct service-to-service call required |

#### `analytics.execution_backends` table (PostgreSQL DDL)

```sql
CREATE TABLE analytics.execution_backends (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      TEXT        NOT NULL,
  backend_id     TEXT        NOT NULL,  -- human-readable, e.g. "snowflake-primary"
  display_name   TEXT        NOT NULL,
  backend_type   TEXT        NOT NULL,  -- "sql_warehouse" | "semantic_layer" | "opendata_api" | "graph_api" | "olap_engine" | "custom"
  data_affinity  TEXT[]      NOT NULL,  -- e.g. ARRAY['portfolio','performance']
  priority       INT         NOT NULL DEFAULT 100,  -- lower = higher priority; FQP uses ascending sort
  config         JSONB       NOT NULL,  -- connection config; credentials are secret_ref pointers only
  enabled        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_backend_per_tenant UNIQUE (tenant_id, backend_id)
);

CREATE INDEX idx_backends_affinity ON analytics.execution_backends
  USING GIN (data_affinity);
```

#### Example backend registration (Admin API `POST /v1/backends`)

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

The FQP loads all `enabled = TRUE` rows for the request's `tenant_id` into its in-memory cache at startup and on each `CATALOG_UPDATED` event. During sub-plan routing, it filters by `data_affinity @> ARRAY[requiredAffinity]` and selects the row with the lowest `priority` value that is currently healthy.

---

### MCP Capability Layer

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Runtime** | Cloudflare Workers (primary) | Sub-10ms cold start at edge; global anycast; no server management |
| **Protocol** | MCP Streamable HTTP transport | Standard MCP interoperability; supports both request/response and streaming |
| **Auth** | JWT validation at edge | Stateless; JWT validated at the edge before any platform computation |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| AWS Lambda + API Gateway | Higher cold start latency; regional, not global by default |
| Fastly Compute@Edge | Strong alternative; less mature ecosystem; viable for future consideration |
| Traditional Node.js server | Operational overhead; does not suit the edge-deployed pattern |

#### MCP tool input JSON schema (`analyse_metric`)

The MCP Capability Layer validates every incoming tool call against a published JSON schema before passing it to the Semantic Intent Layer. Example schema for the primary `analyse_metric` tool:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "analyse_metric input",
  "type": "object",
  "required": ["metrics"],
  "additionalProperties": false,
  "properties": {
    "metrics": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "maxItems": 10,
      "description": "Metric IDs or natural-language metric names to analyse"
    },
    "dimensions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Dimension IDs to group by (e.g. ['portfolio', 'asset_class'])"
    },
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

### Semantic Intent Layer (AI model)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Provider** | Anthropic (Claude) | Best-in-class instruction following for constrained analytical domains; strong tool-use reliability |
| **Intent resolution tier** | Claude Sonnet (standard tier) | Good balance of speed and accuracy for metric resolution; outperforms faster models on domain-specific analytical language |
| **Complex query tier** | Claude Opus (powerful tier) | Used for multi-metric attribution queries and ambiguous intent where higher reasoning quality is required |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| OpenAI GPT-4o | Viable; provider diversity creates lock-in risk; Anthropic preferred for instruction-following quality in governed contexts |
| Google Gemini | Viable; integration complexity with GCP; provider diversity to be considered for v2 |
| Fine-tuned domain model | High ongoing cost of fine-tuning for metric vocabulary; prompt-based context injection preferred in v1 |

---

### Semantic Metrics Registry (SMR)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Primary store** | PostgreSQL with row-level security | Mature, strongly-typed, ACID; RLS enforces per-tenant isolation at the database layer |
| **Search index** | Elasticsearch | Fast fuzzy search for metric lookup by name/description; decoupled from primary store |
| **Version control** | Custom versioning in PostgreSQL | Append-only version records; no external dependency |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| MongoDB | Schema-less is a disadvantage for governed metric definitions; stronger typing needed |
| dbt + Git (as the registry) | Excellent for engineering teams; poor UX for business owners; no runtime query path |
| Apache Atlas | Heavy; enterprise-only adoption patterns; integration complexity not justified for v1 |

#### `analytics.metric_definitions` table (PostgreSQL DDL)

```sql
CREATE TABLE analytics.metric_definitions (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     TEXT        NOT NULL,
  metric_id     TEXT        NOT NULL,  -- stable identifier, e.g. "portfolio_return"
  version       INT         NOT NULL DEFAULT 1,
  status        TEXT        NOT NULL,  -- "proposed" | "approved" | "deprecated"
  source        TEXT        NOT NULL DEFAULT 'tenant',  -- "reference" (from FS Reference Model) | "tenant" (custom)
  definition    JSONB       NOT NULL,  -- full SMR definition document (see example below)
  created_by    TEXT        NOT NULL,
  approved_by   TEXT,
  approved_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  superseded_at TIMESTAMPTZ,          -- set when a new version is approved; old version retained for lineage
  CONSTRAINT uq_metric_version UNIQUE (tenant_id, metric_id, version)
);

-- Partial index: only one approved version per metric per tenant at any time
CREATE UNIQUE INDEX idx_one_approved_version
  ON analytics.metric_definitions (tenant_id, metric_id)
  WHERE status = 'approved';

CREATE INDEX idx_metric_definitions_gin ON analytics.metric_definitions
  USING GIN (definition);  -- enables JSON path queries, e.g. definition->>'category' = 'performance'
```

The Elasticsearch search index mirrors `metric_id`, `displayName`, `description`, `aliases`, and `tags` from the `definition` JSONB. The index is rebuilt on each status transition to `approved` and on any `superseded_at` write.

#### Example metric definition (the `definition` JSONB column)

```json
{
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
    "backendId":    "snowflake-primary",
    "table":        "fact_portfolio_daily",
    "valueColumn":  "portfolio_return",
    "dateColumn":   "price_date",
    "joinKeys":     { "portfolio": "portfolio_id" }
  },
  "formatting": {
    "unit":          "percent",
    "decimalPlaces": 2,
    "suffix":        "%"
  },
  "governance": {
    "costWeight":           1.0,
    "classificationLevel":  "internal",
    "entitledRoles":        ["portfolio_manager", "analyst", "risk_officer"],
    "complianceNotes":      "For MiFID II cost disclosure use cost_adjusted_return."
  },
  "narrativeTemplate": "{{portfolio_name}} returned {{value}}% {{period_label}}, {{direction}} its benchmark by {{tracking_error}}%.",
  "aliases": ["return", "twr", "portfolio_twr"],
  "tags":    ["performance", "core", "reference-model"]
}
```

The `physicalMapping` block is resolved by the FQP at query time. The `governance.costWeight` is used by the Semantic Execution Governance cost estimator: `estimated_cost = sum(metric.costWeight) × dimensionMultiplier × rowCountEstimate`.

---

### Financial Services Reference Model

The reference model is the pre-built industry seed for the SMR — a set of versioned YAML bundles that ship with the platform and seed a new tenant's SMR baseline on first setup.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Packaging format** | Versioned YAML bundles (one per analytical domain) | YAML is human-readable and directly importable via the Admin API; one bundle per domain (`portfolio`, `performance`, `risk`, `regulatory`, `counterparty`, `benchmarks`) allows selective import |
| **Distribution** | Bundled with the platform at installation; also importable from the Semantic Registry Service for updated versions | Platform installation includes a pinned snapshot for air-gapped deployments; connected tenants can pull updated packages from the live Semantic Registry Service |
| **Activation** | `analyticalDomain` config field triggers SMR import at tenant setup | Tenant specifies `analyticalDomain: "wealth_management"` (or `"banking"`, `"investment_management"`) in Admin Console; platform imports the relevant domain bundles as `proposed` definitions; Application Admin approves before they become resolvable |
| **Customisation** | Full edit/override via Admin API after import | Imported definitions are not locked — Application Admins can modify formula, aggregation rules, or dimensions before or after approval. Customised definitions are marked `source: "tenant"` to distinguish them from the reference baseline |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Embedded in platform binary | YAML bundles are easier to inspect, diff, and update without a platform rebuild; Admin Console can render them as human-readable definitions |
| Pulled from external registry only (no bundled snapshot) | Air-gapped regulated deployments need a local copy; bundled snapshot + optional live update is the safer default |
| SQL seed scripts | Less portable across SMR schema versions; YAML bundles can be re-imported idempotently |

#### Example reference model YAML bundle (performance domain, excerpt)

The `performance` domain bundle ships as `bundles/performance/v1.0.yaml`. Definitions import as `status: "proposed"` and are activated via Admin Console approval.

```yaml
# bundles/performance/v1.0.yaml
# Financial Services Reference Model — Performance domain
# Schema version: 1.0 | Minimum platform version: 1.0

bundle:
  domain:      performance
  version:     "1.0"
  description: "Core performance measurement metrics for investment portfolios"

  metrics:

    - metricId:    portfolio_return
      displayName: Portfolio Return
      description: >
        Time-weighted return for the portfolio over the selected period,
        expressed as a percentage.
      category:    performance
      dataAffinity: [portfolio]
      formula:
        type:        time_weighted_return
        inputs:      [daily_return, market_value]
        aggregation: chain_link
      dimensions:
        - { id: portfolio,   required: true  }
        - { id: date,        required: true  }
        - { id: asset_class, required: false }
        - { id: currency,    required: false }
      timePeriods:  [day, week, month, quarter_to_date, year_to_date, trailing_12m]
      formatting:   { unit: percent, decimalPlaces: 2, suffix: "%" }
      governance:
        costWeight:           1.0
        classificationLevel:  internal
        entitledRoles:        [portfolio_manager, analyst, risk_officer]
      aliases: [return, twr, portfolio_twr]
      tags:    [performance, core]

    - metricId:    tracking_error
      displayName: Tracking Error
      description: >
        Annualised standard deviation of the portfolio's excess returns
        relative to its benchmark.
      category:    performance
      dataAffinity: [portfolio, benchmarks]
      formula:
        type:   annualised_std_dev
        inputs: [active_return]
        window: rolling_252d
      dimensions:
        - { id: portfolio,  required: true }
        - { id: benchmark,  required: true }
        - { id: date,       required: true }
      timePeriods:  [trailing_12m, trailing_36m, trailing_60m]
      formatting:   { unit: percent, decimalPlaces: 2, suffix: "%" }
      governance:
        costWeight:           2.0
        classificationLevel:  internal
        entitledRoles:        [portfolio_manager, analyst, risk_officer]
      aliases: [te, active_risk]
      tags:    [performance, risk-adjusted, benchmark-relative]

    - metricId:    information_ratio
      displayName: Information Ratio
      description: >
        Ratio of annualised active return to tracking error. Measures
        portfolio manager skill per unit of active risk taken.
      category:    performance
      dataAffinity: [portfolio, benchmarks]
      formula:
        type:    ratio
        numerator:   active_return_annualised
        denominator: tracking_error
      dimensions:
        - { id: portfolio,  required: true }
        - { id: benchmark,  required: true }
        - { id: date,       required: true }
      timePeriods:  [trailing_12m, trailing_36m, trailing_60m]
      formatting:   { unit: ratio, decimalPlaces: 2 }
      governance:
        costWeight:           2.5
        classificationLevel:  internal
        entitledRoles:        [portfolio_manager, analyst]
      aliases: [ir]
      tags:    [performance, risk-adjusted]
```

The `risk` domain bundle follows the same structure with metrics such as `var_95`, `var_99`, `expected_shortfall`, `beta`, `duration`, and `convexity`. The `regulatory` domain bundle includes `lcr`, `nsfr`, and `leverage_ratio` — all with `classificationLevel: restricted` and compliance metadata specific to their regulatory regime.

---

### Analytical Intent Validator and LQP Generator

There is no custom query language. The MCP tool call JSON parameter format (metric IDs, dimension IDs, time period, filters) is the analytical intent representation — consistent with established semantic layer query conventions (Cube.js, MetricFlow). The validator implements JSON schema validation + SMR ID resolution + LQP generation, not a grammar compiler.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Intent format** | MCP tool call JSON parameters | Already the standard AI tool-use format; no separate language needed; consistent with Cube.js/MetricFlow query conventions |
| **Implementation** | TypeScript (JSON schema validation + SMR resolution) | Lightweight; no custom grammar or parser required; JSON schema validation is well-tooled |
| **LQP format** | Custom DAG (JSON) | Engine-agnostic; portable across SQL, OpenData API, and Graph API backends |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Custom textual DSL (EBNF grammar, Rust compiler) | Over-engineered; the MCP JSON format already expresses the same intent; custom grammar adds maintenance burden for no consumer benefit |
| MetricFlow (dbt) query language | Closest existing alternative; excellent for semantic metric queries; tied to SQL/dbt ecosystem; does not cover OpenData/Graph backends |
| PRQL | SQL target only |
| Apache Calcite SQL dialect | SQL-specific; cannot represent OpenData API or Graph API operations natively |

#### MCP tool input → Logical Query Plan (LQP) transformation

**Input: incoming MCP tool call**

```json
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

**Output: Logical Query Plan (LQP) — engine-agnostic DAG**

```json
{
  "lqp_id":    "lqp_20260514_093247_a1b2c3",
  "tenant_id": "acme-wealth",
  "resolved_metrics": [
    {
      "metricId":     "portfolio_return",
      "version":      2,
      "dataAffinity": ["portfolio"],
      "costWeight":   1.0,
      "physicalMapping": {
        "backendId":   "snowflake-primary",
        "table":       "fact_portfolio_daily",
        "valueColumn": "portfolio_return",
        "dateColumn":  "price_date",
        "joinKeys":    { "portfolio": "portfolio_id" }
      }
    },
    {
      "metricId":     "tracking_error",
      "version":      1,
      "dataAffinity": ["portfolio", "benchmarks"],
      "costWeight":   2.0,
      "physicalMapping": {
        "backendId":   "benchmark-data-service",
        "endpoint":    "/odata/v1/TrackingError",
        "joinKeys":    { "portfolio": "portfolio_id" }
      }
    }
  ],
  "dimensions": [
    { "id": "portfolio", "physicalKey": "portfolio_id" }
  ],
  "time": {
    "period":         "quarter_to_date",
    "as_of_date":     "2026-05-14",
    "resolved_range": { "from": "2026-04-01", "to": "2026-05-14" }
  },
  "filters": [
    {
      "dimension": "portfolio",
      "operator":  "in",
      "values":    ["GLOB_EQ_OPP", "UK_CORE_INC"],
      "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')"
    }
  ],
  "sort":  [{ "metric": "portfolio_return", "direction": "desc" }],
  "limit": 100,
  "governance": {
    "estimated_cost_units": 480,
    "classification":       "internal",
    "entitlement_hash":     "sha256:a3f91c..."
  }
}
```

The LQP is the interface contract between the Analytical Intent Validator and the FQP. It contains no backend-specific syntax — only resolved metric identifiers, physical mapping references, and governance metadata. The FQP is the only component that reads `physicalMapping` and generates backend-specific query syntax from it.

---

### Role-Aware Projection Layer

The Role-Aware Projection Layer sits between the Semantic Intent Layer and the Analytical Intent Validator. It extracts entitlement claims from the request JWT, resolves them against the tenant's role policy, and injects row predicates and column masks into the LQP before it reaches the FQP.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom middleware (TypeScript) | Thin and stateless; operates on the resolved LQP before any backend query is generated |
| **Role resolution** | JWT claim extraction + tenant role config lookup (PostgreSQL) | Role claim field name is configurable per tenant (`entitlements.roleClaimField`); roles are matched against the tenant's role table, not hardcoded |
| **Row predicate injection** | Template interpolation at LQP build time | Predicates reference `{{user.claim_name}}` tokens resolved from JWT claims; injected as additional filter predicates in the LQP `filters` array |
| **Column masking** | Applied to assembled result after FQP execution | Column masks are applied post-assembly in the FQP result assembler, not at the SQL level, to support cross-backend results |
| **Default policy** | `defaultDenyAll: true` | No access unless a matching role is found; opt-in per-tenant to `defaultDenyAll: false` for public metric sets |

#### `analytics.role_policies` table (PostgreSQL DDL)

```sql
CREATE TABLE analytics.role_policies (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        TEXT        NOT NULL,
  role_name        TEXT        NOT NULL,  -- matches value in JWT role claim array
  allowed_metrics  TEXT[],               -- NULL = all approved metrics; explicit array = allow-list
  denied_metrics   TEXT[],               -- explicit deny (takes precedence over allowed_metrics)
  row_predicates   JSONB,                -- per-dimension row filter templates
  column_masks     JSONB,                -- per-metric column suppression rules
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_role_per_tenant UNIQUE (tenant_id, role_name)
);
```

#### Example role policy (JSON representation of a `row_predicates` + `column_masks` record)

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
      "condition": "{{user.roles}} NOT CONTAINS 'senior_analyst'",
      "action":    "suppress",
      "replacement": null
    }
  }
}
```

When a `regional_analyst` user with `managed_portfolios: ["GLOB_EQ_OPP"]` requests `portfolio_return`, the projection layer injects `portfolio_id IN ('GLOB_EQ_OPP')` as an additional filter predicate before the LQP reaches the FQP. The FQP never sees which portfolios the user manages — only the resolved predicate.

---

### Semantic Execution Governance

The governance engine sits between the LQP and FQP submission. It enforces cost budgets, query classification gates, and compliance mode constraints before any backend execution begins.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom rules engine (TypeScript) | Deterministic; no ML inference; rules are config-driven and auditable |
| **Cost estimation** | Weighted formula: `sum(metric.costWeight × dimensionCardinality × timeRangeMultiplier)` | Estimated before execution; actual cost tracked post-execution and used to calibrate future estimates |
| **Circuit breaker** | Per-request cost ceiling + per-user hourly budget | Hard ceiling prevents runaway queries; hourly budget prevents sustained abuse |
| **Config store** | PostgreSQL (`analytics.governance_config` table) | Governance thresholds are per-tenant configuration, not code |

#### `analytics.governance_config` table (PostgreSQL DDL)

```sql
CREATE TABLE analytics.governance_config (
  tenant_id              TEXT    PRIMARY KEY,
  cost_ceiling_per_query INT     NOT NULL DEFAULT 2000,  -- cost units; request blocked above this
  cost_budget_per_user_hourly INT NOT NULL DEFAULT 10000,
  max_concurrent_queries INT     NOT NULL DEFAULT 20,
  max_metrics_per_query  INT     NOT NULL DEFAULT 10,
  max_dimensions         INT     NOT NULL DEFAULT 5,
  classification_gate    TEXT    NOT NULL DEFAULT 'internal',  -- queries above this level require justification
  compliance_modes       TEXT[]  NOT NULL DEFAULT '{}',        -- e.g. ARRAY['mifid2', 'basel3']
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Example governance decision record (emitted per request)

```json
{
  "governance_decision_id": "gov_20260514_093247_a1b2",
  "lqp_id":    "lqp_20260514_093247_a1b2c3",
  "tenant_id": "acme-wealth",
  "user_sub":  "user_pm_001",
  "checks": [
    { "check": "cost_ceiling",        "estimated_cost": 480, "ceiling": 2000, "passed": true },
    { "check": "user_hourly_budget",  "consumed": 1240, "limit": 10000, "passed": true },
    { "check": "concurrent_limit",    "active_queries": 3, "limit": 20, "passed": true },
    { "check": "classification_gate", "level": "internal", "gate": "internal", "passed": true },
    { "check": "compliance_mifid2",   "triggered": false, "passed": true }
  ],
  "decision": "approved",
  "decided_at": "2026-05-14T09:32:47.112Z"
}
```

---

### Federated Query Planner (FQP)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Plan optimiser** | Apache Calcite (query plan optimisation, SQL sub-plan generation) | Battle-tested; used by Trino, Flink, Beam; strong SQL dialect support for warehouse backends |
| **Backend adapter layer** | Custom adapter per backend type | Calcite handles SQL backends; custom adapters translate LQP fragments to REST/OpenData/GraphQL/SPARQL for non-SQL backends |
| **Result assembly** | Custom (TypeScript) | Simple fan-out/fan-in pattern; no off-the-shelf library required |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Trino (as federation engine) | Excellent SQL federation; does not natively query REST/Graph APIs; viable for SQL-only deployments |
| Starburst Galaxy | Managed Trino; same limitations for API backends; cost tier |
| Custom from scratch | Reinventing Calcite's optimiser is not justified; hybrid approach preferred |

#### FQP sub-plan decomposition (JSON)

The FQP splits the LQP into sub-plans by `dataAffinity`. The example LQP above (two metrics, two affinities) produces:

```json
{
  "fqp_plan_id": "fqp_plan_20260514_093247",
  "lqp_id":      "lqp_20260514_093247_a1b2c3",
  "sub_plans": [
    {
      "id":              "sp_a",
      "metrics":         ["portfolio_return"],
      "dimensions":      ["portfolio_id"],
      "time":            { "from": "2026-04-01", "to": "2026-05-14" },
      "filters":         [{ "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')" }],
      "data_affinity":   "portfolio",
      "assigned_backend": "snowflake-primary",
      "generated_query": {
        "dialect": "snowflake",
        "sql": "SELECT p.portfolio_id, p.portfolio_name, SUM(pd.market_value * pd.daily_return) / SUM(pd.market_value) AS portfolio_return FROM fact_portfolio_daily pd JOIN dim_portfolio p ON pd.portfolio_id = p.portfolio_id WHERE pd.price_date BETWEEN '2026-04-01' AND '2026-05-14' AND pd.portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC') GROUP BY p.portfolio_id, p.portfolio_name ORDER BY portfolio_return DESC"
      }
    },
    {
      "id":              "sp_b",
      "metrics":         ["tracking_error"],
      "dimensions":      ["portfolio_id", "benchmark_id"],
      "time":            { "period": "trailing_12m", "as_of_date": "2026-05-14" },
      "filters":         [{ "predicate": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')" }],
      "data_affinity":   "benchmarks",
      "assigned_backend": "benchmark-data-service",
      "generated_query": {
        "dialect": "odata",
        "url":     "/odata/v1/TrackingError",
        "params": {
          "$filter": "portfolio_id in ('GLOB_EQ_OPP','UK_CORE_INC') and as_of_date eq 2026-05-14",
          "$select": "portfolio_id,benchmark_id,tracking_error_annualised"
        }
      }
    }
  ],
  "join_keys":         ["portfolio_id"],
  "assembly_strategy": "left_join_on_portfolio_id"
}
```

#### Backend adapter TypeScript interface

All FQP adapters implement this contract. Custom adapters registered via the `custom` backend type must satisfy the same interface:

```typescript
interface FQPBackendAdapter {
  readonly backendType: BackendType;

  /** Called by the FQP health checker on startup and on CATALOG_UPDATED events. */
  ping(): Promise<{ healthy: boolean; latencyMs: number }>;

  /** Translate a sub-plan fragment into a backend-specific query and execute it. */
  executeSubPlan(
    subPlan:     SubPlanFragment,
    credentials: BackendCredentials
  ): Promise<SubPlanResult>;
}

interface SubPlanFragment {
  id:           string;
  metrics:      string[];
  dimensions:   string[];
  time:         ResolvedTimeRange;
  filters:      PhysicalPredicate[];
  dataAffinity: string;
}

interface SubPlanResult {
  subPlanId:       string;
  status:          "success" | "partial" | "error";
  rows:            Record<string, unknown>[];
  rowCount:        number;
  latencyMs:       number;
  costUnits:       number;
  warningMessage?: string;   // populated on "partial" (e.g. timeout with partial rows)
  errorCode?:      string;   // populated on "error"
}
```

---

### Execution backends (supported adapters)

The FQP backend adapter layer ships with adapters for the following:

| Backend type | Adapter | Protocols supported |
|-------------|---------|-------------------|
| **SQL data warehouse** | Calcite-based SQL adapter | Snowflake SQL, BigQuery SQL, Databricks SQL, Redshift SQL, Trino SQL, Starburst Enterprise, PostgreSQL |
| **Semantic layer** | Semantic layer adapter | dbt Semantic Layer (MetricFlow), Cube.js API |
| **OpenData API** | REST/OData adapter | REST JSON, OData v4, SOAP (via adapter shim) |
| **Graph Data API** | Graph adapter | Neo4j Bolt, Amazon Neptune SPARQL, OpenCypher REST |
| **OLAP engine** | OLAP adapter | Apache Druid, ClickHouse, Pinot |
| **Custom** | Custom adapter interface | Host-implemented adapter conforming to the LQP fragment adapter protocol |

**Named products here are adapter targets, not platform dependencies.** The platform does not require any specific backend; the host registers whichever backends they operate.

---

### Ecosystem complementary services

Three shared ecosystem services integrate with the platform as registered execution backends and config-time resources. They are not owned or operated by the platform — they are external services that the platform is designed to work with.

| Service | Integration type | Implementation choice | Rationale |
|---------|-----------------|----------------------|-----------|
| **Semantic Registry Service** | Config-time resource — `POST /v1/smr/import` | REST API client in the Platform Admin API service | Import is infrequent (setup + version updates); a lightweight REST call from the Admin API service is sufficient; no persistent connection needed |
| **Regulatory Reference Service** | Runtime execution backend — registered in Data Source Catalog with `dataAffinity: ["regulatory"]` | Custom FQP adapter (REST/OData) using the OpenData API adapter pattern | Regulatory data is read-only reference data; the OpenData adapter pattern handles it without a specialised driver |
| **Benchmark Data Service** | Runtime execution backend — registered in Data Source Catalog with `dataAffinity: ["benchmarks"]` | Custom FQP adapter (REST/OData) using the OpenData API adapter pattern | Same adapter pattern as Regulatory Reference Service; benchmark data is time-series reference data over a REST endpoint |

**Integration notes:**
- Both runtime services (Regulatory Reference, Benchmark Data) are registered in the Data Source Catalog at tenant setup and routed by the FQP via `dataAffinity` matching — no special-casing in the FQP core
- Licensing enforcement for the Benchmark Data Service is handled at the service level — the FQP adapter propagates `BENCHMARK_NOT_LICENSED` errors as structured sub-plan failures
- If either runtime service is unavailable, the FQP falls back to the next registered backend with matching `dataAffinity`, or returns a partial result with a structured warning if no fallback is configured

---

### Visualisation Ontology — SCL implementation

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Chart specification format** | Vega-Lite v5 JSON | Industry-standard chart grammar; declarative; excellent ecosystem support across web, server-side, and image rendering; composable for complex charts |
| **Table spec** | Platform-defined `type: "table"` extension | Vega-Lite has no native table mark; minimal JSON extension using the same `data` + `columns` convention is more ergonomic than a separate format |
| **SCL concept name** | "Semantic Charting Language (SCL)" | Product-spec-level abstraction; decouples product design from the specific format library |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Plotly JSON | Strong financial chart types (candlestick, OHLC); larger spec size; less portable to SSR environments |
| Apache ECharts spec | High performance for large datasets; less standard outside enterprise BI; library size |
| Observable Plot spec | Modern and composable; less mature; smaller ecosystem for server-side rendering |
| Custom schema | Reinventing the grammar is not justified; Vega-Lite is widely understood and tooled |

#### Example SCL chart spec (line chart — portfolio return over time)

A complete SCL document returned in the `display_spec` field of an `analyse_metric` response:

```json
{
  "type": "chart",
  "mark": "line",
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
    "x": {
      "field":     "date",
      "type":      "temporal",
      "title":     "Date",
      "axis":      { "format": "%b %d" }
    },
    "y": {
      "field":    "portfolio_return",
      "type":     "quantitative",
      "title":    "Portfolio Return (%)",
      "axis":     { "format": ".2f" }
    },
    "color": {
      "field":    "portfolio",
      "type":     "nominal",
      "legend":   { "title": "Portfolio" }
    }
  },
  "colorScheme": "category10",
  "title":       "Portfolio Return — Quarter to Date (as of 14 May 2026)",
  "formatHints": {
    "yUnit":     "percent",
    "yDecimals": 2,
    "suffix":    "%"
  }
}
```

#### Example SCL table spec

```json
{
  "type": "table",
  "columns": [
    { "field": "portfolio_name",  "label": "Portfolio",       "width": 200 },
    { "field": "portfolio_return","label": "Return (%)",      "format": { "type": "percent", "decimals": 2 } },
    { "field": "tracking_error",  "label": "Tracking Error (%)","format": { "type": "percent", "decimals": 2 } }
  ],
  "data": [
    { "portfolio_name": "Global Equity Opportunities", "portfolio_return": 3.42, "tracking_error": 2.11 },
    { "portfolio_name": "UK Core Income",              "portfolio_return": 2.10, "tracking_error": 1.87 }
  ],
  "thresholds": [
    {
      "column":    "tracking_error",
      "condition": "gt",
      "value":     2.0,
      "style":     { "backgroundColor": "#FFF3CD", "fontWeight": "bold" }
    }
  ],
  "title": "Portfolio Return and Tracking Error — Quarter to Date"
}
```

The `thresholds` array drives cell-level highlighting in the consumer's grid component. The platform determines the threshold values from metric governance config; the consumer applies the style using its own rendering library.

---

### Static image rendering service (vite2img)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Service name** | vite2img | Internal service name |
| **Implementation** | Vite + vega-embed + headless Chromium (via Playwright) | Renders full Vega-Lite specs to SVG/PNG with pixel-accurate output; handles both chart and table specs |
| **Table spec rendering** | Custom HTML table template | For `type: "table"` display specs, renders to a styled HTML table via Playwright screenshot |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Node.js vega-lite CLI | No browser rendering; limited CSS control for table specs |
| Puppeteer-based Vega renderer | Viable; Playwright preferred for reliability and API ergonomics |
| Observable Runtime (server-side) | Complex dependency; not necessary given Vega-Lite's native SVG output |

---

### Consumer-side rendering (reference implementations)

The platform does not mandate a consumer rendering library. The following are the **reference implementations** used in internal consumer products:

| Consumer | Chart rendering | Table rendering |
|---------|----------------|----------------|
| AI Chat Platform | vega-embed (Vega-Lite renderer) embedded in content rendering pipeline | Native data table component |
| Custom host UI | vega-embed (recommended) or any Vega-Lite-compatible library | Host's own grid component |
| Static image service | vite2img service | vite2img service |

**Viable alternatives for host-built consumers:**

| Library | Format compatibility | Notes |
|---------|---------------------|-------|
| vega-embed | Vega-Lite v5 (native) | Recommended; direct SCL compatibility |
| ECharts | Not directly compatible | Requires SCL-to-ECharts spec translation layer |
| Plotly.js | Not directly compatible | Requires translation layer |
| D3.js | Manual implementation | Full control; significant development effort |

---

### Narrative Synthesis Engine

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Provider** | Anthropic (Claude) | Same provider as intent resolution; consistent governance patterns; strong instruction following for constrained prose |
| **Default tier** | Claude Haiku (fast tier) | Narrative prose does not require deep reasoning; fast tier provides acceptable quality at low latency |
| **Complex narratives** | Claude Sonnet (standard tier) | Multi-portfolio attribution narratives with many outliers; complex regulatory narratives |

---

### Analytical Lineage Store

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Lineage records** | PostgreSQL | Structured; queryable; strong ACID guarantees for audit integrity |
| **Result artefacts** | S3-compatible object storage | Large result sets and CSV downloads stored as blobs; referenced by URL in lineage records |
| **Retention** | Configurable per compliance mode; default 7 years for regulated deployments | MiFID II and similar regimes require multi-year audit trails |

**Alternatives considered:**

| Alternative | Why not chosen |
|------------|---------------|
| Apache Atlas (lineage graph) | Enterprise-grade; heavy; not necessary for the lineage schema defined in this product |
| OpenLineage + Marquez | Excellent standard for pipeline lineage; better fit for ETL/data pipeline contexts than query result lineage |
| Custom graph database | Not justified; relational model is sufficient for the query → result lineage chain |

#### `analytics.lineage_records` table (PostgreSQL DDL)

```sql
CREATE TABLE analytics.lineage_records (
  result_id          TEXT        PRIMARY KEY,          -- e.g. "res_20260514_093247_a1b2c3"
  tenant_id          TEXT        NOT NULL,
  user_sub           TEXT        NOT NULL,             -- JWT sub claim
  lqp_id             TEXT        NOT NULL,
  fqp_execution_id   TEXT,                             -- null on cache hit
  cache_hit          BOOLEAN     NOT NULL DEFAULT FALSE,
  request_payload    JSONB       NOT NULL,             -- full MCP tool call input
  resolved_metrics   JSONB       NOT NULL,             -- metric IDs + versions + dataAffinity
  governance_decision JSONB      NOT NULL,             -- full governance decision record
  sub_plans          JSONB,                            -- FQP sub-plan execution records
  result_summary     JSONB       NOT NULL,             -- row count, column count, latency, cost
  error_code         TEXT,                             -- null on success
  compliance_mode    TEXT,                             -- "mifid2" | "basel3" | "sec_reg_bi" | null
  compliance_meta    JSONB,                            -- regime-specific fields (business justification, etc.)
  result_artefact_url TEXT,                            -- S3 URL for large result set; null for cached/small
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at         TIMESTAMPTZ NOT NULL             -- DEFAULT: 7 years from created_at
);

CREATE INDEX idx_lineage_tenant_user  ON analytics.lineage_records (tenant_id, user_sub, created_at DESC);
CREATE INDEX idx_lineage_tenant_time  ON analytics.lineage_records (tenant_id, created_at DESC);
CREATE INDEX idx_lineage_result_id    ON analytics.lineage_records (result_id);
CREATE INDEX idx_lineage_compliance   ON analytics.lineage_records (tenant_id, compliance_mode) WHERE compliance_mode IS NOT NULL;
```

#### Example lineage record (`result_summary` + `sub_plans` fields)

```json
{
  "result_id":       "res_20260514_093247_a1b2c3",
  "tenant_id":       "acme-wealth",
  "user_sub":        "user_pm_001",
  "lqp_id":          "lqp_20260514_093247_a1b2c3",
  "fqp_execution_id":"fqp_exec_20260514_093247",
  "cache_hit":       false,
  "resolved_metrics": [
    { "metricId": "portfolio_return", "version": 2 },
    { "metricId": "tracking_error",   "version": 1 }
  ],
  "governance_decision": {
    "decision": "approved",
    "estimated_cost_units": 480
  },
  "sub_plans": [
    {
      "id":            "sp_a",
      "engine_id":     "snowflake-primary",
      "metrics":       ["portfolio_return"],
      "status":        "success",
      "latency_ms":    1240,
      "rows_returned": 2,
      "cost_units":    300
    },
    {
      "id":            "sp_b",
      "engine_id":     "benchmark-data-service",
      "metrics":       ["tracking_error"],
      "status":        "success",
      "latency_ms":    890,
      "rows_returned": 2,
      "cost_units":    180
    }
  ],
  "result_summary": {
    "row_count":            2,
    "column_count":         3,
    "assembly_latency_ms":  45,
    "total_latency_ms":     1285,
    "total_cost_units":     480,
    "cache_written":        true,
    "cache_ttl_seconds":    3600
  }
}
```

Lineage records are immutable once written. Amendments (e.g. compliance annotation after the fact) are written as a separate `analytics.lineage_amendments` record referencing the original `result_id`, not as updates to the primary record.

---

## Infrastructure

| Component | Platform | Rationale |
|-----------|---------|-----------|
| Edge runtime | Cloudflare Workers | Global, low-latency MCP API surface |
| Backend services | Kubernetes (cloud-agnostic) | FQP, governance, SMR services as independently scalable pods |
| Primary database | PostgreSQL (managed, e.g. Neon or RDS) | SMR, lineage store, tenant config |
| Search | Elasticsearch / OpenSearch | SMR metric search index |
| Object storage | S3-compatible | Result artefacts, cached result sets |
| Message queue | Cloud-native (e.g. SQS, Pub/Sub) | Async lineage writes, governance audit events |
| Secrets management | HashiCorp Vault or cloud-native equivalent | Backend API keys, platform service credentials |

---

## Version compatibility matrix

| Platform version | Vega-Lite (SCL) | MCP protocol | Node.js |
|-----------------|----------------|-------------|---------|
| v1.0 | 5.x | MCP 1.x (Streamable HTTP) | 22 LTS |
