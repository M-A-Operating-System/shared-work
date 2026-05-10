# 14 — Success Metrics

## Governing principle

Metrics are captured from day one. Targets for baseline metrics are set at the end of month 1 based on observed behaviour — not assumed in advance. Targets for activation and engagement metrics are set for the day 90 milestone.

---

## Launch metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Weekly active users** | Distinct users opening a Data AI Assistant session in a 7-day window | 40% of DDA active users by day 90 |
| **Queries per session** | Mean user messages per conversation | ≥ 4 |
| **Guided workflow invocation rate** | Sessions invoking at least one guided workflow | ≥ 25% |
| **Entity link click-through** | Sessions where user clicks a Display ID or binding chip link | ≥ 30% |
| **MCP tool error rate** | Tool invocations resulting in an error | < 3% |
| **User satisfaction (CSAT)** | Post-session rating (1–5) where offered | Mean ≥ 4.0 |
| **Improvement signal rate** | Improvement signals captured per 100 turns | Baseline month 1; target reduction month-over-month |
| **Cache hit rate** | Input tokens served from the Anthropic prompt cache vs. computed | ≥ 40% by month 2 |
| **Document attachment rate** | Sessions including at least one document attachment | Baseline month 1 |
| **Artefact download rate** | Sessions with at least one artefact download | ≥ 20% |
| **Mobile session share** | Sessions on a mobile or tablet viewport | Baseline month 1 |
| **Shared conversation rate** | Proportion of conversations shared with at least one other user | Baseline month 1 |
| **Participant acceptance rate** | Proportion of shared conversation invitations accepted vs. declined | Target ≥ 70% |

---

## Metric definitions

### Weekly active users
A user is counted once per 7-day window regardless of how many sessions they open. "Active" means at least one user message submitted — opening the page without sending a message does not count.

### Queries per session
Calculated as total user messages ÷ total conversation sessions in the period. Excludes sessions with zero user messages (app opens without interaction).

### Guided workflow invocation rate
A session counts if at least one guided workflow was invoked via any method: Guided Workflows drawer click, `@`-binding, or natural-language trigger.

### Entity link click-through
A session counts if at least one binding chip or Display ID link in an assistant response was clicked and navigated to the DDA UI. Tracks whether users are using Data AI Assistant as a gateway to the platform, not just a standalone Q&A surface.

### MCP tool error rate
Calculated as tool invocations with a non-2xx response or an empty result set (where results were expected) ÷ total tool invocations. The "expected results" qualifier requires a confidence classifier — baseline is simple error rate only until the classifier is built.

### User satisfaction (CSAT)
Post-session rating prompt (1–5 stars) shown to a random 20% sample of sessions. Not shown on every session to avoid survey fatigue.

### Improvement signal rate
Total improvement signals (all types) captured per 100 conversation turns. Tracked by signal type to identify which category drives the most volume. Month-over-month reduction in signal rate per signal type indicates the improvement pipeline is working.

### Cache hit rate
`cache_read_input_tokens` ÷ (`input_tokens` + `cache_read_input_tokens`) per the Anthropic API response. Tracked at session level and rolling daily average. Target of ≥ 40% by month 2 reflects the expectation that the DDA system prompt and tool descriptions will be consistently cached after the first turn in each session.

### Document attachment rate
Sessions where the user attached at least one document (PDF, Excel, or Word). Baseline metric — no target until month 1 data is available.

### Artefact download rate
Sessions where the user downloaded at least one artefact from the artefact tray. Tracks whether users find the rendered outputs useful enough to take away.

### Mobile session share
Sessions where the viewport width is < 768px (mobile) or 768px–1023px (tablet) at any point during the session. Baseline metric to validate the business case for mobile-first investment.

### Shared conversation rate
Conversations where at least one invitation was sent (regardless of acceptance). Tracks collaborative usage patterns.

### Participant acceptance rate
Invitations accepted ÷ total invitations sent. A low rate may indicate that users are inviting the wrong people, or that the invitation UX needs improvement.

---

## Measurement responsibilities

| Metric | Source | Owner |
|--------|--------|-------|
| WAU, queries per session, CSAT, attachment rate, artefact download rate, mobile share, shared conversation rate, acceptance rate | `assistant` Postgres schema + session analytics | Engineering |
| Guided workflow invocation rate, entity link click-through | `assistant.tool_calls` + binding click events | Engineering |
| MCP tool error rate | `assistant.tool_calls.status` | Engineering |
| Improvement signal rate | `assistant.improvement_signals` | CDAiO |
| Cache hit rate | Anthropic API response metadata (`cache_read_input_tokens`) stored in `assistant.turns` | Engineering |

---

## Review cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | WAU, tool error rate, CSAT — operational health | Engineering |
| **Monthly** | Full metric review; signal rate analysis; cache hit trend | CDAiO + Engineering |
| **Day 90** | Activation target assessment (40% WAU); decision on next phase prioritisation | CDAiO |
