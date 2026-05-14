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

---

### Execution backends (supported adapters)

The FQP backend adapter layer ships with adapters for the following:

| Backend type | Adapter | Protocols supported |
|-------------|---------|-------------------|
| **SQL data warehouse** | Calcite-based SQL adapter | Snowflake SQL, BigQuery SQL, Databricks SQL, Redshift SQL, Trino SQL, PostgreSQL |
| **Semantic layer** | Semantic layer adapter | dbt Semantic Layer (MetricFlow), Cube.js API |
| **OpenData API** | REST/OData adapter | REST JSON, OData v4, SOAP (via adapter shim) |
| **Graph Data API** | Graph adapter | Neo4j Bolt, Amazon Neptune SPARQL, OpenCypher REST |
| **OLAP engine** | OLAP adapter | Apache Druid, ClickHouse, Pinot |
| **Custom** | Custom adapter interface | Host-implemented adapter conforming to the LQP fragment adapter protocol |

**Named products here are adapter targets, not platform dependencies.** The platform does not require any specific backend; the host registers whichever backends they operate.

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

| Platform version | Vega-Lite (SCL) | MCP protocol | Node.js | Rust compiler |
|-----------------|----------------|-------------|---------|--------------|
| v1.0 | 5.x | MCP 1.x (Streamable HTTP) | 22 LTS | 1.78+ |
