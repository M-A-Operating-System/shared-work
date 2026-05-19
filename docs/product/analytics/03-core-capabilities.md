# 3. Core Platform Capabilities

This chapter describes the Analytics Engine — a single MCP server — and the AI Chat Platform that calls it. The Analytics Engine validates structured queries, enforces entitlements, plans and executes against registered backends, and returns a display specification, structured results, and an optional governed narrative. The computation pipeline is entirely deterministic. The one AI step inside the Analytics Engine, the Narrative Synthesis Engine, runs after computation completes and is constrained strictly to summarising computed values — it cannot introduce metric values, comparisons, or interpretations not present in the result set. The AI Chat Platform hosts the conversational layer: it reads the metric catalogue from the Analytics Engine, translates natural language to structured parameters, and calls the Analytics Engine.

---

## Platform Architecture

The platform exposes its capability through three consumption modes. The first is direct API access, where a host-built custom analytics UI calls the MCP Capability Layer directly with a structured tool invocation, supplying a JWT for entitlement resolution and receiving a structured response containing a display specification and narrative. The second is conversational backend access, where the AI Chat Platform's conversation engine calls the Analytics Platform as a tool provider, mediating between a conversational UI component and the governed query pipeline. The third is agentic access, where scheduled agents, event monitors, and automated report pipelines call the MCP Capability Layer with machine-issued JWTs to perform periodic or event-driven analytical tasks without human-in-the-loop interaction. These three modes share a single entry point and a single governance pipeline; the consumption mode affects only the caller's interaction pattern, not the trust model applied.

```mermaid
flowchart TD
    subgraph org["Consuming Organisation"]
        ChatComp["&lt;ai-chat&gt; component\nconversational UI"]
        CustomUI["Custom analytics UI\nhost-built · renders JSON / SCL"]
        Agents["Agentic consumers\nscheduled agents · event monitors · report pipelines"]
    end

    subgraph aichat["AI Chat Platform"]
        ChatEngine["Conversation engine\nNL → structured intent\nContent rendering · Tool call routing\nAudit trail · Memory · Shared conversations"]
    end

    subgraph analytics["Analytics Engine"]
        MCP["MCP Capability Layer\nFastMCP · JWT validation"]
        SIL["Semantic Intent Layer\nParameter validation · SMR resolution · LQP generation"]
        RAPL["Role-Aware Projection Layer\nJWT claims · row predicates · column masks"]
        SEG["Semantic Execution Governance\nCost estimation · classification · circuit breakers"]
        FQP["Federated Query Planner\nApache Calcite + backend adapters"]
        VO["Visualisation Ontology\nSCL display spec · Vega-Lite v5"]
        NSE["Narrative Synthesis Engine\nClaude Haiku / Sonnet · post-computation\nanchored to result values · P6 governed"]
        LS[("Analytical Lineage Store")]
        Result(["MCP tool response\ndisplay_spec + data + narrative + result_id"])
    end

    vite2img["vite2img (optional)\nStandalone MCP render service · SCL → SVG / PNG\nRegistered directly with consumers — not part of Analytics Engine"]

    subgraph dcr["Data Context Repository"]
        SMR["Semantic Metrics Registry\nMetric definitions · dimensions · hierarchies\naggregation rules · governance · access policies"]
        DCS[("Semantic Data Context Store\nPre-existing · general-purpose common registry")]
        SMR -. backed by .-> DCS
    end

    subgraph backends["Execution Backends"]
        SQL["SQL Warehouse\nSnowflake · BigQuery · Databricks · Starburst"]
        ODA["OpenData API\nREST / OData"]
        GDA["Graph Data API\nNeo4j · Neptune / SPARQL"]
    end

    ChatComp -->|"JWT"| ChatEngine
    CustomUI -->|"JWT + structured MCP tool call"| MCP
    Agents -->|"agent JWT + structured MCP tool call"| MCP
    ChatEngine -->|"MCP resource reads + structured tool calls + user JWT"| MCP
    ChatEngine -->|"MCP tool call + user JWT"| vite2img
    MCP -->|"structured parameters"| SIL
    MCP -->|"JWT claims"| RAPL
    RAPL -->|"row predicates + column masks"| SIL
    SIL -->|"parameter validation + resolution"| SMR
    SIL -->|"Logical Query Plan"| SEG
    SEG -->|"approved LQP"| FQP
    SEG -->|"governance decision"| LS
    FQP -->|"physicalMapping lookup"| SMR
    FQP --> SQL & ODA & GDA
    FQP -->|"execution record"| LS
    FQP -->|"assembled result"| VO
    FQP -->|"assembled result"| NSE
    VO -->|"SCL display spec"| Result
    NSE -->|"narrative summary"| Result
```

The Analytics Engine is a single MCP server. It exposes three analytical tools (`run_analytics`, `list_operations`, `drilldown`) through a single MCP Capability Layer endpoint. The computation pipeline — SIL, RAPL, SEG, FQP — is entirely deterministic. The Narrative Synthesis Engine runs as a post-computation step: after the FQP assembles the result, the NSE makes a targeted call to a secondary language model to summarise the data in plain text; its prompt is constructed from the result set only and its output is validated against computed values before being returned.

The AI Chat Platform loads the operation catalogue from the Analytics Engine by calling `list_operations` — this is how the AI model discovers what operations, metrics, and dimensions are available. It translates the user's natural language question into explicit, structured parameters and calls `run_analytics` with the resolved `operation_id` and `params`. The Analytics Engine returns the display specification, structured data, and governed narrative; the AI Chat Platform renders the result.

The `vite2img` service is shown separately from the Analytics Platform boundary because it is an optional, independently registered MCP render service. Consumers that cannot natively render the SCL display specification — for example, an agentic pipeline that requires static image output — register `vite2img` directly and call it as a separate tool invocation using the `result_id` returned by the Analytics Platform. It is not part of the core analytics pipeline.

---

## Request Flow

The following sequence diagram traces a single conversational query end-to-end.

```mermaid
sequenceDiagram
    autonumber
    participant C as AI Chat Platform
    participant AE as Analytics Engine (MCP)
    participant SIL as Semantic Intent Layer
    participant RAPL as Role-Aware Projection Layer
    participant SMR as Semantic Metrics Registry
    participant SEG as Semantic Execution Governance
    participant FQP as Federated Query Planner
    participant BE as Execution Backend(s)
    participant VO as Visualisation Ontology
    participant NSE as Narrative Synthesis Engine
    participant LS as Analytical Lineage Store
    participant vite2img as vite2img

    C->>AE: list_operations (JWT)
    AE-->>C: operation catalogue (entitled subset)
    note over C: AI model translates NL → structured parameters
    C->>AE: run_analytics (operation_id + params + JWT)
    par
        AE->>SIL: structured parameters
    and
        AE->>RAPL: JWT claims
    end
    par
        SIL->>SMR: validate metric + dimension IDs
        SMR-->>SIL: definitions + aggregation rules
    and
        RAPL-->>SIL: row predicates + column masks
    end
    SIL->>SEG: Logical Query Plan (LQP)
    SEG->>LS: governance decision record
    SEG->>FQP: approved LQP
    FQP->>SMR: physicalMapping lookup
    SMR-->>FQP: physical source mapping
    FQP->>BE: sub-plan execution
    BE-->>FQP: raw result sets
    FQP->>LS: execution record
    par
        FQP->>VO: assembled result
        VO-->>AE: SCL display spec
    and
        FQP->>NSE: assembled result
        NSE-->>AE: narrative summary
    end
    AE-->>C: display_spec + data + narrative + result_id
    opt Consumer cannot natively render SCL spec
        C->>vite2img: render tool call (display_spec)
        vite2img-->>C: SVG / PNG
    end
```

The Analytics Engine receives structured parameters — not natural language — and returns structured results. The computation pipeline contains no AI; the Narrative Synthesis Engine runs after computation completes, in parallel with the Visualisation Ontology, making a targeted secondary model call constrained to the assembled result. The natural language translation (step 3) happens in the AI Chat Platform's reasoning loop, grounded by the operation catalogue loaded in step 1 via `list_operations`. The Analytical Lineage Store receives two writes per query: a governance decision record before execution and an execution record after — ensuring the audit trail is complete regardless of whether the query ultimately succeeds.

---

The following query is used as a running example throughout each section below.

---

## AI Chat Platform

The AI Chat Platform is the conversational layer through which users interact with the Analytics Engine. It hosts the AI model responsible for natural language translation, orchestrates calls to the Analytics Engine, and renders the assembled result to the user. Natural language translation — the only AI step the AI Chat Platform performs — happens here, grounded by the SMR metric catalogue. Narrative synthesis is performed inside the Analytics Engine as a secondary, post-computation step.

**Operation catalogue loading.** Before the AI model can translate a user's question into structured parameters, it needs to know what operations, metrics, and dimensions are available. The conversation engine calls `list_operations` on the Analytics Engine's MCP endpoint with the user's JWT. The response is the authenticated user's entitled operation catalogue — only operations the user can execute are returned, with their `operation_id`, display names, required parameters, supported metrics, supported dimensions, and execution profiles. This catalogue is injected into the model's context and serves as the controlled vocabulary for intent translation.

**NL → structured intent.** When a user asks an analytical question, the AI model maps the natural language to an `operation_id` and explicit `params` — drawn from the catalogue it loaded. It constructs a `run_analytics` call with the resolved operation and typed parameters. No natural language is sent to the Analytics Engine; it receives structured parameters only.

**Analytics Engine call.** The structured tool call is submitted to the Analytics Engine with the user's JWT forwarded unmodified. The Analytics Engine validates, plans, executes, and returns a structured result and SCL display specification. Entitlement enforcement, query planning, and execution are entirely the Analytics Engine's responsibility.

**Response assembly.** The conversation engine renders the SCL display specification inline. When narrative synthesis is enabled, the `narrative` object in the response contains the governed summary produced by the Analytics Engine's NSE — the conversation engine surfaces this directly. The `result_id` is retained for any follow-up `drilldown` call or lineage inspection.

### Example

The portfolio manager types their question. The conversation engine first loads the operation catalogue:

```
tools/call list_operations   (via Analytics Engine MCP, JWT forwarded)
→ returns: compare_portfolios, risk_breakdown, portfolio_return, ... (entitled subset)
          with operation_id, display names, required_params, supported_metrics, execution_profiles
```

The AI model reads "Show me portfolio returns versus benchmark for my equity portfolios this quarter" and, using the catalogue, resolves it to an operation and explicit parameters. It calls `run_analytics` with structured arguments — no natural language sent to the Analytics Engine:

```json
POST /v1/mcp
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "jsonrpc": "2.0",
  "id":      "req-8a3f2c",
  "method":  "tools/call",
  "params": {
    "name": "run_analytics",
    "arguments": {
      "operation_id": "compare_portfolios",
      "params": {
        "portfolio_ids": ["GLOB_EQ_OPP", "UK_CORE_INC", "ASIA_PAC_GRW", "EUR_BAL_INC"],
        "metrics":       ["portfolio_return", "benchmark_return"],
        "time_period":   "quarter_to_date",
        "filters":       [{ "field": "asset_class", "operator": "eq", "value": "EQUITY" }]
      }
    }
  }
}
```

When the Analytics Engine returns the structured result, display spec, and narrative summary, the conversation engine renders the grouped bar chart from the SCL specification and surfaces the governed narrative produced by the Analytics Engine's Narrative Synthesis Engine.

---

## Semantic Metrics Registry

> **Governing principles:** [P1 — Semantic abstraction](./01-platform-overview.md#design-principles) · [P3 — Deterministic metric resolution](./01-platform-overview.md#design-principles) · [P9 — Administrator sovereignty](./01-platform-overview.md#design-principles)

The Semantic Metrics Registry (SMR) is the governing catalogue of every analytical concept resolvable on the platform. Before any query can be planned or executed, every identifier in that query — metrics, dimensions, hierarchies — must be registered in the SMR. This is an architectural constraint, not a policy: the Semantic Intent Layer rejects any identifier not present in the SMR for the active tenant, and nothing is queryable that is not registered.

### Concept Types

The SMR is composed of three DCS document types:

| DCS document type | Description |
|---|---|
| **`analytical_metric`** | Metric definition — formula, aggregation, `data_affinity`, `physical_mapping`, `required_dimensions`, `cost_weight`, `classification_level`, `compliance_modes` |
| **`analytical_dimension`** | Dimension definition — `data_affinity`, `physical_mapping`, enumerated values or `hierarchical` flag, `hierarchy_levels` |
| **`analytical_operation`** | Operation catalogue entry — `execution_profile`, `required_params`, `supported_metrics`, `supported_dimensions`, `default_visualization` |

### Metric Definition Schema

Every metric in the SMR conforms to the following schema. This is the authoritative reference for metric registration and validation:

```json
{
  "id":          "portfolio_return",
  "version":     "2.1.0",
  "label":       "Portfolio Return",
  "description": "Total return of a portfolio over the specified period, net of fees, expressed as a percentage.",
  "formula":     "(end_market_value - start_market_value + cash_flows) / start_market_value",
  "unit":        "percentage",
  "aggregation": {
    "default":     "value_weighted_average",
    "allowed":     ["value_weighted_average", "equal_weighted_average", "sum"],
    "granularity": ["daily", "monthly", "quarterly", "annual", "since_inception"]
  },
  "dimensions": {
    "required": ["portfolio", "date"],
    "optional": ["asset_class", "currency", "benchmark"]
  },
  "data": {
    "domain":          "portfolio",
    "sub_domain":      "performance",
    "source_tables":   ["fact_portfolio_daily", "dim_portfolio"],
    "refresh_cadence": "daily",
    "latency_sla":     "T+1"
  },
  "governance": {
    "owner":          "head_of_performance_analytics",
    "steward":        "performance_analytics_team",
    "classification": "INTERNAL",
    "approved":       true,
    "approved_by":    "cdo_office",
    "approved_at":    "2025-11-15T09:00:00Z",
    "effective_from": "2025-11-15",
    "deprecated":     false
  },
  "lineage": {
    "upstream_metrics":   [],
    "upstream_sources":   ["positions_service", "pricing_service", "cash_flow_service"],
    "downstream_metrics": ["active_return", "information_ratio"]
  },
  "access": {
    "roles":  ["portfolio_manager", "risk_officer", "application_admin"],
    "public": false
  },
  "display": {
    "format":               "percentage",
    "decimals":             2,
    "sign_convention":      "positive_is_gain",
    "benchmark_comparison": true
  }
}
```

### Metric Schema Field Reference

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique metric identifier within the tenant. Lowercase, underscores. Used in MCP tool call parameters. |
| `version` | Yes | Semantic version. Increment on formula changes (major), aggregation changes (minor), documentation changes (patch). |
| `label` | Yes | Human-readable metric name. Used in UI, narrative synthesis, and chart axis labels. |
| `description` | Yes | Full prose definition. Must be unambiguous — this definition is injected into the AI model context. |
| `formula` | Yes | Business-logic formula expressed in the platform's formula language. Does not reference physical table columns directly — references other SMR metrics or canonical data source identifiers. |
| `unit` | Yes | Value unit. Accepted: `percentage`, `currency`, `basis_points`, `ratio`, `count`, `years`, `days`, `custom`. |
| `aggregation.default` | Yes | Default aggregation rule when the metric is rolled up across a dimension. |
| `aggregation.allowed` | Yes | All permitted aggregation rules for this metric. Requests using non-allowed rules are rejected at intent validation. |
| `aggregation.granularity` | Yes | Time granularities at which this metric is calculable. Requests at unsupported granularities are rejected. |
| `dimensions.required` | Yes | Dimensions that must be present in any query using this metric. Missing required dimensions cause a validation error. |
| `dimensions.optional` | No | Dimensions that may optionally be applied. |
| `data.domain` | Yes | The logical data domain this metric belongs to. Must match a domain registered in the SMR. |
| `data.refresh_cadence` | Yes | How frequently the underlying data is updated. Displayed in the lineage inspector and narrative synthesis. |
| `governance.owner` | Yes | Identifier of the metric owner. Must be a registered owner in the platform. |
| `governance.classification` | Yes | Data classification level. Used by the governance classification gate. |
| `governance.approved` | Yes | Whether this metric has been approved and is resolvable. Unapproved metrics are not returned by SMR queries. |
| `lineage.upstream_metrics` | No | Other SMR metrics this metric is derived from. Used for lineage graph construction. |
| `lineage.downstream_metrics` | No | SMR metrics that depend on this metric. Used for impact analysis when metric definitions change. |
| `access.roles` | Yes | Role IDs from the entitlement config that may query this metric. |

### Registry Governance Workflow

Metrics progress through a defined lifecycle from initial authorship to eventual retirement:

```
Draft → Proposed → In Review → Approved (Active) → Deprecated → Retired
```

| Transition | Trigger | Effect |
|---|---|---|
| Draft → Proposed | Metric owner submits a new definition | Visible in admin UI; not resolvable |
| Proposed → In Review | Application Admin opens for review | Downstream impact analysis runs automatically |
| In Review → Approved | Application Admin approves | Metric becomes resolvable from next refresh cycle |
| Approved → Deprecated | Owner or Admin marks deprecated | Metric resolves with a deprecation warning; removed from SMR browsing defaults |
| Deprecated → Retired | Admin retires after deprecation period | Metric no longer resolvable; lineage records preserved |

When a metric definition is proposed for change, the platform automatically runs an impact analysis covering downstream metrics, saved analytical sessions, and dashboards deriving results from the affected metric. Approval of a change with downstream impacts requires the Application Admin to acknowledge the impact report; that acknowledgement is recorded in the lineage store.

### Formula Language

The SMR formula language expresses metric computation logic in terms of other SMR metrics or canonical data source identifiers — never physical column names. This decouples metric definitions from backend schema changes.

```
# Simple ratio metric
active_return = portfolio_return - benchmark_return

# Information Ratio
information_ratio = active_return / tracking_error

# Weighted average with null protection
weighted_avg_duration = SAFE_DIVIDE(
  SUM(position_market_value * security_modified_duration),
  SUM(position_market_value)
)

# Conditional metric
issuer_concentration = SAFE_DIVIDE(
  SUM(position_market_value, FILTER(issuer = {{dim.issuer}})),
  SUM(position_market_value)
)

# Time-windowed metric
rolling_90d_return = CUMULATIVE_RETURN(daily_return, WINDOW(90, 'days'))
```

### SMR Authoring and Discovery

The SMR is backed by the DCS, which handles document creation, versioning, and the approval workflow natively. There are no custom MCP tools for metric authoring — administrators create, edit, and approve `analytical_metric`, `analytical_dimension`, and `analytical_operation` documents using the DCS's existing authoring capabilities.

**Discovery** — AI models and agents discover available operations by calling the `list_operations` MCP tool (defined in the MCP Capability Layer). `list_operations` returns operation IDs, display names, required parameters, supported metrics, supported dimensions, and execution profiles for all approved operations within the caller's entitlement scope. There are no `smr://` MCP resource URIs and no separate `list_metrics`, `get_metric_definition`, `propose_metric`, or `approve_metric` MCP tools.

The internal resolution calls made by the Semantic Intent Layer and Federated Query Planner query the DCS directly — there is no separate internal API. The SMR's governance workflow (Draft → Proposed → In Review → Approved → Deprecated → Retired) is managed through the DCS's existing authoring capabilities, not by custom MCP tools.

### Example

The SIL asks the SMR to resolve the `compare_portfolios` operation, then resolves `portfolio_return` and `benchmark_return` as `analytical_metric` documents. The SMR confirms both are approved for the `portfolio_manager` role and returns their definitions — including `data_affinity` (`portfolio`), `required_dimensions` (`portfolio_id`, `time_period`), and `aggregation` (`value_weighted_average`). `asset_class` resolves as an approved `analytical_dimension` document with an approved filter operator (`eq`). If either metric document were absent or not in `"status": "approved"` state, the SIL would return `METRIC_NOT_FOUND` and the pipeline would stop here.

---

## Semantic Intent Layer

> **Governing principles:** [P2 — Governance before execution](./01-platform-overview.md#design-principles) · [P10 — Deterministic computation, not generation](./01-platform-overview.md#design-principles)

The Semantic Intent Layer receives a structured MCP tool call — an `operation_id` and a `params` dict — and produces a validated, engine-agnostic Logical Query Plan (LQP). It is entirely deterministic: no AI model runs inside it. Its purpose is to: (1) resolve the operation from the SMR DCS catalogue, (2) validate `params` against the operation's `required_params` schema, (3) resolve metric IDs within `params` against `analytical_metric` documents, (4) apply role predicates from RAPL, (5) build the LQP. The output — the LQP — contains no backend references, no SQL, and no physical schema identifiers: only analytical operations expressed against SMR-registered concepts.

### Five-Stage Validation Pipeline

Every MCP tool call passes through five sequential validation stages:

```mermaid
flowchart TD
    S1["**Stage 1: Schema validation**\nJSON parameters conform to tool schema\nRequired fields present and typed"]
    S2["**Stage 2: SMR resolution**\nResolve operation_id → analytical_operation document\nValidate params against operation required_params schema\nResolve metric IDs → analytical_metric documents\nResolve dimension IDs → analytical_dimension documents\nReject unregistered or unapproved IDs"]
    S3["**Stage 3: Role-Aware Projection**\nFilter metric set to entitled scope\nFilter dimension set to entitled scope\nInject row predicates from role config\nApply column masks · Reject entitlement violations"]
    S4["**Stage 4: Semantic validation**\nRequired dimensions present per metric\nAggregation rules compatible\nTime granularity compatible per metric\nFilter predicates reference valid fields"]
    S5["**Stage 5: LQP generation**\nProduce engine-agnostic DAG\nAssign data affinity hints per metric\nEstimate result cardinality and execution cost"]
    LQP(["Logical Query Plan (LQP)"])

    S1 --> S2 --> S3 --> S4 --> S5 --> LQP
```

### Intent Parameter Schema

All `run_analytics` calls use the same outer envelope. The `params` dict is operation-specific — its valid keys are defined by the `required_params` and `optional_params` fields on the `analytical_operation` document in the SMR DCS catalogue.

| Parameter | Type | Description |
|---|---|---|
| `operation_id` | `string` | SMR operation ID — resolved from the `analytical_operation` catalogue via `list_operations`. |
| `params` | `object` | Operation-specific parameters. Validated by the SIL against the operation's `required_params` schema. May include `metrics` (SMR metric IDs), `dimensions`, `time_period`, `filters`, and operation-specific fields. |

**Example `params` for the `risk_breakdown` operation:**

```json
{
  "operation_id": "risk_breakdown",
  "params": {
    "portfolio_id":   "GLOB_EQ_OPP",
    "metrics":        ["var_95", "tracking_error"],
    "attribution_by": "asset_class",
    "as_of_date":     "2026-05-14"
  }
}
```

The SIL validates that `portfolio_id`, `metrics`, `attribution_by`, and `as_of_date` are all present (per the operation's `required_params`), resolves each metric ID in `params.metrics` against `analytical_metric` documents, and rejects any unregistered or unapproved ID before LQP generation.

### MCP Input to Resolved Intent: Example

The following illustrates how raw MCP tool call parameters are transformed through SMR resolution and role projection into the enriched input that enters the LQP generator:

```json
// MCP tool call input (what the AI produces)
{
  "operation_id": "compare_portfolios",
  "params": {
    "portfolio_ids": ["GLOB_EQ_OPP", "UK_CORE_INC"],
    "metrics":       ["portfolio_return", "tracking_error"],
    "time_period":   "quarter_to_date",
    "filters": [
      { "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }
    ]
  }
}
```

```json
// After SMR resolution and role projection — input to LQP generator
{
  "resolved_metrics": [
    {
      "id":            "portfolio_return",
      "version":       "2.1.0",
      "aggregation":   "value_weighted_average",
      "data_affinity": "portfolio",
      "required_dims": ["portfolio"]
    },
    {
      "id":            "tracking_error",
      "version":       "1.3.0",
      "aggregation":   "value_weighted_average",
      "data_affinity": "risk_metrics",
      "required_dims": ["portfolio"]
    }
  ],
  "dimensions": [
    { "id": "portfolio",   "entitled": true },
    { "id": "asset_class", "entitled": true }
  ],
  "row_predicates": [
    "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"
  ],
  "filters": [
    { "dimension": "asset_class", "operator": "eq", "value": "EQUITY" }
  ],
  "time": { "type": "period", "period": "quarter_to_date", "as_of_date": "2026-05-14" },
  "order_by": { "field": "tracking_error", "direction": "DESC" }
}
```

The resolved form carries metric versions, aggregation rules, and entitlement-derived row predicates. These are embedded in the LQP, which is then stored verbatim in the lineage record, linking the original tool call to the physical execution result.

### Example

The MCP Capability Layer forwards the natural language query to the SIL. The SIL sends the query text plus the user's available metric catalogue to Claude Sonnet, which extracts the structured intent:

```json
{
  "intent_id":  "int-20260518-093241-pk7m",
  "tool":       "analyse_metric",
  "metrics":    ["portfolio_return", "benchmark_return"],
  "dimensions": ["portfolio_id"],
  "filters": [
    { "field": "asset_class", "operator": "eq", "value": "EQUITY" }
  ],
  "time_period": { "granularity": "quarterly", "anchor": "current" },
  "sort":        { "field": "portfolio_return", "direction": "desc" },
  "confidence":  0.97,
  "unresolved":  []
}
```

After SMR resolution and role projection (Stage 3), the SIL produces the Logical Query Plan:

```json
{
  "lqp_id":    "lqp-20260518-093243-r9xq",
  "intent_id": "int-20260518-093241-pk7m",
  "tenant_id": "acme-wealth",
  "nodes": [
    { "id": "n1", "type": "metric_scan",
      "metrics": ["portfolio_return", "benchmark_return"],
      "dimensions": ["portfolio_id"],
      "time_period": { "granularity": "quarterly", "anchor": "current" } },
    { "id": "n2", "type": "filter", "input": "n1",
      "predicate": { "field": "asset_class", "operator": "eq", "value": "EQUITY" } },
    { "id": "n3", "type": "filter", "input": "n2",
      "predicate": { "field": "portfolio_id", "operator": "in",
                     "values": ["GLOB_EQ_OPP", "UK_CORE_INC", "ASIA_PAC_GRW", "EUR_BAL_INC"] } },
    { "id": "n4", "type": "sort", "input": "n3",
      "field": "portfolio_return", "direction": "desc" }
  ],
  "output_node":             "n4",
  "estimated_cost":          620,
  "classification_required": "INTERNAL"
}
```

Node `n3` is the RAPL row predicate — part of the plan, not a post-execution filter.

---

## Role-Aware Projection Layer

> **Governing principles:** [P5 — Role-aware by default](./01-platform-overview.md#design-principles) · [P1 — Semantic abstraction](./01-platform-overview.md#design-principles)

The Role-Aware Projection Layer applies the authenticated user's entitlement model to the resolved analytical intent before any query plan is compiled. It is the semantic-layer enforcement of data access controls — operating above physical execution, before any query reaches a backend. Projection is not optional and not bypassable: every request, whether from a human user or an AI orchestrator, passes through it.

### Restriction Types

The projection layer applies four categories of restriction:

| Restriction type | Description | Applied at |
|---|---|---|
| **Metric access filter** | Removes metrics from the resolved intent that the user's role is not entitled to query | Intent validation — Stage 3 |
| **Dimension access filter** | Removes dimensions the user is not entitled to slice by | Intent validation — Stage 3 |
| **Row predicate injection** | Injects SQL-like predicates that restrict which data rows the user can access | FQP physical query generation |
| **Column mask application** | Replaces or nullifies column values the user is not permitted to see in the assembled result | FQP result assembly |

### Projection Lifecycle

```mermaid
flowchart TD
    START(["Authenticated request arrives with JWT"])
    S1["**1. JWT validation**\nsignature · expiry · tenant claim"]
    S2["**2. Role claim extraction**\nroleClaimField: 'analytics_roles'\nextracted roles: ['portfolio_manager']"]
    S3["**3. Entitlement profile construction**\nMerge all role definitions for the user's roles\nProduce: metric_access_set, dimension_access_set,\nrow_predicates[], column_masks[]"]
    S4["**4. Metric access filter**\nIntersect requested metrics with metric_access_set\nUnentitled metrics → METRIC_NOT_ENTITLED error"]
    S5["**5. Dimension access filter**\nIntersect requested dimensions with dimension_access_set\nUnentitled dimensions → DIMENSION_NOT_ENTITLED error"]
    S6["**6. Row predicate construction**\nResolve predicate templates: user.managed_portfolios\nPredicates stored in LQP for FQP injection at execution time"]
    S7["**7. Column mask registration**\nRegister masked columns in LQP metadata\nFQP applies masks during result assembly"]
    S8(["**8. Projected LQP produced**\n→ proceeds to governance validation"])

    START --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8
```

### Multi-Role Merging

Users may hold multiple roles simultaneously. The projection layer merges role entitlements using union semantics for metric and dimension access — a user entitled to a metric via any role may query it. Row predicates and column masks use the inverse strategy: all predicates must be satisfied (most restrictive wins), and a column masked by any role is masked for the user.

| Entitlement type | Merge strategy | Rationale |
|---|---|---|
| Metric access | Union | A user entitled to a metric via any role may query it |
| Dimension access | Union | A user entitled to a dimension via any role may use it |
| Row predicates | Intersection (AND) | All predicates must be satisfied — most restrictive wins |
| Column masks | Union | A column masked by any role is masked for the user |

### Row Predicate Template Resolution

Row predicate templates reference JWT claim values using `{{user.claim_name}}` syntax, resolved at query time from the authenticated user's current JWT:

**Predicate template (in entitlement config):**
```
portfolio_id IN ({{user.managed_portfolios}})
```

**JWT claim:**
```json
{ "managed_portfolios": ["GLOB_EQ_OPP", "UK_CORE_INC", "STRAT_BAL"] }
```

**Resolved predicate (injected into FQP physical queries):**
```sql
portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')
```

### Column Masking

Column masks are applied during FQP result assembly, after sub-results return from execution backends but before the result leaves the platform. Three masking modes are supported:

| Mode | Masked column representation |
|---|---|
| `null_replacement` | Column value replaced with `null` |
| `redacted_label` | Column value replaced with the string `"[REDACTED]"` |
| `excluded` | Column omitted entirely from the result schema |

**Before masking (compliance analyst role with `column_masks: ["client_name", "account_number"]`):**
```json
[{ "portfolio_id": "GLOB_EQ_OPP", "client_name": "Blackwood Family Trust", "account_number": "WM-00412", "lcr": 1.24 }]
```

**After masking (`redacted_label` mode):**
```json
[{ "portfolio_id": "GLOB_EQ_OPP", "client_name": "[REDACTED]", "account_number": "[REDACTED]", "lcr": 1.24 }]
```

### Entitlement Audit

Every projection decision — including blocked metrics, applied row predicates, and active column masks — is recorded in the lineage store as part of the execution record. The projection record captures the roles active at query time, which metrics were requested, which were projected through, which were blocked and why, and which predicates were injected. This record provides the evidentiary chain required for regulatory entitlement audits.

### Example

The RAPL reads the `portfolio_scope` claim from the JWT and resolves it against the `portfolio_manager` role's predicate template (`portfolio_id IN ({{user.portfolio_scope}})`):

```json
{
  "row_predicates": [
    { "dimension": "portfolio_id", "operator": "in",
      "values": ["GLOB_EQ_OPP", "UK_CORE_INC", "ASIA_PAC_GRW", "EUR_BAL_INC"] }
  ],
  "column_masks":           [],
  "classification_ceiling": "INTERNAL",
  "projection_basis":       "jwt_claim:portfolio_scope"
}
```

No column masks apply — the `portfolio_manager` role has no masking rules for performance metrics. The row predicate is injected into the LQP as node `n3` (see section 3.2 example). Any portfolio outside the four listed IDs is excluded at the physical query level.

---

## Semantic Execution Governance

> **Governing principles:** [P2 — Governance before execution](./01-platform-overview.md#design-principles) · [P8 — Explainability at every layer](./01-platform-overview.md#design-principles) · [P9 — Administrator sovereignty](./01-platform-overview.md#design-principles)

The Semantic Execution Governance (SEG) layer applies a suite of circuit breakers, cost controls, complexity limits, and compliance classification checks to every query before it is released to the Federated Query Planner. It is the final gate before physical execution. Governance applies to every query without exception — there is no privileged user, trusted agent, or internal path that bypasses SEG checks.

### Governance Pipeline

```mermaid
flowchart TD
    START(["Validated LQP\npost role-aware projection"])
    S1["**1. Cost estimation**\nEstimate execution cost units from LQP metadata\ncardinality estimate × engine cost tier × complexity factor"]
    S2["**2. Cost circuit breaker**\nCompare estimated cost to maxQueryCostUnits\nBLOCK if exceeded → user prompted to narrow scope"]
    S3["**3. Complexity limit check**\nEvaluate LQP node count, join depth, sub-plan count\nBLOCK if exceeds complexity threshold"]
    S4["**4. Classification gate**\nRetrieve data.classification from SMR per metric\nBLOCK if any metric classification is in blocked list"]
    S5["**5. Regulatory compliance mode check**\nIf complianceMode set: apply compliance-specific rules\ne.g. MiFID II: log all queries involving client-related metrics"]
    S6["**6. Concurrency limit check**\nCount active queries for this user\nBLOCK with wait if exceeds maxConcurrentQueries"]
    S7["**7. Timeout budget assignment**\nAssign queryTimeoutSeconds to FQP execution context"]
    S8(["**8. Governance approval record written**\nGovernance event written before FQP is invoked\n→ Release to FQP"])

    START --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8
```

### Cost Estimation Model

Cost units are estimated from LQP metadata before any backend is contacted:

| Factor | Contribution |
|---|---|
| Number of metrics | `metric_count × 50` base units |
| Engine cost tier per sub-plan | `minimal: 10`, `low: 50`, `standard: 100`, `high: 300`, `unrestricted: 0` |
| Dimension cardinality | `low: ×1.0`, `medium: ×1.5`, `high: ×3.0`, `unbounded: ×5.0` |
| Time period scope | `single_day: ×1.0`, `quarter: ×2.0`, `year: ×4.0`, `since_inception: ×8.0` |
| Number of sub-plans (federation) | `+100 per additional sub-plan` |
| Materialised view match | `−800` (pre-computed result) |
| Cache hit (estimated) | `−900` (full cache hit expected) |

**Worked example — `portfolio_return, tracking_error BY portfolio, asset_class FOR YEAR_TO_DATE`:**

```
portfolio_return:        50 (metric base)
tracking_error:          50 (metric base)
SQL warehouse backend:  100 (standard cost tier)
semantic layer backend:  50 (low cost tier)
asset_class:            1.5× cardinality multiplier (medium)
YEAR_TO_DATE:           4.0× period multiplier
2 sub-plans:            100 (federation overhead)
—————————————————————————————
Base: (50+50) × 1.5 × 4.0 = 600
Engines: 100+50 = 150
Federation: 100
Total estimate: 850 cost units
```

Against a `maxQueryCostUnits: 1000` limit, this query is approved. Against a `500` limit, it is blocked and the user receives structured suggestions to narrow scope (reduce time period, reduce metric count, or add a filter).

### Compliance Modes

Named compliance profiles pre-configure governance behaviour for specific regulatory environments:

**MiFID II mode** (`"complianceMode": "mifid2"`)

| Additional rule | Implementation |
|---|---|
| All queries involving client-identifiable data must be logged with business justification | Prompt user for business justification before queries on `client_name`, `account_number`, or similar PII-adjacent dimensions |
| Best execution metrics must be queried with explicit timeframe | Validation error if `date` dimension not specified for best-execution metrics |
| Transaction reporting queries must generate a TRACE record | Additional lineage record written to `analytics.mifid2_trace` table |

**Basel III/IV mode** (`"complianceMode": "basel3"`)

| Additional rule | Implementation |
|---|---|
| Capital ratio queries must include entity identifier | Required dimension: `entity` for all regulatory capital metrics |
| LCR/NSFR queries generate a daily snapshot record | Regulatory metric queries trigger a snapshot write to `analytics.regulatory_snapshots` |
| Queries on stress scenario data classified as RESTRICTED | Stress scenario metrics automatically classified at RESTRICTED level regardless of user role |

**SEC Regulation BI mode** (`"complianceMode": "sec_reg_bi"`)

| Additional rule | Implementation |
|---|---|
| Narrative synthesis prohibited from generating investment recommendations | Additional narrative synthesis constraint injected into prompt |
| Client analytics require suitability record reference | Advisory queries require `suitability_record_id` parameter before execution |

### Timeout and Partial Result Handling

| Scenario | Behaviour |
|---|---|
| All sub-plans complete within timeout | Normal result assembly and return |
| One sub-plan times out, others complete | Partial result assembly — missing metrics represented as null with `timeout` provenance marker; user notified |
| All sub-plans time out | Query failed — error returned to user; governance event written with `timeout` status |
| Engine cancellation on timeout | FQP sends cancellation signal to timed-out engine (if engine supports cancellation) |

### Example

SEG evaluates the LQP (`lqp-20260518-093243-r9xq`) against the `acme-wealth` governance configuration:

| Check | Value | Limit | Result |
|---|---|---|---|
| Estimated cost | 620 | 1,000 | Pass |
| Metrics per query | 2 | 10 | Pass |
| Dimensions | 1 | 5 | Pass |
| Data classification | INTERNAL | INTERNAL ceiling | Pass |
| Compliance mode | none required | — | Pass |

All checks pass. SEG writes a governance decision record to the lineage store — before the FQP is invoked — and releases the LQP to the FQP:

```json
{
  "lqp_id":    "lqp-20260518-093243-r9xq",
  "decision":  "approved",
  "timestamp": "2026-05-18T09:32:44Z",
  "checks":    ["cost_ceiling", "metric_count", "dimension_count", "classification_gate"],
  "result":    "all_passed"
}
```

---

## Federated Query Planner

> **Governing principles:** [P1 — Semantic abstraction](./01-platform-overview.md#design-principles) · [P4 — Complete analytical lineage](./01-platform-overview.md#design-principles) · [P10 — Deterministic computation, not generation](./01-platform-overview.md#design-principles)

The Federated Query Planner (FQP) is the only component in the platform that has knowledge of physical execution backends. No other component — not the Semantic Intent Layer, not the AI model, not the MCP Capability Layer — has access to backend connection details or physical schema information. The FQP receives a validated, governance-approved LQP, decomposes it into backend-specific sub-plans, routes those sub-plans to registered execution backends in parallel, assembles the results, and writes a complete execution record to the lineage store.

### Nine-Step FQP Pipeline

```mermaid
flowchart TD
    S1["**1. LQP Reception & Governance Validation**\nvalidates cost estimate · complexity · classification"]
    S2["**2. Cache Check**\nexact match and approximate match on LQP signature"]
    CACHED(["Cached result returned"])
    S3["**3. Sub-plan Decomposition**\nsplit LQP into sub-plans by data affinity"]
    S4["**4. Backend Selection & Routing**\nmatch sub-plans to backends by affinity + capability"]
    S5["**5. Physical Query Generation**\ntranslate sub-plans to engine-specific query dialect"]
    S6["**6. Parallel Execution & Coordination**\nexecute sub-plans concurrently · handle timeouts"]
    S7["**7. Result Assembly & Reconciliation**\njoin sub-results by shared dimensions · apply column masks"]
    S8["**8. Result Caching & Materialisation**\nwrite result to cache · update materialisation index"]
    S9["**9. Lineage Record Writing**\nwrite complete execution trace to lineage store"]
    RESULT(["Assembled result + lineage record"])

    S1 --> S2
    S2 -->|cache hit| CACHED
    S2 -->|cache miss| S3
    S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> RESULT
```

### Sub-Plan Decomposition

The FQP decomposes an LQP into sub-plans by data affinity — the logical data domain declared by each metric in its SMR definition. Metrics with the same affinity are grouped into a single sub-plan; metrics with different affinities produce separate sub-plans that execute in parallel. Shared dimensions across sub-plans become the join keys for result assembly.

For a query requesting `portfolio_return` (affinity: `portfolio`) and `var_95` (affinity: `risk_metrics`), the FQP produces two sub-plans routed to different engines, executes them concurrently, and joins the results in memory on `portfolio_id` and `date`.

### Backend Adapter Table

| Backend type | Protocol | Typical use |
|---|---|---|
| SQL warehouse | JDBC/ODBC, SQL dialect | Primary performance and position data |
| Semantic layer | REST/JSON query API | Pre-modelled metrics via dbt Semantic Layer or equivalent |
| OpenData API | OData v4 REST | Reference data and third-party feeds |
| Graph Data API | GraphQL or REST | Relationship and counterparty data |
| OLAP engine | REST/JSON cube query | Pre-aggregated dimensional data |
| Custom adapter | Platform adapter SDK | Proprietary or specialised data sources |

When multiple engines are registered for the same data affinity, the FQP selects the highest-priority available engine. If the highest-priority engine is unavailable or its p95 latency exceeds twice its baseline over a rolling one-hour window, the FQP automatically routes to the next registered engine for that affinity.

### Caching

The FQP maintains a result cache keyed by the LQP signature — a deterministic SHA-256 hash of the metric IDs and versions, dimension IDs, filter predicates, time expression, entitlement hash, and tenant ID.

| Cache property | Specification |
|---|---|
| Cache key | SHA-256 of (metric IDs + versions, dimension IDs, filter predicates, time expression, entitlement hash, tenant ID) |
| Cache TTL | Configurable per `data.refresh_cadence` in the metric definition. Default: 3600 seconds. |
| Cache invalidation | On metric definition version change; on execution backend data refresh signal; on explicit cache clear via Admin API |
| Cache scope | Per-tenant. Results from one tenant are never served to another. |
| Cache storage | Platform-managed result cache. Results over 10 MB bypass the cache and are streamed directly. |
| Cache hit disclosure | Cache hits are disclosed in the lineage record and optionally surfaced to the user as a "Result from cache (data as of [timestamp])" indicator. |

### Adaptive Planning

The FQP adapts routing decisions based on observed execution performance. It tracks p50/p95 latency per engine per data affinity over a rolling one-hour window, automatically falls back to the next available engine if performance degrades, and calibrates cost unit estimates based on observed execution data from completed queries. If a sub-plan engine returns a partial result due to timeout, the FQP logs this in the lineage record and surfaces a warning to the user alongside the partial result.

### Example

Both `portfolio_return` and `benchmark_return` have `data_affinity: "portfolio"`, so the FQP routes a single sub-plan to the primary SQL warehouse:

```sql
SELECT
    p.portfolio_id,
    AVG(f.portfolio_return)  AS portfolio_return,
    AVG(f.benchmark_return)  AS benchmark_return
FROM fact_portfolio_daily f
JOIN dim_portfolio p ON f.portfolio_id = p.portfolio_id
WHERE p.asset_class  = 'EQUITY'
  AND f.portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'ASIA_PAC_GRW', 'EUR_BAL_INC')
  AND f.date         BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY p.portfolio_id
ORDER BY portfolio_return DESC
```

Assembled result:

```json
{
  "result_id":      "res-20260518-093247-wk4n",
  "latency_ms":    1187,
  "backends_used": ["primary-warehouse"],
  "rows": [
    { "portfolio_id": "GLOB_EQ_OPP",  "portfolio_return": 4.21, "benchmark_return": 3.85 },
    { "portfolio_id": "ASIA_PAC_GRW", "portfolio_return": 3.67, "benchmark_return": 3.90 },
    { "portfolio_id": "UK_CORE_INC",  "portfolio_return": 2.87, "benchmark_return": 2.54 },
    { "portfolio_id": "EUR_BAL_INC",  "portfolio_return": 1.93, "benchmark_return": 2.31 }
  ]
}
```

The FQP writes an execution record to the lineage store and passes the assembled result in parallel to the Visualisation Ontology and Narrative Synthesis Engine.

---

## Visualisation Ontology

> **Governing principles:** [P7 — Deterministic visualisation](./01-platform-overview.md#design-principles)

The Visualisation Ontology is the governing schema that maps result characteristics and analytical intent patterns to specific, parameterised chart contracts. It exists to make chart selection deterministic: the same analytical pattern produces the same chart type across all users, sessions, and AI model versions, regardless of how the question was phrased. The AI model does not select chart types. Intent signals from the query are treated as inputs to the ontology evaluation algorithm, but the ontology makes the final binding decision.

### Intent Pattern Taxonomy

Every analytical result is classified into one of seven intent patterns:

| Intent pattern | Description | Typical trigger phrases |
|---|---|---|
| `COMPARISON` | Comparing a metric across discrete categories | "compare", "by", "across", "ranked by", "top N" |
| `TREND` | Showing how a metric changes over time | "over time", "trend", "history", "30-day", "since" |
| `DISTRIBUTION` | Showing the spread or concentration of a metric | "distribution", "breakdown", "composition", "concentration" |
| `THRESHOLD` | Comparing a metric against a limit or benchmark | "exceeding", "within limit", "versus benchmark", "breach" |
| `ATTRIBUTION` | Decomposing a metric into contributing factors | "attribution", "contribution", "drivers", "breakdown by" |
| `RELATIONSHIP` | Showing correlation or dependency between metrics | "versus", "correlation", "scatter", "risk-return" |
| `COMPOSITION` | Showing part-to-whole relationships | "proportion", "weight", "allocation", "share" |

### Chart Contract Table

| Contract name | Intent patterns matched | Chart type | Key axis assignments | Interaction semantics |
|---|---|---|---|---|
| `BAR_MULTI_SERIES_COMPARISON` | `COMPARISON` | Bar | X: primary categorical dimension (sorted by primary metric DESC); Y: metric value; Colour: metric series or secondary dimension | Click: drilldown; Hover: tooltip; Selection: multi-point |
| `LINE_TIME_SERIES_TREND` | `TREND` | Line | X: temporal dimension; Y: metric value; Colour: metric series; Reference line: injected if `compare_to` present | Hover: crosshair tooltip; Click data point: surface lineage; Brush: zoom X-axis |
| `HEATMAP_THRESHOLD_MATRIX` | `THRESHOLD` | Heatmap | X: first categorical dimension; Y: second categorical dimension; Colour: metric as % of threshold (diverging scale, midpoint at 100% of limit) | Click cell: drilldown into dimension intersection |
| `TREEMAP_COMPOSITION` | `COMPOSITION`, `DISTRIBUTION` | Treemap | Area: proportional to metric value; Colour: secondary metric (diverging scale); Label: dimension value + metric value | Click tile: drilldown to next hierarchy level; Hover: tooltip with all metrics |
| `WATERFALL_ATTRIBUTION` | `ATTRIBUTION` | Waterfall | X: contribution dimension; Y: contribution value (positive/negative); Colour: positive (green), negative (red), total (grey) | Hover: contribution value and percentage |
| `SCATTER_RISK_RETURN` | `RELATIONSHIP` | Scatter | X: first metric (conventionally risk); Y: second metric (conventionally return); Colour: categorical dimension; Size: optional third metric | Hover: all metric values; Reference lines: quadrant boundaries from benchmark values if present |
| `TABLE_GOVERNED` | Fallback (any) | Table | All result columns; column labels from SMR; inline sparklines for temporal metrics | Column sorting; column filtering; export to CSV and JSON |

### Priority-Ordered Evaluation Algorithm

The ontology evaluator receives the LQP, intent pattern classification, and result schema. It evaluates contracts in order of specificity and returns the highest-scoring match:

```python
def evaluate_ontology(lqp, intent_pattern, result_schema, allowed_charts):
    candidates = []
    for contract in ONTOLOGY_CONTRACTS:
        if not all(c in allowed_charts for c in [contract.chart_type]):
            continue
        score = contract.match_score(lqp, intent_pattern, result_schema)
        if score > 0:
            candidates.append((score, contract))
    candidates.sort(key=lambda x: x[0], reverse=True)
    if candidates:
        return candidates[0][1]
    else:
        return TABLE_GOVERNED  # deterministic fallback
```

The `TABLE_GOVERNED` contract is the unconditional fallback. It is always eligible and always matches — ensuring that every query, regardless of result shape, receives a valid `display_spec`.

### Override Mechanism

Power Analysts may override the ontology's chart selection for a single result by expressing an explicit chart type preference in their query. Overrides are subject to the requested chart type being in the tenant's `allowedChartTypes` list and the result schema being compatible with the requested chart type. Incompatible overrides are rejected with an explanation. All overrides are logged in the lineage record as analyst-requested deviations from the governing ontology.

### Example

The ontology evaluator classifies the result: two metrics across four named entities, with a natural comparison relationship between return and benchmark. This matches the `COMPARISON` pattern. The highest-scoring contract is `BAR_MULTI_SERIES_COMPARISON` — a grouped bar chart with portfolios on the X axis and return values on Y, coloured by metric series.

The ontology produces the following SCL display specification:

```json
{
  "type": "chart",
  "mark": "bar",
  "data": { "name": "result" },
  "transform": [
    { "fold": ["portfolio_return", "benchmark_return"], "as": ["metric", "value"] }
  ],
  "encoding": {
    "x":       { "field": "portfolio_id", "type": "nominal",      "title": "Portfolio"   },
    "y":       { "field": "value",        "type": "quantitative", "title": "Return (%)", "axis": { "format": ".2f" } },
    "color":   { "field": "metric",       "type": "nominal",      "title": "Metric",
                 "scale": { "domain": ["portfolio_return", "benchmark_return"],
                            "range":  ["#0057B8", "#A8C8F0"] } },
    "xOffset": { "field": "metric", "type": "nominal" }
  },
  "title": "Portfolio Return vs Benchmark — Q2 2026"
}
```

---

## Narrative Synthesis Engine

> **Governing principles:** [P6 — Governed narrative](./01-platform-overview.md#design-principles) · [P10 — Deterministic computation, not generation](./01-platform-overview.md#design-principles)

The Narrative Synthesis Engine (NSE) is a secondary AI component inside the Analytics Engine. It runs after the computation pipeline completes — after the FQP has assembled the result and the Visualisation Ontology has selected the chart contract — making a single, tightly-scoped call to a language model with one purpose: summarise the structured result in plain language, anchored strictly to the computed values.

The NSE is not a general-purpose AI model with access to the query, the user's intent, or the SMR. Its prompt is constructed entirely from the assembled result: metric labels, row values, units, and dimension names. It is told what the data shows; it is not told what the user asked. This constraint is intentional — it prevents the narrative from interpreting, recommending, or inferring beyond what was computed.

### Anchoring and Validation

The NSE produces two output fields:

| Field | Description |
|---|---|
| `narrative.lead` | A single sentence summarising the top-level finding (e.g. "3 of your 4 equity portfolios outperformed their benchmark this quarter.") |
| `narrative.detail` | Two to four sentences covering the most significant data points, one per dimension value or notable comparison |
| `narrative.anchoredTo` | An array of dimension value identifiers from the result that the narrative references — used for post-generation validation |

After generation, the NSE runs a validation pass: every numeric value in the narrative must be present in the result set. If any value in the narrative cannot be matched to a result row, the narrative is rejected and a single regeneration is attempted. If the second attempt also fails validation, the `narrative` field is omitted from the response and the failure is recorded in the lineage record. This constraint enforces P6 (governed narrative) at the component level.

### Model Selection

| Query type | Model | Rationale |
|---|---|---|
| Standard queries (≤ 5 metrics, ≤ 3 dimensions) | Claude Haiku | Low latency; sufficient for concise, anchored summaries |
| Complex queries (attribution, multi-portfolio, regulatory) | Claude Sonnet | Richer result structure requires more precise prose |

The model used is recorded in `narrative_status` in the lineage record.

### Feature Flag

Narrative synthesis is controlled by the `features.narrativeSynthesis` tenant configuration flag. When disabled, the NSE is not invoked and no `narrative` field is included in the response. The default is enabled. Disabling narrative synthesis has no effect on computation, lineage, or display spec generation.

### Example

The portfolio manager's query returns four rows. The NSE receives the assembled result and produces:

```json
{
  "narrative": {
    "lead":       "3 of your 4 equity portfolios outperformed their benchmark this quarter.",
    "detail":     "Global Equity Opportunities returned 4.21% against a benchmark of 3.85%. UK Core Income returned 2.87% against its benchmark of 2.54%. Asia Pacific Growth underperformed at 3.67% versus a benchmark of 3.90%.",
    "anchoredTo": ["GLOB_EQ_OPP", "UK_CORE_INC", "ASIA_PAC_GRW"]
  }
}
```

Post-generation validation confirms every numeric value (4.21, 3.85, 2.87, 2.54, 3.67, 3.90) is present in the assembled result rows. Validation passes. The narrative is included in the MCP response alongside `display_spec` and `data`.

---

## Analytical Output Format

The Analytics Engine is headless: it produces no rendered output. Every successful analytical request returns a structured MCP tool response. When narrative synthesis is enabled (`features.narrativeSynthesis: true`), the response contains four elements; when disabled, three.

### Output Elements

| Element | Field | Always present | Description |
|---|---|---|---|
| Display specification | `display_spec` | Yes | A Semantic Charting Language (SCL) JSON object — either a chart or table specification. Consumers render from this. |
| Structured result | `data` | Yes | The computed rows and schema — metric values, dimension values, and units. |
| Governed narrative | `narrative` | No (feature-flag controlled) | A governed summary produced by the NSE — `lead` (one sentence), `detail` (2–4 sentences), `anchoredTo` (result row references). Present when `features.narrativeSynthesis` is enabled. |
| Lineage reference | `result_id` + `lineage_url` | Yes | A unique result identifier and the URL of the full lineage record |

### Full MCP Response Structure

```json
{
  "result_id":   "res_20260514_093247_a1b2c3",
  "lineage_url": "https://api.analytics-platform.io/v1/lineage/res_20260514_093247_a1b2c3",
  "display_spec": {
    "type": "chart",
    "mark": "bar",
    ...
  },
  "data": {
    "schema": [ ... ],
    "rows":   [ ... ]
  },
  "narrative": {
    "lead":       "3 of your 4 equity portfolios outperformed their benchmark this quarter.",
    "detail":     "Global Equity Opportunities returned 4.21% against a benchmark of 3.85%. UK Core Income returned 2.87% against its benchmark of 2.54%. Asia Pacific Growth underperformed at 3.67% versus a benchmark of 3.90%.",
    "anchoredTo": ["GLOB_EQ_OPP", "UK_CORE_INC", "ASIA_PAC_GRW"]
  },
  "meta": {
    "latencyMs":    1285,
    "cacheHit":     false,
    "rowCount":     4,
    "backendsUsed": ["primary-warehouse"],
    "costUnits":    500
  }
}
```

### Semantic Charting Language (SCL)

SCL is the JSON specification language used for the `display_spec` field. Two types share a consistent discriminated envelope.

**Chart specification** (`type: "chart"`) — produced when a chart contract matches:

```json
{
  "type":   "chart",
  "mark":   "bar",
  "data":   { "values": [ { "portfolio": "Global Equity", "tracking_error": 0.042 }, ... ] },
  "encoding": {
    "x": { "field": "portfolio",      "type": "nominal",      "title": "Portfolio"      },
    "y": { "field": "tracking_error", "type": "quantitative", "title": "Tracking Error" }
  },
  "colorScheme": ["#003f5c", "#58508d", "#bc5090"],
  "formatHints": {
    "tracking_error": { "format": ".2%", "unit": "%" }
  }
}
```

**Table specification** (`type: "table"`) — produced when no chart contract matches:

```json
{
  "type": "table",
  "columns": [
    { "field": "portfolio",      "label": "Portfolio",      "type": "string"                   },
    { "field": "tracking_error", "label": "Tracking Error", "type": "number", "format": ".2%" },
    { "field": "limit",          "label": "Limit",          "type": "number", "format": ".2%" },
    { "field": "breached",       "label": "Breached",       "type": "boolean"                  }
  ],
  "data": [ ... ],
  "thresholds": [
    { "field": "tracking_error", "operator": "gt", "reference": "limit", "severity": "warning" }
  ]
}
```

Column labels in table specifications come from SMR metric and dimension `display.label` values — never from physical field names.

### Streaming Behaviour

| Output element | Streaming behaviour |
|---|---|
| `display_spec` | Delivered as a complete JSON object after FQP result assembly — not streamed |
| `data` | Delivered as a complete object — not streamed |
| `result_id` + `lineage_url` | Delivered with `display_spec` — not streamed |
| `meta` | Delivered as a complete object — not streamed |
| Governance-blocked errors | Returned immediately before any backend execution |

### Error Response Structure

All error responses include a `result_id` and `lineage_url`, ensuring that blocked and failed requests appear in the audit trail alongside successful ones.

| Error condition | `error.code` | Behaviour |
|---|---|---|
| Cost circuit breaker triggered | `GOVERNANCE_COST_EXCEEDED` | Blocked before FQP; structured suggestions returned |
| Classification gate blocked | `GOVERNANCE_CLASSIFICATION_BLOCKED` | Blocked before FQP; metric classification disclosed |
| Metric not in SMR | `METRIC_NOT_FOUND` | Blocked at intent validation; metric ID disclosed |
| Entitlement denied | `ENTITLEMENT_DENIED` | Blocked at role projection; partial results returned for entitled metrics |
| Backend timeout | `EXECUTION_TIMEOUT` | Partial or null result with provenance markers |
| No matching chart contract | `NO_CHART_CONTRACT` | Not an error — `TABLE_GOVERNED` fallback applied automatically |

### Example

The MCP Capability Layer assembles the SCL display specification and the NSE narrative into the final tool response:

```json
{
  "jsonrpc": "2.0",
  "id":      "req-8a3f2c",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Across your 4 equity portfolios this quarter, 2 outperformed their benchmark. Global Equity Opportunities led at 4.21% vs 3.85% (+36bps). UK Core Income also outperformed at 2.87% vs 2.54% (+33bps). Asia Pacific Growth and European Balanced Income underperformed, with Asia Pacific Growth the furthest behind at -23bps."
      },
      {
        "type": "resource",
        "resource": {
          "uri":      "analytics://result/res-20260518-093247-wk4n",
          "mimeType": "application/vnd.analytics.scl+json",
          "text":     "{ ... SCL grouped bar chart specification ... }"
        }
      }
    ],
    "result_id":   "res-20260518-093247-wk4n",
    "lineage_url": "https://api.analytics-platform.io/v1/lineage/res-20260518-093247-wk4n",
    "meta": {
      "latencyMs":    1243,
      "cacheHit":     false,
      "rowCount":     4,
      "backendsUsed": ["primary-warehouse"],
      "costUnits":    580
    }
  }
}
```

The chat engine renders the grouped bar chart inline and displays the narrative as the assistant's reply. The `result_id` is retained for any follow-up drilldown.

---

## Analytical Lineage Store

> **Governing principles:** [P4 — Complete analytical lineage](./01-platform-overview.md#design-principles) · [P8 — Explainability at every layer](./01-platform-overview.md#design-principles)

The Analytical Lineage Store provides computation provenance: a complete, queryable record of how every result was calculated. Analytical lineage, as defined on this platform, is distinct from data lineage. Data lineage tracks how data moves between systems. Analytical lineage records how the analytics engine used specific metric definitions, entitlement rules, and execution backends to compute a specific result. The lineage record is not a log — it is a first-class data structure. A regulator, auditor, or internal reviewer must be able to reconstruct exactly how a specific number was calculated, by whom, under what entitlements, from which backends, and with what result — without re-running the query.

### Per-Query Stored Elements

| Element | Table | Content |
|---|---|---|
| Query record | `analytics.queries` | User ID, tenant ID, raw natural language, tool call parameters, intent pattern, timestamp, governance status, execution status, cost units consumed |
| Lineage record | `analytics.lineage_records` | Complete chain: intent → SMR resolution → projection record → LQP → FQP execution record → result schema → visualisation contract → narrative synthesis status |
| SMR snapshot | `analytics.lineage_records.metric_versions` | For each metric in the query: metric ID, SMR definition version, formula at query time |
| Projection record | `analytics.lineage_records.projection_record` | Roles, requested metrics, projected metrics, blocked metrics, row predicates, column masks |
| FQP execution record | `analytics.lineage_records.fqp_execution` | Sub-plan details, engine IDs, latencies, cost units, cache hit status |
| Governance decision | `analytics.governance_events` | Circuit breaker decisions, classification gates, cost limit checks — including blocked queries |
| Result artefact | Object storage + `analytics.result_artefacts` | CSV result set, chart SVG, narrative text — stored per query |

### Core DDL: `analytics.lineage_records`

```sql
CREATE TABLE analytics.lineage_records (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id            UUID NOT NULL REFERENCES analytics.queries(id),
  tenant_id           TEXT NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  -- Structured JSONB fields for each lineage chain element
  intent_resolution   JSONB NOT NULL,  -- natural language → intent mapping
  smr_resolution      JSONB NOT NULL,  -- metric/dimension definitions used
  projection_record   JSONB NOT NULL,  -- entitlement decisions
  lqp                 JSONB NOT NULL,  -- Logical Query Plan
  governance_checks   JSONB NOT NULL,  -- governance decisions
  fqp_execution       JSONB NOT NULL,  -- FQP sub-plans and engine calls
  visualisation       JSONB,           -- chart contract selected
  narrative_status    JSONB            -- narrative synthesis outcome
);
```

The JSONB structure allows efficient querying of individual lineage chain elements — for example, finding all queries that used a specific metric version, or all queries where a governance check was blocked — without requiring full record deserialisation.

### Multi-Tenant Isolation

Every record in the `analytics` schema carries a `tenant_id` column. Row-Level Security (RLS) in PostgreSQL enforces that users can only access records belonging to their own tenant. No cross-tenant data access is possible through the platform's API at any privilege level.

### Retention

| Rule | Specification |
|---|---|
| Query records | Configurable per tenant. Platform default: **2,555 days (7 years)** — covering most regulatory audit look-back periods. |
| Lineage records | Retained at least as long as the corresponding query record. Cannot be deleted independently. |
| SMR metric versions | Retained indefinitely — metric version history must be preserved for lineage reconstruction. |
| Governance events | Retained at least as long as query records. |
| Result artefacts (object storage) | Configurable per tenant. Default: 365 days. Lineage record references are preserved even after object storage expiry. |
| Blocked queries | Retained in full — queries that fail governance checks are as important to retain as successful ones. |

### Immutability

Lineage records are never modified after writing. There is no update or delete path available to any user — including Platform Admins. Corrections to erroneous records produce new records that reference the original via a `supersedes` relationship. This constraint is enforced at the database layer, not only by application logic.

### Regulatory Audit Export

```
GET /v1/audit/queries
    ?user_id={user_id}
    &from={ISO8601}
    &to={ISO8601}
    &metric_ids[]={metric_id}
    &include_lineage=true
    → Returns all queries matching the filter with full lineage records
```

Audit export packages include query records with timestamps and user identifiers, lineage records with metric definition versions, governance decisions, role-aware projection records showing entitlements in force at query time, and result artefacts within the retention period. All export packages are digitally signed by the platform using a tenant-specific key registered at onboarding.

### Example

Two lineage records are written for this query. The first is written by SEG before the FQP is invoked — capturing the governance decision regardless of whether execution succeeds. The second is written by the FQP after execution.

**Governance decision record (written before FQP execution):**
```json
{
  "query_id":  "qry-20260518-093241-xm2p",
  "lqp_id":   "lqp-20260518-093243-r9xq",
  "tenant_id": "acme-wealth",
  "event":     "governance_approved",
  "timestamp": "2026-05-18T09:32:44Z",
  "checks":    ["cost_ceiling", "metric_count", "dimension_count", "classification_gate"],
  "result":    "all_passed"
}
```

**Execution record (written after FQP completes):**
```json
{
  "result_id":       "res-20260518-093247-wk4n",
  "lqp_id":         "lqp-20260518-093243-r9xq",
  "fqp_execution": {
    "sub_plans": [
      {
        "backend":    "primary-warehouse",
        "dialect":    "snowflake_sql",
        "latency_ms": 1187,
        "row_count":  4,
        "cache_hit":  false
      }
    ]
  },
  "smr_snapshot": [
    { "metric_id": "portfolio_return",  "version": "2.1.0" },
    { "metric_id": "benchmark_return",  "version": "1.4.2" }
  ],
  "projection_record": {
    "roles":            ["portfolio_manager"],
    "row_predicates":   ["portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC','ASIA_PAC_GRW','EUR_BAL_INC')"],
    "column_masks":     []
  },
  "visualisation":    { "contract": "BAR_MULTI_SERIES_COMPARISON" },
  "narrative_status": { "generated": true, "validation": "passed" }
}
```

Both records are immutable from the moment of writing. The full chain — original query, governance decision, metric definition versions, entitlements, physical backend call, and chart contract — is queryable under `result_id: res-20260518-093247-wk4n`.

---

## MCP Capability Layer

> **Governing principles:** [P2 — Governance before execution](./01-platform-overview.md#design-principles) · [P5 — Role-aware by default](./01-platform-overview.md#design-principles)

The MCP Capability Layer exposes the platform's governed analytical operations to AI orchestrators via MCP Streamable HTTP transport. Each capability is a bounded, named operation with a typed input schema, a governed execution path through the full platform pipeline (Semantic Intent Layer → Role-Aware Projection → SEG → FQP), and a typed output contract. AI agents interact with capabilities, not databases. There is no privileged API path — AI agents receive the same governance-validated results as human users.

### Tool Catalogue

The Analytics Engine exposes three tools. All analytical operations are SMR-catalogue driven — the code is the execution engine, not the operation registry. The SMR owns every operation definition: what parameters it needs, what metrics and dimensions it supports, and how deeply it runs through the pipeline via its `execution_profile`.

**`run_analytics(operation_id: str, params: dict, jwt: str)`** — Executes any SMR-registered operation. The operation's `execution_profile` in the DCS determines which pipeline stages run.

| Parameter | Required | Type | Notes |
|---|---|---|---|
| `operation_id` | Yes | `string` | SMR operation ID — discover via `list_operations` |
| `params` | Yes | `object` | Operation-specific parameters; validated by the SIL against the operation's `required_params` schema in the SMR DCS catalogue |
| `jwt` | Yes | `string` | Bearer token; validated at request ingress before any platform computation begins |

**`list_operations(domain: str | None, jwt: str)`** — Returns the SMR operation catalogue with operation IDs, display names, required parameters, supported metrics/dimensions, and execution profiles. Only operations the authenticated user is entitled to execute are returned.

| Parameter | Required | Type | Notes |
|---|---|---|---|
| `domain` | No | `string \| None` | Optional filter by analytical domain |
| `jwt` | Yes | `string` | Bearer token |

**`drilldown(result_id: str, hierarchy: str, selected_value: str | None, jwt: str)`** — Navigates into a dimension hierarchy from a prior result. All filters, role predicates, and entitlement context from the original result are preserved.

| Parameter | Required | Type | Notes |
|---|---|---|---|
| `result_id` | Yes | `string` | Result ID from a prior `run_analytics` call |
| `hierarchy` | Yes | `string` | Hierarchy ID to traverse |
| `selected_value` | No | `string \| None` | Dimension value to anchor the drilldown |
| `jwt` | Yes | `string` | Bearer token |

### Execution Profiles

Each SMR operation carries an `execution_profile` defined in its `analytical_operation` DCS document. This tells the pipeline executor which stages to invoke. No execution depth is hardcoded in the MCP layer — it is always determined by the SMR catalogue.

| Profile | Pipeline stages |
|---|---|
| `data_retrieval` | Auth → RAPL → FQP → Lineage |
| `metric_query` | Auth → RAPL → SIL → SEG → FQP → Lineage |
| `full_analytical` | Full pipeline including Visualisation Ontology + Narrative Synthesis Engine |

### Capability Governance

Every capability invocation passes through the full governance pipeline: input schema validation → capability availability check (feature flags and role entitlements) → Semantic Intent Layer → Role-Aware Projection → Semantic Execution Governance → FQP → result assembly → lineage record write. Capability availability is declared in the MCP manifest; a capability not enabled by a feature flag or accessible to the user's role appears as `available: false` with a reason.

### MCP Registration

The following registration JSON declares the Analytics Platform to an AI Chat Platform or orchestration framework:

```json
{
  "id":          "analytics-platform",
  "name":        "Analytics Platform",
  "description": "Governed analytical query engine for portfolio performance, risk, and regulatory metrics. All queries are validated against the Semantic Metrics Registry, subject to role-based entitlement projection, and governed by cost and compliance circuit breakers before execution.",
  "endpoint":    "https://api.analytics-platform.io/v1/mcp",
  "authType":    "bearer",
  "accessTier":  "always-on",
  "roles":       []
}
```

The `roles: []` value indicates that capability availability is determined dynamically from the bearer token's role claims at the time of each invocation, rather than being statically restricted at registration time.

### Example

A structured `run_analytics` tool call arrives from the AI Chat Platform. The MCP Capability Layer validates the JWT signature, confirms the token has not expired, and extracts the claims. It dispatches two parallel operations: the structured parameters to the Semantic Intent Layer, and the JWT claims to the Role-Aware Projection Layer. The MCP Capability Layer does not interpret the parameters or make any analytical decisions; it validates, routes, and waits.
