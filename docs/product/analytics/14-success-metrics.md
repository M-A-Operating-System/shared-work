# 14 — Success Metrics

## Governing principle

Metrics are captured from day one at both the platform level (across all tenants) and at the application level (per tenant). Governance health metrics are treated as first-class success indicators — not vanity metrics. A platform that is highly used but poorly governed is not successful.

---

## Platform-level metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Active tenants** | Tenants with at least one successful query execution in the 7-day window | Growth metric — tracked weekly |
| **Platform uptime** | API availability (p99 latency < 2s; error rate < 0.1%) | 99.9% |
| **Governance block rate** | Queries blocked by governance checks ÷ total queries | Monitor — sustained > 30% may indicate misconfigured cost limits or entitlements |
| **FQP error rate** | Queries with FQP execution errors ÷ total executed queries | < 2% |
| **Cache hit rate** | Queries served from result cache ÷ total executed queries | ≥ 35% by month 2 |
| **Lineage completeness** | Queries with complete lineage records ÷ total queries | 100% — any deviation is a platform defect |
| **SMR registry health** | Metrics with no owner OR not updated in 12 months ÷ total active metrics | < 5% |

---

## Application-level metrics

### Usage metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Weekly active users (WAU)** | Distinct users executing at least one query in a 7-day window | 50% of entitled users by day 90 |
| **Queries per user per week** | Total query executions ÷ weekly active users | ≥ 8 |
| **Drilldown rate** | Sessions with at least one drilldown traversal ÷ total sessions | ≥ 20% |
| **Export rate** | Sessions with at least one result export ÷ total sessions | ≥ 15% |
| **Narrative synthesis consumption** | Queries where the user expanded the narrative card ÷ total queries with narrative | ≥ 40% |
| **Lineage inspector opens** | Queries where user opened the lineage inspector ÷ total queries (Power Analysts) | ≥ 25% |

### Governance metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Metric resolution success rate** | Queries where all requested metrics resolved from SMR ÷ total queries | ≥ 95% |
| **Cost circuit breaker rate** | Queries blocked by cost limits ÷ total queries | < 5% — sustained > 10% triggers review of cost limit configuration |
| **Classification gate block rate** | Queries blocked by classification gate ÷ total queries | Monitored — any unexpected spike triggers security review |
| **Entitlement error rate** | Queries with METRIC_NOT_ENTITLED or DIMENSION_NOT_ENTITLED errors ÷ total queries | < 3% |
| **SMR approval backlog** | Metric definitions in `proposed` or `in_review` state > 7 days | 0 — all pending definitions reviewed within 7 days |
| **Metric owner coverage** | Active metrics with an assigned owner ÷ total active metrics | 100% |

### Data quality metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Execution engine error rate** | Engine sub-plan failures ÷ total sub-plan executions (per engine) | < 1% per engine |
| **Partial result rate** | Queries returning partial results (timeout on one or more sub-plans) ÷ total queries | < 2% |
| **Stale data indicator rate** | Queries where a metric's data refresh cadence exceeded its SLA ÷ total queries | < 5% |
| **Cache freshness** | Cached results served beyond their TTL (due to cache invalidation delay) ÷ cache hits | < 1% |

### Query quality metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Intent resolution accuracy** | Queries where the user accepted the resolved intent without modification (intent confirmation enabled tenants) ÷ total queries | ≥ 85% |
| **Query reformulation rate** | Queries where the user rephrased within 2 turns after a resolution error ÷ total queries | < 10% |
| **Narrative validation failure rate** | Narrative synthesis attempts failing post-generation validation ÷ total narrative syntheses | < 2% |

---

## Metric definitions

### WAU measurement
A user is counted once per 7-day window regardless of query count. "Active" means at least one successfully executed query (governance-approved + FQP-executed). Queries blocked at governance are not counted.

### Governance block rate interpretation

| Block rate | Interpretation |
|-----------|---------------|
| < 5% | Healthy — some queries are appropriately blocked |
| 5–15% | Review recommended — entitlement or scope configuration may need tuning |
| 15–30% | Likely misconfiguration — cost limits, entitlements, or scope too restrictive |
| > 30% | Configuration review mandatory — platform may be inaccessible to legitimate queries |

### Lineage completeness
Measured as `completed_lineage ÷ total_queries`. Any value below 100% triggers an automated platform alert. Lineage gaps are platform defects, not acceptable operational variance.

### SMR approval backlog
Measured as the count of metric definitions that have been in `proposed` or `in_review` state for more than 7 calendar days. A non-zero count triggers a notification to the Application Admin.

---

## Review cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Daily** | Lineage completeness check; FQP error rate; classification gate spike detection | Platform Engineering (automated) |
| **Weekly** | WAU; governance block rate; SMR approval backlog; engine error rate per tenant | Platform Engineering + Application Admin |
| **Monthly** | Full metric review; query quality analysis; SMR health report; narrative validation rate | Platform team + Application Admins |
| **Day 90 (per tenant)** | WAU adoption target assessment (50%); drilldown adoption; export rate | Application Admin + Platform team |
| **Quarterly** | SMR completeness review; metric owner coverage; entitlement policy review | Application Admin + Metric Owners |

---

## Tenant analytics dashboard

Each tenant's Application Admin has access to a read-only analytics dashboard showing:

- WAU trend (30-day rolling)
- Query volume by intent pattern
- Governance block rate trend with breakdown by circuit breaker type
- SMR metric resolution success rate
- Execution engine error rate per engine
- Cache hit rate trend
- Top 10 most-queried metrics
- Lineage completeness (always 100% or an active alert)
- SMR approval backlog count

Platform-level cross-tenant metrics are visible to the Platform team only.
