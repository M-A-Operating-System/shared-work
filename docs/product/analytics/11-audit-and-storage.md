# 11 — Audit and Storage

## Governing principle

Every analytical query on the AI Analytics Platform produces a complete, queryable lineage record. The audit trail is not a log — it is a first-class data structure that supports regulatory enquiry, governance review, and analytical reproducibility. A regulator, auditor, or internal reviewer must be able to reconstruct exactly what was queried, by whom, under what entitlements, using which metric definitions, through which execution engines, and with what results — without reference to any external system.

---

## Multi-tenant isolation

Every record in the `analytics` schema carries a `tenant_id` column. Row-Level Security (RLS) enforces that users can only access records belonging to their own tenant. No cross-tenant data access is possible through the platform's API.

---

## Storage architecture

```
┌───────────────────────────────────────────────────────┐
│                 Analytics Schema (Postgres + RLS)      │
│                                                       │
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ analytics.       │  │ analytics.                  ││
│  │ queries          │  │ lineage_records             ││
│  │ (one per query)  │  │ (one per query, full chain) ││
│  └─────────────────┘  └─────────────────────────────┘│
│                                                       │
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ analytics.       │  │ analytics.                  ││
│  │ smr_metrics      │  │ smr_metric_versions         ││
│  │ (current defs)   │  │ (version history)           ││
│  └─────────────────┘  └─────────────────────────────┘│
│                                                       │
│  ┌─────────────────┐  ┌─────────────────────────────┐│
│  │ analytics.       │  │ analytics.                  ││
│  │ result_artefacts │  │ governance_events           ││
│  │ (in obj storage) │  │ (all governance decisions)  ││
│  └─────────────────┘  └─────────────────────────────┘│
└───────────────────────────────────────────────────────┘
```

---

## Per-query stored elements

| Element | Table | Content |
|---------|-------|---------|
| Query record | `analytics.queries` | User ID, tenant ID, raw natural language, tool call parameters, intent pattern, timestamp, governance status, execution status, cost units consumed |
| Lineage record | `analytics.lineage_records` | Complete chain: intent → SMR resolution → projection record → LQP → FQP execution record → result schema → visualisation contract → narrative synthesis status |
| SMR snapshot | `analytics.lineage_records.metric_versions` | For each metric in the query: metric ID, SMR definition version, formula at query time |
| Projection record | `analytics.lineage_records.projection_record` | Roles, requested metrics, projected metrics, blocked metrics, row predicates, column masks |
| FQP execution record | `analytics.lineage_records.fqp_execution` | Sub-plan details, engine IDs, latencies, cost units, cache hit status |
| Governance decision | `analytics.governance_events` | Circuit breaker decisions, classification gates, cost limit checks — including blocked queries |
| Result artefact | Object storage + `analytics.result_artefacts` | CSV result set, chart SVG, narrative text — stored per query |

---

## Database schema overview

### `analytics.queries`

```sql
CREATE TABLE analytics.queries (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           TEXT NOT NULL,
  user_id             TEXT NOT NULL,
  session_id          TEXT NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  natural_language    TEXT,
  tool_call_params    JSONB,
  intent_pattern      TEXT,
  governance_status   TEXT NOT NULL,  -- 'approved', 'blocked', 'partial'
  execution_status    TEXT NOT NULL,  -- 'success', 'error', 'timeout', 'cancelled'
  cost_units          INTEGER,
  total_latency_ms    INTEGER,
  result_rows         INTEGER,
  cache_hit           BOOLEAN,
  lineage_id          UUID REFERENCES analytics.lineage_records(id)
);
```

### `analytics.lineage_records`

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

### `analytics.governance_events`

```sql
CREATE TABLE analytics.governance_events (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id            UUID REFERENCES analytics.queries(id),
  tenant_id           TEXT NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  event_type          TEXT NOT NULL,   -- 'cost_limit_check', 'classification_gate', 'complexity_limit', 'circuit_breaker'
  decision            TEXT NOT NULL,   -- 'approved', 'blocked', 'warned'
  cost_estimate       INTEGER,
  cost_limit          INTEGER,
  classification      TEXT,
  blocked_classification TEXT,
  reason              TEXT
);
```

### `analytics.smr_metrics`

```sql
CREATE TABLE analytics.smr_metrics (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           TEXT NOT NULL,
  metric_id           TEXT NOT NULL,
  current_version     TEXT NOT NULL,
  status              TEXT NOT NULL,   -- 'draft', 'proposed', 'approved', 'deprecated', 'retired'
  definition          JSONB NOT NULL,  -- full metric definition YAML, stored as JSONB
  owner               TEXT NOT NULL,
  steward             TEXT,
  approved_by         TEXT,
  approved_at         TIMESTAMPTZ,
  effective_from      DATE,
  deprecated_at       TIMESTAMPTZ,
  UNIQUE(tenant_id, metric_id)
);
```

### `analytics.smr_metric_versions`

```sql
CREATE TABLE analytics.smr_metric_versions (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           TEXT NOT NULL,
  metric_id           TEXT NOT NULL,
  version             TEXT NOT NULL,
  definition          JSONB NOT NULL,
  proposed_by         TEXT,
  approved_by         TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (tenant_id, metric_id) REFERENCES analytics.smr_metrics(tenant_id, metric_id)
);
```

---

## Retention

| Rule | Specification |
|------|--------------|
| Query records | Configurable per tenant. Platform default: **2,555 days (7 years)** — to cover most regulatory audit look-back periods. |
| Lineage records | Retained at least as long as the corresponding query record. Cannot be deleted independently. |
| SMR metric versions | Retained indefinitely — metric version history must be preserved for lineage reconstruction. |
| Governance events | Retained at least as long as query records. |
| Result artefacts (object storage) | Configurable per tenant. Default: **365 days**. Lineage record references are preserved even after object storage expiry. |
| Blocked queries | Retained in full — queries that fail governance checks are as important to retain as successful ones. |

---

## Access control

| Access level | Capability |
|-------------|-----------|
| Authenticated end user | Read access to their own query records and lineage records within their tenant only |
| Power Analyst | Read access to lineage inspector for their own queries |
| Application Admin | Read access to all query records, lineage records, and governance events within their own tenant |
| Metric Owner | Read access to all queries that used their owned metrics (via SMR audit view) |
| Platform Admin | Read access to all records across all tenants for operational purposes |
| No user | May modify or delete query records or lineage records — all records are immutable after writing |

---

## Regulatory audit support

The platform supports regulatory audit requests via the Admin API:

```
GET /v1/audit/queries
    ?user_id={user_id}
    &from={ISO8601}
    &to={ISO8601}
    &metric_ids[]={metric_id}
    &include_lineage=true
    → Returns all queries matching the filter with full lineage records
```

Audit export packages (for submission to regulatory bodies) include:
- Query records with timestamps and user identifiers
- Lineage records with metric definition versions used
- Governance decisions for each query
- Role-aware projection records showing entitlements in force at query time
- Result artefacts (if within retention period)

All export packages are digitally signed by the platform using a tenant-specific key registered at onboarding.
