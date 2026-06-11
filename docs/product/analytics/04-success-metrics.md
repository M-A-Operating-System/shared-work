# 4. Success Metrics

Metrics are captured from day one at both the platform level and the application level. Governance health metrics are first-class success indicators. A platform that is highly used but poorly governed is not successful.

Component definitions referenced in the metrics below (SMR, FQE, RAPL, SCL, NSA, ALS) are in [Chapter 2 — Core Platform Capabilities](./02-core-capabilities.md). [Analytical Lineage Store (ALS)](./02-core-capabilities.md#analytical-lineage-store-als) · [Semantic Controls Layer (SCL)](./02-core-capabilities.md#semantic-controls-layer-scl) · [Narrative Synthesis Agent (NSA)](./02-core-capabilities.md#narrative-synthesis-agent-nsa)


## 4.1 Platform-Level Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Platform uptime** | API availability (p99 end-to-end latency < 2s including FQE backend execution; error rate < 0.1%) | 99.9% |
| **Governance block rate** | Queries blocked by governance checks ÷ total queries | Monitor — sustained > 15% warrants investigation; > 30% triggers mandatory configuration review (see §4.3) |
| **FQE error rate** | Queries with FQE execution errors ÷ total executed queries | < 2% |
| **Cache hit rate** | Queries served from the Result Cache ÷ total executed queries — derived from the `cache_hit` field in the Analytical Lineage Store (ALS) | ≥ 35% by month 2 |
| **Lineage completeness** | Queries with complete lineage records ÷ total queries | **100%** — any deviation is a platform defect |
| **SMR registry health** | Metrics with no owner OR not updated in 12 months ÷ total active metrics | < 5% |


## 4.2 Application-Level Metrics

### Usage

| Metric | Definition | Target |
|--------|-----------|--------|
| **Weekly active users (WAU)** | Distinct users executing at least one query in a 7-day window | 50% of entitled users by day 90 |
| **Queries per user per week** | Total query executions ÷ weekly active users | ≥ 8 |
| **Drilldown rate** | Sessions with at least one drilldown traversal ÷ total sessions | ≥ 20% |
| **Export rate** | Sessions with at least one result export ÷ total sessions | ≥ 15% |
| **Narrative consumption** | Queries where user expanded the narrative card ÷ queries with narrative | ≥ 40% |
| **Lineage inspector opens** | Queries where user opened lineage inspector ÷ total queries (Power Analysts) | ≥ 25% |

### Governance

| Metric | Definition | Target |
|--------|-----------|--------|
| **Metric resolution success rate** | Queries where all requested metrics resolved from SMR ÷ total queries | ≥ 95% |
| **Data scale block rate** | Queries blocked by the SCL data scale check ÷ total queries | < 5% — sustained > 10% triggers review |
| **Classification gate block rate** | Queries blocked by classification gate ÷ total queries | Monitored — any spike triggers security review |
| **Entitlement error rate** | Queries with METRIC_NOT_ENTITLED or DIMENSION_NOT_ENTITLED errors ÷ total queries | < 3% |
| **SMR approval backlog** | Metric definitions in `proposed` or `in_review` state > 7 days | 0 — all pending definitions reviewed within 7 days |
| **Metric owner coverage** | Active metrics with an assigned owner ÷ total active metrics | 100% |

### Data Quality

| Metric | Definition | Target |
|--------|-----------|--------|
| **Backend error rate** | Backend sub-plan failures ÷ total sub-plan executions (per backend) | < 1% per backend |
| **Partial result rate** | Queries returning partial results (timeout on one or more sub-plans) | < 2% |
| **Stale data rate** | Queries where a metric's data refresh cadence exceeded its SLA | < 5% |
| **Cache freshness** | Cached results served beyond TTL ÷ cache hits | < 1% |

### Query Quality

| Metric | Definition | Target |
|--------|-----------|--------|
| **Intent resolution accuracy** | Queries where user accepted resolved intent without modification (when `requiresIntentConfirmation: true` is configured). When intent confirmation is not enabled, use query reformulation rate as the proxy measure. | ≥ 85% |
| **Query reformulation rate** | Queries where user rephrased within 2 turns after a resolution error | < 10% |
| **Narrative validation failure rate** | Narrative synthesis attempts failing post-generation validation | < 2% |


## 4.3 Metric Interpretation

### Governance block rate

| Block rate | Interpretation |
|-----------|---------------|
| < 5% | Healthy — some queries are appropriately blocked |
| 5–15% | Review recommended — entitlement or scope configuration may need tuning |
| 15–30% | Likely misconfiguration — data scale limits, entitlements, or scope too restrictive |
| > 30% | Configuration review mandatory — platform may be inaccessible to legitimate queries |

**Lineage completeness** is measured as `completed_lineage ÷ total_queries`. Any value below 100% triggers an automated platform alert. Lineage gaps are platform defects, not acceptable operational variance.

**SMR approval backlog** counts metric definitions in `proposed` or `in_review` state for more than 7 calendar days. A non-zero count triggers a notification to Analytics Governance.


## 4.4 Review Cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Daily** | Lineage completeness check; FQE error rate; classification gate spike detection | Platform Admin (automated) |
| **Weekly** | WAU; governance block rate; SMR approval backlog; backend error rate per backend | Platform Admin + Analytics Governance |
| **Monthly** | Full metric review; query quality analysis; SMR health report; narrative validation rate | Platform Admin + Analytics Governance |
| **Day 90** | WAU adoption assessment (50% target); drilldown adoption; export rate | Analytics Governance + Platform Admin |
| **Quarterly** | SMR completeness; metric owner coverage; entitlement policy review | Analytics Governance + Metrics Modellers + Entitlements Manager |


## 4.5 Analytics Dashboard

Analytics Governance has access to a read-only dashboard showing:

- WAU trend (30-day rolling)
- Query volume by intent pattern
- Governance block rate trend with breakdown by controls check (data scale · complexity · classification · compliance · concurrency)
- SMR metric resolution success rate
- Execution backend error rate per backend
- Cache hit rate trend
- Top 10 most-queried metrics
- Lineage completeness (always 100% or an active alert)
- SMR approval backlog count

Platform-level infrastructure metrics are visible to the Platform Admin only.
