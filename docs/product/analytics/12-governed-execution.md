# 12 — Governed Execution

## Overview

The **Semantic Execution Governance** layer applies a suite of circuit breakers, cost controls, complexity limits, and compliance classification checks to every analytical query before it is released to the Federated Query Planner. It is the last gate before physical execution.

Governance is applied to every query without exception. There is no privileged user, trusted agent, or internal bypass path that skips governance checks.

---

## Governance pipeline

```
Validated LQP (post role-aware projection)
│
├── 1. Cost estimation
│       Estimate execution cost units from LQP metadata
│       (cardinality estimate × engine cost tier × complexity factor)
│
├── 2. Cost circuit breaker
│       Compare estimated cost to maxQueryCostUnits
│       BLOCK if exceeded → user prompted to narrow scope
│
├── 3. Complexity limit check
│       Evaluate LQP node count, join depth, sub-plan count
│       BLOCK if exceeds complexity threshold
│
├── 4. Classification gate
│       For each metric: retrieve data.classification from SMR
│       Compare against blockedClassifications list
│       BLOCK if any metric's classification is in blocked list
│
├── 5. Regulatory compliance mode check
│       If complianceMode is set: apply compliance-specific rules
│       (e.g. MiFID II: log all queries involving client-related metrics)
│
├── 6. Concurrency limit check
│       Count active queries for this user
│       BLOCK (with wait) if exceeds maxConcurrentQueries
│
├── 7. Timeout budget assignment
│       Assign queryTimeoutSeconds to the FQP execution context
│
└── 8. Governance approval record written
        Governance event record written before FQP is invoked
        (ensures governance decisions are auditable even if FQP fails)
        → Release to FQP
```

---

## Cost estimation model

Cost units are estimated from the LQP before execution. The estimation model uses:

| Factor | Contribution |
|--------|-------------|
| Number of metrics | `metric_count × 50` base units |
| Engine cost tier per sub-plan | `minimal: 10`, `low: 50`, `standard: 100`, `high: 300`, `unrestricted: 0` |
| Dimension cardinality | `low: ×1.0`, `medium: ×1.5`, `high: ×3.0`, `unbounded: ×5.0` |
| Time period scope | `single_day: ×1.0`, `quarter: ×2.0`, `year: ×4.0`, `since_inception: ×8.0` |
| Number of sub-plans (federation) | `+100 per additional sub-plan` |
| Materialised view match | `-800` (pre-computed result) |
| Cache hit (estimated) | `-900` (full cache hit expected) |

**Example cost estimate:**

Query: `portfolio_return, tracking_error BY portfolio, asset_class FOR YEAR_TO_DATE`

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

Against a `maxQueryCostUnits: 1000` limit, this query is approved. Against a `500` limit, it is blocked.

---

## Cost circuit breaker response

When a query is blocked by the cost circuit breaker, the user receives a structured response:

```
┌────────────────────────────────────────────────────────────┐
│ ⚠️  Query scope is too broad                              │
├────────────────────────────────────────────────────────────┤
│ Estimated cost: 850 units (limit: 500 units)              │
│                                                            │
│ Suggestions to reduce scope:                               │
│  • Narrow the time period (e.g. use Quarter-to-Date        │
│    instead of Year-to-Date)                                │
│  • Reduce the number of metrics (e.g. query 'portfolio_    │
│    return' separately from 'tracking_error')               │
│  • Filter to a specific portfolio or asset class           │
│                                                            │
│ [Refine my question]    [Contact Application Admin]        │
└────────────────────────────────────────────────────────────┘
```

The AI assistant reformulates the query based on the suggestions if the user clicks *"Refine my question"*.

---

## Classification gate

The classification gate evaluates the data classification of every metric in the query against the tenant's `blockedClassifications` list.

**Classification evaluation logic:**

```python
def classification_gate(metrics, smr, blocked_classifications):
    for metric in metrics:
        smr_def = smr.get(metric.id)
        if smr_def.governance.classification in blocked_classifications:
            raise GovernanceBlock(
                type="CLASSIFICATION_GATE",
                metric_id=metric.id,
                classification=smr_def.governance.classification,
                message=f"Metric '{smr_def.label}' has classification "
                        f"'{smr_def.governance.classification}' which is "
                        f"not permitted for query execution."
            )
    return "approved"
```

Classification gate blocks are non-negotiable — they cannot be overridden by the user or Application Admin within the session. Changing the classification gate configuration requires an Admin API config update.

---

## Compliance modes

Named compliance profiles pre-configure governance behaviour for specific regulatory environments:

### MiFID II mode

```json
{ "complianceMode": "mifid2" }
```

| Additional rule | Implementation |
|----------------|---------------|
| All queries involving client-identifiable data must be logged with the business justification | Prompt user for business justification before queries on `client_name`, `account_number`, or similar PII-adjacent dimensions |
| Best execution metrics must be queried with explicit timeframe | Validation error if `date` dimension not specified for best-execution metrics |
| Transaction reporting queries must generate a TRACE record | Additional lineage record written to `analytics.mifid2_trace` table |

### Basel III/IV mode

```json
{ "complianceMode": "basel3" }
```

| Additional rule | Implementation |
|----------------|---------------|
| Capital ratio queries must include entity identifier | Required dimension: `entity` for all regulatory capital metrics |
| LCR/NSFR queries generate a daily snapshot record | Regulatory metric queries trigger a snapshot write to `analytics.regulatory_snapshots` |
| Queries on stress scenario data classified as RESTRICTED | Stress scenario metrics automatically classified at RESTRICTED level regardless of user role |

### SEC Regulation BI mode

```json
{ "complianceMode": "sec_reg_bi" }
```

| Additional rule | Implementation |
|----------------|---------------|
| Narrative synthesis prohibited from generating investment recommendations | Additional narrative synthesis constraint injected into prompt |
| Client analytics require suitability record reference | Advisory queries require `suitability_record_id` parameter before execution |

---

## Timeout and partial result handling

The FQP applies the `queryTimeoutSeconds` budget assigned by the governance layer. Timeout behaviour:

| Scenario | Behaviour |
|----------|-----------|
| All sub-plans complete within timeout | Normal result assembly and return |
| One sub-plan times out, others complete | Partial result assembly — missing metrics represented as null with `timeout` provenance marker; user notified |
| All sub-plans time out | Query failed — error returned to user; governance event written with `timeout` status |
| Engine cancellation on timeout | FQP sends cancellation signal to timed-out engine (if engine supports cancellation) |

---

## Governance event record

Every governance evaluation — approved or blocked — produces a governance event record:

```json
{
  "id":            "gov_evt_20260514_093247",
  "query_id":      "qry_20260514_093247",
  "tenant_id":     "acme-wealth",
  "created_at":    "2026-05-14T09:32:47.123Z",
  "checks": [
    {
      "type":      "cost_estimate",
      "decision":  "approved",
      "estimated": 500,
      "limit":     1000
    },
    {
      "type":      "complexity_limit",
      "decision":  "approved",
      "lqp_nodes": 8,
      "limit":     50
    },
    {
      "type":      "classification_gate",
      "decision":  "approved",
      "metrics_checked": ["portfolio_return", "tracking_error"],
      "highest_classification": "INTERNAL",
      "blocked_classifications": ["TOP_SECRET", "RESTRICTED"]
    },
    {
      "type":      "concurrency_limit",
      "decision":  "approved",
      "active_queries": 1,
      "limit":     5
    }
  ],
  "overall_decision": "approved",
  "fqp_released_at": "2026-05-14T09:32:47.201Z"
}
```
