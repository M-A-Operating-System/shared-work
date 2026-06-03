# 2. Consumer Personas and Platform Architecture

## Consumer Personas

The platform is designed to serve a heterogeneous population of users whose needs range from conversational analytics access to deep governance administration. These personas define the platform's access model: who can query what, with what constraints. The six personas below have different levels of access and interact with the platform in different ways.

The platform vision and [Design Principles](./00-overview.md#design-principles) governing these access controls are in [Platform Overview](./00-overview.md). Component specifications for the platform features exercised in the journeys below are in [Chapter 3 — Core Platform Capabilities](./03-core-capabilities.md).

| Persona | Role | Primary need |
|---------|------|--------------|
| **Analytical End User** | Authenticated user accessing analytics as their primary data interface | Ask governed analytical questions and receive reliable, role-appropriate results without knowledge of data structures |
| **Power Analyst** | Experienced user composing multi-dimensional requests and navigating drilldowns | Multi-dimensional exploration, governed drilldown, lineage inspection, result export |
| **Application Admin** | Privileged tenant user responsible for SMR, entitlement policies, governance config | Manage metric definitions, approve registry changes, maintain entitlement policies, review audit trail |
| **Metric Owner** | Subject-matter expert assigned ownership of SMR metric definitions | Review proposed changes to owned metrics, approve aggregation rule changes, maintain documentation |
| **Integration Engineer** | Engineer responsible for data source registration and platform configuration | Register execution backends, maintain config, integrate entitlement model |
| **Platform Admin** | Cross-tenant platform team member | Platform health, tenant onboarding, infrastructure, governance audit |

These persona distinctions are not merely organisational; they directly inform the platform's trust boundaries. The Analytical End User interacts exclusively through natural language and receives rendered, role-constrained results. They are deliberately shielded from physical schema details, metric identifiers, and backend routing. The Power Analyst extends this interface with drilldown navigation, lineage inspection, and export capability, but remains within the same governed query pipeline. The Compliance Analyst is not a separate persona. Any entitled user querying compliance-relevant metrics for a compliance purpose receives the full enhanced governance artifact set automatically — this is determined at runtime by metric metadata and AI intent classification, not by a dedicated role. See the [Compliance Artifact Generation TODO](./TODOS/compliance-artifact-generation.md) for the full design.

The Application Admin must be configured before go-live. This role controls what can be queried, how metrics are defined, and who can access what. Without one, the Semantic Metrics Registry contains no governed metric definitions and the platform cannot serve any analytical query. The Application Admin owns the lifecycle of metric definitions, approves registry changes, and maintains the entitlement policies that the Role-Aware Projection Layer enforces at query time.

Metric Owners let the Application Admin distribute review responsibility to subject-matter experts. Each Metric Owner serves as the authoritative reviewer for definition changes, aggregation rule modifications, and documentation accuracy on their assigned metrics. This spreads governance responsibility across domain expertise without concentrating all approval authority in a single administrator.

The Integration Engineer operates at the infrastructure boundary, handling backend registration, connection configuration, and the physical mapping declarations that the Federated Query Planner resolves at execution time. They interact through configuration interfaces rather than the conversational query path. The Platform Admin sits above the tenant boundary entirely, responsible for infrastructure health, tenant onboarding, and cross-tenant governance audit — this persona has no query interface into tenant data.

These personas are not mutually exclusive. A single individual may hold multiple roles within a tenant; the platform evaluates entitlements from the combined JWT claims present at query time.

## Illustrative Use Cases

The following journeys show how the platform handles three different types of query. Each highlights a different cluster of platform features and the governance guarantees that apply across all query types.

### Journey A: Wealth Management — Portfolio Morning Briefing

A portfolio manager begins their morning with a natural language query: "Show me portfolio returns versus benchmark across all my portfolios for the current quarter, sorted by tracking error."

The AI Chat Platform's model maps the portfolio manager's natural language query to three metric identifiers — `portfolio_return`, `benchmark_return`, and `tracking_error` — using the SMR metric catalogue it loaded at session start. `tracking_error` carries `benchmark_id` as a required dimension; the SIL resolves this from the portfolio's registered default benchmark in the SMR dimension catalogue, so the user does not need to specify it explicitly. These structured parameters are submitted to the Analytics Engine, whose Semantic Intent Layer validates them against the Semantic Metrics Registry and builds a Logical Query Plan. The Role-Aware Projection Layer extracts the manager's portfolio scope from the JWT claims and constructs a row-level predicate restricting results to portfolios within the manager's authorised coverage. This predicate is injected into the Logical Query Plan before any execution backend is contacted — it is not a post-hoc filter applied to a full dataset.

The Visualisation Ontology examines the assembled result pattern — multiple metrics across multiple portfolio entities, sorted by a continuous measure — and selects a multi-series bar chart as the appropriate display specification. The Narrative Synthesis Engine produces: "Across 14 portfolios, 9 outperformed their benchmark. Global Equity Opportunities has the highest tracking error at 3.2%..." This narrative is returned alongside the display specification as a single structured MCP tool response.

The manager clicks a segment of the chart. The governed drilldown mechanism traverses the `asset_class_hierarchy` dimension as defined in the SMR, applying the same role-aware projection constraints to the more granular result set. At no point does the manager's interaction surface raw SQL, physical table names, or backend routing details.

Features exercised: natural language intent resolution, role-aware row projection, multi-metric query, Visualisation Ontology chart selection, Narrative Synthesis Engine, governed drilldown.

### Journey B: Risk Management — VaR Breach Investigation

A risk officer asks: "Which portfolios are breaching their VaR 95 limit today, and what is the dominant risk factor contribution for each?"

The AI Chat Platform's model translates the risk officer's query into three metric identifiers — `var_95`, `var_limit`, and `risk_factor_contribution` — and identifies this as a threshold-comparison pattern with a contributing-factor breakdown. The structured parameters are submitted to the Analytics Engine. The Federated Query Planner, informed by the physical mappings registered in the SMR, routes VaR metrics to the risk engine execution backend and portfolio metadata to the primary data warehouse. These sub-plans execute in parallel; the planner assembles the joined result set before passing it downstream.

The Visualisation Ontology recognises the metric-versus-threshold pattern across multiple entities and selects a heatmap as the display specification. The Narrative Synthesis Engine produces: "3 portfolios are breaching VaR 95 today. Emerging Markets High Yield has the most severe breach at 142% of limit. Dominant risk factor: credit spread widening in BBB-rated corporate bonds (64–71% of excess VaR)."

The risk officer opens the lineage inspector. The inspector surfaces the exact backend identifiers, row predicates, column masks, metric definition versions, and governance decisions that produced this result — all drawn from the Analytical Lineage Store, which recorded each component of the query execution as it progressed through the pipeline. The lineage record is cryptographically associated with the `result_id` returned in the original MCP response.

Features exercised: multi-engine federation, VaR metric domain, heatmap rendering, Narrative Synthesis Engine, lineage inspector.

### Journey C: Compliance — Regulatory Reporting Preparation

A compliance analyst asks for LCR and NSFR ratios for all regulated entities with a 30-day trend.

The Semantic Intent Layer classifies the stated intent — "with a 30-day trend" for regulatory reporting — and sets `compliance_purpose: true`. The LCR and NSFR metrics are flagged `compliance_relevant: true` in the SMR. Both signals are true, so the SEG escalates to the enhanced compliance governance tier automatically: no special role claim is required.

The Role-Aware Projection Layer applies column masks to client name and account number fields, consistent with the entitlement policy associated with this metric domain. A classification gate validates that the assembled result's data classification level is within the requesting user's authorised ceiling. The Visualisation Ontology produces a 30-day trend line chart and a summary table of ratios versus regulatory minima. The response includes the standard result alongside a `compliance` block containing the regulatory trace record and a lineage-gated export — the export cannot be issued without an attached lineage record, enforced automatically by the SEG when the compliance tier is active.

> **Note:** The compliance artifact escalation model (metric metadata + AI intent classification) is a pending design change — see [Compliance Artifact Generation TODO](./TODOS/compliance-artifact-generation.md).

Features exercised: regulatory metric domain, compliance intent classification, compliance-relevant metric metadata, column masking, data classification gating, lineage-gated export, Basel III/IV compliance mode governance.

## Persona × Feature Matrix

The matrix below maps each major platform feature to the personas for whom it is available. Blank cells indicate that the feature is outside the operational scope of that persona, either because it is not needed or because its use would represent a governance violation.

| Feature | End User | Power Analyst | App Admin | Metric Owner | Integration Eng | Platform Admin |
|---------|:--------:|:-------------:|:---------:|:------------:|:--------------:|:--------------:|
| Natural language query | ✓ | ✓ | ✓ | | | |
| Role-aware results | ✓ | ✓ | ✓ | | | |
| Governed drilldown | | ✓ | ✓ | | | |
| Lineage inspector | | ✓ | ✓ | ✓ | | |
| Narrative synthesis | ✓ | ✓ | ✓ | | | |
| Result export | ✓ | ✓ | ✓ | | | |
| SMR browsing | | ✓ | ✓ | ✓ | | |
| SMR metric management | | | ✓ | ✓ | | |
| Entitlement management | | | ✓ | | | |
| Backend registration | | | | | ✓ | |
| Governance audit trail | | | ✓ | | ✓ | ✓ |
| Tenant onboarding / infra | | | | | | ✓ |

The matrix reveals two distinct operational planes. The analytical plane — natural language query through result export — is accessible to all query-facing personas. The governance plane — SMR management, entitlement policy, backend registration, and audit trail — is restricted to the personas whose responsibilities require it. Platform Admin has no query interface into tenant data; their access is limited to cross-tenant infrastructure and governance audit.

> **Note:** Compliance-enhanced governance artifacts (regulatory trace, lineage-gated export, classification enforcement) are not a persona feature — they are triggered automatically at runtime when a compliance-relevant metric is queried with a compliance-stated intent. Any entitled user may trigger this path.

The full platform architecture diagram and request flow sequence are in [Chapter 3 — Core Platform Capabilities](./03-core-capabilities.md).
