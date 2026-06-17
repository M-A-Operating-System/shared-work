# CLAUDE.md — Knowledge Repository

## What this repository is

This is a MAOS Knowledge Repository — a Git-versioned content directory served by the **MAOS Knowledge MCP Server**. The server exposes everything in this directory as resources, prompts, skills, commands, and agent definitions over the Model Context Protocol (MCP 2025-06-18). Any authorised MCP client — AI assistants, agent pipelines, coding agents — can discover and consume the content here in real time.

---

## Your role

You are helping to develop and maintain knowledge content in this repository. Your work is to:

- Author new skills, commands, agents, prompts, and reference resources following the schemas below
- Review and improve existing content for correctness, completeness, and consistency
- Ensure all files conform to the required folder structure, file naming, and front-matter schemas

The server is **read-only at runtime** — it never writes to this directory. All changes go through Git (feature branch → PR → merge to main). You author files here; the server detects changes automatically after merge and notifies all subscribed clients.

---

## Directory structure

The tree is organised as a hierarchy: `domain → sub-domain → application`. The five typed sub-folders are mandatory at every application leaf.

```
knowledge/
└── {domain}/
    └── {sub-domain}/
        └── {application}/          ← one node per application or MCP server
            ├── resources/          ← reference documents, schemas, data files
            ├── prompts/            ← parameterised LLM message templates
            ├── skills/             ← multi-step workflow packages
            ├── commands/           ← discrete executable definitions
            └── agents/             ← autonomous actor specifications
```

**Naming convention:** All path segments use `kebab-case`. No spaces, no underscores, no uppercase anywhere in the tree.

---

## Content type schemas

### Resource (`resources/`)

Any file format. No required front-matter. Used for reference documents, glossaries, JSON schemas, and data files that agents and assistants retrieve and read.

Create a resource when you have reference material consumers need to read — not execute. Nest files in sub-directories freely; the URI mirrors the filesystem path.

---

### Prompt (`prompts/` — `.prompt.md` or `.prompt.json`)

Parameterised templates rendered into a `messages[]` array for direct LLM submission. Use `{{argument_name}}` syntax for substitution points.

**Required front-matter:**

```yaml
---
name:        kebab-case-name          # unique within this application
title:       Human-readable title
version:     1.0.0
description: One sentence describing what this prompt does
tags:
  - tag-one
arguments:
  - name:        arg_name
    description: What this argument represents
    required:    true
  - name:        optional_arg
    description: What this argument represents
    required:    false
    default:     "default value"
---
Prompt body. Reference arguments as {{arg_name}}.
```

The prompt body follows the front-matter and is the raw LLM message content. The server substitutes all `{{argument}}` references at render time and returns a `messages[]` array with a single `user` role message.

---

### Skill (`skills/{skill-name}/SKILL.md`)

Multi-step workflow packages. Each skill is a sub-directory containing a required `SKILL.md` entry point plus any support files.

**Required front-matter for `SKILL.md`:**

```yaml
---
skill:       skill-name               # must match the sub-directory name exactly
title:       Human-readable title
version:     1.0.0
description: One sentence describing what this skill does
tags:
  - tag-one
triggers:
  - "natural language phrase that activates this skill"
inputs:
  - name:        input_name
    type:        string                # string | integer | boolean
    required:    true
    description: What this input represents
outputs:
  - output_name
dependencies:
  - mcp-server-name                   # MCP servers this skill requires at runtime
files:
  - path:  support-file.py
    role:  support
    description: What this file does
---
# Skill title

Step-by-step instructions for executing this workflow. Reference inputs as {{input_name}}.
```

The `skill:` front-matter field must match the sub-directory name. Support files in the same directory are accessible as resources individually.

---

### Command (`commands/` — `.cmd.json` or `.cmd.md`)

Discrete, single-invocation executable definitions. A command carries a `command` string with `{{argument}}` placeholders and a mandatory `danger_level` declaration.

**JSON format (`.cmd.json`):**

```json
{
  "name":        "command-name",
  "title":       "Human-readable title",
  "version":     "1.0.0",
  "description": "One sentence describing what this command does",
  "tags":        ["tag-one"],
  "command":     "tool-name action --flag {{arg_name}}",
  "arguments": [
    { "name": "arg_name",     "type": "string",  "required": true  },
    { "name": "optional_arg", "type": "string",  "required": false, "default": "standard" }
  ],
  "returns":      "description of what the command returns",
  "danger_level": "read-only",
  "target_tool":  "target-mcp-server"
}
```

**Danger levels — must be accurate:**

| Level | Meaning | Client behaviour |
|---|---|---|
| `read-only` | No state mutation | May invoke without confirmation |
| `write` | Creates or modifies state | Should present confirmation prompt |
| `destructive` | Irreversibly modifies or deletes | Must require explicit user confirmation |

---

### Agent (`agents/` — `.agent.md` or `.agent.json`)

Persistent specifications of autonomous actors: persona, model, tool allowlist, memory configuration, and associated skills.

**Required front-matter for `.agent.md`:**

```yaml
---
agent:       agent-name
title:       Human-readable title
version:     1.0.0
description: One sentence describing this agent's role
tags:
  - tag-one
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
system_prompt_extends: base-agent-name   # optional — prepends a base agent's system prompt
---
System prompt body. Describe the agent's persona, operating scope, and behavioural constraints.
```

If `system_prompt_extends` is set, it must reference an existing `agent:` name in this repository. The server prepends the base agent's system prompt before this agent's body.

---

## Key rules

- **Naming:** All path segments are `kebab-case`. No spaces, underscores, or uppercase anywhere in the tree.
- **Skill entry point:** `SKILL.md` is the only recognised skill entry point. Its `skill:` front-matter field must match the sub-directory name.
- **Versioning:** Every file carries a semver `version` field. Bump `PATCH` on every substantive edit; `MINOR` when adding new fields or arguments; `MAJOR` for breaking changes.
- **danger_level:** Mandatory on all commands and must be accurate — clients use it to determine whether to require explicit user confirmation before invoking.
- **system_prompt_extends:** Must reference an existing agent in this repository. The server will error on load if the reference cannot be resolved.
- **File placement:** Do not create files outside the five typed sub-folders unless they are support files inside a `skills/{name}/` directory.
- **No writes at runtime:** Never assume the server or any agent will write files here. All content changes go through Git.
