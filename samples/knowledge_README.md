# Knowledge Repository

This repository is a MAOS Knowledge content store — a Git-versioned directory served by the [MAOS Knowledge MCP Server](https://github.com/m-a-operating-system/shared-work/blob/master/docs/product/knowledge/01-overview.md). Everything in this repository is exposed over the Model Context Protocol and available to any authorised MCP client: AI assistants, agent pipelines, and coding agents.

---

## Structure

Content is organised as a three-level hierarchy — domain, sub-domain, application — with five typed sub-folders at every application leaf.

```
knowledge/
└── {domain}/
    └── {sub-domain}/
        └── {application}/
            ├── resources/      reference documents, schemas, data files
            ├── prompts/        parameterised LLM message templates
            ├── skills/         multi-step workflow packages
            ├── commands/       discrete executable definitions
            └── agents/         autonomous actor specifications
```

All path segments use `kebab-case`. No spaces, underscores, or uppercase anywhere in the tree.

---

## Content types

| Type | Folder | File suffix | Purpose |
|---|---|---|---|
| Resource | `resources/` | any | Reference material for agents and assistants to read |
| Prompt | `prompts/` | `.prompt.md` `.prompt.json` | Parameterised message templates rendered for LLM submission |
| Skill | `skills/{name}/` | `SKILL.md` | Multi-step workflow instructions with typed inputs and outputs |
| Command | `commands/` | `.cmd.json` `.cmd.md` | Discrete executable definitions with argument substitution |
| Agent | `agents/` | `.agent.md` `.agent.json` | Autonomous actor persona, model, tools, memory, and skills |

Full schemas and examples for each type are in [`docs/product/knowledge/02-knowledge-directory-and-content-types.md`](https://github.com/m-a-operating-system/shared-work/blob/master/docs/product/knowledge/02-knowledge-directory-and-content-types.md).

---

## Adding content

1. Create a feature branch from `main`
2. Add or edit files following the schemas below
3. Open a pull request — reviewers check schema compliance and content quality
4. Merge to `main` — the MCP server detects the change, rebuilds its index, and notifies subscribed clients

The server is read-only at runtime. It never writes to this repository.

---

## Schemas at a glance

### Prompt front-matter

```yaml
---
name:        kebab-case-name
title:       Human-readable title
version:     1.0.0
description: One sentence — what this prompt does
tags:
  - tag
arguments:
  - name:     arg_name
    description: What this argument is
    required: true
---
Prompt body. Use {{arg_name}} for substitution.
```

### Skill front-matter (`SKILL.md`)

```yaml
---
skill:       skill-name        # must match sub-directory name
title:       Human-readable title
version:     1.0.0
description: One sentence — what this skill does
tags:
  - tag
triggers:
  - "natural language phrase"
inputs:
  - name: input_name
    type: string
    required: true
    description: What this input is
outputs:
  - output_name
dependencies:
  - mcp-server-name
---
# Skill title

Step-by-step workflow instructions. Reference inputs as {{input_name}}.
```

### Command (`.cmd.json`)

```json
{
  "name":        "command-name",
  "title":       "Human-readable title",
  "version":     "1.0.0",
  "description": "One sentence — what this command does",
  "tags":        ["tag"],
  "command":     "tool action --flag {{arg_name}}",
  "arguments": [
    { "name": "arg_name", "type": "string", "required": true }
  ],
  "returns":      "what the command returns",
  "danger_level": "read-only",
  "target_tool":  "target-mcp-server"
}
```

`danger_level` values: `read-only` · `write` · `destructive`

### Agent front-matter (`.agent.md`)

```yaml
---
agent:       agent-name
title:       Human-readable title
version:     1.0.0
description: One sentence — what this agent does
tags:
  - tag
model:       claude-sonnet-4-6
temperature: 0.3
tools_allowed:
  - get_resource
  - search_knowledge
  - get_skill
memory:
  type:      supabase-pgvector
  namespace: agent-name
  ttl_days:  90
skills:
  - skill-name
---
System prompt body.
```

---

## Rules

- Path segments: `kebab-case` only
- Every file must have a `version` field in semver — bump on every substantive edit
- `skill:` in front-matter must match the skill's sub-directory name
- `danger_level` on commands is mandatory and must accurately reflect the operation
- `system_prompt_extends` on agents must reference an existing agent name in this repository
- Support files belong inside `skills/{name}/` only — do not place non-content files at the application level or above
