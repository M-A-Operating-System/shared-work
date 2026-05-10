# 05 — Input and Composition

## Free-form text input

The primary input is a **multi-line natural-language text field**.

| Behaviour | Specification |
|-----------|--------------|
| Growth | Field grows to five lines before scrolling internally |
| Submit | `Cmd/Ctrl + Enter` |
| While streaming | Input is disabled; replaced by a stop-generation button |
| Character limit | None enforced in v1 (subject to model context window) |

---

## `@`-binding — object binding typeahead

Typing `@` anywhere in the input opens a **scoped typeahead panel** that filters in real time against the bindable object types configured by the host application.

### Binding mechanics

1. User types `@` — typeahead panel opens immediately.
2. User continues typing — panel filters in real time using fuzzy match from the first character after `@`.
3. User selects an object — a **binding chip** is inserted: a styled atomic pill carrying the object type icon and display name, e.g. `@{Finance Domain}`.
4. On submission, binding chips are **resolved server-side** before the message reaches the AI model. The user sees chips; the model receives structured context blocks assembled from the host-configured `contextTemplate` for that bindable type.
5. **Clicking a binding chip** in any message (input or response) fires a `binding-click` event on the web component. The host application handles this event — typically navigating to the object's detail page within the host application. See [16-embedding-and-web-component.md](./16-embedding-and-web-component.md).

### Bindable types

Bindable types are entirely host-configured. The platform provides the typeahead mechanism; the host defines what can be bound via the `bindableTypes` section of the application config (see [00-host-application-config.md](./00-host-application-config.md)).

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

### Inactive and disabled objects

Binding chips for objects that are marked inactive in the host application's search endpoint response (`inactive: true`) are rendered in a **greyed-out style** with an `(inactive)` suffix.

| Behaviour | Specification |
|-----------|--------------|
| Chip appearance | Grey fill and muted text; `(inactive)` suffix; object type icon retained |
| Resolution | The chip still resolves — the `contextTemplate` is populated and the model receives the resolved context, including the inactive status |
| Context injected | The resolved block includes the object's inactive state so the model can acknowledge it |
| Navigation | Clicking the chip still fires the `binding-click` event |
| Typeahead | Inactive objects appear below active objects of the same type, with the `(inactive)` suffix visible |

This ensures historical conversations remain navigable even when referenced objects have been retired — the binding never silently breaks.

### Typeahead behaviour

| Behaviour | Specification |
|-----------|--------------|
| Match | Fuzzy match from the first character after `@` |
| Ranking | Host-configured rank order (ascending `rank` field in `bindableTypes`); alphabetical within type when `rank` values are equal |
| Maximum results | 8 results visible; scroll to see more |
| Keyboard navigation | Arrow keys to move; Enter or Tab to select; Escape to dismiss |
| Mobile | Typeahead anchors to the bottom of the viewport (not cursor position) |
| Permission scope | Each user's typeahead results are filtered by the host's `searchEndpoint` — users see only objects their host application allows them to access |

### `@`-binding in shared conversations

When a conversation is shared, each participant's typeahead is scoped to their own permissions (as enforced by the host's `searchEndpoint`). A participant cannot bind to an object they cannot access in the host application.

If a submitted message contains a binding to an object that another participant cannot access, the restricted participant sees the chip labelled **"[Restricted object]"** — they do not see the resolved context that was injected into the model prompt. See [08-shared-conversations.md](./08-shared-conversations.md).

---

## Display ID detection

When a host application configures a `displayIdPattern` on a bindable type, pasting text that matches the pattern anywhere in the input is **detected automatically**. On detection, the interface presents a direct lookup confirmation:

> *"That looks like a [Type] ID. Want me to look up [displayId]?"*  
> [Yes, look it up] &nbsp;&nbsp; [No, keep as text]

This supports workflows where IDs are shared via email, Slack, or reports — users can paste them directly without knowing the object's name.

---

## Document attachments

Users may attach **multiple documents per message turn**. The limit is a total storage budget per conversation, not a per-message count.

### Supported formats

| Format | Extensions | Processing |
|--------|-----------|-----------|
| PDF | `.pdf` | Full text and structure extracted up to the token limit |
| Excel | `.xlsx`, `.xls` | Sheets extracted as tabular data; multiple sheets processed sequentially |
| Word | `.docx`, `.doc` | Body text, headings, and tables extracted; tracked changes ignored |
| Image | `.png`, `.jpg`, `.jpeg`, `.webp` | Processed as vision content — model can read and reason about the visual content. Typical use: screenshots, dashboards, reports, or external documents not available as PDFs |

Images may be attached directly or **pasted from the clipboard** (`Cmd/Ctrl+V` when the input field is focused). The input area shows a preview thumbnail for each attached image before submission.

### Constraints

| Constraint | Default | Config field |
|-----------|---------|-------------|
| Maximum file size | 10 MB | `conversations.maxAttachmentMbPerFile` |
| Total attachment budget per conversation | 100 MB | `conversations.maxAttachmentMbPerConversation` |
| Password-protected files | Not supported in v1 | — |
| Embedded images | Extracted as vision content blocks where supported; otherwise skipped with a notice | — |
| Quantity per message turn | No limit | — |

### Budget enforcement

The input area displays a running attachment budget indicator: *"42 MB of 100 MB used"*. When the conversation budget is full:
- The attachment button is disabled
- A notice appears: *"Attachment limit reached for this conversation. Start a new conversation to attach more files."*
- Previously attached files remain available in the artefact tray

### Artefact retention

Attached files are **stored in full** in platform storage as part of the conversation audit trail. They are downloadable from the artefact tray for the lifetime of the conversation record and are not deleted when the user closes the session.

### Document display in the conversation

Attached documents appear in the user message bubble as a labelled file card: format icon, file name, and page/sheet count. Documents are not rendered inline.

When the model references a specific section of an attached document, it cites by page number (PDF), sheet name (Excel), or heading (Word).

---

## Message editing

An **edit icon** is associated with each past user message. On desktop it appears on hover; on mobile it is always visible below the message (no hover state). Long-pressing the message on mobile also opens the message action menu.

| Action | Behaviour |
|--------|----------|
| Click edit icon | Inline edit field opens, pre-populated with the original text |
| `@`-binding chips | Preserved in the edit field; editable |
| Submit | Creates a new branched conversation thread (see [04-conversation-management.md](./04-conversation-management.md)) |
| `Escape` | Cancels edit; no branch created; original conversation untouched |

### What editing does not do

- It does not modify the original message in place.
- It does not delete the original conversation thread.
- It does not create an "alternate" version within the same thread.

Editing always creates a distinct, independently navigable thread. This satisfies P4 — audit completeness: no original query-response pair is ever destroyed.
