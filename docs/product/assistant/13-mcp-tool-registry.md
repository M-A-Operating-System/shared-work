# 13 — MCP Tool Registry

## Purpose

The MCP tool registry is a **proposed build-time JSON configuration file** (`src/config/mcp-tool-registry.json`) in the DDA repository. This file does not yet exist — it is specified here as a new artefact to be created as part of the Data AI Assistant build. It will be the **single source of truth** for which MCP tools are available in Data AI Assistant sessions and how they behave.

The registry is **bundled into and consumed by the MCP client** as part of the standard deployment pipeline — it is not fetched at runtime from a separate source or a database table. The MCP client reads it at startup and makes the configured tools available to the session. Adding or removing a tool requires a client build and deploy; there is no runtime mechanism for modifying the tool surface.

---

## Access tiers

| Tier | Behaviour | Current tools |
|------|-----------|--------------|
| **Always-on** | Active in every session; cannot be disabled by users | DDA MCP server |
| **Opt-in** | Off by default; enabled per session by the user via the tool selection panel; does not persist across sessions | Additional registered tools |

The always-on tier is intentionally minimal. The DDA MCP server is the only tool that should be active in every session — it provides the authoritative data estate context that anchors every conversation.

---

## Registry schema

```json
{
  "mcpToolRegistry": {
    "version": "1.0.0",
    "tools": [
      {
        "id": "dda",
        "name": "DDA Platform",
        "description": "Data Design & Architecture platform — entity master, governance workflows, data models, lineage, and quality. Primary tool for all sessions.",
        "endpoint": "https://datadesign.maoperatingsystem.com/mcp",
        "accessTier": "always-on",
        "roles": ["all"],
        "enabled": true
      },
      {
        "id": "placeholder",
        "name": "Future Integration",
        "description": "Placeholder — specific tools to be confirmed during build scoping.",
        "endpoint": null,
        "accessTier": "opt-in",
        "roles": ["all"],
        "enabled": false
      }
    ]
  }
}
```

---

## Registry field reference

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique internal identifier — never displayed to users |
| `name` | string | Human-readable name shown in the tool selection panel |
| `description` | string | One-sentence description injected into the system prompt when the tool is enabled |
| `endpoint` | string \| null | MCP server URL. `null` for stubs not yet production-ready |
| `accessTier` | `"always-on"` \| `"opt-in"` | Determines activation behaviour |
| `roles` | string[] | Permitted DDA role identifiers. `["all"]` = no role restriction |
| `enabled` | boolean | Build-time on/off switch — `false` stubs are present in config but inactive |

---

## Tool selection panel (UI)

The tool selection panel is accessible via the tool icon in the input area. It shows:

- All `opt-in` tools with `enabled: true`
- Name and one-sentence description for each tool
- Toggle switch per tool (off by default)
- A permanent note indicating that the DDA Platform tool is always active

Tools enabled in the panel are active for the remainder of the session only. The panel state does not persist across sessions.

---

## System prompt injection

When a tool is active in a session (either always-on or opt-in enabled), its `description` is injected into the system prompt at session start. This informs the model of the tool's purpose and when to invoke it.

The DDA MCP server `description` is always injected. Opt-in tool descriptions are injected only when the user has enabled the tool for the session.

---

## Adding a new tool to the registry

New tools require the following before being added:

| Pre-requisite | Detail |
|--------------|--------|
| GitHub issue | Documents the tool's purpose, endpoint, and intended users |
| PDD authoring | Product Design Document approved by CDAiO |
| Confirmed MCP endpoint | A production-ready MCP server URL (or `null` for stub) |
| Authentication compatibility | Verified that the tool's auth is compatible with Supabase JWT |
| CDAiO-approved description | One-sentence description reviewed and approved — this is injected directly into the system prompt |
| Role restriction decision | Which DDA roles may access this tool (`["all"]` or specific role identifiers) |
| Build deployment | Registry change requires a build + deploy |

Tools **may be added as `enabled: false` stubs** before their endpoint is ready. This allows the system prompt injection to be drafted and reviewed before the tool is active.

---

## Versioning

The registry follows **semantic versioning**:

| Increment | When |
|-----------|------|
| **Minor** (e.g. 1.0.0 → 1.1.0) | New tool added |
| **Major** (e.g. 1.0.0 → 2.0.0) | Schema changes (new fields, field type changes, breaking changes) |
| **Patch** (e.g. 1.0.0 → 1.0.1) | Description or name updates to existing tools; endpoint changes |

---

## Relationship to `entityRegistry.ts` and `entityMeta.ts`

The MCP tool registry governs **which MCP servers** are available in Data AI Assistant sessions. It is distinct from `src/config/entityRegistry.ts` (source of truth) and the generated `supabase/functions/_shared/entityMeta.ts`, which govern which **entity types are bindable** via `@`-binding and which entity-level tools the DDA MCP server exposes.

Any entity type with a valid `mcp` block in `entityMeta.ts` is automatically bindable — no registry change is required to make a new entity type available in `@`-binding typeahead. The registry controls the tool servers, not the entity surface within those servers.
