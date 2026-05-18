# AI Analytics Platform — Proposed Roadmap

This document describes **one proposed sequence of deliverables** for the AI Analytics Platform — a progression from an initial MVP to a full target-state platform. It is not the only valid sequence, and it is not a committed delivery plan. The product specification (all numbered documents in this folder) defines what the platform must do; this roadmap describes one way to build toward that in meaningful, shippable increments.

Phase boundaries and sequencing should be revisited as implementation proceeds, customer feedback is gathered, and technical constraints become clearer. Decisions to resequence or regroup phases should be recorded here — they do not require changes to the product specification.

---

## Delivery sequence

| Phase | What is achieved | End-user headline |
|-------|-----------------|-------------------|
| **Governed Analytical Core** | The complete governed query pipeline — any MCP consumer can query registered metrics with full lineage | A portfolio manager asks a quantitative question and gets a governed, auditable result |
| **Automated Monitoring and Alerts** | Queries run on a schedule; thresholds trigger push notifications | A risk officer receives a Slack alert when VaR breaches its limit — no manual check needed |
| **SMR Authoring Assistance** | Metric owners define new metrics in plain English | A Head of Fixed Income describes a metric in two sentences and gets a YAML draft back in 30 seconds |
| **Cross-Session Memory** | Preferences, saved queries, and favourites persist across sessions | A Power Analyst opens the platform each morning with their context already applied |
| **Proactive Analytical Intelligence** | Platform surfaces anomalies and trends without being asked | A portfolio manager finds insight cards waiting on Monday morning — no queries submitted |
| **Collaborative Sessions** | Multiple users share a governed session and co-explore data | A portfolio manager and risk officer jointly prepare an investment committee pack |
| **Ecosystem Service Integrations** | Regulatory Reference, Benchmark Data, and Semantic Registry Services connected as registered backends | Regulatory metrics sourced from the authoritative service; benchmark queries use licensed index data without internal ingestion |
| **Regulatory Compliance Modes** | MiFID II, Basel III/IV, and SEC Reg BI compliance profiles active in the governance pipeline | A Basel III LCR query automatically writes a regulatory snapshot; a MiFID II user is prompted for business justification before client-data queries |
| **Cross-Backend Drilldown** | Drilldown traversal spans multiple registered execution backends | An analyst drills from warehouse data into graph relationships in one continuous navigation |
| **Advanced Query Capabilities** | Ranking, window analytics, scenario comparison, and inline benchmarks in a single query | A performance analyst composes a complex multi-dimensional query without splitting it into parts |
| **Open API Surface** | SMR browser API, result streaming with progress events, GraphQL layer, lineage query API, FQP adaptive planning, materialised views | A compliance team queries the lineage store directly; high-frequency queries hit pre-computed materialised views; consumers see real-time progress during query execution |

---

## MVP — Governed Analytical Core

> **What this achieves:** Any MCP-compatible consumer — a conversational AI assistant, a custom application, or an autonomous agent — can submit a governed analytical query against registered metrics and receive a computed result with a chart specification, a governed narrative summary, and a complete lineage record. The result uses only metrics registered in the SMR, is scoped to exactly what the user's role entitles them to see, and every step from intent to result is auditable.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Platform Admin API** | Authenticated REST API for backend registration, SMR management, entitlement policy configuration, and tenant governance settings. Full CRUD on the Data Source Catalog, SMR metric definitions, and role entitlement records. |
| **Admin Console** | Web UI over the Platform Admin API. Metric definition editor, entitlement policy builder, Data Source Catalog manager, governance threshold controls. Application Admins and Metric Owners manage the full platform configuration without writing JSON. |
| **Semantic Metrics Registry (SMR) service** | PostgreSQL primary store with row-level security; Elasticsearch metric search index. Metric CRUD with proposal → review → approved state machine. Append-only version records for each metric definition. Fuzzy metric search by name and description. |
| **Financial Services Reference Model** | Bundled industry seed model covering six analytical domains: `portfolio`, `performance`, `risk`, `regulatory`, `counterparty`, `benchmarks`. Includes pre-built metric definitions (AUM, portfolio return, tracking error, VaR, issuer concentration, LCR, NSFR, and others), dimension schemas, drilldown hierarchies (asset class, geography, sector), and measure groups. Platform administrators seed their SMR at setup by specifying `analyticalDomain: "wealth_management"`, `"banking"`, or `"investment_management"` in the platform config — the relevant subset of the reference model is imported as the tenant's starting SMR baseline. All imported definitions enter the standard `proposed` → approval workflow before becoming resolvable. Definitions may be customised or superseded via the Admin API. |
| **MCP Capability Layer** | Cloudflare Workers edge deployment. JWT validation at the edge. MCP Streamable HTTP transport. All requests authenticated; unauthenticated requests rejected before platform processing begins. Exposes eight analytical capabilities: `analyse_metric` (governed metric query), `compare_portfolios` (cross-portfolio comparison with optional benchmark), `issuer_concentration` (concentration risk calculation), `risk_breakdown` (risk factor attribution — VaR, tracking error, beta), `performance_attribution` (BHB/BF attribution decomposition), `regulatory_metric` (LCR, NSFR, leverage ratio — feature-flag gated), `list_metrics` (SMR metric catalogue for the authenticated user), `drilldown` (hierarchy traversal from a prior result). Capability manifest endpoint returns per-user, per-tenant availability for each capability including feature flag gating. |
| **Semantic Intent Layer** | Deterministic parameter validation and LQP generation — no AI model. JSON schema validation of MCP tool call parameters. SMR ID resolution — rejects unregistered metric and dimension IDs. LQP (Logical Query Plan) generator — produces a backend-agnostic execution DAG from validated parameters. Intent confirmation card payload included in response when enabled. |
| **Role-Aware Projection Layer** | JWT claim extraction (`roles`, `managed_portfolios`, `entity_ids`, `display_name`). Row predicate injection into LQP from role definition templates. Column mask application to result assembly. Metric and dimension visibility enforcement per role. `defaultDenyAll: true` enforcement — users with no matching role receive ENTITLEMENT_DENIED before any query executes. |
| **Semantic Execution Governance** | Cost estimation before any backend call. Classification gate checks against metric data sensitivity levels. Circuit breakers: query complexity limit, per-tenant cost budget, per-user rate limit. All governance decisions logged with the lineage record before execution. Governance-blocked queries receive a structured error with the governance decision reason. |
| **Federated Query Planner (FQP)** | Apache Calcite plan optimiser for SQL sub-plan generation. SQL warehouse adapter (Snowflake, BigQuery, Databricks, Redshift, Trino, PostgreSQL). Semantic layer adapter (dbt MetricFlow, Cube.js). OpenData REST/OData adapter. Fan-out to multiple backends; result assembly in-memory. Per-tenant result cache (SHA-256 keyed; configurable TTL per metric refresh cadence). |
| **Visualisation Ontology** | Eight chart contracts: multi-series bar (comparison), time-series line (trend), heatmap (metric-vs-threshold), treemap (composition/concentration), scatter (relationship), waterfall (attribution/decomposition), stacked bar (composition over time), ranked bar (top-N). SCL display specification generation (Vega-Lite v5 JSON). Platform-defined `type: "table"` extension for tabular results. Chart contract selection is deterministic — governed by result schema and intent pattern, not inferred by LLM. |
| **Narrative Synthesis Engine** | Claude Haiku (default) for standard queries (≤ 5 metrics, ≤ 3 dimensions). Claude Sonnet for attribution, multi-portfolio, and regulatory narratives. Prompt constructed from result set only — no user query, no physical schema. `narrative.lead`, `narrative.detail`, and `narrative.anchoredTo` fields in response. Post-generation validation rejects any numeric value not present in the result set; single regeneration attempted on failure. Controlled by `features.narrativeSynthesis` tenant flag. |
| **Analytical Lineage Store** | PostgreSQL structured lineage records. One record per executed query: intent, SMR definition versions used, tool call parameters, role projection record, LQP, per-backend sub-plans and raw responses, assembled result, governance decisions, SCL display spec. Lineage inspector API — retrieve full lineage by `result_id`. Result artefacts (CSV downloads, large datasets) in S3-compatible object storage; URL referenced in lineage record. 7-year default retention for regulated deployments. |
| **vite2img rendering service** | Vite + vega-embed + headless Chromium (Playwright). Renders any Vega-Lite v5 SCL spec to SVG or PNG. Renders `type: "table"` display specs via styled HTML table template. Used by report pipelines and agentic consumers that need static images for PDF embedding. |

### Infrastructure

| Component | Technology | Notes |
|-----------|-----------|-------|
| Edge runtime | Cloudflare Workers | MCP Capability Layer — global anycast, sub-10ms cold start |
| Backend services | Kubernetes (cloud-agnostic) | FQP, Governance, SMR, Lineage Store as independently scalable pods |
| Primary database | PostgreSQL (managed — Neon or RDS) | SMR, lineage records, tenant config, preference store |
| Metric search index | Elasticsearch / OpenSearch | SMR metric name/description fuzzy search |
| Result cache | Platform-managed in-memory + PostgreSQL | Per-tenant, TTL-governed; >10MB results bypass cache and stream directly |
| Object storage | S3-compatible | Result artefacts, CSV exports, vite2img output |
| Message queue | Cloud-native (SQS / Pub/Sub) | Async lineage writes, governance audit events |
| Secrets management | HashiCorp Vault or cloud-native equivalent | Backend API keys, platform service credentials |

### Acceptance criteria

- A structured tool call resolves to a governed result with an SCL display spec, narrative, and lineage record in under 3 seconds (p95)
- An unregistered metric ID in a tool call returns a structured METRIC_NOT_FOUND error — no partial execution
- A user with no matching role claim receives ENTITLEMENT_DENIED before any query reaches an execution backend
- Every executed query — successful or governance-blocked — has a complete lineage record (lineage completeness: 100%)

---

## Automated Monitoring and Alerts

> **What this achieves:** Analytical queries can be registered to run on a schedule. When metric values breach defined thresholds, the platform delivers a push notification — with a lineage-referenced chart — to a registered endpoint. The platform monitors itself so users do not have to.

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
- Every alert event has a lineage record; lineage completeness remains 100%
- Scheduled queries respect the owner's entitlements at execution time — no superuser access at runtime

### Depends on

Governed Analytical Core (full governance pipeline, lineage store, result artefact store); cron execution infrastructure (Kubernetes CronJob or cloud-native scheduler); Slack MCP server available in the deployment environment.

---

## SMR Authoring Assistance

> **What this achieves:** Metric owners and Application Admins can describe a new metric in plain English and receive a complete, schema-valid draft YAML definition for review — with automatic consistency checking against existing metric definitions. No YAML authoring knowledge required to propose a new metric.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Natural Language → Metric Draft Generator** | Metric Owner or Application Admin describes a metric in prose via the Admin Console. Claude Sonnet generates a complete SMR YAML draft: `id`, `label`, `formula`, `aggregation`, `dimensions`, `data.domain`, `units`, `description`. Output validated against the SMR schema before presenting for review. Draft enters the existing `proposed` state — it cannot be activated without Application Admin approval. |
| **SMR Consistency Checker** | Before the draft is presented for review, it is automatically compared against all existing active metric definitions. Flags: potential duplicate (cosine similarity > 0.85 on formula or description), naming conflict (similar `id` or `label`), dimension mismatch (references dimensions not registered in the SMR), data domain mismatch (inferred domain not in the Data Source Catalog). Findings shown to the reviewer with resolution suggestions. |
| **Metric Draft Review UI** | New Admin Console draft review screen. Side-by-side view: original prose description vs. generated YAML. Inline field editing before submission. Consistency checker findings shown in-context. One-click submit to standard approval workflow. Edit history preserved. |

### Acceptance criteria

- Generated YAML draft passes SMR JSON schema validation in ≥ 90% of cases without manual correction
- Consistency checker correctly identifies exact duplicates in 100% of cases; approximate duplicates in ≥ 80%
- Draft metric cannot be queried until approved — no bypass path through the authoring flow
- All draft generation events logged (input prose, generated YAML, reviewer identity, approval outcome)

### Depends on

Governed Analytical Core (SMR approval workflow, Admin Console); Claude Sonnet API access with prompt caching enabled for SMR context injection.

---

## Cross-Session Memory

> **What this achieves:** User preferences, saved queries, and favourite metrics persist across sessions. Returning users find their analytical context pre-applied. Saved queries are version-controlled against the SMR — changes to metric definitions surface as a staleness warning rather than silent breakage.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **User Preference Store** | Per-user persisted preferences (PostgreSQL, scoped by `tenant_id` + `sub`): default time period, default dimensions, preferred chart type overrides (Power Analyst only), preferred measure groups, UI density preference. Applied as defaults in intent resolution — user can override per query. |
| **Saved Query Registry** | Named analytical queries saved by Power Analysts and Application Admins. Each saved query stores the exact validated MCP tool call parameters (not natural language). Version-controlled: when a metric or dimension in a saved query changes in the SMR, the query is flagged as `needs_review` and the owner notified. Saved queries are private by default; Application Admins can promote a saved query to tenant-wide visibility. |
| **Favourite Metrics Index** | Users mark SMR metrics as personal favourites. Favourites surfaced first in `list_metrics` results, intent resolution disambiguation suggestions, and the SMR browser. Favourites are per-user and never affect other users' results. |
| **My Workspace UI** | New section in any consuming UI (or accessible via Admin API). Preference editor, saved query list (with staleness indicator), favourites management. |

### Acceptance criteria

- User preferences applied consistently — the same user sees the same defaults across sessions and across devices
- A saved query flagged as `needs_review` due to an SMR change cannot be silently executed with stale parameters — user must acknowledge the change
- No preference or saved query data leaks across tenants or users — strict `tenant_id` + `sub` isolation
- Preferences do not affect governance or entitlement enforcement — they are display defaults only

### Depends on

Governed Analytical Core (JWT `sub` claim for user identity, PostgreSQL for preference store, SMR change notification infrastructure).

---

## Proactive Analytical Intelligence

> **What this achieves:** The platform monitors metric series produced by scheduled queries and surfaces anomalies, trend signals, and peer comparisons as unsolicited insight cards — without the user needing to submit a query. The platform tells users what has changed, not just what they ask.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Anomaly Detection Service** | Background service that monitors scheduled query results. For each metric series, maintains a configurable statistical baseline (rolling mean ± N standard deviations; configurable lookback window). Generates a proactive insight event when a metric value falls outside the baseline. Anomaly events are scoped to the role that owns the scheduled query — no cross-entitlement visibility. |
| **Trend Signal Detector** | Identifies metrics showing consistent directional movement across configurable consecutive periods (e.g. 3 periods up, configurable). Trend signals generated as insight events with the metric ID, direction, number of consistent periods, and the lineage reference to the underlying data. |
| **Proactive Insight Card Delivery** | Insight events delivered as structured cards to the consumer's registered notification endpoint (same delivery infrastructure as Automated Monitoring). Cards include: insight type (anomaly / trend), metric ID and label, the observed value vs. baseline, a narrative summary (Haiku-generated, anchored to the anomaly data), and the `result_id` for lineage inspection. |
| **Peer Comparison Signals** | Where the Benchmark Data Service or Regulatory Reference Service is registered, the anomaly service extends its baseline to include peer percentile comparisons. A metric that moves from the 3rd to 1st quartile of its peer group generates a peer comparison signal. |
| **Insight Configuration UI** | Application Admins configure per-metric anomaly detection settings: baseline window, sensitivity (N standard deviations), minimum signal strength (suppress noise below a configurable threshold), and opt-in/opt-out per user role. |

### Acceptance criteria

- Anomaly detection runs on the same schedule as the underlying scheduled query — no additional latency beyond delivery time
- Anomaly insight events respect the entitlement of the scheduled query owner — no data outside their projection scope
- False positive rate configurable — default sensitivity set so < 10% of signals are dismissed by users (monitored via insight card dismissal rate)
- Every insight card has a lineage reference — users can inspect the underlying data from any card

### Depends on

Automated Monitoring and Alerts (anomaly detection runs against scheduled query result series); statistical baseline storage (time-series extension to lineage store or dedicated metric series store).

---

## Collaborative Sessions

> **What this achieves:** Multiple authenticated users within the same tenant can share a live analytical session, each submitting queries governed by their own entitlements. The joint session can be exported as a PDF pack with all results, narratives, annotations, and lineage references attached.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Session Sharing Service** | Authenticated users within the same tenant can invite other authenticated users to an active analytical session by `sub` claim. Invitee receives a session join link valid for 24 hours. Both users can submit queries; all results are visible to all active session participants. Session has an owner (the inviting user); only the owner can close the session or revoke access. |
| **Per-Participant Governance Engine** | Each query submitted in a shared session is evaluated using the submitting participant's own entitlements — not the session owner's. Results from a query the invitee would not be entitled to run are not surfaced to participants who lack that entitlement. The governance engine tags each result with the submitting participant's `sub` and the entitlement projection applied. |
| **Annotation Layer** | Session participants can annotate any result card — chart, table, or narrative — with free-text comments. Annotations are visible to all current session participants. Annotations are stored in the session record and included in session exports. Annotations do not affect query execution or lineage records. |
| **Session Export Service** | Export a complete shared session as a structured PDF (all query cards, charts rendered via vite2img, narrative summaries, annotations) or as a ZIP archive (PDF + raw JSON result sets + lineage URLs). Export is flagged in the audit trail as a session export artefact. `requireLineageForExport: true` governance config applies — each exported result includes its `result_id` and lineage URL. |

### Acceptance criteria

- Participant entitlements are independently enforced — participant A cannot see a result that participant B produced if participant A would receive ENTITLEMENT_DENIED for the same query
- All shared session events (joins, queries, annotations, exports) logged under individual participant identities — not merged into a single session identity
- Session export includes a lineage reference for every result — no result appears in an exported PDF without a traceable `result_id`
- A result submitted by one participant appears for all participants within 2 seconds (p99)

### Depends on

Governed Analytical Core (lineage store, vite2img for PDF rendering); Automated Monitoring and Alerts (Push Delivery Service for session join notifications).

---

## Ecosystem Service Integrations

> **What this achieves:** The platform connects to three shared ecosystem services as registered execution backends — providing authoritative regulatory metric values, licensed market benchmark data, and a curated library of importable metric definitions. Tenants no longer need to license, ingest, or maintain this reference data independently.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Semantic Registry Service integration** | `POST /v1/smr/import` endpoint for importing pre-built metric definition packages from the Semantic Registry Service. Six financial services packages available: `fsi-wealth-v1`, `fsi-investment-v1`, `fsi-banking-v1`, `fsi-risk-v1`, `fsi-regulatory-v1`, `fsi-esg-v1`. Imported definitions are marked with `source: "semantic_registry_service"` and `source_version` in SMR metadata. Version update notifications when the registry publishes a new package version. All imported definitions enter the standard `proposed` → approval workflow. |
| **Regulatory Reference Service adapter** | Registration of the Regulatory Reference Service as a named execution backend in the Data Source Catalog (`dataAffinity: ["regulatory"]`). The FQP routes all sub-plans with `regulatory` data affinity to this backend first, ensuring regulatory metric values (LCR, NSFR, leverage ratio, capital ratios) are always sourced from the authoritative service. Threshold update notification handling: when the service publishes updated regulatory thresholds, the Application Admin is notified and can update tenant SMR display thresholds accordingly. Fallback to the next registered `regulatory` backend if the service is unavailable. |
| **Benchmark Data Service adapter** | Registration of the Benchmark Data Service as a named execution backend (`dataAffinity: ["benchmarks"]`). Provides licensed market index and benchmark data (MSCI World, Bloomberg Global Aggregate, S&P 500, and others) as a resolved data source for benchmark comparison queries. Custom benchmark blend registration via the Benchmark Data Service Admin API — blends registered by `id` and accessible in any query's `benchmark` dimension field. Per-tenant licensing check enforcement — tenants not licensed for a specific index receive a structured error, not silent data omission. |

### Acceptance criteria

- `POST /v1/smr/import` idempotent — re-importing the same package version produces no duplicate definitions and does not overwrite tenant customisations
- FQP routes `regulatory` data affinity sub-plans to the Regulatory Reference Service; falls back correctly when the service is unavailable with a structured partial-result warning
- Benchmark Data Service licensing check fires before any benchmark data is returned — unlicensed index access returns `BENCHMARK_NOT_LICENSED`, not empty data
- Every query result using Regulatory Reference Service or Benchmark Data Service data includes those backends in the `meta.backendsUsed` field and lineage record

### Depends on

Governed Analytical Core (Data Source Catalog, FQP backend adapter layer, `POST /v1/smr/import` Admin API endpoint).

---

## Regulatory Compliance Modes

> **What this achieves:** The governance layer is extended with three named compliance profiles — MiFID II, Basel III/IV, and SEC Regulation BI — that automatically apply regime-specific rules, additional audit records, and query-time constraints without requiring manual configuration per query. A compliance analyst querying LCR under Basel III mode gets a regulatory snapshot record written automatically; a compliance officer under MiFID II is prompted for a business justification before any query touching client-identifiable data proceeds.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Compliance Mode Framework** | `complianceMode` tenant configuration field accepting `"mifid2"`, `"basel3"`, or `"sec_reg_bi"`. Compliance mode is evaluated as step 5 of the governance pipeline — after classification gate, before concurrency check. Compliance mode configuration changes take effect on the next query; no caching of pre-compliance query plans. Multiple modes may be enabled simultaneously for multi-jurisdictional deployments. |
| **MiFID II compliance mode** | Business justification prompt: queries touching `client_name`, `account_number`, or other PII-adjacent dimensions surface a mandatory justification step before execution. Best execution validation: queries on best-execution metrics require an explicit `date` dimension — rejected with a structured validation error if absent. Transaction reporting trace: all queries involving client-related metrics produce an additional lineage record written to the `analytics.mifid2_trace` table for regulatory reporting. |
| **Basel III/IV compliance mode** | Entity dimension requirement: all regulatory capital metric queries (LCR, NSFR, leverage ratio, capital ratio) require the `entity` dimension — rejected with a structured error if absent. Regulatory snapshot writes: LCR and NSFR queries trigger an automatic snapshot write to the `analytics.regulatory_snapshots` table. Stress scenario classification enforcement: stress scenario metrics are automatically classified at `RESTRICTED` regardless of their SMR classification setting, ensuring they cannot be returned to roles without RESTRICTED access. |
| **SEC Regulation BI compliance mode** | Narrative synthesis constraint: an additional prompt-level instruction is injected into the NSE prohibiting investment recommendations in narrative output — even when result values might suggest one. Post-generation validation rejects narratives containing recommendation language and triggers regeneration. Suitability record requirement: advisory queries require a `suitability_record_id` parameter; queries without it are blocked with a structured error before execution. |
| **Compliance mode audit trail** | `analytics.mifid2_trace` table: per-query record for MiFID II transaction reporting queries (query ID, user, entity, timestamp, business justification text, result ID). `analytics.regulatory_snapshots` table: per-query daily snapshot for Basel III/IV regulatory metric queries (entity ID, metric ID, value, regulatory minimum, compliance status, as-of date). Both tables are append-only and retained per the tenant's compliance mode retention policy. |

### Acceptance criteria

- Enabling `complianceMode: "mifid2"` causes every query on a PII-adjacent dimension to require a business justification — no bypass path
- A Basel III LCR query without the `entity` dimension returns a structured `REQUIRED_DIMENSION_MISSING` error — no partial execution
- `analytics.mifid2_trace` and `analytics.regulatory_snapshots` records are written atomically with the query lineage record — a query result with no compliance trace record is a platform defect
- SEC Reg BI narrative synthesis constraint is enforced via post-generation validation — narratives containing investment recommendation language are rejected and regenerated
- A SEC Reg BI advisory query without a `suitability_record_id` parameter is blocked with a structured error before any execution begins

### Depends on

Governed Analytical Core (Semantic Execution Governance pipeline, Analytical Lineage Store); Ecosystem Service Integrations (Regulatory Reference Service providing authoritative regulatory metric values for snapshot records).

---

## Cross-Backend Drilldown

> **What this achieves:** Drilldown traversal is no longer constrained to a single execution backend per hierarchy level. An analyst can drill from a warehouse-sourced view directly into a graph database or API-backed relationship model in one continuous navigation — the backend boundary is transparent.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **FQP Cross-Backend Affinity Resolver** | Enhancement to the Federated Query Planner. When a drilldown traversal crosses a `dataAffinity` boundary (e.g. from `positions` domain served by SQL warehouse to `entity_relationships` domain served by Graph API), the FQP identifies the boundary point in the hierarchy and routes the child-level sub-plan to the appropriate backend. The parent result's projection scope and governance context are passed to the child sub-plan. |
| **Drilldown Result Merger** | Enhancement to FQP result assembly. When a drilldown produces sub-results from two different backends, the FQP uses shared dimension keys (e.g. `issuer_id`) to join child rows back to parent rows. The merged result is assembled into a single SCL display spec — the consumer sees a coherent drilldown result, not a split across two responses. |
| **Cross-Backend Drilldown Lineage** | Lineage record extended to capture the affinity boundary crossing: which backend served the parent level, which backend served the child level, and the dimension key used to join them. |

### Acceptance criteria

- Drilldown traversal that crosses a backend boundary completes within 500ms additional latency vs. same-backend drilldown (p95)
- Merged drilldown result is a single SCL display spec — consumer does not need to handle multi-part responses
- If the child-level backend is unavailable, the drilldown returns a structured error — not a partial result with a silent gap
- Lineage record for cross-backend drilldown is complete — both backends' sub-plans and raw responses captured

### Depends on

Governed Analytical Core (FQP with Graph Data API adapter registered); at least one deployment with both SQL warehouse and Graph API backends registered for the same analytical domain hierarchy.

---

## Advanced Query Capabilities

> **What this achieves:** Ranking, window analytics, scenario comparison, and inline benchmark composition are expressible as a single query — rather than requiring the consumer to compose and join multiple separate queries. The parameter model of the Analytical Intent Validator is extended to cover these patterns natively.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **Ranking and Percentile Query Parameters** | `rank_by` parameter: rank result rows by any metric in the result set. `rank_direction`: `ASC` or `DESC`. `rank_limit`: return only the top/bottom N rows. `rank_percentile`: return rows above/below a percentile threshold. Rankings computed across the full assembled result set — not within each backend's sub-result. |
| **Window Analytics Parameters** | `window_op` parameter: `moving_average`, `rolling_sum`, `period_over_period`. `window_size`: number of periods. `window_anchor`: `trailing` or `centred`. Window operations computed at FQP result assembly — not delegated to backends that may not support them. |
| **Scenario Comparison Parameter** | `scenario` parameter: compare actual metric values against a registered scenario definition (stress test, budget, or forecast registered in the SMR). Scenario definitions are registered by Application Admins in the SMR. A scenario comparison query returns actual values, scenario values, and the delta as a single result set. |
| **Inline Composite Benchmark** | `benchmark` dimension field accepts either a pre-registered Benchmark Data Service ID or an inline composition object (`[{ "benchmark_id": "b_msci_world", "weight": 0.60 }, ...]`). Inline compositions are resolved at query time — no pre-registration required. Inline compositions are logged in the lineage record. |

### Acceptance criteria

- `rank_by` + `rank_limit` applied correctly in federated results — rankings computed across the full assembled result set
- Window operations produce the same result as an equivalent backend-level window function for backends that support it — verified in integration tests
- Scenario comparison results include both actual and scenario values in the same result set — no consumer-side join required
- Inline benchmark compositions are logged in the lineage record — auditors can reconstruct the exact composition used in any query

### Depends on

Governed Analytical Core (Analytical Intent Validator parameter model extensibility, FQP result assembly layer for window computation); Ecosystem Service Integrations (Benchmark Data Service registered for composite benchmark resolution).

---

## Open API Surface

> **What this achieves:** The platform's internal surfaces — the SMR, the lineage store, and the analytical query interface — are accessible via purpose-built REST and GraphQL APIs. Consumers can build metric discovery tools, regulatory audit dashboards, and BI integrations directly against the platform's data without going through the MCP interface or Admin Console.

### Shippable components

| Component | Functionality |
|-----------|--------------|
| **SMR Browser REST API** | `GET /v1/smr/metrics` — paginated list of active metric definitions. `GET /v1/smr/metrics/{id}` — full metric definition including formula, aggregation rule, dimension list, data domain, owner, and version history. `GET /v1/smr/dimensions` — dimension catalogue. `GET /v1/smr/hierarchies` — drilldown hierarchy definitions. All endpoints authenticated by JWT; results scoped to the user's entitled metric visibility. |
| **NDJSON Result Streaming** | The MCP Capability Layer and FQP support streaming delivery of assembled sub-plan results in NDJSON format. Consumers receive individual backend sub-results as they arrive rather than waiting for full assembly. First sub-result delivered within 200ms of FQP execution start (p95). Streaming responses include a terminal frame with the complete assembled result, SCL display spec, and lineage URL. Compatible with existing non-streaming consumers. |
| **Streaming Progress Events** | Four structured progress events emitted during FQP execution and delivered to streaming consumers: `intent_resolved` (Semantic Intent Layer has produced validated tool call parameters), `entitlements_applied` (Role-Aware Projection Layer has produced the row predicate and column mask set), `plan_compiled` (Analytical Intent Validator has produced the LQP), `executing` (FQP has dispatched sub-plans to backends). Events enable consumers to render progressive UI states (e.g. "Applying entitlements…", "Querying risk engine…") rather than displaying a static spinner. |
| **FQP Adaptive Planning** | The FQP tracks observed p50 and p95 execution latency per registered backend (stored in PostgreSQL). When a backend's observed latency degrades beyond its baseline by a configurable multiplier, the adaptive planner automatically routes the next query to the next registered backend with matching `dataAffinity`. Cost estimate calibration: observed execution costs are used to refine the governance layer's cost unit estimates, improving circuit breaker accuracy over time. |
| **Materialised View Registration** | Application Admins register pre-computed result templates via the Admin API — named queries whose results are pre-computed on a cron schedule and stored as cached result sets. When a query matches a registered materialised view (same metric IDs, dimensions, and time expression), the governance cost estimate applies a `-800 unit` offset (as per the cost model in the governance spec). Used for high-frequency analytical queries (e.g. nightly NAV calculations, daily regulatory ratio snapshots) where result freshness within the refresh cadence is acceptable. |
| **GraphQL API Gateway** | Optional GraphQL schema layer over the MCP endpoint. Exposes `analyseMetric`, `comparePortfolios`, `listMetrics`, `getMetricDefinition`, and `drilldown` as GraphQL queries with typed input and output schemas. JWT auth via HTTP header. GraphQL layer is a passthrough — all requests route through the same governance pipeline; no governance bypass. |
| **Lineage Query REST API** | `GET /v1/lineage/{result_id}` — retrieve full lineage record. `POST /v1/lineage/search` — search by `user_sub`, `metric_id`, `time_range`, `backend_id`, or `governance_decision`. `GET /v1/lineage/{result_id}/sub-plans` — retrieve per-backend sub-plans and raw responses. Paginated; JWT-scoped to the querying user's own records (Platform Admins can query tenant-wide). |

### Acceptance criteria

- SMR Browser API results are consistent with the Admin Console SMR view — same data, same entitlement scoping
- Streaming first-frame latency ≤ 200ms (p95) for NDJSON result streaming — measurably faster than full assembly for multi-backend queries
- All four progress events emitted in correct order for every streaming query — no query completes without emitting `executing` before the first result frame
- Adaptive planner latency tracking is transparent to consumers — routing changes are logged in the lineage record's `meta.backendsUsed` field but require no consumer changes
- Materialised view matches reduce governance cost estimate by 800 units — verified against the cost model
- GraphQL responses are semantically equivalent to MCP responses — the API layer adds no data transformation
- Lineage query API search latency ≤ 500ms for queries over the full 7-year retention window (p95)

### Depends on

Governed Analytical Core (lineage store with indexed search, SMR service read API, FQP result assembly refactored to support incremental streaming); Automated Monitoring and Alerts (Scheduled Query Service provides the execution infrastructure for materialised view refresh).

---

## Not in roadmap

| Item | Rationale |
|------|-----------|
| **Raw SQL passthrough** | Architecturally prohibited. Violates P1 (semantic abstraction over physical exposure) and P10 (deterministic computation, not generation). Not planned at any phase. |
| **Physical schema exposure to AI model** | Architecturally prohibited. Violates P1. The Semantic Intent Layer receives SMR metric and dimension names — no table names, column names, or JOIN paths. Not planned. |
| **Ad hoc LLM-generated SQL** | Architecturally prohibited. Violates P2 (governance before execution) and P10. All queries are expressed as validated MCP tool call parameters resolved against the SMR. Not planned. |
| **Unauthenticated analytical access** | Violates P2 and P5 (role-aware by default). JWT validation at the edge is non-negotiable. Not planned. |
| **LLM chart type selection outside Visualisation Ontology** | Violates P7 (deterministic visualisation). Chart selection is always governed by registered chart contracts. LLM intent signals are inputs to the ontology — not direct rendering instructions. Not planned. |
| **Cross-tenant result federation** | Tenant boundary is a non-configurable isolation guarantee (A9). Not planned. |
| **Metric value generation by AI model** | Violates P10. Every number in a result is computed from a registered definition applied to data from a registered backend. The Narrative Synthesis Engine produces prose descriptions of these computed values — not the values themselves. Not planned. |

---

*This is a proposed delivery sequence, not a committed plan. For the product specification, see [README.md](./README.md) and the numbered chapter documents. For the proposed reference implementation stack, see [05-technical-implementation.md](./05-technical-implementation.md).*
