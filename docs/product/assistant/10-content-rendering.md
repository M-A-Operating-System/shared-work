# 10 — Content Rendering

## Rendering decision rules

The rendering engine evaluates each content block in an assistant response in priority order. **The first matching rule wins.**

| Priority | Trigger | Rendered as |
|----------|---------|------------|
| 1 | Tool call event (`mcp_tool_use` / `mcp_tool_result`) | **Tool Call Disclosure** card |
| 2 | Fenced block tag matching a registered host renderer (`renderers[].trigger`) | **Custom host renderer** — host-provided ES module; see below |
| 3 | Fenced block tagged ` ```mermaid ` | **Mermaid diagram** — SVG, expandable, exportable |
| 4 | Fenced block tagged ` ```vega-lite ` | **Vega-Lite chart** — interactive, responsive |
| 5 | Fenced block tagged ` ```math ` or `$$...$$` display block | **Math expression** — KaTeX rendered display block |
| 6 | Fenced block tagged ` ```json ` | **JSON inspector** — collapsible tree, copy-to-clipboard |
| 7 | Fenced block tagged ` ```csv ` or ` ```table ` | **Data table** — sortable, filterable, paginated, CSV export |
| 8 | Any other fenced block | **Syntax-highlighted code** — Prism, copy-to-clipboard, line numbers > 5 lines |
| 9 | Inline `$...$` within prose | **Inline math** — KaTeX rendered inline |
| 10 | All other content | **Rich markdown prose** — GFM |

The system prompt (injected by the platform) instructs the model to prefer structured outputs — Vega-Lite for metrics and trends, Mermaid for relationships and flows, data tables for entity lists — over prose equivalents when the data supports it.

---

## Content type reference

| Content type | Trigger | Typical use cases |
|-------------|---------|------------------|
| Prose / markdown | Default | Explanations, summaries, narrative answers |
| Custom host renderer | Registered `trigger` tag | Host-defined domain-specific visualisations (risk gauges, compliance scorecards, Gantt views, org charts) |
| Mermaid diagram | ` ```mermaid ` | Entity relationships, process flows, system dependencies, hierarchies |
| Vega-Lite chart | ` ```vega-lite ` | Metrics, trends, distributions, comparisons |
| Math expression | ` ```math ` / `$$...$$` / `$...$` | Scoring formulas, ratios, statistical expressions, metric definitions |
| JSON inspector | ` ```json ` | Raw tool results, configuration objects, structured data |
| Data table | ` ```csv ` / ` ```table ` | Multi-row query results, lists, comparison tables |
| Tool call disclosure | Automatic | All MCP tool invocations — always visible, collapsed by default |
| Syntax code | All other fenced blocks | SQL, Python, YAML, shell, TypeScript |

---

## Custom host renderers

Host applications may register custom content renderers in the `renderers` section of their application config (see [00-host-application-config.md](./00-host-application-config.md)). When the model produces a fenced block tagged with a registered `trigger`, the platform loads and invokes the host's renderer module.

### Module loading

Renderer modules are **ES modules** loaded once per session when the first block matching their trigger arrives. The platform loads the module using a dynamic `import()` from the registered `moduleUrl`. Modules are cached for the session lifetime — they are not re-fetched on each block.

The module must export a **renderer class** (or factory function returning an object) that implements the following interface:

```typescript
interface HostRenderer {
  // Called once per content block after the full fenced block content is received.
  // `container` is a plain HTMLElement inside a shadow root — render freely within it.
  render(container: HTMLElement, content: string, context: RendererContext): void | Promise<void>;

  // Optional — called when the rendered element is removed from the DOM.
  dispose?(): void;
}

interface RendererContext {
  tenantId:    string;                    // the current tenant
  conversationId: string;                 // the current conversation
  turnId:      string;                    // the turn this block belongs to
  trigger:     string;                    // the fenced block tag that matched
  themeTokens: Record<string, string>;    // host brand CSS custom properties (e.g. "--color-primary")
}
```

The platform instantiates the renderer class once per content block, passes the full fenced block content as a string to `render()`, and calls `dispose()` when the block leaves the DOM (e.g. conversation navigation, component unmount).

### Isolation

Each rendered block's `container` is the interior of a **shadow root** — the renderer's DOM and styles are isolated from the platform UI and from other rendered blocks. The renderer may use any DOM APIs available to the module. It may not access the platform's internal state, the user's JWT, or other conversations.

### Streaming behaviour

Custom renderers receive the **full fenced block content** after `content_block_stop` — they cannot stream incrementally. While the block is buffering, the platform shows a loading skeleton in place of the renderer output. The skeleton is replaced by the rendered output on receipt.

### System prompt guidance injection

For each registered renderer, the platform injects the renderer's `systemPromptGuidance` (or a generated fallback) into the system prompt at session start. This tells the model when and how to produce the custom content type:

```
[Custom content types]
{renderer.name}: {renderer.systemPromptGuidance}
```

All registered renderer guidance blocks are appended together in the order they appear in the `renderers` config array. They are injected after tool descriptions and before memory blocks in the assembled system prompt.

### Fallback behaviour

If the renderer module fails to load, or if `render()` throws, the platform:

1. Logs the error to the improvement signal pipeline
2. Renders the fenced block content as a **syntax-highlighted code block** (priority 8)
3. Shows an inline notice beneath the block: *"[Renderer name] could not render this content. Showing raw output."*

The fallback is transparent to the user and non-blocking — the rest of the response continues rendering normally.

### Artefact tray

Custom-rendered blocks are added to the artefact tray as downloadable raw content (the fenced block source, stored as plain text with the trigger name as the format label). The renderer name and trigger are shown in the tray entry. If the renderer exposes a `getExportBlob?(): Promise<Blob>` method, the platform calls it on download and uses the returned blob in preference to the raw source — allowing the renderer to export a rendered image or structured file.

### Example: risk gauge renderer

Given the config:

```json
{
  "id":      "risk-gauge",
  "trigger": "risk-gauge",
  "name":    "Risk Gauge",
  "moduleUrl": "https://cdn.acme.com/ai-renderers/risk-gauge.js",
  "systemPromptGuidance": "Use a ```risk-gauge block when asked for a risk score. The block must contain JSON: { \"score\": <0–100>, \"label\": \"<text>\", \"breakdown\": [ { \"factor\": \"<name>\", \"score\": <0–100> } ] }."
}
```

The model produces:

````
```risk-gauge
{ "score": 72, "label": "Medium-High", "breakdown": [
    { "factor": "Data quality", "score": 80 },
    { "factor": "Ownership coverage", "score": 55 },
    { "factor": "Policy compliance", "score": 90 }
  ]
}
```
````

The platform calls `RiskGaugeRenderer.render(container, content, context)`. The renderer parses the JSON and renders a gauge widget into `container`. The raw JSON is stored in the artefact tray.

---

## Mermaid diagrams

| Behaviour | Specification |
|-----------|--------------|
| Rendering | SVG via Mermaid.js |
| Default display | Full-width in conversation thread, collapsed to thumbnail in artefact tray |
| Expand | Full-screen overlay available |
| Export | SVG download from artefact tray |
| Mobile | Horizontally scrollable — never scaled to illegibility |
| Accessibility | Descriptive alt text generated by the model and attached to the SVG |
| Artefact | Mermaid source stored in turn record; added to artefact tray on render complete |

### Common Mermaid diagram types

| Diagram type | Mermaid syntax | Typical trigger |
|-------------|---------------|----------------|
| Entity relationship | `erDiagram` | *"Show me the relationship between X and Y"* |
| Process flow | `flowchart LR` | *"Walk me through the approval workflow"* |
| Sequence diagram | `sequenceDiagram` | *"How do these services communicate?"* |
| Hierarchy / tree | `graph TD` | *"Show me the organisational structure"* |
| Timeline | `timeline` | *"Show the project milestones"* |

---

## Vega-Lite charts

| Behaviour | Specification |
|-----------|--------------|
| Rendering | Interactive via vega-embed |
| Responsive sizing | `width: "container"` — adapts to viewport or container |
| Export | PNG or SVG download from artefact tray |
| Interactivity | Hover tooltips, click-to-filter where applicable |
| Mobile | Responsive; minimum bar/point size maintained for touch targets |
| Artefact | Vega-Lite spec stored in turn record; added to artefact tray on render complete |

---

## Math expressions

Mathematical expressions are rendered using **KaTeX** — fast, lightweight, and browser-native.

| Behaviour | Specification |
|-----------|--------------|
| Display block | Triggered by ` ```math ` fenced block or `$$...$$` delimiter — rendered full-width, centred |
| Inline | Triggered by `$...$` within prose — renders inline without breaking text flow |
| Library | KaTeX — subset of LaTeX math notation |
| Copy | LaTeX source copy-to-clipboard button on display blocks |
| Export | LaTeX source and rendered SVG downloadable from artefact tray |
| Mobile | Display blocks horizontally scrollable at narrow viewports |
| Fallback | If KaTeX fails to parse, the raw LaTeX source is shown in a code block with a parse-error notice |

---

## JSON inspector

| Behaviour | Specification |
|-----------|--------------|
| Default state | Collapsed to two levels |
| Navigation | Expand/collapse nodes; copy individual values or subtrees |
| Export | Full JSON download from artefact tray |
| Use cases | Tool result payloads, configuration inspection, structured record data |

---

## Data tables

| Behaviour | Specification |
|-----------|--------------|
| Sorting | Click column header to sort ascending/descending |
| Filtering | Inline filter row per column |
| Pagination | 25 rows per page; configurable |
| Mobile | Horizontally scrollable; first column sticky |
| Export | CSV download from artefact tray |
| Empty state | "No results" message with query context |

---

## Syntax-highlighted code

| Behaviour | Specification |
|-----------|--------------|
| Highlighting | Prism.js — auto-detects language from fenced block tag |
| Copy | Copy-to-clipboard button always visible |
| Line numbers | Shown for blocks of more than five lines |
| Languages | SQL, Python, YAML, TypeScript, JSON, Bash, and all Prism-supported languages |

---

## Attached document and image display

**Non-image documents** (PDF, Excel, Word) appear in the user message bubble as a labelled file card:
- Format icon
- File name
- Page count (PDF), sheet count (Excel), or section count (Word)

Non-image documents are **not rendered inline**. When the model references a specific section, it cites by page number (PDF), sheet name (Excel), or heading (Word).

**Images** (PNG, JPEG, WEBP) are **rendered inline** in the user message bubble at a constrained size (max 320px wide, max 240px tall, maintaining aspect ratio). Multiple images in one turn stack vertically. Clicking an image opens it in a full-screen lightbox overlay. The original file is downloadable from the lightbox and from the artefact tray.

---

## Inline source citations

When the model's response draws on data returned by an MCP tool call, it should cite the source inline using a numbered superscript that links to the corresponding tool call disclosure card.

| Element | Specification |
|---------|--------------|
| Format | Superscript numeral in the prose (e.g. *"There are 12 entities in this domain¹"*) |
| Anchor | Clicking the superscript scrolls to and expands the referenced disclosure card |
| Scope | Citations reference the specific MCP tool invocation, not a generic tool name |
| Multiple sources | Where a claim draws on more than one tool call, multiple citations appear (e.g. *"...entities¹ ²"*) |
| Attached documents | Citations to attached documents use the document's cite format: page number (PDF), sheet name (Excel), heading (Word) |

Citations are rendered as part of the markdown prose block. Superscript numbers reset per response.

---

## Streaming behaviour

| Content type | Streaming behaviour |
|-------------|-------------------|
| Prose / markdown | Streams character-by-character; renders incrementally |
| Non-prose blocks (Mermaid, Vega-Lite, JSON, tables, code) | Buffers internally; renders on `content_block_stop` to prevent hydration errors on partial content |
| Tool call disclosures | Appear as an in-progress card while the tool is running; update on result receipt |
| Artefact chips | *"Added to artefacts ↗"* chip appears beneath each completed non-prose block |

While the model is streaming, the input field is disabled and replaced by a **stop-generation button**. Stopping generation saves the partial response to the audit trail as a partial turn — it does not discard it. When stopped, a *"(generation stopped)"* label appears beneath the partial response.

### Truncated response — continue generating

When the model's response ends without a natural conclusion (detected heuristically: response ends mid-sentence, or the model emits a continuation signal), a **Continue** button appears below the response:

> *"Response may be incomplete.* **Continue →***"*

Clicking Continue submits an implicit *"Please continue"* turn, which regenerates from the end of the incomplete response in a new branch. The original truncated response is preserved. This handles output-token-limit cases transparently without requiring the user to know why the response stopped.

The Continue button is shown for a maximum of 60 seconds after the truncated response; after that it is dismissed to avoid polluting old threads.
