# 05 — Analytics DSL

## Overview

The **Analytics DSL** is the platform's constrained query language — the interface layer between analytical intent and the Federated Query Planner. It exposes business semantics drawn from the Semantic Metrics Registry, supports AI reasoning about analytical queries, and compiles to engine-agnostic Logical Query Plans (LQPs).

The DSL is not exposed directly to end users. It is the internal representation produced by the Semantic Intent Layer after resolving natural language against the SMR. It may also be used directly by AI orchestrators accessing the platform via the MCP Capability Layer.

The DSL deliberately excludes:
- Physical table or column references
- Database-specific syntax or functions
- JOIN operations (joins are resolved by the FQP using data affinity declarations)
- Raw SQL passthrough of any kind

---

## DSL grammar (EBNF notation)

```ebnf
query           ::= "ANALYSE" metric-list
                    ["BY" dimension-list]
                    ["WHERE" filter-expression]
                    ["FOR" time-expression]
                    ["ORDER BY" order-expression]
                    ["LIMIT" integer]
                    ["COMPARE TO" comparison-target]
                    ["DRILLDOWN" drilldown-expression]

metric-list     ::= metric-ref ("," metric-ref)*
metric-ref      ::= metric-id ["AS" alias]
                  | "MEASURE_GROUP" "(" measure-group-id ")"

dimension-list  ::= dimension-ref ("," dimension-ref)*
dimension-ref   ::= dimension-id ["AT" granularity]

filter-expr     ::= predicate ("AND" | "OR" predicate)*
predicate       ::= dimension-id comparison-op value
                  | metric-id comparison-op value
                  | metric-id "BETWEEN" value "AND" value
                  | predicate "AND" predicate
                  | predicate "OR" predicate
                  | "NOT" predicate
                  | "(" predicate ")"

time-expression ::= "PERIOD" "(" period-spec ")"
                  | "RANGE" "(" date-literal "TO" date-literal ")"
                  | "LAST" integer time-unit
                  | "YEAR_TO_DATE"
                  | "QUARTER_TO_DATE"
                  | "SINCE_INCEPTION"
                  | "FISCAL_YEAR" integer

comparison-op   ::= "=" | "!=" | ">" | "<" | ">=" | "<="
                  | "IN" "(" value-list ")" | "NOT IN" "(" value-list ")"
                  | "LIKE" string | "IS NULL" | "IS NOT NULL"

comparison-target ::= "BENCHMARK" "(" benchmark-id ")"
                     | "PERIOD" "(" period-spec ")"
                     | "PEER_GROUP" "(" peer-group-id ")"

drilldown-expr  ::= "INTO" dimension-id ["AT" depth]

order-expression ::= metric-id | dimension-id ("ASC" | "DESC")

granularity     ::= "DAY" | "WEEK" | "MONTH" | "QUARTER" | "YEAR"
time-unit       ::= "DAYS" | "WEEKS" | "MONTHS" | "QUARTERS" | "YEARS"
```

---

## DSL examples

### Example 1 — Single metric, single dimension, time filter

**Natural language:** "Show me portfolio returns for the current quarter."

**Resolved DSL:**
```dsl
ANALYSE portfolio_return
BY portfolio
FOR QUARTER_TO_DATE
ORDER BY portfolio_return DESC
```

### Example 2 — Multi-metric, multi-dimension, benchmark comparison

**Natural language:** "Show portfolio return and tracking error by asset class compared to benchmark."

**Resolved DSL:**
```dsl
ANALYSE portfolio_return, tracking_error
BY portfolio, asset_class
FOR QUARTER_TO_DATE
COMPARE TO BENCHMARK(b_msci_acwi)
ORDER BY tracking_error DESC
```

### Example 3 — Filtered query with threshold

**Natural language:** "Which portfolios have VaR exceeding their limit today?"

**Resolved DSL:**
```dsl
ANALYSE var_95, var_limit, var_utilisation_pct
BY portfolio
FOR PERIOD(today)
WHERE var_utilisation_pct > 1.0
ORDER BY var_utilisation_pct DESC
```

### Example 4 — Measure group with rolling time window

**Natural language:** "Show me performance metrics for the last 12 months."

**Resolved DSL:**
```dsl
ANALYSE MEASURE_GROUP(performance_metrics)
BY portfolio, date AT MONTH
FOR LAST 12 MONTHS
ORDER BY date ASC
```

### Example 5 — Drilldown expression

**Natural language:** "Drill into asset class for the Global Equity portfolio — show me sub-asset class breakdown."

**Resolved DSL:**
```dsl
ANALYSE portfolio_return, aum
BY sub_asset_class
FOR QUARTER_TO_DATE
WHERE portfolio = 'GLOBAL_EQUITY_OPPORTUNITIES'
DRILLDOWN INTO asset_class_hierarchy AT 2
```

### Example 6 — Issuer concentration with threshold filter

**Natural language:** "Show issuers where concentration exceeds 5% of AUM across all equity portfolios."

**Resolved DSL:**
```dsl
ANALYSE issuer_concentration, aggregate_position_value
BY issuer, portfolio
FOR PERIOD(today)
WHERE asset_class = 'EQUITY'
  AND issuer_concentration > 0.05
ORDER BY issuer_concentration DESC
```

---

## DSL compiler

The DSL compiler is the component that:
1. Receives a DSL expression (produced by the Semantic Intent Layer from natural language)
2. Validates all identifiers against the active SMR for the tenant
3. Applies role-aware projection (see [09-role-aware-projections.md](./09-role-aware-projections.md))
4. Produces an engine-agnostic Logical Query Plan (LQP)

### Compilation stages

```
┌──────────────────┐
│  DSL Expression  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Stage 1: Lexical & Syntax Parse │
│  - Tokenise DSL expression       │
│  - Validate grammar conformance  │
│  - Reject malformed expressions  │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Stage 2: SMR Resolution         │
│  - Resolve metric IDs → metric   │
│    definitions (formula, agg,    │
│    dimensions, data domain)      │
│  - Resolve dimension IDs →       │
│    dimension definitions         │
│  - Resolve hierarchy refs →      │
│    hierarchy definitions         │
│  - Reject unregistered IDs       │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Stage 3: Role-Aware Projection  │
│  - Apply metric access filter    │
│  - Apply dimension access filter │
│  - Inject row predicates         │
│  - Apply column masks            │
│  - Reject entitlement violations │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Stage 4: Semantic Validation    │
│  - Validate required dimensions  │
│    are present per metric        │
│  - Validate aggregation rules    │
│  - Validate time granularity     │
│    compatibility                 │
│  - Validate filter predicates    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Stage 5: LQP Generation         │
│  - Produce engine-agnostic DAG   │
│  - Assign data affinity hints    │
│  - Estimate result cardinality   │
│  - Estimate execution cost units │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Logical Query Plan (LQP)        │
└──────────────────────────────────┘
```

### Compiler error types

| Error type | Example | User-facing message |
|-----------|---------|---------------------|
| `METRIC_NOT_FOUND` | Metric ID not in SMR | *"The metric 'xyz' is not defined in the analytics registry."* |
| `METRIC_NOT_ENTITLED` | Metric in SMR but not in user's role | *"You do not have access to the metric 'portfolio_return'."* |
| `REQUIRED_DIMENSION_MISSING` | `portfolio_return` queried without `portfolio` | *"The metric 'portfolio_return' requires the 'portfolio' dimension."* |
| `INVALID_AGGREGATION` | Aggregation not in `allowed` list | *"The aggregation 'count' is not supported for metric 'portfolio_return'."* |
| `UNSUPPORTED_GRANULARITY` | Daily granularity for a monthly-only metric | *"The metric 'monthly_nav' is only calculable at monthly or lower frequency."* |
| `SYNTAX_ERROR` | Malformed DSL expression | *"Analytical query could not be parsed — please rephrase your question."* |
| `HIERARCHY_NOT_ALLOWED` | Drilldown hierarchy not in tenant config | *"Drilldown into 'counterparty_hierarchy' is not enabled for this application."* |

---

## Logical Query Plan (LQP) schema

The LQP is a directed acyclic graph of analytical operations, serialised as JSON:

```json
{
  "lqp_id":      "lqp_20260514_093247_a1b2c3",
  "tenant_id":   "acme-wealth",
  "version":     "1.0",
  "created_at":  "2026-05-14T09:32:47Z",
  "dsl_source":  "ANALYSE portfolio_return, tracking_error BY portfolio FOR QUARTER_TO_DATE",
  "metrics": [
    {
      "id":          "portfolio_return",
      "version":     "2.1.0",
      "aggregation": "value_weighted_average",
      "period":      "quarter_to_date"
    },
    {
      "id":          "tracking_error",
      "version":     "1.3.0",
      "aggregation": "value_weighted_average",
      "period":      "quarter_to_date"
    }
  ],
  "dimensions": [
    { "id": "portfolio", "required": true }
  ],
  "filters": [
    {
      "type":      "row_predicate",
      "source":    "role_projection",
      "predicate": "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"
    }
  ],
  "time": {
    "type":        "period",
    "period":      "quarter_to_date",
    "as_of_date":  "2026-05-14"
  },
  "data_affinity": {
    "portfolio_return": "portfolio",
    "tracking_error":   "risk_metrics"
  },
  "cost_estimate": {
    "units":       450,
    "confidence":  "medium"
  },
  "cardinality_estimate": {
    "rows":        14,
    "columns":     3
  }
}
```

---

## AI interaction with the DSL

The Analytics DSL is the primary interface for AI agents accessing the platform via the MCP Capability Layer. When an AI orchestrator submits an analytical query, it may do so via:

1. **Natural language** — the Semantic Intent Layer resolves to DSL internally
2. **DSL directly** — the AI submits a DSL expression to the `/v1/query/dsl` endpoint
3. **Pre-defined analytical operations** — the AI invokes named operations from the MCP Capability Layer (which internally produce DSL)

In all cases, the DSL passes through the compiler pipeline — there is no "trusted" bypass for AI-submitted queries. AI agents are subject to the same SMR validation, role-aware projection, and governance checks as human users.
