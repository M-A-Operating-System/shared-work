# AI Analytics Platform — Product Design Specification

|                    |                                                                    |
|--------------------|--------------------------------------------------------------------|
| **Document status**| Draft v1.0                                                         |
| **Product area**   | AI Analytics Platform — shared governed analytical backend service |
| **Author**         | Andrew Bush                                                        |
| **Date**           | May 2026                                                           |
| **Audience**       | Product, design, and engineering — pre-build reference             |

---

## What is this?

The **AI Analytics Platform** is a governed, headless analytical intelligence layer that any application can adopt via its MCP Capability Layer. Host applications bring their own semantic metric registries, role-aware entitlement models, analytical domain configurations, and execution backends. The platform provides the semantic query engine, Analytical Intent Validator, federated query planner, visualisation ontology, MCP capability layer, and multi-tenant governed execution infrastructure.

A platform administrator registers data sources, defines the Semantic Metrics Registry, and configures entitlement policies via the Platform Admin API. Any MCP-compatible consumer — an interactive user, a conversational AI assistant, or an autonomous agent — then queries the shared service at `POST /v1/mcp` and receives governed, explainable, role-aware analytical results with complete lineage.

The platform is designed specifically for environments where governance, explainability, and semantic consistency are non-negotiable: wealth management, banking, investment management, institutional analytics, and regulated financial services.

---

## Architecture in one line

> One governed semantic layer. One federated query planner. One analytical MCP interface. Register your data sources, define your metrics, configure entitlements — then any consumer gets governed analytical access.

---

## Why a governed semantic layer, not direct SQL?

Direct LLM-to-SQL architectures are unsuitable for regulated financial environments. The platform eliminates this pattern entirely and replaces it with a layered semantic abstraction:

| Direct SQL / Text2SQL | AI Analytics Platform |
|-----------------------|-----------------------|
| LLM generates arbitrary SQL against physical schema | LLM resolves intent against a governed semantic metric registry |
| Physical schema exposed to AI context | Business semantics only — no physical schema leakage |
| Metrics defined inconsistently per query | Metrics defined once, governed centrally, version-controlled |
| No role-aware execution path | Entitlements enforced at the semantic layer before execution |
| Execution cost unpredictable | Query plans bounded by governed analytical operations |
| No lineage on AI-generated queries | Full lineage from intent → semantic plan → execution → result |
| Hallucinated metrics possible | Only registered, governed metrics are resolvable |

---

## Reading order

Start at `00` and read through in sequence. Each document assumes you have read the previous one.

| # | Document | Purpose |
|---|----------|---------|
| 00 | [00-overview.md](./00-overview.md) | Vision, what the platform is and is not, scope, architecture — **start here** |
| 01 | [01-data-source-registration.md](./01-data-source-registration.md) | Data source catalog, entitlement model, and platform administration |
| 02 | [02-personas-and-journeys.md](./02-personas-and-journeys.md) | Platform-level and financial-services-specific user archetypes and journeys |
| 03 | [03-design-principles.md](./03-design-principles.md) | Nine governing principles that take precedence over any feature decision |
| 04 | [04-semantic-metrics-registry.md](./04-semantic-metrics-registry.md) | Semantic metric definitions, dimensions, hierarchies, governance, lineage |
| 05 | [05-analytical-intent.md](./05-analytical-intent.md) | Analytical intent format, validation pipeline, and LQP generation |
| 06 | [06-federated-query-planning.md](./06-federated-query-planning.md) | Logical query DAG, federation, distributed execution, caching |
| 07 | [07-visualization-ontology.md](./07-visualization-ontology.md) | Rendering ontology, chart contracts, interaction semantics, drilldown |
| 08 | [08-mcp-capability-layer.md](./08-mcp-capability-layer.md) | MCP analytical capabilities, capability negotiation, semantic contracts |
| 09 | [09-role-aware-projections.md](./09-role-aware-projections.md) | Entitlement model, role-aware execution, data masking, row/column filtering |
| 10 | [10-analytical-output-format.md](./10-analytical-output-format.md) | Output format, display spec structure, narrative synthesis, error responses |
| 11 | [11-audit-and-storage.md](./11-audit-and-storage.md) | Multi-tenant storage, execution audit trail, lineage, retention |
| 12 | [12-governed-execution.md](./12-governed-execution.md) | Semantic execution governance, circuit breakers, cost controls, compliance |
| 13 | [13-financial-services-model.md](./13-financial-services-model.md) | Reference semantic model for wealth management and financial services |
| 14 | [14-success-metrics.md](./14-success-metrics.md) | Platform-level and application-level metrics, definitions, and targets |
| 15 | [15-consumer-integration.md](./15-consumer-integration.md) | MCP endpoint, JWT authentication, response handling, agentic consumer patterns |
| 16 | [16-complementary-services.md](./16-complementary-services.md) | Semantic Registry Service, Benchmark Data Service, Regulatory Reference Service |
| — | [ROADMAP.md](./ROADMAP.md) | Planned enhancements beyond the current release |

---

## Key concepts

| Term | Definition |
|------|------------|
| **Platform administrator** | The person or team responsible for registering data sources, managing the SMR, and configuring entitlement policies |
| **Data Source Catalog** | The platform's registry of all available execution backends and the data domains they serve |
| **Semantic Metrics Registry (SMR)** | The governed catalogue of metrics, dimensions, hierarchies, and aggregation rules that defines all resolvable analytical concepts for a tenant |
| **Analytical Intent Validator** | The platform component that validates MCP tool call parameters against the SMR, applies role projection, and compiles a Logical Query Plan — the MCP JSON parameter format is the query interface, no custom query language |
| **Logical Query Plan (LQP)** | The structured, backend-agnostic representation of a validated analytical request, produced by the Analytical Intent Validator before federation |
| **Federated Query Planner (FQP)** | The component that routes LQP fragments to appropriate execution engines and assembles results |
| **Visualisation Ontology** | The governed schema of chart types, interaction contracts, and rendering semantics used to deterministically select and parameterise visualisations |
| **MCP Capability Layer** | The MCP-style interface that exposes bounded analytical operations to AI orchestrators |
| **Role-Aware Projection** | The semantic-layer enforcement of entitlements — applying row filters, column masks, and metric restrictions before query execution |
| **Semantic Execution Governance** | The suite of circuit breakers, cost controls, and compliance checks applied at the semantic layer before any query reaches a physical execution engine |
| **Analytical Intent** | The business question expressed by a user or AI agent, resolved against the SMR before any query is formed |
| **Application Admin** | A privileged user within a tenant who manages the SMR, entitlement policies, and tenant configuration |

---

## Platform decisions

| ID | Decision |
|----|---------|
| **A1** | The platform never exposes physical schema to AI models. All AI interaction is mediated through the Semantic Metrics Registry and Analytical Intent Validator. |
| **A2** | Raw query generation by LLMs is not a permitted execution path on this platform. All queries are expressed as validated MCP tool call parameters resolved against the SMR. |
| **A3** | Every metric must be registered in the SMR before it is resolvable. Unregistered metrics cannot be queried. |
| **A4** | Entitlements are enforced at the semantic layer — before the logical query plan is compiled and before any execution engine is contacted. |
| **A5** | All analytical execution produces a lineage record linking analytical intent → semantic plan → logical query plan → execution engine call → result. |
| **A6** | Visualisation type selection is deterministic and governed by the Visualisation Ontology — not inferred ad hoc by the LLM per query. |
| **A7** | The Analytical Intent Validator produces a Logical Query Plan that is backend-agnostic. Physical execution is the responsibility of the Federated Query Planner. |
| **A8** | Cost and execution circuit breakers are applied at the semantic layer. No query reaches a physical execution engine without passing governance checks. |
| **A9** | Entitlements are the only isolation boundary. A single shared platform instance serves all consumers — access to metrics, dimensions, and data rows is controlled exclusively by the configured entitlement model and JWT role claims. |
| **A10** | Narrative synthesis (prose explanation of analytical results) is always anchored to the governed metric values returned — the LLM may not introduce metric values not present in the execution result. |

---

## Platform scope

### In scope

- Headless MCP API (`POST /v1/mcp`) — sole consumer entry point; returns structured JSON result sets and SCL display specifications
- Data Source Catalog — platform registry of all registered execution backends and the data domains they serve
- Semantic Metrics Registry — governed catalogue of metrics, dimensions, hierarchies, aggregation rules, and lineage
- Analytical Intent Validator — validates MCP tool call parameters against the SMR, applies role projection, compiles to backend-agnostic Logical Query Plans
- Federated Query Planner — routes LQP fragments to registered execution backends (SQL warehouses, OpenData APIs, Graph Data APIs, semantic layers, OLAP engines)
- Role-Aware Projection Layer — semantic-layer entitlement enforcement before execution
- Semantic Execution Governance — circuit breakers, cost controls, compliance checks
- Visualisation Ontology — deterministic chart selection and parameterisation
- MCP Capability Layer — bounded analytical operations exposed to AI orchestrators
- Narrative synthesis — governed LLM-generated prose anchored to execution results
- Governed drilldown — semantic traversal of analytical hierarchies within registered scope
- Full analytical lineage trail: intent → plan → execution → result
- Multi-tenant data isolation with row-level security
- Regulated financial services reference semantic model (wealth management, banking, investment)
- Role-aware metric registry with per-role metric visibility and aggregation restrictions
- Execution cost monitoring and circuit breakers

### Out of scope

- Direct SQL execution against host databases (by design — prohibited)
- Physical schema exposure to AI model context (by design — prohibited)
- Ad hoc LLM-generated SQL (by design — prohibited)
- Real-time streaming data ingestion (v1 — planned)
- Natural language report authoring beyond governed narrative synthesis
- Cross-tenant metric federation
- Public-facing analytical endpoints without authentication

---

*AI Analytics Platform — Product Design · Confidential*
