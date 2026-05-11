# 13 — MCP Tool Registry

## Purpose

The MCP tool registry is the **per-tenant runtime list of MCP servers** available in a session. It is derived directly from the `mcpServers` array in the tenant's application config — there is no separate registry file or database table beyond the config itself.

When a session starts, the platform resolves the active registry from the tenant's current config and:
1. Activates all `always-on` servers immediately
2. Makes `opt-in` servers available in the tool selection panel (but not active)
3. Injects descriptions for active servers into the system prompt

This document covers the registry model, how host teams populate it, the relationship to the MCP Repository complementary service, and how the registry interacts with the MCP Resources Service.

---

## Access tiers

| Tier | Behaviour |
|------|-----------|
| **Always-on** | Active in every session; description injected into system prompt automatically; user cannot disable |
| **Opt-in** | Off by default; user activates per session via tool selection panel; description injected only when active; does not persist across sessions |

Use `always-on` for servers that are foundational to the assistant's usefulness (e.g. the host application's primary data API). Use `opt-in` for servers that are situationally useful but not needed in every session (e.g. a warehouse query tool, an external analytics service).

---

## Registry schema

The registry is the `mcpServers` array in the application config. Each entry:

```json
{
  "id":          "string — unique within tenant",
  "name":        "string — shown in tool selection panel",
  "description": "string — injected into system prompt when active; write for the model",
  "endpoint":    "string — MCP-compliant HTTPS URL",
  "authType":    "bearer | api-key | none",
  "accessTier":  "always-on | opt-in",
  "roles":       ["array of role identifiers — empty = all users"],
  "enabled":     true
}
```

The `enabled` field allows stubs to be added before an endpoint is production-ready. Setting `enabled: false` keeps the entry in the config but excludes it from session resolution — the tool does not appear in the tool selection panel and its description is never injected.

Full field reference is in [01-host-application-config.md — mcpServers](./01-host-application-config.md).

---

## Tool description quality

The `description` field is **the most important field in the registry**. It is injected directly into the model's system prompt and directly influences whether the model invokes the correct tool for a given user query.

**Good description (written for the model):**
> Provides access to Acme Corp's data governance platform. Use this tool to look up data domains, entities, quality metrics, data ownership records, and policy information. Use when the user asks about data assets, governance status, quality issues, owners, or compliance.

**Poor description (written for the user):**
> Governance Platform MCP server.

Application Admins should review and iterate on tool descriptions based on improvement signals. Poor tool descriptions are one of the most common causes of the model choosing the wrong tool.

---

## Adding a new MCP server to the registry

| Step | Description |
|------|-------------|
| 1. Identify the server | Browse the **MCP Repository** to find an existing server, or confirm the host team's own MCP endpoint |
| 2. Verify the endpoint | Confirm the MCP endpoint is production-ready and accessible from the platform's network |
| 3. Confirm auth compatibility | Verify that `bearer` (host JWT forwarded), `api-key`, or `none` auth is appropriate |
| 4. Draft the description | Write the description for the model — describe what data it provides and when to use it |
| 5. Decide access tier | `always-on` if needed in every session; `opt-in` if situationally useful |
| 6. Decide role restriction | Which users should see or activate this tool; empty `roles` array = all users |
| 7. Update the config | Add the entry to `mcpServers` via the Config Editor UI or Admin API |
| 8. Validate | The platform runs an endpoint reachability check on config submission |
| 9. Monitor | Watch improvement signals in the first weeks for tool invocation failures or misuse |

Servers may be added as `enabled: false` stubs before their endpoint is ready. This allows the description to be drafted and reviewed before the server becomes active.

---

## Versioning

Tool registry changes are versioned as part of the overall application config (see [01-host-application-config.md — Config versioning](./01-host-application-config.md)):

| Change | Config version increment |
|--------|--------------------------|
| New MCP server added | Minor |
| Existing server description or name updated | Patch |
| Server removed or `enabled` changed to `false` | Minor |
| `authType`, `endpoint`, or `accessTier` changed | Minor |

---

## Relationship to the MCP Repository

The **MCP Repository** is a complementary ecosystem service (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md)) that provides a discoverable catalogue of available MCP servers — both from the platform ecosystem and from external contributors.

The relationship to the per-tenant registry is:

```
MCP Repository               Per-tenant registry
(discover & browse)    →     (configure & activate)
```

Host teams use the MCP Repository to find servers that already exist and are ready to integrate. Once a suitable server is found, its details (endpoint, suggested description, auth type) are used to populate the `mcpServers` entry in the application config.

The MCP Repository is a read-only browsing surface at config time — it is not invoked at session runtime. The per-tenant registry (derived from the config) is the authoritative source for what is available in a session.

---

## Relationship to the MCP Resources Service

The **MCP Resources Service** is a complementary ecosystem service that provides centralised skills, static resources, and reusable prompt artefacts for use across the MCP ecosystem (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md)).

Host applications may register the MCP Resources Service as an MCP server in their tenant registry (typically as an `opt-in` server). When registered and activated in a session:
- The model can invoke the MCP Resources Service to retrieve platform-standard skills, guidance documents, and reusable prompt patterns
- Resources returned appear as MCP tool results in the conversation thread with the standard tool call disclosure card
- Resources are added to the session artefact tray for download

The MCP Resources Service endpoint is published in the MCP Repository.

---

## System prompt injection

When a server is active in a session (always-on or opt-in enabled), its `description` is injected into the system prompt at session start. This informs the model of the server's purpose and when to invoke it.

Always-on server descriptions are always injected. Opt-in server descriptions are injected only when the user has enabled the server for the session. This keeps the system prompt lean when opt-in tools are not in use.

Combined description injection is included in the prompt cache — the cache hit rate metric accounts for the combined length of all active tool descriptions.
