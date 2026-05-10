# 06 — Model Configuration

## AI provider architecture

Data AI Assistant is designed to be **AI provider-agnostic**. The model provider is abstracted behind the Supabase Edge Function layer — the conversational surface, MCP tool access, `@`-binding resolution, and audit trail are identical regardless of which AI provider is active.

| Release | Provider | Models |
|---------|---------|--------|
| **v1 (current)** | Anthropic Claude | Sonnet 4 (default), Opus 4, Haiku 4 |
| **Planned** | OpenAI | GPT-4o and successors |
| **Planned** | Google | Gemini Pro/Ultra |

The provider abstraction means users and administrators will eventually be able to select provider as well as model. In v1, only Claude models are available — the UI exposes model selection within the Claude family only.

---

## Model switching

Users may switch the active model at any point in a conversation. The switch takes effect on the **next turn** — it does not re-process previous turns.

The DDA system prompt, MCP tool access, and `@`-binding resolutions are identical across all models within the active provider.

### v1 available models (Claude)

| Model | Profile | Recommended DDA use |
|-------|---------|---------------------|
| **Claude Sonnet 4** | Default — balanced capability and speed | General queries, entity lookup, governance summaries, diagram generation |
| **Claude Opus 4** | Maximum capability, higher latency | Complex multi-entity reasoning, cross-domain analysis, large document analysis |
| **Claude Haiku 4** | Fastest, lowest latency | Quick lookups, Display ID resolution, simple factual answers |

### Model UI

- The **active model chip** is displayed adjacent to the input field — always visible regardless of scroll position.
- Clicking the chip opens a **model selection popover** showing all three models with their profiles and a recommended-use summary.
- Each assistant turn carries a **hover-visible metadata line**: model label + token counts (e.g. `↑ 1,240 in · ↓ 847 out · ⚡ 312 cached`).
- The model label on each response enables participants in shared conversations to see which model was active for each turn.

### Model in shared sessions

The active model and any opt-in MCP tools apply to the session as a whole. The user who submits a message determines the model context for that turn, based on their current model chip selection. Other participants see the model label on each assistant response.

---

## Communication style and verbosity

The model's communication style and verbosity are **driven by the authenticated user's DDA profile** — not a chat-specific setting. This ensures consistent behaviour across the DDA platform.

Two fields are added to the existing DDA user profile:

| Profile field | Values | Effect |
|--------------|--------|--------|
| `communication_style` | `technical` · `business` · `executive` | Controls vocabulary, platform terminology, and assumed data literacy |
| `response_verbosity` | `concise` · `standard` · `detailed` | Controls response length and depth |

### Communication style definitions

All three styles avoid internal DDA platform implementation terminology (entityMeta, entityCrud, MCP, RLS, edge functions). These are implementation details of the DDA platform — they are never surfaced to any user. The `technical` style is calibrated for professional data engineering and governance staff, not platform developers.

| Style | Vocabulary | DDA domain terminology | Assumed knowledge |
|-------|-----------|----------------------|-------------------|
| `technical` | Precise, data-professional language — data modelling concepts, quality metrics, governance frameworks, SQL-level reasoning | DDA governance terms used (entity, domain, data model, classification, data owner, lineage) — no internal implementation terms (entityMeta, MCP, RLS, etc.) | Data engineering and professional data modelling literacy assumed |
| `business` | Plain English | DDA terms replaced with business equivalents (e.g. "data asset" not "entity", "governance record" not "entityMeta row") | Business domain literacy; no data platform literacy assumed |
| `executive` | Summary-first, outcome-focused | No technical or platform terminology | Strategic framing; operational detail minimised |

### Response verbosity definitions

| Verbosity | Behaviour |
|-----------|----------|
| `concise` | Direct answers; minimal preamble; tables preferred over prose lists |
| `standard` | Balanced explanation with supporting context where helpful |
| `detailed` | Full explanation including methodology, caveats, and follow-up suggestions |

### Where the settings live

Profile fields are set on the **DDA profile settings page** — not within Data AI Assistant. The chat surface reflects the profile settings via a **read-only link** in the input footer (e.g. `Business · Standard`) — it is not an editable inline control, but it is clickable and navigates to the DDA profile settings page.

### Technical depth signal for business/executive users

When a user's `communication_style` is `business` or `executive` and their question genuinely requires technical detail for a correct or complete answer, the model should:

1. Answer in the user's configured style — plain language, no platform jargon
2. Append a brief signal at the end of the response: *"A more detailed technical breakdown is available — ask Andi for the full technical view."*

The user can then request the technical version in their next message. The model provides it for that turn only; the profile default is restored on the subsequent turn.

The model does **not** silently switch style, does **not** omit information that would make the answer misleading, and does **not** refuse to answer. The business/executive style controls vocabulary and framing — it does not prevent the model from surfacing important governance information.

### Per-turn style override

Users may override the communication style for a single turn using natural-language instruction (e.g. *"Give me the full technical details"*). The profile default is restored automatically on the next turn — it is not a persistent override.

### Style in shared conversations

Each user's `communication_style` and `response_verbosity` profile settings apply to the turns they submit. A response generated for a `technical` user may sit alongside a response generated for a `business` user within the same thread. The style label is visible on each assistant response so participants can see the context in which that response was calibrated.

---

## System prompt

The DDA system prompt is the foundation for all model behaviour. It is **platform-managed only** — not editable by users.

| System prompt responsibility | Description |
|-----------------------------|-------------|
| Domain scoping | Establishes DDA as the exclusive subject matter; instructs model to decline out-of-scope queries |
| Communication style injection | Injects the user's `communication_style` and `response_verbosity` values at session start |
| Tool description injection | Injects descriptions of all enabled MCP tools (always-on DDA tool + any opt-in tools) |
| Write confirmation flow | Instructs the model to propose the before/after state for any entity update and wait for explicit user confirmation before making any MCP write call. Andi never implies a write has occurred if it has not. |
| Governance audit instruction | Instructs the model to always show tool calls, never imply writes, and cite sources |
| Prompt injection mitigation | DDA §6a clause instructing the LLM to treat field content as data, not instructions |

Changes to the system prompt follow the DDA improvement pipeline — they are not deployed without a GitHub issue and CDAiO approval (see [12-continuous-improvement.md](./12-continuous-improvement.md)).

---

## Prompt caching

The DDA system prompt is injected as a cacheable prefix on every Anthropic API request. Prompt caching reduces input token cost and latency for the static components of every turn.

| Cached prefix | Contents |
|--------------|---------|
| System prompt | Full DDA system prompt (~3,000–5,000 tokens) |
| Tool descriptions | All enabled MCP tool descriptions injected at session start |
| Static `@`-binding context | Resolved context for `@`-bindings that appear in the first system turn |

The **cache hit rate** is tracked as a launch metric (target: ≥ 40% by month 2 — see [14-success-metrics.md](./14-success-metrics.md)).
