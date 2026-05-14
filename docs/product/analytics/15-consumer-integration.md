# 15 — Consumer Integration

## Overview

The AI Analytics Platform is consumed exclusively via its **MCP Capability Layer** — a single endpoint that accepts MCP-protocol tool calls and returns structured JSON responses. There is no embeddable component, no client-side SDK, and no rendering layer. Any MCP-compatible consumer — a conversational AI assistant, an autonomous agent, a custom application, or a report pipeline — integrates in the same way.

This document describes the integration contract: authentication, request format, response handling, and error patterns. For the full MCP tool catalogue (available capabilities, parameters, and examples), see [08-mcp-capability-layer.md](./08-mcp-capability-layer.md).

---

## Authentication

Every request to the MCP endpoint must carry a **host-issued JWT** in the `Authorization: Bearer <token>` header. The platform validates the JWT and extracts the user's identity and entitlement claims.

### Required JWT claims

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User's unique identifier within the tenant |
| `tenant_id` | string | Must match the tenant's registered `tenantId` |
| `exp` | number | JWT expiry timestamp |

### Required analytical claims

| Claim | Type | Description |
|-------|------|-------------|
| Any field matching `entitlements.roleClaimField` | `string[]` | User's analytical role array. Used by the Role-Aware Projection Layer to determine metric and dimension access. |

### Optional claims

| Claim | Type | Description |
|-------|------|-------------|
| `managed_portfolios` | `string[]` | Portfolio IDs managed by this user — resolved in row predicate templates |
| `entity_ids` | `string[]` | Legal entities the user is associated with |
| `display_name` | string | User's display name for lineage records and audit trail |
| Any claim referenced in role `rowPredicates` | any | Any value referenced by `{{user.claim_name}}` in predicate templates |

Tokens with no matching analytical role receive an `ENTITLEMENT_DENIED` error (or a public-access metric set, if `defaultDenyAll: false`). Expired tokens are rejected at the authentication boundary.

---

## MCP endpoint

```
POST https://api.analytics-platform.io/v1/mcp
Authorization: Bearer <host-issued-JWT>
Content-Type: application/json
```

The request body follows the MCP Streamable HTTP transport protocol. See [08-mcp-capability-layer.md](./08-mcp-capability-layer.md) for available tools and their input schemas.

---

## Response structure

A successful response returns a JSON object. See [10-analytical-output-format.md](./10-analytical-output-format.md) for the full output specification.

```json
{
  "result_id":   "res_20260514_093247_a1b2c3",
  "lineage_url": "https://api.analytics-platform.io/v1/lineage/res_...",
  "display_spec": {
    "type": "chart" | "table",
    ...
  },
  "narrative": { ... },
  "meta": {
    "latencyMs": 1285,
    "cacheHit":  false,
    "rowCount":  14,
    "costUnits": 500
  }
}
```

### Handling `display_spec`

Consumers branch on `display_spec.type`:

- `"chart"` — render using a chart grammar library of the consumer's choosing. The SCL spec includes `mark`, `data.values`, `encoding`, `colorScheme`, and `formatHints`. See the technical specification for the full SCL schema and recommended rendering libraries.
- `"table"` — render as a data grid. The spec includes `columns` (with labels and format hints), `data`, and optional `thresholds` for cell highlighting.

The platform governs *which* chart contract is selected and *how* it is parameterised. The consumer governs *how* it is rendered.

### Handling `narrative`

`narrative` is present when `features.narrativeSynthesis` is enabled and the result meets the synthesis threshold. The consumer may display `narrative.lead` and `narrative.detail` as prose, or pass them to a downstream document assembly pipeline. `narrative.anchoredTo` links the prose to the governing result record.

### Handling `meta`

`meta` is provided for observability. Consumers may pass `latencyMs`, `cacheHit`, and `costUnits` to their own telemetry pipeline, or surface them in a developer/admin overlay.

---

## Token refresh

JWTs issued by the consuming application expire per the organisation's standard session policy. When a token approaches expiry:

1. The consuming application issues a refreshed JWT.
2. The consumer includes the new token in the next request header.
3. No re-authentication step is required on the platform side — the new JWT is validated at the boundary of each request.

For long-running agentic consumers, the consuming application must supply fresh JWTs before the previous token's `exp` timestamp.

---

## Drilldown continuity

When a consumer receives a response with a `result_id`, they may pass that ID to the `drilldown` MCP capability to traverse analytical hierarchies while preserving the parent result's governance context:

```json
{
  "tool": "drilldown",
  "input": {
    "result_id":    "res_20260514_093247_a1b2c3",
    "hierarchy":    "asset_class_hierarchy",
    "selected_value": "EQUITY"
  }
}
```

The platform looks up the original result's projection scope, role filters, and entitlement context from the lineage store and applies them to the drilldown query. The consumer does not need to re-specify the original query parameters.

---

## Error handling

All errors return a structured MCP error response:

```json
{
  "error": {
    "code":      "GOVERNANCE_COST_EXCEEDED",
    "message":   "Estimated cost 1,400 units exceeds limit 1,000. Narrow the query scope.",
    "result_id": "res_20260514_094002_b3c4d5"
  }
}
```

The `result_id` is present on all error responses, including governance-blocked requests. This ensures every request — successful or not — appears in the audit trail and is reachable via the lineage API.

For the full error code catalogue, see [10-analytical-output-format.md](./10-analytical-output-format.md).

---

## Agentic consumers

Autonomous agents (scheduled pipelines, event-triggered monitors, report generators) integrate identically to interactive consumers. The only differences are:

- **JWT issuance** — the host must provision service-level JWTs for agents, scoped to the agent's role (not a user's identity). The agent's JWT must include role claims that reflect the data access the agent is authorised for.
- **No elevated privilege** — the Role-Aware Projection Layer applies the same entitlement enforcement to agent JWTs as to user JWTs. An agent cannot access data that a user with the same role cannot access.
- **Lineage** — every agent-initiated request is recorded in the Analytical Lineage Store under the agent's `sub` claim. Agent queries are distinguishable from user queries via the audit trail.

See [00-overview.md — Agentic consumers](./00-overview.md) for the full list of anticipated agent patterns and their governance implications.
