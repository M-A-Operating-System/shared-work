# 00 — Overview

## Vision

### A deterministic semantic computation engine — used by GenAI

The **AI Analytics Platform** is a **deterministic semantic computation engine**, not a generative AI product. Given a structured analytical query — a set of metric IDs, dimensions, time period, and filters resolved against the Semantic Metrics Registry — it always computes the same answer from the same data. There is no probability, no sampling, no generation. Metric values are calculated from registered definitions applied to data retrieved from execution backends.

Generative AI is a consumer of the platform, not the platform itself. A conversational AI assistant uses the platform's MCP Capability Layer as a tool — submitting structured queries and receiving computed results. The AI narrates those results in prose. The AI never produces the numbers. The platform always produces the numbers, deterministically.

It is a shared analytical backend service: a governed, role-aware computation layer over registered data sources, accessible to any MCP-compatible consumer — applications, AI agents, or automated pipelines — without each consumer needing to build query infrastructure or implement query governance independently.

It is not a general-purpose analytics tool and not a natural-language SQL interface. It is a **governed analytical specialist** scoped to a registered Semantic Metrics Registry, a declared set of data sources, and a configured entitlement model.

The platform serves multiple consumer types simultaneously: human users querying via any MCP-compatible client, conversational AI users asking questions through the **AI Chat Platform**, and autonomous agents running scheduled or event-triggered analytical workflows. All consumers share the same governance pipeline and lineage trail.

> **Governing intent:** Give any application or agent the ability to access a production-grade, governed AI analytics layer — fully scoped to a registered semantic metric domain, connected to registered data sources via a federated query planner, enforcing a configured entitlement model, and producing a complete analytical lineage trail for every query — whether that query originates from a human user, a conversational assistant, or an autonomous agent.

### What the platform is and is not

| It is | It is not |
|-------|-----------|
| A **deterministic semantic computation engine** — the same query, the same data, the same entitlements always produce the same result; metric values are computed from registered definitions applied to data, never generated | A generative AI product — GenAI is a consumer of this platform, not the platform itself; the AI narrates results, the engine computes them |
| A headless MCP API service — it returns structured JSON result sets and optional SCL display specifications; any application or agent can consume it regardless of their UI stack | A general-purpose SQL query interface, BI tool replacement, or UI-rendering layer |
| A platform where all AI-accessible metrics are registered, governed, and version-controlled in a Semantic Metrics Registry | A system that allows LLMs to generate arbitrary SQL against physical schemas |
| A federated query planner that routes governed analytical plans to appropriate execution backends — SQL data warehouses, OpenData APIs, Graph Data APIs, semantic layers, or any registered retrieval mechanism | A single-engine analytics layer coupled to one database or query technology |
| A role-aware entitlement enforcement layer applied at the semantic tier before execution | A system that relies on database-level access controls as the primary security boundary for AI queries |
| A headless chart specification layer — the Visualisation Ontology selects chart contracts and produces SCL display specifications; rendering is always the consumer's responsibility | A system that allows LLMs to select chart types ad hoc without a governing contract, or that renders charts directly |
| A complete analytical lineage trail from business question to execution result | A black-box analytics system with no explainability mechanism |
| A governed narrative synthesis layer anchored to registered metric values | A free-text generation layer that can introduce metric values not present in the execution result |
| An MCP Capability Layer accessible to any MCP-compatible AI orchestrator — conversational assistants, autonomous agents, and pipelines alike | A data API accessible only to a specific AI platform or a specific consumer type |

---

## Guiding principles

| Principle | What it means in practice |
|-----------|--------------------------|
| **Governed by default** | No metric, query, or result escapes the governance pipeline. Circuit breakers, compliance classification, cost controls, and role enforcement apply to every request regardless of consumer type. There is no fast path that bypasses governance. |
| **Semantic, not syntactic** | All analytical intent is expressed in business vocabulary registered in the SMR. Physical schemas, SQL, and execution-engine specifics are never exposed to AI models or to consumers. The platform owns the translation from intent to execution. |
| **Headless and consumer-agnostic** | The platform produces structured JSON results and SCL display specifications. It never renders charts or generates HTML. Rendering is always the consumer's responsibility — any MCP-compatible consumer renders from the returned display specification using their own UI stack. |
| **Role enforcement at the semantic tier** | Entitlements are applied at the Role-Aware Projection Layer before any Logical Query Plan is compiled. The execution engine is not the security boundary — a query that the user is not entitled to see never reaches physical execution. |
| **Lineage for everything** | Every analytical result carries a `result_id` linking to a complete, queryable provenance chain from natural-language intent through SMR resolution, role projection, plan compilation, engine routing, and result assembly. |
| **Equal governance for all consumer types** | Human users, conversational assistants, and autonomous agents route through the same pipeline and receive results with identical metric definitions, entitlement enforcement, and lineage provenance. There is no privileged consumer class and no governance bypass. |
| **Computation, not generation** | Analytical results are computed from registered metric definitions and retrieved data — never generated by an AI model. GenAI participates at two explicitly bounded points only: translating natural language into structured query parameters (input side), and narrating computed values in prose (output side). The numbers are always the product of deterministic computation. |

---

## Deterministic computation engine — not generative AI

This distinction is foundational and must be understood before anything else in this specification.

The AI Analytics Platform is a **deterministic semantic computation engine**. Given a structured analytical query — a set of metric IDs, dimensions, a time period, and filters resolved against the Semantic Metrics Registry — the platform always computes the same answer from the same data. There is no probability, no sampling, no model inference in the computation layer. Metric values are calculated from versioned, registered definitions applied to data retrieved from execution backends.

### What generative AI does — and does not do — in this platform

Generative AI has exactly two bounded roles:

| Role | Where | What the model does | What the model cannot do |
|------|-------|--------------------|-----------------------|
| **Intent translation** | Input — Semantic Intent Layer | Converts a natural-language question into a structured set of MCP tool call parameters: metric IDs, dimension IDs, time period, filters. Output is a JSON object validated against the SMR. | Produce metric values, construct queries that bypass the SMR, or access execution backends directly. |
| **Narrative synthesis** | Output — Narrative Synthesis Engine | Writes a prose description of a computed result, strictly constrained to values present in the execution result. | Introduce metric values, comparisons, or figures not present in the computed result set. |

Every number in an analytical result is the product of computation. No number is the product of generation.

### The platform runs without generative AI

If a consumer submits a structured MCP tool call directly — explicit metric IDs, dimensions, and filters, no natural language — the Semantic Intent Layer is bypassed entirely. The computation pipeline (SMR resolution → role projection → governance → FQP → result assembly) is purely deterministic code. This is how automated agents, scheduled pipelines, and direct API integrations typically operate.

Natural language is a convenience layer over a computation engine. The computation engine is the product.

### What this means in practice

| Implication | Detail |
|-------------|--------|
| **Results are reproducible** | The same structured query at the same point in time with the same data always returns the same result. There is no run-to-run variation in the computation layer. |
| **Metric values cannot be hallucinated** | If a metric value appears in a result, it was computed from a registered definition and data from a registered backend. If the metric ID does not exist in the SMR, the query fails — it does not produce an approximation. |
| **Errors are diagnosable** | If a result is wrong, the cause is incorrect data in the backend, an incorrect metric definition in the SMR, or an incorrect intent translation (the wrong query was submitted). All three are visible in the lineage record. None is hallucination. |
| **Auditors and regulators get computed facts** | The number in the result is calculated, not estimated or inferred. The lineage record shows exactly which definition version was used and which data was retrieved to produce it. |
| **AI narrates; the engine calculates** | The AI Chat Platform, autonomous agents, and any other GenAI consumer receive the platform's computed results and may describe, summarise, or act on them. They do not produce the underlying analytical values. |

---

## Scope

### In scope

- Headless MCP API (`POST /v1/mcp`) — the sole entry point for all consumers; returns structured JSON result sets and SCL display specifications; no rendering layer
- Data Source Catalog — the platform's registry of all available execution backends and the data domains they serve; the FQP routes queries to backends by data domain affinity declared in the SMR
- Semantic Metrics Registry (SMR) — the governing catalogue of all resolvable metrics, dimensions, hierarchies, aggregation rules, ownership assignments, and lineage metadata
- Analytical Intent Validator — validates MCP tool call parameters (metric IDs, dimension IDs, time periods, filters) against the SMR, applies role projection, and compiles to an engine-agnostic Logical Query Plan; no custom query language — the MCP JSON parameter format is the query interface
- Federated Query Planner — routes Logical Query Plan fragments to registered execution backends and assembles results; backends may be SQL-based data warehouses, OpenData APIs, Graph Data APIs, semantic layers, or any other registered retrieval mechanism
- Role-Aware Projection Layer — applies entitlement filters (row restrictions, column masks, metric visibility rules) at the semantic tier before plan compilation
- Semantic Execution Governance — circuit breakers, cost controls, query complexity limits, and compliance classification checks applied before any backend call
- Visualisation Ontology — a governed schema of chart contracts, interaction semantics, drilldown definitions, and chart contract parameters; produces a Semantic Charting Language (SCL) display specification returned to the consumer — the platform does not render charts
- MCP Capability Layer — exposes bounded, pre-defined analytical operations to AI orchestrators via MCP-compatible interfaces
- Narrative synthesis — LLM-generated prose explanations anchored to execution results, governed to prohibit metric hallucination
- Analytical lineage trail — computation provenance (not data lineage): a complete, queryable record of which metric definitions, aggregation rules, role projections, and backend sub-results the engine used to calculate each specific response
- Example industry model (Financial Services) — a reference set of pre-built metric definitions for wealth management, banking, investment management, and regulatory reporting; demonstrates the model packaging pattern for other industry domains
- Host-configured analytical domain scoping, metric access policies, and execution engine registration
- Governed drilldown — traversal of registered analytical hierarchies within host-configured scope

### Out of scope

- Chart or table rendering of any kind — consumers are responsible for all display
- Web component or UI embedding layer — any such component is a separate consumer product
- Direct query execution against host data sources — all queries are expressed as Logical Query Plans and executed via registered backends
- Exposure of physical data source schemas, endpoints, or query languages to AI model context
- Ad hoc query generation against unregistered data sources at any layer
- Real-time streaming data ingestion (v1)
- General-purpose BI authoring beyond governed narrative synthesis
- Cross-tenant metric federation
- Unauthenticated analytical access

---

## Platform architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                   Consumer (any MCP-compatible caller)              │
│                                                                    │
│   AI Chat Platform · autonomous agent · custom application         │
│   — presents user JWT with role claims                             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                         │
                         │  POST /v1/mcp  (JWT + MCP tool call)
                         │
┌────────────────────────▼───────────────────────────────────────────┐
│                   AI Analytics Platform                             │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  Semantic Intent Layer                       │  │
│  │  (LLM resolves natural language → analytical intent)        │  │
│  └─────────────────────┬───────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │             Semantic Metrics Registry (SMR)                  │  │
│  │  (governed metric definitions, dimensions, hierarchies,      │  │
│  │   aggregation rules, lineage, ownership, access policies)    │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │              Role-Aware Projection Layer                     │  │
│  │  (entitlement enforcement — rows, columns, metrics)          │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │              Analytical Intent Validator                     │  │
│  │  (MCP JSON params → SMR validation → LQP)                   │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │            Semantic Execution Governance                     │  │
│  │  (circuit breakers, cost limits, compliance classification)  │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │               Federated Query Planner (FQP)                  │  │
│  │  (routes LQP fragments to registered execution engines)      │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │             Visualisation Ontology                           │  │
│  │  (deterministic chart contract selection; SCL display spec   │  │
│  │   generated — no rendering; returned to consumer)            │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │                Narrative Synthesis Engine                    │  │
│  │  (governed LLM prose anchored to execution result values)    │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────────────────┐  │
│  │               Analytical Lineage Store                       │  │
│  │  (intent → plan → execution → result, queryable)            │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────────┐
         │               │                   │
┌────────▼───────┐ ┌─────▼──────────┐ ┌─────▼──────────────┐
│ Execution      │ │ Execution       │ │ Execution           │
│ Backend A      │ │ Backend B       │ │ Backend C           │
│ (SQL data      │ │ (OpenData API / │ │ (Graph Data API /   │
│  warehouse)    │ │  semantic layer)│ │  OLAP engine)       │
└────────────────┘ └────────────────┘ └────────────────────┘
```

### Components

**Semantic Intent Layer** receives natural language from the user or AI orchestrator, resolves it against the SMR, and produces a structured analytical intent representation — the set of metrics, dimensions, filters, and hierarchy traversals being requested.

**Semantic Metrics Registry (SMR)** is the governing catalogue of all resolvable analytical concepts. It defines what can be queried, how metrics are computed, what dimensions are permissible, and who owns each definition. It is the single source of truth for metric semantics across the platform.

**Role-Aware Projection Layer** applies the authenticated user's entitlement claims against the resolved intent. It filters the metric set to what the user is permitted to see, injects row-level security predicates, and applies column-level masking rules — before any query plan is compiled.

**Analytical Intent Validator** takes the structured JSON parameters from an MCP tool call, validates all metric and dimension IDs against the SMR, applies role-aware projection, validates semantic rules (required dimensions, aggregation compatibility, time granularity), and produces an engine-agnostic Logical Query Plan (LQP). The LQP is a directed acyclic graph (DAG) of analytical operations with no physical engine or backend references. There is no separate query language — the MCP JSON parameter format is the analytical intent representation, consistent with established semantic layer query conventions (Cube.js, MetricFlow).

**Semantic Execution Governance** validates the LQP against circuit breakers (cost estimates, complexity limits, data classification compliance) before releasing it to the Federated Query Planner. Governance applies regardless of which backend type will execute the plan.

**Federated Query Planner (FQP)** decomposes the LQP into backend-specific sub-plans, routes them to registered execution backends, handles result assembly, and manages caching and materialisation. Registered backends may include SQL-based data warehouses, OpenData APIs, Graph Data APIs, semantic layers, OLAP engines, or any other data retrieval mechanism the host has registered — the LQP is backend-agnostic and the FQP owns the translation to each backend's query or request protocol.

**Visualisation Ontology** receives the assembled result set and applies the governing Visualisation Ontology to select a chart contract and parameterise it from the result schema. It produces a **Semantic Charting Language (SCL)** display specification — a governed `display_spec` JSON object — that is returned to the consumer as part of the MCP tool response. The Analytics Platform does not render charts; rendering is always the consumer's responsibility.

**Narrative Synthesis Engine** generates governed prose explanations of the result, anchored exclusively to the values present in the execution result — LLM hallucination of metric values is architecturally prohibited.

**Analytical Lineage Store** persists the complete chain from intent to result for every query, providing explainability and regulatory audit support.

---

## Headless by design

The AI Analytics Platform is a **headless service**. It has no rendering layer and produces no HTML, SVG, or rendered UI output of any kind. Every analytical request returns a structured MCP tool response containing:

| Output field | Type | Description |
|-------------|------|-------------|
| `result_id` | string | Unique identifier for this execution result, linking to the full lineage record |
| `display_spec` | JSON object | A Semantic Charting Language (SCL) display specification — always present. Either a governed chart specification (`type: "chart"`) or a tabular specification (`type: "table"`), both in a consistent JSON envelope (see below). Consumers render from this object regardless of result shape. |
| `narrative` | string (optional) | Governed prose explanation produced by the Narrative Synthesis Engine — present when the host has enabled narrative synthesis for the tenant |

### Display spec format — Semantic Charting Language (SCL)

The platform defines a **Semantic Charting Language (SCL)** as its output format for display specifications. SCL is a declarative JSON format with two types, both in a consistent envelope. The specific implementation library that satisfies the SCL contract is defined in the technical specification.

The platform returns a single `display_spec` JSON object for every result, using a `type` discriminator so consumers always render from one consistent structure:

**Chart result** — an SCL chart specification:

```json
{
  "type": "chart",
  "mark": "bar",
  "data": { "values": [ ... ] },
  "encoding": {
    "x": { "field": "portfolio",      "type": "nominal"      },
    "y": { "field": "tracking_error", "type": "quantitative" }
  }
}
```

**Tabular result** — an SCL table specification (a minimal, platform-defined extension using the same JSON envelope):

```json
{
  "type": "table",
  "columns": [
    { "field": "portfolio",      "label": "Portfolio",      "type": "string"  },
    { "field": "tracking_error", "label": "Tracking Error", "type": "number", "format": ".2%" },
    { "field": "limit",          "label": "Limit",          "type": "number", "format": ".2%" },
    { "field": "breached",       "label": "Breached",       "type": "boolean" }
  ],
  "data": [ ... ]
}
```

The `type: "table"` spec is a deliberate, minimal extension of the SCL convention — it carries the same `data` array and typed column definitions, but signals to the consumer that a grid layout is the appropriate presentation rather than a chart. It fills the gap that chart grammar formats leave for pure tabular results without introducing a second output contract.

The Visualisation Ontology determines which shape is returned based on the result schema and the registered chart contract for the query type. Consumers always render from `display_spec.type` — they do not need to inspect the raw result to decide how to display it.

**Rendering is always the consumer's responsibility:**

| Consumer | How they render |
|---------|------------------------------|
| Custom analytics UI (host-built) | Inspect `display_spec.type`; render chart specs with a compatible chart rendering library and table specs with a grid component — both choices are the host's |
| AI Chat Platform | Native content rendering pipeline handles both chart and table spec types |
| Agentic consumers producing PDF/email reports | Pass `display_spec` to a static image rendering service (see complementary services), which converts chart and table specs to PNG or SVG for embedding in non-interactive output |
| Custom consumers | Any chart-grammar-compatible library for chart specs; any grid component for table specs |

An optional **static image rendering service** accepts a `display_spec` JSON object and returns a static image (PNG or SVG). It is independently deployable and intended for use cases where interactive rendering is unavailable — automated report generation, email delivery, PDF production, and batch pipelines. It does not interact with the Analytics Platform's governance pipeline; it receives only the already-produced display spec.

This headless design means:
- The Analytics Platform can serve any consumer regardless of their UI stack.
- A single `display_spec` field is always present — consumers never need to branch on whether a chart or table was produced.
- The governed chart contract (chart type, axis semantics, colour by meaning) is enforced at spec-generation time — consumer rendering libraries cannot override it.

---

## Dependencies

| Dependency | Role |
|------------|------|
| **AI provider** | Provider-agnostic abstraction used by the Semantic Intent Layer and Narrative Synthesis Engine. The platform maps tiers to the tenant's configured provider's current models. |
| **Platform storage** | Relational database with RLS for SMR records, lineage records, and configuration; object storage for cached result sets and artefacts. |
| **Platform edge function** | JWT handling, intent resolution API, intent validation and LQP compilation, governance checks, FQP orchestration, result assembly, SCL display spec generation. |
| **Consumer authentication** | The organisation's identity provider issues JWTs for users and service accounts, including the role claims used by the Role-Aware Projection Layer. |
| **Host execution backends** | The host's registered data retrieval backends — SQL data warehouses, OpenData APIs, Graph Data APIs, semantic layers, OLAP engines, or any other mechanism the host registers. The FQP translates Logical Query Plan fragments into each backend's native request protocol. |
| **AI Chat Platform** | The primary conversational consumer of the Analytics Platform's MCP Capability Layer. See [Role in the AI-Enablement Product Ecosystem](#role-in-the-ai-enablement-product-ecosystem) below. |
| **Static image rendering service** | Optional complementary service — accepts a `display_spec` JSON object and returns a static image (PNG or SVG). Used by agentic consumers, report pipelines, and email delivery workflows where interactive rendering is unavailable. |
| **Semantic Registry Service** | Complementary ecosystem service — a curated library of pre-built metric definitions for financial services domains. |
| **Regulatory Reference Service** | Complementary ecosystem service — regulatory metric definitions for compliance reporting (Basel III/IV, IFRS 9, MiFID II, etc.). |
| **Benchmark Data Service** | Complementary ecosystem service — market benchmark and index data integrated as dimensional reference data. |

---

## Role in the AI-Enablement Product Ecosystem

### Two-product architecture — and beyond

The AI Analytics Platform and the **AI Chat Platform** form a complementary two-layer AI-enablement offering. They are designed to be deployed together, with clear and deliberate division of responsibility:

| Layer | Product | Responsibility |
|-------|---------|---------------|
| **Conversational surface** | AI Chat Platform | Generative chat interface, conversation management, multi-modal content rendering, tool call transparency, shared conversations, memory, and audit trail. Provides the user's entry point for all interaction. Has no built-in analytical capability. |
| **Analytical backend** | AI Analytics Platform | Governed semantic metric resolution, large-scale federated query execution, role-aware entitlement enforcement, SCL display specification generation, and lineage-backed result delivery. Headless — returns structured data and display specs; has no rendering layer and no conversational surface. |

The AI Chat Platform is **one consumer** of the Analytics Platform's capabilities, not the only one. The Analytics Platform's MCP Capability Layer (see [08-mcp-capability-layer.md](./08-mcp-capability-layer.md)) is an MCP-compatible interface designed to be consumed by any AI orchestrator — the AI Chat Platform today, and additional agentic consumers in the future.

> **Architectural intent:** Any AI agent that needs to answer quantitative questions against large datasets — whether a conversational assistant, an autonomous monitoring agent, a report-generation pipeline, or a compliance review workflow — should route through the Analytics Platform's MCP Capability Layer rather than building its own data access path. The governance pipeline, role enforcement, and lineage trail apply equally to all consumers, regardless of how they invoke the capabilities.

This means the Analytics Platform's value grows with the number of AI consumers an organisation operates. As the AI ecosystem matures — multi-agent workflows, scheduled analytical agents, event-triggered compliance monitors — each new agentic consumer gets the same governed, lineage-backed analytical foundation without re-implementing query governance independently.

This separation is intentional. The AI Chat Platform remains a generic conversational infrastructure product. The AI Analytics Platform remains a governed analytical infrastructure product. Neither product needs to own what the other provides, and both can be deployed independently or together.

### Consumption modes

The AI Analytics Platform is designed for three modes of consumption, which may be used simultaneously by the same host application:

| Mode | Consumer | When to use |
|------|---------|-------------|
| **Direct API consumer** | A custom application calling `POST /v1/mcp` directly — rendering the returned JSON result sets and SCL display specifications using their own UI stack | Dedicated analytics views, dashboards, analytical workbooks built by the host team — where the application owns the rendering layer entirely |
| **Conversational backend** | AI Chat Platform, registered via `mcpServers` config | Conversational analytics — where the user asks quantitative questions in natural language; the AI Chat Platform routes tool calls to the Analytics Platform's MCP endpoint |
| **Agentic consumer** | Autonomous AI agents, scheduled pipelines, event-triggered workflows | Any AI orchestrator that needs to query large datasets, monitor metrics, generate governed reports, or trigger analytical workflows without a human in the loop — all via the same MCP Capability Layer |

All three modes route through the same governance pipeline. A portfolio manager drilling through a chart in a standalone view, asking the same question conversationally, and an overnight monitoring agent checking for limit breaches all receive results with identical metric definitions, role enforcement, and lineage provenance. There is no privileged path and no governance bypass for any consumer class.

---

### Combined platform architecture

The following diagram shows all three consumption modes operating against the same Analytics Platform backend:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              Host Application                               │
│                                                                            │
│  ┌───────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐ │
│  │  <ai-chat> component  │  │ Custom analytics UI  │  │ Agentic consumers │ │
│  │  (conversational UI)  │  │ (host-built; renders │  │ (scheduled agents,│ │
│  └──────────┬────────────┘  │  returned JSON/spec) │  │  event monitors,  │ │
│             │ JWT           └──────────┬────────────┘  │  report pipelines)│ │
└─────────────┼──────────────────────────┼───────────────┴────────┬──────────┘
              │                          │ JWT                     │ JWT
┌─────────────▼──────────────────────────▼─────────────────────────▼──────────┐
│                             AI Chat Platform                                 │
│                                                                              │
│   Conversation engine · Content rendering · Tool call routing                │
│   Audit trail · Memory · Shared conversations                                │
│                                                                              │
│   mcpServers:  [ { "id": "analytics-platform",                               │
│                    "endpoint": "…/v1/mcp",                                   │
│                    "accessTier": "always-on" } ]                             │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │                         │
                    MCP tool call │                         │ MCP tool call
                    (Chat Platform│                         │ (Agentic consumer,
                     + user JWT)  │                         │  agent JWT)
┌─────────────────────────────────▼─────────────────────────▼──────────────────┐
│                          AI Analytics Platform                                │
│                                                                               │
│  MCP Capability Layer  ──►  Semantic Intent Layer                             │
│                        ──►  Semantic Metrics Registry (SMR)                  │
│                        ──►  Role-Aware Projection Layer                       │
│                        ──►  Analytical Intent Validator                       │
│                        ──►  Semantic Execution Governance                     │
│                        ──►  Federated Query Planner (FQP)                     │
│                        ──►  Visualisation Ontology (SCL display spec generation)│
│                        ──►  Narrative Synthesis Engine                        │
│                        ──►  Analytical Lineage Store                          │
└─────────────────────────────────┬─────────────────────────────────────────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
           ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────────┐
           │ Execution   │ │ Execution   │ │ Execution        │
           │ Backend A   │ │ Backend B   │ │ Backend C         │
           │ (SQL data   │ │ (OpenData   │ │ (Graph Data API / │
           │  warehouse) │ │  API /      │ │  OLAP engine)     │
           │             │ │  sem. layer)│ │                   │
           └─────────────┘ └─────────────┘ └──────────────────┘
```

No consumer — AI Chat Platform, `<ai-analytics>` component, or agentic agent — has a path to execution engines, physical schemas, or raw SQL. Every analytical request routes through the MCP Capability Layer and the full governance pipeline. The Analytical Lineage Store records every invocation, regardless of which consumer initiated it.

---

### MCP registration

To connect the Analytics Platform to the AI Chat Platform, a host application adds the following entry to the `mcpServers` section of its AI Chat Platform application config:

```json
{
  "id":          "analytics-platform",
  "name":        "Analytics Platform",
  "description": "Governed analytical query engine. Resolves quantitative questions against registered business metrics via the Semantic Metrics Registry. Use for portfolio performance, risk decomposition, performance attribution, issuer concentration, regulatory metrics, and any question requiring large-scale data analysis. Always specify metric IDs — do not attempt to construct SQL or use unregistered identifiers. Call list_metrics first if unsure which metrics are available.",
  "endpoint":    "https://api.analytics-platform.io/v1/mcp",
  "authType":    "bearer",
  "accessTier":  "always-on",
  "roles":       []
}
```

The `description` field is injected verbatim into the AI Chat Platform's system prompt and is the primary signal the AI model uses to decide when to route a question to the Analytics Platform versus other registered MCP servers. The description above is the recommended starting point; host teams should customise it to reflect their specific metric domains.

Setting `accessTier: "always-on"` ensures the Analytics Platform's capabilities are available in every session without user action — appropriate because most quantitative questions in a governed financial application require the Analytics Platform by default.

---

### End-to-end conversational analytics flow

When a user asks a quantitative question in the AI Chat Platform, the complete flow from natural language to rendered result is:

```
User (in AI Chat Platform):
  "Show me the tracking error for each equity portfolio over the last quarter,
   and flag any that are above their mandate limit."

  ↓  AI Chat Platform routes to AI model with Analytics Platform capabilities in context

AI model:
  Resolves question → analyses_metric tool call
  {
    "metrics":    ["tracking_error", "tracking_error_limit"],
    "dimensions": ["portfolio"],
    "time_period": "quarter_to_date",
    "filters": [{ "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }],
    "order_by": "tracking_error DESC"
  }

  ↓  AI Chat Platform forwards tool call to Analytics Platform MCP endpoint
     with the user's JWT

AI Analytics Platform — governance pipeline:
  1. Input schema validation
  2. Capability availability check (feature flags + user role)
  3. SMR resolution: verify tracking_error, tracking_error_limit, portfolio dimension
  4. Role-Aware Projection: filter to portfolios the user is entitled to see
  5. Intent validation → Logical Query Plan
  6. Semantic Execution Governance: cost estimate check, compliance classification
  7. Federated Query Planner: route to registered execution engine(s)
  8. Result assembly + lineage record written

  ↓  Returns governed MCP tool response to AI Chat Platform:
     {
       "result_id":    "res_...",
       "display_spec": {
         "type":     "chart",
         "mark":     "bar",
         "data":     { "values": [ ... ] },
         "encoding": { ... }
       },
       "narrative": null   ← narrative generated in step below
     }

AI Chat Platform:
  - Renders result as data table + bar chart (from the returned SCL display spec) in conversation thread
  - Displays tool call disclosure card (collapsible): inputs, result_id, latency
  - AI model generates governed narrative:
    "Three portfolios are above their tracking error limit this quarter:
     Global Equity (4.2% vs 3.5% limit), EM Growth (5.1% vs 4.0% limit), ..."
    (values anchored exclusively to the execution result — hallucination prohibited)

User:
  "Drill into the Global Equity portfolio — break down what's driving the tracking error."

  ↓  AI model resolves to risk_breakdown tool call
     { "portfolio_id": "global-equity", "risk_metric": "tracking_error",
       "attribution_by": "factor", "as_of_date": "2026-03-31" }

  ↓  Full governance pipeline repeats; factor attribution result returned and rendered
```

At no point in this flow does the AI model construct SQL, access a physical schema, or produce a number not present in the Analytics Platform's execution result. Every quantitative claim in the conversation is backed by a lineage record in the Analytics Platform's Analytical Lineage Store, reachable via the `result_id` in the tool call disclosure card.

---

### What the integration enables

| Capability | Provided by |
|-----------|-------------|
| **Large-scale, multi-backend data analytics from a conversation** | Analytics Platform FQP routes governed plans to any registered execution backend — SQL data warehouses, OpenData APIs, Graph Data APIs, or other backends — irrespective of result set size |
| **Role-aware results without any configuration in the chat layer** | Analytics Platform's Role-Aware Projection Layer enforces entitlements before results leave the analytical backend; the AI Chat Platform surfaces only what the authenticated user is permitted to see |
| **Governed metric vocabulary, not ad hoc SQL** | The AI model calls named, registered capabilities (`analyse_metric`, `risk_breakdown`, etc.) — the Analytics Platform's SMR ensures metric definitions are consistent, versioned, and owned |
| **Deterministic chart specification** | The Analytics Platform's Visualisation Ontology selects chart types based on the result schema and metric semantics, returning a governed SCL display spec — the AI Chat Platform renders that spec, not a chart chosen ad hoc by the LLM |
| **Governed narrative synthesis** | The Narrative Synthesis Engine produces prose explanations anchored exclusively to execution result values; metric hallucination is architecturally prohibited |
| **Full analytical lineage from every conversation turn** | Every tool call disclosure card in the AI Chat Platform carries a `result_id` that maps to a complete lineage record — from natural-language intent through SMR resolution, projection, plan compilation, execution, and result delivery |
| **Complex institutional workflows as simple conversational queries** | Performance attribution, issuer concentration, risk decomposition, regulatory compliance checks — exposed as simple tool calls the AI model can compose in response to natural-language questions |
| **Drilldown continuity across turns** | The `drilldown` capability accepts a `result_id` from a prior turn, preserving parent-level filters and governance context as the user deepens their analysis across multiple conversation turns |

---

### Routing alongside other MCP servers (AI Chat Platform)

Host applications that deploy both platforms will typically register the Analytics Platform alongside their own operational MCP servers. The AI model routes between them based on the `description` fields in the `mcpServers` config:

| Server | Handles | Example queries |
|--------|---------|----------------|
| **Analytics Platform MCP** | Large-scale, governed metric computation; federated query; attribution and decomposition | *"What is the tracking error for my equity portfolios?"*, *"Break down the risk drivers for Global Equity"* |
| **Host application MCP** | Operational data, workflow actions, entity lookups, real-time state (balances, positions, alerts, approval queues) | *"Show me the latest valuation for fund XYZ"*, *"What trades are pending settlement today?"* |
| **Web Search MCP** | Current market news, regulatory announcements, external reference data | *"What did the Fed announce yesterday?"*, *"What is the current SOFR rate?"* |

For quantitative analytical questions, the AI model routes to the Analytics Platform. For operational lookups and real-time state, it routes to the host application's own servers. The `description` field on each server is the primary routing signal — the suggested `description` text above is optimised for correct routing in a financial services deployment.

### Agentic consumers

Beyond the AI Chat Platform, the Analytics Platform's MCP Capability Layer is designed to serve any MCP-compatible AI orchestrator. Anticipated agentic consumers include:

| Agent type | Example use case |
|-----------|-----------------|
| **Scheduled analytical agents** | Nightly portfolio risk summary generated against the SMR and delivered as a governed narrative; daily regulatory metric check run before market open |
| **Event-triggered monitors** | An agent that runs `risk_breakdown` automatically when a tracking error threshold is breached, producing a governed analysis for the investment committee |
| **Report-generation pipelines** | Automated investment committee pack generation — `performance_attribution`, `compare_portfolios`, and `regulatory_metric` composed into a governed narrative document; SCL display specs converted to static images via the static image rendering service for PDF embedding |
| **Compliance review agents** | Periodic mandate compliance checks using `issuer_concentration` and `regulatory_metric`, with results written to an audit log |
| **Research augmentation agents** | Agents that combine web search (current news) with governed `analyse_metric` results to produce investment research anchored to verified portfolio data |

All agentic consumers must present a valid JWT containing role claims. The Analytics Platform's Role-Aware Projection Layer enforces the same entitlement model as for human users — an agent operating with a portfolio manager's JWT receives exactly the same metric visibility and row-level security that the portfolio manager receives interactively. There is no elevated-privilege path for agents.
