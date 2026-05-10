# 09 — Interaction Design

## Page structure

Data AI Assistant is a **top-level navigation destination** within the DDA platform. The layout uses **four zones**, designed to integrate cleanly with the DDA platform's existing left navigation and to allow future sharing of the left nav between DDA modules and the assistant.

| Zone | Location | Contents |
|------|----------|---------|
| **DDA platform nav** | Far left (shared with DDA) | Top-level DDA navigation including Data AI Assistant entry; assistant sub-items: New Conversation, History, Guided Workflows |
| **History panel** | Inner left sidebar | Conversation list — **My Conversations** and **Shared With Me** (reverse-chronological); conversation search; pinned conversations; new conversation button |
| **Conversation area** | Centre — primary | Message thread, streaming responses, rendered content, input area |
| **Conversation panel** | Right sidebar | Attachments and artefacts for the **current conversation only**; participant list and share management; session token summary |

### Why this layout

The left side of the screen belongs to navigation and access — history and workflow entry points are navigation choices that fit naturally with the DDA platform's existing left nav pattern. The right side belongs to the **current conversation**: what has been attached, what has been produced, who is in the conversation. This distinction scales cleanly: as DDA adds more modules, the left nav can surface assistant navigation alongside them without restructuring the conversation view.

### DDA platform nav — assistant sub-items

When the user is in Data AI Assistant, the DDA platform nav shows assistant-level sub-items beneath the top-level entry:

| Sub-item | Behaviour |
|----------|----------|
| **New Conversation** | Starts a fresh conversation; clears the conversation area |
| **History** | Opens / collapses the inner left history panel |
| **Guided Workflows** | Opens the guided workflow library as a slide-in drawer over the history panel (not in the right sidebar) |

This means guided workflows are accessible from the nav, not pinned to the right sidebar. The right sidebar remains entirely conversation-specific.

### Conversation panel (right sidebar) detail

The right panel is scoped entirely to the **active conversation** — it changes when the user switches conversations.

| Section | Contents |
|---------|---------|
| **Attachments** | All documents and images attached to the current conversation, in submission order; file name, type, turn back-link |
| **Artefacts tray** | All output artefacts generated in the current conversation (Mermaid diagrams, Vega-Lite charts, data tables, JSON exports, code blocks); badge count on panel tab |
| **Participants** | Participant list (shared conversations); invite control; leave / remove actions |
| **Session summary** | Running token totals (`14 turns · 18,430 tokens`) with tooltip expanding to input / output / cached breakdown |

---

## Responsive and mobile design

Mobile-first and responsive layout is a core DDA platform standard — see [_design/02-responsive-and-mobile.md](../_design/02-responsive-and-mobile.md) for the platform-wide requirements. The following covers assistant-specific layout behaviour at each breakpoint.

| Viewport | Layout |
|----------|--------|
| Desktop (≥ 1280px) | Full four-zone layout — DDA nav + history panel + conversation area + conversation panel |
| Desktop narrow (1024px – 1279px) | History panel collapses to icon-only rail; conversation panel remains; DDA nav unchanged |
| Tablet (768px – 1023px) | DDA nav collapses to icon rail; history and conversation panels become slide-in drawers; conversation area is primary |
| Mobile (< 768px) | Single-column; DDA nav as top bar or bottom bar per platform convention; history and conversation panels as bottom-sheet drawers; input pinned to bottom |

### Mobile-specific requirements

| Requirement | Specification |
|-------------|--------------|
| Input controls | All controls (attachment, tool selection, model chip, send/stop) are thumb-reachable and fully visible — no controls hidden behind secondary menus |
| `@`-binding typeahead | Anchors to the bottom of the viewport (not cursor position); sized so the top edge is visible above the raised keyboard |
| Mermaid diagrams | Horizontally scrollable — never scaled to illegibility |
| Vega-Lite charts | `width: "container"` for responsive sizing |
| Data tables | Horizontally scrollable; first column (entity name or Display ID) is sticky |
| Conversation panel | Opens as full-height bottom sheet — accessible via a tray icon in the input area footer |
| History panel | Opens as full-height bottom sheet — accessible via the history sub-item in the DDA platform nav |
| Conversation search | Opens as full-screen overlay with keyboard raised |
| Touch targets | Minimum 44 × 44 px (Apple HIG / Material Design) — see [_design/03-accessibility.md](../_design/03-accessibility.md) |

### Input area on mobile

The input toolbar presents all controls in a **single row above the text field**, within thumb reach. When horizontal space is tight, secondary controls (model chip, profile indicator) collapse behind an overflow icon — the paperclip (attachment) and send/stop button are **never** moved to overflow.

| Control | Mobile behaviour |
|---------|----------------|
| Paperclip / attachment | Opens the native mobile file picker — includes camera roll, Files app, and camera capture. Drag-and-drop is desktop-only. |
| Image from camera | Accessible via the native file picker; camera capture supported on devices with a camera |
| Tool selection | Opens a full-screen bottom sheet listing available MCP tools |
| Model chip | Opens a bottom sheet listing available models |
| Text input | Grows to 3 lines maximum on mobile (vs. 5 on desktop) to preserve space above the raised keyboard |
| Submit | Large dedicated tap target — always visible; `Cmd/Ctrl + Enter` is the keyboard shortcut on desktop but the Send button is the primary action on mobile |
| Profile indicator | Hidden in the input area on mobile; accessible via the DDA profile settings page |

### Keyboard and viewport behaviour

When the software keyboard raises on mobile, the conversation thread scrolls to keep the latest turn visible above the input area. The input area stays pinned to the top of the keyboard — it does not scroll out of view. The `@`-binding typeahead panel appears above the keyboard, not above the cursor.

The **Jump to latest ↓** button is positioned above the input area so it remains visible and tappable when the keyboard is raised.

### Hover states on mobile

Many desktop interactions are hover-triggered. On mobile, hover does not exist. The following table defines the mobile equivalents for all hover-dependent controls.

| Desktop (hover) | Mobile equivalent |
|----------------|-----------------|
| Report icon appears on hover over a turn | Report icon is always visible on mobile — shown as a small persistent icon below each turn |
| Edit icon appears on hover over a user message | Edit icon always visible below each user message |
| Assistant response action row (regenerate, copy, artefact chip) appears on hover | Always visible below each assistant response |
| Metadata line (model + tokens) appears on hover | Tap the assistant response bubble to reveal the metadata line as an inline callout; tap again to hide |
| Inactive binding chip tooltip (`(inactive)` suffix) | Shown as permanent suffix text on the chip — no hover required |

### Gestures

| Gesture | Action |
|---------|--------|
| Swipe right from left edge | Opens the history panel bottom sheet |
| Swipe left from right edge | Opens the conversation panel bottom sheet |
| Long press on a user message | Opens the message action menu (edit, report, copy) |
| Long press on an assistant response | Opens the response action menu (copy, report, regenerate) |
| Tap a binding chip | Navigates to the DDA page for the bound object |
| Pinch-to-zoom on a Mermaid diagram | Enters full-screen diagram view |

### File attachment on mobile

On mobile, **drag-and-drop is not supported**. The paperclip icon opens the native file picker with the following sources:

- Camera roll / photo library
- Files app (iCloud Drive, device storage, third-party providers)
- Camera capture (take a photo directly)
- Documents from other apps (share sheet integration)

Clipboard paste (copy image from another app, then paste into the input field) is supported on mobile browsers that expose clipboard access.

### CSAT prompt on mobile

On mobile, the CSAT floating card is **centred in the viewport as a bottom sheet** rather than anchored to the bottom-right corner. It appears above the input area and does not obscure the conversation thread. Tap outside the sheet to skip.

### Keyboard shortcuts on mobile

Hardware keyboard shortcuts (`Cmd/Ctrl + Enter`, `Cmd/Ctrl + K`, etc.) are only applicable when a hardware keyboard is connected. On a software keyboard, all actions are performed via on-screen controls. The keyboard shortcut reference (`?` icon) is not shown on mobile unless a hardware keyboard is detected.

---

## Conversation thread anatomy

### User messages

- Right-aligned in a muted bubble
- `@`-binding chips render as interactive pills within the bubble
- In shared conversations: author's name and avatar above the bubble

### Other participants' messages (shared conversations only)

- Left-aligned
- Distinct colour per participant (DDA design system participant palette — up to nine distinct colours)
- Author name and avatar above the bubble

### Report icon — every turn

Every turn in the conversation thread (both user messages and assistant responses) carries a **report icon**. On desktop it is visible on hover; on mobile it is always visible below the turn (no hover state exists on touch devices).

Clicking it opens:

> **What's wrong with this?**
> [Text field — optional explanation]
> [Submit report] &nbsp;&nbsp; [Cancel]

The explanation is optional but strongly encouraged. On submit, an improvement signal is captured and stored against the specific turn (see [12-continuous-improvement.md](./12-continuous-improvement.md)).

| Report scenario | Turn type | Example |
|----------------|-----------|---------|
| Incorrect answer | Assistant | Model states the wrong data owner |
| Misleading framing | Assistant | Summary omits a known quality issue |
| Wrong entity referenced | User | User bound the wrong `@Entity` and wants to flag it for audit |
| Inappropriate response in shared session | Assistant | Response in shared context revealed restricted framing |

### Assistant responses

- Occupy the full content width
- Each assistant response carries:

| Element | Desktop | Mobile |
|---------|---------|--------|
| Metadata line | Appears on hover — model label + token counts + (in shared sessions) the name of the submitting user | Revealed on tap of the response bubble |
| Report icon | Appears on hover | Always visible below the response |
| Regenerate | Appears on hover | Always visible below the response |
| Copy full response | Appears on hover | Always visible below the response |
| Artefact chips | *"Added to artefacts ↗"* beneath each generated block | Same |

### Suggested follow-ups

At the end of each assistant response, up to **three suggested follow-up queries** are presented as pill chips generated by the model. Single-click to submit. Follow-ups are model-generated — not sourced from a static list.

---

## Input area controls

| Control | Function |
|---------|---------|
| Paperclip icon | Opens file picker or accepts drag-and-drop (PDF, Excel, Word, images); images also accepted via clipboard paste (Cmd/Ctrl+V) |
| Tool selection icon | Opens MCP tool opt-in panel |
| Active model chip | Opens model selection popover |
| Text input | Multi-line, grows to 5 lines, `Cmd/Ctrl + Enter` to submit |
| Profile indicator | Read-only `Style · Verbosity` link to DDA profile settings — not an editable inline control, but clickable |
| Send / Stop | Submits message or stops active stream |
| Share icon | Opens participant management panel (invite, view, and remove participants) |

---

## Session artefact tray

The artefact tray accumulates every input and output artefact produced during a conversation. It persists for the full lifetime of the conversation record — all file content is stored in Supabase Storage as part of the audit trail.

### Artefact classes

| Class | Direction | Examples |
|-------|-----------|---------|
| Attached document | Input | PDF report, Excel extract, Word policy document |
| Generated document | Output | Markdown report, Word document, PDF summary |
| Mermaid diagram | Output | ERD, lineage flow, workflow sequence |
| Vega-Lite chart | Output | Quality distribution, coverage metric, trend |
| Data table | Output | Multi-row query result (CSV) |
| JSON export | Output | Entity record or tool result |
| Code block | Output | SQL, Python, YAML |
| Binding reference | Input | Non-downloadable — reference card linking to the DDA entity record |

### Tray entry anatomy

Each tray entry shows:
- Format icon
- Auto-generated name: `[Content type] — [Subject] — [Date]`
- Turn back-link (click to jump to the source turn in the conversation)
- Direction label (Input / Output)
- Download button
- Preview link

Users may **rename** tray entries. A **"Download all"** control packages all artefacts as a zip archive.

---

## Onboarding state

On **first visit**, the conversation area shows a welcome state:

1. A one-sentence description of the CDO second brain concept
2. Three suggested starter questions — drawn from the **same guided workflow list** used in the Guided Workflows tab (e.g. the first three workflows in the platform-managed prompt library, surfaced as plain-language questions)
3. A link to the full guided workflow library (opens the Guided Workflows drawer from the DDA platform nav)

The onboarding state is shown once — it is not shown again once the user has started a conversation.

The starter questions are not hardcoded strings — they are generated from the platform-managed guided workflow registry, so they stay current as workflows are added or updated without a separate onboarding content change.

---

## Error and boundary states

| State | Presentation | User action |
|-------|-------------|------------|
| Model timeout | Inline error card with retry button | Retry re-submits the last message |
| MCP tool failure | Tool call disclosure shows error status and raw detail | Rephrase or copy error to report |
| MCP server unavailable | Degraded-mode banner; session continues in text-only mode | Model answers from system prompt context only; no silent failure |
| Context window limit (80%) | Subtle warning in conversation header | Branch to new thread or accept auto-summarisation |
| Out-of-scope query | Model explains scope boundary and suggests reformulation | No error state — graceful redirect |
| Auth session expired | Modal overlay prompting re-authentication | Re-auth restores session and full conversation history; any unsent in-progress input is lost |
| Unsupported file type | Inline notice on file selection | User prompted to use a supported format |
| Last participant constraint | Tooltip on disabled Leave/Remove controls | Invite another user before leaving |

---

## Accessibility

Platform-wide accessibility standards (WCAG 2.1 AA, keyboard navigation, touch targets, screen reader requirements, colour + state) are defined in [_design/03-accessibility.md](../_design/03-accessibility.md). The following are assistant-specific additions to those standards.

| Assistant-specific requirement | Specification |
|-------------------------------|--------------|
| Mermaid SVG alt text | Descriptive alt text generated by the model for each Mermaid diagram |
| Conversation thread live region | The conversation thread is an `aria-live` region — streaming assistant responses and new messages in shared conversations are announced to screen readers |
| `@`-binding typeahead | Fully keyboard-navigable (arrow keys, Enter/Tab to select, Escape to dismiss); focus returns to input field on selection or dismissal |

---

## Jump to latest

When a user has scrolled up in a conversation (to review earlier turns) and new content arrives (streaming response or shared conversation message), a **"Jump to latest ↓"** pill button appears, anchored to the bottom of the conversation area above the input field. Clicking it scrolls immediately to the most recent turn. The button disappears when the user is already at the bottom.

---

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + Enter` | Submit message |
| `Cmd/Ctrl + K` | Open cross-conversation search |
| `Cmd/Ctrl + F` | Open in-conversation search |
| `Cmd/Ctrl + N` | Start a new conversation |
| `Escape` | Cancel edit / dismiss typeahead / close modal |
| `↑` in empty input | Edit most recent user message |
| `Arrow keys` | Navigate `@`-binding typeahead; navigate in-conversation search results |
| `Enter` / `Tab` | Select item in `@`-binding typeahead |
| `Cmd/Ctrl + Shift + C` | Copy most recent assistant response to clipboard |
| `?` or `Cmd/Ctrl + /` | Show keyboard shortcut reference |

Keyboard shortcut reference is also accessible via the **`?` icon** in the input area footer.

---

## Post-session CSAT prompt

A **1–5 star rating prompt** is shown to a random 20% sample of users at the end of a session (not on every session — to avoid survey fatigue). See metric definition in [14-success-metrics.md](./14-success-metrics.md).

**Placement and presentation:**

The prompt appears as a **non-blocking floating card** anchored to the bottom-right of the conversation area, after the user has been idle for 30 seconds following the last assistant response:

> **How useful was this conversation?**
> ★ ★ ★ ★ ★
> [Optional: What could be better? — single text line]
> [Submit] &nbsp;&nbsp; [Skip]

- The card is dismissible (Skip or click outside)
- It does not block the input field or any conversation content
- Skipping is not counted as a negative signal — only submitted ratings are recorded
- The rating and optional comment are stored in `assistant.conversations.csat_score` and `assistant.conversations.csat_comment`
