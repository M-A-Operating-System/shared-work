# Glossary

This glossary defines every named component, technical term, abbreviation, and domain concept used across the AI Analytics Platform documentation. Terms are grouped by category and ordered alphabetically within each group. Where a term has an abbreviation, the abbreviation is shown in parentheses immediately after the term name. Cross-references to other glossary entries are indicated by **bold** text.

---

## Platform Components

| Term | Abbrev | Definition |
|------|--------|------------|
| **Analytics Engine** | — | The platform's deterministic computation core. Given a precisely specified request — which metrics, which dimensions, which filters, which time period — it always produces the same answer from the same data with the same access permissions in force. Contains no AI in its computation pipeline. |
| **Analytical Lineage Store** | — | Append-only, write-once store of computation provenance records. One JSON document per query, stored in object storage at `lineage/{tenant_id}/{yyyy}/{mm}/{dd}/{result_id}.json`. Distinct from data lineage: records how the Analytics Engine used specific metric definitions, entitlement rules, and execution backends to compute a specific result — not how data moved between systems. |
| **Data Context Repository** | DCR | Pre-existing platform component that hosts the **Semantic Data Context Store**. Provides the persistence layer for all SMR definitions. |
| **Federated Query Engine** | FQE | The only platform component with knowledge of physical execution backends. Receives a governance-approved **Logical Query Plan**, decomposes it into backend-specific sub-plans by data affinity, executes sub-plans in parallel across registered backends, assembles results, and writes a complete execution record to the **Analytical Lineage Store**. No other component — not the SIL, not the AI model, not the MCP Capability Layer — has access to backend connection details or physical schema information. |
| **MCP Capability Layer** | — | The single governed entry point through which all AI consumers access the platform. Exposes three tools — `run_analytics`, `list_operations`, and `drilldown` — over MCP Streamable HTTP. Validates JWT tokens and routes all requests through the invariant governance pipeline. No alternative execution path exists. |
| **Narrative Synthesis Engine** | NSE | Post-computation component that makes a targeted call to a language model to summarise a structured result in plain text. Strictly anchored to computed values — it cannot introduce figures, comparisons, or interpretations not present in the result. Invocation is optional and can be disabled per tenant. |
| **Role-Aware Projection Layer** | RAPL | Entitlement enforcement component. Applied after **SIL** resolution and before any query plan reaches a backend. Applies metric access filters, dimension access filters, row predicates, and column masks derived from the authenticated user's JWT claims. Operates on the resolved analytical intent — not on raw SQL. |
| **Semantic Data Context Store** | DCS | General-purpose semantic definition registry that backs the **Semantic Metrics Repository**. Stores `analytical_metric`, `analytical_dimension`, `analytical_operation`, and `governance_config` document types as versioned JSON/YAML documents. |
| **Semantic Execution Governance** | SEG | Governance gate applied after **RAPL** projection and before **FQE** dispatch. Applies five sequential checks: cost estimation, classification gating, complexity limits, circuit breakers, and compliance mode classification. No query reaches a physical backend without passing all five checks. Writes a governance decision record to the lineage store before any backend call. |
| **Semantic Intent Layer** | SIL | Receives a structured MCP tool call (`operation_id` and `params`), resolves every identifier against the approved analytics and metrics definitions in the **Semantic Metrics Repository**, and produces a validated, platform-agnostic **Logical Query Plan**. Entirely deterministic — no AI model runs inside it. |
| **Semantic Metrics Repository** | SMR | The governing catalogue of all resolvable analytical concepts for a tenant — metrics, dimensions, hierarchies, measure groups, and domains. Nothing is queryable that is not registered, approved, and versioned here. Backed by the **Semantic Data Context Store**. The pre-condition for every downstream component: no query can be served against a concept that has not been modelled and approved in the SMR. |
| **Visualisation Ontology** | VO | Governed schema of chart contracts that map result schemas and intent patterns to specific chart configurations. Chart selection is deterministic — the same analytical pattern always produces the same chart type across users, sessions, and time. AI consumers do not select chart types. |
| **vega2img** | — | Standalone MCP render service that converts **DVL** chart specifications to static SVG or PNG images. Registered directly with AI consumers as a peer MCP server. Not part of the Analytics Engine. |

---

## Query Planning & Execution

| Term | Abbrev | Definition |
|------|--------|------------|
| **Backend adapter** | — | Translator component within the **FQE** that converts a sub-plan into a backend's native protocol (SQL, OData, SPARQL, etc.) and returns a typed result set. Each adapter implements a two-method contract: `ping()` for health checking and `executeSubPlan()` for execution. |
| **Cache bypass** | — | Behaviour enforced when `compliance_purpose: true` — compliance queries are never served from the result cache. A fresh computation is required for every regulatory submission. |
| **Cost units** | — | Abstract execution cost metric used by the **SEG** to estimate query cost before any backend is contacted. Calculated from: metric count × backend cost tier × result cardinality estimate × time period complexity × federation overhead × cache discount. Compared against per-tenant cost ceilings. |
| **Data affinity** | — | Logical data domain tag declared by each metric in its SMR definition (e.g., `portfolio`, `risk_metrics`, `regulatory`, `benchmarks`). The **FQE** uses data affinity to route each sub-plan to the correct registered backend. Metrics sharing the same affinity are grouped into a single sub-plan. |
| **Execution profile** | — | Declares which pipeline stages a given analytical operation invokes. Three profiles: `data_retrieval` (Auth → RAPL → FQE → Lineage), `metric_query` (adds SIL and SEG), `full_analytical` (adds Visualisation Ontology and NSE). |
| **LQP signature** | — | Deterministic SHA-256 hash of the metric IDs and versions, dimension IDs, filter predicates, time expression, entitlement hash, and tenant ID. Used as the cache key for result caching. |
| **Logical Query Plan** | LQP | Platform-agnostic DAG of analytical operations produced by the **Semantic Intent Layer**. Contains no backend references, no SQL, and no physical schema identifiers — only analytical operations expressed against SMR-registered concepts. The FQE translates the LQP into backend-specific physical queries at execution time. |
| **Physical query** | — | Backend-specific SQL, OData, SPARQL, or other protocol query generated from a **LQP** sub-plan by a **backend adapter**. Never exposed to AI consumers or language models. |
| **Result assembly** | — | Final **FQE** step: joining sub-results returned by multiple backends on shared dimension keys to produce a single unified result set. |
| **Sub-plan** | — | Fragment of a **Logical Query Plan** scoped to a single execution backend, produced by splitting the LQP by data affinity. Sub-plans execute in parallel. |
| **Sub-plan decomposition** | — | The **FQE** process of splitting an LQP into sub-plans by data affinity, assigning each to the matching registered backend. |

---

## Governance & Entitlements

| Term | Abbrev | Definition |
|------|--------|------------|
| **Circuit breaker** | — | **SEG** check that blocks a query if it exceeds a configured threshold — cost ceiling, complexity limit, or per-user rate limit. Applies before any backend is contacted. |
| **Classification gating** | — | **SEG** check that compares each metric's `classification_level` against the requesting user's clearance. Queries that include metrics above the user's clearance ceiling are blocked. |
| **Column mask** | — | Entitlement rule applied by **RAPL** that suppresses, redacts, or nullifies specific column values based on the user's access policy. Applied at result assembly, not at query generation. |
| **Default deny** | — | Recommended access control posture: `defaultDenyAll: true`. An unauthenticated or unentitled request is blocked before any analytical processing begins. Any user with no matching role receives `ENTITLEMENT_DENIED` before any query executes. |
| **Entitlement hash** | — | SHA-256 of the resolved row predicates and column masks active for a query. Incorporated into the **LQP signature** to ensure cached results are only served to users with identical entitlement state. |
| **Entitlement snapshot** | — | Frozen record of the user's roles, entity scope, and evaluated entitlements at the moment of query execution. Embedded in the **compliance provenance record**. |
| **Field ceiling** | — | Entitlement rule restricting the data classification level of fields visible to a user or agent. Fields exceeding the ceiling are excluded from the approved field set before query execution. |
| **Governance decision record** | — | Record written to the **Analytical Lineage Store** by **SEG** before any backend call, capturing the outcome of all five governance checks — including blocked queries. Every query produces a governance decision record whether it proceeds or is rejected. |
| **Governance floor** | — | Minimum governance configuration that cannot be lowered by any tenant, including Platform Admins. Governance floors are architectural properties of the platform, not configurable thresholds. There is no bypass mode. |
| **Projection record** | — | **RAPL** output record capturing: roles presented, metrics requested, metrics projected, metrics blocked, row predicates applied, and column masks applied — at query time. Embedded in the compliance provenance record. |
| **Row predicate** | — | WHERE clause condition injected into the **LQP** by **RAPL** to restrict which data rows a user can access (e.g., `portfolio_id IN (authorised_portfolio_list)`). Applied at the query level, not as a post-retrieval filter. |

---

## Compliance & Regulatory

| Term | Abbrev | Definition |
|------|--------|------------|
| **Basel III/IV mode** | — | Compliance governance mode enforcing capital adequacy regulatory requirements: entity dimension required on all queries, regulatory snapshot writes to dedicated tables, stress scenario classification. |
| **Compliance artifact tier** | — | Enhanced output tier triggered automatically when both compliance signals are present. Produces a regulatory trace record, enforces the export gate, and generates a signed **compliance provenance record**. No user action or role claim is required. |
| **Compliance provenance record** | — | Sealed, cryptographically signed record of the complete computation chain for a compliance-escalated query: raw request, intent classification, metric definition and version, logical field specification, physical execution detail, and entitlement snapshot. Signed using ECDSA-P256-SHA256. Written to the append-only compliance audit store. Any party holding the platform's published public key can independently verify that no field has been altered since sealing. |
| **Compliance-relevant flag** | — | Metadata flag set by the **Metric Owner** at registration time on any metric whose output may be used in regulatory reporting. One of the two signals required to trigger compliance artifact escalation. |
| **Compliance purpose** | — | AI classification of a query's stated intent as regulatory in nature. Expressed as a `compliance_purpose_score` (0–1) compared against a tenant-configured `compliance_intent_threshold` (default 0.8). One of the two signals required to trigger compliance artifact escalation. |
| **Export gate** | — | Lock applied to compliance-escalated query results preventing export until the complete **compliance provenance record** has been confirmed written. Released only when provenance is complete. |
| **MiFID II mode** | — | Compliance governance mode for Markets in Financial Instruments Directive II: enforces PII-adjacent dimension logging, best-execution timeframe requirements, and transaction reporting trace records. |
| **Regulatory trace record** | — | Compliance mode-specific audit record written to a dedicated trace table (e.g., `analytics.mifid2_trace`) in addition to the standard lineage record. Required for MiFID II and Basel III/IV compliance modes. |
| **SEC Regulation BI mode** | — | Compliance governance mode for SEC best interest regulation: blocks investment recommendations in **NSE** narrative synthesis output. |
| **Two-signal compliance model** | — | The mechanism by which compliance artifact escalation is triggered. Both signals must be independently present: (1) `metric.compliance_relevant: true` — set statically by the Metric Owner at registration; (2) `intent.compliance_purpose: true` — classified dynamically by the AI at query time. Either signal alone is insufficient. |

---

## Output & Visualisation

| Term | Abbrev | Definition |
|------|--------|------------|
| **Chart contract** | — | A named, parameterised specification in the **Visualisation Ontology** that maps a specific intent pattern and result schema to a fully configured chart type. Evaluated deterministically — the highest-scoring contract match governs the output. |
| **Data Visualization Language** | DVL | The platform's output format for display specifications. A JSON envelope with two types: `type: "chart"` (a Vega-Lite v5 specification) and `type: "table"` (a typed column schema with pagination and formatting rules). The DVL specification is consumed by AI consumers or passed to **vega2img** for static rendering. |
| **Display intent** | — | Declarative presentation preference expressed in the structured request (e.g., `display_intent: chart → comparative metrics across categorical dimension → grouped_bar`). Used as input to the **Visualisation Ontology** evaluation alongside the result schema and intent pattern. |
| **Intent pattern** | — | Classification of the analytical operation's output shape. Governs **Visualisation Ontology** contract selection. Defined patterns: `COMPARISON`, `TREND`, `DISTRIBUTION`, `THRESHOLD`, `ATTRIBUTION`, `RELATIONSHIP`, `COMPOSITION`. |
| **Narrative** | — | Governed plain-language summary of the computed result produced by the **NSE**. Every numeric value in the narrative must be present in the result set — if any value cannot be matched, the narrative is rejected and regenerated. If the second attempt also fails, the `narrative` field is omitted. |

---

## Platform Roles

| Term | Definition |
|------|------------|
| **Analytical End User** | Asks governed analytical questions via natural language and receives role-constrained results. Has no knowledge of data structures or metric identifiers. |
| **Application Admin** | Privileged tenant user responsible for **SMR** integrity, entitlement policies, and governance configuration. Must be configured before go-live — without one, the SMR contains no approved definitions and the platform cannot serve any query. Approves **Semantic Modeller** changes. |
| **Integration Engineer** | Registers execution backends, maintains connection configuration, and declares the physical mapping that the **FQE** resolves at execution time. Operates through configuration interfaces, not the query path. |
| **Metric Owner** | Subject-matter expert assigned ownership of one or more registered metrics. Reviews proposed definition changes, approves aggregation rule modifications, and sets the `compliance_relevant` flag. Distributes approval responsibility without concentrating it in the Semantic Modeller or Application Admin. |
| **Platform Admin** | Cross-tenant platform team responsible for infrastructure health, tenant onboarding, and cross-tenant governance audit. Has no query interface into tenant data. |
| **Power Analyst** | Multi-dimensional exploration, governed drilldown, lineage inspection, and result export. |
| **Semantic Modeller** | Defines and maintains the logical semantic layer: metric definitions, dimension hierarchies, aggregation rules, measure groups, and domain structures in the SMR. A specialist data modelling role requiring both domain knowledge (what does this metric mean?) and modelling precision (how is it calculated, from which sources, under which dimensional hierarchies, with which access policies?). The critical pre-condition for everything downstream — no query can be served against a concept that has not been modelled, approved, and registered. |

---

## Analytical Concepts

| Term | Abbrev | Definition |
|------|--------|------------|
| **Aggregation rule** | — | Defines how a metric's values are combined across a dimension (e.g., `value_weighted_average`, `sum`, `last`, `count`, `mean`). Declared in the SMR metric definition. Applied identically in every query against that metric. |
| **Benchmark return** | — | Return of a portfolio's registered default benchmark index over the query period. Used as the comparison reference in performance analytics. |
| **BHB attribution** | — | Brinson-Hood-Beebower performance attribution. Decomposes active return into allocation effect, selection effect, and interaction effect. |
| **Dimension hierarchy** | — | Ordered set of dimension levels that support aggregation and drilldown (e.g., geography: country → region → global). Declared in the SMR and enforced by the **SIL**. |
| **Drilldown** | — | Governed decomposition of a computed metric into a finer dimension level. Exposed as the `drilldown` MCP tool. Produces a new governed result scoped to the selected dimension value. |
| **Factor bucket** | — | Risk factor categorisation dimension (e.g., rates, credit, equity, FX) used in VaR attribution and risk factor contribution analysis. |
| **Information ratio** | IR | Active return divided by tracking error. Measures consistency of outperformance relative to benchmark. |
| **Metric definition** | — | A registered, versioned, formula-specific declaration of how a metric is calculated, from which sources, under which dimensional constraints, and with which access policies. Stored in the SMR. A metric can only be queried once it has been approved and versioned. |
| **Measure group** | — | A set of related metrics grouped by analytical domain in the SMR (e.g., all performance metrics, all risk metrics). Supports bulk entitlement assignment and catalogue navigation. |
| **Semantic layer** | — | The abstraction between AI consumers and physical data backends. Exposes governed business concepts (metrics, dimensions, operations) rather than database tables and columns. The SMR is the platform's semantic layer. |
| **Tracking error** | TE | Annualised standard deviation of the difference between portfolio returns and benchmark returns. Measures portfolio volatility relative to benchmark. |
| **Value at Risk** | VaR | Probabilistic estimate of the maximum loss over a given time horizon at a specified confidence level. Platform supports VaR 95 (95th percentile) and VaR 99 (99th percentile) using historical simulation. |
| **Weight metric** | — | A metric referenced by `weight_metric_id` that provides the weighting values for value-weighted aggregations. The **SIL** validates the weight metric reference at query time. |

---

## Regulatory Metrics

| Term | Abbrev | Definition |
|------|--------|------------|
| **High-Quality Liquid Assets** | HQLA | LCR numerator component. Assets that can be readily converted to cash to meet liquidity needs in a stressed scenario. |
| **Liquidity Coverage Ratio** | LCR | Basel III regulatory metric. Calculated as `SUM(hqla_value) / SUM(net_outflow_30d)`. Requires entity-level grain and must be identical across all reports and regulatory submissions. A `compliance_relevant` metric by definition. |
| **Net Stable Funding Ratio** | NSFR | Basel III regulatory metric measuring the stability of a bank's funding profile over a one-year horizon. A `compliance_relevant` metric by definition. |
| **Net Interest Margin** | NIM | Banking metric: net interest income as a percentage of average earning assets. |
| **Risk-Weighted Assets** | RWA | Regulatory capital adequacy measure: assets weighted by credit risk. Used in capital ratio calculation. |

---

## Protocols & Standards

| Term | Abbrev | Definition |
|------|--------|------------|
| **ECDSA-P256-SHA256** | — | Elliptic Curve Digital Signature Algorithm using P-256 curve and SHA-256 hash. Used to cryptographically sign **compliance provenance records**. Any party holding the platform's published public key can independently verify record integrity without platform access. |
| **JSON Web Token** | JWT | Host-issued bearer token passed with every MCP tool call. Contains `sub` (user identity), `tenant_id`, `exp` (expiry), role claims, and scope claims (`managed_portfolios`, `entity_ids`). The platform evaluates entitlements from the combined claims present at query time. |
| **Model Context Protocol** | MCP | Open standard for connecting AI systems to tools and data. The single governed channel through which all AI consumers access the platform. Uses Streamable HTTP transport. All consumers — conversational assistants, autonomous agents, custom applications — enter through this channel and traverse the same governance pipeline. |
| **Vega-Lite v5** | — | Chart specification grammar used as the underlying format for **DVL** `type: "chart"` specifications. JSON-based. Not exposed as a named dependency in platform prose — referenced only within DVL specification content. |

---

## SMR Document Types

| Term | Definition |
|------|------------|
| **analytical_dimension** | DCS document declaring a dimension: its values, hierarchical levels, physical mapping, and access policies. |
| **analytical_metric** | DCS document declaring a metric: formula, aggregation rule, required and optional dimensions, `data_affinity`, `classification_level`, `compliance_relevant` flag, physical mapping, and cost weight. |
| **analytical_operation** | DCS document declaring a queryable operation: execution profile, required and optional parameters, and the set of supported metrics and dimensions. A `run_analytics` call referencing a value not in the operation catalogue is rejected before LQP generation. |
| **governance_config** | Per-tenant DCS document declaring cost ceilings, circuit breaker thresholds, compliance intent threshold, and classification gating rules. Read by SEG at startup and refreshed on DCS change events. |

---

## Metric & Document Lifecycle

| Status | Definition |
|--------|------------|
| **Proposed** | Initial state. Definition is under authorship by the Semantic Modeller. Not queryable. |
| **In review** | Submitted for approval. Visible to Metric Owners and Application Admins. Not queryable. |
| **Approved** | Ratified by the Metric Owner or Application Admin. Assigned a version identifier. Queryable. |
| **Deprecated** | Superseded by a newer version. Resolvable but surfaced with a deprecation warning. Metric Owners should migrate consumers to the replacement version. |
| **Retired** | Removed from the resolvable set after the deprecation period. Not queryable. Lineage records referencing the retired version are preserved. |

---

*AI Analytics Platform — Product Design & Technical Specification · Confidential*
