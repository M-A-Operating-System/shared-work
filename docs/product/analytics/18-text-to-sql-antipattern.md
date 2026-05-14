# 18 — Why Not Text-to-SQL? The GenAI Analytics Antipattern

## What this document is

This document describes the Text-to-SQL approach to AI-powered analytics — what it is, why it is appealing, why it is commonly the first thing teams reach for, and why it is not an appropriate long-term foundation for governed analytical intelligence in a regulated environment. It is intended as a reference for teams evaluating their options and as context for why the AI Analytics Platform was designed the way it was.

The Text-to-SQL pattern is not wrong everywhere. For exploratory data work, internal tooling, and low-stakes analytical sandboxes, it is a legitimate option. The argument here is narrower: for production analytical systems serving regulated business processes, it is the wrong foundation — and the structural defects compound over time rather than resolve.

---

## What Text-to-SQL is

Text-to-SQL (also called "natural language to SQL", "NL2SQL", or "chat with your data") is an approach where a large language model receives a natural language question and generates SQL directly against a physical database schema.

The typical architecture:

```
User question (natural language)
        │
        ▼
LLM receives:
  - The user's question
  - Physical database schema (table names, column names, data types, sample rows)
  - Optional: few-shot SQL examples
        │
        ▼
LLM generates SQL query
        │
        ▼
SQL executed against database
        │
        ▼
Result rows returned to user
(optionally: LLM narrates the result)
```

No semantic layer. No metric registry. No governed definitions. The LLM reasons about the physical schema and constructs what it believes to be the correct SQL for the question asked.

This can be implemented in hours. The demo is compelling. For many simple questions on well-structured schemas, it produces correct results. And it requires no upfront investment in semantic modelling.

---

## Why teams reach for it

Text-to-SQL is the natural first move when an organisation wants to add AI to its analytics capability. The appeal is genuine:

| Appeal | Reality in the short term |
|--------|--------------------------|
| **Fast time-to-demo** | An LLM connected to a schema can answer natural language questions in a day |
| **No semantic modelling upfront** | No need to define metrics, dimensions, or hierarchies before showing something working |
| **Impressive for simple questions** | "What is the total AUM?" produces correct SQL and a correct answer reliably |
| **Off-the-shelf availability** | Numerous tools, APIs, and frameworks implement this pattern out of the box |
| **Low initial cost** | Connecting an LLM to a database requires minimal infrastructure |
| **Iterative** | Can start narrow and extend question coverage progressively |

These advantages are real. Text-to-SQL is a legitimate quick win for low-stakes exploratory analytics — internal data exploration, ad hoc business intelligence, developer tooling. The pattern earns its initial enthusiasm.

The problem is not that it fails immediately. The problem is that every structural defect in the pattern becomes more costly as the use case matures, the user base grows, and regulatory scrutiny increases.

---

## The structural defects

### 1. Metrics have no single definition

In a Text-to-SQL system, "Portfolio Return" means whatever the LLM infers from the schema at query time. Ask the same question twice and you may get two different SQL expressions — and two different numbers. Ask it in two different ways and the metric formula may differ. There is no authoritative definition; there is only what the LLM decides the SQL should be this time.

In institutional analytics, this is not a nuance — it is a breakdown of trust. "Portfolio Return" must mean the same thing in every report, every conversation, and every regulatory submission. The Modified Dietz method is not equivalent to a simple return calculation, and an LLM reasoning from column names has no reliable way to know which applies.

**The outcome:** Metric inconsistency across sessions, users, and time. Numbers that look correct but are not calculated the same way. Regulatory submissions that cannot be reconciled with one another.

---

### 2. Physical schema is exposed to the AI model

For the LLM to generate SQL, it must know the schema. In practice this means injecting table names, column names, relationships, and often sample data rows into the model's context. This has several consequences:

- **Schema leakage risk:** Every query request transmits internal database structure — table names, column semantics, data relationships — to a third-party AI provider (unless the model runs entirely on-premises). This is a data governance concern and in some jurisdictions a regulatory requirement.
- **Prompt extraction:** A user who understands the system prompt structure can ask questions designed to reveal the schema to themselves — effectively reconnaissance against the organisation's data architecture.
- **Column rename brittleness:** Renaming a database column breaks all queries that relied on that column's name being interpretable by the LLM. The system has no abstraction layer between the physical schema and the AI.
- **Join path inference:** For complex schemas with many tables, the LLM must infer correct JOIN paths. It will sometimes infer incorrectly, producing queries that join on plausible but wrong keys — results that look reasonable but are computed from the wrong rows.

**The outcome:** Internal data architecture becomes an AI input surface. Schema is not a safe thing to expose to a generative model, and any system that requires schema exposure is structurally insecure for production use.

---

### 3. Results cannot be audited

When a user asks "what is the tracking error for the Global Equity fund this quarter?" and receives an answer, what was the calculation? In a Text-to-SQL system, the answer is: the LLM generated some SQL, the SQL was executed, and this number came back. The SQL may or may not have been saved. Even if it was saved, it is an LLM artefact — there is no guarantee it implements the correct formula, and there is no metric definition that it was verified against.

In a regulated environment — MiFID II, Basel III, AIFMD, SEC Regulation BI — "the AI wrote some SQL and this number came back" is not an acceptable audit trail. Regulators require the ability to reconstruct how a specific number was calculated: which formula, which data, which aggregation, over which scope, at which point in time.

Text-to-SQL provides none of this. Every query is a one-off artefact. There is no lineage, no versioned definition, no reproducible calculation path.

**The outcome:** Regulatory audit requests cannot be satisfied. The system is not appropriate for any analytical output that may be challenged — which in financial services is almost all of them.

---

### 4. There is no entitlement model at the semantic tier

In a Text-to-SQL system, access control is typically enforced at the database level — the LLM connects with credentials that determine what tables and rows it can read. This means:

- The LLM has access to everything within those credentials. A user who asks the right question may receive data they should not see, because the entitlement boundary is at the database connection, not at the question.
- Row-level security must be implemented in the database engine and inferred correctly by the LLM's SQL — if the LLM generates a query that bypasses a WHERE clause designed to restrict data, the restriction is not applied.
- There is no concept of "this user's role determines which metrics they may query." The LLM cannot enforce semantic-level entitlements; it can only generate SQL within the connection's permissions.
- Prompt manipulation — asking the question in a way that causes the LLM to generate SQL without the expected filters — is a real attack surface.

**The outcome:** The security boundary is the database credential, not the user's entitlement. In a multi-user environment where different roles should see different analytical views of the same data, this is inadequate.

---

### 5. SQL generation quality degrades with complexity

Text-to-SQL works well for simple aggregations against single tables. Performance degrades rapidly as complexity increases:

| Query type | Text-to-SQL reliability |
|-----------|------------------------|
| `SUM(column) GROUP BY dimension` | High — LLMs handle this well |
| Multi-table JOIN with filtering | Medium — join path errors are common |
| Window functions (rolling averages, period-over-period) | Low — common errors in frame specification |
| Derived metrics (metric A / metric B) with null handling | Low — `SAFE_DIVIDE` vs `/` errors cause silent division-by-zero |
| Time-bucketed aggregation (QTD, YTD, since inception) | Low — date arithmetic is a frequent failure mode |
| Cross-domain queries spanning multiple data sources | Very low — the LLM cannot orchestrate across systems it cannot see |
| Regulatory formulas (Modified Dietz, LCR, Tracking Error) | Very low — formula precision requires explicit definition, not inference |

The queries that matter most in institutional analytics — complex multi-metric calculations, regulated formulas, cross-domain federation — are exactly the queries where LLM SQL generation is least reliable.

**The outcome:** The system works impressively for the queries users don't actually depend on, and fails silently for the queries that drive investment decisions and regulatory submissions.

---

### 6. There is no metric versioning or change management

When the definition of a metric must change — a regulatory update changes the LCR formula, a methodology change updates how portfolio return is calculated — a Text-to-SQL system has no mechanism for managing this. There is no versioned definition to update, no approval workflow, no audit of which definition was in use at which time, and no way to ensure all queries use the new formula from a given date.

In practice, teams handle this by updating prompts or few-shot examples. But there is no guarantee the LLM applies the update consistently, and no lineage record preserving which formula version was used for any given historical result.

**The outcome:** Metric evolution is unmanageable at scale. Historical results cannot be reconciled against current definitions. Regulatory audits of past periods are impossible to reconstruct.

---

### 7. The system cannot say "this question is out of scope"

A governed semantic layer can reject questions that reference metrics or dimensions not registered in the registry — "the metric 'projected_alpha' is not defined in the analytics registry." A Text-to-SQL system has no such boundary. The LLM will attempt to answer any question, either generating SQL that produces some number (which may be wrong) or hallucinating an answer when the schema cannot satisfy the query.

There is no mechanism for a Text-to-SQL system to distinguish between "I can answer this correctly" and "I am generating plausible-looking SQL that may produce a meaningless result."

**The outcome:** Users receive answers to questions the system should not answer. Wrong answers may be indistinguishable from correct ones until the number is challenged.

---

### 8. Cost and performance are unpredictable

LLM-generated SQL is written to satisfy the question, not to execute efficiently. Common patterns:

- Full table scans where indexed queries are available
- Unnecessary subqueries that could be simplified
- Missing partition filters that cause expensive scans of large time-series tables
- Unoptimised aggregation order that moves more data than necessary

A single poorly generated query on a large warehouse table can consume significant compute cost. In a usage environment where many users are submitting queries, unpredictable query costs make budget governance difficult.

**The outcome:** Query cost is ungovernable. A system designed to control analytical spend cannot rely on an LLM to generate cost-efficient SQL.

---

### 9. Multi-source federation is not possible

The Text-to-SQL pattern is fundamentally limited to a single query target that speaks SQL. An organisation whose analytical data spans a SQL data warehouse, an OpenData API, a graph database, and a semantic metrics layer cannot serve a unified natural-language analytics experience via Text-to-SQL — the LLM can only query one backend per request, and cannot orchestrate sub-queries across systems with different query interfaces.

**The outcome:** The pattern does not scale to the data architectures typical of large financial institutions, where portfolio data, risk data, market data, and reference data are held in different systems with different query interfaces.

---

## Why the problems compound over time

Text-to-SQL is an easy start and a hard landing. The problems above are individually manageable in early, low-stakes deployments — most are not visible at the demo stage. They become visible and costly as:

- The user base grows and metric inconsistency becomes apparent across users
- Regulatory scrutiny requires audit trails that don't exist
- The question scope broadens to the complex calculations where SQL generation fails
- Data breaches or entitlement failures surface schema exposure risks
- The business requires metric change management and finds there is nothing to manage

At each stage, the natural response is to add complexity to the prompt, add guardrails around the LLM, add schema-filtering logic, add post-hoc validation. Each addition partially addresses one problem while the others persist. The system accumulates point fixes on a structurally weak foundation.

The teams that travel furthest down this path — adding prompt engineering, schema filtering, few-shot libraries, SQL validators, and output reconciliation layers — often end up having built, inadvertently, an approximation of a semantic layer. An expensive, brittle, prompt-dependent approximation of a semantic layer.

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

---

## Summary

| Concern | Text-to-SQL outcome |
|---------|-------------------|
| Metric consistency | ✗ — definitions inferred per query; no guarantee of consistency |
| Schema security | ✗ — physical schema exposed to the AI model and its provider |
| Audit trail | ✗ — no reproducible calculation record; regulatory audit impossible |
| Entitlement enforcement | ✗ — boundary is the database credential, not the user's role |
| Complex query accuracy | ✗ — degrades rapidly for regulated formulas, window functions, cross-domain queries |
| Metric change management | ✗ — no versioned definitions; no approval workflow; no lineage by definition version |
| Scope control | ✗ — system will attempt to answer any question, including ones it should not |
| Query cost governance | ✗ — LLM-generated SQL is unpredictable in execution cost |
| Multi-source federation | ✗ — limited to single SQL target; cannot span heterogeneous backends |
| Time to first demo | ✓ — hours to a working demo on a well-structured schema |
| Appropriate for regulated production use | ✗ |
