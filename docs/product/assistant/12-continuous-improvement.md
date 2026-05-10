# 12 — Continuous Improvement

## Principle

Data AI Assistant is a living system. Every session generates signal data. **No change is applied automatically** — every recommendation is raised as a GitHub issue and follows the standard DDA 13-stage product approval pipeline before any change is made (P8 — human-gated improvement).

The improvement framework generates signal → triage → issue → approval → deploy. It does not generate signal → auto-patch.

---

## Improvement signals

Five types of improvement signal are captured automatically from day one:

| Signal type | Detection | Auto-issue? |
|-------------|----------|-------------|
| **Explicit turn report** | User clicks the report icon on any turn (user or assistant) and submits the modal — optionally with a written explanation | Always |
| **Query retry / rephrase** | User submits a substantially similar query within two turns | If confidence ≥ threshold |
| **MCP tool failure or empty result** | Tool call log shows error or zero-result set where results were expected | If confidence ≥ threshold |
| **In-conversation correction** | User explicitly corrects the model mid-session (e.g. *"That's wrong, it should be…"*) | If confidence ≥ threshold |
| **Out-of-scope response** | Response contains no MCP tool invocation and no entity references for a query that should have triggered one | If confidence ≥ threshold |

### Explicit turn report — detail

The report icon appears on every turn. When a user submits a report:

- The turn `id`, `conversation_id`, `reporter_user_id`, optional `explanation` text, and a timestamp are stored in `assistant.improvement_signals`
- The signal always generates a GitHub issue — no confidence threshold
- The GitHub issue includes: the full turn content, the reporter's explanation (if provided), the preceding and following turns for context, and the MCP tool call log for the turn

The written explanation is the most valuable signal — it tells the CDAiO exactly what was wrong and why, without inference. Users should be encouraged (via the modal copy) to describe the issue in plain language.

### Signal lifecycle

Each signal is stored in `assistant.improvement_signals` with a lifecycle status:

```
new → triaged → issued → resolved
```

| Status | Description |
|--------|-------------|
| `new` | Signal captured; awaiting triage |
| `triaged` | Reviewed by CDAiO; decision made on whether to raise a GitHub issue |
| `issued` | GitHub issue created; signal linked to issue number |
| `resolved` | Underlying change deployed and validated |

### Confidence threshold

Automatically detected signals below the confidence threshold queue for **manual review first** before a GitHub issue is raised. The exact threshold is set by the CDAiO at launch and adjusted based on signal volume.

Explicit user reports (submitted via the report icon) bypass the confidence threshold and **always generate a GitHub issue**.

---

## GitHub issue pipeline

Qualifying signals are automatically processed into a GitHub issue containing:

| Issue element | Content |
|--------------|---------|
| Failure description | Signal type, turn summary, and model output excerpt |
| Full conversation turn | Raw prompt, resolved prompt, tool call log, and model response |
| MCP tool call log | All tool invocations for the turn (tool name, params, result, latency) |
| System-generated recommendation | Most likely remediation target — see table below |

### Remediation targets

| Remediation target | When recommended |
|-------------------|-----------------|
| System prompt | Model goes out of scope, misrepresents capabilities, uses wrong terminology for user's `communication_style` |
| Entity registry | MCP tool returns incomplete or incorrect data; `entityRegistry.ts` / `entityMeta.ts` binding resolution is wrong |
| MCP tool description | Model chooses the wrong tool or fails to invoke a tool when it should |
| Guided workflow prompt | A guided workflow returns unhelpful or incomplete output |

Issues enter the DDA triage pipeline at the **Classifier stage** of the 13-stage product approval process.

---

## Improvement cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | Triage new signal issues; advance high-confidence items to PDD stage | CDAiO |
| **Monthly** | Aggregate signal analysis; identify systemic patterns; set remediation priorities | CDAiO |
| **Per release** | Post-change validation: monitor signal volume for the affected signal type for two weeks after deployment | Engineering + CDAiO |

---

## What the improvement framework does not do

| Action | Status |
|--------|--------|
| Auto-update the system prompt based on signals | Not permitted — all changes require human approval |
| Auto-retrain or fine-tune the model | Not in scope — Data AI Assistant uses Anthropic's foundation models |
| Apply changes to guided workflow prompts automatically | Not permitted |
| Apply changes to `entityRegistry.ts` or `entityMeta.ts` automatically | Not permitted |
| Close improvement issues without human triage | Not permitted — every issue requires CDAiO review |
