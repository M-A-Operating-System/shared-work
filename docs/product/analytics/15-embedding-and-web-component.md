# 15 — Embedding and Web Component

## Overview

The `<ai-analytics>` component is a **custom HTML element** that host applications embed within their own UI. It is self-contained — it manages its own state, handles the full analytical pipeline from natural language through to rendered results, and communicates with the platform API independently of the host application's framework.

The component delivers a three-zone layout:

| Zone | Location | Contents |
|------|----------|---------|
| **Query history panel** | Left sidebar | Session query history, SMR browser, saved queries |
| **Analytical workspace** | Centre — primary | Query input, rendered results, narrative, lineage inspector |
| **Context panel** | Right sidebar | Active metric definitions, result artefacts, drilldown breadcrumb, session summary |

---

## Quick start

```html
<script type="module" src="https://analytics-platform.io/sdk/v1/ai-analytics.js"></script>

<ai-analytics
  tenant-id="acme-wealth"
  user-token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  theme="light"
></ai-analytics>
```

The component renders at 100% of its container's width and height.

---

## HTML attributes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `tenant-id` | Yes | string | Tenant identifier from the application config |
| `user-token` | Yes | string | Host-authenticated user JWT. Must contain role claims for projection. |
| `theme` | No | `"light"` \| `"dark"` | Colour scheme. Default: `"light"`. |
| `locale` | No | string | BCP 47 locale tag. Overrides tenant config `scope.language` for UI strings and number formatting. |
| `initial-query` | No | string | Pre-populate the query input with a specific question on mount. Useful for deep-linking from the host application. |
| `smr-panel-visible` | No | boolean | Whether the SMR browser panel opens on first mount. Default: `false`. |

---

## Authentication bridge

The platform validates the host-issued JWT and extracts:

### Required JWT claims

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User's unique identifier within the tenant |
| `tenant_id` | string | Must match the `tenant-id` attribute |
| `exp` | number | JWT expiry time |

### Required analytical claims

| Claim | Type | Description |
|-------|------|-------------|
| Any field matching `entitlements.roleClaimField` | string[] | User's analytical role array. Used by the Role-Aware Projection Layer. |

### Optional claims

| Claim | Type | Description |
|-------|------|-------------|
| `managed_portfolios` | string[] | Portfolio IDs managed by this user — resolved in row predicate templates |
| `entity_ids` | string[] | Legal entities the user is associated with — for multi-entity deployments |
| `display_name` | string | User's display name for lineage records and audit trail |
| Any other claim referenced in role `rowPredicates` | * | Any claim value referenced by `{{user.claim_name}}` in predicate templates |

---

## JavaScript API

```javascript
const analytics = document.querySelector('ai-analytics');
```

### Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `updateToken(token)` | `token: string` | Refresh the user JWT without remounting |
| `submitQuery(query)` | `query: string` | Programmatically submit a natural language query |
| `clearSession()` | — | Clear the current session's query history and results |
| `openSMRBrowser()` | — | Open the SMR metric browser panel |
| `setLocale(locale)` | `locale: string` | Change number formatting locale at runtime |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `activeMetrics` | `string[]` | Metric IDs in the most recent result |
| `isExecuting` | `boolean` | Whether a query is currently in execution |
| `lastLineageId` | `string \| null` | Lineage ID of the most recent completed query |

---

## Events

| Event | Detail payload | Description |
|-------|---------------|-------------|
| `query-submitted` | `{ naturalLanguage, sessionId }` | Fired when user submits a query |
| `intent-resolved` | `{ intentPattern, metrics, dimensions, dslExpression }` | Fired after Semantic Intent Layer resolution |
| `governance-blocked` | `{ reason, circuitBreaker, estimatedCost, costLimit }` | Fired when a query is blocked by governance |
| `query-complete` | `{ lineageId, metrics, rowCount, latencyMs, cacheHit }` | Fired when a query completes successfully |
| `query-error` | `{ error, errorType, lineageId }` | Fired on execution error |
| `drilldown-navigated` | `{ hierarchy, level, selectedValue, lineageId }` | Fired on governed drilldown traversal |
| `result-exported` | `{ format, lineageId, filename }` | Fired when user exports a result |
| `metric-definition-viewed` | `{ metricId, metricVersion }` | Fired when user views a metric definition from the SMR browser |
| `token-expired` | — | Fired when user JWT approaches expiry |

### Handling `governance-blocked`

```javascript
analytics.addEventListener('governance-blocked', (event) => {
  const { reason, circuitBreaker, estimatedCost, costLimit } = event.detail;
  
  // Host application may log this for operational monitoring
  telemetry.track('analytics.governance_block', {
    circuit_breaker: circuitBreaker,
    estimated_cost:  estimatedCost,
    cost_limit:      costLimit
  });
});
```

### Handling `query-complete` for host application integration

```javascript
analytics.addEventListener('query-complete', (event) => {
  const { lineageId, metrics, rowCount } = event.detail;
  
  // Host application may link analytical results to their own workflow
  if (metrics.includes('var_95') && rowCount > 0) {
    riskManagementApp.flagForReview(lineageId);
  }
});
```

---

## Sizing and layout

The `<ai-analytics>` component renders at **100% width and 100% height** of its container.

### Minimum dimensions

| Dimension | Minimum |
|-----------|---------|
| Width | 480px |
| Height | 500px |

Below minimum dimensions, a fallback state is displayed.

### Responsive layout breakpoints

| Viewport width | Layout |
|---------------|--------|
| ≥ 1280px | Full three-zone layout |
| 1024px–1279px | Context panel collapses to icon rail |
| 768px–1023px | Both panels as slide-in drawers |
| < 768px | Single-column; query input pinned to bottom; panels as bottom sheets |

---

## Content Security Policy

```
script-src    https://analytics-platform.io [renderer module origins];
connect-src   https://api.analytics-platform.io;
img-src       https://cdn.analytics-platform.io;
style-src     https://analytics-platform.io 'nonce-{page-nonce}';
```

---

## Framework wrappers

**React:**
```jsx
import { AiAnalytics } from '@analytics-platform/react';

<AiAnalytics
  tenantId="acme-wealth"
  userToken={jwt}
  onQueryComplete={({ lineageId, metrics }) => handleResult(lineageId, metrics)}
  onGovernanceBlocked={({ circuitBreaker }) => logBlock(circuitBreaker)}
/>
```

**Vue:**
```vue
<AiAnalytics
  tenant-id="acme-wealth"
  :user-token="jwt"
  @query-complete="handleResult"
/>
```

---

## Query history panel

The left panel shows all queries from the current session and (optionally) saved queries from prior sessions:

```
┌─────────────────────────────┐
│  🔍 Search queries           │
│  + New query                 │
├─────────────────────────────┤
│  📊 SMR Metric Browser       │
├─────────────────────────────┤
│  This session                │
│  — 09:32 —                  │
│  Portfolio QTD vs benchmark  │
│  — 09:45 —                  │
│  VaR breach investigation    │
├─────────────────────────────┤
│  Saved queries               │
│  Morning risk brief          │
│  IC preparation pack         │
└─────────────────────────────┘
```

---

## SMR metric browser

Accessible via the left panel, the SMR browser lets users explore registered metrics within their entitlement scope:

- Searchable catalogue of accessible metrics
- Full metric definition: formula (human-readable), unit, aggregation rules, data refresh cadence
- Lineage: upstream sources, downstream metrics
- Owner and steward contact
- Version history (for Power Analysts and above)
- *"Query this metric"* button that pre-populates the query input

Metrics outside the user's entitlement scope are not visible in the browser.
