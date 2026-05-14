# 02 — Personas and User Journeys

The AI Analytics Platform is deployed by host applications across regulated financial services contexts. This document describes personas at two levels: **platform-level archetypes** (roles that exist across all deployments) and **illustrative host application journeys** (examples showing how different financial services contexts use the platform).

---

## Platform-level personas

| Persona | Role | Primary need |
|---------|------|--------------|
| **Analytical End User** | Authenticated user of the host application using the analytics layer as their primary data access interface | Ask governed analytical questions and receive reliable, role-appropriate results without knowledge of underlying data structures or metric definitions |
| **Power Analyst** | Experienced user who composes multi-dimensional analytical requests and navigates drilldown hierarchies | Multi-dimensional analytical exploration, governed drilldown, lineage inspection, result export for downstream use |
| **Application Admin** | Privileged user within the tenant responsible for the SMR, entitlement policies, and governance configuration | Manage metric definitions, approve registry changes, maintain entitlement policies, review governance audit trail |
| **Metric Owner** | Subject-matter expert assigned ownership of one or more metric definitions in the SMR | Review proposed changes to owned metrics, approve aggregation rule changes, maintain metric documentation |
| **Host Developer** | Engineer at the host application team responsible for config and engine integration | Register execution engines, maintain the application config, integrate entitlement model |
| **Platform Admin** | AI Analytics Platform team member with cross-tenant visibility | Platform health, tenant onboarding, infrastructure, governance audit review |

### Application Admin design note

The Application Admin role is the platform's equivalent of a Chief Data Officer or Head of Analytics Data Governance within the tenant. They are responsible for the integrity of the SMR — what can be queried, how metrics are defined, and who can access what. Key responsibilities:

- Managing the Semantic Metrics Registry — approving new metric definitions, deprecating obsolete ones, resolving definition conflicts
- Maintaining entitlement policies — role-to-metric-access mappings, row predicates, column masks
- Reviewing the governance audit trail — flagging unusual query patterns or policy violations
- Configuring execution engine routing priorities and cost limits
- Approving Application Context for the analytical assistant

This role must exist in every tenant before go-live.

---

## Illustrative host application journeys

---

### Journey A — Wealth management: portfolio morning briefing

**Host application type:** Wealth management platform  
**Persona:** Portfolio Manager (Analytical End User)  
**Setting:** Desktop, first thing in the morning

A portfolio manager opens the analytics layer and types: *"Show me portfolio returns versus benchmark across all my portfolios for the current quarter, sorted by tracking error."*

The platform resolves the intent against the SMR, identifying metrics `portfolio_return`, `benchmark_return`, `tracking_error` and the `portfolio` and `date` dimensions. The Role-Aware Projection Layer injects a row predicate scoped to this manager's assigned portfolios from their JWT claims.

The platform produces:
- A bar chart (Visualisation Ontology selects: multi-series bar, metric-to-benchmark comparison pattern) showing quarterly return vs. benchmark by portfolio
- A ranked data table by tracking error
- A narrative synthesis: *"Across 14 portfolios, 9 outperformed their benchmark this quarter. The Global Equity Opportunities portfolio has the highest tracking error at 3.2%, driven primarily by significant overweight positions in Technology. Two portfolios — UK Core Income and Strategic Balanced — are within their tracking error budget."*

The manager clicks the Technology bar segment. A governed drilldown traverses the `asset_class_hierarchy` to the sector level, showing sector-level attribution.

**Features exercised:** Natural language intent resolution, role-aware projection, multi-metric query, Visualisation Ontology chart selection, narrative synthesis, governed drilldown, lineage trail.

---

### Journey B — Risk management: VaR limit breach investigation

**Host application type:** Investment risk management system  
**Persona:** Risk Officer (Power Analyst)  
**Setting:** Desktop, intraday monitoring

A risk officer receives an alert. They open the analytics layer and ask: *"Which portfolios are breaching their VaR 95 limit today, and what is the dominant risk factor contribution for each?"*

The platform resolves `var_95`, `var_limit`, `risk_factor_contribution` metrics and the `portfolio` and `date` dimensions. The intent confirmation card is not shown (disabled for this tenant). The FQP routes the VaR metrics to the risk engine and the portfolio data to the primary warehouse.

The result is:
- A heatmap (Visualisation Ontology: metric-vs-threshold pattern → heatmap contract) showing breach severity by portfolio
- A drilldown-ready table of limit breach amounts
- Narrative synthesis: *"3 portfolios are breaching their VaR 95 limit today. Emerging Markets High Yield has the most severe breach at 142% of limit. The dominant risk factor for all three portfolios is credit spread widening in BBB-rated corporate bonds, accounting for 64–71% of the excess VaR."*

The risk officer opens the lineage inspector. They can see exactly which execution engines were called, what predicates were applied, and which metric definitions from the SMR were used.

**Features exercised:** Multi-engine federation, VaR metrics, risk factor attribution, heatmap rendering, narrative synthesis, lineage inspector.

---

### Journey C — Compliance: regulatory reporting preparation

**Host application type:** Banking compliance management platform  
**Persona:** Compliance Analyst  
**Setting:** Desktop, end-of-quarter regulatory reporting cycle

A compliance analyst needs to prepare the LCR (Liquidity Coverage Ratio) and NSFR (Net Stable Funding Ratio) summary for submission. They ask: *"Show me the current LCR and NSFR for all regulated entities, with a 30-day trend."*

The platform identifies that the `regulatory_reporting` feature flag is enabled and the user's role includes `compliance_analyst`. The Role-Aware Projection Layer applies column masks to client name and account number fields per the compliance role definition. The governance layer validates that the data classification of LCR and NSFR data is within the user's permitted classification level.

The result is:
- A line chart showing 30-day trend of LCR and NSFR per entity
- A summary table of current ratios vs. regulatory minima
- An export-ready data table with the complete lineage record attached (required by `requireLineageForExport: true` in the governance config)

**Features exercised:** Regulatory metric domain, role-aware column masking, classification gating, lineage-gated export, compliance mode governance.

---

### Journey D — Institutional analytics: issuer concentration review

**Host application type:** Institutional asset management platform  
**Persona:** Power Analyst  
**Setting:** Desktop, pre-investment committee

An analyst prepares for the investment committee meeting. They ask: *"Show me issuer concentration risk across all equity portfolios — highlight any issuer where the aggregate position exceeds 5% of total AUM."*

The platform resolves `issuer_concentration`, `aum`, `aggregate_position_pct` metrics and slices by `issuer` and `portfolio` dimensions. The Visualisation Ontology selects a treemap (issuer concentration pattern → treemap contract) with threshold highlighting.

The analyst then uses the drilldown to navigate from the issuer level to individual security positions within the highest-concentration issuer.

They export the result as PDF — the lineage record is automatically attached. The export is flagged in the audit trail as a pre-committee analytical artefact.

**Features exercised:** Issuer concentration metrics, treemap rendering, drilldown (issuer → security), PDF export with lineage, audit trail artefact flagging.

---

### Journey E — Application Admin: metric definition governance

**Host application type:** Any financial services platform  
**Persona:** Application Admin  
**Setting:** Platform Admin UI

A metric owner has proposed a new metric: `modified_duration_weighted` — a portfolio-level modified duration weighted by market value. The Application Admin reviews the proposal in the SMR management UI:

- Metric label: Modified Duration (Market Value Weighted)
- Formula: `SUM(position_market_value × security_modified_duration) / SUM(position_market_value)`
- Aggregation: `value_weighted_average`
- Dimensions: `portfolio`, `asset_class`, `date`
- Data lineage: sourced from `positions` domain, `risk_metrics` sub-domain
- Owner: Head of Fixed Income Risk
- Access roles: `risk_officer`, `portfolio_manager`

The Application Admin reviews, notes that the formula is consistent with the existing `duration` metric's definition style, and approves. The metric is now resolvable in the SMR from the next refresh cycle.

**Features exercised:** SMR metric approval workflow, formula review, ownership assignment, role access policy, metric activation.

---

## Persona × Feature Matrix

| Feature | End User | Power Analyst | Compliance Analyst | App Admin | Metric Owner | Host Developer |
|---------|:--------:|:-------------:|:-----------------:|:---------:|:------------:|:--------------:|
| Natural language query | ✓ | ✓ | ✓ | ✓ | | |
| Metric resolution from SMR | ✓ | ✓ | ✓ | ✓ | | |
| Role-aware results | ✓ | ✓ | ✓ | ✓ | | |
| Governed drilldown | | ✓ | ✓ | ✓ | | |
| Lineage inspector | | ✓ | ✓ | ✓ | ✓ | |
| Narrative synthesis | ✓ | ✓ | ✓ | ✓ | | |
| Result export | ✓ | ✓ | ✓ | ✓ | | |
| SMR browsing (read-only) | | ✓ | ✓ | ✓ | ✓ | |
| SMR metric proposal | | | | ✓ | ✓ | |
| SMR metric approval | | | | ✓ | | |
| Entitlement policy management | | | | ✓ | | |
| Engine registration | | | | | | ✓ |
| Governance audit trail | | | ✓ | ✓ | | ✓ |
| Config management | | | | ✓ | | ✓ |
| Regulatory metric domain | | | ✓ | ✓ | | |
