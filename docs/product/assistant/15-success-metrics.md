# 14 — Success Metrics

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---


## Governing principle

Metrics are captured from day one at both the platform level (across all tenants) and at the application level (per tenant). Platform-level targets reflect the health of the infrastructure and ecosystem. Application-level targets reflect the value each host application is delivering to its users. Baseline targets for new tenants are set at the end of month 1 based on observed behaviour.

---

## Platform-level metrics

These metrics are tracked across all tenants by the platform team.

| Metric | Definition | Target |
|--------|-----------|--------|
| **Active tenants** | Tenants with at least one active session in the 7-day window | Growth metric — tracked weekly |
| **Platform uptime** | API availability (p99 latency < 2s; error rate < 0.1%) | 99.9% |
| **MCP tool error rate (platform)** | Tool invocations with non-2xx response across all tenants | < 3% |
| **Cache hit rate (platform)** | `cache_read_input_tokens` ÷ total input tokens across all tenants | ≥ 40% by month 2 |
| **Tenant onboarding time** | Time from tenant registration to first active session | Baseline month 1 |
| **Improvement signal volume** | Total signals across all tenants per week | Baseline month 1; monitor trend |
| **Config validation failure rate** | Config submissions that fail validation ÷ total submissions | < 10% |

---

## Application-level metrics

These metrics are tracked per tenant and reported to the Application Admin via the tenant analytics dashboard.

| Metric | Definition | Target |
|--------|-----------|--------|
| **Weekly active users (WAU)** | Distinct users opening a session in a 7-day window | 40% of the tenant's eligible user base by day 90 |
| **Queries per session** | Mean user messages per conversation | ≥ 4 |
| **Workflow invocation rate** | Sessions invoking at least one guided workflow | ≥ 25% where workflows are configured |
| **Binding click-through** | Sessions where user clicks a binding chip (fires `binding-click` event) | ≥ 30% |
| **MCP tool error rate (application)** | Tool invocations with error in the tenant | < 3% |
| **User satisfaction (CSAT)** | Post-session rating (1–5) where offered | Mean ≥ 4.0 |
| **Improvement signal rate** | Improvement signals per 100 turns | Baseline month 1; reduction month-over-month |
| **Cache hit rate (application)** | Cache hit rate for this tenant's sessions | ≥ 40% by month 2 |
| **Document attachment rate** | Sessions with at least one document attachment | Baseline month 1 |
| **Artefact download rate** | Sessions with at least one artefact download | ≥ 20% |
| **Mobile session share** | Sessions on mobile/tablet viewport | Baseline month 1 |
| **Shared conversation rate** | Conversations with at least one invitation sent | Baseline month 1 |
| **Participant acceptance rate** | Invitations accepted ÷ total invitations sent | ≥ 70% |

---

## Metric definitions

### Weekly active users
A user is counted once per 7-day window regardless of session count. "Active" means at least one user message submitted — opening the component without sending a message does not count.

### Queries per session
Total user messages ÷ total conversation sessions in the period. Excludes sessions with zero user messages.

### Workflow invocation rate
A session counts if at least one guided workflow was invoked via any method: Workflow Library click, `@`-binding, or natural-language trigger.

### Binding click-through
A session counts if at least one binding chip in an assistant response was clicked (firing the `binding-click` event to the host application). Tracks whether users are using the assistant as a gateway into the host application, not just a standalone Q&A surface.

### MCP tool error rate
Tool invocations with a non-2xx response or an empty result set (where results were expected) ÷ total tool invocations. The "expected results" qualifier requires a confidence classifier — baseline tracks simple error rate only until the classifier is calibrated.

### User satisfaction (CSAT)
Post-session rating prompt (1–5 stars) shown to a random sample configured via `features.csatSampleRate` (default: 20% of sessions).

### Improvement signal rate
Total improvement signals (all types) per 100 conversation turns, tracked by signal type. Month-over-month reduction in signal rate per type indicates the improvement pipeline is working.

### Cache hit rate
`cache_read_input_tokens` ÷ (`input_tokens` + `cache_read_input_tokens`) per the AI provider API response. Tracked at session level and rolling daily average. A target of ≥ 40% by month 2 reflects the expectation that the system prompt and tool descriptions will be consistently cached after the first turn in each session.

### Document attachment rate
Sessions where the user attached at least one document (PDF, Excel, Word, or image). Baseline metric — no target until month 1 data is available.

### Artefact download rate
Sessions where the user downloaded at least one artefact from the artefact tray. Tracks whether users find rendered outputs useful enough to take away.

### Mobile session share
Sessions where the viewport width is < 768px (mobile) or 768px–1023px (tablet) at any point during the session. Baseline metric to validate mobile-first investment.

### Shared conversation rate
Conversations where at least one invitation was sent (regardless of acceptance). Tracks collaborative usage.

### Participant acceptance rate
Invitations accepted ÷ total invitations sent. A low rate may indicate users are inviting the wrong people, or that the invitation UX needs improvement.

---

## Measurement responsibilities

| Metric | Source | Owner |
|--------|--------|-------|
| WAU, queries per session, CSAT, attachment rate, artefact download, mobile share, shared rate, acceptance rate | `assistant` schema + session analytics | Platform Engineering |
| Workflow invocation rate, binding click-through | `assistant.tool_calls` + binding click events | Platform Engineering |
| MCP tool error rate | `assistant.tool_calls.status` | Platform Engineering |
| Improvement signal rate | `assistant.improvement_signals` | Platform team + Application Admin |
| Cache hit rate | AI provider API response metadata stored in `assistant.turns` | Platform Engineering |
| Platform uptime, config validation failure rate | Platform infrastructure monitoring | Platform Engineering |

---

## Review cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | WAU, tool error rate, CSAT per tenant — operational health | Platform Engineering |
| **Weekly** | Application Admin reviews improvement signal issues for their tenant | Application Admin |
| **Monthly** | Full metric review; signal rate analysis; cache hit trend | Platform team + Application Admins |
| **Day 90 (per tenant)** | Activation target assessment (40% WAU); decision on next feature priorities | Application Admin + Platform team |

---

## Tenant analytics dashboard

Each tenant's Application Admin has access to a **read-only analytics dashboard** showing their tenant's application-level metrics over time:
- WAU trend (30-day rolling)
- Queries per session trend
- CSAT distribution
- Top improvement signal types
- MCP tool error rate by server
- Cache hit rate trend

Platform-level metrics (cross-tenant) are visible to the Platform team only.
