# 15 — Memory and Recall

## Overview

Memory and recall governs how Andi retains standing context across sessions and how that context is scoped to the right users. Three controls work together:

| Control | Purpose | Scope |
|---------|---------|-------|
| **Personal memory** | Standing context about the individual user — role, focus areas, preferences, org-specific corrections | That user only |
| **Institutional memory** | Standing context about the organisation — terminology, structure, governance decisions | All users within the same organisation/tenant (read-only) |
| **Recall scope** | Who a user can share a conversation with and recall shared context from | Restricted to users within the same organisation/tenant |

All three controls are **transparent** — users always see exactly what context Andi is working with, and memory is never injected silently (P1 — governance-first transparency).

---

## Personal memory

### Purpose

Personal memory lets users tell Andi things that are true about them specifically, so they don't have to repeat context at the start of every conversation. Examples:

- *"I am the data owner for the Finance domain"*
- *"I primarily work with Customer and Transaction entities"*
- *"When I ask for a quality summary, I want it scoped to Gold-tier entities only"*
- *"In our Finance team, 'account' means a customer record, not a financial account"*

### Management UI — My Memory

Personal memory is managed on the **My Memory** tab of the DDA profile settings page.

| Section | Contents |
|---------|---------|
| **Memory toggle** | On/Off switch for personal memory injection. When off, Andi starts each session with no personal context. Toggle state is always visible. Default: **off** until the user explicitly enables it. |
| **Memory items list** | All memory items (Active and Inactive) — title, category tag, source (Manual / Extracted), date added, token count, status badge, edit and delete controls. Full text shown inline on expand; collapsed to title by default. |
| **Search / filter** | Full-text search across item titles and content; filter by category (Role / Preference / Correction / Context) and status (Active / Inactive). Allows users to locate and manage items as the list grows. |
| **Add item** | Free-text input — user types the memory item in plain language, optionally assigns a category, confirms, and it is saved as Active. |
| **Extract from conversation** | User-initiated only. See [Extraction process](#extraction-process) below. |
| **Token budget indicator** | Shows current usage against the 2,000-token personal memory budget (e.g. `640 / 2,000 tokens`) with a colour-coded bar (green / amber / red). |
| **Clear all** | Archives all personal memory items (moves to Inactive) after confirmation. Does not permanently delete — archived items remain in the audit trail. |

### Personal memory item categories

Personal memory items are tagged with a category on creation to aid management and filtering:

| Category | Examples |
|----------|---------|
| **Role** | Job title, domain ownership, team membership |
| **Preference** | Preferred response style, scope defaults, output format preferences |
| **Correction** | Organisation-specific term overrides; corrections to Andi's default assumptions |
| **Context** | Current focus areas, active projects, known constraints |

### Personal memory item lifecycle

Each item carries a status that determines whether it is injected into sessions:

```
Active → Inactive (budget exceeded or user toggle) → Archived (deleted by user)
```

| Status | Injected? | Editable? | Visible in UI? |
|--------|-----------|-----------|---------------|
| **Active** | Yes | Yes | Yes |
| **Inactive** | No | Yes — user can reactivate | Yes (greyed out) |
| **Archived** | No | No | No (retained in audit trail only) |

Items are never permanently deleted — the `assistant.user_memory` record is retained with `status = archived` for the audit trail. The UI shows only Active and Inactive items.

### Extraction process

"Extract from conversation" is a structured, user-initiated workflow — nothing is extracted automatically.

1. User opens the conversation picker (full-text search across their conversation history)
2. User selects a past conversation
3. A dedicated **Claude Haiku 4** call analyses the selected conversation using a structured extraction prompt — it identifies discrete, self-contained statements of user context worth persisting (role declarations, expressed preferences, corrections made, constraints stated)
4. Andi presents a **review panel** showing each proposed item with: suggested text, suggested category, estimated token cost, and source conversation reference
5. User accepts, edits, or discards each proposal **individually** — there is no bulk accept
6. Accepted items are saved as Active; discarded proposals are not stored

The extraction call is a separate API call from the session — it does not affect the conversation context window. The structured prompt explicitly excludes DDA entity references (stale risk) and system prompt override attempts before they reach the review panel.

### Token budget

Personal memory is injected into the system prompt as a labelled `[Your context]` block. The budget is **2,000 tokens maximum**. When the budget is exceeded, the user is warned in the management UI and the oldest items are marked inactive (not deleted) — the user decides which items to reactivate or remove.

### What personal memory cannot contain

- `@`-bindings or Display IDs referencing DDA entities — these may become stale as entity records change. Andi resolves live entity context via the DDA MCP server, not from memory.
- Other users' personal information
- Instructions that would override the DDA system prompt (e.g. *"Always answer as if you are a general assistant"*) — the system prompt takes precedence and Andi will note any conflict

### Injection behaviour

When personal memory is enabled, the `[Your context]` block is injected into the system prompt at session start — before the first user message. It appears in the conversation header as a collapsed indicator: **"Your context active [2 items · 640 tokens] ↗"** — click to expand and inspect the full content.

The injected content is recorded in `assistant.turns` alongside the resolved prompt — a reviewer can see exactly what personal context Andi had at the start of any session.

---

## Institutional memory

### Scope

Institutional memory is **scoped to the authenticated user's organisation/tenant**. Memory items defined by one tenant's CDAiO are never visible to or injected into sessions belonging to another tenant. The `org_id` column on `assistant.org_memory` enforces this at the data layer, consistent with the tenant-isolation model introduced in the survey module.

### Purpose

Institutional memory gives Andi organisation-wide context that applies to all users and sessions within the organisation. It provides the ground truth for terminology, structure, and standing governance decisions that Andi would otherwise have to infer or ask about. Examples:

- *"The organisation uses 'account' to refer to customer records. 'Account' does not mean a financial account."*
- *"The Customer domain is the master domain. All other domains reference it for shared entity definitions."*
- *"Data owner assignments are reviewed quarterly. An assignment may be up to 90 days out of date."*
- *"The Finance domain is under an active regulatory review. Flag any Finance domain queries to the user before providing governance assessments."*

### Management UI — Institutional Memory

Institutional memory is managed in the **DDA Admin area** under **Andi > Institutional Memory**. This interface is accessible to users with the CDAiO or Admin role only.

| Section | Contents |
|---------|---------|
| **Memory items list** | All memory items with title, category, approval status, effective date, and the user who approved it |
| **Add item** | Free-text input — CDAiO proposes a new memory item with a title, category, and content |
| **Approval workflow** | New items enter a lightweight two-step flow: Propose → Approve. The proposer and approver must be different users. An item is only injected into sessions after it has been approved. |
| **Edit item** | Any edit to an approved item creates a new draft — the existing approved version continues to be injected until the edit is approved |
| **Retire item** | Removes an item from injection without deleting it. Retired items are preserved in the audit trail. |
| **Version history** | Every item carries a full version history: original text, all edits, approval actions, effective dates, and retirement date if applicable |
| **Token budget indicator** | Shows current usage against the 4,000-token institutional memory budget |

### Categories

Memory items are classified by category to aid management and triage:

| Category | Examples |
|----------|---------|
| **Terminology** | Organisation-specific term definitions; overrides to common terms |
| **Structure** | Organisational hierarchy, domain ownership, team structure |
| **Governance** | Standing decisions, active reviews, classification conventions |
| **Data context** | Known data quality issues, known gaps, recency caveats |

### Token budget

Institutional memory is injected as a labelled `[Organisation context]` block in the system prompt. The budget is **4,000 tokens maximum**. Items are injected in category order (Governance → Terminology → Structure → Data context) and by effective date (newest first) within category. Items that would exceed the budget are queued as inactive and flagged for admin review.

### Visibility for all users

Institutional memory is visible (read-only) to all authenticated DDA users at **DDA profile settings > Organisation context** or from the conversation header indicator. Users can see exactly what organisation-wide context Andi is working with in any session. They cannot edit it.

### Injection behaviour

The `[Organisation context]` block is injected into every session regardless of the user's personal memory settings. It appears in the conversation header alongside the personal memory indicator: **"Organisation context active [4 items · 1,240 tokens] ↗"**

The injected content is recorded in every turn record — part of the governance audit trail.

### Approval pipeline

Institutional memory changes follow a lightweight version of the DDA improvement pipeline:

```
Draft → Proposed → Approved (active) → Retired
```

| Transition | Who can trigger | Effect |
|-----------|----------------|--------|
| Draft → Proposed | CDAiO, Admin | Item visible in admin UI; not yet injected |
| Proposed → Approved | CDAiO, Admin (different user from proposer) | Item becomes active; injected into all subsequent sessions |
| Approved → Retired | CDAiO, Admin | Item removed from injection; retained in audit trail |
| Approved → Draft (edit) | CDAiO, Admin | New draft created; approved version continues to be injected until new draft is approved |

---

## Combined injection — conversation header

In every conversation, the header shows the combined active memory state:

```
┌──────────────────────────────────────────────────────┐
│  🧠 Your context  [2 items · 640 tokens] ↗           │
│  🏢 Org context   [4 items · 1,240 tokens] ↗         │
└──────────────────────────────────────────────────────┘
```

Both indicators are collapsed by default. Clicking either opens a **two-level panel**:

**Level 1 — Compact list** (default on open)
Each active memory item shown as a single line: category tag + title + token count. Gives a fast overview without requiring the user to read every item.

```
  [Role]        Data owner for Finance domain           · 12 tok
  [Correction]  'account' means customer record here    · 18 tok
  [Preference]  Quality summaries scoped to Gold tier   · 15 tok
```

**Level 2 — Full text** (expand per item)
Click any item row to expand to its full content — exactly as injected into the system prompt.

This progressive disclosure approach keeps the panel scannable even when the token budget is near capacity.

A user may **disable personal memory for a single session** by clicking the indicator and toggling off before sending their first message. This does not affect the global personal memory setting — it is a session-only override.

Institutional memory cannot be disabled by individual users.

---

## Token budget summary

| Memory type | Budget | Injected as |
|------------|--------|-------------|
| Personal memory | 2,000 tokens | `[Your context]` block in system prompt |
| Institutional memory | 4,000 tokens | `[Organisation context]` block in system prompt |
| Combined maximum | 6,000 tokens | Injected before the first turn; cached on subsequent turns |

The combined 6,000-token memory budget is included in the prompt cache (see [06-model-configuration.md](./06-model-configuration.md)) — the cache hit rate metric accounts for it.

---

## Recall and access scope

### Organisation/tenant boundary

A user can only share a conversation with — and recall shared context alongside — other users **within their own organisation/tenant**. This is a hard boundary enforced at the data layer, consistent with the tenant-isolation model introduced in the survey module.

| Boundary | Behaviour |
|----------|-----------|
| Conversation sharing | Invitation search returns users within the authenticated user's `org_id` only. Cross-tenant results are excluded. |
| Institutional memory | `[Organisation context]` is scoped to the authenticated user's `org_id`. Memory items from one tenant are never injected into another tenant's sessions. |
| Personal memory | Personal memory items are owned by `user_id` and are never visible to other users, regardless of org membership. |

### Why this boundary exists

Conversation threads accumulate governance-sensitive data about an organisation's data estate: entity quality scores, classification decisions, active regulatory reviews, domain ownership. Permitting cross-tenant access to this context would violate data confidentiality and undermine the governance integrity of the audit trail. The org/tenant boundary is therefore a design constraint, not a configurable option.

### Admin view

Users with the CDAiO or Admin role can see (read-only) the full list of users in their organisation's tenant at **DDA Admin > Users**. This is the population that can be invited to shared conversations. Admins cannot modify this boundary or grant cross-tenant access.

---

## Audit trail

| Element | Where stored |
|---------|-------------|
| Personal memory items | `assistant.user_memory` — `user_id`, `content`, `category`, `source`, `status` (`active` / `inactive` / `archived`), `created_at`, `updated_at` |
| Institutional memory items | `assistant.org_memory` — `org_id`, `title`, `category`, `content`, `status`, `proposed_by`, `approved_by`, `effective_from`, `retired_at`, version history in `assistant.org_memory_versions` |
| Memory injected per session | `assistant.turns` — the resolved system prompt including both memory blocks is stored on the first turn of every conversation |

Retention aligns with the 3-year conversation record retention policy. Memory items themselves are retained indefinitely (they are governance configuration, not conversation data) — only their injection into turns is subject to the 3-year retention.

---

## What memory cannot replace

Memory provides standing context. It does not replace live data. Andi always resolves entity data, quality scores, ownership, and governance status via the DDA MCP server at query time — memory items that describe DDA entities are advisory framing, not authoritative data.

Example of correct use: *"The Finance domain is under an active regulatory review — flag Finance domain queries."* This is framing that helps Andi contextualise queries.

Example of incorrect use (rejected by the validation UI): *"The Finance domain has 42 entities and Jane Smith is the owner."* This would become stale. Andi queries the MCP server for live entity data.
