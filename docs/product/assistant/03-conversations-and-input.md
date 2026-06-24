# 03 — Conversations and Input

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Conversation management

### Conversation model

Each conversation is a **named, persistent thread** scoped to the authenticated user within their tenant. Key properties:

- Conversations survive browser refresh and are resumable across sessions.
- The history panel lists all past conversations in reverse-chronological order with auto-generated titles derived from the first user message.
- Users may rename, archive, or delete conversations — subject to the tenant's configured retention period (see [08-platform-operations.md](./08-platform-operations.md)).
- Conversations are **append-only at the turn level**. No turn is ever overwritten or destroyed. Editing creates a new branched thread; the original is preserved in full.

#### Conversation states

| State | Description |
|-------|-------------|
| **Active** | Has been interacted with in the last 30 days; appears in the default history view |
| **Pinned** | Permanently anchored to the top of the My Conversations list regardless of recency. Maximum 5 pinned conversations. Useful for recurring reviews or ongoing work threads. |
| **Archived** | Hidden from default history view; accessible via archived filter; retains full content |
| **Deleted** | Removed from user view; physical deletion deferred to retention expiry per tenant retention policy |
| **Shared** | One or more other authenticated users in the same tenant have accepted an invitation; appears under **Shared With Me** group in history panel |
| **Locked (read-only)** | Last remaining participant's account deactivated; flagged for administrative review |

---

### Conversation branching

Users may edit any previously submitted message. Editing creates a **new conversation thread** — not an in-thread branch.

#### Branch mechanics

1. User clicks the edit icon on any past user message.
2. An inline edit field opens, pre-populated with the original text. `@`-binding chips are preserved and editable.
3. Submitting the edited message creates a **new conversation thread** that inherits all turns up to and including the edited turn (with the edit applied) and continues independently.
4. The original conversation is **untouched**.
5. Both threads are linked:
   - The new branch carries a header chip: *"Branched from: [title], turn N"*
   - The origin conversation carries a reciprocal reference at the corresponding turn
6. `Escape` cancels the edit without creating a branch.

#### Regeneration

Regeneration (resending an unchanged message for a fresh model response) follows the same model: a new thread is created from that turn point. The original response in the parent conversation is untouched.

#### Why branching, not in-place editing?

> **Audit completeness (P4):** Every turn is an auditable record. Overwriting turns in place would destroy the original query-response pair. Branching preserves both the original intent and the refined intent as independent, auditable threads. This design holds regardless of the host application domain.

---

### Conversation search

A search field at the top of the history panel searches across all the authenticated user's conversations — personal and shared — within their tenant.

#### Search scope

| Field searched | Examples |
|---------------|---------|
| Conversation title | "Finance governance review" |
| User message text | "Compare error rates for `@{Payment Service}`" |
| Assistant response text | "The Payment Service had three error spikes in the last hour" |

#### Search behavior

- Results are returned in **relevance order** with the matching excerpt highlighted.
- Selecting a result opens the conversation **at the matching turn**.
- Accessible via `Cmd/Ctrl + K` from anywhere on the chat surface.
- On mobile, search opens as a **full-screen overlay** with the keyboard raised.
- Search spans both **My Conversations** and **Shared With Me** groups.

---

### Context window management

Silent truncation is not permitted (P1 — transparency first). The user is always informed when context is being condensed.

#### Conversation length limit

A conversation may not exceed **100 turns** (configurable per tenant up to the platform maximum via `conversations.maxTurnLimit`). This is an explicit product limit — not a technical one — chosen to keep conversations focused and auditable. At the turn limit, the conversation is closed to new input and the user is prompted to continue in a new thread (see branching above). The full turn history is always retained in the audit trail.

#### Token warning — 80%

Before the turn limit is reached, the active context window may fill based on message length and attachment size. When a conversation reaches **80% of the model's context window** (160K tokens on current 200K context models), a **persistent warning banner** appears in the conversation header:

> *"This conversation is getting long. Older turns are being summarized automatically to keep [AssistantName] running. [View summary ↗]"*

The warning is persistent (not dismissible) and remains visible until the conversation ends or is branched.

#### Automatic summarization — default behavior

When the context window reaches **80%**, the platform **automatically summarizes the oldest turns** to free space, without requiring user action.

| Element | Behavior |
|---------|----------|
| What gets summarized | Oldest turns first — the earliest 40% of turns are summarized; the most recent 60% are always kept verbatim in the context window |
| Summary model | A separate **fast-tier model** API call generates the summary before the next user turn is processed |
| Summary format | Structured: **Key entities discussed** · **Key findings** · **Decisions or conclusions reached** · **Unresolved questions** |
| Visibility | A **condensation marker** is inserted in the conversation thread: *"↑ N turns summarized — [tap to expand]"* |
| Expansion | Tapping the marker shows the full structured summary inline |
| Audit trail | Original turn content is **always retained in full** in `assistant.turns`. Summarisation affects only the active context window sent to the AI provider, not stored data. |
| Frequency | Re-summarizes incrementally on each subsequent turn that would exceed the context limit |
| Injection | Summary injected as a `[Context from earlier turns]` block at the top of the conversation context — clearly labeled so the model treats it as historical context |

#### Manual branch — user-initiated

At any point, the user may start a new conversation thread from the current context. A **"Continue in new thread"** button appears in the warning banner. Clicking it:

1. Creates a new conversation thread
2. Pre-loads it with the auto-generated summary as the opening context
3. Links it back to the origin conversation with a *"Continued from: [title], turn N"* header chip
4. Archives the original conversation (untouched)

#### Model context limits

Context window sizes are determined by the configured AI provider and model tier. The 80% warning threshold applies regardless of context size.

| Model tier | Typical context window | Warning threshold |
|------------|----------------------|------------------|
| Fast | Provider-specific — refer to provider documentation | 80% of context window |
| Standard | Provider-specific | 80% of context window |
| Powerful | Provider-specific | 80% of context window |

The platform queries the active model's context limit at session start and calculates the warning threshold dynamically. Summarisation triggers at 80% of whatever the active model's window is — no manual threshold configuration is needed.

---

### History panel organization

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
│  — Today —                   │
│  ├── Payment service audit   │
│  — Yesterday —               │
│  ├── Refund policy query     │
│  — Past 7 days —             │
│  └── Onboarding questions    │
├─────────────────────────────┤
│  Shared With Me              │
│  ├── 📋 Team review session  │
│  └── 📋 Incident post-mortem │
└─────────────────────────────┘
```

- **Pinned** — conversations explicitly pinned by the user; always at the top regardless of recency; max 5; pin/unpin via right-click or long-press context menu
- **My Conversations** — all conversations created by the authenticated user; grouped by recency (Today / Yesterday / Past 7 days / Past 30 days / Older); within each group, reverse-chronological. Groups with no conversations are omitted.
- **Shared With Me** — conversations to which the user has accepted an invitation; reverse-chronological; visually distinct (shared icon)
- Conversations with unread turns in shared threads show a badge count
- Archived conversations are hidden unless the archived filter is active
- **Empty state** — when the user has no conversations at all (first visit, or after deletion of all conversations), the My Conversations area shows a brief prompt to start a new conversation, mirroring the onboarding state in the conversation area
- **Search empty state** — when a search query returns no results, the panel shows *"No conversations matching '[query]'"* with a prompt to try different terms

---

### In-conversation search

Users may search within the currently open conversation to locate a specific turn or content. Accessible via **`Cmd/Ctrl + F`** while the conversation area is focused.

| Behavior | Specification |
|-----------|--------------|
| Scope | Full text of all turns in the current conversation — user messages, assistant responses, and artifact names |
| Presentation | Matching text highlighted in-thread; navigation arrows to move between matches |
| Turn navigation | Each match shows the turn number and jumps the scroll position to that turn |
| Close | `Escape` or clicking outside the search bar dismisses it |

In-conversation search is distinct from the cross-conversation search in the history panel (`Cmd/Ctrl + K`), which searches across all conversations.

---

## Input and composition

### Free-form text input

The primary input is a **multi-line natural-language text field**.

| Behavior | Specification |
|-----------|--------------|
| Growth | Field grows to five lines before scrolling internally |
| Submit | `Cmd/Ctrl + Enter` |
| While streaming | Input is disabled; replaced by a stop-generation button |
| Character limit | None enforced in v1 (subject to model context window) |
| Draft preservation | An unsent message is preserved per conversation in browser storage. If the user switches to another conversation or navigates away, the draft is restored when they return to that conversation. Drafts are discarded on explicit send or when the user manually clears the field. `@`-binding chips are included in draft state. |

---

### `@`-binding — object binding typeahead

Typing `@` anywhere in the input opens a **scoped typeahead panel** that filters in real time against the bindable object types configured by the host application.

#### Binding mechanics

1. User types `@` — typeahead panel opens immediately.
2. User continues typing — panel filters in real time using fuzzy match from the first character after `@`.
3. User selects an object — a **binding chip** is inserted: a styled atomic pill carrying the object type icon and display name, e.g. `@{Finance Domain}`.
4. On submission, binding chips are **resolved server-side** before the message reaches the AI model. The user sees chips; the model receives structured context blocks assembled from the host-configured `contextTemplate` for that bindable type.
5. **Clicking a binding chip** in any message (input or response) fires a `binding-click` event on the web component. The host application handles this event — typically navigating to the object's detail page within the host application. See [07-embedding-and-integration.md](./07-embedding-and-integration.md).

#### Bindable types

Bindable types are entirely host-configured. The platform provides the typeahead mechanism; the host defines what can be bound via the `bindableTypes` section of the application config (see [02-host-config.md](./02-host-config.md)).

Examples of host-configured bindable types:

| Example type | Example chip | What gets injected into model prompt |
|-------------|-------------|--------------------------------------|
| Data Domain | `@{Finance Domain}` | Domain name, ID, owner, entity count — from host `contextTemplate` |
| Policy | `@{Refund Policy}` | Policy name, status, effective date, summary — from host `contextTemplate` |
| Service | `@{Payment Service}` | Service name, owner, SLO, current health — from host `contextTemplate` |
| Customer | `@{Acme Industries}` | Customer name, account status, account manager — from host `contextTemplate` |
| Document | `@{Q2 Board Report}` | Document title, type, date, summary — from host `contextTemplate` |
| Workflow | `@{Expense Approval Workflow}` | Workflow name, description — invokes the workflow prompt on submission |

Any object type the host application defines is bindable. The platform imposes no restrictions on the number or nature of bindable types.

#### Inactive and disabled objects

Binding chips for objects that are marked inactive in the host application's search endpoint response (`inactive: true`) are rendered in a **greyed-out style** with an `(inactive)` suffix.

| Behavior | Specification |
|-----------|--------------|
| Chip appearance | Grey fill and muted text; `(inactive)` suffix; object type icon retained |
| Resolution | The chip still resolves — the `contextTemplate` is populated and the model receives the resolved context, including the inactive status |
| Context injected | The resolved block includes the object's inactive state so the model can acknowledge it |
| Navigation | Clicking the chip still fires the `binding-click` event |
| Typeahead | Inactive objects appear below active objects of the same type, with the `(inactive)` suffix visible |

This ensures historical conversations remain navigable even when referenced objects have been retired — the binding never silently breaks.

#### Typeahead layout

```
┌──────────────────────────────────────────────────────────┐
│  Tell me about @fin                                      │  ← Input with @ typed
│              ┌──────────────────────────────────────┐    │
│              │ Data Domains                          │    │
│              │  🗄 Finance Domain       DOM-001  ▶  │    │  ← Highlighted result
│              │  🗄 Financial Reporting  DOM-012     │    │
│              │  🗄 FinTech Partnerships DOM-037     │    │
│              │                                      │    │
│              │ Policies                              │    │
│              │  🛡 Financial Controls Policy        │    │
│              │  🛡 Finance Data Retention           │    │
│              └──────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
  Arrow keys to navigate · Enter or Tab to select · Esc to dismiss
```

After selection, the chosen object becomes a binding chip inline in the input:

```
┌──────────────────────────────────────────────────────────┐
│  Tell me about [@Finance Domain ×]                       │  ← Binding chip
└──────────────────────────────────────────────────────────┘
```

Inactive objects appear below active results with a greyed style:

```
              │  🗄 Finance Domain  (inactive)  DOM-004  │
```

#### Typeahead behavior

| Behavior | Specification |
|-----------|--------------|
| Match | Fuzzy match from the first character after `@` |
| Ranking | Host-configured rank order (ascending `rank` field in `bindableTypes`); alphabetical within type when `rank` values are equal |
| Maximum results | 8 results visible; scroll to see more |
| Keyboard navigation | Arrow keys to move; Enter or Tab to select; Escape to dismiss |
| Mobile | Typeahead anchors to the bottom of the viewport (not cursor position) |
| Permission scope | Each user's typeahead results are filtered by the host's `searchEndpoint` — users see only objects their host application allows them to access |

#### `@`-binding in shared conversations

When a conversation is shared, each participant's typeahead is scoped to their own permissions (as enforced by the host's `searchEndpoint`). A participant cannot bind to an object they cannot access in the host application.

If a submitted message contains a binding to an object that another participant cannot access, the restricted participant sees the chip labeled **"[Restricted object]"** — they do not see the resolved context that was injected into the model prompt. See [05-tools-and-memory.md](./05-tools-and-memory.md).

---

### Display ID detection

When a host application configures a `displayIdPattern` on a bindable type, pasting text that matches the pattern anywhere in the input is **detected automatically**. On detection, the interface presents a direct lookup confirmation:

```
┌──────────────────────────────────────────────────────────┐
│  Please review DOM-4821                                  │  ← Pasted text
│  ┌────────────────────────────────────────────────────┐  │
│  │ That looks like a Data Domain ID.                  │  │
│  │ Want me to look up DOM-4821?                       │  │
│  │                                                    │  │
│  │  [Yes, look it up]          [No, keep as text]     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

If confirmed, `DOM-4821` is resolved to a binding chip exactly as if the user had selected it via the `@`-binding typeahead.

> *"That looks like a [Type] ID. Want me to look up [displayId]?"*  
> [Yes, look it up] &nbsp;&nbsp; [No, keep as text]

This supports workflows where IDs are shared via email, Slack, or reports — users can paste them directly without knowing the object's name.

---

### Document attachments

Users may attach **multiple documents per message turn**. The limit is a total storage budget per conversation, not a per-message count.

#### Supported formats

| Format | Extensions | Processing |
|--------|-----------|-----------|
| PDF | `.pdf` | Full text and structure extracted up to the token limit |
| Excel | `.xlsx`, `.xls` | Sheets extracted as tabular data; multiple sheets processed sequentially |
| Word | `.docx`, `.doc` | Body text, headings, and tables extracted; tracked changes ignored |
| Image | `.png`, `.jpg`, `.jpeg`, `.webp` | Processed as vision content — model can read and reason about the visual content. Typical use: screenshots, dashboards, reports, or external documents not available as PDFs |

Images may be attached directly or **pasted from the clipboard** (`Cmd/Ctrl+V` when the input field is focused). The input area shows a preview thumbnail for each attached image before submission.

#### Constraints

| Constraint | Default | Config field |
|-----------|---------|-------------|
| Maximum file size | 10 MB | `conversations.maxAttachmentMbPerFile` |
| Total attachment budget per conversation | 100 MB | `conversations.maxAttachmentMbPerConversation` |
| Password-protected files | Not supported in v1 | — |
| Embedded images | Extracted as vision content blocks where supported; otherwise skipped with a notice | — |
| Quantity per message turn | No limit | — |

#### Budget enforcement

The input area displays a running attachment budget indicator: *"42 MB of 100 MB used"*. When the conversation budget is full:
- The attachment button is disabled
- A notice appears: *"Attachment limit reached for this conversation. Start a new conversation to attach more files."*
- Previously attached files remain available in the artifact tray

#### Artifact retention

Attached files are **stored in full** in platform storage as part of the conversation audit trail. They are downloadable from the artifact tray for the lifetime of the conversation record and are not deleted when the user closes the session.

#### Document display in the conversation

Attached documents appear in the user message bubble as a labeled file card: format icon, file name, and page/sheet count. Documents are not rendered inline.

```
┌────────────────────────────────────────────────────────────┐
│  ┌──────────────────────┐  ┌────────────────────────────┐  │
│  │ 📄 Q2 Report.pdf     │  │ 📊 Finance Data.xlsx       │  │  ← File cards
│  │   32 pages           │  │   3 sheets                 │  │
│  └──────────────────────┘  └────────────────────────────┘  │
│                                                            │
│  Summarize the key governance findings and compare         │  ← Message text
│  against the Finance domain metrics.                       │
└────────────────────────────────────────────────────────────┘
```

The attachment budget indicator appears below the input area:

```
┌──────────────────────────────────────────────────────────┐
│  [input…]                                          [→]   │
├──────────────────────────────────────────────────────────┤
│ 📎  42 MB of 100 MB used  ████████░░░░░░░░░░░░░░         │
└──────────────────────────────────────────────────────────┘
```

When the conversation attachment budget is exhausted:

```
┌──────────────────────────────────────────────────────────┐
│  [📎 disabled]  [input…]                           [→]   │
├──────────────────────────────────────────────────────────┤
│ 📎  100 MB of 100 MB used  ████████████████████████  ⚠   │
│ Attachment limit reached. Start a new conversation to    │
│ attach more files.                                       │
└──────────────────────────────────────────────────────────┘
```

When the model references a specific section of an attached document, it cites by page number (PDF), sheet name (Excel), or heading (Word).

---

### Message editing

An **edit icon** is associated with each past user message. On desktop it appears on hover; on mobile it is always visible below the message (no hover state). Long-pressing the message on mobile also opens the message action menu.

| Action | Behavior |
|--------|----------|
| Click edit icon | Inline edit field opens, pre-populated with the original text |
| `@`-binding chips | Preserved in the edit field; editable |
| Submit | Creates a new branched conversation thread (see [Conversation branching](#conversation-branching)) |
| `Escape` | Cancels edit; no branch created; original conversation untouched |

#### Edit field layout

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Show me the quality gaps for @{Finance Domain}     │  │  ← Edit field
│  │                                              ↵     │  │    (pre-populated,
│  └────────────────────────────────────────────────────┘  │     chips editable)
│                                                          │
│  [Save and branch →]               [Cancel  Esc]        │
│                                                          │
│  ⓘ Editing creates a new branch — the original          │
│     conversation and responses are preserved.            │
└──────────────────────────────────────────────────────────┘
```

#### What editing does not do

- It does not modify the original message in place.
- It does not delete the original conversation thread.
- It does not create an "alternate" version within the same thread.

Editing always creates a distinct, independently navigable thread. This satisfies P4 — audit completeness: no original query-response pair is ever destroyed.
