# AI Analytics Platform — Product Design & Technical Specification

|                     |                                                                         |
|---------------------|-------------------------------------------------------------------------|
| **Document status** | Draft v2.0                                                              |
| **Product area**    | AI Analytics Platform — governed analytical backend service             |
| **Author**          | Andrew Bush                                                             |
| **Date**            | May 2026                                                                |
| **Audience**        | Enterprise-wide technical audience — product, architecture, engineering, compliance |

---

## Abstract

The AI Analytics Platform is a **deterministic semantic computation engine** designed for AI-native enterprise analytics. It exposes governed, role-aware analytical capabilities to any MCP-compatible consumer (conversational AI assistants, autonomous agents, and custom applications) through a headless JSON API backed by a federated query planner, a governed Semantic Metrics Registry, and a complete analytical lineage store.

The platform eliminates Text-to-SQL as an architectural pattern for regulated analytics, replacing ad-hoc LLM query generation with a governed semantic layer where every metric is registered, every query is validated, every entitlement is enforced before execution, and every result carries a complete provenance record.

---

## Document Structure

| Chapter | Title | Contents |
|---------|-------|---------|
| [1. The Platform](./01-platform-overview.md) | Platform Overview | Analytics intelligence challenge, platform vision, design principles |
| [2. Personas and Architecture](./02-personas-and-architecture.md) | Consumer Personas and Platform Architecture | User personas, use cases, platform architecture diagrams, request flow |
| [3. Core Capabilities](./03-core-capabilities.md) | Core Platform Capabilities | Deep-dive specifications: SMR, Intent Layer, RAPL, Governance, FQP, Visualisation Ontology, Output Format, Lineage Store, MCP Layer |
| [4. Integration and Deployment](./04-integration-and-deployment.md) | Integration and Deployment | Consumer integration, platform administration, Financial Services reference model, complementary services |
| [5. Technical Implementation](./05-technical-implementation.md) | Proposed Technical Implementation | Reference stack with rationale: Cloudflare Workers, Apache Calcite, Vega-Lite, PostgreSQL lineage store, Anthropic Claude |
| [6. Success Metrics](./06-success-metrics.md) | Success Metrics | Platform and application-level metrics, governance health indicators, review cadence |
| [Appendix: Text-to-SQL Antipattern](./07-text-to-sql-antipattern.md) | Why Not Text-to-SQL? | Structural failure modes, security risks, and the case for a governed semantic layer |
| [8. Roadmap](./08-roadmap.md) | Platform Roadmap | Planned enhancements beyond the current release |

Read sequentially from Chapter 1. Each chapter assumes the previous. The appendix may be read independently as a standalone reference for teams evaluating architectural options.

---

## Key Concepts

| Term | Definition |
|------|------------|
| **[Semantic Metrics Registry (SMR)](./03-core-capabilities.md#semantic-metrics-registry)** | The governing catalogue of all resolvable analytical concepts for a tenant — metrics, dimensions, hierarchies, measure groups, and domains. Nothing is queryable that is not registered. |
| **[Logical Query Plan (LQP)](./03-core-capabilities.md#semantic-intent-layer)** | Engine-agnostic DAG of analytical operations produced by the Semantic Intent Layer. No physical backend references. |
| **[Federated Query Planner (FQP)](./03-core-capabilities.md#federated-query-planner)** | The only component with knowledge of physical backends. Decomposes the LQP into sub-plans, routes by data domain affinity, executes in parallel, assembles results. |
| **[Role-Aware Projection Layer (RAPL)](./03-core-capabilities.md#role-aware-projection-layer)** | Semantic-tier entitlement enforcement. Applies metric access filters, dimension access filters, row predicates, and column masks — before any query plan is compiled. |
| **[Semantic Execution Governance (SEG)](./03-core-capabilities.md#semantic-execution-governance)** | Suite of circuit breakers, cost controls, complexity limits, and compliance classification checks applied to every query before FQP release. |
| **[Visualisation Ontology](./03-core-capabilities.md#visualisation-ontology)** | Governed schema of chart contracts that map result schemas and intent patterns to specific chart configurations. Chart selection is deterministic — not AI-chosen. |
| **[Semantic Charting Language (SCL)](./03-core-capabilities.md#analytical-output-format)** | Platform output format for display specifications. Two types in a consistent JSON envelope: `type: "chart"` (Vega-Lite v5) and `type: "table"`. |
| **[Analytical Lineage](./03-core-capabilities.md#analytical-lineage-store)** | Computation provenance — not data lineage. A complete, queryable record of which metric definitions, aggregation rules, role projections, and backend sub-results produced each analytical result. |
| **Application Admin** | Privileged tenant user responsible for SMR integrity, entitlement policies, and governance configuration. Equivalent to a Chief Data Officer within the platform context. Must exist before go-live. |
| **vite2img** | Standalone MCP render service for static image output. Registered directly with consumers as a peer server. Not part of the Analytics Platform. |

---

## Non-Negotiable Platform Decisions

These decisions are non-negotiable architectural constraints. Each maps to one or more [Design Principles](./01-platform-overview.md#design-principles) defined in Chapter 1.

| ID | Decision | Principle |
|----|---------|-----------|
| **A1** | The platform never exposes physical schemas to AI models. All AI interaction is mediated through the SMR. | [P1](./01-platform-overview.md#design-principles) |
| **A2** | Raw query generation by LLMs is not a permitted execution path. All queries are expressed as validated MCP tool call parameters resolved against the SMR. | [P2](./01-platform-overview.md#design-principles), [P10](./01-platform-overview.md#design-principles) |
| **A3** | Every metric must be registered in the SMR before it is resolvable. Unregistered metrics cannot be queried. | [P3](./01-platform-overview.md#design-principles) |
| **A4** | Entitlements are enforced at the semantic tier — before the LQP is compiled and before any execution backend is contacted. | [P5](./01-platform-overview.md#design-principles) |
| **A5** | Every analytical result has a lineage record linking intent → semantic plan → LQP → backend execution → result. | [P4](./01-platform-overview.md#design-principles) |
| **A6** | Chart selection is deterministic and governed by the Visualisation Ontology — not inferred by the LLM per query. | [P7](./01-platform-overview.md#design-principles) |
| **A7** | The LQP is backend-agnostic. Physical execution translation is the FQP's responsibility. | [P10](./01-platform-overview.md#design-principles) |
| **A8** | Governance circuit breakers are applied at the semantic tier. No query reaches a physical backend without passing governance checks. | [P2](./01-platform-overview.md#design-principles) |
| **A9** | A single shared platform instance serves all consumers — isolation is enforced exclusively by the entitlement model and JWT role claims. | [P5](./01-platform-overview.md#design-principles) |
| **A10** | Narrative synthesis is anchored to governed metric values in the execution result. The LLM may not introduce metric values not present in the result. | [P6](./01-platform-overview.md#design-principles) |

---

*AI Analytics Platform — Product Design & Technical Specification · Confidential*
