# 01 — Overview

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Protocol:** MCP 2025-06-18  
**Author:** Andrew Bush / Fortium Partners  

---

## Problem Statement

MAOS platform components — MCP servers providing value-added capabilities, agent pipelines, and downstream agent systems — each carry their own local copies of prompts, skill definitions, agent personas, and reference documentation. There is no single authoritative location to publish, version, and retrieve these assets. When a prompt is updated, every consumer must be updated in lockstep. There is no discovery mechanism and no governed access pattern.

## Solution

A centralised MCP server exposing a structured knowledge directory over the Model Context Protocol. Every MAOS component and any authorised MCP client connects to this server to discover and consume resources, prompts, skills, commands, and agent definitions from one place. The server is the single source of truth for all reusable AI assets across the platform.

---

## Background: MCP Primitives

The Model Context Protocol defines four core primitives that servers use to expose capabilities to clients. The Knowledge MCP Server uses all four.

| Primitive | What it is | How this server uses it |
|---|---|---|
| **Resource** | Named content items a server exposes for clients to discover (`resources/list`) and read (`resources/read`). Identified by a URI. Can be files, database records, or any structured data. | Every file in the knowledge directory is surfaced as a resource addressable by its `file:///knowledge/...` URI — reference documents, skill packages, agent definitions, and more. |
| **Prompt** | Parameterised message templates the server registers (`prompts/list`) and renders on demand (`prompts/get`). Arguments are substituted at render time; the result is a `messages[]` array ready for direct LLM submission. | Prompt templates, skill entry points, command definitions, and agent system prompts are all registered as prompts. A client calls `prompts/get` with arguments and receives a fully rendered message array. |
| **Tool** | Callable functions the server exposes for clients and models to invoke. Each tool has a typed input schema; the server executes the function and returns `content` (display text) and `structuredContent` (typed payload). | Ten typed tools cover all five content categories — e.g. `invoke_skill` substitutes inputs into a SKILL.md template and returns a rendered prompt; `load_agent` returns a full agent definition with its rendered system prompt. |
| **Notification** | Server-to-client push messages signalling state changes. Clients subscribe to specific resource URIs or to list-change events and receive notifications when content is added, removed, or updated. | When a file changes in the knowledge directory the server emits `notifications/resources/updated` to subscribed clients and `notifications/resources/list_changed` or `notifications/prompts/list_changed` when the set of entries changes. |

---

## Design Principles

**P1 — Single source of truth.** One server, one directory. No mirrors, no local copies that diverge.

**P2 — Filesystem native.** The knowledge directory is a plain filesystem tree versioned in Git. Any developer can read, write, and deploy content with standard tools. No proprietary database required to author.

**P3 — MCP protocol-first.** All access is through the MCP 2025-06-18 specification. No bespoke APIs, no direct filesystem mounts for consumers.

**P4 — Type-safe content.** Five distinct content types — resources, prompts, skills, commands, agents — each with a defined schema, discovery path, and rendering contract.

**P5 — Folder URI consistency.** Passing a folder URI to any list, read, or get operation returns all entries scoped to that folder. This behaviour is uniform across all content types and all tools.

**P6 — Read-only enforcement.** The server never writes to the knowledge directory. All mutation is performed by authorised humans or deployment pipelines operating through version control.

**P7 — OAuth 2.1 on all remote connections.** Every token is bound to this specific server via RFC 8707. No token sharing across servers.

---

## System Context

```mermaid
graph TD
    subgraph MAOS Platform
        A[MCP Client Application]
        B[Agent Pipeline]
        C[Value-Add MCP Server]
        K[Knowledge MCP Server]
        D[(Knowledge Directory\nGit-versioned)]
    end

    A -->|JSON-RPC 2.0\nStreamable HTTP / OAuth 2.1| K
    B -->|JSON-RPC 2.0\nStreamable HTTP / OAuth 2.1| K
    C -->|JSON-RPC 2.0\nStreamable HTTP / OAuth 2.1| K
    K -->|read-only filesystem mount| D
```

## Protocol and Capability Declaration

Transport: Streamable HTTP (HTTPS + SSE). Message format: JSON-RPC 2.0. Auth: OAuth 2.1 + PKCE with RFC 8707 resource binding.

```json
{
  "protocolVersion": "2025-06-18",
  "capabilities": {
    "resources": { "subscribe": true, "listChanged": true },
    "prompts":   { "listChanged": true },
    "tools":     { "listChanged": false }
  },
  "serverInfo": {
    "name":    "maos-knowledge-mcp-server",
    "title":   "MAOS Knowledge MCP Server",
    "version": "1.0.0"
  },
  "instructions": "Serves the MAOS knowledge directory as resources, prompts, skills, commands, and agent definitions. All content is under file:///knowledge/. Pass a folder URI to any list or get operation to enumerate entries. Use typed tools for skills, commands, and agents."
}
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| MCP SDK | `mcp[cli]` (Python), official SDK |
| ASGI server | Uvicorn |
| Auth | OAuth 2.1 + PKCE, `python-jose`, `authlib` |
| Full-text search | SQLite FTS5 (embedded) |
| Filesystem watch | `watchfiles` |
| Front-matter parsing | `python-frontmatter` |
| Deployment | Docker / OCI, read-only volume mount |

## Consumers at Launch

- MCP client applications — chat interfaces and interactive tools
- Agent pipelines — orchestrators and sub-agents performing multi-step workflows
- Value-add MCP servers — servers that enrich their own capabilities with knowledge assets
- Claude Code CLI sessions operating in MAOS context

---

## Decisions Log

| ID | Decision |
|---|---|
| D-001 | Protocol locked to `2025-06-18` for v1.0 |
| D-002 | Python 3.12 + FastMCP as server stack |
| D-003 | Knowledge directory is Git-native, read-only mount |
| D-004 | SQLite FTS5 for search — no external search dependency in v1.0 |
| D-005 | Five typed sub-folders are mandatory at every application leaf |
| D-006 | `invoke_skill` and `invoke_command` return resolved definitions only — they do not execute |
| D-007 | Dotted prompt name convention: `{domain}.{subdomain}.{app}.{name}` |

## Open Decisions

**OD-001 — Search index persistence** (MEDIUM): Rebuild on startup is simple and always correct; acceptable if startup time is under 10 seconds. Recommendation: rebuild for v1.0, revisit if startup latency is a problem in practice.

**OD-002 — Write path for AI-generated content** (MEDIUM): Agents may eventually need to propose new knowledge content. Recommendation: implement via GitHub PR tool when a confirmed requirement exists — not in v1.0.

**OD-003 — Prompt name collision** (LOW): Dotted name convention assumes application names are unique across the directory. Recommendation: use full dotted path including all domain segments as the prompt name to guarantee uniqueness.
