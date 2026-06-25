# 05 — Client Integration Guide

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  

---

## Connection

### Server Manifest

```
GET https://knowledge-mcp.maoperatingsystem.com/.well-known/mcp-server
```

```json
{
  "mcp_version": "2025-06-18",
  "name":        "MAOS Knowledge MCP Server",
  "endpoint":    "https://knowledge-mcp.maoperatingsystem.com/mcp",
  "transport":   "http",
  "auth": {
    "required":     true,
    "methods":      ["oauth2"],
    "metadata_url": "https://auth.maoperatingsystem.com/.well-known/oauth-authorization-server"
  },
  "capabilities": ["tools", "resources", "prompts"]
}
```

### Python SDK Initialization

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client(
    "https://knowledge-mcp.maoperatingsystem.com/mcp",
    headers={"Authorization": f"Bearer {access_token}"}
) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # session ready
```

### Claude Code CLI Configuration

```json
// .claude/settings.json
{
  "mcpServers": {
    "maos-knowledge": {
      "transport": "http",
      "url":       "https://knowledge-mcp.maoperatingsystem.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MAOS_KNOWLEDGE_MCP_TOKEN}"
      }
    }
  }
}
```

---

## Common Patterns

### Discover all skills for an application

```python
result = await session.call_tool("get_skill", {
    "skill_name": "file:///knowledge/maos/dda/data-design-authority/skills/"
})
# result.structuredContent["entries"] — list of skill directories
```

### Get a skill with rendered prompt

```python
result = await session.call_tool("get_skill", {
    "skill_name": "gmail-triage",
    "app_uri":    "file:///knowledge/maos/dda/data-design-authority/skills/",
    "arguments":  { "max_threads": "30", "lookback_hours": "48" }
})
rendered_prompt = result.structuredContent["rendered_prompt"]
triggers        = result.structuredContent["triggers"]
dependencies    = result.structuredContent["dependencies"]
# Inject rendered_prompt into current conversation context
```

### Load an agent before instantiation

```python
result = await session.call_tool("load_agent", {
    "agent_name": "dda-analyst",
    "app_uri":    "file:///knowledge/maos/dda/data-design-authority/agents/"
})
agent         = result.structuredContent
system_prompt = agent["system_prompt"]
model         = agent["model"]
tools_allowed = agent["tools_allowed"]
memory_config = agent["memory"]
```

### Search then retrieve

```python
search = await session.call_tool("search_knowledge", {
    "query":         "data retention",
    "folder_uri":    "file:///knowledge/maos/dda/data-design-authority/",
    "content_types": ["resource", "prompt"],
    "max_results":   5
})
top_uri = search.structuredContent["results"][0]["uri"]
content = await session.call_tool("get_resource", { "uri": top_uri })
```

### Get relevant sections of a large document

```python
result = await session.call_tool("get_resource", {
    "uri":   "file:///knowledge/maos/dda/data-design-authority/resources/data-model.md",
    "query": "data retention policy minimum years",
    "top_k": 3
})
chunks = result.structuredContent["chunks"]
# chunks: [{ chunk_id, section_heading, text, similarity_score }]
```

### Render a prompt template

```python
result = await session.call_tool("get_prompt", {
    "prompt_name": "file:///knowledge/maos/dda/data-design-authority/prompts/maturity-assessment.prompt.md",
    "arguments":   { "org_name": "Acme Corp", "scope": "Data Governance" }
})
messages = result.structuredContent["messages"]
# Pass to LLM API
```

### Subscribe to resource changes

```python
await session.subscribe_resource(
    "file:///knowledge/maos/dda/data-design-authority/agents/dda-analyst.agent.md"
)
# Re-fetch and reload agent definition on notifications/resources/updated
```

---

## Per-Consumer Guidance

### DDA AI Chat

At session start: call `load_agent` with `dda-analyst` to retrieve system prompt and tool config; subscribe to the agent file URI; call `list_prompts` scoped to the prompts folder to populate the prompt picker.

During session: use `get_prompt` to render prompt templates; `search_knowledge` for knowledge lookup; `get_skill` when the user triggers a skill by phrase match against `triggers[]` — `get_skill` returns the rendered prompt and typed metadata in one call.

### AI Agile Pipeline Orchestrator

At pipeline start: call `load_agent` with `pipeline-orchestrator`; call `get_skill` for each skill in `agent.skills[]` to pre-cache SKILL.md content; subscribe to skill file URIs for invalidation.

During execution: use `get_command` with arguments supplied — the `resolved_command` field in `structuredContent` returns the command string with arguments substituted, ready to pass to the target MCP server; use `get_resource` to retrieve reference schemas, supplying `query` to retrieve only relevant sections from large documents.

### Claude Code CLI Sessions

Once connected via the settings above, Claude Code can call any tool directly in a session:

```
> Use get_skill to load the data-lineage-review skill for this task
> Search for resources related to the concept-type enum before making changes
> Load the dda-analyst agent definition and use its tool allowlist as a constraint
```

---

## Error Handling

| Code | Client Action |
|---|---|
| `-32002` Resource not found | Do not retry without correcting the URI |
| `-32602` Invalid params | Fix the URI or argument before retrying |
| `-32603` Internal error | Retry with exponential backoff; alert on repeated failure |
| HTTP `429` Rate limited | Honor `Retry-After`; implement client-side request queuing |
| HTTP `401` Unauthorized | Refresh token via OAuth 2.1 refresh flow; retry once |

## Offline / Unavailable Behavior

Cache the last successful response per URI with a 5-minute TTL. On connection failure or `5xx`, serve the cached version and log a warning. On cache miss with server unavailable, surface a user-visible notice and continue operating — do not surface server unavailability as an agent failure.

---

## Roadmap

**v1.1 — Operational hardening**

- Prometheus-compatible `/metrics` — request counts, latency, index size, active SSE connections
- Structured JSON logging with correlation IDs, client ID, URI, latency per request
- Content validation CLI: `knowledge-mcp validate ./knowledge/` — checks front-matter schema compliance for all typed files
- BM25 weight tuning for FTS5 based on observed query patterns

**v1.2 — Discovery enhancements**

- Tag-based filtering in `search_knowledge` — tags declared in front-matter
- `triggers` index — `search_knowledge` searches skill and command `triggers[]` arrays for phrase-match discovery
- `list_applications` tool — lists all application nodes with entry counts per content type
- Dependency graph resolution — `get_skill` and `load_agent` optionally resolve dependency chains

**v2.0 — Write path via GitHub PR** *(conditional on confirmed requirement)*

- `propose_resource` tool — agent proposes new content; server opens a GitHub PR via the GitHub MCP server
- Staging sub-tree — `/staging/` accessible to proposing agent; promoted to `/knowledge/` on merge
