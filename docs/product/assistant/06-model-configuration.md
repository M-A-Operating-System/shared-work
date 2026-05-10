# 06 — Model Configuration

## AI provider architecture

The AI Chat Platform is designed to be **AI provider-agnostic**. The model provider is abstracted behind the platform's edge function layer — the conversational surface, MCP tool access, `@`-binding resolution, and audit trail are identical regardless of which AI provider is active for a tenant.

| Release | Provider | Models |
|---------|---------|--------|
| **v1 (current)** | Anthropic Claude | Sonnet 4.6 (default), Opus 4.7, Haiku 4.5 |
| **Planned** | OpenAI | GPT-4o and successors |
| **Planned** | Google | Gemini Pro and successors |

The provider abstraction means host applications will eventually be able to select provider as well as model. In v1, only Claude models are available. The provider is configured per tenant in the `models.provider` field of the application config.

---

## Model switching

Users may switch the active model at any point in a conversation. The switch takes effect on the **next turn** — it does not re-process previous turns.

The host-configured system prompt, MCP tool access, and `@`-binding resolutions are identical across all models within the active provider.

Host applications configure the allowed model set and default model in the `models` section of the application config. Users can only switch to models in the `allowedModels` list. Setting `userCanSwitch: false` locks all sessions to the `defaultModel`.

### v1 available models (Anthropic Claude)

| Model | Profile | Typical use |
|-------|---------|------------|
| **Claude Sonnet 4.6** | Default — balanced capability and speed | General queries, entity lookup, domain summaries, diagram generation |
| **Claude Opus 4.7** | Maximum capability, higher latency | Complex multi-entity reasoning, cross-domain analysis, large document analysis |
| **Claude Haiku 4.5** | Fastest, lowest latency | Quick lookups, simple factual answers, Display ID resolution |

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

Host applications configure which JWT claim fields map to style and verbosity, and define the prompt text for each value, in the `userProfile` section of the application config (see [00-host-application-config.md](./00-host-application-config.md)).

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

The platform assembles the system prompt from multiple layers before each session:

| Layer | Source | Editable by |
|-------|--------|------------|
| **Host base prompt** | `scope.systemPrompt` in application config | Host Developer / Application Admin |
| **Tool descriptions** | Auto-injected from active MCP server descriptions (always-on + opt-in enabled) | Platform (from host tool config) |
| **Communication style** | Injected from user's JWT claims + `userProfile` config | Platform (from user claims) |
| **Memory blocks** | `[Your context]` (personal memory) + `[Application context]` (application context) | Platform (from stored memory) |
| **Write confirmation flow** | Instructs model to propose before/after state and wait for confirmation before any write MCP call | Platform — non-configurable |
| **Transparency instruction** | Instructs model to show all tool calls and cite sources | Platform — non-configurable |
| **Prompt injection mitigation** | Instructs model to treat tool result content as data, not instructions | Platform — non-configurable |

The write confirmation, transparency, and prompt injection mitigation layers are **platform-managed and non-overridable** — they cannot be suppressed by host system prompt content.

Changes to the host base prompt are made via the Config Editor UI or Admin API and go through config validation before taking effect.

---

## Prompt caching

The static components of the system prompt are injected as a cacheable prefix on every AI provider API request. Prompt caching reduces input token cost and latency.

| Cached component | Contents |
|-----------------|---------|
| Host base prompt | Full host system prompt |
| Tool descriptions | All active MCP server descriptions (always-on + opt-in enabled for the session) |
| Memory blocks | Application context and personal memory blocks (change infrequently) |

The **cache hit rate** is tracked as a launch metric (target: ≥ 40% by month 2 — see [14-success-metrics.md](./14-success-metrics.md)).
