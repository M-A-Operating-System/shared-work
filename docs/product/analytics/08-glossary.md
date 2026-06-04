# Glossary

All named components, technical terms, abbreviations, and domain concepts used across the AI Analytics Platform documentation. Terms are sorted alphabetically. Cross-references to other glossary entries are shown in **bold**.

| Term | Abbrev | Definition |
|------|--------|------------|
| **Aggregation rule** | — | Defines how a metric's values are combined across a dimension (e.g., sum, mean, value-weighted average). Declared in the **SMR** metric definition. Applied identically in every query against that metric. |
| **Analytical Lineage Store** | ALS | Append-only, write-once store of computation provenance records. Records how the **AE** used specific metric definitions, entitlement rules, and execution backends to compute each result. Distinct from data lineage — this is computation provenance, not data movement tracking. |
| **Analytics Engine** | AE | The platform's deterministic computation core. Given a precisely specified request — which metrics, which dimensions, which filters, which time period — it always produces the same answer from the same data with the same access permissions in force. Contains no AI in its computation pipeline. |
| **Chart contract** | — | A named specification in the **DVL** that maps a specific result shape and analytical intent to a deterministic chart type. The same analytical pattern always produces the same chart — not AI-chosen. |
| **Compliance artifact tier** | — | Enhanced output tier triggered automatically when both compliance signals are present — the metric's compliance-relevant flag and the AI's classification of the query's stated purpose. Produces a signed **compliance provenance record** and enforces the **export gate**. No user action or role claim is required. |
| **Compliance provenance record** | — | Sealed, cryptographically signed record of the complete computation chain for a compliance-escalated query: the original request, intent classification, metric definition and version, logical field specification, physical execution detail, and entitlement snapshot. Any party holding the platform's public key can independently verify that no field has been altered since sealing. |
| **Compliance purpose** | — | AI classification of a query's stated intent as regulatory in nature. Scored 0–1 against a configurable threshold (default 0.8). One of the two signals required to trigger the **compliance artifact tier**. |
| **Compliance-relevant flag** | — | Flag set by the Metric Owner at registration time on any metric whose output may be used in regulatory reporting. One of the two signals required to trigger the **compliance artifact tier**. |
| **Cost units** | — | Abstract measure of query execution cost estimated by **SEG** before any backend is contacted. Used to enforce platform-level cost ceilings and block runaway queries before execution. |
| **Data Context Repository** | DCR | Pre-existing platform component that provides the persistence and versioning layer for all governed analytical definitions. The **SMR** is the governance layer built on top of it. |
| **Data Visualization Language** | DVL | The platform's governed presentation format. Produces a deterministic display specification — either a chart or a structured table — based on the result shape and analytical intent. AI consumers do not select chart types; the DVL governs that choice. |
| **Default deny** | — | Access control posture in which an unauthenticated or unentitled request is blocked before any analytical processing begins. The recommended platform configuration. |
| **Entitlement snapshot** | — | Frozen record of the user's roles and access scope at the moment of query execution. Embedded in every **compliance provenance record**. |
| **Federated Query Engine** | FQE | The only platform component with knowledge of physical execution backends. Receives the approved **LQP**, decomposes it into backend-specific sub-plans by data affinity, executes them in parallel, and assembles the result. No other component has access to backend connection details or physical schema information. |
| **Information ratio** | IR | Active return divided by tracking error. Measures consistency of outperformance relative to benchmark. |
| **JSON Web Token** | JWT | Host-issued bearer token passed with every request. Contains user identity, role claims, and access scope. The platform evaluates entitlements from the combined claims present at query time. |
| **Logical Query Plan** | LQP | Platform-agnostic plan of analytical operations produced by the **SIL**. Contains no backend references, no SQL, and no physical schema identifiers. The **FQE** translates it into backend-specific queries at execution time. |
| **MCP Capability Layer** | MCP | The single governed entry point through which all AI consumers access the platform. Exposes `run_analytics`, `list_operations`, and `drilldown` tools. No alternative execution path exists. |
| **Metric definition** | — | A registered, versioned, formula-specific declaration of how a metric is calculated, from which sources, under which dimensional constraints, and with which access policies. A metric can only be queried once it has been approved and versioned in the **SMR**. |
| **Model Context Protocol** | MCP | Open standard for connecting AI systems to tools and data. The protocol used by the platform's **MCP Capability Layer**. |
| **Narrative** | — | Governed plain-language summary of a computed result, produced by the **NSE**. Every value in the narrative must be present in the result — unanchored figures are rejected. |
| **Narrative Synthesis Engine** | NSE | Post-computation component that produces a plain-language summary of a result. Anchored strictly to computed values. Optional — can be disabled. |
| **Net Interest Margin** | NIM | Net interest income as a percentage of average earning assets. |
| **Net Stable Funding Ratio** | NSFR | Basel III metric measuring funding stability over a one-year horizon. A compliance-relevant metric by definition. |
| **Risk-Weighted Assets** | RWA | Assets weighted by credit risk. Used in regulatory capital ratio calculations. |
| **Role-Aware Projection Layer** | RAPL | Entitlement enforcement component. Applies metric access filters, dimension filters, row predicates, and column masks derived from the user's identity before any query reaches a backend. |
| **Row predicate** | — | Access condition injected into the query by **RAPL** that restricts which data rows a user can access. Applied at the query level — not as a post-retrieval filter. |
| **SEC Regulation BI mode** | — | Compliance governance mode for SEC best interest regulation. Blocks investment recommendations in **NSE** narrative output. |
| **Semantic Data Context Store** | DCS | The document store within the **DCR** that persists all governed analytical definitions — metrics, dimensions, operations, and governance configuration — as versioned documents. |
| **Semantic Execution Governance** | SEG | Governance gate between **RAPL** and **FQE**. Applies cost estimation, data classification checks, complexity limits, and compliance mode classification. No query reaches a backend without passing all checks. |
| **Semantic Intent Layer** | SIL | Receives a structured request, resolves every identifier against the approved analytics and metrics definitions in the **SMR**, and produces a validated, platform-agnostic **LQP**. Entirely deterministic — no AI model runs inside it. |
| **Semantic layer** | — | The abstraction between AI consumers and physical data backends. Exposes governed business concepts — metrics, dimensions, operations — rather than database tables and columns. The **SMR** is the platform's semantic layer. |
| **Semantic Metrics Repository** | SMR | The governing catalogue of all resolvable analytical concepts for the organisation — metrics, dimensions, hierarchies, measure groups, and domains. Nothing is queryable that is not registered, approved, and versioned here. |
| **Tracking error** | TE | Annualised standard deviation of the difference between portfolio returns and benchmark returns. Measures portfolio volatility relative to benchmark. |
| **Two-signal compliance model** | — | The mechanism by which the **compliance artifact tier** is triggered. Both signals must be independently present: (1) the metric's compliance-relevant flag set at registration; (2) the AI's classification of the query's stated purpose as compliance-driven. Either signal alone is insufficient. |
| **Value at Risk** | VaR | Probabilistic estimate of the maximum loss over a given time horizon at a specified confidence level. Platform supports VaR 95 (95th percentile) and VaR 99 (99th percentile). |
| **vega2img** | — | Standalone render service that converts **DVL** chart specifications to static images. Registered directly with AI consumers as a peer service. Not part of the **AE**. |

---

*AI Analytics Platform — Product Design & Technical Specification · Confidential*
