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
| 01 | [01-overview.md](./01-overview.md) | Vision, scope, architecture, personas and journeys, design principles, platform decisions — **start here** |
| 02 | [02-host-config.md](./02-host-config.md) | The JSON config schema every host application provides — the single most important reference for host developers |
| 03 | [03-conversations-and-input.md](./03-conversations-and-input.md) | Conversation model, branching, search, context window; free-form input, `@`-binding, Display ID detection, attachments, editing |
| 04 | [04-model-and-prompt.md](./04-model-and-prompt.md) | Provider abstraction, model switching, communication style, system prompt layers, session context block |
| 05 | [05-tools-and-memory.md](./05-tools-and-memory.md) | Host-registered MCP servers, tool registry, guided workflows, transparency; personal memory and application context; shared conversations |
| 06 | [06-interface-and-rendering.md](./06-interface-and-rendering.md) | Web component layout, responsive behaviour, thread anatomy, artefact tray, accessibility; rendering decision rules and content types |
| 07 | [07-embedding-and-integration.md](./07-embedding-and-integration.md) | All three embedding modes (Floating Widget, Inline Page, Form Field Assist) and the `<ai-chat>` component API: attributes, events, auth bridge, CSP, sizing |
| 08 | [08-platform-operations.md](./08-platform-operations.md) | Audit and storage, continuous improvement, success metrics, complementary MCP services |
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
| **MCP Knowledge** | The [MAOS Knowledge MCP Server](../knowledge/01-overview.md) — centralised skills, guidance documents, and prompt templates across the MCP ecosystem |
| **MCP Internet Fetch & Search** | The [MAOS Internet Access MCP Server](../internet/01-overview.md) — controlled web search and page fetch; registered by hosts as an opt-in or always-on MCP server |
| **`<ai-chat>`** | Mode 2 web component — full inline assistant embedded in a host app page |
| **`<ai-chat-widget>`** | Mode 1 web component — floating FAB that expands to a mini/full chat panel; persists across pages |
| **`<ai-chat-field>`** | Mode 3 web component — ephemeral contextual assist scoped to a single form field |

---

> Platform **scope** (in/out) and the **platform decisions** log (D1–D12) are specified in [01-overview.md](./01-overview.md).

---

## Quick Reference

**Web components:**

| Component | Mode | Description |
|---|---|---|
| `<ai-chat-widget>` | Floating Widget | FAB that expands to a mini/full chat panel; persists across pages |
| `<ai-chat>` | Inline Page | Full inline assistant embedded in a host app page |
| `<ai-chat-field>` | Form Field Assist | Ephemeral contextual assist scoped to a single form field |

**Complementary MCP services:**

| Service | Specification |
|---|---|
| MCP Knowledge | [Knowledge MCP Server](../knowledge/01-overview.md) |
| MCP Internet Fetch & Search | [Internet Access MCP Server](../internet/01-overview.md) |

---

## References

| Resource | URL |
|---|---|
| MCP Specification 2025-03-26 | https://modelcontextprotocol.io/specification/2025-03-26 |
| MCP Authorization Specification 2025-11-25 | https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization |
| OAuth 2.1 | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1 |
| RFC 8707 Resource Indicators | https://datatracker.ietf.org/doc/html/rfc8707 |

---

*Provided as a public research resource. Not intended for use in live or production environments without independent professional review and adaptation.*
