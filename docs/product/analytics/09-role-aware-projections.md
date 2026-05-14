# 09 — Role-Aware Projections

## Overview

The **Role-Aware Projection Layer** is the component that applies the authenticated user's entitlement model to the resolved analytical intent before any query plan is compiled. It is the semantic-layer enforcement of data access controls — operating above the physical execution layer, before any query reaches an execution engine.

Role-aware projection is not optional and not bypassable. Every analytical request — whether from natural language or an MCP tool call — passes through the projection layer.

---

## Projection model

The projection layer applies four categories of restriction:

| Restriction type | Description | Applied at |
|-----------------|-------------|------------|
| **Metric access filter** | Removes metrics from the resolved intent that the user's role is not entitled to query | Intent validation — Stage 3 |
| **Dimension access filter** | Removes dimensions the user is not entitled to slice by | Intent validation — Stage 3 |
| **Row predicate injection** | Injects SQL-like predicates that restrict which data rows the user can access | FQP physical query generation |
| **Column mask application** | Replaces or nullifies column values the user is not permitted to see in the assembled result | FQP result assembly |

---

## Projection lifecycle

```
Authenticated request arrives with JWT
│
├── 1. JWT validation (signature, expiry, tenant claim)
│
├── 2. Role claim extraction
│       roleClaimField: "analytics_roles"
│       extracted roles: ["portfolio_manager"]
│
├── 3. Entitlement profile construction
│       Merge all role definitions for the user's roles
│       Produce: metric_access_set, dimension_access_set,
│               row_predicates[], column_masks[]
│
├── 4. Metric access filter
│       Intersect requested metrics with metric_access_set
│       Unentitled metrics → METRIC_NOT_ENTITLED error (per metric)
│
├── 5. Dimension access filter
│       Intersect requested dimensions with dimension_access_set
│       Unentitled dimensions → DIMENSION_NOT_ENTITLED error (per dimension)
│
├── 6. Row predicate construction
│       Resolve predicate templates: {{user.managed_portfolios}}
│       → "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"
│       Predicates stored in LQP for FQP injection at execution time
│
├── 7. Column mask registration
│       Register masked columns in LQP metadata
│       FQP applies masks during result assembly
│
└── 8. Projected LQP produced → proceeds to governance validation
```

---

## Multi-role entitlement merging

Users may hold multiple roles simultaneously. The projection layer merges role entitlements using **union semantics** — a user holding both `portfolio_manager` and `risk_officer` roles receives the union of both metric access sets and both dimension access sets.

Row predicates and column masks from multiple roles are intersected (most restrictive wins):

| Entitlement type | Merge strategy | Rationale |
|-----------------|---------------|-----------|
| Metric access | Union | A user entitled to a metric via any role may query it |
| Dimension access | Union | A user entitled to a dimension via any role may use it |
| Row predicates | Intersection (AND) | All predicates must be satisfied — most restrictive wins |
| Column masks | Union | A column masked by any role is masked for the user |

**Example multi-role merge:**

User has roles: `portfolio_manager` + `risk_officer`

| | `portfolio_manager` | `risk_officer` | Merged |
|-|--------------------|--------------------|--------|
| Metric access | `{portfolio_return, aum, tracking_error, sharpe_ratio}` | `{var_95, var_99, beta, duration, tracking_error}` | `{portfolio_return, aum, tracking_error, sharpe_ratio, var_95, var_99, beta, duration}` |
| Dimension access | `{portfolio, asset_class, date}` | `{portfolio, asset_class, issuer, rating, date}` | `{portfolio, asset_class, issuer, rating, date}` |
| Row predicates | `portfolio_id IN ({{user.managed_portfolios}})` | *(none)* | `portfolio_id IN ({{user.managed_portfolios}})` |
| Column masks | *(none)* | *(none)* | *(none)* |

---

## Row predicate template resolution

Row predicate templates reference JWT claim values using `{{user.claim_name}}` syntax. Resolution occurs at query time using the authenticated user's current JWT:

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

**Supported predicate functions:**

| Function | Description |
|----------|-------------|
| `{{user.claim_name}}` | Direct JWT claim value (string or array) |
| `{{user.claim_name \| upper}}` | Claim value uppercased |
| `{{user.claim_name \| join(',')}}` | Array claim joined as a CSV string |
| `CURRENT_USER_ID()` | Platform user ID — resolved at execution time |
| `CURRENT_DATE()` | Execution date — resolved at execution time |

---

## Column masking

Column masks are applied by the FQP during result assembly, after sub-results are returned from execution engines but before the result is returned to the calling layer.

**Masking modes (configured per tenant):**

| Mode | Masked column representation |
|------|------------------------------|
| `null_replacement` | Column value replaced with `null` |
| `redacted_label` | Column value replaced with the string `"[REDACTED]"` |
| `excluded` | Column omitted entirely from the result schema |

**Example:**

Compliance analyst role has `column_masks: ["client_name", "account_number"]` with `columnMaskingMode: "redacted_label"`.

**Assembled result before masking:**
```json
[
  { "portfolio_id": "GLOB_EQ_OPP", "client_name": "Blackwood Family Trust", "account_number": "WM-00412", "lcr": 1.24 }
]
```

**Assembled result after masking:**
```json
[
  { "portfolio_id": "GLOB_EQ_OPP", "client_name": "[REDACTED]", "account_number": "[REDACTED]", "lcr": 1.24 }
]
```

---

## Projection errors and user-facing messaging

When the projection layer blocks a metric or dimension, the response to the user or AI agent includes a structured error alongside the partial result (for multi-metric queries where some metrics are accessible):

```json
{
  "result": {
    "rows": [ ... ],
    "columns": ["portfolio_return", "tracking_error"]
  },
  "projection_errors": [
    {
      "type":       "METRIC_NOT_ENTITLED",
      "metric_id":  "var_95",
      "role":       "portfolio_manager",
      "message":    "The metric 'VaR 95%' is not available to your role. Contact your Application Admin to request access."
    }
  ]
}
```

The Narrative Synthesis Engine is aware of projection errors and will include an acknowledgement in the narrative: *"Note: VaR 95% was requested but is not available to your current role."*

---

## Entitlement audit

Every projection decision is recorded in the lineage store as part of the execution record:

```json
{
  "projection_record": {
    "user_roles":       ["portfolio_manager"],
    "requested_metrics": ["portfolio_return", "tracking_error", "var_95"],
    "projected_metrics": ["portfolio_return", "tracking_error"],
    "blocked_metrics":   [{ "id": "var_95", "reason": "METRIC_NOT_ENTITLED" }],
    "row_predicates":    ["portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC', 'STRAT_BAL')"],
    "column_masks":      [],
    "predicate_sources": { "portfolio_id IN (...)": "jwt_claim:managed_portfolios" }
  }
}
```

This record is available in the lineage inspector and provides evidence for regulatory entitlement audits.

---

## Entitlement cache

Entitlement profiles (merged role sets, resolved predicates) are cached per session to avoid re-computation on every query:

| Cache property | Value |
|---------------|-------|
| Cache key | SHA-256 of (user_id, tenant_id, sorted role claims) |
| Cache TTL | Until JWT expiry or role claim change detected |
| Invalidation | On JWT refresh (new JWT is re-evaluated); on entitlement config change (via Admin API signal) |
| Scope | In-memory per platform edge function instance |

If a user's JWT is refreshed with changed role claims during a session, the entitlement cache is invalidated and the projection is re-evaluated on the next query. Results from before the role change are not retroactively restricted.
