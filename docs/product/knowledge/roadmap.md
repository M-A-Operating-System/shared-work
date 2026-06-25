# ROADMAP — MAOS Knowledge MCP Server

**Date:** 2026-06-16

This roadmap describes the evolution from a simple embedded knowledge folder co-located with a single application, through to a centralized governed knowledge platform serving the full MAOS suite. Each version is independently deployable and leaves the API surface of prior versions intact.

---

## v1.0 — Embedded Knowledge: Resources and Skills

The knowledge folder lives inside the application repo and is deployed with it. The MCP server is co-located with the application — it is not a shared service. No cross-application sharing. No dedicated knowledge infrastructure. The pattern is proven at zero operational cost before any architectural commitments are made.

### Scope

Two content types only: **resources** and **skills**. Everything else is deferred until the pattern is validated.

### Folder Structure

```
{application-repo}/
├── knowledge/
│   ├── resources/          # reference files — markdown, JSON, CSV
│   │   └── glossary.json
│   └── skills/             # skill packages
│       └── gmail-triage/
│           ├── SKILL.md
│           └── parse_state.py
├── src/
│   └── ...
└── docker-compose.yml      # knowledge-mcp co-located with the application
```

The knowledge directory is mounted read-only into the MCP server container. It is versioned and deployed as part of the application — a knowledge change is a code change, goes through the same PR and CI process.

### Tool Surface

| Tool | Purpose |
|---|---|
| `get_resource` | Retrieve a file or directory listing by URI |
| `search_knowledge` | FTS5 keyword search across resources and skills |
| `search_resources` | Shortcut — search_knowledge scoped to resources |
| `search_skills` | Shortcut — search_knowledge scoped to skills, searches triggers[] |
| `get_skill` | Retrieve SKILL.md metadata and rendered prompt |
| `get_prompt` | Render a .prompt.md file with argument substitution |
| `list_prompts` | Enumerate all promptable content (skills and any .prompt.md files) |

### MCP Primitives

| Primitive | Methods |
|---|---|
| Resources | `resources/list`, `resources/templates/list`, `resources/read`, `resources/subscribe` |
| Prompts | `prompts/list`, `prompts/get` |
| Tools | `tools/list`, `tools/call` |

### Infrastructure

- Python 3.12 + FastMCP
- SQLite FTS5 — embedded, zero external dependency
- `watchfiles` for filesystem change detection
- Docker, knowledge directory as read-only bind mount from application repo
- OAuth 2.1 + PKCE

### URI Convention

```
file:///knowledge/resources/{+path}
file:///knowledge/skills/{skill-name}/SKILL.md
```

The root is `file:///knowledge/` — simple, flat, no domain/app segments needed at this stage. The URI convention is forward-compatible; the domain/app segments are added in v2.0 without breaking existing URIs for single-application deployments that choose to adopt them.

### What Is Out of Scope

Prompts as a standalone content type, commands, agents, cross-application sharing, entitlements, semantic search, and authoring tooling are all deferred. The goal of v1.0 is a working, deployable server that a single application can use to serve its own knowledge content to its own agents.

---

## v1.1 — Full Content Types, Still Embedded

Adds the remaining three content types within the same embedded, co-located deployment model. The knowledge folder structure gains `prompts/`, `commands/`, and `agents/` folders alongside the existing `resources/` and `skills/`. No new infrastructure. The MCP server is still part of the application repo.

### What Changes

**New content types:**

| Type | Folder | Entry point |
|---|---|---|
| Prompt | `knowledge/prompts/` | `.prompt.md` / `.prompt.json` |
| Command | `knowledge/commands/` | `.cmd.md` / `.cmd.json` |
| Agent | `knowledge/agents/` | `.agent.md` / `.agent.json` |

**New tools:**

| Tool | Purpose |
|---|---|
| `search_prompts` | Shortcut — search_knowledge scoped to prompts |
| `search_commands` | Shortcut — search_knowledge scoped to commands, includes danger_level in results |
| `search_agents` | Shortcut — search_knowledge scoped to agents, includes model and tools_allowed in results |
| `get_command` | Retrieve command definition; returns resolved_command with arguments substituted |
| `list_agents` | Enumerate agent definitions |
| `load_agent` | Return full agent definition with rendered system prompt |

**Front-matter additions:**
- `tags` field added to all typed schemas — enables faceted filtering across all search tools
- `triggers[]` indexed as a dedicated FTS5 column with boosted weight — phrase-match queries against `search_skills` and `search_commands` now surface matching content by natural language trigger

**Operational additions:**
- Prometheus-compatible `/metrics` endpoint
- Structured JSON logging with correlation IDs per request
- `knowledge-mcp validate ./knowledge/` CLI — checks front-matter schema compliance for all typed files before deployment

### What Does Not Change

Deployment model, infrastructure, URI convention, and all v1.0 tools are unchanged.

---

## v2.0 — Centralised Knowledge Server

The knowledge folder moves out of the application repo into a dedicated Git repository. The MCP server becomes a shared service running independently of any application. Multiple applications each have their own sub-tree. Applications change from running their own embedded server to connecting as MCP clients to the shared server.

### Architectural Change

```
Before (v1.x):
  application-repo/
  ├── knowledge/          # owned by this application
  └── src/

After (v2.0):
  knowledge-repo/         # standalone Git repo
  └── knowledge/
      └── {domain}/
          └── {sub-domain}/
              └── {application}/
                  ├── resources/
                  ├── skills/
                  ├── prompts/
                  ├── commands/
                  └── agents/

  application-repo/       # no longer contains knowledge/
  └── src/                # connects to shared knowledge MCP server as a client
```

### URI Convention Update

The URI root gains domain and application segments to namespace content across multiple consumers:

```
file:///knowledge/{domain}/{sub-domain}/{application}/resources/{+path}
file:///knowledge/{domain}/{sub-domain}/{application}/skills/{skill}/SKILL.md
```

Applications that adopted the flat v1.x URI convention update their client configuration to use the new root. All tool names and parameter schemas are unchanged.

### New Tools

| Tool | Purpose |
|---|---|
| `list_applications` | Enumerate all application nodes in the knowledge directory with per-type entry counts |

### New Infrastructure

- Dedicated knowledge Git repository with CD pipeline syncing main branch to the server's mounted filesystem
- `watchfiles` now serves multiple consumers — `listChanged` and `updated` notifications fan out to all subscribed clients
- Shared OAuth 2.1 authorization server; per-application scopes available but flat `knowledge:read` remains the default

### Migration Path

1. Create `knowledge-repo` and move each application's `knowledge/` folder to its namespaced sub-tree
2. Deploy the centralized knowledge MCP server pointing at the new repo mount
3. Update each application's MCP client configuration to point at the shared server endpoint and the new URI root
4. Remove the embedded server from each application's `docker-compose.yml`

No tool API changes. No knowledge content changes beyond the folder relocation.

---

## v2.1 — Search, RAG, and Vector Retrieval

This version adds pgvector-backed semantic search and chunk retrieval. Nothing in the v1.x or v2.0 surface changes — v2.1 is purely additive.

### New Capability: `search`

Replaces `search_knowledge` as the standard discovery tool. Combines FTS5 keyword ranking and pgvector semantic ranking using Reciprocal Rank Fusion. Accepts identical parameters to `search_knowledge` — all typed shortcuts (`search_skills`, `search_agents` etc.) delegate to `search` automatically once v2.1 is deployed. `search_knowledge` remains available as a fallback.

```
Input:  query, folder_uri?, content_types?, tags?, top_k
Output: [{ uri, name, title, content_type, snippet, rrf_score, keyword_rank, semantic_rank }]
```

### New Capability: Chunk Retrieval via `get_resource`

Chunk retrieval is not a new tool — it is an extension of `get_resource` activated by supplying an optional `query` parameter. When `query` is present, the server returns ranked sections of the document rather than the full content.

```
get_resource(uri, query="data retention policy", top_k=3)
→ { chunks: [{ chunk_id, section_heading, text, similarity_score }] }
```

Individual chunks are addressable via fragment URI:
```
file:///knowledge/maos/dda/data-design-authority/resources/data-model.md#chunk=3
```

### New Infrastructure

| Component | Purpose |
|---|---|
| Supabase pgvector | `knowledge_vectors` schema — one embedding row per file, one per chunk |
| `registry/embeddings.py` | Generates embeddings on reindex, upserts to pgvector with `embedding_model` and `embedding_dimensions` stored as row metadata |
| `registry/chunker.py` | Section-based splitting for markdown (on `##` headings); sliding window with overlap for prose |
| `tools/search_tools_v2.py` | Implements `search`; `get_resource` chunk path handled in `resource_tools.py` |

### Graceful Degradation

`search` and chunk retrieval via `get_resource` are gated by `KNOWLEDGE_MCP_SEARCH_ENABLED=true`. When the flag is absent or false both return `-32603` with message `"Not available — pgvector not configured"`. All FTS5 tools remain fully operational.

### Open Decision

**OD-005 — Embedding model versioning:** Store `embedding_model` and `embedding_dimensions` as metadata on every pgvector row. A model change without re-indexing produces silently degraded results — the stored metadata enables the server to detect and reject stale embeddings after an upgrade.

---

## v3.0 — Knowledge Authoring and Entitlements

This version transforms the server from read-only infrastructure into a governed knowledge platform. It is the first version with a write path.

### Knowledge Authoring Frontend

A web application for creating and editing knowledge content without touching Git or the filesystem directly. Targeted at practitioners — CDOs, data stewards, solution architects — who need to publish prompts, skills, and agent definitions but are not developers.

**Capabilities:**

- Create and edit all five content types through structured forms — front-matter fields rendered as typed inputs, body rendered as a markdown editor
- Front-matter schema validation on save — malformed content is rejected before it reaches the server index
- Preview rendering — prompt templates rendered with sample arguments, skills displayed as their final injected form
- Draft and publish states — content exists in draft (visible only to the author) until explicitly published to the live index
- Publish workflow — optional approval gate; a reviewer approves or rejects before content goes live
- Version history — each published version is a Git commit; authors can view diff and roll back

**Implementation approach:** The authoring frontend calls a write API layer that manages Git operations on the knowledge repository. The MCP server itself remains read-only — it continues to serve from the filesystem as before. The write path is entirely in the authoring layer, not in the MCP server.

### Entitlements

Per-application access control replacing the flat `knowledge:read` scope.

**Read entitlements:** A client's access token carries claims scoping it to one or more application sub-trees. A token scoped to `maos/dda/data-design-authority` cannot read content from `maos/pipelines/ai-agile`. The MCP server enforces this at the URI validation step — a request for a URI outside the token's scoped sub-trees returns `403`.

**Author entitlements:** The authoring frontend enforces who can create and edit content within each application sub-tree. Separate from read entitlements — a user may be able to read across multiple applications but author only within their own.

**Approval entitlements:** Designated reviewers per application sub-tree. The publish workflow routes approval requests to the correct reviewer based on the content's application path.

### What Does Not Change

The MCP server tool surface, URI convention, primitive methods, and all consumer integrations are unchanged. Entitlements are enforced at the token and URI validation layer — the tools themselves have no awareness of entitlements.

---

## Summary

| Version | Deployment Model | Content Types | Search | Authoring |
|---|---|---|---|---|
| v1.0 | Embedded in app repo | Resources, Skills | FTS5 keyword | Git / filesystem |
| v1.1 | Embedded in app repo | + Prompts, Commands, Agents | FTS5 + tags + triggers | Git / filesystem |
| v2.0 | Centralised shared server | All five | FTS5 + tags + triggers | Git / filesystem |
| v2.1 | Centralised shared server | All five | + Hybrid (FTS5 + pgvector + RRF), chunk retrieval | Git / filesystem |
| v3.0 | Centralised shared server | All five | Hybrid + chunk retrieval | Web authoring frontend + entitlements |

---

## Discovery and Retrieval Architecture

The search/get boundary is stable across all versions. Search tools are discovery — they return URIs and snippets. Get tools are retrieval — they return content at a known URI. v2.1 adds richer discovery; v3.0 adds authoring. The boundary itself never changes.

```
┌─────────────────────────────────────────────────────────────┐
│                       Discovery Layer                       │
│                                                             │
│  v1   search_knowledge     → FTS5, all content types       │
│  v1   search_resources     → shortcut: resource            │
│  v1   search_skills        → shortcut: skill + triggers[]  │
│  v1.1 search_prompts       → shortcut: prompt              │
│  v1.1 search_commands      → shortcut: command             │
│  v1.1 search_agents        → shortcut: agent               │
│  v1   list_prompts         → enumeration by folder         │
│  v1.1 list_agents          → enumeration by folder         │
│  v1   get_skill (folder)   → enumeration by folder         │
│  v1.1 get_command (folder) → enumeration by folder         │
│  v2.0 list_applications    → enumerate all app nodes       │
│                                                             │
│  v2.1 search        → FTS5 + pgvector + RRF         │
│       typed shortcuts delegate to search in v2.1     │
└─────────────────────────┬───────────────────────────────────┘
                          │  URI
┌─────────────────────────▼───────────────────────────────────┐
│                       Retrieval Layer                       │
│                                                             │
│  v1   get_resource         → full file or directory         │
│  v2.1 get_resource + query → ranked chunks of a file        │
│  v1   get_prompt           → rendered messages[]            │
│  v1   get_skill            → metadata + rendered_prompt     │
│  v1.1 get_command          → definition + resolved_command  │
│  v1.1 load_agent           → full agent definition          │
└─────────────────────────────────────────────────────────────┘
```
