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

**Example application paths for MAOS:**
```
knowledge/maos/dda/data-design-authority/
knowledge/maos/pipelines/ai-agile/
knowledge/maos/analytics/starburst-nl2sql/
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

**Rendering contract:** `invoke_skill` returns the rendered `SKILL.md` body as a `user` role message, with `{{input_name}}` references substituted.

### Command (`.cmd.json` / `.cmd.md`)

Discrete, single-invocation executable definitions carrying a `command` string and a `danger_level` declaration.

**JSON schema:**
```json
{
  "name":        "run-quality-check",
  "title":       "Run Data Quality Check",
  "version":     "1.0.0",
  "description": "Executes the DDA quality gate against a target entity",
  "command":     "dda quality-check --entity {{entity_id}} --profile {{profile}}",
  "arguments": [
    { "name": "entity_id", "type": "string",  "required": true  },
    { "name": "profile",   "type": "string",  "required": false, "default": "standard" }
  ],
  "returns":      "quality_report",
  "danger_level": "read-only",
  "target_tool":  "dda-mcp-server"
}
```

**Danger levels:**

| Level | Meaning | Client Behaviour |
|---|---|---|
| `read-only` | No state mutation | May invoke without confirmation |
| `write` | Creates or modifies state | Should present confirmation prompt |
| `destructive` | Irreversibly modifies or deletes | Must require explicit confirmation |

**Rendering contract:** `invoke_command` substitutes arguments into the `command` string and returns the resolved command. It does not execute.

### Agent (`.agent.md` / `.agent.json`)

Persistent specifications of autonomous actors — persona, model, tool allowlist, memory configuration, associated skills.

**Front-matter schema:**
```yaml
---
agent:       dda-analyst
title:       DDA Data Analyst Agent
version:     2.0.0
description: Chief Data Officer's second brain
model:       claude-sonnet-4-6
temperature: 0.2
tools_allowed:
  - get_resource
  - search_resource
  - invoke_skill
  - invoke_command
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
| Resource | ✅ | ✅ raw content | — | — | `get_resource`, `search_resource` |
| Prompt | ✅ raw file | ✅ raw content | ✅ with arguments | ✅ rendered `messages[]` | `get_prompt`, `list_prompts` |
| Skill | ✅ all files | ✅ any file | ✅ SKILL.md as template | ✅ rendered SKILL.md | `get_skill`, `invoke_skill` |
| Command | ✅ raw file | ✅ raw content | ✅ as instruction | ✅ rendered instruction | `get_command`, `invoke_command` |
| Agent | ✅ raw file | ✅ raw content | ✅ system prompt | ✅ rendered system prompt | `load_agent`, `list_agents` |

---

## Version Control and Deployment

1. Author creates or edits files in a feature branch
2. PR reviewed and merged to main
3. CD pipeline syncs main to the mounted filesystem
4. Server detects change via `watchfiles`, rebuilds content index, emits `notifications/resources/list_changed` and `notifications/prompts/list_changed` to subscribed clients
5. Clients re-call `resources/list` or `prompts/list` to refresh

The server never writes to the knowledge directory under any code path.
