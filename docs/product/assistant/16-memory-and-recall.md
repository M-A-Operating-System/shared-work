# 15 — Memory and Recall

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---


## Overview

Memory and recall governs how the assistant retains standing context across sessions and how that context is scoped to the right users. Two memory controls work together:

| Control | Purpose | Scope |
|---------|---------|-------|
| **Personal memory** | Standing context about the individual user — role, focus areas, preferences, and corrections | That user only |
| **Application context** | Standing context about the organisation/application — terminology, structure, governance decisions, standing guidance | All users within the same tenant |

A third control — **recall scope** — determines who a user can share a conversation with: only users within the same tenant.

All three controls are **transparent** — users always see exactly what context the assistant is working with. Memory is never injected silently (P1 — transparency first).

---

## Personal memory

### Purpose

Personal memory lets users tell the assistant things that are true about them specifically, so they don't have to repeat context at the start of every conversation. Examples:

- *"I am the owner of the Finance domain"*
- *"I primarily work with Customer and Transaction data"*
- *"When I ask for a quality summary, scope it to Gold-tier only"*
- *"In our team, 'account' means a customer record, not a financial account"*

### Management UI

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

### Personal memory item categories

Host applications configure memory categories in `memory.personalMemory.categories` in the application config. Default categories:

| Category | Examples |
|----------|---------|
| **Role** | Job title, domain ownership, team membership |
| **Preference** | Preferred response style, scope defaults, output format preferences |
| **Correction** | Organisation-specific term overrides; corrections to the assistant's default assumptions |
| **Context** | Current focus areas, active projects, known constraints |

### Personal memory item lifecycle

```
Active → Inactive (budget exceeded or user toggle) → Archived (deleted by user)
```

| Status | Injected? | Editable? | Visible in UI? |
|--------|-----------|-----------|---------------|
| **Active** | Yes | Yes | Yes |
| **Inactive** | No | Yes — user can reactivate | Yes (greyed out) |
| **Archived** | No | No | No (retained in audit trail only) |

Items are never permanently deleted — the record is retained with `status = archived` for the audit trail.

### Extraction process

"Extract from conversation" is a structured, user-initiated workflow — nothing is extracted automatically.

1. User opens the conversation picker (full-text search across their conversation history)
2. User selects a past conversation
3. A dedicated **fast-tier model** call analyses the selected conversation using a structured extraction prompt — it identifies discrete, self-contained statements of user context worth persisting (role declarations, expressed preferences, corrections made, constraints stated)
4. The assistant presents a **review panel** showing each proposed item with: suggested text, suggested category, estimated token cost, and source conversation reference
5. User accepts, edits, or discards each proposal **individually** — there is no bulk accept
6. Accepted items are saved as Active; discarded proposals are not stored

The extraction call is a separate API call — it does not affect the conversation context window. The extraction prompt explicitly excludes host application object references (stale risk) and system prompt override attempts before they reach the review panel.

### Token budget

Personal memory is injected into the system prompt as a labelled `[Your context]` block. The budget is configurable per tenant via `memory.personalMemory.tokenBudget` (default: 2,000 tokens). When the budget is exceeded, the user is warned and the oldest items are marked Inactive — the user decides which items to reactivate or remove.

### What personal memory cannot contain

- Host application object IDs or live data references — these may become stale. The assistant resolves live data via MCP at query time.
- Other users' personal information
- Instructions that would override the platform system prompt — the platform prompt takes precedence

### Injection behaviour

When personal memory is enabled, the `[Your context]` block is injected into the system prompt at session start. It appears in the conversation header as a collapsed indicator: **"Your context active [2 items · 640 tokens] ↗"** — click to expand and inspect the full content.

---

## Application context

### Purpose

Application context gives the assistant organisation-wide context that applies to all users and sessions within the tenant. It provides ground truth for terminology, structure, and standing decisions that the assistant would otherwise have to infer or ask about. Examples:

- *"Our organisation uses 'account' to refer to customer records. 'Account' does not mean a financial account."*
- *"The Customer domain is the master domain. All other domains reference it for shared definitions."*
- *"Data owner assignments are reviewed quarterly — an assignment may be up to 90 days out of date."*
- *"The Finance domain is under an active regulatory review. Flag any Finance domain queries before providing assessments."*

### Management UI

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

### Categories

Host applications configure application context categories in `memory.applicationContext.categories` (default):

| Category | Examples |
|----------|---------|
| **Terminology** | Organisation-specific term definitions; overrides to common terms |
| **Structure** | Organisational hierarchy, domain ownership, team structure |
| **Policy** | Standing governance decisions, active reviews, classification conventions |
| **Domain context** | Known data quality issues, known gaps, recency caveats |

### Token budget

Application context is injected as a labelled `[Application context]` block in the system prompt. The budget is configurable per tenant via `memory.applicationContext.tokenBudget` (default: 4,000 tokens). Items are injected in category order and by effective date (newest first) within category.

### Visibility for all users

Application context is visible (read-only) to all authenticated users within the tenant from the conversation header indicator. Users can see exactly what organisation-wide context the assistant is working with in any session. They cannot edit it.

### Approval pipeline

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

## Combined injection — conversation header

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

## Token budget summary

| Memory type | Default budget | Injected as |
|------------|---------------|-------------|
| Personal memory | 2,000 tokens | `[Your context]` block in system prompt |
| Application context | 4,000 tokens | `[Application context]` block in system prompt |
| Combined maximum | 6,000 tokens | Injected before the first turn; cached on subsequent turns |

The combined 6,000-token memory budget is included in the prompt cache — the cache hit rate metric accounts for it.

---

## Recall and access scope

### Tenant boundary

A user can only share a conversation with — and recall shared context alongside — other users **within the same tenant**. This is a hard boundary enforced at the data layer.

| Boundary | Behaviour |
|----------|-----------|
| Conversation sharing | Invitation search returns users within the authenticated user's tenant only. Cross-tenant results are excluded. |
| Application context | The `[Application context]` block is scoped to the authenticated user's tenant. Context from one tenant is never injected into another tenant's sessions. |
| Personal memory | Personal memory items are owned by `user_id` and are never visible to other users. |

### Why this boundary exists

Conversation threads accumulate context about an organisation's operations, decisions, and data. Permitting cross-tenant access to this context would violate data confidentiality. The tenant boundary is a design constraint, not a configurable option.

---

## Audit trail

| Element | Where stored |
|---------|-------------|
| Personal memory items | `assistant.user_memory` — `tenant_id`, `user_id`, `content`, `category`, `source`, `status`, timestamps |
| Application context items | `assistant.app_context` — `tenant_id`, `title`, `category`, `content`, `status`, `proposed_by`, `approved_by`, `effective_from`, `retired_at`; version history in `assistant.app_context_versions` |
| Memory injected per session | `assistant.turns` — the resolved system prompt including both memory blocks is stored on the first turn of every conversation |

Memory items themselves are retained indefinitely (they are governance configuration, not conversation data). Only their injection into turns is subject to the tenant's configured retention period.

---

## What memory cannot replace

Memory provides standing context. It does not replace live data. The assistant always resolves live object data, status, and metrics via host MCP servers at query time. Memory items that describe application objects are advisory framing, not authoritative data.

**Correct use:** *"The Finance domain is under an active regulatory review — flag Finance queries."* This is framing that helps the assistant contextualise queries.

**Incorrect use (rejected by validation):** *"The Finance domain has 42 entities and Jane Smith is the owner."* This would become stale. The assistant queries the host MCP server for live entity data.
