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

Ten tools across five content-type pairs. All tools return a `content` array (text summary for display) and a `structuredContent` object (full typed payload for programmatic use).

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
               "pattern": "^file:///knowledge/" }
    },
    "required": ["uri"]
  }
}
```

`structuredContent` for a file: `{ uri, name, mimeType, size, lastModified, isDirectory: false, text | blob }`  
`structuredContent` for a folder: `{ uri, isDirectory: true, entries: [{ uri, name, mimeType }] }`

---

**`search_resource`** — full-text and metadata search across the knowledge directory.

```json
{
  "name": "search_resource",
  "description": "Full-text and metadata search. Scope by folder URI or content type filter. Returns ranked results with snippets.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query":         { "type": "string" },
      "folder_uri":    { "type": "string", "pattern": "^file:///knowledge/" },
      "content_types": { "type": "array",
                         "items": { "type": "string",
                                    "enum": ["resource","prompt","skill","command","agent"] }},
      "mime_types":    { "type": "array", "items": { "type": "string" }},
      "max_results":   { "type": "integer", "default": 10, "minimum": 1, "maximum": 50 }
    },
    "required": ["query"]
  }
}
```

`structuredContent`: `{ query, total_hits, results: [{ uri, name, title, content_type, mimeType, snippet, score }] }`

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
