# 07 — Tool Access

## Host-registered MCP servers

The AI Chat Platform has **no built-in always-on tool**. Every MCP server available in a session is registered by the host application in the `mcpServers` section of the application config (see [00-host-application-config.md](./00-host-application-config.md)).

Host teams can discover available MCP tools via the **MCP Repository** complementary service before registering them (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md)).

If no MCP servers are registered, the assistant operates in **prompt-only mode** — it answers from system prompt knowledge only, with no live data access.

### Access tiers

| Tier | Behaviour |
|------|-----------|
| **Always-on** | Active in every session; cannot be disabled by the end user. Designated by setting `accessTier: "always-on"` in the server's config entry. Host applications should designate as always-on only the MCP servers that should be available to all sessions without user action. |
| **Opt-in** | Off by default; enabled by the end user per session via the tool selection panel. Does not persist across sessions. Designated by `accessTier: "opt-in"`. |

The always-on tier should be used sparingly. Each always-on tool's description is injected into the system prompt on every session, consuming token budget. Opt-in tools inject their description only when enabled.

### Role-based tool access

MCP servers can be restricted to specific user roles via the `roles` field in the server config entry. Roles are matched against the user's JWT claims forwarded via the authentication bridge. If `roles` is empty, the server is available to all authenticated users.

A user who does not hold a required role will not see the server in the tool selection panel and cannot activate it. The server description will not be injected into their system prompt.

---

## Guided workflows

Guided workflows are host-defined conversation starters accessible from the **Workflow Library** panel. They are configured in the `workflows` section of the application config.

| Invocation method | How it works |
|------------------|-------------|
| Click in Workflow Library panel | Single click opens a parameter form (if parameters are defined); the assembled prompt is injected into the input field; user reviews and submits |
| `@`-binding | If a workflow is configured as a bindable type, typing `@` followed by the workflow name injects the workflow prompt on submission |
| Natural language | Phrasing that closely matches a workflow's purpose may cause the model to suggest the workflow and offer to launch it |

Guided workflows are **host-managed** — the prompts are version-controlled in the application config. End users cannot create or modify guided workflows.

### Workflow parameter types

| Parameter type | UI presentation |
|---------------|-----------------|
| `binding` | Opens an `@`-binding typeahead scoped to the configured `bindableTypeId` |
| `text` | Free-text input field with the parameter's `label` |
| `select` | Dropdown populated from the `options` array in the parameter config |

Required parameters must be filled before the workflow can be launched. Optional parameters may be left empty.

---

## Tool call transparency

Every MCP tool invocation renders as a **collapsible disclosure card** in the conversation thread. This is mandatory — tool calls are never hidden (P1 — transparency first).

### Disclosure card anatomy

```
┌─────────────────────────────────────────────────────┐
│ 🔧 Governance Platform · list_entities  ✓ 12 results  ▼ │
└─────────────────────────────────────────────────────┘
```

On expansion:

```
┌─────────────────────────────────────────────────────┐
│ 🔧 Governance Platform · list_entities  ✓ 12 results  ▲ │
├─────────────────────────────────────────────────────┤
│ Input parameters                                    │
│   domain: "Finance"                                 │
│   classification: "Gold"                            │
│   limit: 50                                         │
├─────────────────────────────────────────────────────┤
│ Response status: 200 OK · 145ms                     │
│ Result: 12 entities returned (total: 12)            │
└─────────────────────────────────────────────────────┘
```

| Card element | Content |
|-------------|---------|
| Tool name | MCP server name + tool name (e.g. `Governance Platform · list_entities`) |
| Status icon | ✓ success / ✗ error / ⏳ in-progress |
| Result summary | Brief outcome (e.g. `12 results`, `error: permission denied`) |
| Expand/collapse | Chevron — collapsed by default |
| Input parameters | Full parameter object |
| Response status | HTTP status code + latency in milliseconds |
| Result detail | Full result summary or error detail |

### Write operations

When the model proposes a write action (an MCP tool call that modifies data), the assistant **must** surface a confirmation step before executing the call:

```
┌─────────────────────────────────────────────────────┐
│ ✏️  Proposed update to Finance Domain               │
├─────────────────────────────────────────────────────┤
│ Before: Owner → Jane Smith                          │
│ After:  Owner → Alex Johnson                        │
├─────────────────────────────────────────────────────┤
│ [Confirm update]        [Cancel]                    │
└─────────────────────────────────────────────────────┘
```

The confirmation step is mandatory and non-configurable. The assistant never implies a write has occurred if it has not.

### Error states in disclosures

When a tool call fails, the disclosure card shows error status with full detail. The model surfaces the error to the user in plain language, citing the specific tool and the nature of the failure.

### MCP server unavailability

If a host MCP server is unreachable:
- An **always-on server failure** triggers a **degraded-mode banner** across the session: *"[Server name] is unavailable. [AssistantName] is answering from its own knowledge only — data may not reflect the current state of your application."* The session continues in text-only mode. No silent failure.
- An **opt-in server failure** shows an error in the tool call disclosure card. The user is informed and may disable the failing server for the session.

The degraded-mode banner is persistent until connectivity is restored.

---

## Tool selection panel (UI)

The tool selection panel is accessible via the tool icon in the input area. It shows:

- All **always-on** servers with a permanent "always active" indicator (no toggle)
- All **opt-in** servers with `enabled: true` in the registry: name, one-sentence description, and a toggle switch (off by default)
- Opt-in servers restricted by role are not shown to users who don't hold the required role

Tools enabled in the panel are active for the remainder of the session only. The panel state does not persist across sessions.

---

## Tool access in shared sessions

The active model and enabled opt-in tools apply to the session as a whole. The user who submits a message determines the tool context for that turn based on their current tool panel state. Other participants see the tool call disclosure cards in the thread.

Participants cannot access MCP tools beyond their own permission level. If a tool call succeeds for the submitting user but the host MCP server enforces per-user access control, other participants may see restricted results in the disclosure card (`[Restricted — insufficient permissions]` on the result summary).

---

## Complementary MCP services in tool context

Beyond host-registered MCP servers, two platform-level ecosystem services are available for integration:

- **MCP Repository** — Host teams use this during configuration to discover and browse available MCP tools before registering them. It is not directly invoked in conversations but informs the tool registry setup.
- **MCP Resources Service** — Provides centralised skills, static resources, and reusable prompt artefacts. Host applications may choose to register the MCP Resources Service as an opt-in or always-on server, making its capabilities available during conversations.

See [17-complementary-mcp-services.md](./17-complementary-mcp-services.md) for full descriptions of both services.
