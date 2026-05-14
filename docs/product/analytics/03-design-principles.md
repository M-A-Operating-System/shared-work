# 03 — Design Principles

These nine principles govern all design decisions for the AI Analytics Platform. Where a proposed feature conflicts with a principle, the principle takes precedence. Deviations require an explicit decision record.

---

## P1 — Semantic abstraction over physical exposure

The platform never exposes physical storage schemas, table names, column names, or execution engine internals to AI models or end users. All AI interaction is mediated through the Semantic Metrics Registry. If a business concept is not registered in the SMR, it is not queryable. There is no escape hatch to raw SQL.

**Consequences:**
- The Analytical Intent Validator operates exclusively on SMR-registered identifiers. Any attempt to introduce unregistered identifiers is rejected at the validation boundary.
- Physical query generation is entirely the responsibility of the Federated Query Planner — the LLM has no access to or knowledge of physical schemas.
- The system prompt injected into the AI model contains metric names, dimension names, and analytical concepts drawn from the SMR — not table schemas, column names, or JOIN paths.
- Schema leakage — even partial — is a security and governance violation. The platform architecture makes this impossible by design, not by policy enforcement alone.

---

## P2 — Governance before execution

Every analytical query passes through the governance pipeline before any physical execution begins. There is no fast path that bypasses the Role-Aware Projection Layer or the Semantic Execution Governance checks. Governance is not a post-processing filter — it is a pre-execution gate.

**Consequences:**
- The execution sequence is invariant: Intent Resolution → SMR Resolution → Role-Aware Projection → Intent Validation → Governance Validation → FQP → Execution. No step may be skipped.
- Queries that fail governance checks are blocked entirely — they do not partially execute. Partial results from a governance-blocked query are never returned.
- Governance decisions are logged before the query reaches an execution engine, so the audit trail reflects the governance state at decision time, not at result time.
- Governance configuration changes (entitlement policies, classification gates, cost limits) take effect on the next query — there is no cache of pre-governance query plans.

---

## P3 — Deterministic metric resolution

A given metric name must resolve to exactly one governed definition for a given tenant at a given point in time. There are no context-dependent interpretations of metric semantics. "Portfolio Return" means the same thing in every query, every dashboard, and every narrative — or it is a bug.

**Consequences:**
- Metric definitions in the SMR are version-controlled. A metric name resolves to its approved definition at the time of query execution. Historical lineage records preserve the definition version used.
- Conflicting metric definitions are a configuration error — the platform rejects any SMR submission where a metric ID already exists with a different formula, unless the submission is an explicit version update.
- The LLM may not infer metric definitions from context. If a metric is not in the SMR, the platform returns a resolution error — not an inferred or approximated definition.
- User-visible metric labels, descriptions, and units are sourced from the SMR definition — the LLM does not paraphrase or reinterpret them.

---

## P4 — Complete analytical lineage

Every analytical result has a complete, queryable lineage chain: the user's natural language intent, the resolved analytical intent, the validated tool call parameters, the Logical Query Plan, the physical backend sub-plans, the execution backend responses, the assembled result set, and the applied governance decisions. This lineage is a first-class artefact.

**Consequences:**
- Lineage records are written atomically with the result — a result with no lineage record is a platform defect.
- The lineage inspector UI is available to Power Analysts and above for every analytical result in their session.
- Exported analytical results include a lineage reference that can be used to reconstruct the full execution chain.
- Regulatory audit requests can be satisfied by querying the lineage store directly.
- Lineage records are not mutable after writing. Corrections produce a new lineage record referencing the original.

---

## P5 — Role-aware by default

The platform applies entitlements by default — a user sees exactly the metrics, dimensions, and data rows their role entitles them to, without having to request restrictions. There is no opt-in to data governance. An unauthenticated or unentitled query is blocked before any resolution occurs.

**Consequences:**
- JWT validation and role claim extraction happen before any analytical processing begins.
- `defaultDenyAll: true` is the platform-recommended setting — users with no matching role see nothing, not a default public view.
- Row predicates are injected at the physical query level — not as a post-processing filter that could leak data via error messages.
- If a user's role changes mid-session, the new entitlements apply to subsequent queries. In-session results from before the role change are not retrospectively restricted — but their lineage records reflect the entitlements in force at execution time.

---

## P6 — Governed narrative, not free narrative

Narrative synthesis (LLM-generated prose describing analytical results) is anchored exclusively to the values present in the execution result. The LLM may not introduce metric values, comparisons, or interpretations that are not directly derivable from the result set. Hallucinated financial metrics are a regulatory and reputational risk.

**Consequences:**
- The narrative synthesis prompt is constructed from the execution result — the LLM receives the structured result values, not a free-form query context.
- A system-level constraint is injected into the narrative synthesis prompt: *"You may only reference metric values, dates, and identifiers present in the provided result set. You may not introduce external figures, estimates, or comparisons from your training data."*
- Narrative synthesis outputs are validated post-generation against the result set — any numeric value in the narrative that does not appear in the result is flagged and the narrative is regenerated.
- Users can inspect the source result set underlying any narrative via the lineage inspector.

---

## P7 — Deterministic visualisation

Chart type selection is governed by the Visualisation Ontology — a registered set of chart contracts that map result schemas and intent patterns to specific chart configurations. The LLM does not select chart types ad hoc. This ensures that the same analytical pattern always produces the same chart type across users, sessions, and time.

**Consequences:**
- The Visualisation Ontology defines: for a given result schema (metric types, dimension cardinality, time axis presence) and intent pattern (comparison, trend, distribution, composition, relationship), which chart contract applies.
- Chart contract parameters (axis assignments, colour encoding, tooltip definitions, drilldown anchors) are derived algorithmically from the result schema — not inferred by the LLM.
- Custom chart types must be registered as host renderer modules before they can be selected by the ontology.
- The LLM may express an intent that suggests a chart preference (e.g. *"show me a breakdown"*), but the Visualisation Ontology makes the final chart selection — the LLM suggestion is treated as an intent signal, not a direct rendering instruction.

---

## P8 — Explainability at every layer

Users and compliance functions must be able to understand exactly what was queried, why, and with what results at every layer of the analytical stack. Opacity is unacceptable in regulated financial analytics.

**Consequences:**
- The intent confirmation card (when enabled) shows the user the resolved analytical intent before execution — giving them the opportunity to correct misinterpretations before a query is run.
- The lineage inspector exposes every step of the execution chain in a structured, human-readable format.
- Execution governance decisions (blocks, cost warnings, classification gates) are explained to the user in plain language — not just "query blocked".
- SMR metric definitions are accessible to any authenticated user (within their entitlement scope) — users can inspect exactly how any metric they see is calculated.
- The narrative synthesis output can be expanded to show the source result values it was anchored to.

---

## P9 — Host sovereignty within governance bounds

The host application has final authority over the analytical configuration — which metrics are registered, how entitlements are structured, which execution engines are used, and what governance thresholds apply. The platform enforces a set of non-negotiable governance minimums (lineage, role-awareness, semantic abstraction) but within those bounds, the host is in control.

**Consequences:**
- Host applications configure their SMR, entitlement model, execution engines, and governance thresholds via the application config and Admin API.
- Platform-managed governance (no raw SQL, mandatory lineage, role-aware projection, semantic abstraction) are non-overridable — they cannot be disabled by host config.
- Hosts may raise governance thresholds (tighter cost limits, stricter classification gates) but may not lower them below platform minimums.
- New platform-level governance defaults that would affect existing tenants require a migration path and advance notice.

---

## Principle interactions

| Principle | Most common tension | Resolution |
|-----------|--------------------|-----------| 
| P1 (semantic abstraction) vs query expressiveness | Users or AI agents want to express analytical logic not in the SMR | Add the concept to the SMR — it is a governance and configuration task, not a platform limitation |
| P2 (governance before execution) vs query latency | Governance pipeline adds latency | Governance checks are optimised for sub-100ms execution; entitlement projections are cached per session |
| P3 (deterministic resolution) vs metric evolution | Metric definitions change over time | SMR version-controls metric definitions; lineage records preserve definition version at query time |
| P4 (complete lineage) vs storage cost | Lineage records consume significant storage | Lineage record retention is tenant-configurable; compressed lineage format used for long-term storage |
| P6 (governed narrative) vs narrative quality | Strict anchoring may produce less fluent prose | Narrative quality improves with richer result sets; the constraint prevents hallucination at the cost of occasional prosaic output |
| P7 (deterministic visualisation) vs user chart preferences | Users may prefer a different chart type | Ontology includes an override mechanism for Power Analysts — overrides are logged in the lineage record |
| P8 (explainability) vs UX simplicity | Full lineage exposure may overwhelm casual users | Lineage inspector is progressive disclosure — collapsed by default, expandable by Power Analysts |
| P9 (host sovereignty) vs P2 (governance before execution) | Host wants to bypass governance for internal tools | Governance minimums are absolute — the platform does not provide a governance bypass mode |
