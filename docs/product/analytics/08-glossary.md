# Glossary

All named components, technical terms, abbreviations, and domain concepts used across the AI Analytics Platform documentation. Terms are sorted alphabetically. Cross-references to other glossary entries are shown in **bold**.

| Term | Abbrev | Definition |
|------|--------|------------|
| **Analytical Lineage Store** | ALS | Append-only, write-once store of computation provenance records. Records how the **AE** used specific metric definitions, entitlement rules, and execution backends to compute each result. Distinct from data lineage — this is computation provenance, not data movement tracking. |
| **Analytics Engine** | AE | The platform's deterministic computation core. Given a precisely specified request — which metrics, which dimensions, which filters, which time period — it always produces the same answer from the same data with the same access permissions in force. Contains no AI in its computation pipeline. |
| **Compliance artifact tier** | — | Enhanced output tier triggered automatically when both compliance signals are present — the metric's compliance-relevant flag and the AI's classification of the query's stated purpose. Produces a signed **compliance provenance record** and enforces the **export gate**. No user action or role claim is required. |
| **Compliance provenance record** | — | Sealed, cryptographically signed record of the complete computation chain for a compliance-escalated query: the original request, intent classification, metric definition and version, logical field specification, physical execution detail, and entitlement snapshot. Any party holding the platform's public key can independently verify that no field has been altered since sealing. |
| **Compliance purpose** | — | AI classification of a query's stated intent as regulatory in nature. Scored 0–1 against a configurable threshold (default 0.8). One of the two signals required to trigger the **compliance artifact tier**. |
| **Compliance-relevant flag** | — | Flag set by the Metric Owner at registration time on any metric whose output may be used in regulatory reporting. One of the two signals required to trigger the **compliance artifact tier**. |
| **Data Context Repository** | DCR | Pre-existing platform component that provides the persistence and versioning layer for all governed analytical definitions. The **SMR** is the governance layer built on top of it. |
| **Data Visualization Language** | DVL | The platform's governed presentation format. Produces a deterministic display specification — either a chart or a structured table — based on the result shape and analytical intent. AI consumers do not select chart types; the DVL governs that choice. |
| **Federated Query Engine** | FQE | The only platform component with knowledge of physical execution backends. Receives the approved **LQP**, decomposes it into backend-specific sub-plans by data affinity, executes them in parallel, and assembles the result. No other component has access to backend connection details or physical schema information. |
| **JSON Web Token** | JWT | Host-issued bearer token passed with every request. Contains user identity, role claims, and access scope. The platform evaluates entitlements from the combined claims present at query time. |
| **Logical Query Plan** | LQP | Platform-agnostic plan of analytical operations produced by the **SIL**. Contains no backend references, no SQL, and no physical schema identifiers. The **FQE** translates it into backend-specific queries at execution time. |
| **MCP Capability Layer** | MCP | The single governed entry point through which all AI consumers access the platform. Exposes `run_analytics`, `list_operations`, and `drilldown` tools. No alternative execution path exists. |
| **Metric definition** | — | A registered, versioned, formula-specific declaration of how a metric is calculated, from which sources, under which dimensional constraints, and with which access policies. A metric can only be queried once it has been approved and versioned in the **SMR**. |
| **Model Context Protocol** | MCP | Open standard for connecting AI systems to tools and data. The protocol used by the platform's **MCP Capability Layer**. |
| **Narrative** | — | Governed plain-language summary of a computed result, produced by the **NSE**. Every value in the narrative must be present in the result — unanchored figures are rejected. |
| **Narrative Synthesis Engine** | NSE | Post-computation component that produces a plain-language summary of a result. Anchored strictly to computed values. Optional — can be disabled. |
| **Role-Aware Projection Layer** | RAPL | Entitlement enforcement component. Applies metric access filters, dimension filters, row predicates, and column masks derived from the user's identity before any query reaches a backend. |
| **Semantic Data Context Store** | DCS | The document store within the **DCR** that persists all governed analytical definitions — metrics, dimensions, operations, and governance configuration — as versioned documents. |
| **Semantic Execution Governance** | SEG | Governance gate between **RAPL** and **FQE**. Applies cost estimation, data classification checks, complexity limits, and compliance mode classification. No query reaches a backend without passing all checks. |
| **Semantic Intent Layer** | SIL | Receives a structured request, resolves every identifier against the approved analytics and metrics definitions in the **SMR**, and produces a validated, platform-agnostic **LQP**. Entirely deterministic — no AI model runs inside it. |
| **Semantic Metrics Repository** | SMR | The governing catalogue of all resolvable analytical concepts for the organisation — metrics, dimensions, hierarchies, measure groups, and domains. Nothing is queryable that is not registered, approved, and versioned here. |

---

*AI Analytics Platform — Product Design & Technical Specification · Confidential*
