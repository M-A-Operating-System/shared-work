# 01 — Overview

## Vision

### Conversational AI for any application

The **AI Chat Platform** enables any application to give its users a persistent, context-aware conversational interface — without building AI infrastructure. The experience is modelled on the best native AI desktop applications: rich rendered output, transparent tool usage, and a conversation that remembers where you left off. It is not a general-purpose assistant layer — each deployment is a **specialist** tuned to its host application's domain.

> **Governing intent:** Give any application team the ability to drop a production-grade AI assistant into their product within days — fully branded, scoped to their domain, connected to their data, and backed by a complete audit trail.

### What the platform is and is not

| It is | It is not |
|-------|-----------|
| A white-label assistant layer any application can embed as a web component | A standalone AI product with its own brand or identity |
| A multi-tenant platform where each host application brings its own scope, tools, and branding | A shared assistant all host applications configure from a single pool |
| A complete audit trail for every conversation turn and artefact | A transient chat tool with no persistent record |
| A controlled, host-configured MCP integration surface | An open API that allows arbitrary tool connections without host approval |
| A read-and-write assistant — queries, reasoning, and actions via host-registered MCP tools | A system that bypasses host application security models or acts without user confirmation |

### The assistant has no platform name

The platform has no end-user-facing name. Every tenant names their own assistant in their application config (`identity.assistantName`). End users see only that name — they are not exposed to the underlying platform. This document uses **[AssistantName]** as a placeholder wherever the assistant name would appear.

---

## Scope

### In scope

- Embeddable `<ai-chat>` web component with full branding token support
- Multi-tenant architecture with complete per-tenant data isolation
- Persistent, named conversation threads scoped to the authenticated user within their tenant
- Conversation branching via message edit or regeneration — preserving the complete audit trail
- Full-text search across all user conversations within the tenant
- Host-configured `@`-binding for application-defined object types
- Host-configured Display ID pattern detection and auto-resolution
- Document attachments (PDF, Excel, Word, images) stored as platform artefacts
- Model switching within the host-configured allowed model set; provider-agnostic architecture
- Communication style and verbosity driven by host-provided user profile claims
- Host-registered MCP servers with always-on and opt-in access tiers
- Host-defined guided workflow prompts accessible from the Workflow Library panel
- Tool call transparency — every MCP invocation rendered as a collapsible disclosure card
- Write operations — actions via host MCP tools with explicit user confirmation before execution
- Shared conversations — up to ten participants within the same tenant, equal-participant model
- Personal memory (user-managed) and application context (Application Admin-managed)
- Session artefact tray accumulating all input and output artefacts
- Document canvas — iteratable working-document surface in the conversation panel; versioned, editable, model-revisable
- Three-zone responsive layout (history panel, conversation area, conversation panel) embedded within host app UI
- Rich content rendering: Mermaid, Vega-Lite, JSON inspector, data tables, syntax-highlighted code, prose markdown, math (KaTeX)
- Continuous improvement signal capture and per-tenant improvement issue pipeline
- Full audit trail per turn: raw prompt, resolved prompt, tool call log, output artefacts, token counts
- Complementary MCP ecosystem services: MCP Repository (tool discovery), MCP Resources (shared skills and artefacts), and Web Search (real-time web search)

### Out of scope

- Semantic search over application data (pgvector RAG) — structured MCP tool calls are the primary data access pattern in v1
- Conversation export (PDF or markdown) — planned; data classification complexity must be resolved first
- Voice or multimodal input
- Context globbing (pulling context from multiple past conversations into one session)
- Incognito or temporary chat (no-history mode) — conflicts with audit completeness
- Platform-owned web search — available via the Web Search complementary MCP service registered by the host (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md))
- Image or content generation
- Code execution sandbox
- Public shareable links — all sharing is participant-controlled and tenant-scoped
- Read receipts in shared conversations
- Dark mode — not in v1

---

## Platform architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Host Application                          │
│                                                              │
│   ┌────────────────────────────────────────┐                 │
│   │        <ai-chat> web component         │                 │
│   │   (embedded in host application UI)    │                 │
│   └────────────────┬───────────────────────┘                 │
│                    │ Authentication bridge (JWT + claims)    │
└────────────────────┼─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│                  AI Chat Platform                             │
│                                                              │
│  ┌─────────────────┐   ┌──────────────────────────────────┐  │
│  │  Conversation   │   │  AI Provider Edge Function        │  │
│  │  Engine         │◀──│  (provider-agnostic abstraction;  │  │
│  │                 │   │   fast / standard / powerful tier)│  │
│  └────────┬────────┘   └──────────────────────────────────┘  │
│           │                                                  │
│  ┌────────▼────────┐   ┌──────────────────────────────────┐  │
│  │  Audit Storage  │   │  Per-tenant tool registry         │  │
│  │  (multi-tenant) │   │  (from application config)        │  │
│  └─────────────────┘   └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                     │
     ┌───────────────┼────────────────────┐
     │               │                    │
┌────▼────┐   ┌──────▼──────┐   ┌────────▼───────┐
│ Host    │   │ Host MCP    │   │ Complementary     │
│ App     │   │ Server(s)   │   │ MCP Services      │
│ API     │   │ (registered │   │ (Repository +     │
│         │   │  in config) │   │  Resources +      │
│         │   │             │   │  Web Search)      │
└─────────┘   └─────────────┘   └───────────────────┘
```

### Components

**AI Chat Platform** owns the conversational surface, content rendering, audit trail, shared conversation model, memory management, and improvement signal pipeline. It depends on, but does not duplicate, the capabilities of the host application or its MCP servers.

**Host Application** owns the user identity model, application business logic, and MCP server endpoints. It embeds the platform via the web component and passes user context via the authentication bridge.

**Host MCP Servers** are the host application's data and action providers. The platform routes tool calls to these servers and surfaces the results transparently in the conversation thread.

**Complementary MCP Services** — the MCP Repository, MCP Resources Service, and Web Search Service — are ecosystem-level services that operate alongside both the platform and host MCP servers. They are not owned by the platform or by individual host applications. See [17-complementary-mcp-services.md](./17-complementary-mcp-services.md).

---

## Dependencies

| Dependency | Role |
|------------|------|
| **AI provider** | Provider-agnostic abstraction exposing three model tiers: `fast`, `standard` (default), `powerful`. The platform maps tiers to the tenant's configured provider's current models. Multiple providers planned — see [ROADMAP.md](./ROADMAP.md). |
| **Platform storage** | Relational database with row-level security for conversation records; object storage for binary artefacts. |
| **Platform edge function** | JWT handling, AI provider API request construction, SSE stream passthrough, MCP call routing. Provider-agnostic interface. |
| **Host authentication** | The host application issues JWTs for its users. The platform validates these tokens and trusts the embedded claims. No re-authentication is performed by the platform. |
| **Host MCP server(s)** | The host's registered MCP endpoints providing data access and action capabilities. |
| **MCP Repository** | Complementary ecosystem service — discoverable registry of available MCP tools. |
| **MCP Resources Service** | Complementary ecosystem service — centralised skills, static resources, and reusable prompt artefacts. |
| **Web Search Service** | Complementary ecosystem service — real-time web search and page retrieval; registered by hosts as an opt-in or always-on MCP server. |
