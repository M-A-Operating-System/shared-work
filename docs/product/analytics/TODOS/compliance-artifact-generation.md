# TODO: Compliance Artifact Generation

**Status:** Implemented in Chapters 2, 3, 4, 5. Open questions resolved. Closed.  
**Affects:** Chapters 2, 3, 4, 5 and SMR metric schema  
**Priority:** High — current documents describe an incorrect architecture (role-based compliance) that should be replaced with a metadata + intent driven model

---

## The Problem With the Current Design

The documents currently model compliance governance as a **role-based** concern: Journey C requires the user to carry a `compliance_analyst` JWT claim before enhanced governance artifacts are produced. The Persona × Feature Matrix treats "Compliance Analyst" as a distinct persona column.

This is architecturally wrong. A compliance-relevant metric (e.g. LCR, NSFR, VaR for regulatory reporting) queried for a business reason (e.g. "what's our LCR today?") does not require the full compliance artifact set. The same metric queried for a compliance reason (e.g. "prepare our LCR for the regulatory submission") does. The difference is not who is asking — it is **what the query is for**.

---

## Agreed Design

Enhanced compliance governance artifacts are triggered by **two independent signals, both of which must be true** (AND logic):

### Signal 1 — Metric metadata (objective, static)

The SMR `analytical_metric` schema gains a `compliance_relevant` flag:

```json
"compliance_relevant": true
```

Set by the metric owner at registration time. Flags metrics whose output is used in regulatory reporting, audit submissions, or compliance filings (e.g. LCR, NSFR, VaR 95 for Basel reporting, best-execution metrics under MiFID II). A compliance-relevant metric can still be queried for business purposes — the flag alone does not trigger enhanced artifacts.

### Signal 2 — AI intent classification (inferred, runtime)

The Semantic Intent Layer adds a compliance intent classification step. After resolving the operation and parameters, the SIL classifies the natural language query to determine whether the stated purpose is compliance-driven.

```json
"compliance_purpose": true | false
```

Examples that produce `true`: "for the regulatory submission", "for the board compliance pack", "for the MiFID report", "for the auditors", "prepare our LCR filing".  
Examples that produce `false`: "what's our LCR today?", "show me VaR across portfolios", "morning briefing".

The classification is performed by the AI model as part of the SIL intent resolution step. It should be surfaced in the lineage record alongside the resolved intent.

### Combined decision in SEG

The SEG evaluates both signals:

| `compliance_relevant` | `compliance_purpose` | Governance output |
|---|---|---|
| `true` | `true` | **Enhanced** — full compliance artifact set |
| `true` | `false` | Standard governance output |
| `false` | `true` | Standard governance output |
| `false` | `false` | Standard governance output |

Only when both are true does the SEG escalate to the enhanced compliance artifact tier.

---

## Enhanced Compliance Artifact Set

When both signals are true, the SEG triggers additional governance outputs as part of the response:

- **Regulatory trace record** — written to the compliance-mode-specific trace table (e.g. `analytics.mifid2_trace`, `analytics.regulatory_snapshots`) in addition to the standard lineage record
- **Lineage-gated export** — export of the result is blocked until a complete lineage record exists (`requireLineageForExport` enforced automatically, not a configurable option)
- **Classification ceiling enforcement** — the assembled result's classification level is validated against the requesting user's authorised ceiling before the result is returned
- **Business justification prompt** — if the compliance mode requires it (e.g. MiFID II client-data queries), a structured justification is requested before execution proceeds
- **Compliance metadata in response** — the MCP response includes a `compliance` block alongside the standard `narrative`, `data`, and `display_spec` fields, containing: `compliance_purpose: true`, `regulatory_trace_id`, `artifact_set_version`, `triggered_by` (which metric IDs and compliance modes contributed)

---

## Document Changes Required

### Chapter 2 — Consumer Personas and Platform Architecture

- **Remove** the Compliance Analyst column from the Persona × Feature Matrix — it is not a distinct persona
- **Rewrite Journey C** to remove the `compliance_analyst` JWT role claim requirement. The new journey: a user queries LCR and NSFR, the SIL classifies the intent as compliance-purpose, both metrics are flagged `compliance_relevant: true`, SEG escalates automatically and returns the full compliance artifact set alongside the standard result. No special role claim required.
- Update the persona prose to remove the sentence describing Compliance Analyst as a specialised Power Analyst — the concept dissolves. Any entitled user querying compliance-relevant metrics for a compliance purpose receives the enhanced artifacts.

### Chapter 3 — Core Platform Capabilities

- **SMR metric schema**: add `compliance_relevant: boolean` field to the `analytical_metric` definition schema and field reference table
- **SIL section**: add a compliance intent classification step to the intent resolution pipeline description. The SIL produces `compliance_purpose: boolean` as part of the resolved intent object
- **SEG section**: document the two-signal AND decision. Replace the current role-claim-based compliance mode description with the metadata + intent model. The `complianceMode` platform config remains (it determines which trace tables and regulatory rules apply) but it no longer gates on a user role claim
- **Response format**: add `compliance` block to the MCP response structure, present only when the enhanced artifact tier is triggered
- **Caching note**: compliance-triggered responses must not be served from cache — the compliance artifact set must be freshly generated for each compliance-purpose query. Add a cache bypass rule to the FQE caching spec

### Chapter 4 — Integration and Deployment

- Update the `complianceMode` governance config description to clarify it configures the regulatory ruleset and trace targets, not the trigger condition. Remove any implication that `complianceMode` gates on user role claims.

### Chapter 5 — Technical Implementation

- Add `compliance_relevant` to the `analytical_metric` DCS document type
- Update SEG implementation sketch to show the two-signal evaluation
- Add compliance metadata block to the response assembly step

---

## Open Questions

1. **Confidence threshold for intent classification**: should `compliance_purpose` be a boolean or a confidence score with a configurable threshold? A threshold allows the platform to be tuned for sensitivity (e.g. require high confidence before triggering the full artifact set for costly regulatory trace writes).

2. **User confirmation**: when `compliance_purpose: true` is inferred, should the platform confirm with the user before generating the full artifact set? ("I've detected this query is for compliance purposes — generating the full regulatory artifact set. Confirm?") This would prevent false-positive artifact generation from ambiguous phrasing.

3. **Retroactive compliance classification**: if a user queries a metric for business reasons and later needs it for compliance purposes, can they re-submit with explicit compliance intent to generate the artifact set against the cached result, or must the query be re-executed?

4. **Audit of the classifier itself**: the compliance_purpose classification is AI-inferred. For regulatory purposes, is the classifier decision itself auditable? Should the SIL record the raw classification reasoning in the lineage record?
