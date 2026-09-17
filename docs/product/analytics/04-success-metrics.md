# 4. Evaluation Framework and Proposed Success Measures

**Technical White Paper:** Governed AI-Enabled Analytics and Data Mining

**Status:** Proposed architecture for evaluation

**Document Version:** 2.1 (draft)

**Date:** 2026-09-17

**Author:** Andrew Bush / M&A Operating System

---


Evaluation should test whether the proposed architecture improves accuracy, traceability, and repeatability for the intended analytical and data-mining workloads. The measures below are proposed acceptance criteria and operating targets, not measured outcomes or service commitments. Owners should establish baselines and approve workload-specific thresholds before drawing conclusions about adoption.

## Evaluation of the Central Proposal

| Requirement | Evaluation Method | Evidence Required |
|---|---|---|
| Accuracy | Compare calculated values and dataset selections with independently verified reference results. Include ambiguous requests, incorrect definitions, missing data, and boundary cases. | Record expected and actual results, approved tolerances, interpretation errors, and unresolved discrepancies. |
| Traceability | Ask an authorized reviewer to reconstruct a sample of successful, rejected, and failed requests from their evidence records. | Demonstrate links to definition and policy versions, source snapshots or references, execution decisions, and returned results or failure states. |
| Repeatability | Rerun approved requests against preserved data and versioned definitions, permissions, and settings. | Compare result values and dataset membership under a declared tolerance and ordering policy. Explain every difference. |
| Governed Access | Exercise permitted and denied requests across roles, organizations, and dataset fields. | Show that execution and evidence access respect policy, including cache hits and bulk retrieval. |

Compare the approach with the organization's existing analytical process and, where relevant, a controlled Text-to-SQL workflow using the same questions and source data. Record definition-authoring effort, review effort, latency, cost, and unsupported questions alongside correctness. A benefit is established by those measurements, not by the presence of an architectural component.

Component definitions referenced in the measures below are in [Section 2, Proposed Architecture and Capabilities](./02-core-capabilities.md), including the [Analytical Lineage Store](./02-core-capabilities.md#analytical-lineage-store-als), [Semantic Controls Layer](./02-core-capabilities.md#semantic-controls-layer-scl), and [Narrative Synthesis Agent](./02-core-capabilities.md#narrative-synthesis-agent-nsa).


## 4.1 Platform-Level Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **API availability** | Valid requests receiving a non-5xx terminal response ÷ valid requests, measured monthly; planned exclusions must be documented in the SLO policy | ≥ 99.9% |
| **Interactive latency** | End-to-end latency for successful interactive metric queries, reported separately for cache hits and executions | p95 < 2s cached; workload-specific execution SLOs |
| **Platform 5xx rate** | Valid requests ending in a platform-attributable 5xx response ÷ valid requests | < 0.1% |
| **Governance block rate** | Queries blocked by governance checks ÷ total queries | Monitor — sustained > 15% warrants investigation; > 30% triggers mandatory configuration review (see §4.3) |
| **FQE error rate** | Queries with FQE execution errors ÷ total executed queries | < 2% |
| **Cache hit rate** | Queries served from the Result Cache ÷ total executed queries — derived from the `cache_hit` field in the Analytical Lineage Store (ALS) | ≥ 35% by month 2 |
| **Lineage durability** | Accepted requests with a durable terminal lineage record ÷ accepted requests | 100% invariant; fail closed or queue durably when the ALS is unavailable |
| **Lineage reconciliation lag** | Time from a recoverable partial write to a reconciled object/index/signature state | p99 < 5 minutes; no unresolved item > 24 hours |
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
| **Intent confirmation rate** | Natural-language requests requiring user confirmation ÷ natural-language requests | Monitor by operation and domain; sustained increases trigger catalog review |
| **Cost per successful query** | Compute, model, federation, and storage cost ÷ successful queries, segmented by workload class | Establish baseline in month 1 and approve budgets by workload class |


## 4.3 Metric Interpretation

### Governance block rate

| Block rate | Interpretation |
|-----------|---------------|
| < 5% | Healthy — some queries are appropriately blocked |
| 5–15% | Review recommended — entitlement or scope configuration may need tuning |
| 15–30% | Likely misconfiguration — data scale limits, entitlements, or scope too restrictive |
| > 30% | Configuration review mandatory — platform may be inaccessible to legitimate queries |

**Lineage durability** is measured over accepted requests: requests that pass transport authentication and receive a platform request identifier. Authentication attempts that fail before an identifier is issued are recorded in the security audit system rather than the ALS denominator. Every accepted request must reach a durable terminal state: completed, denied by controls, cancelled, timed out, or failed. If the ALS cannot accept a durable write, execution fails closed or the event is committed to a durable queue before processing continues. Reconciliation lag measures temporary divergence between the object, index, and signature state.

**SMR approval backlog** counts metric definitions in `proposed` or `in_review` state for more than 7 calendar days. A non-zero count triggers a notification to Analytics Governance.


## 4.4 Review Cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Daily** | Lineage durability and reconciliation; FQE error rate; classification gate spike detection | Platform Admin (automated) |
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
- Lineage durability and reconciliation lag (100% durable terminal records or an active incident)
- SMR approval backlog count

Platform-level infrastructure metrics are visible to the Platform Admin only.
