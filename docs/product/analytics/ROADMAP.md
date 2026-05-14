# AI Analytics Platform — Proposed Roadmap

This document describes **one proposed delivery sequence** for the AI Analytics Platform — a specific phasing of capabilities that represents a reasonable progression from a shippable v1.0 core to a full-featured platform. It is not the only valid sequence. The product specification (all numbered documents in this folder) defines what the platform must do; this roadmap describes one way to get there incrementally.

Phase boundaries, release contents, and sequencing should be revisited as implementation proceeds, customer feedback is gathered, and technical constraints are better understood. A decision to resequence a phase or move a component between releases should be documented here — it does not require changes to the product specification.

|                    |                           |
|--------------------|---------------------------|
| **Current release**| v1.0                      |
| **Date**           | May 2026                  |
| **Status**         | v1.0 in production; subsequent phases proposed, not committed |

---

## Release summary

| Release | Theme | End-user headline | Status |
|---------|-------|------------------|--------|
| **v1.0** | Governed semantic analytics core | Any MCP consumer can query governed metrics, receive results with charts, narrative, and full lineage | **Shipped** |
| **v1.1** | Scheduled queries and alert delivery | Metrics monitor themselves — users get Slack/webhook alerts when thresholds breach | Proposed |
| **v1.2** | SMR authoring assistance | Metric owners define new metrics in plain English; platform generates the YAML draft | Proposed |
| **v1.3** | Cross-session memory | Preferences, saved queries, and favourite metrics persist across sessions | Proposed |
| **v2.0** | Proactive analytical intelligence | Platform surfaces anomalies and trend signals without being asked | Proposed |
| **v2.1** | Collaborative analytical sessions | Multiple users share a governed session and co-explore data | Proposed |
| **v2.2** | Cross-backend drilldown | Drilldown traversal spans multiple registered execution backends | Proposed |
| **v2.3** | Analytical intent extensions | Ranking, window analytics, scenario comparison, and inline benchmarks in a single query | Proposed |
| **v3.0** | API surface extensions | SMR browser API, result streaming, GraphQL layer, lineage query API | Proposed |

---

## v1.0 — Governed Semantic Analytics Core

**Shipped: May 2026**

> **End-user outcome:** A portfolio manager, risk officer, or compliance analyst can ask a governed quantitative question — in natural language or via a structured MCP tool call — and receive a computed result with a chart, narrative summary, and a complete lineage record. The result uses only metrics registered in the SMR, is scoped to exactly what their role entitles them to see, and can be audited end-to-end.

### Shippable components

| Component | Functionality shipped in v1.0 |
|-----------|-------------------------------|
| **Platform Admin API** | Authenticated REST API for backend registration, SMR management, entitlement policy configuration, and tenant governance settings. Full CRUD on the Data Source Catalog, SMR metric definitions, and role entitlement records. |
| **Admin Console** | Web UI over the Platform Admin API. Metric definition editor, entitlement policy builder, Data Source Catalog manager, governance threshold controls. Application Admins and Metric Owners can manage the full platform configuration without writing JSON. |
| **Semantic Metrics Registry (SMR) service** | PostgreSQL primary store with row-level security; Elasticsearch metric search index. Metric CRUD with proposal → review → approved state machine. Append-only version records for each metric definition. Fuzzy metric search by name and description. |
| **MCP Capability Layer** | Cloudflare Workers edge deployment. JWT validation at the edge. Exposes four capabilities: `analyse_metric`, `compare_portfolios`, `list_metrics`, `get_metric_definition`. MCP Streamable HTTP transport. All requests authenticated; unauthenticated requests rejected before platform processing begins. |
| **Semantic Intent Layer** | Claude Sonnet (standard tier) for natural language → structured MCP tool call parameter translation. Claude Opus (complex tier) for multi-metric attribution queries and ambiguous intent. System prompt constructed from SMR metric and dimension names — no physical schema injected. Structured output validated against MCP tool input schema before proceeding. |
| **Analytical Intent Validator** | JSON schema validation of MCP tool call parameters. SMR ID resolution — rejects unregistered metric and dimension IDs. LQP (Logical Query Plan) generator — produces a backend-agnostic execution DAG from validated parameters. Intent confirmation card payload included in response when enabled. |
| **Role-Aware Projection Layer** | JWT claim extraction (`roles`, `managed_portfolios`, `entity_ids`, `display_name`). Row predicate injection into LQP from role definition templates. Column mask application to result assembly. Metric and dimension visibility enforcement per role. `defaultDenyAll: true` enforcement — users with no matching role receive ENTITLEMENT_DENIED before any query executes. |
| **Semantic Execution Governance** | Cost estimation before any backend call. Classification gate checks against metric data sensitivity levels. Circuit breakers: query complexity limit, per-tenant cost budget, per-user rate limit. All governance decisions logged with the lineage record before execution. Governance-blocked queries receive a structured error with the governance decision reason. |
| **Federated Query Planner (FQP)** | Apache Calcite plan optimiser for SQL sub-plan generation. SQL warehouse adapter (Snowflake, BigQuery, Databricks, Redshift, Trino, PostgreSQL). Semantic layer adapter (dbt MetricFlow, Cube.js). OpenData REST/OData adapter. Fan-out to multiple backends; result assembly in-memory. Per-tenant result cache (SHA-256 keyed; configurable TTL per metric refresh cadence). |
| **Visualisation Ontology** | Eight chart contracts: multi-series bar (comparison), time-series line (trend), heatmap (metric-vs-threshold), treemap (composition/concentration), scatter (relationship), waterfall (attribution/decomposition), stacked bar (composition over time), ranked bar (top-N). SCL display specification generation (Vega-Lite v5 JSON). Platform-defined `type: "table"` extension for tabular results. Chart contract selection is deterministic — governed by result schema and intent pattern, not inferred by LLM. |
| **Narrative Synthesis Engine** | Claude Haiku (default) for standard analytical prose. Claude Sonnet for multi-portfolio attribution and regulatory narratives. Prose strictly anchored to computed result values — post-generation validation rejects any numeric value not present in the result set. `narrative.lead`, `narrative.detail`, and `narrative.anchoredTo` fields in response. |
| **Analytical Lineage Store** | PostgreSQL structured lineage records. One record per executed query: intent, SMR definition versions used, tool call parameters, role projection record, LQP, per-backend sub-plans and raw responses, assembled result, governance decisions, SCL display spec. Lineage inspector API — retrieve full lineage by `result_id`. Result artefacts (CSV downloads, large datasets) in S3-compatible object storage; URL referenced in lineage record. 7-year default retention for regulated deployments. |
| **vite2img rendering service** | Vite + vega-embed + headless Chromium (Playwright). Renders any Vega-Lite v5 SCL spec to SVG or PNG. Renders `type: "table"` display specs via styled HTML table template. Used by report pipelines and agentic consumers that need static images for PDF embedding. |

### Infrastructure shipped

| Component | Technology | Notes |
|-----------|-----------|-------|
| Edge runtime | Cloudflare Workers | MCP Capability Layer — global anycast, sub-10ms cold start |
| Backend services | Kubernetes (cloud-agnostic) | FQP, Governance, SMR, Lineage Store as independently scalable pods |
| Primary database | PostgreSQL (managed — Neon or RDS) | SMR, lineage records, tenant config, preference store |
| Metric search index | Elasticsearch / OpenSearch | SMR metric name/description fuzzy search |
| Result cache | Platform-managed in-memory + PostgreSQL | Per-tenant, TTL-governed; >10MB results bypass cache and stream directly |
| Object storage | S3-compatible | Result artefacts, CSV exports, vite2img output |
| Secrets management | HashiCorp Vault or cloud-native equivalent | Backend API keys, platform service credentials |

### What is NOT in v1.0

- No scheduled or recurring query execution
- No alert threshold monitoring or push delivery
- No SMR natural language authoring assistance
- No cross-session user preferences or saved queries
- No multi-user shared sessions
- No cross-backend drilldown (drilldown limited to single-backend sub-plans per hierarchy level)
- No ranking / window / scenario / inline benchmark query parameters
- No SMR browser REST API, result streaming, or GraphQL layer

---

## v1.1 — Scheduled Queries and Alert Delivery

> **End-user outcome:** A risk officer registers a daily VaR breach check once. From that point, the platform runs it automatically every morning and sends a Slack message — with a lineage-referenced chart attached — whenever any portfolio exceeds its VaR limit. No manual query required.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Scheduled Query Service** | Application Admins and Power Analysts register any valid `analyse_metric` or `compare_portfolios` call as a scheduled query using cron expressions. Scheduled queries run through the full governance pipeline using the registered owner's entitlement claims at execution time — no elevated privilege at runtime. Results written to the Analytical Lineage Store and result artefact store. |
| **Alert Threshold Engine** | Define up to 10 threshold conditions per scheduled query (e.g. `var_95 > var_limit`, `tracking_error > 3.2`). Engine evaluates conditions against each result row after FQP assembly. Supports `gt`, `lt`, `gte`, `lte`, `eq`, `pct_change_gt` operators. Each breach event generates a lineage record linked to the triggering query. |
| **Push Delivery Service** | Webhook delivery to any HTTPS endpoint. Email delivery via SMTP integration. Slack delivery via Slack MCP server. Each delivery payload includes the `result_id`, the breached threshold description, the SCL display spec (chart or table), and the lineage URL. Delivery failures retry with exponential backoff; undeliverable events logged in the audit trail. |
| **Scheduled Query Admin UI** | New Admin Console section: schedule management (create, edit, pause, delete scheduled queries), threshold configuration, delivery endpoint management, execution history, and alert audit log. |

### Acceptance criteria

- A scheduled query with a 09:00 cron fires within 60 seconds of its scheduled time
- An alert delivery reaches the registered webhook within 30 seconds of breach detection
- Every alert event has a lineage record; lineage completeness metric remains 100%
- Scheduled queries respect the owner's entitlements at execution time — not superuser access

### Pre-requisites

Cron execution infrastructure (Kubernetes CronJob or cloud-native scheduler); message queue for async delivery (SQS / Pub/Sub — already in v1.0 infra stack); Slack MCP server available in the deployment environment.

---

## v1.2 — SMR Authoring Assistance

> **End-user outcome:** A Head of Fixed Income Risk needs to register a new metric — `modified_duration_weighted`. Instead of writing YAML from scratch, they describe it in two sentences. Within 30 seconds they have a complete draft YAML definition with formula, aggregation rule, dimensions, and data domain inferred. They review, adjust one field, and submit for Application Admin approval — no YAML knowledge required.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Natural Language → Metric Draft Generator** | Metric Owner or Application Admin describes a metric in prose via the Admin Console. Claude Sonnet generates a complete SMR YAML draft: `id`, `label`, `formula`, `aggregation`, `dimensions`, `data.domain`, `units`, `description`. Output validated against the SMR schema before presenting for review. Draft enters the existing `proposed` state — it cannot be activated without Application Admin approval. |
| **SMR Consistency Checker** | Before the draft is presented for review, it is automatically compared against all existing active metric definitions. Flags: potential duplicate (cosine similarity > 0.85 on formula or description), naming conflict (similar `id` or `label`), dimension mismatch (references dimensions not registered in SMR), data domain mismatch (inferred domain not in Data Source Catalog). Findings shown to the reviewer with resolution suggestions. |
| **Metric Draft Review UI** | New Admin Console draft review screen. Side-by-side view: original prose description vs. generated YAML. Inline field editing before submission. Consistency checker findings shown in-context. One-click submit to standard approval workflow. Edit history preserved. |

### Acceptance criteria

- Generated YAML draft passes SMR JSON schema validation in ≥ 90% of cases without manual correction
- Consistency checker correctly identifies exact duplicates in 100% of cases; approximate duplicates in ≥ 80%
- Draft metric cannot be queried until approved — no bypass path
- All draft generation events logged (input prose, generated YAML, reviewer identity, approval outcome)

### Pre-requisites

v1.0 SMR approval workflow; Claude Sonnet API access with prompt caching enabled for SMR context injection.

---

## v1.3 — Cross-Session Memory

> **End-user outcome:** A Power Analyst who always starts with equity portfolios, quarterly period, and tracking error as their first dimension no longer has to re-specify these each morning. Their saved "Monday risk sweep" query is one click away and automatically flagged if a metric definition change has invalidated it since they last ran it.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **User Preference Store** | Per-user persisted preferences (PostgreSQL, scoped by `tenant_id` + `sub`): default time period, default dimensions, preferred chart type overrides (Power Analyst only), preferred measure groups, UI density preference. Applied as defaults in intent resolution — user can override per query. |
| **Saved Query Registry** | Named analytical queries saved by Power Analysts and Application Admins. Each saved query stores the exact validated MCP tool call parameters (not natural language). Version-controlled: when a metric or dimension in a saved query changes in the SMR, the query is flagged as `needs_review` and the owner notified. Saved queries are private by default; Application Admins can promote a saved query to tenant-wide visibility. |
| **Favourite Metrics Index** | Users mark SMR metrics as personal favourites. Favourites surfaced first in `list_metrics` results, intent resolution disambiguation suggestions, and the SMR browser. Favourites are per-user and never affect other users' results. |
| **Preference and Saved Query UI** | New "My Workspace" section in any consuming UI (or accessible via Admin API). Preference editor, saved query list (with staleness indicator), favourites management. |

### Acceptance criteria

- User preferences applied consistently — the same user sees the same defaults across sessions and across devices
- A saved query flagged as `needs_review` due to SMR change cannot be silently executed with stale parameters — user must acknowledge the change
- No preference leaks across tenants or users — strict `tenant_id` + `sub` isolation
- Preferences do not affect governance or entitlement enforcement — they are display defaults only

### Pre-requisites

v1.0 User identity model (JWT `sub` claim); PostgreSQL preference schema migration; Admin Console extensible enough to host new "My Workspace" section.

---

## v2.0 — Proactive Analytical Intelligence

> **End-user outcome:** A portfolio manager opens the platform on Monday morning to find three proactive insight cards waiting for them — one flagging that the tracking error on Global Equity has climbed above its 90-day average for three consecutive weeks, one noting that Emerging Markets debt concentration has reached a 12-month high, and one showing that two portfolios have moved into the top decile of their peer group. None of these required a manual query.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Anomaly Detection Service** | Background service that monitors scheduled query results. For each metric series, maintains a configurable statistical baseline (rolling mean ± N standard deviations; configurable lookback window). Generates a proactive insight event when a metric value falls outside the baseline. Anomaly events are scoped to the role that owns the scheduled query — no cross-entitlement visibility. |
| **Trend Signal Detector** | Identifies metrics showing consistent directional movement across configurable consecutive periods (e.g. 3 periods up, configurable). Trend signals generated as insight events with the metric ID, direction, number of consistent periods, and the lineage reference to the underlying data. |
| **Proactive Insight Card Delivery** | Insight events delivered as structured cards to the consumer's registered notification endpoint (same delivery infrastructure as v1.1 alerts). Cards include: insight type (anomaly / trend), metric ID and label, the observed value vs. baseline, a narrative summary (Haiku-generated, anchored to the anomaly data), and the `result_id` for lineage inspection. |
| **Peer Comparison Signals** | Where the Benchmark Data Service or Regulatory Reference Service is registered, the anomaly service extends its baseline to include peer percentile comparisons. A metric that moves from the 3rd to 1st quartile of its peer group generates a peer comparison signal. |
| **Insight Configuration UI** | Application Admins configure per-metric anomaly detection settings: baseline window, sensitivity (N standard deviations), minimum signal strength (suppress noise below a configurable threshold), and opt-in/opt-out per user role. |

### Acceptance criteria

- Anomaly detection runs on the same schedule as the underlying scheduled query — no additional latency beyond delivery time
- Anomaly insight events respect the entitlement of the scheduled query owner — no data outside their projection scope
- False positive rate configurable — default sensitivity set so < 10% of signals are dismissed by users (monitored via insight card dismissal rate)
- Every insight card has a lineage reference — users can inspect the underlying data from any card

### Pre-requisites

v1.1 Scheduled Query Service (anomaly detection runs against scheduled query result series); statistical baseline storage (time-series extension to lineage store or dedicated metric series store).

---

## v2.1 — Collaborative Analytical Sessions

> **End-user outcome:** A portfolio manager and a risk officer join the same analytical session before an investment committee meeting. The portfolio manager submits a performance attribution query; the risk officer submits a VaR decomposition. Both sets of results are visible to both participants — but each result is governed by the submitting user's entitlements. They annotate the charts together, then export the full session as a PDF pack for the committee.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Session Sharing Service** | Authenticated users within the same tenant can invite other authenticated users to an active analytical session by `sub` claim. Invitee receives a session join link valid for 24 hours. Both users can submit queries; all results are visible to all active session participants. Session has an owner (the inviting user); only the owner can close the session or revoke access. |
| **Per-Participant Governance Engine** | Each query submitted in a shared session is evaluated using the submitting participant's own entitlements — not the session owner's. Results from a query the invitee would not be entitled to run are not surfaced to participants who lack that entitlement. The governance engine tags each result with the submitting participant's `sub` and the entitlement projection applied. |
| **Annotation Layer** | Session participants can annotate any result card — chart, table, or narrative — with free-text comments. Annotations are visible to all current session participants. Annotations are stored in the session record and included in session exports. Annotations are not operational data — they do not affect query execution or lineage records. |
| **Session Export Service** | Export a complete shared session as a structured PDF (all query cards, charts rendered via vite2img, narrative summaries, annotations) or as a ZIP archive (PDF + raw JSON result sets + lineage URLs). Export is flagged in the audit trail as a session export artefact. `requireLineageForExport: true` governance config applies — each exported result includes its `result_id` and lineage URL. |

### Acceptance criteria

- Participant entitlements are independently enforced — participant A cannot see a result that participant B's query produced if participant A would receive ENTITLEMENT_DENIED for the same query
- All shared session events (joins, queries, annotations, exports) logged in the audit trail under individual participant identities — not merged into a single session identity
- Session export includes a lineage reference for every result — no result appears in an exported PDF without a traceable `result_id`
- Session state is consistent across participants — a result submitted by one participant appears for all within 2 seconds (p99)

### Pre-requisites

v1.0 Analytical Lineage Store; v1.1 Push Delivery Service (for session join notifications); v1.0 vite2img (for PDF rendering of charts).

---

## v2.2 — Cross-Backend Drilldown

> **End-user outcome:** An analyst drilling from portfolio-level issuer concentration (sourced from the SQL warehouse) into the network of legal entity relationships for the top-concentration issuer (sourced from the Graph Data API) navigates in one continuous drilldown — no need to open a separate query.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **FQP Cross-Backend Affinity Resolver** | Enhancement to the Federated Query Planner. When a drilldown traversal crosses a `dataAffinity` boundary (e.g. from `positions` domain served by SQL warehouse to `entity_relationships` domain served by Graph API), the FQP identifies the boundary point in the hierarchy and routes the child-level sub-plan to the appropriate backend. The parent result's projection scope and governance context are passed to the child sub-plan. |
| **Drilldown Result Merger** | Enhancement to FQP result assembly. When a drilldown produces sub-results from two different backends, the FQP uses shared dimension keys (e.g. `issuer_id`) to join child rows back to parent rows. The merged result is assembled into a single SCL display spec — the consumer sees a coherent drilldown result, not a split across two responses. |
| **Cross-Backend Drilldown Lineage** | Lineage record extended to capture the affinity boundary crossing: which backend served the parent level, which backend served the child level, and the dimension key used to join them. |

### Acceptance criteria

- Drilldown traversal that crosses a backend boundary completes within 500ms additional latency vs. same-backend drilldown (p95)
- Merged drilldown result is a single SCL display spec — consumer does not need to handle multi-part responses
- If the child-level backend is unavailable, the drilldown returns a structured error (not a partial result with a silent gap)
- Lineage record for cross-backend drilldown is complete — both backends' sub-plans and raw responses captured

### Pre-requisites

v1.0 FQP with Graph Data API adapter registered; at least one tenant with both SQL warehouse and Graph API backends registered for the same analytical domain hierarchy.

---

## v2.3 — Analytical Intent Extensions

> **End-user outcome:** A performance analyst asks "show me the top 10 portfolios by quarter-to-date return with a 30-day moving average and comparison to the MSCI World blend" in a single query — rather than running separate queries for ranking, the moving average, and the benchmark comparison and assembling them manually.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Ranking and Percentile Query Parameters** | `rank_by` parameter: rank result rows by any metric in the result set. `rank_direction`: `ASC` or `DESC`. `rank_limit`: return only the top/bottom N rows. `rank_percentile`: return rows above/below a percentile threshold. These replace the current workaround of ordering + limiting, which does not apply ranking semantics correctly in federated results. |
| **Window Analytics Parameters** | `window_op` parameter: `moving_average`, `rolling_sum`, `period_over_period`. `window_size`: number of periods. `window_anchor`: `trailing` or `centred`. Window operations computed at FQP result assembly — not delegated to backends that may not support them. |
| **Scenario Comparison Parameter** | `scenario` parameter: compare actual metric values against a registered scenario definition (stress test, budget, or forecast registered in the SMR). Scenario definitions are registered by Application Admins in the SMR. A scenario comparison query returns actual values, scenario values, and the delta as a single result set. |
| **Inline Composite Benchmark** | `benchmark` dimension field accepts either a pre-registered Benchmark Data Service ID or an inline composition object (`[{ "benchmark_id": "b_msci_world", "weight": 0.60 }, ...]`). Inline compositions are resolved at query time — no pre-registration required. Inline compositions are not persisted; they are logged in the lineage record. |

### Acceptance criteria

- `rank_by` + `rank_limit` applied correctly in federated results — rankings are computed across the full assembled result set, not within each backend's sub-result
- Window operations produce the same result as an equivalent backend-level window function for backends that support it — verified in integration tests
- Scenario comparison results include both actual and scenario values in the same result set — consumer does not need to join two separate queries
- Inline benchmark compositions are logged in the lineage record — auditors can reconstruct the exact composition used in any query

### Pre-requisites

v1.0 Analytical Intent Validator with parameter model extensibility; v1.0 FQP result assembly layer for window computation; v1.0 Benchmark Data Service integration for composite benchmark resolution.

---

## v3.0 — API Surface Extensions

> **End-user outcome:** A compliance engineering team builds a bespoke regulatory audit dashboard that queries the lineage store directly by metric ID and time range. A BI team integrates the Analytics Platform into their existing GraphQL gateway with no protocol translation work. A report pipeline begins streaming FQP results progressively rather than waiting for full assembly.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **SMR Browser REST API** | `GET /v1/smr/metrics` — paginated list of active metric definitions. `GET /v1/smr/metrics/{id}` — full metric definition including formula, aggregation rule, dimension list, data domain, owner, and version history. `GET /v1/smr/dimensions` — dimension catalogue. `GET /v1/smr/hierarchies` — drilldown hierarchy definitions. All endpoints authenticated by JWT; results scoped to the user's entitled metric visibility. Enables consumers to build metric discovery, browsing, and documentation experiences without screen-scraping the Admin Console. |
| **NDJSON Result Streaming** | The MCP Capability Layer and FQP support streaming delivery of assembled sub-plan results in NDJSON format. Consumers receive individual backend sub-results as they arrive — rather than waiting for full assembly. First sub-result delivered within 200ms of FQP execution start (p95). Streaming responses include a terminal frame with the complete assembled result, SCL display spec, and lineage URL. Compatible with existing non-streaming consumers (full response frame always present). |
| **GraphQL API Gateway** | Optional GraphQL schema layer over the MCP endpoint. Exposes `analyseMetric`, `comparePortfolios`, `listMetrics`, `getMetricDefinition`, and `drilldown` as GraphQL queries with typed input and output schemas. JWT auth via HTTP header. Enables consumers with existing GraphQL infrastructure to integrate without MCP client tooling. GraphQL layer is a passthrough — all requests route through the same governance pipeline as MCP calls; no governance bypass. |
| **Lineage Query REST API** | `GET /v1/lineage/{result_id}` — retrieve full lineage record for a result. `POST /v1/lineage/search` — search lineage records by `user_sub`, `metric_id`, `time_range`, `backend_id`, or `governance_decision`. `GET /v1/lineage/{result_id}/sub-plans` — retrieve per-backend sub-plans and raw responses for a result. Paginated; JWT-scoped to the querying user's own lineage records (Platform Admins can query tenant-wide). Enables regulatory audit tooling, compliance review dashboards, and operational monitoring to be built directly against the lineage store without direct database access. |

### Acceptance criteria

- SMR Browser API results are consistent with the Admin Console SMR view — same data, same entitlement scoping
- Streaming first-frame latency is ≤ 200ms (p95) — measurably faster than full assembly for multi-backend queries
- GraphQL responses are byte-for-byte equivalent to MCP responses — the API layer adds no data transformation
- Lineage query API search latency ≤ 500ms for queries over 7-year retention window (p95) — usable for real-time compliance review

### Pre-requisites

v1.0 Analytical Lineage Store with indexed search; v1.0 SMR service with read API; v1.0 FQP result assembly refactored to support incremental streaming (internal architecture prerequisite).

---

## Not in roadmap

| Item | Rationale |
|------|-----------|
| **Raw SQL passthrough** | Architecturally prohibited. Violates P1 (semantic abstraction over physical exposure) and P10 (deterministic computation, not generation). Not planned at any version. |
| **Physical schema exposure to AI model** | Architecturally prohibited. Violates P1. The Semantic Intent Layer receives SMR metric and dimension names — no table names, column names, or JOIN paths. Not planned. |
| **Ad hoc LLM-generated SQL** | Architecturally prohibited. Violates P2 (governance before execution) and P10. All queries are expressed as validated MCP tool call parameters resolved against the SMR. Not planned. |
| **Unauthenticated analytical access** | Violates P2 and P5 (role-aware by default). JWT validation at the edge is non-negotiable. Not planned. |
| **LLM chart type selection outside Visualisation Ontology** | Violates P7 (deterministic visualisation). Chart selection is always governed by registered chart contracts. LLM intent signals are inputs to the ontology — not direct rendering instructions. Not planned. |
| **Cross-tenant result federation** | Tenant boundary is a non-configurable isolation guarantee (A9). Not planned. |
| **Metric value generation by AI model** | Violates P10. Every number in a result is computed from a registered definition applied to data from a registered backend. AI models produce intent translations and narrative prose only. Not planned. |

---

*This is a proposed delivery sequence, not a committed plan. For the product specification, see [README.md](./README.md) and the numbered specification documents. For the proposed reference implementation stack, see [17-proposed-technical-architecture.md](./17-proposed-technical-architecture.md).*
