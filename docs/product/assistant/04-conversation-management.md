# 04 — Conversation Management

## Conversation model

Each conversation is a **named, persistent thread** scoped to the authenticated user within their tenant. Key properties:

- Conversations survive browser refresh and are resumable across sessions.
- The history panel lists all past conversations in reverse-chronological order with auto-generated titles derived from the first user message.
- Users may rename, archive, or delete conversations — subject to the tenant's configured retention period (see [11-audit-and-storage.md](./11-audit-and-storage.md)).
- Conversations are **append-only at the turn level**. No turn is ever overwritten or destroyed. Editing creates a new branched thread; the original is preserved in full.

### Conversation states

| State | Description |
|-------|-------------|
| **Active** | Has been interacted with in the last 30 days; appears in the default history view |
| **Pinned** | Permanently anchored to the top of the My Conversations list regardless of recency. Maximum 5 pinned conversations. Useful for recurring reviews or ongoing work threads. |
| **Archived** | Hidden from default history view; accessible via archived filter; retains full content |
| **Deleted** | Removed from user view; physical deletion deferred to retention expiry per tenant retention policy |
| **Shared** | One or more other authenticated users in the same tenant have accepted an invitation; appears under **Shared With Me** group in history panel |
| **Locked (read-only)** | Last remaining participant's account deactivated; flagged for administrative review |

---

## Conversation branching

Users may edit any previously submitted message. Editing creates a **new conversation thread** — not an in-thread branch.

### Branch mechanics

1. User clicks the edit icon on any past user message.
2. An inline edit field opens, pre-populated with the original text. `@`-binding chips are preserved and editable.
3. Submitting the edited message creates a **new conversation thread** that inherits all turns up to and including the edited turn (with the edit applied) and continues independently.
4. The original conversation is **untouched**.
5. Both threads are linked:
   - The new branch carries a header chip: *"Branched from: [title], turn N"*
   - The origin conversation carries a reciprocal reference at the corresponding turn
6. `Escape` cancels the edit without creating a branch.

### Regeneration

Regeneration (resending an unchanged message for a fresh model response) follows the same model: a new thread is created from that turn point. The original response in the parent conversation is untouched.

### Why branching, not in-place editing?

> **Audit completeness (P4):** Every turn is an auditable record. Overwriting turns in place would destroy the original query-response pair. Branching preserves both the original intent and the refined intent as independent, auditable threads. This design holds regardless of the host application domain.

---

## Conversation search

A search field at the top of the history panel searches across all the authenticated user's conversations — personal and shared — within their tenant.

### Search scope

| Field searched | Examples |
|---------------|---------|
| Conversation title | "Finance governance review" |
| User message text | "Compare error rates for `@{Payment Service}`" |
| Assistant response text | "The Payment Service had three error spikes in the last hour" |

### Search behaviour

- Results are returned in **relevance order** with the matching excerpt highlighted.
- Selecting a result opens the conversation **at the matching turn**.
- Accessible via `Cmd/Ctrl + K` from anywhere on the chat surface.
- On mobile, search opens as a **full-screen overlay** with the keyboard raised.
- Search spans both **My Conversations** and **Shared With Me** groups.

---

## Context window management

Silent truncation is not permitted (P1 — transparency first). The user is always informed when context is being condensed.

### Conversation length limit

A conversation may not exceed **100 turns** (configurable per tenant up to the platform maximum via `conversations.maxTurnLimit`). This is an explicit product limit — not a technical one — chosen to keep conversations focused and auditable. At the turn limit, the conversation is closed to new input and the user is prompted to continue in a new thread (see branching above). The full turn history is always retained in the audit trail.

### Token warning — 80%

Before the turn limit is reached, the active context window may fill based on message length and attachment size. When a conversation reaches **80% of the model's context window** (160K tokens on current 200K context models), a **persistent warning banner** appears in the conversation header:

> *"This conversation is getting long. Older turns are being summarised automatically to keep [AssistantName] running. [View summary ↗]"*

The warning is persistent (not dismissible) and remains visible until the conversation ends or is branched.

### Automatic summarisation — default behaviour

When the context window reaches **80%**, the platform **automatically summarises the oldest turns** to free space, without requiring user action.

| Element | Behaviour |
|---------|----------|
| What gets summarised | Oldest turns first — the earliest 40% of turns are summarised; the most recent 60% are always kept verbatim in the context window |
| Summary model | A separate **Claude Haiku 4.5** API call generates the summary before the next user turn is processed |
| Summary format | Structured: **Key entities discussed** · **Key findings** · **Decisions or conclusions reached** · **Unresolved questions** |
| Visibility | A **condensation marker** is inserted in the conversation thread: *"↑ N turns summarised — [tap to expand]"* |
| Expansion | Tapping the marker shows the full structured summary inline |
| Audit trail | Original turn content is **always retained in full** in `assistant.turns`. Summarisation affects only the active context window sent to the AI provider, not stored data. |
| Frequency | Re-summarises incrementally on each subsequent turn that would exceed the context limit |
| Injection | Summary injected as a `[Context from earlier turns]` block at the top of the conversation context — clearly labelled so the model treats it as historical context |

### Manual branch — user-initiated

At any point, the user may start a new conversation thread from the current context. A **"Continue in new thread"** button appears in the warning banner. Clicking it:

1. Creates a new conversation thread
2. Pre-loads it with the auto-generated summary as the opening context
3. Links it back to the origin conversation with a *"Continued from: [title], turn N"* header chip
4. Archives the original conversation (untouched)

### Model context limits

| Model | Context window | Warning threshold |
|-------|---------------|------------------|
| Claude Haiku 4.5 | 200K tokens | 160K tokens (80%) |
| Claude Sonnet 4.6 | 200K tokens | 160K tokens (80%) |
| Claude Opus 4.7 | 200K tokens | 160K tokens (80%) |

---

## History panel organisation

```
┌─────────────────────────────┐
│  🔍 Search conversations     │
│  + New conversation          │
├─────────────────────────────┤
│  📌 Pinned                   │
│  ├── Weekly Governance Check │
│  └── Q3 Review Thread        │
├─────────────────────────────┤
│  My Conversations            │
│  ├── Payment service audit   │
│  ├── Refund policy query     │
│  └── Onboarding questions    │
├─────────────────────────────┤
│  Shared With Me              │
│  ├── 📋 Team review session  │
│  └── 📋 Incident post-mortem │
└─────────────────────────────┘
```

- **Pinned** — conversations explicitly pinned by the user; always at the top regardless of recency; max 5; pin/unpin via right-click or long-press context menu
- **My Conversations** — all conversations created by the authenticated user; reverse-chronological
- **Shared With Me** — conversations to which the user has accepted an invitation; reverse-chronological; visually distinct (shared icon)
- Conversations with unread turns in shared threads show a badge count
- Archived conversations are hidden unless the archived filter is active

---

## In-conversation search

Users may search within the currently open conversation to locate a specific turn or content. Accessible via **`Cmd/Ctrl + F`** while the conversation area is focused.

| Behaviour | Specification |
|-----------|--------------|
| Scope | Full text of all turns in the current conversation — user messages, assistant responses, and artefact names |
| Presentation | Matching text highlighted in-thread; navigation arrows to move between matches |
| Turn navigation | Each match shows the turn number and jumps the scroll position to that turn |
| Close | `Escape` or clicking outside the search bar dismisses it |

In-conversation search is distinct from the cross-conversation search in the history panel (`Cmd/Ctrl + K`), which searches across all conversations.
