# 09 — Interaction Design

## Component structure

The AI Chat Platform is delivered as an `<ai-chat>` web component that host applications embed within their own UI. The component owns a **three-zone layout** inside its mounting point. The host application retains full ownership of its own navigation, header, and surrounding UI — the component does not attempt to replace or extend the host UI beyond its mounting point.

| Zone | Location within component | Contents |
|------|--------------------------|---------|
| **History panel** | Left sidebar | Conversation list — **My Conversations** and **Shared With Me** (reverse-chronological); conversation search; pinned conversations; new conversation button; workflow library access |
| **Conversation area** | Centre — primary | Message thread, streaming responses, rendered content, input area |
| **Conversation panel** | Right sidebar | **Canvas** (active when a document is open for iteration); attachments and artefacts; participant list and share management; session token summary |

### Desktop layout (≥ 1280px)

```
┌─────────────────────────────────────────────────────────────┐
│                    <ai-chat> component                       │
├─────────────┬───────────────────────────┬────────────────────┤
│ History     │                           │ Conversation panel │
│             │    Conversation area      │                    │
│ [🔍 Search]│                           │ Canvas  Artefacts  │
│             │  ┌─────────────────────┐  │ Participants    ∑  │
│ ▾ My Convs │  │ 🔧 Tool call card   │  ├────────────────────┤
│   — Today   │  └─────────────────────┘  │                    │
│   Conv 1    │  ┌─────────────────────┐  │  [Active canvas    │
│   Conv 2    │  │ Assistant response  │  │   or artefact      │
│   — Yesterday│  │ [👍][👎][↻][⎘]  │  │   panel content]   │
│   Conv 3    │  └─────────────────────┘  │                    │
│             │                           │ — Artefacts —      │
│ ▾ Shared   │  ┌─────────────────────┐  │  📄 report.pdf     │
│   Conv A    │  │ User message bubble │  │  📊 chart.xlsx     │
│             │  └─────────────────────┘  │                    │
│ [Workflows] ├───────────────────────────┤  14 turns · 18 k  │
│             │ 📎 ⚙ [✦ Standard][→]   │                    │
└─────────────┴───────────────────────────┴────────────────────┘
```

### Why three zones (not four)

The platform component owns three zones inside its mounting point. The host application manages its own navigation independently — the `<ai-chat>` component occupies its mounting point only, making it embeddable anywhere in the host layout: a full page, a side panel, or a modal drawer.

### History panel

```
┌──────────────────────────┐
│ My Conversations    [+ ] │  ← New conversation
├──────────────────────────┤
│ [🔍 Search conversations]│
├──────────────────────────┤
│ 📌 Pinned                │
│   Q2 Governance Review   │
├──────────────────────────┤
│ Today                    │
│ ▶ Finance domain audit   │  ← Active (highlighted)
│   Onboarding checklist   │
├──────────────────────────┤
│ Yesterday                │
│   Payment service SLOs   │
│   Team standup recap     │
├──────────────────────────┤
│ Past 7 days              │
│   Policy gap analysis    │
├──────────────────────────┤
│ Past 30 days             │
│   Data quality review    │
├──────────────────────────┤
│ Shared With Me           │
│   Team review session ③  │  ← Unread badge
├──────────────────────────┤
│ [⚡ Workflows]           │
└──────────────────────────┘
```

### Workflow Library

The Workflow Library is accessible via a **Workflows** button in the history panel header. It slides in as a panel over the history list — it is not part of the right sidebar, which is reserved for conversation-specific content.

When clicked, a workflow from the library opens a parameter form (if the workflow has parameters) before injecting the prompt into the input field.

```
┌──────────────────────────────────────┐
│ ⚡ Workflow Library          [ × ]   │
├──────────────────────────────────────┤
│ [🔍 Search workflows…]               │
├──────────────────────────────────────┤
│ ⚡ Governance Health Check           │
│   Summarise coverage and quality     │
│   gaps across a selected domain. [→] │
├──────────────────────────────────────┤
│ 📅 Weekly Status Report              │
│   Generate a plain-language weekly   │
│   summary for a team.           [→]  │
├──────────────────────────────────────┤
│ 📋 Policy Compliance Scan            │
│   Review entities against active     │
│   policies.                     [→]  │
└──────────────────────────────────────┘
```

Selecting a workflow with parameters opens a parameter form before launch:

```
┌──────────────────────────────────────┐
│ ← Governance Health Check            │
├──────────────────────────────────────┤
│ Summarise governance coverage,       │
│ quality gaps, and policy compliance  │
│ across a selected domain.            │
├──────────────────────────────────────┤
│ Data Domain *                        │
│ ┌──────────────────────────────────┐ │
│ │ @{Finance Domain}              × │ │  ← @-binding typeahead
│ └──────────────────────────────────┘ │
├──────────────────────────────────────┤
│             [Launch workflow →]      │
└──────────────────────────────────────┘
```

### Conversation panel (right sidebar) detail

The right panel is scoped entirely to the **active conversation** and switches between two primary modes via a tab strip at the top:

| Tab | Contents | When active |
|-----|---------|-------------|
| **Canvas** | The active working document — editable, versioned, iteratable | Whenever a canvas document is open in the conversation |
| **Attachments & Artefacts** | All input documents and output artefacts in submission order | Always available |
| **Participants** | Participant list (shared conversations); invite control; leave / remove actions | Always available |
| **Session summary** | Running token totals (`14 turns · 18,430 tokens`) with tooltip expanding to input / output / cached breakdown | Always available |

When a canvas document is opened, the panel automatically switches to the **Canvas** tab. Switching to another tab does not close the canvas — the document remains active and the model retains its context.

---

## Responsive and mobile design

Mobile-first and responsive layout is a core platform standard. The following covers layout behaviour at each breakpoint when the component is mounted at full-page width.

| Viewport | Layout |
|----------|--------|
| Desktop (≥ 1280px) | Full three-zone layout — history panel + conversation area + conversation panel |
| Desktop narrow (1024px – 1279px) | History panel collapses to icon-only rail; conversation panel remains |
| Tablet (768px – 1023px) | Both panels become slide-in drawers; conversation area is primary |
| Mobile (< 768px) | Single-column; history and conversation panels as bottom-sheet drawers; input pinned to bottom |

When the component is mounted in a constrained container (e.g. a side panel or modal), it uses the container width rather than viewport width to determine layout breakpoints. See [16-embedding-and-web-component.md](./16-embedding-and-web-component.md) for container sizing guidance.

### Narrow desktop layout (1024px – 1279px)

The history panel collapses to an icon-only rail. Hovering an icon reveals its label tooltip; clicking a conversation icon opens it.

```
┌─────────────────────────────────────────────────────────────┐
│                    <ai-chat> component                       │
├──────┬────────────────────────────────┬──────────────────────┤
│  ☰   │                                │ Conversation panel   │
│  🔍  │     Conversation area          │                      │
│  ─── │                                │ Canvas  Artefacts    │
│  ●   │  ┌──────────────────────────┐  │ Participants    ∑    │
│  ●   │  │ Assistant response       │  ├──────────────────────┤
│  ─── │  │ [👍][👎][↻][⎘]         │  │                      │
│  ●   │  └──────────────────────────┘  │  [Panel content]     │
│  ─── │  ┌──────────────────────────┐  │                      │
│  ●   │  │ User message             │  │                      │
│  ─── ├──────────────────────────────────┤                    │
│  ⚡  │ 📎 ⚙ [✦ Standard][input][→]│                      │
└──────┴──────────────────────────────────┴──────────────────────┘
     Icon rail — hover to label, click to expand
```

### Tablet layout (768px – 1023px)

Both panels become slide-in drawers triggered by header buttons. The conversation area is the primary view.

```
┌──────────────────────────────────────────────────┐
│                <ai-chat> component                │
├──────────────────────────────────────────────────┤
│  [☰ History]                      [⊞ Panel]     │  ← Drawer triggers in header
├──────────────────────────────────────────────────┤
│                                                  │
│         Conversation area                        │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │ Assistant response                         │  │
│  │ [👍][👎][↻][⎘]                           │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │ User message bubble                        │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
├──────────────────────────────────────────────────┤
│ 📎 ⚙ [✦ Standard]  [input…]             [→]    │
└──────────────────────────────────────────────────┘
  Slide-in drawers — swipe from edge or tap header button
```

### Mobile layout (< 768px)

Single-column; history and conversation panels as full-height bottom-sheet drawers; input pinned to bottom of screen above the keyboard.

```
┌────────────────────────────────────────┐
│           <ai-chat> component          │
├────────────────────────────────────────┤
│                                        │
│       Conversation area                │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │ Assistant response               │  │
│  │ [👍][👎][↻][⎘]                 │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │              User message        │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌────────────────────────────────┐    │
│  │ Jump to latest ↓               │    │  ← Anchored above input when scrolled
│  └────────────────────────────────┘    │
├────────────────────────────────────────┤
│ 📎 ⚙ ✦ Standard   [input…]     [→]   │  ← Pinned above keyboard
└────────────────────────────────────────┘
  ← swipe right: history panel (bottom sheet)
  ← swipe left:  conversation panel (bottom sheet)
```

### Mobile-specific requirements

| Requirement | Specification |
|-------------|--------------|
| Input controls | All controls (attachment, tool selection, model chip, send/stop) are thumb-reachable — no controls hidden behind secondary menus on mobile |
| `@`-binding typeahead | Anchors to the bottom of the viewport (not cursor position); sized so the top edge is visible above the raised keyboard |
| Mermaid diagrams | Horizontally scrollable — never scaled to illegibility |
| Vega-Lite charts | `width: "container"` for responsive sizing |
| Data tables | Horizontally scrollable; first column is sticky |
| Conversation panel | Opens as full-height bottom sheet — accessible via a tray icon in the input area footer |
| History panel | Opens as full-height bottom sheet — accessible via a history button |
| Conversation search | Opens as full-screen overlay with keyboard raised |
| Touch targets | Minimum 44 × 44 px (Apple HIG / Material Design) |

### Input area on mobile

The input toolbar presents all controls in a **single row above the text field**, within thumb reach. When horizontal space is tight, secondary controls (model chip, profile indicator) collapse behind an overflow icon — the paperclip (attachment) and send/stop button are **never** moved to overflow.

| Control | Mobile behaviour |
|---------|----------------|
| Paperclip / attachment | Opens the native mobile file picker (camera roll, Files app, camera capture) |
| Tool selection | Opens a full-screen bottom sheet listing available MCP tools |
| Model chip | Opens a bottom sheet listing allowed models |
| Text input | Grows to 3 lines maximum on mobile (vs. 5 on desktop) |
| Submit | Large dedicated tap target — always visible |

### Keyboard and viewport behaviour

When the software keyboard raises on mobile, the conversation thread scrolls to keep the latest turn visible above the input area. The input area stays pinned to the top of the keyboard. The `@`-binding typeahead panel appears above the keyboard.

### Hover states on mobile

| Desktop (hover) | Mobile equivalent |
|----------------|-----------------|
| Report icon appears on hover over a turn | Always visible below each turn |
| Edit icon appears on hover over a user message | Always visible below each user message |
| Assistant response action row appears on hover | Always visible below each assistant response |
| Metadata line appears on hover | Tap the response bubble to reveal; tap again to hide |

### Gestures

| Gesture | Action |
|---------|--------|
| Swipe right from left edge | Opens the history panel bottom sheet |
| Swipe left from right edge | Opens the conversation panel bottom sheet |
| Long press on a user message | Opens message action menu (edit, report, copy) |
| Long press on an assistant response | Opens response action menu (copy, report, regenerate) |
| Tap a binding chip | Fires `binding-click` event to the host application |
| Pinch-to-zoom on a Mermaid diagram | Enters full-screen diagram view |

---

## Conversation thread anatomy

### User messages

- Appear immediately in the conversation thread on submit (**optimistic UI**) — the message is visible before the API acknowledges receipt. If the send fails, the message is styled as failed with an inline retry control.
- Right-aligned in a muted bubble
- `@`-binding chips render as interactive pills within the bubble
- In shared conversations: author's name and avatar above the bubble

### Other participants' messages (shared conversations only)

- Left-aligned
- Distinct colour per participant (derived from host primary brand colour)
- Author name and avatar above the bubble

### Message timestamps

Every message in the conversation thread carries a **timestamp**.

| Display rule | Format |
|-------------|--------|
| Default | Relative: *"Just now"*, *"3 min ago"*, *"Yesterday"*, *"Mon 09:14"* |
| Hover (desktop) | Absolute: *"Monday 11 May 2026, 09:14:32"* |
| Older than 7 days | Absolute date always shown: *"4 May, 09:14"* |

Timestamps are shown below each message bubble (user and assistant). They are not shown during active streaming — the timestamp appears when streaming completes.

### Thinking indicator

After the user submits a message and before the first streaming token arrives, the assistant displays a **thinking indicator** in the conversation thread:

```
[AssistantName] is thinking…   ●●●
```

An animated three-dot pulse appears beneath a placeholder response bubble. The indicator is replaced immediately by the first streaming token. If the model is queuing tool calls before generating prose, the thinking indicator transitions to the tool call disclosure card (in-progress state) without a gap.

The thinking indicator is suppressed if the model begins streaming within 300 ms of submission.

### Full thread anatomy

A complete exchange showing all thread elements in sequence:

```
┌──────────────────────────────────────────────────────────┐
│                    Conversation area                      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Show me the governance health for @{Finance       │  │  ← User message bubble
│  │  Domain}                                           │  │    (right-aligned)
│  │                                     Just now  🕐  │  │  ← Timestamp
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Atlas is thinking…   ● ● ●                              │  ← Thinking indicator
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ 🔧 Governance Platform · get_domain_health  ✓ ▼ │    │  ← Tool call disclosure
│  └──────────────────────────────────────────────────┘    │    (collapsed)
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ The Finance Domain is in **good health** overall.  │  │  ← Assistant response
│  │                                                    │  │
│  │ | Metric          | Status   |                     │  │
│  │ | Coverage        | 94 %     |                     │  │
│  │ | Quality score   | 87 / 100 |                     │  │
│  │ | Open issues     | 3        |                     │  │
│  │                                                    │  │
│  │ ¹ Governance Platform · get_domain_health          │  │  ← Inline source citation
│  │                                                    │  │
│  │ ✦ Standard · 1,240 tokens · 3 min ago             │  │  ← Metadata (hover/tap)
│  │ [👍] [👎] [↻ Regenerate] [⎘ Copy]               │  │  ← Feedback row
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  · What are the open quality issues?                     │  ← Suggested follow-ups
│  · Who owns the Finance domain?                          │
│  · Show me a breakdown by sub-domain                     │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  📎  ⚙  [✦ Standard]  [input…]                   [→]   │
└──────────────────────────────────────────────────────────┘
```

### Per-turn feedback

**User messages** carry a **report icon** (visible on hover / always visible on mobile). Clicking opens the report dialog:

> **What's wrong with this?**  
> [Text field — optional explanation]  
> [Submit report] &nbsp;&nbsp; [Cancel]

On submit, an improvement signal is captured against the specific turn (see [12-continuous-improvement.md](./12-continuous-improvement.md)).

**Assistant responses** carry a feedback row with three controls:

| Control | Desktop | Mobile | Action |
|---------|---------|--------|--------|
| 👍 Thumbs up | Appears on hover | Always visible below the response | Records a positive improvement signal against the turn. One-click — no dialog. Fills on selection; toggleable. |
| 👎 Thumbs down | Appears on hover | Always visible below the response | Opens the report dialog (same as user message report). Records a negative signal on submit. |
| Regenerate | Appears on hover | Always visible below the response | Creates a new branch from this turn (see doc 04). |
| Copy full response | Appears on hover | Always visible below the response | Copies the full response text to clipboard. |

Both thumbs signals feed the improvement pipeline (doc 12). Thumbs up signals are used to identify high-quality turns for reference; thumbs down signals trigger the same improvement signal workflow as the explicit report.

### Assistant responses

Each assistant response carries:

| Element | Desktop | Mobile |
|---------|---------|--------|
| Metadata line | Appears on hover — model label + token counts + (in shared sessions) submitting user's name | Revealed on tap of the response bubble |
| Feedback row (👍 👎 Regenerate Copy) | Appears on hover | Always visible below the response |
| Artefact chips | *"Added to artefacts ↗"* beneath each generated block | Same |

### Suggested follow-ups

At the end of each assistant response, up to **three suggested follow-up queries** are presented as pill chips generated by the model. Single-click to submit. Follow-ups are model-generated — not from a static list.

---

## Input area controls

| Control | Function |
|---------|---------|
| Paperclip icon | Opens file picker or accepts drag-and-drop (PDF, Excel, Word, images); images also accepted via clipboard paste |
| Tool selection icon | Opens MCP tool opt-in panel |
| Active model chip | Opens model selection popover |
| Text input | Multi-line, grows to 5 lines, `Cmd/Ctrl + Enter` to submit |
| Profile indicator | Read-only `Style · Verbosity` link to host app profile settings — clickable |
| Send / Stop | Submits message or stops active stream |
| Share icon | Opens participant management panel |

### Input area layout

```
┌──────────────────────────────────────────────────────────┐
│  @{Finance Domain} What are the quality gaps in this     │  ← Text input
│  domain? Any open ownership issues?                      │    (grows to 5 lines)
├──────────────────────────────────────────────────────────┤
│ 📎  ⚙  [✦ Standard]  [Technical · Concise]  [⇪]  [→]  │  ← Controls row
└──────────────────────────────────────────────────────────┘
  📎 Attachment        — file picker / drag-and-drop / clipboard paste
  ⚙  Tool selection   — opens MCP tool opt-in panel (see below)
  ✦ Standard          — model tier chip; opens model selection popover
  Technical · Concise — profile indicator (style · verbosity); read-only link
  ⇪  Share            — opens participant management panel
  →  Send / Stop      — always visible; submits or stops active stream
```

While streaming, the input field is disabled and the Send button becomes a Stop button:

```
┌──────────────────────────────────────────────────────────┐
│  [input disabled while streaming]                        │
├──────────────────────────────────────────────────────────┤
│ 📎  ⚙  [✦ Standard]  [Technical · Concise]  [⇪]  [■]  │  ← ■ Stop
└──────────────────────────────────────────────────────────┘
```

### Tool selection panel

Opened via the ⚙ icon in the input area:

```
┌──────────────────────────────────────┐
│ Tools                         [ × ]  │
├──────────────────────────────────────┤
│ Always active                        │
│                                      │
│  ● Governance Platform               │
│    Entities, quality, policies       │
│    [Always on — cannot be disabled]  │
├──────────────────────────────────────┤
│ Available for this session           │
│                                      │
│  ○ Data Warehouse        [Enable →]  │
│    Read-only warehouse access        │
│                                      │
│  ○ Web Search            [Enable →]  │
│    Real-time web results             │
│                                      │
│  ○ Platform Resources    [Enable →]  │
│    Shared skills and templates       │
└──────────────────────────────────────┘
  Enabled tools are active for this session only.
  Settings reset on the next session.
```

---

## Session artefact tray

The artefact tray accumulates every input and output artefact produced during a conversation. It persists for the full lifetime of the conversation record.

### Artefact classes

| Class | Direction | Examples |
|-------|-----------|---------|
| Attached document | Input | PDF report, Excel extract, Word document |
| Generated document | Output | Markdown report, summary |
| Mermaid diagram | Output | Relationship diagram, flow, sequence |
| Vega-Lite chart | Output | Bar chart, trend line, distribution |
| Data table | Output | Multi-row query result (CSV) |
| JSON export | Output | Tool result or entity record |
| Code block | Output | SQL, Python, YAML, shell |
| Binding reference | Input | Non-downloadable — reference card linking to the host application object |

### Tray entry anatomy

Each tray entry shows:
- Format icon
- Auto-generated name: `[Content type] — [Subject] — [Date]`
- Turn back-link (click to jump to the source turn)
- Direction label (Input / Output)
- Download button
- Preview link

Users may **rename** tray entries. A **"Download all"** control packages all artefacts as a zip archive.

Canvas documents in the artefact tray carry an additional **"Open in canvas"** action that re-opens the document in the canvas panel for further editing, regardless of which turn produced it.

---

## Document canvas

The canvas is the platform's working-document surface — a persistent, editable panel where the model and user collaborate iteratively on a document across multiple turns, rather than treating each AI response as a disposable message.

### What opens in canvas

The model uses a ` ```document ` fenced block to produce canvas-eligible output. The platform's non-overridable system prompt layer instructs the model to use `document` blocks for substantial, document-like prose outputs — reports, summaries, plans, policy drafts, specifications, structured analyses — where the user is likely to want to refine rather than simply read and move on.

Non-prose outputs (Mermaid diagrams, Vega-Lite charts, data tables, code blocks, JSON) remain as inline thread content and artefact tray entries. They do not open in canvas.

Users may also manually promote any text artefact in the tray to canvas by clicking **"Open in canvas"** on that tray entry.

### Canvas panel layout

```
┌─────────────────────────────────────────┐
│ [Document title — editable]    v3  [ ↗ ]│  ← Header: title + version + full-screen
├───────────────────────────────────────┬─┤
│ [Toolbar: Edit | Copy | Download]     │ │
├───────────────────────────────────────┤ │
│                                       │ │
│  The canvas document content renders  │ │
│  here as styled markdown. In Edit     │ │
│  mode, becomes a live text editor.    │ │
│                                       │ │
│                                       │ │
└───────────────────────────────────────┴─┘
```

| Element | Behaviour |
|---------|----------|
| **Document title** | Auto-generated from document content; editable inline by clicking |
| **Version indicator** | Shows current version (v1, v2 …); clicking opens a version history dropdown listing every model-generated and user-edited version with timestamp. Selecting a prior version restores it as a new version (no destructive overwrites). |
| **Full-screen toggle** | Expands canvas to fill the component mount point; the conversation area collapses to a narrow strip. Second click restores the split layout. |

### Canvas full-screen layout

```
┌───────────────────────────────────────────────────────────────┐
│                      <ai-chat> component                       │
├────────────────────────────────────────────────────────┬───────┤
│ [Document title — editable]     v3  [Edit][Copy][↙]×  │ [msg] │
├────────────────────────────────────────────────────────┤  ···  │
│                                                        │ [msg] │
│   Full-width canvas document — headings, prose, and    │       │
│   tables render at full canvas width.                  │ [msg] │
│                                                        │       │
│   Section heading                                      │       │
│   ───────────────                                      │       │
│   Body text renders here with full line length.        │ [inp] │
│   | Col A | Col B |   ← tables at full width          │  [→]  │
│   | ───── | ───── |                                   │       │
│   | val 1 | val 2 |                                   │       │
│                                                        │       │
└────────────────────────────────────────────────────────┴───────┘
  ↙ collapses back to split layout    × closes canvas
```

### Canvas version history

Clicking the version indicator (e.g. **v3**) opens a dropdown listing every version of the document:

```
┌────────────────────────────────────────────┐
│ [Document title — editable]     v3   [ ↗ ] │
│                           ┌──────────────┐  │
│  [Toolbar]                │ ● v3 · 09:14 │  │  ← Current version
│                           │   Model rev. │  │
│  Document content         │   v2 · 08:52 │  │  ← User edit
│  renders here.            │   User edit  │  │
│                           │   v1 · 08:47 │  │  ← Initial output
│                           │   Initial    │  │
│                           │              │  │
│                           │ [Restore v2] │  │
│                           └──────────────┘  │
└────────────────────────────────────────────┘
  Restoring a prior version creates a new version — no destructive overwrite.
```
| **Edit mode** | Clicking **Edit** transforms the canvas from a read-only rendered view into a live markdown editor. User edits are saved immediately as a new version. Exiting edit mode re-renders the markdown. |
| **Copy** | Copies the full markdown source to the clipboard |
| **Download** | Downloads the document as `.md` (default), `.txt`, or `.pdf` (platform-rendered) |

### In-thread reference card

When the model produces a `document` block, the conversation thread shows a compact **reference card** in place of the full content:

```
┌────────────────────────────────────────┐
│ 📄  Q2 Governance Summary              │
│     Report · 1,240 words               │
│                           [Open canvas →] │
└────────────────────────────────────────┘
```

The full document is in the canvas panel — it is not rendered inline in the thread. This keeps the conversation thread scannable and avoids large content blocks interrupting the exchange.

### Model-assisted revision

When a canvas document is open, the platform automatically includes the current canvas content in the model's context:

```
[Canvas document — Q2 Governance Summary]
{full document markdown}
[End canvas document]
```

The user can ask the model to revise the document in natural language: *"Shorten the executive summary to two sentences"*, *"Add a risks section after the findings"*, *"Rewrite this in a more formal tone"*. The model responds with a new `document` block containing the full revised document, which replaces the canvas content and is saved as a new version. The model's reply in the conversation thread confirms what changed: *"Updated — shortened the executive summary and added a risks section."*

### Multiple canvases

A conversation may produce more than one canvas document. Each is a separate tab within the canvas panel, ordered by creation time. The active tab is the most recently updated document.

```
┌──────────────────────────────────────────┐
│ Q2 Governance Summary │ Risk Register  ▾ │  ← Canvas tabs (+ overflow menu)
├──────────────────────────────────────────┤
│ [Edit] [Copy] [Download]         v3 [ ↗] │
├──────────────────────────────────────────┤
│                                          │
│  Q2 Governance Summary content           │
│  (active tab)                            │
│                                          │
└──────────────────────────────────────────┘
  Switching tabs does not close the inactive canvas — both remain in context.
```

### Canvas in Mode 1 (floating widget)

The canvas panel is only available in **full state**. In the mini state, canvas documents show as reference cards in the thread with an *"Expand for canvas view ↗"* note. Transitioning to full state opens the canvas panel for the active document.

### Canvas and the artefact tray

All canvas document versions are stored in the artefact tray as versioned entries. The tray shows the latest version with a version count badge (e.g. `v4`). Individual versions are downloadable from the version history dropdown in the canvas panel.

---

## Returning user state

### Mode 2 — Inline Page (`<ai-chat>`)

When the component mounts and the authenticated user has prior conversation history, the **conversation area** shows a home state before opening any conversation. The home state is shown on the **first mount per browser session** — subsequent navigations to the page within the same session resume the last-active conversation directly.

```
┌─────────────────────────────────────────────────────────┐
│  Welcome back, [name]                                   │
│                                                         │
│  Continue where you left off:                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📄 Q2 Governance Summary   ·  2 hours ago   [→]  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Recent                                                 │
│  ├── Payment service audit          Yesterday           │
│  └── Onboarding checklist review    Monday              │
│                                                         │
│  ┌─ Unread shared activity ─────────────────────────┐  │
│  │ 📋 Team review session — 3 new messages          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [+ Start new conversation]                             │
└─────────────────────────────────────────────────────────┘
```

| Element | Specification |
|---------|--------------|
| **Continue card** | The single most recently active conversation; single click opens it directly |
| **Recent list** | Up to 2 further recent conversations; click to open |
| **Unread shared activity** | Shown only if there are unread messages in shared conversations; click to open the conversation at the first unread turn |
| **Start new conversation** | Clears to a new conversation with the onboarding welcome state (first-time) or an empty input (returning) |
| **Trigger condition** | Shown when the user has ≥ 1 prior conversation and has not interacted with the component in the current browser session |
| **Skip condition** | Not shown if the user is deep-linked to a specific conversation via the `initial-conversation-id` attribute |

### Mode 1 — Floating Widget (`<ai-chat-widget>`)

When the widget transitions from collapsed FAB to mini state for the first time in a browser session — and the user was last active more than **4 hours** ago (configurable via `widget.returningUserThreshold` in hours) — the mini panel opens to a compact returning-user card rather than resuming mid-conversation:

```
┌──────────────────────────────────────┐
│ 🤖 Atlas                 [ ↗ ] [ × ] │
├──────────────────────────────────────┤
│  Welcome back                        │
│  ┌────────────────────────────────┐  │
│  │ Continue: Q2 Governance…  [→]  │  │
│  └────────────────────────────────┘  │
│  [📋 3 unread in Team review]        │
│  [+ New conversation]                │
├──────────────────────────────────────┤
│  [input…]                      [→]   │
└──────────────────────────────────────┘
```

The card auto-dismisses when the user clicks any option or starts typing in the input field. If the threshold has not been exceeded (recent session), the widget opens directly into the last conversation.

---

## Onboarding state

On **first visit**, the conversation area shows a welcome state drawn from the host application config:

1. The host-configured `identity.assistantDescription`
2. Starter workflows from `features.starterWorkflows` (up to 3, shown as question-style prompts)
3. Starter questions from `features.starterQuestions` (up to 3, if no starter workflows or alongside them)
4. A link to the full Workflow Library

The onboarding state is shown once per user — it is not shown again once the user has started a conversation.

---

## Error and boundary states

| State | Presentation | User action |
|-------|-------------|------------|
| Model timeout | Inline error card with retry button | Retry re-submits the last message |
| Send failure (network) | Failed user message styled with error colour + inline retry icon | Tap/click retry to resend |
| Connection lost | Non-blocking banner below the conversation header: *"Connection lost — reconnecting…"*; animated reconnect indicator. Banner updates to *"Reconnected"* (auto-dismisses after 3s) on restore. | Wait; drafts are preserved locally |
| MCP tool failure | Tool call disclosure shows error status and raw detail | Rephrase or copy error to report |
| Always-on MCP server unavailable | Degraded-mode banner; session continues in text-only mode | Model answers from system prompt context only |
| Opt-in MCP server unavailable | Error in tool call disclosure | Disable the failing server for the session |
| Context window limit (80%) | Subtle warning in conversation header | Branch to new thread or accept auto-summarisation |
| Out-of-scope query | Model explains scope boundary and suggests reformulation | No error state — graceful redirect |
| Auth session expired | Modal overlay prompting re-authentication | Re-auth restores session and full conversation history |
| Unsupported file type | Inline notice on file selection | User prompted to use a supported format |
| Last participant constraint | Tooltip on disabled Leave/Remove controls | Invite another user before leaving |
| Component mount failure | Error state within the component mount point | Host application is notified via the `error` event |

### Error state layouts

**Connection lost — non-blocking banner:**

```
┌──────────────────────────────────────────────────────────┐
│ ⚠ Connection lost — reconnecting…  ◌ ◌ ◌               │  ← Banner below header
├──────────────────────────────────────────────────────────┤
│                                                          │
│   [conversation thread — still readable]                 │
│   Input disabled until reconnected                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
  Banner updates to "✓ Reconnected" and auto-dismisses after 3 seconds.
```

**Always-on MCP server unavailable — degraded-mode banner:**

```
┌──────────────────────────────────────────────────────────┐
│ ⚠ Governance Platform is unavailable. Atlas is answering │
│   from its own knowledge only — data may not reflect     │
│   the current state of your application.                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   [conversation thread — text-only mode]                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
  Persistent until connectivity is restored.
```

**Auth session expired — blocking modal:**

```
┌──────────────────────────────────────────────────────────┐
│           Session expired                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Please sign in again to continue. Your conversation     │
│  history is preserved and will be restored on sign-in.   │
│                                                          │
│                    [Sign in again]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
  Full-viewport modal — no interaction behind it.
```

**Send failure — inline retry on user message:**

```
  ┌────────────────────────────────────────────────────┐
  │ What are the quality gaps in the Finance domain?   │
  │ ⚠ Failed to send  [↺ Retry]                       │  ← Inline retry
  └────────────────────────────────────────────────────┘
```

**Context window warning (80% threshold) — subtle header indicator:**

```
┌──────────────────────────────────────────────────────────┐
│ Atlas                    ⚠ Long conversation — 83% full  │  ← Header indicator
│                          [Branch to new thread]          │
├──────────────────────────────────────────────────────────┤
```

---

## Accessibility

WCAG 2.1 AA compliance is a platform requirement. The following are platform-specific additions.

| Requirement | Specification |
|-------------|--------------|
| Mermaid SVG alt text | Descriptive alt text generated by the model for each Mermaid diagram |
| Conversation thread live region | The thread is an `aria-live` region — streaming responses and new shared conversation messages are announced to screen readers |
| `@`-binding typeahead | Fully keyboard-navigable (arrow keys, Enter/Tab to select, Escape to dismiss); focus returns to input field on selection or dismissal |
| Branding token contrast | Platform validates that host-provided colour tokens meet WCAG 2.1 AA contrast ratios at config submission |
| `prefers-reduced-motion` | When the OS-level reduced motion preference is active: streaming text renders immediately (no character-by-character animation); panel slide transitions are instant; the thinking indicator uses a static label instead of the animated three-dot pulse; the FAB pulse animation on stream-in-progress is suppressed; Mermaid and Vega-Lite render-in animations are disabled |
| Focus management | When a shared conversation message arrives, focus is not stolen from the input field. The unread badge and "Jump to latest" button are announced via the live region. Focus only moves to new content on explicit user action. |
| Modal focus trap | All modal overlays (full widget state, diagram full-screen, write confirmation) implement a focus trap — Tab cycles only within the modal; Escape dismisses |

---

## Jump to latest

When a user has scrolled up and new content arrives (streaming response or shared conversation message), a **"Jump to latest ↓"** pill button appears anchored above the input field. Clicking it scrolls immediately to the most recent turn. The button disappears when the user is already at the bottom.

---

## Keyboard shortcuts

The shortcut reference overlay (triggered by `?` or `Cmd/Ctrl + /`):

```
┌──────────────────────────────────────────────┐
│ Keyboard shortcuts                    [ × ]  │
├──────────────────────────────────────────────┤
│ Cmd/Ctrl + Enter     Submit message          │
│ Cmd/Ctrl + K         Cross-conversation search│
│ Cmd/Ctrl + F         In-conversation search  │
│ Cmd/Ctrl + N         New conversation        │
│ ↑  (empty input)     Edit last user message  │
│ Escape               Dismiss / cancel edit   │
│ Cmd/Ctrl + Shift + C Copy last response      │
│ ?  /  Cmd/Ctrl + /   This shortcut list      │
└──────────────────────────────────────────────┘
```

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + Enter` | Submit message |
| `Cmd/Ctrl + K` | Open cross-conversation search |
| `Cmd/Ctrl + F` | Open in-conversation search |
| `Cmd/Ctrl + N` | Start a new conversation |
| `Escape` | Cancel edit / dismiss typeahead / close modal |
| `↑` in empty input | Edit most recent user message |
| `Arrow keys` | Navigate `@`-binding typeahead; navigate search results |
| `Enter` / `Tab` | Select item in `@`-binding typeahead |
| `Cmd/Ctrl + Shift + C` | Copy most recent assistant response to clipboard |
| `?` or `Cmd/Ctrl + /` | Show keyboard shortcut reference |

---

## Post-session CSAT prompt

A **1–5 star rating prompt** is shown to a random sample of users (configured via `features.csatSampleRate`) at the end of a session, after 30 seconds of idle time following the last assistant response.

The prompt appears as a **non-blocking floating card** anchored to the bottom-right of the conversation area:

```
                          ┌────────────────────────────┐
                          │ How useful was this        │
                          │ conversation?              │
                          │                            │
                          │  ★  ★  ★  ★  ☆            │
                          │                            │
                          │ [What could be better?…]   │
                          │                            │
                          │   [Submit]       [Skip]    │
                          └────────────────────────────┘
```

> **How useful was this conversation?**  
> ★ ★ ★ ★ ★  
> [Optional: What could be better? — single text line]  
> [Submit] &nbsp;&nbsp; [Skip]

- Non-blocking — does not prevent input
- Dismissible (Skip or click outside)
- Skipping is not counted as a negative signal
- On mobile: appears as a bottom sheet centred in the viewport

The rating and optional comment are stored in `assistant.conversations.csat_score` and `assistant.conversations.csat_comment`.
