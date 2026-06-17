# Knowledge Repository — Instructions

This is a MAOS Knowledge content repository. You are working here to create, review, and improve knowledge content that will be served to AI assistants, agent pipelines, and coding agents via the MAOS Knowledge MCP Server.

Read these instructions before doing any work in this repository.

---

## What this repository is

Everything in this repository is exposed over the Model Context Protocol and consumed in real time by authorised MCP clients. When a file is merged to `main`, the MCP server detects the change and notifies all connected clients immediately. There are no local copies — this is the single source of truth.

The server is **read-only at runtime**. It never writes files. All changes go through Git: feature branch → PR → merge.

---

## Your role

- Create new skills, commands, agents, prompts, and resources when asked
- Review existing content for correctness, completeness, and schema compliance
- Never invent structure — follow the schemas in this file exactly
- Never modify a file without bumping its `version` field
- Never place files outside the five typed sub-folders (except support files inside a skill directory)

---

## Directory structure

The tree follows a fixed hierarchy: `domain → sub-domain → application`. The five typed sub-folders below are mandatory at every application leaf.

```
knowledge/
└── {domain}/
    └── {sub-domain}/
        └── {application}/
            ├── resources/
            ├── prompts/
            ├── skills/
            ├── commands/
            └── agents/
```

**Naming rule:** Every path segment must be `kebab-case`. No spaces, no underscores, no uppercase anywhere in the tree.

---

## When to use each content type

| Use this | When you need |
|---|---|
| `resources/` | Reference material — documents, schemas, data files — that agents retrieve and read |
| `prompts/` | A reusable, parameterised message template rendered into a `messages[]` array for LLM submission |
| `skills/` | A named, multi-step workflow an agent can invoke by name |
| `commands/` | A discrete, single-invocation executable with typed arguments and a danger declaration |
| `agents/` | A persistent autonomous actor specification: persona, model, tools, memory, and skills |

---

## Schemas

Follow these schemas exactly. Do not add fields that are not listed. Do not omit required fields.

### Resource

Any file in `resources/`. No required structure. Front-matter is optional and treated as metadata only.

---

### Prompt — `.prompt.md` or `.prompt.json`

```yaml
---
name:        kebab-case-name          # required — unique within this application
title:       Human-readable title     # required
version:     1.0.0                    # required — bump on every edit
description: One sentence.            # required
tags:                                 # optional
  - tag
arguments:                            # omit if none
  - name:        arg_name
    description: What this argument is
    required:    true
  - name:        optional_arg
    description: What this argument is
    required:    false
    default:     "default value"
---
Prompt body. Reference arguments as {{arg_name}}.
```

- Use `{{argument_name}}` syntax for all substitution points
- The body is the raw LLM message content — write it as if speaking directly to the model

---

### Skill — `skills/{skill-name}/SKILL.md`

Create a sub-directory named after the skill. `SKILL.md` is the only required file. Support files go in the same directory.

```yaml
---
skill:       skill-name               # required — must match the sub-directory name exactly
title:       Human-readable title     # required
version:     1.0.0                    # required — bump on every edit
description: One sentence.            # required
tags:                                 # optional
  - tag
triggers:                             # natural language phrases that activate this skill
  - "phrase"
inputs:                               # omit if none
  - name:        input_name
    type:        string               # string | integer | boolean
    required:    true
    description: What this input is
outputs:                              # omit if none
  - output_name
dependencies:                         # MCP servers required at runtime; omit if none
  - mcp-server-name
files:                                # list any support files; omit if none
  - path:        support-file.py
    role:        support
    description: What this file does
---
# Skill title

Step-by-step workflow instructions. Reference inputs as {{input_name}}.
```

- The `skill:` field must match the sub-directory name — the server uses this to resolve the entry point
- Write the body as explicit, numbered steps the executing agent will follow

---

### Command — `.cmd.json` or `.cmd.md`

```json
{
  "name":        "command-name",
  "title":       "Human-readable title",
  "version":     "1.0.0",
  "description": "One sentence.",
  "tags":        ["tag"],
  "command":     "tool-name action --flag {{arg_name}}",
  "arguments": [
    { "name": "arg_name",     "type": "string",  "required": true  },
    { "name": "optional_arg", "type": "string",  "required": false, "default": "standard" }
  ],
  "returns":      "description of return value",
  "danger_level": "read-only",
  "target_tool":  "target-mcp-server"
}
```

`danger_level` is mandatory and must be accurate — clients use it to decide whether to require user confirmation:

| Value | Meaning |
|---|---|
| `read-only` | No state mutation |
| `write` | Creates or modifies state |
| `destructive` | Irreversibly modifies or deletes |

---

### Agent — `.agent.md` or `.agent.json`

```yaml
---
agent:       agent-name               # required — kebab-case, unique within this application
title:       Human-readable title     # required
version:     1.0.0                    # required — bump on every edit
description: One sentence.            # required
tags:                                 # optional
  - tag
model:       provider/model-name      # required
temperature: 0.3                      # required
tools_allowed:                        # required — list only tools this agent needs
  - get_resource
  - search_knowledge
  - get_skill
memory:                               # omit if no persistent memory required
  type:      supabase-pgvector
  namespace: agent-name
  ttl_days:  90
skills:                               # omit if none
  - skill-name
system_prompt_extends: base-agent     # optional — must reference an existing agent name
---
System prompt body. Write the agent's persona, scope, and behavioural constraints here.
```

- If `system_prompt_extends` is set, it must name an existing agent in this repository — the server prepends that agent's system prompt before this body
- List only the tools the agent genuinely needs in `tools_allowed` — do not grant broad access by default

---

## Rules

1. `kebab-case` for all path segments — no exceptions
2. Every file must include a `version` field in semver; bump it on every substantive edit
3. The `skill:` front-matter field must match the skill's sub-directory name exactly
4. `danger_level` on every command is mandatory and must accurately reflect the operation's impact
5. `system_prompt_extends` must reference an existing agent in this repository
6. Support files belong only inside `skills/{name}/` — nowhere else outside the five typed folders
7. Do not add fields that are not in the schema above — unknown fields are ignored by the server and create drift
