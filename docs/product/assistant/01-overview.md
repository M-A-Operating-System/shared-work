# 01 — Overview

## Vision

### The CDO's second brain

The **Data AI Assistant** is a conversational interface embedded within the DDA platform. Its primary purpose is to function as the **Chief Data Officer's second brain** — a persistent, always-available intelligence layer that knows the organisation's data estate, understands governance context, and surfaces the right entity, model, or next action at the speed of a question.

The experience is modelled on the Claude native desktop application: a context-aware conversation with rich rendered output. It is not a general-purpose assistant. Every interaction is anchored to the DDA domain — entities, models, lineage, quality, governance posture.

> **Governing intent:** Replace point-and-click navigation of the DDA platform with a conversational interface that gives the CDO and their team instant, contextual access to the full data estate — at the speed of a question.

### What it is and is not

| It is | It is not |
|-------|-----------|
| A specialist governance assistant with deep DDA platform knowledge | A general-purpose AI assistant |
| The primary access layer for non-technical business users | A replacement for the DDA UI for power users |
| A complete governance audit trail for every conversation and artefact | A transient chat tool with no persistent record |
| Extensible to additional MCP tools via a controlled registry | An open integration surface for arbitrary tools |
| A read and write governance assistant — queries, reasoning, and governed entity updates via the DDA security model | A system that bypasses DDA security or writes without governance controls |

### Naming

The AI assistant is named **Andi**. The screen/navigation title within the DDA platform is **"Data AI Assistant"**. The informal shorthand used by the team and in business communications is **"ask Andi"**.

---

## Scope

### In scope

- Persistent, named conversation threads scoped to the authenticated DDA user
- Full-text search across all user conversations
- Conversation branching via message edit or regeneration — preserving the complete governance audit trail
- `@`-binding for DDA objects (domains, concepts, products, entities, data models, data owners, surveys, guided workflows)
- Document attachments (PDF, Excel, Word) stored as turn-level artefacts
- Model switching between Claude Sonnet 4, Opus 4, and Haiku 4 mid-conversation
- Communication style and verbosity controlled by the authenticated user's DDA profile
- Always-on DDA MCP server providing entity lookup, governance summaries, data model queries, and survey content
- Governed entity update and status-change via MCP — subject to the DDA security model; every proposed update requires explicit user confirmation before the write call is made
- Opt-in additional MCP tools via a build-time registry
- Five DDA guided workflow prompts accessible from the Guided Workflows drawer (DDA platform nav)
- Shared conversations — up to ten authenticated DDA participants with equal rights
- Four-zone responsive layout (DDA platform nav with assistant sub-items, history panel, conversation area, conversation panel) functional on mobile
- Rich content rendering: Mermaid, Vega-Lite, JSON inspector, data tables, syntax-highlighted code, prose markdown, math (KaTeX)
- Full governance audit trail: raw prompt, resolved prompt, attached files, model response, tool call log, output artefacts, token counts
- Continuous improvement signal capture and GitHub issue pipeline

### Out of scope

- Semantic search over entity descriptions (pgvector RAG) — entity lookup uses structured MCP tool calls
- Data warehouse query access — read access to the underlying business data warehouse is a planned capability (see [ROADMAP.md](./ROADMAP.md))
- Conversation export (PDF or markdown)
- User-customisable prompt library — the guided workflow library is platform-managed only
- Voice or multimodal input

---

## Relationship to other DDA modules

```
┌─────────────────────────────────────────┐
│           DDA Platform (Lovable)         │
│                                         │
│  ┌─────────────┐   ┌──────────────────┐ │
│  │  Data AI Assistant   │──▶│  DDA MCP Server  │ │
│  │ (this doc)  │   │ (docs/product/   │ │
│  │             │   │      mcp/)       │ │
│  └─────────────┘   └────────┬─────────┘ │
│                             │           │
│                    ┌────────▼─────────┐ │
│                    │   entityCrud     │ │
│                    │  edge function   │ │
│                    └──────────────────┘ │
└─────────────────────────────────────────┘
```

- **DDA MCP Server** ([docs/product/mcp/](../mcp/README.md)) is the tool provider for every Data AI Assistant session. The always-on DDA tool in the MCP registry calls the MCP server; the MCP server wraps `entityCrud`.
- **entityCrud** is the single source of truth for entity data. **Andi never reads the database directly** — all data flows through `entityCrud` via the MCP server. This applies to all current and future tool capabilities: the MCP server is the only path to DDA data.
- **Data AI Assistant** owns the conversational surface, rendering, audit trail, shared conversation model, and improvement signal pipeline. It depends on, but does not duplicate, the capabilities of the layers beneath it.

---

## Dependencies

- DDA MCP server — always-on tool provider (see [docs/product/mcp/](../mcp/README.md))
- Supabase Auth — identity provider and JWT issuer for all API calls
- **AI model provider** — v1 uses Anthropic Claude (Sonnet 4 default, Opus 4, Haiku 4). The architecture is designed to be provider-agnostic; OpenAI and Gemini models are the planned follow-on providers. The model provider abstraction is owned by the edge function layer.
- Supabase Storage — binary artefact retention (attached documents, generated outputs)
- Supabase Edge Function — JWT handling, AI provider API request construction, SSE stream passthrough; provider-agnostic interface
- `src/config/entityRegistry.ts` + generated `supabase/functions/_shared/entityMeta.ts` — source of truth for bindable object types and MCP tool availability
- DDA design system — typography, colour, spacing, component library

## Related issues

- Issue #216 — this work
- Issue #6 / docs/product/mcp — DDA MCP server (tool provider)
