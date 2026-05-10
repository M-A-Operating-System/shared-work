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

## `@`-binding — lookahead object binding

Typing `@` anywhere in the input opens a **scoped typeahead panel** that filters in real time against the full DDA object catalogue accessible to the authenticated user.

### Binding mechanics

1. User types `@` — typeahead panel opens immediately.
2. User continues typing — panel filters in real time using fuzzy match from the first character after `@`.
3. User selects an object — a **binding chip** is inserted: a styled atomic pill carrying the object type icon and display name, e.g. `@{Finance Domain}`.
4. On submission, binding chips are **resolved server-side** before the message reaches the AI model. The user sees chips; the model receives structured context blocks in the established DDA format — `@{ObjectName}` for entity/object bindings and `#{InlineReference}` for inline structured data references, consistent with the existing text-blob conventions used across the platform.
5. **Clicking a binding chip** in any message (input or response) **navigates to the corresponding DDA page** for that object — the entity record, domain view, data owner profile, or survey, as appropriate. This makes Andi a direct gateway into the DDA platform.

### Bindable object types

Bindable object types are driven by `src/config/entityRegistry.ts` (source of truth) and the generated `supabase/functions/_shared/entityMeta.ts` — any entity type with a valid `mcp` block in `entityMeta` is automatically bindable with no additional configuration.

| Object type | Example chip | Resolved context injected into model prompt |
|-------------|-------------|---------------------------------------------|
| Domain | `@{Finance Domain}` | Name, Display ID, owning team, entity count |
| Concept | `@{Customer Lifetime Value}` | Name, Display ID, definition, linked entities and models |
| Product | `@{Payments Platform}` | Name, Display ID, owning domain, associated data assets |
| Entity | `@{Customer Master Entity}` | Name, Display ID, domain, data owner, classification, quality score |
| Data Model | `@{Transaction Data Model}` | Name, Display ID, linked entities, version, owner |
| Data Owner | `@{Jane Smith}` | Name, owned entities and domains, contact |
| Survey | `@{Q2 Data Maturity Survey}` | Survey title, scope, response summary, key findings, strategic recommendations linked to it |
| Policy / Standard | `@{Data Retention Policy}` | Policy title, scope, version, effective date, key provisions — planned capability; not in current release (see [ROADMAP.md](./ROADMAP.md)) |
| Guided Workflow | `@{Data Quality Assessment}` | Name, description — invokes full guided workflow prompt on submission |

> Binding a **Guided Workflow** object invokes the full workflow prompt alongside the user message — equivalent to clicking the workflow in the **Guided Workflows drawer** (DDA platform nav).

### Inactive and disabled objects

Binding chips for objects that are **inactive or disabled** in the DDA platform are rendered in a **greyed-out style** with an `(inactive)` suffix appended to the display name — for example: `@{Finance Domain (inactive)}`.

| Behaviour | Specification |
|-----------|--------------|
| Chip appearance | Grey fill and muted text; `(inactive)` suffix; object type icon retained |
| Resolution | The chip still resolves — the MCP tool call is made and the model receives the resolved context, including the inactive status flag |
| Context injected | The resolved context block includes the object's inactive/disabled state so the model can acknowledge it in its response |
| Navigation | Clicking the chip still navigates to the DDA page for the object |
| Typeahead | Inactive objects appear in typeahead results below active results for the same type, with `(inactive)` suffix visible in the result list |
| Write operations | Andi will not propose updates to an inactive object without first surfacing a warning that the object is inactive |

This ensures that historical conversations and audit trails remain fully navigable even when referenced objects have been retired — the binding never silently breaks.

### Typeahead behaviour

| Behaviour | Specification |
|-----------|--------------|
| Match | Fuzzy match from the first character after `@` |
| Ranking | Universal fixed order: Domain → Concept → Product → Entity → Data Model → Data Owner → Survey → Guided Workflow, then alphabetically within type |
| Maximum results | 8 results visible; scroll to see more |
| Keyboard navigation | Arrow keys to move; Enter or Tab to select; Escape to dismiss |
| Mobile | Typeahead anchors to the bottom of the viewport (not cursor position) |
| Permission scope | Each user's typeahead is scoped to their DDA permission level — objects they cannot access in the DDA UI do not appear |

### `@`-binding in shared conversations

When a user shares a conversation with other participants, each participant's typeahead is scoped to their own DDA permissions. A participant cannot bind to an object they cannot access in the main platform.

If a submitted message contains a binding to an object that another participant cannot access, the restricted participant sees the chip labelled **"[Restricted object]"** — they do not see the resolved context that was injected into the model prompt. This preserves each user's permission boundary within the shared thread.

---

## Display ID detection

Pasting a Display ID (e.g. `DMD00000001`) anywhere in the input is **detected automatically**. On detection, the interface pre-populates a direct entity lookup query, presenting it to the user for confirmation before submission.

This supports the existing DDA workflow where Display IDs are shared via email, Slack, or reports — users can paste them into Data AI Assistant without knowing the entity's name.

---

## Document attachments

Users may attach **multiple documents per message turn**. The limit is a total storage budget per conversation, not a per-message count.

### Supported formats

| Format | Extensions | Processing |
|--------|-----------|-----------|
| PDF | `.pdf` | Full text and structure extracted up to the token limit |
| Excel | `.xlsx`, `.xls` | Sheets extracted as tabular data; multiple sheets processed sequentially |
| Word | `.docx`, `.doc` | Body text, headings, and tables extracted; tracked changes ignored |
| Image | `.png`, `.jpg`, `.jpeg`, `.webp` | Processed as vision content — model can read and reason about the visual content. Typical use: screenshots of reports, dashboards, data quality outputs, or external governance documents not available as PDFs |

Images may be attached directly or **pasted from the clipboard** (Cmd/Ctrl+V when the input field is focused). The input area shows a preview thumbnail for each attached image before submission.

### Constraints

| Constraint | Specification |
|-----------|--------------|
| Maximum file size (per file) | 10 MB |
| **Total attachment budget (per conversation)** | **100 MB** — across all turns and all participants |
| Password-protected files | Not supported in v1 |
| Embedded images | Extracted as vision content blocks where supported; otherwise skipped with a user notice |
| Quantity per message turn | No limit — any number of supported files may be attached to a single message |

### Budget enforcement

The input area displays a running attachment budget indicator: *"42 MB of 100 MB used"*. When the conversation budget is full:
- The attachment button is disabled
- A notice appears: *"Attachment limit reached for this conversation (100 MB). Start a new conversation to attach more files."*
- Previously attached files remain available in the artefact tray and can still be referenced by the model

### Artefact retention

Attached files are **stored in full** in Supabase Storage as part of the conversation audit trail. They are downloadable from the artefact tray for the lifetime of the conversation record. They are not deleted when the user closes the session.

### Document display in the conversation

Attached documents appear in the user message bubble as a labelled file card showing: format icon, file name, and page/sheet count. Documents are not rendered inline.

When the model references a specific section of an attached document, it cites by page number (PDF), sheet name (Excel), or heading (Word).

---

## Message editing

An **edit icon** is associated with each past user message. On desktop it appears on hover; on mobile it is always visible below the message (no hover state). Long-pressing the message on mobile also opens the message action menu including edit.

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

Editing always creates a distinct, independently navigable thread. This design satisfies the P4 audit completeness principle — no original query-response pair is ever destroyed.
