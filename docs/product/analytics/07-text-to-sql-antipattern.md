# Appendix: Why Not Text-to-SQL? The GenAI Analytics Antipattern

This appendix describes the Text-to-SQL approach to AI-powered analytics — what it is, why it is appealing, why it is commonly the first thing teams reach for, and why it is not an appropriate long-term foundation for governed analytical intelligence in a regulated environment. It is intended as a reference for teams evaluating their options and as context for why the AI Analytics Platform was designed the way it was.

The Text-to-SQL pattern is not wrong everywhere. For exploratory data work, internal tooling, and low-stakes analytical sandboxes, it is a legitimate option. The argument here is narrower: for production analytical systems serving regulated business processes, it is the wrong foundation — and the structural defects compound over time rather than resolve.

---

## What Text-to-SQL is

Text-to-SQL (NL2SQL, "chat with your data") feeds a natural language question plus a physical database schema to an LLM, which generates SQL executed directly against the database. No semantic layer, no metric registry, no governed definitions. The demo is compelling and implementable in hours. The problem is that every structural defect compounds as the use case matures and regulatory scrutiny increases.

The pattern has genuine short-term appeal:

| Appeal | Short-term reality |
|--------|--------------------|
| Fast time-to-demo | Working demo in hours on a well-structured schema |
| No semantic modelling upfront | No need to define metrics or hierarchies before showing results |
| Impressive for simple questions | `SUM(AUM) GROUP BY portfolio` reliably produces correct SQL |
| Off-the-shelf availability | Numerous tools implement this pattern out of the box |

These advantages are real for low-stakes exploratory analytics. The argument here is narrower: for production analytical systems serving regulated business processes, the pattern is the wrong foundation — and the structural defects compound over time.

---

## The structural defects

**1. Metrics have no single definition.** "Portfolio Return" means whatever the LLM infers from the schema at query time — the same question can produce different SQL and different numbers. In institutional analytics, metric definitions must be identical across reports, conversations, and regulatory submissions.

**2. Physical schema is exposed to the AI model.** SQL generation requires injecting table names, column names, and relationships into the LLM's context — transmitting internal data architecture to third-party providers, enabling schema reconnaissance, and creating brittleness when columns are renamed.

**3. Results cannot be audited.** "The AI wrote some SQL and this number came back" is not an acceptable audit trail for MiFID II, Basel III, AIFMD, or SEC Regulation BI. Every query is a one-off artefact; there is no lineage, no versioned definition, and no reproducible calculation path.

**4. No entitlement model at the semantic tier.** Access control is the database credential. A user who causes the LLM to omit expected WHERE-clause restrictions receives data they should not see. There is no concept of "this role may query these metrics."

**5. SQL generation degrades with complexity.** The queries that matter most are where LLM SQL generation is least reliable:

| Query type | Reliability |
|-----------|-------------|
| `SUM(column) GROUP BY dimension` | High |
| Multi-table JOIN with filtering | Medium — join path errors common |
| Window functions (rolling averages, period-over-period) | Low — frame specification errors |
| Derived metrics with null handling | Low — silent division-by-zero |
| Time-bucketed aggregation (QTD, YTD, since inception) | Low — date arithmetic failures |
| Regulatory formulas (Modified Dietz, LCR, Tracking Error) | Very low — requires explicit definition, not inference |

**6. No metric versioning or change management.** When a regulatory update changes a formula, there is no versioned definition to update, no approval workflow, and no audit of which formula version produced which historical result.

**7. No scope boundary.** A governed semantic layer rejects unregistered metric references. Text-to-SQL attempts to answer any question, generating plausible-looking SQL that may produce meaningless results with no signal to the user.

**8. Cost and performance are unpredictable.** LLM-generated SQL is written to satisfy the question, not execute efficiently — full table scans, missing partition filters, and unoptimised aggregations make query cost governance impossible.

**9. Multi-source federation is not possible.** The pattern is limited to a single SQL-speaking backend. Portfolio, risk, market, and reference data held in heterogeneous systems cannot be served from a unified natural-language interface.

---

## Security risks

These risks are structural — they exist because the LLM is both the interface and the query generator. Prompt guardrails reduce surface area but cannot eliminate them; the only reliable defence is to remove the attack surface.

**Prompt injection.** User input and SQL generation share the same LLM context. A crafted query can instruct the LLM to override access restrictions, return data outside the user's entitlement, or expose other entities' data. Indirect injection — malicious instructions embedded in data fields the LLM reads — is also viable.

**Schema exfiltration.** The database schema is in the system prompt. Questions such as "What tables do you have access to?" or error-inducing probes can surface internal table and column names — a reconnaissance step for further attacks and itself a data governance breach.

**Data exfiltration via filter bypass.** Row restrictions depend on the LLM generating correct WHERE clauses. An omitted predicate, an aggregation inference query ("How many portfolios have return > 15%?"), or a cross-role confusion attack can expose data the credential technically permits but the user is not entitled to see.

| Risk | Text-to-SQL | Semantic Analytics Platform |
|------|------------|------------------------------|
| Prompt injection | LLM receives user input and generates SQL — injection can influence query logic | LLM produces structured JSON parameters only; deterministic code validates and executes |
| Schema exfiltration | Physical schema is in the system prompt | Physical schema is never in any prompt; only SMR business definitions are exposed |
| Data exfiltration / filter bypass | Row restrictions generated by the LLM can be omitted or bypassed | Row predicates injected by deterministic Role-Aware Projection; LLM cannot omit or alter them |

---

## Why this matters for regulated financial services

Most of the defects above are invisible at the demo stage and tolerable in early, low-stakes deployments. They become expensive when:

- Metric inconsistency becomes apparent across users and regulatory submissions
- A regulator requests an audit trail that doesn't exist
- The question scope reaches regulated formulas and cross-domain federation — the queries where SQL generation is least reliable
- A prompt injection or filter bypass incident surfaces entitlement failures
- A formula change is needed and there is no versioned definition to update

Teams that attempt to patch these problems incrementally — adding schema filtering, prompt guardrails, SQL validators, and output reconciliation — typically end up building a brittle, prompt-dependent approximation of a semantic layer, at far greater cost than building it correctly from the start.

---

## The correct pattern

The AI Analytics Platform inverts the relationship between GenAI and data access:

| Text-to-SQL | AI Analytics Platform |
|------------|----------------------|
| LLM generates SQL against physical schema | LLM translates intent to structured query parameters |
| Schema is the LLM's input surface | Semantic Metrics Registry is the LLM's input surface |
| Query logic is inferred at runtime | Metric definitions are registered, versioned, and approved |
| Access control is at the database credential | Entitlements are enforced at the semantic tier before execution |
| Results cannot be audited | Every result has a full computation provenance record |
| Metrics are inconsistent across queries | A metric resolves to exactly one definition at any point in time |
| Complex queries fail silently | Unresolvable queries fail explicitly with a structured error |
| Schema exposure is unavoidable | Physical schema is never visible to the AI model |
| Multi-source federation is not supported | FQP routes LQP fragments to any registered backend type |

The LLM's role is constrained to what it is reliable at: translating natural language into structured intent. The computation — resolving metric definitions, enforcing entitlements, executing against data, assembling results — is handled by deterministic components that do not generate.
