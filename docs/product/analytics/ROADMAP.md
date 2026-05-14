# AI Analytics Platform — Roadmap

|                    |                           |
|--------------------|---------------------------|
| **Current release**| v1 — governed semantic analytics layer, SMR, Analytical Intent Validator, FQP, role-aware projection, visualisation ontology, MCP capability layer |
| **Date**           | May 2026                  |

---

## Near-term — Scheduled and alert-driven queries

**Objective:** Allow analytical queries to be scheduled for recurring execution and trigger alert workflows when metric thresholds are breached.

| Item | Description |
|------|-------------|
| Scheduled query registration | Application Admins and Power Analysts register analytical queries for scheduled execution (cron-based). Scheduled queries run through the full governance pipeline using the owner's entitlement claims at execution time. Results written to the result artefact store. |
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

## Phase 2 — Federated drilldown across backends

**Objective:** Enable drilldown traversal that spans multiple execution backends (currently drilldown is limited to sub-plans served by a single backend per hierarchy level).

| Item | Description |
|------|-------------|
| Cross-backend drilldown | The FQP coordinates drilldown across backends by identifying the affinity change point in the hierarchy and routing the child-level sub-plan to the appropriate backend. Result assembly handles the cross-backend join at the drilldown boundary. |
| Drilldown result merging | When a drilldown traversal produces sub-results from multiple backends, the FQP uses the shared dimension keys to assemble a coherent drilldown result. |

---

## Phase 2 — Analytical intent extensions

**Objective:** Expand the analytical intent parameter model to support more complex query patterns via new MCP tool capabilities.

| Item | Description |
|------|-------------|
| Ranking and percentile queries | Ranking metrics within a dimension (e.g. top-10 portfolios by return) expressed as `rank_by` and `limit` parameters. Currently approximated by ordering + limiting. |
| Window analytics | Moving averages, rolling sums, and period-over-period comparisons expressed as dedicated window operation parameters rather than requiring separate queries. |
| Scenario comparison | Compare actual metric values against scenario-adjusted values (e.g. stress test scenarios) within a single query via a `scenario` parameter. |
| Composite benchmark definition | Define blended benchmark compositions inline in the query without requiring pre-registration in the Benchmark Data Service. |

---

## Phase 3 — API surface extensions

**Objective:** Expand the headless API surface and delivery options for host consumers.

| Item | Description |
|------|-------------|
| SMR browser API | Full read access to the tenant's SMR — metric definitions, dimensions, hierarchies — via authenticated REST endpoints. Enables consumers to build metric discovery and browsing experiences. |
| Result streaming | Stream FQP results to consumers in NDJSON format for real-time progressive display as sub-plan results arrive. |
| GraphQL layer | Optional GraphQL API layer over the MCP endpoint for consumers with existing GraphQL infrastructure. |
| Lineage query API | Direct queryable access to the lineage store — search by user, metric, time range, or result ID. Supports regulatory audit tooling. |

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
