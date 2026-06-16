# AI Chat Platform — Product Design Specification

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## What is this?

The **AI Chat Platform** is a white-label, embeddable conversational AI layer that any application can adopt. Host applications bring their own domain scope, MCP tooling, entity bindings, guided workflows, and branding. The platform provides the conversation engine, content rendering, audit storage, memory management, and multi-tenant infrastructure.

A host application registers as a **tenant**, provides a **JSON application config**, and drops an `<ai-chat>` web component into their UI. Their users get a persistent, context-aware conversational assistant that speaks their domain, respects their permission model, and reflects their brand — with no AI infrastructure to build or maintain.

The assistant has no platform-level name. Each host application names their own assistant instance in their config (e.g. "Atlas", "Nova", "Sage"). End users see only the name their host application has chosen.

---

## Architecture in one line

> One multi-tenant platform. One web component. One config schema. Every host application brings its own identity, tools, and scope.

---

## Reading order

Start at `01` and read through in sequence. Each document assumes you have read the previous one.

| # | Document | Purpose |
|---|----------|---------|
| 01 | [01-overview.md](./01-overview.md) | Vision, what the platform is and is not, scope — **start here** |
| 02 | [02-host-application-config.md](./02-host-application-config.md) | The JSON config schema every host application provides — the single most important reference for host developers |
| 03 | [03-personas-and-journeys.md](./03-personas-and-journeys.md) | Platform-level and application-level user archetypes and journeys |
| 04 | [04-design-principles.md](./04-design-principles.md) | Nine governing principles that take precedence over any feature decision |
| 05 | [05-conversation-management.md](./05-conversation-management.md) | Conversation model, branching, search, context window management |
| 06 | [06-input-and-composition.md](./06-input-and-composition.md) | Free-form input, `@`-binding, Display ID detection, document attachments, editing |
| 07 | [07-model-configuration.md](./07-model-configuration.md) | Provider abstraction, model switching, communication style, system prompt |
| 08 | [08-tool-access.md](./08-tool-access.md) | Host-registered MCP servers, always-on vs opt-in access, guided workflows, tool call transparency |
| 09 | [09-shared-conversations.md](./09-shared-conversations.md) | Invitation model, participant rights, permission-scoped bindings, audit trail |
| 10 | [10-interaction-design.md](./10-interaction-design.md) | Web component layout, responsive behaviour, thread anatomy, artefact tray, error states, accessibility |
| 11 | [11-content-rendering.md](./11-content-rendering.md) | Rendering decision rules, content types, streaming behaviour |
| 12 | [12-audit-and-storage.md](./12-audit-and-storage.md) | Multi-tenant storage model, retention, access control, DB schema reference |
| 13 | [13-continuous-improvement.md](./13-continuous-improvement.md) | Improvement signals, issue pipeline, improvement cadence |
| 14 | [14-mcp-tool-registry.md](./14-mcp-tool-registry.md) | Per-tenant tool registry, tool registration, relationship to complementary MCP services |
| 15 | [15-success-metrics.md](./15-success-metrics.md) | Platform-level and application-level metrics, definitions, and targets |
| 16 | [16-memory-and-recall.md](./16-memory-and-recall.md) | Personal memory, application context, recall scope |
| 17 | [17-embedding-and-web-component.md](./17-embedding-and-web-component.md) | `<ai-chat>` web component API (Mode 2 — Inline Page): attributes, events, authentication bridge, CSP, sizing |
| 18 | [18-complementary-mcp-services.md](./18-complementary-mcp-services.md) | MCP Repository and MCP Resources — ecosystem services that complement the platform |
| 19 | [19-entry-points-and-embedding-modes.md](./19-entry-points-and-embedding-modes.md) | All three embedding modes: Floating Widget, Inline Page, and Form Field Assist |
| — | [ROADMAP.md](./ROADMAP.md) | Planned enhancements beyond the current release |

---

## Key concepts

| Term | Definition |
|------|------------|
| **Host application** | A product team's application that embeds the AI Chat Platform |
| **Tenant** | A registered host application instance on the platform; identified by `tenant_id` |
| **Application config** | The JSON document a host provides to configure their tenant — system prompt, MCP servers, bindable types, workflows, branding, feature flags |
| **[AssistantName]** | Placeholder in these documents for the assistant name defined by each host in their config |
| **Bindable type** | A host-defined object type that end users can reference via `@`-binding in the input field |
| **Application admin** | A privileged user within a tenant who manages application context (org-level memory) and tenant configuration |
| **Application context** | Tenant-scoped standing context injected into every conversation; managed by the Application Admin |
| **Web component** | The `<ai-chat>` custom element that host applications embed in their UI |
| **Authentication bridge** | The mechanism by which the host application passes the authenticated user's identity and claims to the web component |
| **MCP Repository** | A complementary platform service providing a discoverable registry of available MCP tools that tenants can browse and register |
| **MCP Resources Service** | A complementary platform service providing centralised skills, static resources, and reusable prompt artefacts across the MCP ecosystem |
| **Web Search Service** | A complementary MCP service providing real-time web search and page retrieval; registered by hosts as an opt-in or always-on MCP server |
| **`<ai-chat>`** | Mode 2 web component — full inline assistant embedded in a host app page |
| **`<ai-chat-widget>`** | Mode 1 web component — floating FAB that expands to a mini/full chat panel; persists across pages |
| **`<ai-chat-field>`** | Mode 3 web component — ephemeral contextual assist scoped to a single form field |

---

## Platform scope

### In scope

- Multi-tenant platform with per-tenant application config
- Embeddable `<ai-chat>` web component with host branding token support
- Persistent, named conversation threads scoped to the authenticated user within their tenant
- Conversation branching via message edit or regeneration — no in-place overwrites
- Full-text conversation search across all user conversations
- 100-turn conversation limit with automatic context summarisation and user-initiated branch-to-new-thread
- Host-configured `@`-binding typeahead for application-defined object types
- Host-configured Display ID pattern detection and auto-resolution
- Document attachments (PDF, Excel, Word, images) — stored as platform artefacts
- Model switching within host-configured allowed model set; provider-agnostic architecture
- Communication style and verbosity driven by host-provided user profile claims
- Host-registered MCP servers; always-on and opt-in access tiers
- Host-defined guided workflow prompts accessible from the Workflow Library panel
- Tool call transparency — every MCP invocation rendered as a collapsible disclosure card
- Shared conversations with equal-participant model (max 10 users); sharing scoped to users within the same tenant
- Personal memory (user-managed) and application context (Application Admin-managed)
- Session artefact tray accumulating all input and output artefacts
- Document canvas — iteratable working-document surface in the right panel; versioned, editable, model-revisable
- Real-time web search via the Web Search complementary MCP service (host-registered, opt-in)
- Three-zone layout (history panel, conversation area, conversation panel) embedded within host app UI
- Rich content rendering: Mermaid diagrams, Vega-Lite charts, JSON inspector, data tables, syntax-highlighted code, prose markdown, math (KaTeX)
- Inline source citations linking to MCP tool call disclosure cards
- Continuous improvement signal capture; improvement issue pipeline
- Full audit trail per turn: raw prompt, resolved prompt, tool call log, artefacts, token counts
- Multi-tenant data isolation with row-level security

### Out of scope

- Semantic search (pgvector RAG) — structured MCP tool calls are the primary data access pattern
- Conversation export (PDF or markdown)
- Voice or multimodal input
- Context globbing (pulling context from multiple past conversations into one session)
- Incognito / temporary chat (no-history mode) — conflicts with audit completeness
- Platform-owned web search — available via the Web Search complementary MCP service registered by the host
- Image or content generation
- Code execution sandbox
- Public shareable links — all sharing is participant-controlled and tenant-scoped
- Read receipts in shared conversations
- Dark mode — not in v1

---

## Platform decisions

| ID | Decision |
|----|---------|
| **D1** | Host applications configure everything via a JSON application config. The platform provides mechanisms; hosts provide content (system prompt, tools, bindings, workflows, branding). |
| **D2** | The platform has no end-user-facing name. Each host application names its own assistant in its config. |
| **D3** | The platform is multi-tenant. One deployment serves many host applications, each fully isolated by `tenant_id` with row-level security. |
| **D4** | Conversations and artefacts are stored in the platform's own database. Host applications do not manage storage. |
| **D5** | The web component is the only supported embedding model in v1. Direct iframe embedding is not supported. |
| **D6** | The authentication bridge passes host-authenticated user identity to the component. The platform trusts the host's JWT; it does not re-authenticate users independently. |
| **D7** | No MCP server is always-on by default. Host applications designate which of their registered servers should be always-on in their config. If no always-on server is registered, the platform operates in prompt-only mode. |
| **D8** | Conversations are append-only at the turn level. Message editing creates a new branched thread; the original is preserved. |
| **D9** | Improvement signals generated by the platform are routed to the platform team and optionally forwarded to the host application via webhook. |
| **D10** | Retention period is configurable per tenant in the application config. The platform default is 3 years. |
| **D11** | Conversation sharing is scoped to users within the same tenant. Cross-tenant invitations are not supported. |
| **D12** | The MCP Repository, MCP Resources Service, and Web Search Service are complementary ecosystem services — the platform assumes their availability but does not own or operate them. |

---

*Provided as a public research resource. Not intended for use in live or production environments without independent professional review and adaptation.*
