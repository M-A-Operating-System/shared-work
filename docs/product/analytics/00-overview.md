# 00 — Overview

## Vision

### Governed AI analytics for any regulated application

The **AI Analytics Platform** enables any application to give its users a governed, explainable, role-aware analytical intelligence layer — without building semantic query infrastructure. The experience is modelled on the best institutional analytics environments: deterministic metric resolution, auditable execution, role-enforced data access, and AI-generated insights that are always anchored to governed, registered business definitions.

It is not a general-purpose analytics tool and not a natural-language SQL interface. Each deployment is a **governed analytical specialist** configured to its host application's metric domain, entitlement model, and regulatory context.

> **Governing intent:** Give any application team the ability to deploy a production-grade, governed AI analytics layer into their product within days — fully scoped to their semantic metric domain, connected to their execution engines via a federated query planner, enforcing their entitlement model, and producing a complete analytical lineage trail for every query.

### What the platform is and is not

| It is | It is not |
|-------|-----------|
| A white-label governed semantic analytics layer any application can embed as a web component | A general-purpose SQL query interface or BI tool replacement |
| A platform where all AI-accessible metrics are registered, governed, and version-controlled in a Semantic Metrics Registry | A system that allows LLMs to generate arbitrary SQL against physical schemas |
| A federated query engine that routes governed analytical plans to appropriate execution backends | A single-engine analytics layer coupled to one database or warehouse |
| A role-aware entitlement enforcement layer applied at the semantic tier before execution | A system that relies on database-level access controls as the primary security boundary for AI queries |
| A deterministic visualisation engine governed by a Visualisation Ontology | A system that allows LLMs to select chart types ad hoc without a governing contract |
| A complete analytical lineage trail from business question to execution result | A black-box analytics system with no explainability mechanism |
| A governed narrative synthesis layer anchored to registered metric values | A free-text generation layer that can introduce metric values not present in the execution result |

---

## Scope

### In scope

- Embeddable `<ai-analytics>` web component with full branding token support
- Multi-tenant architecture with complete per-tenant data isolation
- Semantic Metrics Registry (SMR) — the governing catalogue of all resolvable metrics, dimensions, hierarchies, aggregation rules, ownership assignments, and lineage metadata
- Analytics DSL — a constrained, AI-readable query language that exposes business semantics and compiles to engine-agnostic Logical Query Plans
- Federated Query Planner — routes Logical Query Plan fragments to registered execution engines and assembles results
- Role-Aware Projection Layer — applies entitlement filters (row restrictions, column masks, metric visibility rules) at the semantic tier before plan compilation
- Semantic Execution Governance — circuit breakers, cost controls, query complexity limits, and compliance classification checks applied before any physical engine call
- Visualisation Ontology — a governed schema of chart contracts, interaction semantics, drilldown definitions, and rendering parameters
- MCP Capability Layer — exposes bounded, pre-defined analytical operations to AI orchestrators via MCP-compatible interfaces
- Narrative synthesis — LLM-generated prose explanations anchored to execution results, governed to prohibit metric hallucination
- Analytical lineage trail — complete, queryable lineage from intent resolution through semantic planning, execution, and result delivery
- Financial services reference semantic model — pre-built metric definitions for wealth management, banking, investment management, and regulatory reporting domains
- Host-configured analytical domain scoping, metric access policies, and execution engine registration
- Governed drilldown — traversal of registered analytical hierarchies within host-configured scope

### Out of scope

- Direct SQL execution against host databases
- Physical schema exposure to AI model context
- Ad hoc LLM-generated SQL at any layer
- Real-time streaming data ingestion (v1)
- General-purpose BI authoring beyond governed narrative synthesis
- Cross-tenant metric federation
- Unauthenticated analytical access

---

## Platform architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        Host Application                             │
│                                                                    │
│   ┌──────────────────────────────────────────────┐                │
│   │         <ai-analytics> web component          │                │
│   │    (embedded in host application UI)          │                │
│   └───────────────────┬──────────────────────────┘                │
│                        │  Authentication bridge (JWT + role claims) │
└────────────────────────┼───────────────────────────────────────────┘
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
│  │                 Analytics DSL Compiler                       │  │
│  │  (governed DSL → Logical Query Plan)                        │  │
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
│  │             Visualisation Ontology + Renderer                │  │
│  │  (deterministic chart selection, parameterisation, render)   │  │
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
│ Engine A       │ │ Engine B        │ │ Engine C            │
│ (e.g. Snowflake│ │ (e.g. Databricks│ │ (e.g. dbt Semantic  │
│  / BigQuery)   │ │  / Trino)       │ │  Layer / Cube)      │
└────────────────┘ └────────────────┘ └────────────────────┘
```

### Components

**Semantic Intent Layer** receives natural language from the user or AI orchestrator, resolves it against the SMR, and produces a structured analytical intent representation — the set of metrics, dimensions, filters, and hierarchy traversals being requested.

**Semantic Metrics Registry (SMR)** is the governing catalogue of all resolvable analytical concepts. It defines what can be queried, how metrics are computed, what dimensions are permissible, and who owns each definition. It is the single source of truth for metric semantics across the platform.

**Role-Aware Projection Layer** applies the authenticated user's entitlement claims against the resolved intent. It filters the metric set to what the user is permitted to see, injects row-level security predicates, and applies column-level masking rules — before any query plan is compiled.

**Analytics DSL Compiler** translates the projected analytical intent into an engine-agnostic Logical Query Plan (LQP) expressed in the platform's Analytics DSL. The LQP is a directed acyclic graph (DAG) of analytical operations with no physical engine references.

**Semantic Execution Governance** validates the LQP against circuit breakers (cost estimates, complexity limits, data classification compliance) before releasing it to the Federated Query Planner.

**Federated Query Planner (FQP)** decomposes the LQP into engine-specific sub-plans, routes them to registered execution engines, handles result assembly, and manages caching and materialisation.

**Visualisation Ontology + Renderer** receives the assembled result set and applies the governing Visualisation Ontology to select a chart contract, parameterise it from the result schema, and produce a rendered visualisation.

**Narrative Synthesis Engine** generates governed prose explanations of the result, anchored exclusively to the values present in the execution result — LLM hallucination of metric values is architecturally prohibited.

**Analytical Lineage Store** persists the complete chain from intent to result for every query, providing explainability and regulatory audit support.

---

## Dependencies

| Dependency | Role |
|------------|------|
| **AI provider** | Provider-agnostic abstraction used by the Semantic Intent Layer and Narrative Synthesis Engine. The platform maps tiers to the tenant's configured provider's current models. |
| **Platform storage** | Relational database with RLS for SMR records, lineage records, and configuration; object storage for cached result sets and artefacts. |
| **Platform edge function** | JWT handling, intent resolution API, DSL compilation, governance checks, FQP orchestration, rendering pipeline. |
| **Host authentication** | The host application issues JWTs for its users, including role claims used by the Role-Aware Projection Layer. |
| **Host execution engines** | The host's registered analytical backends (data warehouses, semantic layers, OLAP engines) that execute physical query plans. |
| **Semantic Registry Service** | Complementary ecosystem service — a curated library of pre-built metric definitions for financial services domains. |
| **Regulatory Reference Service** | Complementary ecosystem service — regulatory metric definitions for compliance reporting (Basel III/IV, IFRS 9, MiFID II, etc.). |
| **Benchmark Data Service** | Complementary ecosystem service — market benchmark and index data integrated as dimensional reference data. |
