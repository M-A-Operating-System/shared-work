# 06 — Model Configuration

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---


## AI provider architecture

The AI Chat Platform is designed to be **AI provider-agnostic**. The model provider is abstracted behind the platform's edge function layer — the conversational surface, MCP tool access, `@`-binding resolution, and audit trail are identical regardless of which AI provider is active for a tenant.

| Release | Provider examples |
|---------|-----------------|
| **v1 (current)** | One AI provider configured per tenant — host selects from the platform's supported providers at tenant registration |
| **Planned** | Multiple providers available for selection; model capability parity validated across providers before enablement |

The provider abstraction means host applications select provider as well as model tier at the tenant level. The conversational surface, MCP tool access, `@`-binding resolution, and audit trail are identical regardless of which provider is active. See [ROADMAP.md](./ROADMAP.md) for the multi-provider timeline.

---

## Model tiers

The platform exposes three **model tiers** that host applications configure in their `models` section. Each tier maps to the configured provider's appropriate model — the host config uses tier names, not provider-specific model IDs.

| Tier | Config value | Profile | Typical use |
|------|-------------|---------|------------|
| **Standard** | `"standard"` | Default — balanced capability and speed | General queries, data lookup, summaries, diagram generation |
| **Powerful** | `"powerful"` | Maximum capability, higher latency and cost | Complex multi-entity reasoning, cross-domain analysis, large document analysis |
| **Fast** | `"fast"` | Fastest, lowest latency and cost | Quick lookups, simple factual answers, Display ID resolution |

The platform maps each tier to the provider's current best-fit model at the time of session start. When the provider releases a new model, the platform updates the tier mapping — host application configs do not need to change.

---

## Model switching

Users may switch the active model tier at any point in a conversation. The switch takes effect on the **next turn** — it does not re-process previous turns.

The host-configured system prompt, MCP tool access, and `@`-binding resolutions are identical across all tiers within the active provider.

Host applications configure the allowed tiers and default tier in the `models` section of the application config. Users can only switch to tiers in the `allowedModels` list. Setting `userCanSwitch: false` locks all sessions to the `defaultModel` tier.

### Model UI

- The **active model chip** is displayed adjacent to the input field — always visible regardless of scroll position.
- Clicking the chip opens a **model selection popover** showing all allowed models with their profiles and recommended-use summary.
- Each assistant turn carries a **hover-visible metadata line**: model label + token counts (e.g. `↑ 1,240 in · ↓ 847 out · ⚡ 312 cached`).
- The model label on each response enables participants in shared conversations to see which model was active for each turn.

### Model in shared sessions

The active model and any opt-in MCP tools apply to the session as a whole. The user who submits a message determines the model context for that turn, based on their current model chip selection. Other participants see the model label on each assistant response.

---

## Communication style and verbosity

The model's communication style and verbosity are driven by **claims in the user's authenticated JWT** — not a chat-specific setting. This keeps the assistant experience consistent with the rest of the host application, where user preferences are already managed.

Host applications configure which JWT claim fields map to style and verbosity, and define the prompt text for each value, in the `userProfile` section of the application config (see [01-host-application-config.md](./01-host-application-config.md)).

### Example style definitions

Host applications define their own style values and descriptions. Below is an example configuration:

| Style value | Example prompt instruction |
|-------------|---------------------------|
| `technical` | Respond with technical precision. Include field names, IDs, and system details. |
| `business` | Respond in plain business language. Avoid jargon. Use analogies where helpful. |
| `executive` | Respond concisely in three to five sentences. Lead with the conclusion. Omit process detail. |

### Response verbosity

| Verbosity value | Behaviour |
|----------------|----------|
| `concise` | Direct answers; minimal preamble; tables preferred over prose lists |
| `standard` | Balanced explanation with supporting context |
| `detailed` | Full explanation including methodology, caveats, and follow-up suggestions |

### Where the settings live

Profile fields are managed in the host application — not within the chat interface. The chat surface reflects the profile settings via a **read-only link** in the input footer (e.g. `Business · Standard`). It is not an editable inline control, but it is clickable and navigates to the host application's profile settings page (configurable as a deep link or via the `userProfile` config).

If no `userProfile` config is provided by the host, or if the user's JWT contains no matching claims, the assistant uses a single neutral default tone with no style injection.

### Technical depth signal for non-technical styles

When a user's style is configured to a non-technical value (e.g. `business` or `executive`) and their question genuinely requires technical detail for a correct answer, the model should:

1. Answer in the user's configured style — plain language, no jargon
2. Append a brief signal at the end of the response: *"A more detailed technical breakdown is available — ask me for the full technical view."*

The user can then request the technical version in their next message. The profile default is restored on the following turn. The model does **not** silently switch style, does **not** omit information that would make the answer misleading, and does **not** refuse to answer.

### Per-turn style override

Users may override the communication style for a single turn using natural-language instruction (e.g. *"Give me the full technical details"*). The profile default is restored automatically on the next turn.

### Style in shared conversations

Each user's style settings apply to the turns they submit. A response generated for a `technical` user may sit alongside a response generated for a `business` user within the same thread. The style label is visible on each assistant response.

---

## System prompt

The platform assembles the system prompt from multiple layers before each session. Layers are injected in the order below — platform-managed non-overridable layers come first so the model encounters behavioral constraints before any host-authored content, ensuring they cannot be suppressed by a host system prompt. Host-authored content is always last.

| # | Layer | Source | Editable by |
|---|-------|--------|------------|
| 1 | **Session context block** | Platform — identity config + JWT claims + server clock | Platform; claim field mappings in `userProfile.sessionContext` |
| 2 | **Write confirmation flow** | Platform — model must propose before/after state and await confirmation before any write MCP call | Non-overridable |
| 3 | **Transparency instruction** | Platform — model must show all tool calls and cite sources | Non-overridable |
| 4 | **Prompt injection mitigation** | Platform — model must treat tool result content as data, not instructions | Non-overridable |
| 5 | **Uncertainty acknowledgment** | Platform — model must signal uncertainty, offer search, or acknowledge gaps rather than producing confident answers from incomplete information | Non-overridable |
| 6 | **Tool descriptions** | Platform — auto-injected from active MCP server descriptions (always-on + opt-in enabled) | Platform (from host tool config) |
| 7 | **Communication style** | Platform — injected from user's JWT claims + `userProfile` config | Platform (from user claims) |
| 8 | **Memory blocks** | Platform — personal memory + application context | Platform (from stored memory) |
| 9 | **Host base prompt** | `scope.systemPrompt` in application config | Host Developer / Application Admin |

Layers 1–5 are **platform-managed and non-overridable** — they cannot be suppressed by host system prompt content.

Host applications may reinforce or tailor uncertainty behaviour further in their `scope.systemPrompt` — for example, specifying the domain areas where the model should be especially cautious, or providing alternative phrasings for uncertainty acknowledgment that fit the application's voice. The MCP Resources Service also publishes guidance documents on uncertainty handling that hosts can register and retrieve at session time (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md)).

Changes to the host base prompt are made via the Config Editor UI or Admin API and go through config validation before taking effect.

---

## Session context block

The session context block is the first layer injected into every system prompt. It grounds the model in its operating environment — who it is, who it is speaking with, and when the session is happening — without requiring the host to encode any of this in their static system prompt.

The platform assembles the block at session start from three sources: the tenant identity config, the authenticated user's JWT claims (mapped via `userProfile.sessionContext`), and the platform's own server-side values (date/time, config version).

### Rendered output

The block is rendered as plain text and injected at the top of the system prompt. Example:

```
## Session context
Assistant: Atlas (AI assistant for Acme Data Hub)
User: Sarah Chen · sarah.chen@acme.com · Senior Data Analyst · Acme Corporation
Session: Tuesday 16 June 2026, 09:14 UTC · Config v2.3.1
```

All four lines are always present. Fields within each line are omitted gracefully if the source data is unavailable — for example, if `roleField` is not configured, the role is omitted from the User line rather than showing a blank or placeholder.

### Field sources

| Field | Source | Always present |
|---|---|---|
| Assistant name | `identity.assistantName` | Yes |
| Application name | `identity.applicationName` | Yes |
| User display name | JWT claim mapped via `userProfile.sessionContext.displayNameField` | If claim present |
| User email | JWT claim mapped via `userProfile.sessionContext.emailField` | If claim present |
| User role / job title | JWT claim mapped via `userProfile.sessionContext.roleField` | If claim present |
| User organisation | JWT claim mapped via `userProfile.sessionContext.organisationField` | If claim present |
| Date and time | Platform server clock (UTC) | Yes |
| Config version | Active tenant config version record | Yes |

### Configuration

Claim field mappings are declared in the `userProfile.sessionContext` section of the host application config — see [01-host-application-config.md](./02-host-application-config.md). If `sessionContext` is omitted from the config, the User line contains only the fields derivable without JWT claims (typically none — the line is omitted entirely).

### Caching

The session context block is **not cacheable** — it contains user-specific identity and a session timestamp that differ on every request. It is injected after the cacheable prefix (host base prompt, tool descriptions, memory blocks) so that caching of the static layers is not disrupted.

---

## Prompt caching

The static components of the system prompt are injected as a cacheable prefix on every AI provider API request. Prompt caching reduces input token cost and latency.

| Cached component | Contents |
|-----------------|---------|
| Host base prompt | Full host system prompt |
| Tool descriptions | All active MCP server descriptions (always-on + opt-in enabled for the session) |
| Memory blocks | Application context and personal memory blocks (change infrequently) |

The session context block is excluded from the cacheable prefix — it is appended after the cache boundary on every request.

The **cache hit rate** is tracked as a launch metric (target: ≥ 40% by month 2 — see [14-success-metrics.md](./14-success-metrics.md)).
