# 01 — Overview

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Protocol:** MCP 2025-06-18  
**Author:** Andrew Bush / Fortium Partners  

---

## Problem Statement

MAOS platform components — the DDA, the AI Agile pipeline, the Starburst NL2SQL server, and downstream agent systems — each carry their own local copies of prompts, skill definitions, agent personas, and reference documentation. There is no single authoritative location to publish, version, and retrieve these assets. When a prompt is updated, every consumer must be updated in lockstep. There is no discovery mechanism and no governed access pattern.

## Solution

A centralised MCP server exposing a structured knowledge directory over the Model Context Protocol. Every MAOS component and any authorised MCP client connects to this server to discover and consume resources, prompts, skills, commands, and agent definitions from one place. The server is the single source of truth for all reusable AI assets across the platform.

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

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAOS Platform                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  DDA AI Chat │  │  AI Agile    │  │  Starburst NL2SQL    │  │
│  │  (MCP Client)│  │  Agents      │  │  MCP Server          │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         └─────────────────┴──────────────────────┘             │
│                           │  JSON-RPC 2.0                       │
│                           │  Streamable HTTP / OAuth 2.1        │
│                           ▼                                     │
│              ┌────────────────────────┐                         │
│              │  Knowledge MCP Server  │                         │
│              └────────────┬───────────┘                         │
│                           │  read-only filesystem mount         │
│                           ▼                                     │
│              ┌────────────────────────┐                         │
│              │  Knowledge Directory   │                         │
│              │  (Git-versioned)       │                         │
│              └────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
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

- DDA platform AI Chat
- AI Agile pipeline agents (PDD Writer, Sizing Agent, Orchestrator)
- Starburst NL2SQL MCP server
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

**OD-001 — Multi-tenancy scoping** (HIGH): Current `knowledge:read` scope grants full directory access to all clients. If multi-tenant deployments are required, per-sub-tree scoping will need a claims-based filtering mechanism. Recommendation: launch with flat scope, revisit when multi-tenant requirement is confirmed.

**OD-002 — Search index persistence** (MEDIUM): Rebuild on startup is simple and always correct; acceptable if startup time is under 10 seconds. Recommendation: rebuild for v1.0, revisit if startup latency is a problem in practice.

**OD-003 — Write path for AI-generated content** (MEDIUM): Agents may eventually need to propose new knowledge content. Recommendation: implement via GitHub PR tool when a confirmed requirement exists — not in v1.0.

**OD-004 — Prompt name collision** (LOW): Dotted name convention assumes application names are unique across the directory. Recommendation: use full dotted path including all domain segments as the prompt name to guarantee uniqueness.
