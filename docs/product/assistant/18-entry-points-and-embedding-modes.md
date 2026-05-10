# 18 — Entry Points and Embedding Modes

The AI Chat Platform is delivered through three distinct embedding modes, each with its own component, visual presentation, and conversation model. Host applications may deploy one, two, or all three modes simultaneously — they are independent components that share the same platform backend.

---

## Mode overview

| Mode | Component | Conversation model | Persistence | Primary use |
|------|-----------|--------------------|-------------|-------------|
| **1 — Floating Widget** | `<ai-chat-widget>` | Full — shared with Mode 2 | Persistent across pages | Always-available assistant access from anywhere in the host app |
| **2 — Inline Page** | `<ai-chat>` | Full — shared with Mode 1 | Persistent | Dedicated assistant page or embedded content section |
| **3 — Form Field Assist** | `<ai-chat-field>` | Ephemeral — scoped to the field instance | Discarded on close | Contextual help and content generation for individual form fields |

Modes 1 and 2 are **persistent conversation modes** — they share the same conversation history for a given user and tenant. A conversation started in the floating widget appears in the history panel of the inline page view, and vice versa. Mode 3 is entirely **ephemeral and transactional** — it does not create persistent conversation threads and does not appear in any history view.

---

## Mode 1 — Floating Widget

### Overview

The floating widget provides always-available assistant access without requiring the user to navigate away from their current page. It is anchored to a corner of the viewport and overlays the host application's content. It has three states: **collapsed** (FAB only), **mini** (compact chat panel), and **full** (complete conversation interface).

### States

#### Collapsed state — the FAB

The widget renders as a **floating action button** (FAB) in the configured corner of the viewport (default: bottom-right). The FAB carries:

- The assistant's icon or initial (from `identity.logoUrl` or the first letter of `identity.assistantName`)
- An unread **badge** count when there are new messages in a shared conversation the user has not viewed
- A subtle pulse animation when the assistant is mid-stream in a minimised conversation

Clicking the FAB transitions to the mini state.

#### Mini state — compact chat panel

The mini state is a compact, non-blocking chat panel anchored above the FAB. Default dimensions: **380px wide × 520px tall**, configurable via the `widget` config section. The panel is elevated above host application content with a shadow; it does not push or reflow page content.

```
┌──────────────────────────────────────┐
│ 🤖 Atlas                 [ ↗ ] [ × ] │  ← Header
├──────────────────────────────────────┤
│                                      │
│  [Assistant response with rendered   │  ← Conversation thread
│   content — Mermaid diagrams show    │    (no history panel or
│   as thumbnails; tables scroll]      │    conversation panel)
│                                      │
│  [User message]                      │
│                                      │
├──────────────────────────────────────┤
│  [📎] [⚙] [✦ Sonnet]  [input…] [→]  │  ← Input area (compact)
└──────────────────────────────────────┘
```

**Mini state behaviours:**

| Element | Specification |
|---------|--------------|
| Conversation shown | The most recently active conversation. If no prior conversation exists, shows the onboarding welcome state. |
| History access | No history panel in mini state. A **conversations icon** (☰) in the header opens a compact conversation list overlay within the panel — not a full sidebar. |
| New conversation | Available via the conversations list overlay; "+ New" button |
| Input area | Full input capability: text, `@`-binding, attachments, model chip, tool selection. Controls compact but not hidden. |
| Content rendering | All content types render (prose, Mermaid, Vega-Lite, tables, code). Diagrams and wide tables are constrained to the panel width and scroll horizontally. Mermaid diagrams collapse to thumbnail by default — tap/click to expand to full-screen overlay. |
| Tool call disclosures | Rendered as collapsed cards, same as full mode. |
| Resize | User can drag the top edge to adjust panel height within the range 360px–80vh. Width is fixed. |
| Draggable | The panel header is draggable — user can reposition the mini panel within the viewport. |
| Keyboard shortcut | `Escape` collapses mini state back to FAB. |

**Header controls in mini state:**

| Control | Action |
|---------|--------|
| ↗ Expand icon | Transitions to full state (see below) |
| × Close icon | Collapses to FAB; does not end the conversation |

#### Full state — complete conversation interface

Clicking the expand icon (↗) from the mini state transitions to the full conversation interface. The full state renders as a **large modal overlay** occupying most of the viewport:

```
┌────────────────────────────────────────────────────────────┐
│ 🤖 Atlas                                    [ ↙ ] [ × ]   │
├──────────┬─────────────────────────────────┬───────────────┤
│ History  │                                 │ Conversation  │
│ panel    │     Conversation area           │ panel         │
│          │                                 │               │
│ My       │  (full 3-zone layout)           │ Artefacts     │
│ Convs    │                                 │ Participants  │
│          │                                 │ Token summary │
│ Shared   │                                 │               │
│ With Me  │                                 │               │
├──────────┴─────────────────────────────────┴───────────────┤
│              Input area (full)                             │
└────────────────────────────────────────────────────────────┘
```

The full state renders the complete three-zone layout from `09-interaction-design.md`. The conversation active in mini state is the conversation shown on transition — no context is lost.

**Full state behaviours:**

| Behaviour | Specification |
|-----------|--------------|
| Layout | Complete three-zone layout: history panel + conversation area + conversation panel |
| Modal dimensions | Default: `min(90vw, 1200px)` wide × `min(90vh, 860px)` tall, centred in viewport |
| Background | Host page dimmed (overlay) but not blocked — user can click outside to collapse to mini state |
| Transition | Smooth expand animation from mini panel position to modal centre |
| Collapse | ↙ icon collapses back to mini state; × closes to FAB |
| Page navigation | If the user navigates while full state is open, full state collapses to mini state automatically |

### Conversation continuity between mini and full

There is no transition cost when moving between mini and full states. The same conversation is active in both views, and they share state in real time — a response streaming in mini state continues streaming when the user expands to full state.

### Floating widget across page navigation

The floating widget persists across client-side page navigation (SPA routing). It retains the current conversation and streaming state as the user moves between pages. On hard page reload, the widget remounts and restores the most recently active conversation.

### Web component

```html
<!-- Place once in the host application shell / layout -->
<ai-chat-widget
  tenant-id="acme-corp"
  user-token="..."
  position="bottom-right"
></ai-chat-widget>
```

#### Widget-specific HTML attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `position` | `bottom-right` | FAB and panel position. Options: `bottom-right`, `bottom-left` |
| `mini-width` | `380` | Width of the mini panel in pixels (range: 320–600) |
| `mini-height` | `520` | Default height of the mini panel in pixels (range: 360–800) |
| `z-index` | `9000` | CSS z-index for the widget stack |
| `offset-x` | `24` | Horizontal margin from the viewport edge in pixels |
| `offset-y` | `24` | Vertical margin from the viewport edge in pixels |

#### Widget-specific events

| Event | Detail | Description |
|-------|--------|-------------|
| `widget-expanded` | `{ state: 'mini' \| 'full' }` | Widget transitioned from collapsed to mini or full |
| `widget-collapsed` | `{ previousState: 'mini' \| 'full' }` | Widget collapsed to FAB |

All other events from `16-embedding-and-web-component.md` (`binding-click`, `turn-complete`, `token-expired`, etc.) fire identically from `<ai-chat-widget>`.

### Config

The `widget` config section in the application config controls widget-level defaults:

```json
{
  "widget": {
    "defaultState": "collapsed",
    "fabIcon":      "https://cdn.acme.com/atlas-icon.svg",
    "showBadge":    true
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `defaultState` | `"collapsed"` | State on first page load: `"collapsed"` or `"mini"` |
| `fabIcon` | Assistant logo from `branding.logoUrl` | Custom icon for the FAB. 40×40px SVG or PNG. |
| `showBadge` | `true` | Show unread badge count on FAB for shared conversation activity |

---

## Mode 2 — Inline Page

### Overview

The inline page mode embeds the assistant as a first-class content block within a host application page. It uses the `<ai-chat>` component described in full in `16-embedding-and-web-component.md`. It is the **richest and most capable** embedding mode — the full three-zone layout with no constraints on features or content rendering.

### Conversation model

Mode 2 shares conversation history fully with Mode 1. The same history panel, the same conversation list, the same threads — a user moving between a dedicated assistant page (Mode 2) and the floating widget (Mode 1) sees the same conversations in both. There is no concept of "page-scoped" conversations in Mode 2.

### Typical placements

| Placement | Description |
|-----------|-------------|
| Dedicated assistant page | A route in the host application dedicated to the assistant (e.g. `/assistant`). The `<ai-chat>` component fills the main content area. Most capable experience. |
| Split-panel page | The host application page is split: content on the left, assistant on the right. The component is mounted in a fixed-width right panel (minimum 480px recommended). |
| Tab within a page | The assistant occupies one tab of a tabbed page. The component mounts/unmounts on tab switch — component state is restored on remount via the platform API. |

### Relationship to Mode 1

A host application that deploys both `<ai-chat>` and `<ai-chat-widget>` on the same page will have two simultaneous conversation views. This is an unusual configuration but is supported. Both components connect to the same platform backend with the same `tenant_id` and `user_id` — changes in one are reflected in the other in real time.

For most host applications, Mode 1 (floating widget) is deployed site-wide in the layout shell, and Mode 2 (inline) is deployed on a dedicated assistant page. When the user navigates to the dedicated page, the floating widget collapses automatically (the host application controls this by calling `widget.collapse()` on the `<ai-chat-widget>` element).

---

## Mode 3 — Form Field Assist

### Overview

The Form Field Assist provides contextual, ephemeral AI assistance scoped to an individual form field. It appears as a small icon or button adjacent to the field and opens a **compact contextual popover** when activated. The interaction is entirely transactional — there is no conversation history, no history panel, and no persistent thread. When the popover closes, the session is discarded.

Form Field Assist is designed for tasks like:
- *"Write a product description for this item"*
- *"Suggest a title based on these bullet points"*
- *"Explain what this field is asking for"*
- *"Translate this text into French"*
- *"Summarise this paragraph more concisely"*

### Trigger presentation

The trigger can be presented in two ways, depending on the host application's UI:

**Inline icon trigger** (inside the field)

```
┌────────────────────────────────────────────┐
│ Product description                        │
│ ┌──────────────────────────────────────┬──┐│
│ │                                      │✦ ││
│ │                                      │  ││
│ └──────────────────────────────────────┴──┘│
└────────────────────────────────────────────┘
```

A small ✦ (or assistant icon) appears inside the field at the trailing edge. It does not overlay field content — the field's right padding is adjusted by the component to accommodate it.

**External button trigger** (beside or below the field)

```
┌────────────────────────────────────────────┐
│ Product description                        │
│ ┌──────────────────────────────────────┐  │
│ │                                      │  │
│ └──────────────────────────────────────┘  │
│ [✦ AI assist]                             │
└────────────────────────────────────────────┘
```

A button or link appears below or beside the field. The host application styles the button; the `<ai-chat-field>` component fires a `field-trigger-click` event the host handles. This variant gives the host full control over the trigger's visual appearance.

The trigger variant is configured via the `trigger` attribute on the component (see Web component below).

### Popover layout

```
┌──────────────────────────────────────┐
│ ✦ Atlas  ·  Helping with: [Label]  × │  ← Header
├──────────────────────────────────────┤
│                                      │
│  [Compact conversation area]         │  ← Ephemeral thread
│  No history panel                    │    (messages for this
│  No artefact tray                    │     session only)
│  No shared conversations             │
│                                      │
├──────────────────────────────────────┤
│  [input…]                      [→]   │  ← Compact input
├──────────────────────────────────────┤  ← Write-back bar
│  [Insert into field]  [Copy]         │    (if write-back enabled)
└──────────────────────────────────────┘
```

Default popover dimensions: **320px wide × flexible height** (grows with conversation, max 480px, then scrolls). The popover anchors to the trigger element and repositions automatically to stay within the viewport.

### Ephemeral session model

| Property | Specification |
|----------|--------------|
| Conversation persistence | None — the session is discarded when the popover closes |
| History access | No history panel; no access to past conversations |
| Shared conversations | Not available |
| Model switching | Not available — uses the tenant's `defaultModel` |
| Workflow Library | Not available |
| Artefact tray | Not available (individual outputs can be inserted or copied) |
| `@`-binding typeahead | Available — useful for referencing application objects in the field context |
| MCP tools | Always-on tools are available by default; can be disabled per-field via `tools-disabled` attribute |
| Personal memory | Not injected by default; optionally enabled via `inject-personal-memory` attribute |
| Application context | Always injected — org terminology and standing context is relevant to field composition |
| Improvement signals | Captured and attributed to the tenant; no turn-level audit trail (ephemeral session not persisted) |

### Context injection

When the popover opens, the platform assembles a field-specific system prompt from:

1. **Tenant base prompt** — from `scope.systemPrompt` in the application config
2. **Application context** — `[Application context]` block, always injected
3. **Field context block** — assembled from the component attributes:

```
[Field context]
Field: {{field-label}}
Current value: {{field-value}} (if provided and non-empty)
Form context: {{field-context}} (if provided)
Task: Help the user compose or refine the content for this field.
```

4. **Platform-managed instructions** — write-back guidance (if enabled), tool transparency, injection mitigation

The field context block keeps the model tightly focused on the field's purpose. The model does not reference other conversations or memory items not explicitly injected.

### Write-back behaviour

When `write-back` is configured for a field, a **write-back bar** appears at the bottom of the popover after each assistant response that contains renderable text content.

| Control | Behaviour |
|---------|----------|
| **Insert into field** | Fires the `field-insert` event with the response content. The host application handles this event to update the field value. |
| **Copy** | Copies the response text to the clipboard. No host event required. |

For multi-turn field sessions, the write-back bar always shows the most recent response. Earlier responses can be copied by selecting text directly in the popover.

Write-back format is configurable per field:

| Format | Use case |
|--------|---------|
| `plain` (default) | Standard text fields, input fields |
| `markdown` | Rich text editors that accept markdown |
| `html` | WYSIWYG editors |
| `json` | Structured data fields |

### Web component

Two component variants are provided:

**Variant A — Wrapper** (component wraps the field element)

```html
<ai-chat-field
  tenant-id="acme-corp"
  user-token="..."
  field-label="Product Description"
  field-context="Help the user write a compelling product description for an e-commerce listing. Focus on benefits, not features."
  write-back="true"
  write-back-format="plain"
  trigger="inline"
>
  <textarea name="description" rows="4"></textarea>
</ai-chat-field>
```

**Variant B — Standalone trigger** (component placed near the field)

```html
<textarea id="desc-field" name="description" rows="4"></textarea>
<ai-chat-field
  tenant-id="acme-corp"
  user-token="..."
  field-label="Product Description"
  field-context="Help the user write a compelling product description."
  field-target="#desc-field"
  write-back="true"
  trigger="button"
  trigger-label="AI assist"
></ai-chat-field>
```

#### `<ai-chat-field>` attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `tenant-id` | Yes | Tenant identifier |
| `user-token` | Yes | Host-authenticated user JWT |
| `field-label` | Yes | The field's label — shown in the popover header and injected as field context |
| `field-context` | No | A plain-language description of what this field is for and how the assistant should help. Injected into the field context block. |
| `field-value` | No | The field's current value, passed by the host for editing assistance. Injected into the field context block. If omitted, the component reads the value from the wrapped field element (Variant A only). |
| `write-back` | No | `"true"` enables the write-back bar. Default: `"false"`. |
| `write-back-format` | No | `"plain"` \| `"markdown"` \| `"html"` \| `"json"`. Default: `"plain"`. |
| `trigger` | No | `"inline"` — icon inside the field; `"button"` — external button. Default: `"inline"`. |
| `trigger-label` | No | Button label text when `trigger="button"`. Default: `"AI assist"`. |
| `field-target` | No | CSS selector for the target field element (Variant B). |
| `tools-disabled` | No | `"true"` disables always-on MCP tools for this field session. Useful for simple text-generation fields that don't need live data. Default: `"false"`. |
| `inject-personal-memory` | No | `"true"` injects the user's personal memory into the field session. Useful for fields where personal preferences or role context are relevant. Default: `"false"`. |
| `placeholder-prompt` | No | Pre-filled text shown in the input field on first open (e.g. `"Describe this product in 2–3 sentences"`). Helps orient the user. |

#### `<ai-chat-field>` events

| Event | Detail payload | Description |
|-------|---------------|-------------|
| `field-insert` | `{ fieldLabel, content, format }` | Fired when user clicks "Insert into field". Host updates the field value using `content`. |
| `field-copy` | `{ fieldLabel, content }` | Fired when user clicks "Copy" |
| `field-opened` | `{ fieldLabel }` | Fired when the popover opens |
| `field-closed` | `{ fieldLabel, messageCount }` | Fired when the popover closes |
| `token-expired` | — | Identical to other component variants — host refreshes via `updateToken()` |

#### `<ai-chat-field>` JavaScript API

| Method | Description |
|--------|-------------|
| `open()` | Programmatically open the popover |
| `close()` | Programmatically close and discard the session |
| `updateToken(token)` | Refresh the user JWT — same as other components |
| `setFieldValue(value)` | Update the `field-value` context without reopening the popover |

### Handling `field-insert`

```javascript
document.querySelectorAll('ai-chat-field').forEach((field) => {
  field.addEventListener('field-insert', (event) => {
    const { fieldLabel, content, format } = event.detail;
    const textarea = document.querySelector(`[data-label="${fieldLabel}"]`);
    if (textarea) {
      textarea.value = content;
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
});
```

---

## Cross-mode design decisions

| Decision | Rationale |
|----------|-----------|
| Modes 1 and 2 share conversation history | Both are persistent conversation modes accessing the same user session and tenant. There is no "page-specific" conversation context in these modes — the user's conversations belong to them, not to a page. |
| Mode 3 is entirely ephemeral | Form field interactions are transactional. The user wants help completing a specific field right now. Persisting these as conversations would pollute the history with low-value threads and create privacy/audit implications for draft field values. |
| Mode 3 does not escalate to Modes 1 or 2 | The form field context is scoped to a specific field instance at a specific moment. It would not be useful as a persistent thread — the field context would be stale, and the user's goal (filling the field) would already be complete. |
| Application context is injected in Mode 3 | Org terminology, standing guidance, and governance decisions are just as relevant when composing field content as in a full conversation. Omitting them would cause inconsistent terminology in AI-generated field values. |
| Personal memory is opt-in in Mode 3 | Personal memory may contain preferences relevant to some fields (e.g. writing style, role context for approvals). But for most fields it adds unnecessary token overhead. The host decides per field. |
| Always-on MCP tools available in Mode 3 by default | Some fields benefit from live data access (e.g. a "domain owner" field might benefit from the governance MCP). Host can disable per field if not needed. |
| Write-back requires host event handling | The platform does not manipulate the DOM directly — it fires events and the host application updates its own fields. This keeps the component framework-agnostic and respects the host's form state management. |

---

## Summary: which component to use

| Scenario | Component |
|----------|-----------|
| Provide assistant access from anywhere in the app without navigation | `<ai-chat-widget>` (Mode 1) |
| Build a dedicated assistant page or embed a full assistant panel | `<ai-chat>` (Mode 2) |
| Add contextual AI assistance to individual form fields | `<ai-chat-field>` (Mode 3) |
| All three simultaneously | All three components can coexist — they share the same auth and platform backend |
