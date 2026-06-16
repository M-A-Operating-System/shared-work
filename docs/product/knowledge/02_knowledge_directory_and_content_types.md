# 02 — Knowledge Directory and Content Types

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  

---

## Directory Layout

The knowledge directory is a Git repository mounted read-only into the server process. The tree is arbitrarily deep above the application node. The five typed sub-folders are mandatory at every application leaf.

```
knowledge/
└── {domain}/
    └── {sub-domain}/                    # arbitrary depth
        └── {application-mcp-server}/   # one per application
            ├── resources/               # raw reference files
            │   ├── data-model.md
            │   ├── glossary.json
            │   └── schemas/
            │       └── concept-entity.json
            ├── prompts/                 # parameterised LLM templates
            │   ├── maturity-assessment.prompt.md
            │   └── onboarding-survey.prompt.md
            ├── skills/                  # multi-file workflow packages
            │   ├── gmail-triage/
            │   │   ├── SKILL.md         # entry point — required
            │   │   └── parse_state.py
            │   └── data-lineage-review/
            │       └── SKILL.md
            ├── commands/                # discrete executable definitions
            │   ├── run-quality-check.cmd.json
            │   └── generate-report.cmd.md
            └── agents/                 # agent persona definitions
                ├── dda-analyst.agent.md
                └── pipeline-orchestrator.agent.json
```

All path segments use kebab-case. No spaces, no underscores, no uppercase. The application segment must match the name in the application's own MCP server manifest.

## File Suffix Registry

| Folder | Recognised Suffixes | Content Type |
|---|---|---|
| `resources/` | `*` (any) | Resource |
| `prompts/` | `.prompt.md`, `.prompt.json` | Prompt |
| `skills/` | `SKILL.md` (one per skill sub-directory) | Skill entry point |
| `commands/` | `.cmd.md`, `.cmd.json` | Command |
| `agents/` | `.agent.md`, `.agent.json` | Agent |

Files not matching a typed suffix within a typed folder are surfaced as raw resources but excluded from typed registries.

## URI Scheme

All content is addressed using `file://` URIs rooted at `file:///knowledge/`. The server enforces this prefix on every incoming URI.

```
file:///knowledge/{domain}/{sub-domain}/{app}/{kind}/{+path}
```

**Folder URI behaviour:** Passing a trailing-slash URI to any list, read, or get operation returns all direct children scoped to that folder. This is uniform across all content types and all MCP methods. Directory entries are identified with MIME type `inode/directory`.

**Example URIs:**
```
# Specific file
file:///knowledge/maos/dda/data-design-authority/resources/glossary.json

# Folder listing
file:///knowledge/maos/dda/data-design-authority/skills/

# Skill entry point
file:///knowledge/maos/dda/data-design-authority/skills/gmail-triage/SKILL.md

# Application root
file:///knowledge/maos/dda/data-design-authority/
```

> **Note:** While all content types are reachable via the generic URI scheme above, each typed content category also has its own dedicated entry points. Skills, prompts, commands, and agents can be discovered and retrieved through their respective typed tools (`get_skill`, `get_prompt`, `list_prompts`, `get_command`, `list_agents`, `load_agent`) and via the `prompts/*` MCP primitives. These typed entry points return structured metadata, rendered templates, and resolved definitions — not just raw file content.

---

## Content Type Schemas

### Resource

Any file in `resources/`. No structural convention. Front-matter optional and treated as metadata only. Returns `text` (UTF-8) or `blob` (base64) via `resources/read`. Directory URIs return a listing of children.

### Prompt (`.prompt.md` / `.prompt.json`)

Parameterised templates rendered into a `messages[]` array for direct LLM submission.

**Front-matter schema:**
```yaml
---
name:        maturity-assessment       # kebab-case, unique within app
title:       Data Maturity Assessment
version:     1.1.0
description: Guides an organisation through a structured data maturity survey
tags:
  - governance
  - assessment
arguments:
  - name:        org_name
    description: Organisation name
    required:    true
  - name:        scope
    description: Assessment domain
    required:    false
    default:     "General"
---
You are conducting a data maturity assessment for {{org_name}}.
Scope: {{scope}}...
```

**Prompt name convention:** The `name` field in `prompts/list` responses is the file URI — the same URI returned by `resources/list` for the same file. This eliminates a second identifier for the same resource. `prompts/get` and all typed get tools accept the URI directly. Uniqueness is guaranteed by the filesystem.

**Rendering contract:** `prompts/get` and `get_prompt` substitute all `{{argument}}` references and return a `messages[]` array with a single `user` role message.

### Skill (`{skill-name}/SKILL.md`)

Multi-file packages encoding a reusable, multi-step workflow. `SKILL.md` at the root of the skill sub-directory is the entry point. Support files in the same directory are accessible individually as resources.

**Front-matter schema:**
```yaml
---
skill:       gmail-triage              # matches sub-directory name
title:       Gmail Triage Skill
version:     1.2.0
description: Runs a Gmail triage and todo-management cycle
tags:
  - email
  - productivity
triggers:
  - "run email triage"
  - "check my inbox for todos"
inputs:
  - name:     max_threads
    type:     integer
    default:  50
    description: Maximum threads to process per cycle
outputs:
  - action_list
  - reply_needed
dependencies:
  - gmail-mcp
  - google-drive-mcp
files:
  - path:  parse_state.py
    role:  support
    description: Parses triage state from Drive markdown
---
# Gmail Triage Skill
...step-by-step workflow instructions...
```

**Rendering contract:** `get_skill` returns the rendered `SKILL.md` body with `{{input_name}}` references substituted in the `rendered_prompt` field of `structuredContent`, alongside full typed metadata. No separate invocation tool exists.

### Command (`.cmd.json` / `.cmd.md`)

Discrete, single-invocation executable definitions carrying a `command` string and a `danger_level` declaration.

**JSON schema:**
```json
{
  "name":        "run-quality-check",
  "title":       "Run Data Quality Check",
  "version":     "1.0.0",
  "description": "Executes a quality gate check against a target entity",
  "tags":        ["governance", "quality"],
  "command":     "quality-check --entity {{entity_id}} --profile {{profile}}",
  "arguments": [
    { "name": "entity_id", "type": "string",  "required": true  },
    { "name": "profile",   "type": "string",  "required": false, "default": "standard" }
  ],
  "returns":      "quality_report",
  "danger_level": "read-only",
  "target_tool":  "target-mcp-server"
}
```

**Danger levels:**

| Level | Meaning | Client Behaviour |
|---|---|---|
| `read-only` | No state mutation | May invoke without confirmation |
| `write` | Creates or modifies state | Should present confirmation prompt |
| `destructive` | Irreversibly modifies or deletes | Must require explicit confirmation |

**Rendering contract:** `get_command` substitutes supplied arguments into the `command` string and returns the result in the `resolved_command` field of `structuredContent`. It does not execute. No separate invocation tool exists.

### Agent (`.agent.md` / `.agent.json`)

Persistent specifications of autonomous actors — persona, model, tool allowlist, memory configuration, associated skills.

**Front-matter schema:**
```yaml
---
agent:       dda-analyst
title:       DDA Data Analyst Agent
version:     2.0.0
description: Chief Data Officer's second brain
tags:
  - analyst
  - governance
model:       claude-sonnet-4-6
temperature: 0.2
tools_allowed:
  - get_resource
  - search_knowledge
  - get_skill
  - get_command
memory:
  type:      supabase-pgvector
  namespace: dda-analyst
  ttl_days:  90
skills:
  - data-lineage-review
  - gmail-triage
system_prompt_extends: base-cdaio-persona  # optional — prepends base agent system prompt
---
You are the DDA Analyst — the Chief Data Officer's second brain...
```

**Rendering contract:** `load_agent` returns the full agent metadata in `structuredContent` plus a `messages[]` array containing the system prompt as a `system` role message. If `system_prompt_extends` is set, the base agent's system prompt is prepended.

---

## Content Type to MCP Primitive Mapping

| Content Type | `resources/list` | `resources/read` | `prompts/list` | `prompts/get` | Tools |
|---|---|---|---|---|---|
| Resource | ✅ | ✅ raw content | — | — | `get_resource`, `search_resources` |
| Prompt | ✅ raw file | ✅ raw content | ✅ with arguments | ✅ rendered `messages[]` | `get_prompt`, `list_prompts` |
| Skill | ✅ all files | ✅ any file | ✅ SKILL.md as template | ✅ rendered SKILL.md | `get_skill` |
| Command | ✅ raw file | ✅ raw content | ✅ as instruction | ✅ rendered instruction | `get_command` |
| Agent | ✅ raw file | ✅ raw content | ✅ system prompt | ✅ rendered system prompt | `load_agent`, `list_agents` |

---

## Version Control and Deployment

1. Author creates or edits files in a feature branch
2. PR reviewed and merged to main
3. CD pipeline syncs main to the mounted filesystem
4. Server detects change via `watchfiles`, rebuilds content index, emits `notifications/resources/list_changed` and `notifications/prompts/list_changed` to subscribed clients
5. Clients re-call `resources/list` or `prompts/list` to refresh

The server never writes to the knowledge directory under any code path.
