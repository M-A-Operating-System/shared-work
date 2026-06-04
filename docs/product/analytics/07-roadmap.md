# AI Analytics Platform — Proposed Roadmap

This document describes one proposed sequence of deliverables for the AI Analytics Platform. It is not the only valid sequence and is not a committed delivery plan. Phase boundaries should be revisited as implementation proceeds, customer feedback is gathered, and technical constraints become clearer. Decisions to resequence or regroup phases should be recorded here; they do not require changes to the product specification.

---

<table>
<thead>
<tr>
<th>#</th>
<th>Phase</th>
<th>Component</th>
<th>Build</th>
<th>Business Outcome</th>
</tr>
</thead>
<tbody>

<!-- ── Phase 1 ── -->
<tr>
<td rowspan="14">1</td>
<td rowspan="14"><strong>Governed Analytical Core</strong></td>
<td>Platform Admin API</td>
<td>Create new authenticated REST service; implement CRUD endpoints for the Data Source Catalog, SMR metric definitions, and role entitlement records; add tenant governance settings endpoints for circuit breaker thresholds and feature flags; secure all routes with JWT middleware</td>
<td rowspan="14">Any MCP-compatible consumer — AI assistant, application, or autonomous agent — can query a registered metric and receive a governed, reproducible result with a chart, a narrative, and an audit-grade lineage record, scoped to exactly the user's entitlements</td>
</tr>
<tr>
<td>Admin Console</td>
<td>Create new React web application over the Platform Admin API; build metric definition editor with YAML preview, entitlement policy builder with role-to-metric mapping UI, Data Source Catalog manager, and governance threshold controls</td>
</tr>
<tr>
<td>Semantic Metrics Repository (SMR)</td>
<td>Extend the pre-existing Semantic Data Context Store (DCS) with three new document types — <code>analytical_metric</code>, <code>analytical_dimension</code>, and <code>analytical_operation</code>; status field (<code>proposed → in_review → approved → deprecated → retired</code>) on each document drives the DCS native approval workflow with one approved version enforced per <code>(tenant_id, id)</code>; reuse the DCS native search index for <code>list_operations</code> queries — no separate search infrastructure required; expose document authoring and approval via the Platform Admin API</td>
</tr>
<tr>
<td>Financial Services Reference Model</td>
<td>Author seed YAML definitions for six analytical domains (<code>portfolio</code>, <code>performance</code>, <code>risk</code>, <code>regulatory</code>, <code>counterparty</code>, <code>benchmarks</code>) including pre-built metrics for AUM, portfolio return, tracking error, VaR, LCR, and NSFR; implement a <code>POST /v1/smr/seed</code> endpoint that imports a domain profile into the SMR in <code>proposed</code> state; add domain profile selection to the tenant setup flow</td>
</tr>
<tr>
<td>MCP Capability Layer</td>
<td>Build new Python service using FastMCP + Uvicorn (ASGI); deploy as a Kubernetes pod; implement JWT validation middleware at request ingress rejecting unauthenticated requests before any platform processing; implement three <code>@mcp.tool()</code> handlers (<code>run_analytics</code>, <code>list_operations</code>, <code>drilldown</code>) routing through the shared pipeline (<code>validate_jwt → sil.resolve → rapl.project → seg.approve → fqp.execute → assemble_response</code>); implement MCP resource handlers serving knowledge artifacts from the Knowledge Store (<code>guide://</code> and <code>skills://</code> URIs — no JWT required, no governance pipeline); implement two <code>@mcp.prompt()</code> templates (standard analytical assistant, regulatory reporting assistant); build per-user capability manifest endpoint reflecting feature-flag state and entitlement-gated tool availability</td>
</tr>
<tr>
<td>Semantic Intent Layer</td>
<td>Build new service implementing JSON schema validation for all MCP tool call parameters; implement SMR ID resolver that calls the SMR service to validate metric and dimension references, returning structured <code>METRIC_NOT_FOUND</code> errors for unregistered IDs; build LQP generator producing a platform-agnostic execution DAG from validated parameters; no LLM invocation in this layer</td>
</tr>
<tr>
<td>Role-Aware Projection Layer</td>
<td>Build new service implementing JWT claim extraction (<code>roles</code>, <code>managed_portfolios</code>, <code>entity_ids</code>); implement role definition template store in PostgreSQL; build row predicate injector that materialises WHERE clause conditions from role templates and attaches them to the LQP before FQE dispatch; implement column mask registry and apply masks at result assembly; enforce <code>defaultDenyAll: true</code> — return <code>ENTITLEMENT_DENIED</code> for any user with no matching role before any query executes</td>
</tr>
<tr>
<td>Semantic Execution Governance</td>
<td>Build new governance pipeline service with five sequential steps: (1) cost estimation against a configurable cost unit model, (2) classification gate checking the LQP's metric data sensitivity levels against the requesting role's clearance, (3) circuit breaker checks for query complexity score, per-tenant cost budget, and per-user rate limit, (4) governance decision record written to the lineage store before any backend call, (5) pass-through or structured rejection with decision reason; read per-tenant governance config from a <code>governance_config</code> document in the DCS at startup and refresh on DCS change events — config is not stored in a separate database table; all decisions logged with microsecond timestamps</td>
</tr>
<tr>
<td>Federated Query Engine (FQE)</td>
<td>Integrate Apache Calcite as the SQL sub-plan optimiser; implement pluggable backend adapter interface; build SQL warehouse adapter with connection pooling for Snowflake, BigQuery, Databricks, Redshift, Trino, and PostgreSQL; build semantic layer adapter for dbt MetricFlow and Cube.js; build OpenData REST/OData adapter; implement in-process result fan-out, sub-plan execution, and assembly; add per-tenant result cache keyed on SHA-256 of the LQP with TTL configurable per metric refresh cadence</td>
</tr>
<tr>
<td>Visualisation Ontology</td>
<td>Define eight named chart contracts in a versioned contract registry (multi-series bar, time-series line, heatmap, treemap, scatter, waterfall, stacked bar, ranked bar); implement deterministic chart selector that maps result schema shape and intent pattern to a contract — no LLM invocation; implement DVL display spec generator producing Vega-Lite v5 JSON conforming to the selected contract; add <code>type: "table"</code> extension for tabular results</td>
</tr>
<tr>
<td>Narrative Synthesis Engine</td>
<td>Build new service implementing two prompt templates (standard: Claude Haiku for ≤5 metrics / ≤3 dimensions; complex: Claude Sonnet for attribution, multi-portfolio, and regulatory queries); construct prompt exclusively from the assembled result set — no user query text, no physical schema; implement post-generation numeric leakage validator that rejects any value in the narrative not present in the result set; implement single regeneration attempt on validation failure before returning an error</td>
</tr>
<tr>
<td>Analytical Lineage Store</td>
<td>Provision S3-compatible object store bucket with date-partitioned key structure (<code>lineage/{tenant_id}/{yyyy}/{mm}/{dd}/{result_id}.json</code>); implement write-once JSON document serialiser covering the full query record (request payload, resolved metric versions, governance decision, sub-plans, assembled result, DVL display spec, compliance metadata); implement write path called by the Semantic Execution Governance service before any backend execution and by the FQE on completion; create lightweight <code>analytics.lineage_index</code> PostgreSQL table (scalar fields only — no JSON payloads) for future search queries; configure object lifecycle policy for 7-year default retention; post-hoc compliance annotations written as sibling amendment documents, never mutating the original record</td>
</tr>
<tr>
<td>vega2img Rendering Service</td>
<td>Build as a standalone MCP server (not part of the Analytics Platform); implement Vite + vega-embed + headless Chromium via Playwright; expose DVL spec rendering (Vega-Lite v5 → SVG or PNG) and <code>type: "table"</code> rendering via styled HTML template as MCP tools; consumers (AI Chat Platform, agentic consumers) register vega2img as a peer MCP server alongside the Analytics Platform — the Analytics Platform does not call vega2img directly</td>
</tr>
<tr>
<td>Knowledge Store</td>
<td>Provision S3-compatible object store with versioned Markdown artifact storage; author and bundle default content at installation: platform overview guide, analytical domain reference (six domains), query pattern examples, skills definitions for portfolio performance review, risk analysis, and regulatory reporting, and compliance guides for MiFID II and Basel III/IV; implement versioned read path consumed by MCP resource handlers (URI-to-path mapping: <code>guide://analytics/platform-overview</code> → <code>guide/analytics/platform-overview.md</code>); add knowledge artifact CRUD endpoints to the Platform Admin API so tenant administrators can add, update, or override content without modifying platform defaults</td>
</tr>

<!-- ── Phase 2 ── -->
<tr>
<td rowspan="4">2</td>
<td rowspan="4"><strong>Automated Monitoring and Alerts</strong></td>
<td>Scheduled Query Service</td>
<td>Create <code>scheduled_queries</code> table in PostgreSQL storing cron expression, owner <code>sub</code>, and validated MCP tool call parameters; implement Kubernetes CronJob controller that reads pending schedules and dispatches them through the full governance pipeline using the stored owner JWT claims at runtime; write results to the Analytical Lineage Store and result artefact store on completion</td>
<td rowspan="4">Risk officers and portfolio managers receive automated push notifications when a metric breaches its defined threshold — no manual query required; every alert payload carries a lineage reference to the underlying computation</td>
</tr>
<tr>
<td>Alert Threshold Engine</td>
<td>Create <code>alert_thresholds</code> table in PostgreSQL linked to scheduled queries; implement threshold evaluator service that iterates each result row after FQE assembly and evaluates up to ten conditions per query using <code>gt</code>, <code>lt</code>, <code>gte</code>, <code>lte</code>, <code>eq</code>, <code>pct_change_gt</code> operators; write a breach event record to the lineage store for each triggered condition and enqueue a delivery job</td>
</tr>
<tr>
<td>Push Delivery Service</td>
<td>Create <code>delivery_endpoints</code> table and delivery job queue; implement three delivery adapters — HTTPS webhook (POST with HMAC signature), SMTP email, and Slack via Slack MCP server; build delivery payload serialiser including <code>result_id</code>, threshold description, DVL display spec, and lineage URL; implement exponential-backoff retry with max attempts configurable per endpoint; log undeliverable events to the audit trail</td>
</tr>
<tr>
<td>Scheduled Query Admin UI</td>
<td>Add new Admin Console section; build schedule management CRUD UI over the Scheduled Query Service API; build threshold configuration form supporting up to ten conditions per schedule; build delivery endpoint manager; add execution history view with per-run status and lineage links; add alert audit log view</td>
</tr>

<!-- ── Phase 3 ── -->
<tr>
<td rowspan="3">3</td>
<td rowspan="3"><strong>SMR Authoring Assistance</strong></td>
<td>Natural Language → Metric Draft Generator</td>
<td>Add <code>POST /v1/smr/draft</code> endpoint to the Platform Admin API accepting a prose description; implement Claude Sonnet prompt that generates a structured SMR YAML draft (<code>id</code>, <code>label</code>, <code>formula</code>, <code>aggregation</code>, <code>dimensions</code>, <code>data.domain</code>, <code>units</code>, <code>description</code>) with output validated against the SMR JSON schema before being returned; write the validated draft to the SMR in <code>proposed</code> state; block activation until Application Admin approval is recorded</td>
<td rowspan="3">Metric owners propose new definitions in plain English without writing YAML; the platform detects duplicates and structural conflicts automatically before a draft enters the approval workflow</td>
</tr>
<tr>
<td>SMR Consistency Checker</td>
<td>Build consistency check service invoked automatically on every new draft before it is surfaced for review; implement cosine-similarity comparison of the concatenated draft <code>formula</code> and <code>description</code> fields against the same fields of all active metric definitions, using the same embedding model configured for platform semantic search; flag matches above a 0.85 similarity threshold (initial value — to be calibrated against a test set of known-duplicate and known-distinct metrics during Phase 3 development); implement naming conflict check against existing <code>id</code> and <code>label</code> fields; implement dimension existence check against the registered dimension catalogue; implement data domain check against the Data Source Catalog; attach findings to the draft record as structured annotations</td>
</tr>
<tr>
<td>Metric Draft Review UI</td>
<td>Add new Admin Console draft review screen; build side-by-side layout rendering original prose alongside generated YAML with inline field editing; surface consistency checker findings as in-context warning panels with resolution suggestions; implement one-click submission to the existing <code>proposed → under_review</code> state transition; persist edit history as append-only records on the draft</td>
</tr>

<!-- ── Phase 4 ── -->
<tr>
<td rowspan="5">4</td>
<td rowspan="5"><strong>Cross-Session Memory</strong></td>
<td>User Preference Store</td>
<td>Create <code>user_preferences</code> table in PostgreSQL scoped by <code>tenant_id + sub</code>; extend the Semantic Intent Layer to read preference defaults (default time period, dimensions, chart type overrides, measure groups) and apply them as parameter defaults at intent resolution, overridable per individual query; expose preference CRUD via the Platform Admin API</td>
<td rowspan="5">Returning users find their analytical context pre-applied; saved queries surface SMR changes as explicit staleness warnings before execution rather than producing silently incorrect results</td>
</tr>
<tr>
<td>Saved Query Registry</td>
<td>Create <code>saved_queries</code> table in PostgreSQL storing validated MCP tool call parameters (not natural language); implement version reference columns linking each saved query to the SMR metric and dimension version IDs used at save time; add <code>needs_review</code> flag set by the SMR change event handler; implement tenant-wide promotion flag controlled by Application Admin role; expose saved query CRUD via the Platform Admin API</td>
</tr>
<tr>
<td>Favourite Metrics Index</td>
<td>Create <code>user_favourites</code> table in PostgreSQL scoped by <code>tenant_id + sub</code>; extend the <code>list_operations</code> response to sort favourited metric IDs to the top of results; extend the Semantic Intent Layer disambiguation logic to prefer favourited metrics in tie-breaking; extend the SMR browser to visually distinguish favourited metrics</td>
</tr>
<tr>
<td>My Workspace UI</td>
<td>Add new My Workspace section to the consuming UI and expose it via the Platform Admin API; build preference editor form; build saved query list view with staleness indicator (highlighted when <code>needs_review</code> is set) and acknowledgement flow before re-execution; build favourites management panel</td>
</tr>
<tr>
<td>SMR Service</td>
<td>Extend the existing SMR service to publish a <code>definition_changed</code> event to the message queue whenever a metric or dimension definition transitions to <code>approved</code> or <code>deprecated</code>; implement a consumer in the Saved Query Registry that receives these events and sets <code>needs_review = true</code> on all saved queries referencing the changed definition</td>
</tr>

<!-- ── Phase 5 ── -->
<tr>
<td rowspan="4">5</td>
<td rowspan="4"><strong>Proactive Analytical Intelligence</strong></td>
<td>Anomaly Detection Service</td>
<td>Create new background service that reads completed scheduled query results from the Analytical Lineage Store; maintain a rolling statistical baseline (configurable mean ± N standard deviations and lookback window) per metric series in a time-series extension table; generate a structured insight event record when a new result value falls outside the baseline; when Benchmark Data Service or Regulatory Reference Service backends are registered, extend the baseline computation to include peer percentile comparisons using data from those backends</td>
<td rowspan="4">The platform surfaces anomalies and trend signals without users submitting queries; portfolio managers and risk officers find scoped, lineage-referenced insight cards traceable to the scheduled query result that produced the signal</td>
</tr>
<tr>
<td>Trend Signal Detector</td>
<td>Add trend detection module to the Anomaly Detection Service; implement directional consistency check across configurable N consecutive periods per metric series; generate a structured trend insight event record with metric ID, direction, period count, and lineage reference to the underlying result series when the condition is met</td>
</tr>
<tr>
<td>Insight Configuration UI</td>
<td>Add new Admin Console section for per-metric anomaly detection configuration; build form for baseline window size, sensitivity (N standard deviations), minimum signal strength threshold (to suppress low-significance noise), and role-level opt-in/opt-out toggles; persist configuration to a new <code>anomaly_config</code> table in PostgreSQL</td>
</tr>
<tr>
<td>Push Delivery Service</td>
<td>Extend existing Push Delivery Service (Phase 2) to handle a new <code>insight_card</code> delivery job type; implement insight card payload serialiser including insight category (anomaly / trend / peer comparison), metric ID and label, observed value vs. baseline, Haiku-generated narrative anchored to the anomaly data, and <code>result_id</code> for lineage inspection; reuse existing delivery adapters and retry infrastructure</td>
</tr>

<!-- ── Phase 6 ── -->
<tr>
<td rowspan="4">6</td>
<td rowspan="4"><strong>Collaborative Sessions</strong></td>
<td>Session Sharing Service</td>
<td>Create <code>shared_sessions</code> and <code>session_participants</code> tables in PostgreSQL; implement session creation, participant invitation (by <code>sub</code> claim with 24-hour signed join tokens), and owner-controlled access revocation; build session event log capturing all joins, queries, annotations, and exports under individual participant identities; expose session management via the Platform Admin API</td>
<td rowspan="4">Portfolio managers and risk officers co-explore data in a shared governed session — each participant's results governed by their own entitlements — and export a lineage-referenced PDF pack for investment committee or regulatory review</td>
</tr>
<tr>
<td>Per-Participant Governance Engine</td>
<td>Extend the governance pipeline to accept a participant context identifier on each query submitted within a shared session; route each query through the full Role-Aware Projection Layer using the submitting participant's own JWT claims — not the session owner's; tag each result record with the participant's <code>sub</code> and the projection applied; implement a result visibility filter that withholds results from participants who would receive <code>ENTITLEMENT_DENIED</code> for the same query</td>
</tr>
<tr>
<td>Annotation Layer</td>
<td>Create <code>session_annotations</code> table in PostgreSQL linked to session and result card IDs; implement annotation CRUD API scoped to active session participants; extend the session event log to record annotation events under the annotating participant's identity; include annotations in session export payloads</td>
</tr>
<tr>
<td>Session Export Service</td>
<td>Create new export service that assembles a complete session into a structured PDF using vega2img for chart rendering and a Pandoc-based document pipeline for layout; implement ZIP export producing PDF + per-result JSON + lineage URL manifest; enforce that every exported result includes its <code>result_id</code> and lineage URL; write an export artefact record to the audit trail</td>
</tr>

<!-- ── Phase 7 ── -->
<tr>
<td rowspan="3">7</td>
<td rowspan="3"><strong>Ecosystem Service Integrations</strong></td>
<td>Admin API — SMR Import Endpoint</td>
<td>Add <code>POST /v1/smr/import</code> endpoint to the Platform Admin API; implement package download and schema-validation pipeline for six financial services metric packages from the Semantic Registry Service; write imported definitions to the SMR in <code>proposed</code> state with <code>source</code> and <code>source_version</code> metadata columns; implement idempotency check — re-importing the same package version produces no duplicate definitions and does not overwrite tenant customisations; add package version update notification handler</td>
<td rowspan="3">Regulatory metric values are sourced from the authoritative service; benchmark queries resolve against licensed index data without internal data ingestion, licensing management, or refresh pipelines owned by the tenant</td>
</tr>
<tr>
<td>Regulatory Reference Service Adapter</td>
<td>Implement new FQE backend adapter registering the Regulatory Reference Service with <code>dataAffinity: ["regulatory"]</code>; extend the FQE backend selector to route all sub-plans with <code>regulatory</code> affinity to this adapter first; implement automatic fallback to the next registered <code>regulatory</code> backend with a structured partial-result warning when the service is unavailable; implement threshold update notification handler that triggers an Admin Console alert when the service publishes new regulatory thresholds</td>
</tr>
<tr>
<td>Benchmark Data Service Adapter</td>
<td>Implement new FQE backend adapter registering the Benchmark Data Service with <code>dataAffinity: ["benchmarks"]</code>; add per-tenant licensing record table in PostgreSQL; implement licensing check in the adapter before any index data is returned, returning <code>BENCHMARK_NOT_LICENSED</code> for unlicensed indices; implement custom benchmark blend registration via the Benchmark Data Service Admin API, storing blend IDs accessible through the <code>benchmark</code> dimension field</td>
</tr>

<!-- ── Phase 8 ── -->
<tr>
<td rowspan="4">8</td>
<td rowspan="4"><strong>Regulatory Compliance Modes</strong></td>
<td>Compliance Mode Framework</td>
<td>Extend the Semantic Execution Governance service to add a new pipeline step 5 evaluating the tenant's <code>complianceMode</code> configuration field; implement a compliance mode dispatcher that routes to the appropriate mode handler(s); support concurrent activation of multiple modes; invalidate any cached governance plan on <code>complianceMode</code> configuration change so the new rules apply immediately to the next query</td>
<td rowspan="4">Regulated queries automatically write regime-specific compliance audit records and enforce query-time constraints without per-query manual configuration; the governance pipeline is the enforcement point</td>
</tr>
<tr>
<td>MiFID II Compliance Mode</td>
<td>Implement MiFID II handler in the Compliance Mode Framework; add PII-adjacent dimension registry (configurable list including <code>client_name</code>, <code>account_number</code>); block queries touching PII-adjacent dimensions pending a user-supplied business justification string; enforce presence of <code>date</code> dimension on best-execution metric queries; create append-only <code>analytics.mifid2_trace</code> table and write a record (query ID, user, entity, timestamp, justification text, result ID) for every qualifying query</td>
</tr>
<tr>
<td>Basel III/IV Compliance Mode</td>
<td>Implement Basel III/IV handler in the Compliance Mode Framework; enforce presence of the <code>entity</code> dimension on all regulatory capital metric queries (LCR, NSFR, leverage ratio, capital ratio) returning <code>REQUIRED_DIMENSION_MISSING</code> if absent; create append-only <code>analytics.regulatory_snapshots</code> table and write a snapshot record (entity ID, metric ID, value, regulatory minimum, compliance status, as-of date) for every LCR and NSFR query; override the SMR classification of all stress scenario metrics to <code>RESTRICTED</code> at the governance layer regardless of their registered classification</td>
</tr>
<tr>
<td>SEC Regulation BI Compliance Mode</td>
<td>Implement SEC Reg BI handler in the Compliance Mode Framework; inject an additional system-level instruction into the Narrative Synthesis Engine prompt prohibiting investment recommendation language; extend the NSE post-generation validator to detect recommendation language patterns and trigger a single regeneration attempt; add <code>suitability_record_id</code> as a required parameter for advisory queries in the Semantic Intent Layer schema, blocking execution with a structured error if absent</td>
</tr>

<!-- ── Phase 9 ── -->
<tr>
<td rowspan="3">9</td>
<td rowspan="3"><strong>Cross-Backend Drilldown</strong></td>
<td>Cross-Backend Affinity Resolver</td>
<td>Extend the FQE to inspect the <code>dataAffinity</code> of each hierarchy level in a drilldown traversal; implement boundary detection logic that identifies the point at which the traversal crosses from one affinity domain to another; route child-level sub-plans to the backend registered for the child domain, carrying forward the parent result's governance context, projection scope, and row predicates to the child sub-plan dispatcher</td>
<td rowspan="3">Analysts drill from a warehouse-sourced aggregate into graph-backed entity relationships in one continuous navigation; the backend boundary is transparent to the consumer and the full cross-backend traversal is captured in a single lineage record</td>
</tr>
<tr>
<td>Drilldown Result Merger</td>
<td>Extend the FQE result assembly layer to handle multi-backend drilldown results; implement a dimension-key join that matches child rows from the secondary backend back to parent rows using shared dimension keys (e.g. <code>issuer_id</code>); produce a single unified DVL display spec from the merged result; return a structured <code>CHILD_BACKEND_UNAVAILABLE</code> error rather than a partial result with a silent gap if the child-level backend cannot be reached</td>
</tr>
<tr>
<td>Cross-Backend Drilldown Lineage</td>
<td>Extend the <code>lineage_records</code> table schema to add columns for affinity boundary crossing: parent backend ID, child backend ID, dimension key used for the join; extend the lineage record writer to capture both backends' sub-plans and raw responses in the existing JSONB sub-plans column</td>
</tr>

<!-- ── Phase 10 ── -->
<tr>
<td rowspan="4">10</td>
<td rowspan="4"><strong>Advanced Query Capabilities</strong></td>
<td>Ranking and Percentile Parameters</td>
<td>Extend the Semantic Intent Layer JSON schema to add <code>rank_by</code>, <code>rank_direction</code>, <code>rank_limit</code>, and <code>rank_percentile</code> parameters; extend the FQE result assembly layer to apply ranking after all backend sub-results are assembled into the full result set, ensuring cross-backend results are ranked as a unified dataset rather than per-backend</td>
<td rowspan="4">Complex analytical queries — ranking, rolling windows, stress scenario comparisons, and composite benchmarks — are expressible as a single governed call; consumers receive a complete, join-ready result set without requiring multi-call composition</td>
</tr>
<tr>
<td>Window Analytics Parameters</td>
<td>Extend the Semantic Intent Layer JSON schema to add <code>window_op</code> (<code>moving_average</code>, <code>rolling_sum</code>, <code>period_over_period</code>), <code>window_size</code>, and <code>window_anchor</code> parameters; implement window computation in the FQE result assembly layer — computed against the fully assembled result set, not delegated to individual backends — to guarantee consistent behaviour across all registered backend types</td>
</tr>
<tr>
<td>Scenario Comparison Parameter</td>
<td>Add <code>scenario_definitions</code> table to the SMR PostgreSQL schema; extend the Platform Admin API with scenario definition CRUD; extend the Semantic Intent Layer JSON schema to add a <code>scenario</code> parameter referencing a registered scenario ID; extend the FQE result assembly layer to perform scenario delta computation, producing a three-column result set (actual value, scenario value, delta) from a single query execution</td>
</tr>
<tr>
<td>Inline Composite Benchmark</td>
<td>Extend the <code>benchmark</code> dimension field in the Semantic Intent Layer schema to accept an inline composition object (<code>[{ "benchmark_id": "…", "weight": 0.60 }, …]</code>) in addition to a pre-registered blend ID; implement inline composition resolution in the Benchmark Data Service Adapter at query time without requiring a pre-registration step; extend the lineage record writer to serialise the inline composition into the lineage record for auditability</td>
</tr>

<!-- ── Phase 11 ── -->
<tr>
<td rowspan="6">11</td>
<td rowspan="6"><strong>Open API Surface</strong></td>
<td>SMR Browser REST API</td>
<td>Add new read-only API surface to the SMR service: <code>GET /v1/smr/metrics</code> (cursor-paginated), <code>GET /v1/smr/metrics/{id}</code> (full definition with version history), <code>GET /v1/smr/dimensions</code>, <code>GET /v1/smr/hierarchies</code>; enforce JWT authentication on all endpoints; apply the querying user's entitled metric visibility as a row-level filter on all responses</td>
<td rowspan="6">Compliance teams query the lineage store directly for regulatory audit; BI and application teams integrate against open REST and GraphQL APIs without routing through the MCP interface; high-frequency queries hit pre-computed materialised views for predictable sub-second latency; streaming consumers render progressive query status</td>
</tr>
<tr>
<td>Lineage Query REST API</td>
<td>Add new read-only API surface to the Analytical Lineage Store service: <code>GET /v1/lineage/{result_id}</code> fetches the full JSON document from the object store by key; <code>POST /v1/lineage/search</code> queries the <code>analytics.lineage_index</code> PostgreSQL table for matching <code>result_id</code>s (filterable by <code>user_sub</code>, <code>time_range</code>, <code>compliance_mode</code>, <code>error_code</code>), then fetches full documents from the object store for each match; <code>GET /v1/lineage/{result_id}/sub-plans</code> returns the <code>sub_plans</code> field from the fetched object store document; enforce JWT scoping so users retrieve only their own records; extend to tenant-wide search for Platform Admin role</td>
</tr>
<tr>
<td>GraphQL API Gateway</td>
<td>Create new GraphQL server implementing a typed schema over the MCP Capability Layer; define query types for <code>analyseMetric</code>, <code>comparePortfolios</code>, <code>listMetrics</code>, <code>getMetricDefinition</code>, and <code>drilldown</code> with typed input and output schemas; implement JWT extraction from HTTP Authorization header; route all resolvers through the unchanged governance pipeline — no direct backend access, no governance bypass</td>
</tr>
<tr>
<td>NDJSON Result Streaming and Progress Events</td>
<td>Extend the MCP Capability Layer to support a streaming response mode; extend the FQE to emit four ordered progress events during execution (<code>intent_resolved</code>, <code>entitlements_applied</code>, <code>plan_compiled</code>, <code>executing</code>); implement NDJSON frame serialisation delivering each backend sub-result as it arrives followed by a terminal frame containing the complete assembled result, DVL display spec, and lineage URL; maintain backward compatibility with existing non-streaming consumers</td>
</tr>
<tr>
<td>FQE Adaptive Planning</td>
<td>Add <code>backend_latency_stats</code> table to PostgreSQL; extend the FQE to record observed p50 and p95 execution latency per backend after every query; implement adaptive routing logic that compares current observed latency against the rolling baseline and reroutes to the next registered backend with matching <code>dataAffinity</code> when degradation exceeds a configurable multiplier; log all routing decisions in the lineage record's <code>meta.backendsUsed</code> field</td>
</tr>
<tr>
<td>Materialised View Registration</td>
<td>Create <code>materialised_views</code> table in PostgreSQL storing named pre-computed result templates (metric IDs, dimensions, time expression) with a cron refresh schedule; extend the Scheduled Query Service to execute registered materialised view refreshes and write results to a dedicated cache store; extend the FQE query matcher to detect when an incoming LQP matches a registered materialised view and route to the cache store; extend the Semantic Execution Governance cost estimator to apply an 800-unit cost reduction for matched materialised view queries</td>
</tr>

</tbody>
</table>

---

*This is a proposed delivery sequence, not a committed plan. For the product specification, see [README.md](./README.md) and the numbered chapter documents. For the proposed reference implementation stack, see [04-technical-implementation.md](./04-technical-implementation.md).*
