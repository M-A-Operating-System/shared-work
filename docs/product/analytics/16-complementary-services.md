# 16 — Complementary Services

The AI Analytics Platform assumes the availability of three ecosystem-level complementary services that extend its capabilities for financial services deployments. These services are not owned or operated by the AI Analytics Platform itself — they are shared infrastructure within the broader analytics ecosystem. The platform is designed to integrate with them, but none is a hard dependency for platform operation.

---

## Semantic Registry Service

### Overview

The **Semantic Registry Service** is a curated, publicly discoverable library of pre-built metric definitions, dimension schemas, and hierarchy definitions for financial services analytical domains. It reduces the time and expertise required for platform administrators to populate their Semantic Metrics Registry from scratch.

The Semantic Registry Service is primarily a **config-time resource** — platform administrators use it when establishing their SMR baseline. Approved definitions may be imported into the tenant's SMR via the Admin API.

### What the Semantic Registry Service provides

The service organises its content into analytical domain packages:

| Package | Domain | Metric count |
|---------|--------|-------------|
| `fsi-wealth-v1` | Wealth management and private banking | 85 metric definitions |
| `fsi-investment-v1` | Institutional investment management | 120 metric definitions |
| `fsi-banking-v1` | Retail and wholesale banking | 95 metric definitions |
| `fsi-risk-v1` | Cross-domain risk management | 75 metric definitions |
| `fsi-regulatory-v1` | Regulatory reporting (Basel III/IV, MiFID II, AIFMD) | 60 metric definitions |
| `fsi-esg-v1` | ESG and sustainable investment metrics | 45 metric definitions |

Each package provides:
- **Metric definitions** in the platform's SMR YAML schema (ready for import)
- **Dimension schemas** in the platform's SMR schema format
- **Hierarchy definitions** for navigable drilldown
- **Measure group collections** for common analytical workflows
- **Formula documentation** with calculation methodology references
- **Regulatory mapping** where applicable (e.g. which metrics satisfy which regulatory reporting requirements)

### Integration with the tenant SMR

Platform administrators integrate the Semantic Registry Service at initial SMR setup via the Admin API:

```bash
# Seed the SMR from a registry package
POST /v1/smr/import
{
  "source":  "semantic-registry-service",
  "package": "fsi-wealth-v1",
  "version": "2.3.0",
  "mode":    "merge"   # 'merge' preserves existing definitions; 'overwrite' replaces
}
```

Imported definitions are marked with `source: "semantic_registry_service"` and `source_version: "2.3.0"` in their SMR metadata. When the Semantic Registry Service publishes an updated package version, platform administrators receive a notification and may import the update via the same API.

### Governance of imported definitions

Imported metric definitions are subject to the tenant's normal SMR governance workflow — they enter as `proposed` and require Application Admin approval before becoming resolvable. Application Admins may modify the imported definition before approval if the organisation's calculation methodology differs from the published standard.

### Relationship to the platform

The Semantic Registry Service is an optional companion to the platform. Platform administrators using the `seedTemplate` config field are seeding from a cached snapshot of the relevant Semantic Registry Service package, pre-bundled at platform installation. The live Semantic Registry Service provides the most current definitions and supports packages beyond the core seed templates.

---

## Regulatory Reference Service

### Overview

The **Regulatory Reference Service** is an ecosystem service that provides up-to-date regulatory metric definitions, compliance thresholds, and reporting templates for the major financial regulatory regimes. It is a **runtime service** — registered as an execution backend that the FQP can route regulatory metric sub-plans to.

Unlike internally-managed execution backends, the Regulatory Reference Service holds the authoritative definitions and current threshold values for regulatory metrics — eliminating the need for platform administrators to maintain regulatory threshold tables internally.

### What the Regulatory Reference Service provides

| Component | Description |
|-----------|-------------|
| **Regulatory metric catalogue** | Authoritative definitions for regulatory metrics (LCR, NSFR, leverage ratio, capital ratios, etc.) aligned to current regulatory text |
| **Current threshold values** | Regulatory minima and maxima, jurisdiction-specific, updated on regulatory publication schedules |
| **Transition schedule** | Announced future threshold changes with effective dates (e.g. Basel III transition to Basel IV) |
| **Reporting templates** | Structured result formats compatible with common regulatory submission templates (XBRL, COREP, FINREP) |

### Registration in the Data Source Catalog

```json
{
  "executionBackends": [
    {
      "id":           "regulatory-reference",
      "name":         "Regulatory Reference Service",
      "type":         "custom",
      "endpoint":     "https://regulatory.analytics-ecosystem.io/engine",
      "authType":     "api-key",
      "capabilities": ["metric", "filter"],
      "dataAffinity": ["regulatory"],
      "priority":     1,
      "costTier":     "low",
      "enabled":      true
    }
  ]
}
```

When registered and enabled, the FQP routes all sub-plans with `dataAffinity: "regulatory"` to the Regulatory Reference Service first. This ensures regulatory metric values are always sourced from the authoritative service rather than from host-maintained tables that may lag regulatory updates.

### Threshold update notifications

When the Regulatory Reference Service publishes updated threshold values (e.g. a jurisdiction's minimum LCR changes), it broadcasts an update notification to all registered tenants via the platform's notification API. The Application Admin reviews the change and (if relevant) updates the tenant's SMR metric display thresholds accordingly.

### Relationship to the platform

If the Regulatory Reference Service is unavailable, the FQP falls back to the next registered engine with the `regulatory` data affinity. If no fallback is registered, regulatory sub-plans fail and the user is notified. The platform does not fabricate regulatory threshold values when the authoritative source is unavailable.

---

## Benchmark Data Service

### Overview

The **Benchmark Data Service** is an ecosystem service that provides market index and benchmark data as a registered execution backend within the analytics platform. It enables benchmark comparison queries without platform administrators needing to license, ingest, and maintain benchmark data independently.

### What the Benchmark Data Service provides

| Data category | Examples |
|-------------|---------|
| **Equity indices** | MSCI World, MSCI ACWI, S&P 500, FTSE All-World, Russell 2000 |
| **Fixed income indices** | Bloomberg Global Aggregate, ICE BofA Investment Grade, JP Morgan EMBI |
| **Multi-asset indices** | MSCI ACWI 60/40, AQR Risk Parity |
| **Custom benchmark blends** | Host-configurable blended benchmark compositions from registered components |
| **Factor indices** | MSCI Minimum Volatility, MSCI Value, MSCI Quality, MSCI Momentum |

### Registration in the Data Source Catalog

```json
{
  "executionBackends": [
    {
      "id":           "benchmark-data",
      "name":         "Benchmark Data Service",
      "type":         "custom",
      "endpoint":     "https://benchmarks.analytics-ecosystem.io/engine",
      "authType":     "api-key",
      "capabilities": ["metric", "dimension", "filter", "timeseries"],
      "dataAffinity": ["benchmarks"],
      "priority":     1,
      "costTier":     "low",
      "enabled":      true
    }
  ]
}
```

### Benchmark dimension integration

When the Benchmark Data Service is registered, the `benchmark` dimension in the SMR is backed by the service's benchmark catalogue. Users and AI agents can include benchmark IDs in the `benchmark` dimension field of MCP tool call parameters; the FQP resolves these against the service.

### Custom benchmark blends

Platform administrators may register custom benchmark blends via the Benchmark Data Service Admin API:

```json
{
  "custom_benchmark": {
    "id":          "acme_balanced_benchmark",
    "label":       "Acme Balanced Benchmark",
    "components": [
      { "benchmark_id": "b_msci_world",          "weight": 0.60 },
      { "benchmark_id": "b_bloomberg_global_agg", "weight": 0.35 },
      { "benchmark_id": "b_libor_3m",             "weight": 0.05 }
    ],
    "rebalance_frequency": "monthly"
  }
}
```

Custom benchmarks are accessible within the tenant's queries using the registered `id`.

### Data licensing

The Benchmark Data Service operates under data licensing agreements with index providers. Tenants using the service must confirm their licensing entitlement for each index they access. The service enforces licensing checks per tenant — tenants that are not licensed for a specific index cannot access that benchmark via the service.

---

## Complementary service summary

| Service | Type | Activation | Primary benefit |
|---------|------|-----------|----------------|
| Semantic Registry Service | Config-time resource | Import via Admin API | Accelerated SMR setup from vetted financial services metric definitions |
| Regulatory Reference Service | Runtime execution backend | Register in Data Source Catalog | Authoritative, up-to-date regulatory metrics without internal maintenance |
| Benchmark Data Service | Runtime execution backend | Register in Data Source Catalog | Licensed benchmark data for comparison queries without internal data licensing and ingestion |
