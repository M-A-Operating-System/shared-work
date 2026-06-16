# 12 — Continuous Improvement

## Principle

The AI Chat Platform is a living system. Every session generates signal data. **No change is applied automatically** — every recommendation enters a triage pipeline and requires human review before any change is deployed (P8 — human-gated improvement).

The improvement framework generates: **signal → triage → issue → approval → deploy**. It does not generate signal → auto-patch.

---

## Improvement signals

Five types of improvement signal are captured automatically from day one:

| Signal type | Detection | Auto-issue? |
|-------------|----------|-------------|
| **Explicit turn report** | User clicks the report icon on any turn and submits the modal — optionally with a written explanation | Always |
| **Query retry / rephrase** | User submits a substantially similar query within two turns | If confidence ≥ threshold |
| **MCP tool failure or empty result** | Tool call log shows error or zero-result set where results were expected | If confidence ≥ threshold |
| **In-conversation correction** | User explicitly corrects the assistant mid-session | If confidence ≥ threshold |
| **Out-of-scope response** | Response contains no tool invocation and no domain-specific content for a query that should have triggered one | If confidence ≥ threshold |

### Explicit turn report — detail

The report icon appears on every turn (user and assistant). When a user submits a report:

- The turn `id`, `conversation_id`, `tenant_id`, `reporter_user_id`, optional `explanation` text, and a timestamp are stored in `assistant.improvement_signals`
- The signal always generates an improvement issue — no confidence threshold
- The improvement issue includes: the full turn content, the reporter's explanation (if provided), the preceding and following turns for context, and the MCP tool call log for the turn

The written explanation is the most valuable signal — it describes the problem in plain language without inference. Users should be encouraged (via the modal copy) to describe what was wrong and why.

### Signal lifecycle

Each signal is stored in `assistant.improvement_signals` with a lifecycle status:

```
new → triaged → issued → resolved
```

| Status | Description |
|--------|-------------|
| `new` | Signal captured; awaiting triage |
| `triaged` | Reviewed; decision made on whether to raise an improvement issue |
| `issued` | Improvement issue created; signal linked to issue reference |
| `resolved` | Underlying change deployed and validated |

### Confidence threshold

Automatically detected signals below the confidence threshold queue for **manual review first** before an improvement issue is raised. The exact threshold is set at launch and adjusted based on signal volume.

Explicit user reports bypass the confidence threshold and **always generate an improvement issue**.

---

## Improvement issue pipeline

Qualifying signals are processed into an improvement issue containing:

| Issue element | Content |
|--------------|---------|
| Failure description | Signal type, turn summary, and assistant output excerpt |
| Full conversation turn | Raw prompt, resolved prompt, tool call log, and assistant response |
| MCP tool call log | All tool invocations for the turn (server name, tool name, params, result, latency) |
| System-generated recommendation | Most likely remediation target — see table below |
| Tenant context | `tenant_id`, application name, config version active at the time |

### Remediation targets

| Remediation target | When recommended |
|-------------------|-----------------|
| Host system prompt | Assistant goes out of scope, misrepresents capabilities, uses wrong terminology for the user's communication style |
| MCP tool description | Assistant chooses the wrong tool or fails to invoke a tool when it should |
| Guided workflow prompt | A workflow returns unhelpful or incomplete output |
| Bindable type `contextTemplate` | Binding resolution provides insufficient or incorrect context for the model |
| Application context | Out-of-date or missing application-level memory causing incorrect assumptions |

### Routing

Improvement issues are:
1. **Always** visible to the Platform team for platform-level patterns
2. **Optionally forwarded to the host application** via the tenant's configured improvement webhook (see below)

Host applications that configure an improvement webhook receive structured JSON payloads for each qualifying signal, enabling their Application Admin to triage within their own tooling.

### Improvement webhook (optional)

Host applications may configure an improvement webhook endpoint in the Platform Admin API. When configured:
- Qualifying improvement signals (above threshold or explicit user reports) trigger a POST to the webhook URL with a structured JSON payload
- The payload includes: `tenant_id`, `signal_type`, `turn_summary`, `remediation_recommendation`, `issue_id`
- Authentication: the platform signs webhook payloads with an HMAC key provided at registration

---

## Improvement cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | Application Admin reviews new improvement issues for their tenant; advances high-confidence items | Application Admin (per tenant) |
| **Weekly** | Platform team reviews platform-level patterns across all tenants | Platform team |
| **Monthly** | Aggregate signal analysis; identify systemic patterns; set remediation priorities | Application Admin + Platform team |
| **Per release** | Post-change validation — monitor signal volume for the affected signal type for two weeks after deployment | Host development team + Platform team |

---

## What the improvement framework does not do

| Action | Status |
|--------|--------|
| Auto-update the host system prompt based on signals | Not permitted — all changes require host team review and config update |
| Auto-retrain or fine-tune the AI model | Not in scope — the platform uses foundation AI provider models |
| Apply changes to guided workflow prompts automatically | Not permitted — workflow changes require host team config update |
| Apply changes to MCP tool descriptions automatically | Not permitted |
| Close improvement issues without human triage | Not permitted — every issue requires Application Admin or Platform team review |
| Share improvement signal content across tenants | Not permitted — signals are tenant-scoped and never exposed to other tenants |
