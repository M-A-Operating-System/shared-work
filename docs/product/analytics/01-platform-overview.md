# 1. The Platform

## The Analytics Intelligence Problem

Large financial services organisations — asset managers, investment banks, insurance firms, regulatory reporting units — operate on analytical data of extraordinary complexity and regulatory consequence. Portfolio managers compare risk-adjusted returns across hundreds of strategies against regulated benchmarks. Risk officers monitor VaR breaches across multiple entities in real time. Compliance analysts prepare LCR and NSFR submissions under Basel III/IV, MiFID II, and SEC Regulation BI. All of these decisions depend on metrics that are not simple aggregations: they are versioned, regulated, formula-specific computations that must be calculated identically across every report, every system, and every user session — or they are wrong.

The consequence of this complexity is a structural bottleneck. Business users — portfolio managers, risk officers, compliance analysts — cannot access the data they need without going through a specialist intermediary. Quantitative developers translate business requirements into SQL. Data engineers maintain the pipelines. Analysts mediate between business questions and physical data. This is not a resourcing problem; it is an architectural one. The interface between business intent and governed data is so technically demanding that it requires dedicated expertise at every step. Decision-making slows to the analysts' capacity. Strategic questions queue behind routine reporting. Insight arrives days or weeks after the moment it was needed.

The regulatory dimension sharpens this. In a governed financial services organisation, an analytical result is not just a number — it is an assertion. When a regulator asks how a capital ratio was calculated, the answer must be reproducible, version-controlled, and complete. When a metric definition changes due to a regulatory update, every historical result produced under the prior definition must be identifiable and traceable. When the same metric appears in submissions to two regulators across two jurisdictions, it must resolve to exactly the same formula. These are not quality aspirations — they are legal requirements. An organisation that cannot produce computation provenance for its regulatory submissions is not merely technically incomplete; it is exposed.

Generative AI changes this equation materially. For the first time, it is genuinely possible for a portfolio manager to ask "show me portfolio returns versus benchmark for my equity portfolios this quarter" in plain English and receive a governed, role-constrained, auditable analytical result. The AI handles the translation from business intent to structured query. The platform handles everything that must be deterministic. The analyst bottleneck breaks, the regulatory requirements hold, and the organisation moves at the speed of its decision-makers rather than the speed of its data team.

The most commonly observed first implementation of this capability is the Text-to-SQL pattern: a language model receives a natural language question alongside a physical database schema and generates SQL executed directly against the database. Text-to-SQL has real short-term appeal — a working demonstration is achievable in hours, simple aggregations are handled reliably, and it requires no semantic modelling upfront. For internal tooling, exploratory sandboxes, and low-stakes analytical work it is a legitimate option. For governed enterprise analytics in regulated financial services it is the wrong foundation: there is no versioned metric definition to audit, no reproducible calculation record, no architectural guarantee on entitlement enforcement, and accuracy degrades on the complex formulas that matter most. The [Text-to-SQL Anti-Pattern appendix](./07-text-to-sql-antipattern.md) examines these structural failure modes in detail and explains why they cannot be patched incrementally.

The AI Analytics Platform is a different architecture — one that captures the productivity gains of generative AI while satisfying the governance requirements that regulated organisations actually need:

| Enterprise analytical challenge | Platform response |
|---|---|
| Metric consistency across users, reports, and regulatory submissions | Every metric resolves to exactly one versioned SMR definition — "Portfolio Return" means the same thing in every context |
| Computation provenance for regulatory review | Full lineage record for every result: intent → definitions → entitlements → plan → execution → result |
| Entitlement enforcement for sensitive financial data | Enforced at the semantic tier before any backend is contacted — not bounded by SQL generation reliability |
| Complex regulated formulas (VaR, LCR, BHB attribution) | Defined once in the SMR, computed deterministically — not re-inferred per query |
| Metric governance and change management | SMR version-controls every definition with approval workflow and audit trail |
| Physical schema protection from AI models | Schema never exposed — all AI interaction mediated through the Semantic Metrics Registry |
| Query cost governance for enterprise warehouses | Cost estimated from Logical Query Plan before execution; circuit breaker blocks excess spend |
| Multi-source analytical federation | Federated Query Planner routes governed plans to SQL warehouses, OpenData APIs, Graph Data APIs, and any registered backend |

---

## Platform Vision

The **Analytics Engine** is a deterministic semantic computation engine: given explicit metric identifiers, dimensions, time period, and filters resolved against the Semantic Metrics Registry, it always computes the same answer from the same data with the same entitlements in force. No probability, no sampling, no generation affects the computed metric values. The computation pipeline — metric resolution, entitlement projection, query planning, execution — contains no AI.

AI has two roles in the analytical pipeline. The primary role lives in the consuming AI client: it reads the metric catalogue from the Analytics Engine's SMR resources, translates a natural-language question into explicit, structured MCP tool call parameters, and submits those to the Analytics Engine. The secondary role lives inside the Analytics Engine itself: after computation completes, the Narrative Synthesis Engine makes a targeted call to a language model to summarise the structured result in plain text, anchored strictly to computed values. The NSE cannot introduce metric values, comparisons, or interpretations not present in the result set.

This architecture supports three consumer types. Conversational AI assistants load the metric catalogue, translate natural language to structured parameters, and call the Analytics Engine. Autonomous agents and scheduled pipelines submit structured tool calls directly — no natural language translation needed. Custom applications call the Analytics Engine directly. For all consumer types, narrative synthesis is optional and controlled by the `features.narrativeSynthesis` tenant flag. The Analytics Engine's governance pipeline is identical for all three; entitlements, lineage, and semantic abstraction apply unconditionally.

The following table defines the Analytics Engine's scope precisely:

| It is | It is not |
|-------|-----------|
| A deterministic semantic computation engine — same query + data + entitlements → same computed result | An AI product — computation is always deterministic; the Narrative Synthesis Engine is a constrained post-computation summariser, not a query generator |
| A headless MCP server returning structured result sets and SCL display specifications | A general-purpose SQL interface, BI tool replacement, or rendering layer |
| A governed Semantic Metrics Registry — all queryable metrics are registered, versioned, and owned | A system that accepts natural language or allows LLMs to generate arbitrary SQL |
| A federated query planner routing governed plans to SQL warehouses, OpenData APIs, Graph APIs, and any registered backend | A single-engine analytics layer |
| A role-aware entitlement layer enforced at the semantic tier before execution | A system relying on database-level access controls as the primary AI security boundary |

The Analytics Engine is headless in its computation: metric values are never generated by AI. Every request returns a structured result set, an SCL display specification, and — when narrative synthesis is enabled — a governed narrative summary anchored to the computed values. Natural language translation and rendering are consumer responsibilities.

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
        direction LR
        A1["Conversational\nAssistant"]
        A2["Autonomous\nAgent"]
        A3["Custom\nApplication"]
    end

    subgraph platform["Analytics Capability"]
        direction LR
        B1["MCP Capability Layer"]
        B2["Semantic Metrics Registry"]
        B3["Governance Pipeline\nRALP · SEG · FQP"]
    end

    subgraph data["Data Sources"]
         direction LR
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

Consumer personas and illustrative query journeys are in [Chapter 2 — Consumer Personas and Platform Architecture](./02-personas-and-architecture.md). Component specifications — SMR, SIL, RAPL, SEG, FQP, Visualisation Ontology, NSE, Lineage Store, MCP Capability Layer — are in [Chapter 3 — Core Platform Capabilities](./03-core-capabilities.md). The reference implementation stack is in [Chapter 5 — Proposed Technical Implementation](./05-technical-implementation.md).
