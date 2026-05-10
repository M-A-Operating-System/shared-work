# Data AI Assistant — Product Design Documents

This directory contains the product design specification for the **Data AI Assistant** ("ask Andi"), the CDO's second brain embedded in the DDA platform. Tracks [Issue #216](https://github.com/agbush2/master-model-maven/issues/216).

|                    |                                                       |
|--------------------|-------------------------------------------------------|
| **Document status**| Draft v2.0                                            |
| **Product area**   | DDA Platform — Lovable-hosted frontend                |
| **Author**         | Andrew Bush, Interim CDAiO · Fortium Partners         |
| **Date**           | May 2026                                              |
| **Audience**       | Product, design, and engineering — pre-build reference|

## Purpose

Provide the CDO and their team with a persistent, domain-aware conversational interface to the full DDA data estate — at the speed of a question. The experience is modelled on the Claude native desktop application but scoped entirely to DDA governance: entities, models, lineage, quality, and posture.

Andi is a **read and write** governance assistant. All data operations flow through entityCrud via the DDA MCP server, enforcing the existing DDA security model. Write operations require explicit user confirmation before any change is committed.

## Reading order

Start at the top and read through in sequence. Each document assumes you have read the previous one.

| # | Document | Purpose |
|---|----------|---------|
| — | [ROADMAP.md](./ROADMAP.md) | Planned enhancements beyond the current release |
| 1 | [01-overview.md](./01-overview.md) | Vision, what it is and is not, scope |
| 2 | [02-personas-and-journeys.md](./02-personas-and-journeys.md) | User personas and representative user journeys |
| 3 | [03-design-principles.md](./03-design-principles.md) | Eight governing principles that take precedence over any feature decision |
| 4 | [04-conversation-management.md](./04-conversation-management.md) | Conversation model, branching, search, context window management |
| 5 | [05-input-and-composition.md](./05-input-and-composition.md) | Free-form input, `@`-binding, Display ID detection, document attachments, editing |
| 6 | [06-model-configuration.md](./06-model-configuration.md) | Model switching, communication style, verbosity — driven by DDA user profile |
| 7 | [07-tool-access.md](./07-tool-access.md) | Always-on DDA MCP server, opt-in tools, guided workflows, tool call transparency |
| 8 | [08-shared-conversations.md](./08-shared-conversations.md) | Invitation model, participant rights, `@`-binding permissions, audit trail |
| 9 | [09-interaction-design.md](./09-interaction-design.md) | Page structure, responsive layout, thread anatomy, artefact tray, error states, accessibility |
| 10 | [10-content-rendering.md](./10-content-rendering.md) | Rendering decision rules, content types, streaming behaviour |
| 11 | [11-audit-and-storage.md](./11-audit-and-storage.md) | Storage policy, retention, access control, DB schema reference |
| 12 | [12-continuous-improvement.md](./12-continuous-improvement.md) | Improvement signals, GitHub issue pipeline, improvement cadence |
| 13 | [13-mcp-tool-registry.md](./13-mcp-tool-registry.md) | Build-time registry: access tiers, schema, process for adding tools |
| 14 | [14-success-metrics.md](./14-success-metrics.md) | Launch metrics, definitions, and targets |
| 15 | [15-memory-and-recall.md](./15-memory-and-recall.md) | Personal memory, institutional memory, and recall scope (org/tenant boundary) |

## Scope — Issue #216

### In scope

- [x] Persistent, named conversation threads scoped to the authenticated DDA user
- [x] Conversation branching via message edit or regeneration — no in-place overwrites
- [x] Full-text conversation search across all user conversations
- [x] 100-turn conversation limit with automatic context summarisation (visible condensation marker in thread) and user-initiated branch-to-new-thread option
- [x] `@`-binding typeahead for DDA objects (domains, concepts, products, entities, models, data owners, surveys, guided workflows) — resolves to `@{...}` / `#{...}` structured blocks; universal fixed ranking order
- [x] Display ID paste detection and auto-resolution
- [x] Document attachments (PDF, Excel, Word) — multiple files per message turn; 100 MB total budget per conversation; stored as governance artefacts
- [x] Image and screenshot input (PNG, JPG, WEBP) — clipboard paste supported
- [x] Model switching (Claude Sonnet 4 / Opus 4 / Haiku 4) mid-conversation; provider-agnostic architecture
- [x] Communication style and verbosity driven by DDA user profile (`technical` / `business` / `executive`)
- [x] Always-on DDA MCP server; opt-in additional tools via MCP tool registry
- [x] Survey objects accessible as MCP tool results — title, scope, response summary, key findings, strategic recommendations
- [x] Governed entity update and status-change via MCP — DDA security model enforced; every proposed update requires explicit user confirmation before write
- [x] Five guided workflow prompts accessible from the Guided Workflows drawer (DDA platform nav)
- [x] Tool call transparency — every MCP invocation rendered as a collapsible disclosure card
- [x] Shared conversations with equal-participant model (max 10 users); sharing scoped to users within the same organisation/tenant
- [x] Personal memory (user-managed, 2,000-token budget, off by default) and institutional memory (CDAiO-managed, 4,000-token budget, approval workflow)
- [x] Session artefact tray accumulating all input and output artefacts
- [x] Four-zone layout (DDA platform nav with assistant sub-items, history panel, conversation area, conversation panel) — responsive to mobile
- [x] Rich content rendering: Mermaid diagrams, Vega-Lite charts, JSON inspector, data tables, syntax code, prose markdown, math (KaTeX)
- [x] Inline source citations linking to MCP disclosure cards
- [x] Continuous improvement signal capture and GitHub issue pipeline
- [x] Full governance audit trail per turn: raw prompt, resolved prompt, tool call log, artefacts, token counts

### Out of scope

- Semantic search over entity descriptions (pgvector RAG) — entity lookup uses structured MCP tool calls
- Data warehouse query access — planned capability; see [ROADMAP.md](./ROADMAP.md)
- Conversation export (PDF or markdown)
- User-customisable prompt library — platform-managed only
- Voice or multimodal input
- Context globbing (pulling context from multiple past conversations into one session)
- Incognito / temporary chat (no-history mode) — directly conflicts with P4 audit completeness; all governance conversations must persist
- Web search (real-time internet retrieval) — outside DDA specialist scope; governance data comes from MCP, not the web
- Image or content generation — Andi reasons about data, does not generate media
- Code execution sandbox — Andi reasons about data, does not execute it
- Public shareable links — governance data cannot be shared via open URLs; all sharing is participant-controlled and org-scoped
- Read receipts in shared conversations
- Dark mode — the DDA platform does not currently support dark mode; this is a platform-level decision

## Key decisions

| ID | Decision |
|----|---------|
| **A1** | Governed entity update and status-change are in scope. Every proposed write requires explicit user confirmation before the MCP call is made. The before/after state is shown; the user confirms or cancels. Andi never implies a write has occurred if it has not. |
| **A2** | Prompt library is platform-managed only — no per-user prompt storage or management UI. |
| **A3** | Entity lookup uses structured MCP tool calls. Semantic (pgvector RAG) search is not active. |
| **A4** | Conversation records are retained for 3 years (working guide; compliance to ratify before launch). |
| **A5** | MCP server unavailability degrades gracefully to text-only mode with a banner. No silent failure. |
| **A6** | Conversation export is not available. Data classification inheritance must be resolved before it can be added. |
| **A7** | Message editing and regeneration both create new branched threads. No in-place overwrite of any turn. |
| **A8** | `@`-binding chips resolve to `@{...}` and `#{...}` structured blocks, consistent with the existing DDA text-blob convention. |
| **A9** | `@`-binding typeahead uses a universal fixed ranking order: Domain → Concept → Product → Entity → Data Model → Data Owner → Survey → Guided Workflow. No persona-adaptive ranking. |
| **A10** | Conversations are limited to 100 turns. Auto-summarisation triggers at 80% context window; a condensation marker is always shown in the thread. Silent truncation is not permitted. |
| **A11** | A shared conversation must always have at least one participant. The last participant cannot leave or remove themselves until another user has accepted an invitation. |
| **A12** | Invited participants always see the full conversation history. A full-page disclaimer must be acknowledged before the user can enter the conversation — shown on every acceptance, not once. |
| **A13** | When a `business` or `executive` style user asks a question requiring technical depth, the model answers in their style and appends a signal offering the full technical view on request. It never silently switches style or omits information. |
| **A14** | Multiple attachments allowed per message turn. Total attachment budget is 100 MB per conversation (not per message). Per-file maximum remains 10 MB. |
| **A15** | Guided workflow prompts reviewed against existing MCP prompts. 5 Andi-specific workflows defined with governance/business orientation. `trace_lineage` and `compare_concepts` not carried forward as workflows (available via natural language). |
| **A16** | Auto-summarisation uses Claude Haiku 4 for the summary API call (fast/low-cost). Structured summary format (entities, findings, decisions, unresolved questions). Oldest 40% of turns summarised; most recent 60% kept verbatim. |
| **A17** | MCP tool registry is bundled into the MCP client at deployment — not fetched at runtime from a separate source. |
| **A18** | Report icon on every turn (user and assistant). Modal requests an explanation. Always generates a GitHub issue with the explanation, the turn, and surrounding context. |
| **A19** | Auth session expiry: conversation history is restored on re-auth; unsent in-progress input is not preserved (keep simple). |
| **A20** | Retention period: 3 years (working guide, to be ratified by compliance before launch). |
| **A21** | Conversation sharing is scoped to users within the same organisation/tenant. Cross-tenant invitations are not supported. |
| **A22** | Personal memory is off by default. Users opt in explicitly. Institutional memory is always injected for all users in the organisation. Neither memory type may contain `@`-bindings, Display IDs, or system prompt overrides. |
| **A23** | The AI model provider is abstracted behind the edge function layer. v1 uses Anthropic Claude (Sonnet 4 default, Opus 4, Haiku 4). The architecture supports OpenAI and Gemini as follow-on providers without changes to the conversational surface, MCP tooling, or audit trail. |
| **A24** | Andi never reads the DDA database directly. All data access — read and write — flows through entityCrud via the DDA MCP server. |
| **A25** | Survey objects are bindable via `@`-binding and accessible as MCP tool results. Survey content is available to Andi for strategy and governance recommendations. |

## Related

- [docs/product/mcp/](../mcp/README.md) — DDA MCP server design (the tool provider for every session)
- [docs/product/entity-crud/](../entity-crud/) — entityCRUD edge function (read surface the MCP wraps)
- [GitHub Issue #216](https://github.com/agbush2/master-model-maven/issues/216) — source specification

---

*Confidential — Fortium Partners / MAOS*
