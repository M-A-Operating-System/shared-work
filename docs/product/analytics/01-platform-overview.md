# 1. The Platform

## The Analytics Intelligence Problem

Regulated analytics has always depended on human experts — analysts, compliance officers, quant developers — to bridge business questions and raw data. Generative AI changes that. But the most common approach for applying it to analytics, Text-to-SQL, has structural flaws that get worse as the use cases become more demanding.

The Text-to-SQL pattern — feeding a natural language question and a physical database schema to a language model, then executing the generated SQL — is the default first step most organisations take. A working demonstration is achievable in hours on a well-structured schema. Simple aggregations are handled reliably. For exploratory data work, internal tooling, and low-stakes analytical sandboxes, the pattern is a legitimate option and can accelerate genuine productivity.

The problem is that the structural defects of Text-to-SQL are largely invisible at the demonstration stage and tolerable in early deployments. They surface when the system is asked to do what regulated analytics actually requires.

When a regulator asks how a specific number was calculated, "the AI wrote some SQL and this number came back" is not an answer. When a metric definition changes due to a regulatory update, there is no versioned definition to update, no approval workflow, and no audit trail of which formula version produced which historical result. When the same metric is queried by two analysts through two different session contexts, the question of whether they received definitions consistent with one another has no reliable answer. When a user's entitlements restrict them to a subset of portfolios, the restriction's reliability is bounded by the language model's ability to generate the correct WHERE clause — a constraint that can be circumvented by sufficiently crafted input and cannot be architecturally guaranteed.

The following table maps each structural concern to its Text-to-SQL disposition and to the disposition the AI Analytics Platform is designed to provide:

| Concern | Text-to-SQL | AI Analytics Platform |
|---------|------------|------------------------------|
| Metric consistency | ✗ — definitions inferred per query | ✓ — every metric resolves to exactly one versioned SMR definition |
| Schema security | ✗ — physical schema exposed to AI model | ✓ — physical schema never visible to AI model |
| Audit trail | ✗ — no reproducible calculation record | ✓ — full computation provenance for every result |
| Entitlement enforcement | ✗ — boundary is the database credential | ✓ — enforced at the semantic tier before any backend is contacted |
| Complex query accuracy | ✗ — degrades for regulated formulas, window functions | ✓ — complex metric formulas defined once in SMR, applied deterministically |
| Metric change management | ✗ — no versioned definitions | ✓ — SMR version-controls every definition with approval workflow |
| Scope control | ✗ — attempts to answer any question | ✓ — queries with unregistered metric IDs are rejected with structured error |
| Query cost governance | ✗ — LLM-generated SQL is unpredictable in cost | ✓ — cost estimated from LQP before execution; circuit breaker blocks excess |
| Multi-source federation | ✗ — limited to single SQL target | ✓ — FQP routes to SQL warehouses, OpenData APIs, Graph Data APIs, and more |

These are not quality tradeoffs resolvable through prompt engineering, guardrails, or SQL validation layers. They are structural properties of an architecture in which a language model is both the query interface and the query generator — an architecture in which the same channel carries user intent, data access logic, and physical schema exposure simultaneously. Patching these properties incrementally typically produces a brittle, prompt-dependent approximation of a semantic layer at substantially higher ongoing cost than building the semantic layer correctly from the start.

The AI Analytics Platform is the alternative architecture: one that constrains generative AI to the narrow tasks it performs reliably, and delegates everything that must be deterministic — metric definition, entitlement enforcement, query execution, lineage recording — to deterministic components.

---

## Platform Vision

The platform comprises two separately deployable MCP servers. The **Analytics Engine** is a deterministic semantic computation engine: given explicit metric identifiers, dimensions, time period, and filters resolved against the Semantic Metrics Registry, it always computes the same answer from the same data with the same entitlements in force. No probability, no sampling, no generation — no AI runs inside it. The **Narrative Synthesis Engine** is a bounded AI service that generates governed prose from a computed result, constrained strictly to values present in that result.

AI has two roles in the end-to-end flow, and both live in the consuming AI client — not inside either MCP server. On the input side, the AI client reads the metric catalogue from the Analytics Engine's SMR resources, then translates a natural-language question into explicit, structured MCP tool call parameters. On the output side, after receiving the structured result from the Analytics Engine, the AI client calls the Narrative Synthesis Engine to produce prose. Every number in that prose is the product of computation, not generation.

This architecture supports three consumer types. Conversational AI assistants load the metric catalogue, translate natural language to structured parameters, and call both MCP servers in sequence. Autonomous agents and scheduled pipelines submit structured tool calls directly to the Analytics Engine — no natural language translation needed — and call the NSE only if narrative output is required. Custom applications call the Analytics Engine directly and own their own narrative generation or omit it entirely. The Analytics Engine's governance pipeline is identical for all three; entitlements, lineage, and semantic abstraction apply unconditionally.

The following table defines the Analytics Engine's scope precisely:

| It is | It is not |
|-------|-----------|
| A deterministic semantic computation engine — same query + data + entitlements → same result | An AI product — no AI model runs inside it |
| A headless MCP server returning structured result sets and SCL display specifications | A general-purpose SQL interface, BI tool replacement, or rendering layer |
| A governed Semantic Metrics Registry — all queryable metrics are registered, versioned, and owned | A system that accepts natural language or allows LLMs to generate arbitrary SQL |
| A federated query planner routing governed plans to SQL warehouses, OpenData APIs, Graph APIs, and any registered backend | A single-engine analytics layer |
| A role-aware entitlement layer enforced at the semantic tier before execution | A system relying on database-level access controls as the primary AI security boundary |

The Analytics Engine is explicitly headless. Every request returns a structured result set and SCL display specification. Narrative prose, rendering, and natural language translation are all consumer responsibilities — handled by the AI client and, optionally, the Narrative Synthesis Engine.

---

## Design Principles

Ten non-negotiable principles govern all design decisions for the AI Analytics Platform. Where a proposed feature conflicts with a principle, the principle takes precedence over the feature. Where two principles appear to conflict with one another, the resolution mechanism is specified in each case. These principles are not aspirational — they are architectural constraints that shape every component and every interface.

| Principle | What it means | Key consequence |
|-----------|--------------|-----------------|
| **P1 — Semantic abstraction** | The platform never exposes physical schemas, table names, or column names to AI models or end users. All AI interaction is mediated through the Semantic Metrics Registry. There is no escape hatch to raw SQL. | Unregistered concepts cannot be queried. Schema leakage is impossible by design, not by policy. |
| **P2 — Governance before execution** | Every analytical query passes through the full governance pipeline before any physical execution begins. Governance is a pre-execution gate, not a post-processing filter. There is no fast path. | The execution sequence — Intent → SMR Resolution → Role Projection → Validation → Governance → FQP → Execution — is invariant. Governance decisions are logged before any backend is contacted. |
| **P3 — Deterministic metric resolution** | A metric name resolves to exactly one governed definition for a given tenant at a given point in time. There are no context-dependent interpretations of metric semantics. "Portfolio Return" means the same thing in every query, every report, and every regulatory submission — or it is a bug. | Metric definitions are version-controlled in the SMR. Unregistered metrics return a resolution error, never an inferred definition. |
| **P4 — Complete analytical lineage** | This is not data lineage — ETL pipelines and source-to-warehouse flows are a separate concern. This is computation provenance: a complete, queryable record of exactly how the analytics engine used individual data elements to calculate a specific response. | Every result carries a full lineage chain — intent, resolved definitions, role projection, query plans, raw responses, governance decisions, and display specification. Lineage is written atomically with the result. |
| **P5 — Role-aware by default** | The platform applies entitlements without opt-in. `defaultDenyAll: true` is the platform-recommended configuration. An unauthenticated or unentitled query is blocked before any resolution occurs. | JWT validation and role claim extraction happen before any analytical processing begins. Row predicates are injected at the physical query level, not applied as a post-processing filter. |
| **P6 — Governed narrative** | Narrative synthesis is anchored exclusively to values present in the execution result. The LLM may not introduce metric values, comparisons, or interpretations not directly derivable from the result set. Hallucinated financial metrics are a regulatory and reputational risk. | The narrative prompt is constructed from the execution result only. Post-generation validation checks every numeric value against the result set and triggers regeneration if any are absent. |
| **P7 — Deterministic visualisation** | Chart type selection is governed by the Visualisation Ontology — a registered set of chart contracts that map result schemas and intent patterns to chart configurations. The LLM does not select chart types. | The same analytical pattern always produces the same chart type across users, sessions, and time. LLM chart preferences are treated as intent signals only; the Visualisation Ontology decides. |
| **P8 — Explainability at every layer** | Users and compliance functions must be able to understand what was queried, why, and with what results at every layer of the analytical stack. Opacity is unacceptable in regulated financial analytics. | The intent confirmation card shows resolved intent before execution; the lineage inspector exposes every step in human-readable form. Metric definitions are accessible to any authenticated user within their entitlement scope. |
| **P9 — Administrator sovereignty within governance bounds** | Platform administrators have authority over analytical configuration — data sources, SMR content, entitlements, and governance thresholds. Within those bounds, administrators are in control. | Administrators may raise governance thresholds above platform minimums but not below them. There is no bypass mode. |
| **P10 — Deterministic computation, not generation** | Analytical results are computed from registered metric definitions applied to data retrieved from execution backends. They are never generated by an AI model. If a consumer submits a structured MCP tool call directly — explicit metric identifiers, dimensions, and filters with no natural language — the Semantic Intent Layer is bypassed entirely, and the pipeline is pure deterministic code from first contact. | The same structured query, with the same entitlements and data, always returns the same result. If a result is wrong, the lineage record identifies the cause — incorrect data, an incorrect SMR definition, or an incorrect intent translation. |

### Principle Interactions

Several of these principles create natural tensions with product requirements that arise in practice. Each tension has a defined resolution; the table below documents the most common cases.

| Principle | Most common tension | Resolution |
|-----------|--------------------|-----------| 
| P1 (semantic abstraction) vs query expressiveness | Users want logic not in the SMR | Add the concept to the SMR — a governance task, not a platform limitation |
| P2 (governance before execution) vs query latency | Governance adds latency | Governance checks optimised for sub-100ms; entitlement projections cached per session |
| P3 (deterministic resolution) vs metric evolution | Metric definitions change | SMR version-controls definitions; lineage records preserve definition version at query time |
| P4 (complete lineage) vs storage cost | Lineage records consume storage | Retention is tenant-configurable; compressed format for long-term storage |
| P6 (governed narrative) vs narrative quality | Strict anchoring may reduce fluency | Quality improves with richer result sets; constraint prevents hallucination |
| P7 (deterministic visualisation) vs user chart preferences | Users prefer different chart types | Override mechanism for Power Analysts — overrides logged in lineage |
| P8 (explainability) vs UX simplicity | Full lineage may overwhelm casual users | Lineage inspector is progressive disclosure — collapsed by default |
| P9 (administrator sovereignty) vs P2 (governance before execution) | Admins want to bypass governance | Governance minimums are absolute — no bypass mode |

The first and last entries are the most consequential. When a business concept cannot be queried, the resolution is to register it in the SMR — a governed addition subject to approval workflow and version control, not an ad hoc inference. That tension is productive: it is how the platform's analytical vocabulary grows.

The tension between P9 and P2 is different in kind. There is no internal tooling path that bypasses the governance pipeline. Governance minimums are architectural properties of the platform, not configurable thresholds.

---

## The Architecture in Practice

```mermaid
flowchart TB
    subgraph clients["AI-Enabled Clients"]
        A1["Conversational\nAssistant"]
        A2["Autonomous\nAgent"]
        A3["Custom\nApplication"]
    end

    subgraph platform["Analytics Capability"]
        B1["MCP Capability Layer"]
        B2["Semantic Metrics Registry"]
        B3["Governance Pipeline\nRALP · SEG · FQP"]
    end

    subgraph data["Data Sources"]
        C1["SQL Warehouse"]
        C2["OpenData API"]
        C3["Graph Data API"]
    end

    clients -->|"MCP tool call\n+ JWT"| B1
    B1 --> B2
    B2 --> B3
    B3 --> data
```

Every consumer type routes through the MCP Capability Layer, traverses the invariant governance sequence, and produces a lineage record. No path to execution backends, physical schemas, or raw SQL exists outside that pipeline. Subsequent chapters describe each component in detail; the principles established here are the reference frame throughout.
