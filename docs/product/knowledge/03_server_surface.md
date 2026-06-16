# 03 — Server Surface

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  

---

## MCP Primitives

### Resources

All five content types are surfaced as raw file content through the resource primitive. The host application or model determines what to do with the content.

**`resources/list`** — paginated list of all files in the knowledge directory.

```json
// Response (one entry shown)
{
  "resources": [{
    "uri":          "file:///knowledge/maos/dda/data-design-authority/resources/get_started.md",
    "name":         "get_started.md",
    "title":        "DDA Get Started & Onboarding Guide",
    "mimeType":     "text/md",
    "size":         8192,
    "annotations":  { "audience": ["user", "assistant"], "priority": 0.8,
                      "lastModified": "2026-05-01T09:00:00Z" }
  }],
  "nextCursor": "next-page-cursor"
}
```

**`resources/templates/list`** — URI templates for parameterised access.

```json
{ "resourceTemplates": [
    { "uriTemplate": "file:///knowledge/{+path}",
      "name": "knowledge-any",
      "title": "Knowledge Directory — Any Path",
      "description": "Resolves any path. Trailing slash returns directory listing." },
    { "uriTemplate": "file:///knowledge/{domain}/{subdomain}/{app}/skills/{skill}/SKILL.md",
      "name": "knowledge-skill", "title": "Knowledge Skill Entry Point", "mimeType": "text/markdown" },
    { "uriTemplate": "file:///knowledge/{domain}/{subdomain}/{app}/agents/{+path}",
      "name": "knowledge-agent", "title": "Knowledge Agent Definition" }
]}
```

**`resources/read`** — retrieve a file or directory listing.

```json
// File response
{ "contents": [{ "uri": "file:///knowledge/.../glossary.json",
                 "mimeType": "application/json", "text": "{ ... }" }] }

// Folder response (trailing-slash URI)
{ "contents": [
    { "uri": "file:///knowledge/.../skills/gmail-triage/",         "mimeType": "inode/directory" },
    { "uri": "file:///knowledge/.../skills/data-lineage-review/",  "mimeType": "inode/directory" }
]}
```

**`resources/subscribe`** — subscribe to change notifications on a specific URI. Server emits `notifications/resources/updated` when the file changes on disk.

---

### Prompts

Surfaces prompt, skill, command, and agent files as parameterised templates rendered into `messages[]` arrays.

**Prompt name convention:** The `name` field in every `prompts/list` entry is the file URI — identical to the URI returned by `resources/list` for the same file. This is the primary identifier across all MCP methods. `prompts/get` and all typed get tools accept the URI directly.

**`prompts/list`** — all registered templates with their arguments arrays.

```json
{ "prompts": [
    { "name": "file:///knowledge/maos/dda/data-design-authority/prompts/maturity-assessment.prompt.md",
      "title": "Data Maturity Assessment",
      "arguments": [
        { "name": "org_name", "description": "Organisation name", "required": true },
        { "name": "scope",    "description": "Assessment domain",  "required": false }
      ]},
    { "name": "file:///knowledge/maos/dda/data-design-authority/skills/gmail-triage/SKILL.md",
      "title": "Gmail Triage Skill",
      "arguments": [{ "name": "max_threads", "required": false }] },
    { "name": "file:///knowledge/maos/dda/data-design-authority/agents/dda-analyst.agent.md",
      "title": "DDA Data Analyst Agent — System Prompt", "arguments": [] }
]}
```

**`prompts/get`** — render a template with arguments substituted.

```json
// Request
{ "method": "prompts/get",
  "params": { "name": "file:///knowledge/maos/dda/data-design-authority/prompts/maturity-assessment.prompt.md",
              "arguments": { "org_name": "Acme Corp", "scope": "Data Governance" } } }

// Response
{ "result": { "description": "Data Maturity Assessment for Acme Corp — Data Governance scope",
              "messages": [{ "role": "user",
                             "content": { "type": "text", "text": "You are conducting..." }}] } }
```

---

### Notifications

| Notification | Trigger |
|---|---|
| `notifications/resources/list_changed` | File added or deleted anywhere in the knowledge directory |
| `notifications/resources/updated` | File content changed on a subscribed URI |
| `notifications/prompts/list_changed` | Prompt, skill, command, or agent file added, deleted, or renamed |

---

## Tool Surface

All tools return a `content` array (text summary for display) and a `structuredContent` object (full typed payload for programmatic use).

| Content Type | Search (Discovery) | List (Enumeration) | Read |
|---|---|---|---|
| All types | `search_knowledge` (v1), `hybrid_search`* (v2) | — | — |
| Resource | `search_resources` | — | `get_resource` (+ `query` for chunks*) |
| Prompt | `search_prompts` | `list_prompts` | `get_prompt` |
| Skill | `search_skills` | `get_skill` (folder URI) | `get_skill` |
| Command | `search_commands` | `get_command` (folder URI) | `get_command` |
| Agent | `search_agents` | `list_agents` | `load_agent` |

*v2 — requires pgvector infrastructure. Typed shortcuts delegate to `hybrid_search` in v2 deployments with no API change for callers.

### Resource Tools

**`get_resource`** — file content or directory listing by URI.

```json
{
  "name": "get_resource",
  "description": "Returns the content of a knowledge resource by URI. Pass a trailing-slash folder URI to list all entries within that folder. Works for all content types.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "uri": { "type": "string", "description": "file:// URI. Must begin with file:///knowledge/.",
               "pattern": "^file:///knowledge/" },
      "query": {
        "type": "string",
        "description": "When supplied, activates chunk retrieval — returns the most relevant sections of the document ranked by similarity to this query rather than the full file content. Requires v2 infrastructure (pgvector). Ignored for directory URIs and binary files."
      },
      "top_k": {
        "type": "integer",
        "default": 3,
        "minimum": 1,
        "maximum": 10,
        "description": "Number of chunks to return when query is supplied."
      }
    },
    "required": ["uri"]
  }
}
```

```
// Whole file (query omitted)
{ uri, name, mimeType, size, lastModified, isDirectory: false, text | blob }

// Directory (trailing-slash URI)
{ uri, isDirectory: true, entries: [{ uri, name, mimeType }] }

// Chunk retrieval (query supplied, v2)
{ uri, name, mimeType, isDirectory: false,
  chunks: [{ chunk_id, section_heading?, text, similarity_score }] }
```

> When `query` is supplied and `hybrid_search_enabled` is `False`, returns `-32603` with message `"Chunk retrieval not available — pgvector not configured"`.

---

> **Chunk-addressed URIs (v2):** Individual chunks are addressable via a fragment identifier on the file URI:
>
> ```
> file:///knowledge/maos/dda/data-design-authority/resources/data-model.md#chunk=3
> ```
>
> A `resources/read` request or a `get_resource` call on a chunk URI returns only that chunk's text with `mimeType: text/plain`. `hybrid_search` results may include `resource_link` entries pointing to chunk URIs.

---

**`search_knowledge`** — full-text and metadata search across the knowledge directory.

```json
{
  "name": "search_knowledge",
  "description": "Full-text and metadata search across the entire knowledge directory using SQLite FTS5. Searches all content types — resources, prompts, skills, commands, and agents — unless content_types is supplied to narrow scope. Searches file content, front-matter fields, and triggers[] arrays. Use typed shortcuts (search_skills, search_agents, etc.) when the content type is known. In v2, prefer hybrid_search for better recall.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search terms or phrase. Matched against file content, title, description, and triggers[] arrays."
      },
      "folder_uri": {
        "type": "string",
        "pattern": "^file:///knowledge/",
        "description": "Optional folder URI to restrict search scope."
      },
      "content_types": {
        "type": "array",
        "items": { "type": "string", "enum": ["resource","prompt","skill","command","agent"] },
        "description": "Optional filter. Omit to search all content types."
      },
      "tags": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Filter by tags declared in front-matter. All supplied tags must be present (AND semantics)."
      },
      "fields": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Front-matter fields to include in each result. E.g. [\"version\", \"triggers\", \"dependencies\"]. Omit for default snippet-only results."
      },
      "max_results": {
        "type": "integer",
        "default": 10,
        "minimum": 1,
        "maximum": 50
      }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, content_type, mimeType, snippet, score, tags?, fields? }] }`

---

### Typed Search Shortcuts

Five convenience wrappers around `search_knowledge` with `content_types` pre-set. These are thin wrappers — no independent index logic.

---

**`search_resources`** — scoped to `content_types: ["resource"]`

```json
{
  "name": "search_resources",
  "description": "Search the resources/ folder across the knowledge directory. Equivalent to search_knowledge with content_types set to resource.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":       { "type": "string" },
      "folder_uri":  { "type": "string", "pattern": "^file:///knowledge/" },
      "tags":        { "type": "array", "items": { "type": "string" } },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, mimeType, snippet, score }] }`

---

**`search_prompts`** — scoped to `content_types: ["prompt"]`

```json
{
  "name": "search_prompts",
  "description": "Search prompt templates across the knowledge directory. Equivalent to search_knowledge with content_types set to prompt. Returns arguments array in results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":       { "type": "string" },
      "folder_uri":  { "type": "string", "pattern": "^file:///knowledge/" },
      "tags":        { "type": "array", "items": { "type": "string" } },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, arguments, snippet, score }] }`

---

**`search_skills`** — scoped to `content_types: ["skill"]`

```json
{
  "name": "search_skills",
  "description": "Search skill definitions across the knowledge directory. Equivalent to search_knowledge with content_types set to skill. Searches triggers[] arrays — phrase queries like 'run email triage' will surface matching skills. Returns triggers, dependencies, and inputs in results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":       { "type": "string" },
      "folder_uri":  { "type": "string", "pattern": "^file:///knowledge/" },
      "tags":        { "type": "array", "items": { "type": "string" } },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, triggers, dependencies, inputs, snippet, score }] }`

---

**`search_commands`** — scoped to `content_types: ["command"]`

```json
{
  "name": "search_commands",
  "description": "Search command definitions across the knowledge directory. Equivalent to search_knowledge with content_types set to command. Returns danger_level and target_tool in results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":       { "type": "string" },
      "folder_uri":  { "type": "string", "pattern": "^file:///knowledge/" },
      "tags":        { "type": "array", "items": { "type": "string" } },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, danger_level, target_tool, snippet, score }] }`

---

**`search_agents`** — scoped to `content_types: ["agent"]`

```json
{
  "name": "search_agents",
  "description": "Search agent definitions across the knowledge directory. Equivalent to search_knowledge with content_types set to agent. Returns model, tools_allowed, and skills in results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":       { "type": "string" },
      "folder_uri":  { "type": "string", "pattern": "^file:///knowledge/" },
      "tags":        { "type": "array", "items": { "type": "string" } },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, model, tools_allowed, skills, snippet, score }] }`

---

### v2 Tool

**`hybrid_search`** *(v2 — requires pgvector infrastructure)*

```json
{
  "name": "hybrid_search",
  "description": "v2 replacement for search_knowledge. Combines FTS5 keyword search and pgvector semantic search using Reciprocal Rank Fusion. Accepts identical parameters to search_knowledge — all typed shortcuts (search_skills, search_agents, etc.) delegate to hybrid_search in v2 deployments via content_types. Use search_knowledge when pgvector is unavailable. Requires v2 infrastructure (pgvector).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "folder_uri": { "type": "string", "pattern": "^file:///knowledge/" },
      "content_types": {
        "type": "array",
        "items": { "type": "string", "enum": ["resource","prompt","skill","command","agent"] },
        "description": "Optional filter. Omit to search all content types."
      },
      "tags": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Filter by tags. All supplied tags must be present (AND semantics)."
      },
      "top_k": { "type": "integer", "default": 5, "minimum": 1, "maximum": 20 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, results: [{ uri, name, title, content_type, snippet, rrf_score, keyword_rank, semantic_rank }] }`

---

### Prompt Tools

**`list_prompts`** — all registered prompt templates, optionally scoped.

```json
{
  "name": "list_prompts",
  "description": "Returns registered prompt templates. Pass folder_uri to scope to an application. Includes prompts, skills, commands, and agents as promptable types.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "folder_uri":    { "type": "string", "pattern": "^file:///knowledge/" },
      "content_types": { "type": "array",
                         "items": { "type": "string", "enum": ["prompt","skill","command","agent"] }},
      "cursor":        { "type": "string" }
    }
  }
}
```

---

**`get_prompt`** — render a named template with argument substitution.

```json
{
  "name": "get_prompt",
  "description": "Renders a named prompt with argument substitution. Returns messages[] ready for LLM submission. Pass a folder URI as prompt_name to list promptable content under that path.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "prompt_name": { "type": "string",
                       "description": "Dotted name (e.g. maos.dda.data-design-authority.maturity-assessment) or folder URI" },
      "arguments":   { "type": "object", "additionalProperties": { "type": "string" } }
    },
    "required": ["prompt_name"]
  }
}
```

`structuredContent`: `{ prompt_name, description, messages: [{ role, content }] }`

---

### Skill Tools

**`get_skill`** — SKILL.md metadata and rendered content for a named skill. Folder URI lists all skills under that path.

```json
{
  "name": "get_skill",
  "description": "Returns the parsed SKILL.md entry point and metadata for a named skill. Pass a folder URI to list all skills. Set include_files=true to retrieve all files in the skill package.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "skill_name":    { "type": "string", "description": "Kebab-case skill name or folder URI" },
      "app_uri":       { "type": "string", "pattern": "^file:///knowledge/" },
      "include_files": { "type": "boolean", "default": false }
    },
    "required": ["skill_name"]
  }
}
```

`structuredContent`: `{ kind: "skill", name, title, version, uri, description, triggers, inputs, outputs, dependencies, files: [{ uri, role }], rendered_prompt }`

---

### Command Tools

**`get_command`** — parsed command definition including command string, arguments, and danger level. Folder URI lists all commands.

```json
{
  "name": "get_command",
  "description": "Returns the parsed definition of a named command. Pass a folder URI to list all commands under that path.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "command_name": { "type": "string", "description": "Kebab-case command name or folder URI" },
      "app_uri":      { "type": "string", "pattern": "^file:///knowledge/" }
    },
    "required": ["command_name"]
  }
}
```

`structuredContent`: `{ kind: "command", name, title, version, uri, description, command, arguments, returns, danger_level, target_tool, resolved_command, arguments_used }`

> `resolved_command` contains the command string with supplied `arguments` substituted. Pass arguments to `get_command` to receive the resolved string in the same response — no separate tool is required.

---

### Agent Tools

**`list_agents`** — all registered agent definitions, optionally scoped.

```json
{
  "name": "list_agents",
  "description": "Returns all registered agent definitions. Pass folder_uri to scope to an application.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "folder_uri": { "type": "string", "pattern": "^file:///knowledge/" },
      "cursor":     { "type": "string" }
    }
  }
}
```

`structuredContent`: `{ agents: [{ agent, title, version, description, model, uri, skills, tools_allowed }] }`

---

**`load_agent`** — full agent definition with rendered system prompt, ready for runtime instantiation. Folder URI lists agents.

```json
{
  "name": "load_agent",
  "description": "Returns the full agent definition including rendered system prompt, model config, tool allowlist, memory config, and skill list. system_prompt_extends causes the base agent system prompt to be prepended. Pass a folder URI to list available agents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent_name": { "type": "string", "description": "Kebab-case agent name or folder URI" },
      "app_uri":    { "type": "string", "pattern": "^file:///knowledge/" }
    },
    "required": ["agent_name"]
  }
}
```

`structuredContent`: `{ kind: "agent", agent, title, version, uri, model, temperature, tools_allowed, memory, skills, system_prompt, messages: [{ role: "system", content }] }`
