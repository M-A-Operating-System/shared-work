# AI Analytics Platform — Roadmap

|                    |                           |
|--------------------|---------------------------|
| **Current release**| v1 — governed semantic analytics layer, SMR, Analytics DSL, FQP, role-aware projection, visualisation ontology, MCP capability layer |
| **Date**           | May 2026                  |

---

## Near-term — Scheduled and alert-driven queries

**Objective:** Allow analytical queries to be scheduled for recurring execution and trigger alert workflows when metric thresholds are breached.

| Item | Description |
|------|-------------|
| Scheduled query registration | Application Admins and Power Analysts register DSL expressions for scheduled execution (cron-based). Scheduled queries run through the full governance pipeline using the owner's entitlement claims at execution time. Results written to the result artefact store. |
| Threshold alert configuration | Define metric thresholds on scheduled queries. When a result exceeds a threshold, trigger a webhook or in-platform notification. |
| Alert lineage | Each alert event generates a lineage record linked to the query that triggered it. Alert audit trail is preserved for regulatory review. |
| Push delivery | Results delivered to registered endpoints (webhook, email, Slack via MCP) with the lineage reference attached. |

**Pre-requisites:** Scheduled execution infrastructure; webhook delivery; alert threshold schema in SMR.

---

## Near-term — Natural language SMR authoring assistance

**Objective:** Allow metric owners to define new SMR metric definitions in natural language, with the platform generating the structured YAML definition for review.

| Item | Description |
|------|-------------|
| Natural language → metric draft | Metric owner describes a metric in prose. The platform generates a draft SMR YAML definition with formula, aggregation rules, dimensions, and data domain inferred from the description and validated against the existing SMR. |
| Consistency check | Generated draft is compared against existing metric definitions to detect potential duplicates, formula inconsistencies, or naming conflicts before the owner reviews. |
| Review workflow | Generated draft enters the standard SMR approval workflow — it is never directly activated without Application Admin review. |

---

## Near-term — Cross-session analytical memory

**Objective:** Allow users to save analytical context across sessions — preferred dimensions, frequently used metrics, drilldown paths.

| Item | Description |
|------|-------------|
| Session preferences | User preferences (default dimensions, preferred chart types, favourite measure groups) persisted across sessions. Applied as defaults for new queries. |
| Saved queries | Named analytical queries saved by Power Analysts and retrievable in future sessions. Saved queries are version-controlled — SMR changes that invalidate a saved query are flagged to the owner. |
| Personal metric registry | Users can mark metrics from the SMR as "favourites" — surfaced first in intent resolution suggestions and SMR browser. |

---

## Phase 2 — Proactive analytical insights

**Objective:** Surface unsolicited analytical observations when metric values deviate from expected ranges.

| Item | Description |
|------|-------------|
| Anomaly detection | Background jobs monitor scheduled query results for metric values outside configurable statistical ranges. Anomalies surface as proactive insight cards in the analytical workspace. |
| Trend signals | Platform identifies metrics showing consistent directional movement across multiple periods. Presented as trend signals with lineage references. |
| Peer comparison | Where the Benchmark Data Service or Regulatory Reference Service provides peer data, the platform surfaces peer comparison signals. |

**Pre-requisites:** Scheduled query infrastructure; statistical anomaly detection; notification delivery.

---

## Phase 2 — Collaborative analytical sessions

**Objective:** Allow multiple users within the same tenant to share and collaborate on analytical sessions.

| Item | Description |
|------|-------------|
| Shared session model | Invite other authenticated users within the tenant to an analytical session. Both participants can submit queries; all results visible to all participants. |
| Annotation layer | Participants can annotate charts and narrative cards with comments, visible to all session participants. |
| Session export | Export a complete shared session — all queries, results, narratives, lineage records — as a structured PDF or ZIP archive. |
| Permission boundary | Participant entitlements are applied individually — each participant's queries are governed by their own role claims. Results from one participant's query are not surfaced to another participant if the other participant would not be entitled to that result. |

---

## Phase 2 — Federated drilldown across engines

**Objective:** Enable drilldown traversal that spans multiple execution engines (currently drilldown is limited to sub-plans served by a single engine per hierarchy level).

| Item | Description |
|------|-------------|
| Cross-engine drilldown | The FQP coordinates drilldown across engines by identifying the affinity change point in the hierarchy and routing the child-level sub-plan to the appropriate engine. Result assembly handles the cross-engine join at the drilldown boundary. |
| Drilldown result merging | When a drilldown traversal produces sub-results from multiple engines, the FQP uses the shared dimension keys to assemble a coherent drilldown result. |

---

## Phase 2 — Analytical DSL extensions

**Objective:** Extend the Analytics DSL to support more complex analytical expressions.

| Item | Description |
|------|-------------|
| `RANK()` and `NTILE()` operations | Ranking metrics within a dimension (e.g. top-10 portfolios by return) expressible natively in DSL. Currently approximated by ordering + limiting. |
| `WINDOW()` analytics | Moving averages, rolling sums, period-over-period comparisons expressible as DSL window operations rather than separate queries. |
| `SCENARIO()` modifier | Compare actual metric values against scenario-adjusted values (e.g. stress test scenarios) within a single DSL expression. |
| `COMPOSITE_BENCHMARK()` | Define blended benchmark compositions inline in DSL without requiring pre-registration in the Benchmark Data Service. |

---

## Phase 3 — Headless analytics API

**Objective:** Expose the full analytical pipeline via a governed headless API for host applications to embed analytical results in their own interfaces without using the web component.

| Item | Description |
|------|-------------|
| REST analytics API | Full query, result, lineage, and SMR access via authenticated REST API. Same governance pipeline as the web component — no bypass path. |
| Result streaming | Stream FQP results to the host application in NDJSON format for real-time display in host-owned UI components. |
| Vega-Lite spec delivery | Return Vega-Lite chart specifications from the Visualisation Ontology as part of the query response — host renders the chart in their own UI using the platform-provided spec. |
| GraphQL layer | Optional GraphQL API over the headless analytics API for host applications with existing GraphQL infrastructure. |

---

## Not in roadmap

| Item | Rationale |
|------|-----------|
| Raw SQL passthrough | Architecturally prohibited — violates P1 (semantic abstraction). Not planned. |
| Physical schema exposure | Architecturally prohibited — violates P1. Not planned. |
| Unauthenticated analytical access | Violates P2 (governance before execution) and P5 (role-aware by default). Not planned. |
| LLM-selected chart types without ontology | Violates P7 (deterministic visualisation). Not planned. |
| Cross-tenant result federation | Data confidentiality constraint — tenant boundary is non-configurable. Not planned. |

---

*For current product specification, see [README.md](./README.md) and the numbered specification documents.*
