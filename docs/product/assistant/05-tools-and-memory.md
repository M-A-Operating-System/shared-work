# 05 — Tools, Memory, and Sharing

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Tool access

### Host-registered MCP servers

The AI Chat Platform has **no built-in always-on tool**. Every MCP server available in a session is registered by the host application in the `mcpServers` section of the application config (see [02-host-config.md](./02-host-config.md)).

Host teams can discover available MCP tools via the **MCP Repository** complementary service before registering them (see [08-platform-operations.md](./08-platform-operations.md)).

If no MCP servers are registered, the assistant operates in **prompt-only mode** — it answers from system prompt knowledge only, with no live data access.

#### Access tiers

| Tier | Behaviour |
|------|-----------|
| **Always-on** | Active in every session; cannot be disabled by the end user. Designated by setting `accessTier: "always-on"` in the server's config entry. Host applications should designate as always-on only the MCP servers that should be available to all sessions without user action. |
| **Opt-in** | Off by default; enabled by the end user per session via the tool selection panel. Does not persist across sessions. Designated by `accessTier: "opt-in"`. |

The always-on tier should be used sparingly. Each always-on tool's description is injected into the system prompt on every session, consuming token budget. Opt-in tools inject their description only when enabled.

#### Role-based tool access

MCP servers can be restricted to specific user roles via the `roles` field in the server config entry. Roles are matched against the user's JWT claims forwarded via the authentication bridge. If `roles` is empty, the server is available to all authenticated users.

A user who does not hold a required role will not see the server in the tool selection panel and cannot activate it. The server description will not be injected into their system prompt.

---

### Guided workflows

Guided workflows are host-defined conversation starters accessible from the **Workflow Library** panel. They are configured in the `workflows` section of the application config.

| Invocation method | How it works |
|------------------|-------------|
| Click in Workflow Library panel | Single click opens a parameter form (if parameters are defined); the assembled prompt is injected into the input field; user reviews and submits |
| `@`-binding | If a workflow is configured as a bindable type, typing `@` followed by the workflow name injects the workflow prompt on submission |
| Natural language | Phrasing that closely matches a workflow's purpose may cause the model to suggest the workflow and offer to launch it |

Guided workflows are **host-managed** — the prompts are version-controlled in the application config. End users cannot create or modify guided workflows.

#### Workflow parameter types

| Parameter type | UI presentation |
|---------------|-----------------|
| `binding` | Opens an `@`-binding typeahead scoped to the configured `bindableTypeId` |
| `text` | Free-text input field with the parameter's `label` |
| `select` | Dropdown populated from the `options` array in the parameter config |

Required parameters must be filled before the workflow can be launched. Optional parameters may be left empty.

---

### Tool call transparency

Every MCP tool invocation renders as a **collapsible disclosure card** in the conversation thread. This is mandatory — tool calls are never hidden (P1 — transparency first).

#### Disclosure card anatomy

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

#### Write operations

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

#### Error states in disclosures

When a tool call fails, the disclosure card shows error status with full detail. The model surfaces the error to the user in plain language, citing the specific tool and the nature of the failure.

#### MCP server unavailability

If a host MCP server is unreachable:
- An **always-on server failure** triggers a **degraded-mode banner** across the session: *"[Server name] is unavailable. [AssistantName] is answering from its own knowledge only — data may not reflect the current state of your application."* The session continues in text-only mode. No silent failure.
- An **opt-in server failure** shows an error in the tool call disclosure card. The user is informed and may disable the failing server for the session.

The degraded-mode banner is persistent until connectivity is restored.

---

### Tool selection panel (UI)

The tool selection panel is accessible via the tool icon in the input area. It shows:

- All **always-on** servers with a permanent "always active" indicator (no toggle)
- All **opt-in** servers with `enabled: true` in the registry: name, one-sentence description, and a toggle switch (off by default)
- Opt-in servers restricted by role are not shown to users who don't hold the required role

Tools enabled in the panel are active for the remainder of the session only. The panel state does not persist across sessions.

---

### Tool access in shared sessions

The active model and enabled opt-in tools apply to the session as a whole. The user who submits a message determines the tool context for that turn based on their current tool panel state. Other participants see the tool call disclosure cards in the thread.

Participants cannot access MCP tools beyond their own permission level. If a tool call succeeds for the submitting user but the host MCP server enforces per-user access control, other participants may see restricted results in the disclosure card (`[Restricted — insufficient permissions]` on the result summary).

---

### Complementary MCP services in tool context

Beyond host-registered MCP servers, three platform-level ecosystem services are available for integration:

- **MCP Repository** — Host teams use this during configuration to discover and browse available MCP tools before registering them. It is not directly invoked in conversations but informs the tool registry setup.
- **MCP Resources Service** — Provides centralised skills, static resources, and reusable prompt artefacts. Host applications may choose to register the MCP Resources Service as an opt-in or always-on server, making its capabilities available during conversations.
- **Web Search Service** — Provides real-time web search and page retrieval. Registered by host applications as an opt-in or always-on MCP server for sessions that need current information beyond the host's own data.

See [08-platform-operations.md](./08-platform-operations.md) for full descriptions of all three services.

---

## MCP tool registry

### Purpose

The MCP tool registry is the **per-tenant runtime list of MCP servers** available in a session. It is derived directly from the `mcpServers` array in the tenant's application config — there is no separate registry file or database table beyond the config itself.

When a session starts, the platform resolves the active registry from the tenant's current config and:
1. Activates all `always-on` servers immediately
2. Makes `opt-in` servers available in the tool selection panel (but not active)
3. Injects descriptions for active servers into the system prompt

This document covers the registry model, how host teams populate it, the relationship to the MCP Repository complementary service, and how the registry interacts with the MCP Resources Service.

---

### Access tiers

| Tier | Behaviour |
|------|-----------|
| **Always-on** | Active in every session; description injected into system prompt automatically; user cannot disable |
| **Opt-in** | Off by default; user activates per session via tool selection panel; description injected only when active; does not persist across sessions |

Use `always-on` for servers that are foundational to the assistant's usefulness (e.g. the host application's primary data API). Use `opt-in` for servers that are situationally useful but not needed in every session (e.g. a warehouse query tool, an external analytics service).

---

### Registry schema

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

Full field reference is in [02-host-config.md — mcpServers](./02-host-config.md).

---

### Tool description quality

The `description` field is **the most important field in the registry**. It is injected directly into the model's system prompt and directly influences whether the model invokes the correct tool for a given user query.

**Good description (written for the model):**
> Provides access to Acme Corp's data governance platform. Use this tool to look up data domains, entities, quality metrics, data ownership records, and policy information. Use when the user asks about data assets, governance status, quality issues, owners, or compliance.

**Poor description (written for the user):**
> Governance Platform MCP server.

Application Admins should review and iterate on tool descriptions based on improvement signals. Poor tool descriptions are one of the most common causes of the model choosing the wrong tool.

---

### Adding a new MCP server to the registry

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

### Versioning

Tool registry changes are versioned as part of the overall application config (see [02-host-config.md — Config versioning](./02-host-config.md)):

| Change | Config version increment |
|--------|--------------------------|
| New MCP server added | Minor |
| Existing server description or name updated | Patch |
| Server removed or `enabled` changed to `false` | Minor |
| `authType`, `endpoint`, or `accessTier` changed | Minor |

---

### Relationship to the MCP Repository

The **MCP Repository** is a complementary ecosystem service (see [08-platform-operations.md](./08-platform-operations.md)) that provides a discoverable catalogue of available MCP servers — both from the platform ecosystem and from external contributors.

The relationship to the per-tenant registry is:

```
MCP Repository               Per-tenant registry
(discover & browse)    →     (configure & activate)
```

Host teams use the MCP Repository to find servers that already exist and are ready to integrate. Once a suitable server is found, its details (endpoint, suggested description, auth type) are used to populate the `mcpServers` entry in the application config.

The MCP Repository is a read-only browsing surface at config time — it is not invoked at session runtime. The per-tenant registry (derived from the config) is the authoritative source for what is available in a session.

---

### Relationship to the MCP Resources Service

The **MCP Resources Service** is a complementary ecosystem service that provides centralised skills, static resources, and reusable prompt artefacts for use across the MCP ecosystem (see [08-platform-operations.md](./08-platform-operations.md)).

Host applications may register the MCP Resources Service as an MCP server in their tenant registry (typically as an `opt-in` server). When registered and activated in a session:
- The model can invoke the MCP Resources Service to retrieve platform-standard skills, guidance documents, and reusable prompt patterns
- Resources returned appear as MCP tool results in the conversation thread with the standard tool call disclosure card
- Resources are added to the session artefact tray for download

The MCP Resources Service endpoint is published in the MCP Repository.

---

### System prompt injection

When a server is active in a session (always-on or opt-in enabled), its `description` is injected into the system prompt at session start. This informs the model of the server's purpose and when to invoke it.

Always-on server descriptions are always injected. Opt-in server descriptions are injected only when the user has enabled the server for the session. This keeps the system prompt lean when opt-in tools are not in use.

Combined description injection is included in the prompt cache — the cache hit rate metric accounts for the combined length of all active tool descriptions.

---

## Memory and recall

### Overview

Memory and recall governs how the assistant retains standing context across sessions and how that context is scoped to the right users. Two memory controls work together:

| Control | Purpose | Scope |
|---------|---------|-------|
| **Personal memory** | Standing context about the individual user — role, focus areas, preferences, and corrections | That user only |
| **Application context** | Standing context about the organisation/application — terminology, structure, governance decisions, standing guidance | All users within the same tenant |

A third control — **recall scope** — determines who a user can share a conversation with: only users within the same tenant.

All three controls are **transparent** — users always see exactly what context the assistant is working with. Memory is never injected silently (P1 — transparency first).

---

### Personal memory

#### Purpose

Personal memory lets users tell the assistant things that are true about them specifically, so they don't have to repeat context at the start of every conversation. Examples:

- *"I am the owner of the Finance domain"*
- *"I primarily work with Customer and Transaction data"*
- *"When I ask for a quality summary, scope it to Gold-tier only"*
- *"In our team, 'account' means a customer record, not a financial account"*

#### Management UI

Personal memory is managed on the **My Memory** tab within the assistant's profile settings area (accessible from within the `<ai-chat>` component).

| Section | Contents |
|---------|---------|
| **Memory toggle** | On/Off switch for personal memory injection. Default: **off** until the user explicitly enables it. Toggle state is always visible. |
| **Memory items list** | All memory items (Active and Inactive) — title, category tag, source (Manual / Extracted), date added, token count, status badge, edit and delete controls. |
| **Search / filter** | Full-text search across item titles and content; filter by category and status. |
| **Add item** | Free-text input — user types the memory item in plain language, optionally assigns a category, confirms, and it is saved as Active. |
| **Extract from conversation** | User-initiated only. See [Extraction process](#extraction-process) below. |
| **Token budget indicator** | Shows current usage against the tenant-configured token budget (e.g. `640 / 2,000 tokens`) with a colour-coded bar. |
| **Clear all** | Archives all items (moves to Inactive) after confirmation. Does not permanently delete — archived items remain in the audit trail. |

#### Personal memory item categories

Host applications configure memory categories in `memory.personalMemory.categories` in the application config. Default categories:

| Category | Examples |
|----------|---------|
| **Role** | Job title, domain ownership, team membership |
| **Preference** | Preferred response style, scope defaults, output format preferences |
| **Correction** | Organisation-specific term overrides; corrections to the assistant's default assumptions |
| **Context** | Current focus areas, active projects, known constraints |

#### Personal memory item lifecycle

```
Active → Inactive (budget exceeded or user toggle) → Archived (deleted by user)
```

| Status | Injected? | Editable? | Visible in UI? |
|--------|-----------|-----------|---------------|
| **Active** | Yes | Yes | Yes |
| **Inactive** | No | Yes — user can reactivate | Yes (greyed out) |
| **Archived** | No | No | No (retained in audit trail only) |

Items are never permanently deleted — the record is retained with `status = archived` for the audit trail.

#### Extraction process

"Extract from conversation" is a structured, user-initiated workflow — nothing is extracted automatically.

1. User opens the conversation picker (full-text search across their conversation history)
2. User selects a past conversation
3. A dedicated **fast-tier model** call analyses the selected conversation using a structured extraction prompt — it identifies discrete, self-contained statements of user context worth persisting (role declarations, expressed preferences, corrections made, constraints stated)
4. The assistant presents a **review panel** showing each proposed item with: suggested text, suggested category, estimated token cost, and source conversation reference
5. User accepts, edits, or discards each proposal **individually** — there is no bulk accept
6. Accepted items are saved as Active; discarded proposals are not stored

The extraction call is a separate API call — it does not affect the conversation context window. The extraction prompt explicitly excludes host application object references (stale risk) and system prompt override attempts before they reach the review panel.

#### Token budget

Personal memory is injected into the system prompt as a labelled `[Your context]` block. The budget is configurable per tenant via `memory.personalMemory.tokenBudget` (default: 2,000 tokens). When the budget is exceeded, the user is warned and the oldest items are marked Inactive — the user decides which items to reactivate or remove.

#### What personal memory cannot contain

- Host application object IDs or live data references — these may become stale. The assistant resolves live data via MCP at query time.
- Other users' personal information
- Instructions that would override the platform system prompt — the platform prompt takes precedence

#### Injection behaviour

When personal memory is enabled, the `[Your context]` block is injected into the system prompt at session start. It appears in the conversation header as a collapsed indicator: **"Your context active [2 items · 640 tokens] ↗"** — click to expand and inspect the full content.

---

### Application context

#### Purpose

Application context gives the assistant organisation-wide context that applies to all users and sessions within the tenant. It provides ground truth for terminology, structure, and standing decisions that the assistant would otherwise have to infer or ask about. Examples:

- *"Our organisation uses 'account' to refer to customer records. 'Account' does not mean a financial account."*
- *"The Customer domain is the master domain. All other domains reference it for shared definitions."*
- *"Data owner assignments are reviewed quarterly — an assignment may be up to 90 days out of date."*
- *"The Finance domain is under an active regulatory review. Flag any Finance domain queries before providing assessments."*

#### Management UI

Application context is managed in the **Tenant Admin area** (accessible to users with the Application Admin role). 

| Section | Contents |
|---------|---------|
| **Context items list** | All items with title, category, approval status, effective date, and approver |
| **Add item** | Application Admin proposes a new item with a title, category, and content |
| **Approval workflow** | If `memory.applicationContext.approvalRequired: true` (default), new items require two-step approval: Propose → Approve. Proposer and approver must be different users. |
| **Edit item** | Any edit to an approved item creates a new draft — the existing approved version continues to be injected until the edit is approved |
| **Retire item** | Removes an item from injection without deleting it |
| **Version history** | Full version history per item: original text, all edits, approval actions, effective dates |
| **Token budget indicator** | Current usage against the tenant-configured budget |

#### Categories

Host applications configure application context categories in `memory.applicationContext.categories` (default):

| Category | Examples |
|----------|---------|
| **Terminology** | Organisation-specific term definitions; overrides to common terms |
| **Structure** | Organisational hierarchy, domain ownership, team structure |
| **Policy** | Standing governance decisions, active reviews, classification conventions |
| **Domain context** | Known data quality issues, known gaps, recency caveats |

#### Token budget

Application context is injected as a labelled `[Application context]` block in the system prompt. The budget is configurable per tenant via `memory.applicationContext.tokenBudget` (default: 4,000 tokens). Items are injected in category order and by effective date (newest first) within category.

#### Visibility for all users

Application context is visible (read-only) to all authenticated users within the tenant from the conversation header indicator. Users can see exactly what organisation-wide context the assistant is working with in any session. They cannot edit it.

#### Approval pipeline

```
Draft → Proposed → Approved (active) → Retired
```

| Transition | Who can trigger | Effect |
|-----------|----------------|--------|
| Draft → Proposed | Application Admin | Item visible in admin UI; not yet injected |
| Proposed → Approved | Application Admin (different user from proposer) | Item becomes active; injected into all subsequent sessions |
| Approved → Retired | Application Admin | Item removed from injection; retained in audit trail |
| Approved → Draft (edit) | Application Admin | New draft created; approved version continues injecting until new draft approved |

When `memory.applicationContext.approvalRequired: false`, the two-step approval is replaced by a single-step publish action (any Application Admin can publish immediately).

---

### Combined injection — conversation header

In every conversation, the header shows the combined active memory state:

```
┌──────────────────────────────────────────────────────┐
│  🧠 Your context       [2 items · 640 tokens] ↗      │
│  🏢 Application context [4 items · 1,240 tokens] ↗   │
└──────────────────────────────────────────────────────┘
```

Both indicators are collapsed by default. Clicking either opens a two-level panel:

**Level 1 — Compact list** (default on open)
Each active memory item shown as a single line: category tag + title + token count.

**Level 2 — Full text** (expand per item)
Click any item row to expand to its full content — exactly as injected.

A user may **disable personal memory for a single session** by clicking the indicator and toggling off before sending their first message. This does not affect the global personal memory setting.

Application context cannot be disabled by individual users.

---

### Token budget summary

| Memory type | Default budget | Injected as |
|------------|---------------|-------------|
| Personal memory | 2,000 tokens | `[Your context]` block in system prompt |
| Application context | 4,000 tokens | `[Application context]` block in system prompt |
| Combined maximum | 6,000 tokens | Injected before the first turn; cached on subsequent turns |

The combined 6,000-token memory budget is included in the prompt cache — the cache hit rate metric accounts for it.

---

### Recall and access scope

#### Tenant boundary

A user can only share a conversation with — and recall shared context alongside — other users **within the same tenant**. This is a hard boundary enforced at the data layer.

| Boundary | Behaviour |
|----------|-----------|
| Conversation sharing | Invitation search returns users within the authenticated user's tenant only. Cross-tenant results are excluded. |
| Application context | The `[Application context]` block is scoped to the authenticated user's tenant. Context from one tenant is never injected into another tenant's sessions. |
| Personal memory | Personal memory items are owned by `user_id` and are never visible to other users. |

#### Why this boundary exists

Conversation threads accumulate context about an organisation's operations, decisions, and data. Permitting cross-tenant access to this context would violate data confidentiality. The tenant boundary is a design constraint, not a configurable option.

---

### Audit trail

| Element | Where stored |
|---------|-------------|
| Personal memory items | `assistant.user_memory` — `tenant_id`, `user_id`, `content`, `category`, `source`, `status`, timestamps |
| Application context items | `assistant.app_context` — `tenant_id`, `title`, `category`, `content`, `status`, `proposed_by`, `approved_by`, `effective_from`, `retired_at`; version history in `assistant.app_context_versions` |
| Memory injected per session | `assistant.turns` — the resolved system prompt including both memory blocks is stored on the first turn of every conversation |

Memory items themselves are retained indefinitely (they are governance configuration, not conversation data). Only their injection into turns is subject to the tenant's configured retention period.

---

### What memory cannot replace

Memory provides standing context. It does not replace live data. The assistant always resolves live object data, status, and metrics via host MCP servers at query time. Memory items that describe application objects are advisory framing, not authoritative data.

**Correct use:** *"The Finance domain is under an active regulatory review — flag Finance queries."* This is framing that helps the assistant contextualise queries.

**Incorrect use (rejected by validation):** *"The Finance domain has 42 entities and Jane Smith is the owner."* This would become stale. The assistant queries the host MCP server for live entity data.

---

## Shared conversations

### Overview

Any conversation may be shared with other authenticated users **within the same tenant**. Sharing is **explicit and controlled** — there are no open links, no public access, and no anonymous participants. Every person in a shared conversation must hold an active account in the host application and be a member of the same tenant. The tenant boundary and its rationale are specified in [Recall and access scope](#recall-and-access-scope) above.

Shared conversations require the `features.sharedConversations: true` feature flag in the tenant config.

---

### Invitation model

The conversation owner invites participants by searching for their name or email address **within their tenant's user directory**. Cross-tenant sharing is not supported — the search is hard-scoped to the authenticated user's tenant.

| Rule | Specification |
|------|--------------|
| Search scope | Users within the same tenant only — it is not possible to invite a user from another tenant or an external email address |
| Shareable URLs | Not supported — invitations are directed to a specific named user |
| Maximum participants | Configured by host in `conversations.maxParticipants` (default: 10) |
| Invitation delivery | In-platform notification; optionally email per the recipient's notification preferences |
| Invitation content | Conversation title, inviting user's name, accept/decline action |
| Accept | Adds the conversation to the participant's history panel under the **Shared With Me** group |
| Decline | Removes the invitation; no notification to the inviter |

---

### Participant model

All participants are **equal**. There are no roles, no elevated permissions, and no designated owner after the conversation has been shared. Any participant may:

- Invite additional users within the same tenant to the conversation
- Remove any other participant
- Leave the conversation themselves
- Archive or rename the conversation

#### The last-participant constraint

**A conversation must always have at least one participant.** If a participant is the **last person remaining**, they cannot leave or remove themselves until at least one other user has accepted an invitation.

The interface handles this by:
- Disabling the **Leave** and **Self-remove** controls when the user is the last participant
- Surfacing a tooltip: *"You are the only person in this conversation. Invite another participant before leaving."*

If the last remaining participant's account is **deactivated by a host application administrator**, the conversation is locked to **read-only** and flagged for administrative review.

---

### Conversation history visibility

When a participant accepts an invitation, they see the **full conversation history from the beginning** — not only from the point they were invited. This is intentional: the value of a shared conversation is the full context.

#### Acceptance disclaimer

Before a user can enter a shared conversation, they must acknowledge a **full-page disclaimer**:

> **Before you join this conversation**
>
> You have been invited to join *"[Conversation title]"* by [Inviter name].
>
> By accepting, you will have access to the **complete conversation history** from the beginning — including all messages sent before you were invited.
>
> Everything you send will be stored as part of the audit trail for this conversation.
>
> [**Accept and open conversation**] &nbsp;&nbsp; [Decline]

The disclaimer is shown every time a user accepts an invitation — it is not a one-time acknowledgement. The user cannot enter the conversation without explicitly clicking **Accept and open conversation**.

---

### Message attribution

In a shared conversation thread, each message bubble carries the **author's name and avatar**.

| Message source | Display |
|---------------|---------|
| Active user's messages | Right-aligned, muted bubble |
| Other participants' messages | Left-aligned, with a distinct colour per participant (generated from the host's primary brand colour) |
| Model responses | Left-aligned as the assistant — never attributed to a user |

The model label (and, on hover, the name of the user who submitted the preceding message) is visible on each assistant response.

---

### `@`-binding in shared conversations

Each user's `@`-binding typeahead is **scoped to their own permissions** (as enforced by the host's `searchEndpoint`). A participant cannot bind to an object they cannot access in the host application.

If a user submits a message containing a binding to an object that another participant **cannot access**:
- The restricted participant sees the binding chip labelled **"[Restricted object]"**
- They do not see the resolved context that was injected into the model prompt
- The tool call disclosure for any resulting MCP call shows `[Restricted — insufficient permissions]` on the result summary for that participant

This preserves the integrity of each user's permission boundary within the shared thread.

---

### Communication style in shared sessions

Each user's communication style and verbosity settings (from their JWT claims) apply **to the turns they submit**. A response generated for a `technical` user may sit alongside a response generated for a `business` user within the same thread.

The style label is visible on each assistant response — participants can always see the context in which a response was calibrated.

---

### Model and tool configuration in shared sessions

The active model and any opt-in MCP tools **apply to the session as a whole** — they are not per-user settings within a shared conversation. The user who submits a message determines the model and tool context for that turn. Other participants see the model label on each assistant response.

---

### Sharing controls (input area)

The **share icon** in the input area opens the participant management panel. From this panel, any participant may:

| Action | Behaviour |
|--------|----------|
| Search for users | Search within the authenticated user's tenant by name or email — cross-tenant results are excluded |
| Invite a user | Sends in-platform notification to the named user |
| View participants | See all current participants with name, avatar, and join date |
| Remove a participant | Removes their access; their prior messages remain in the thread |
| Leave the conversation | Removes self; only available when at least one other participant remains |

---

### Notifications

| Event | Notification |
|-------|-------------|
| New invitation received | In-platform notification with conversation title, inviter name, accept/decline |
| New message in shared conversation (not actively viewing) | In-platform notification + badge count on conversation in history panel |
| Email notifications | Per recipient's notification preferences; **off by default** for shared conversation activity |

---

### Audit trail for shared conversations

The audit trail records the `user_id` of the message author on every turn. In shared conversations this records the specific participant who submitted each turn.

| Recorded element | Table | Notes |
|-----------------|-------|-------|
| Message author | `assistant.turns.user_id` | FK to platform user record; records the submitting participant |
| Participant list | `assistant.conversation_participants` | `user_id`, `invited_by`, `invited_at`, `accepted_at`, `departed_at` |
| Invitation events | `assistant.conversation_participants` | Full invitation lifecycle per participant |

There are no role fields — all participants are equal. The audit record reflects actions taken, not role assignments.

---

### Leaving and removing participants

| Action | Who can do it | Effect |
|--------|--------------|--------|
| Leave | Any participant (subject to last-participant constraint) | Conversation removed from leaver's history panel; their prior messages remain in thread |
| Remove another participant | Any participant | Removed user loses access; their prior messages remain; they may be reinvited |
| Reinvite a departed participant | Any remaining participant | Same invitation flow as initial invite |

Departed or removed participants' messages remain **visible to all remaining participants** and in the **full audit trail**. No message is deleted when a participant leaves.
