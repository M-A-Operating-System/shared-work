# 03 — Design Principles

These eight principles govern all design decisions for Data AI Assistant. Where a proposed feature conflicts with a principle, the principle takes precedence. Deviations require an explicit decision record.

---

## P1 — Governance-first transparency

Every action the model takes is visible. Tool calls are shown, not hidden. The model never implies a write operation has occurred if it has not. Opacity is a trust risk on a governance platform.

**Consequences:**
- Every MCP tool invocation renders as a collapsible disclosure card in the conversation thread — tool name, input parameters, response status, result summary.
- The model may not summarise tool call activity without providing access to the full disclosure.
- Every write operation proposed by Andi displays a **confirmation step** showing the before/after state before any MCP write call is made. Andi never implies a write has occurred if it has not.

---

## P2 — Specialist over generalist

The interface is scoped to the DDA platform. This is a feature, not a constraint — users are consulting a specialist colleague, not a general assistant. When a query falls outside scope, the model explains clearly and redirects constructively.

**Consequences:**
- The system prompt establishes DDA domain scope and instructs the model to decline out-of-scope queries with a constructive redirect.
- Out-of-scope responses are captured as improvement signals (signal type: *out-of-scope response*) to inform system prompt refinement.
- No general-purpose prompt library. All guided prompts are DDA governance workflows.

---

## P3 — Rendered output over raw text

Plain text answers to data queries are a regression from the existing DDA UI. The default mode is rendered — charts, diagrams, tables — with prose reserved for narrative explanation. Every structured output has a rendered form.

**Consequences:**
- The rendering decision ruleset ([10-content-rendering.md](./10-content-rendering.md)) is applied to every assistant response before display.
- Mermaid, Vega-Lite, and tabular data are always rendered — never displayed as raw source.
- The system prompt instructs the model to prefer structured outputs (Vega-Lite for metrics, Mermaid for relationships, tables for entity lists) over prose equivalents.

---

## P4 — Audit completeness

Every conversation turn is a self-contained, reproducible record: raw prompt, resolved prompt, attached files, model response, tool call log, output artefacts. A governance reviewer can reconstruct any turn without referring to an external system.

**Consequences:**
- Storage policy ([11-audit-and-storage.md](./11-audit-and-storage.md)) retains all turn elements at write time — nothing is generated on demand.
- Conversations are append-only at the turn level. Editing creates a new branched thread; the original is untouched.
- Conversation records align with the DDA audit log retention policy. Users may not physically delete individual turns.
- The `assistant` Postgres schema is isolated from the DDA governance schema with RLS enabled on all tables.

---

## P5 — Mobile-first and responsive

The chat surface is fully functional on mobile and tablet. This is a **DDA platform standard** — see [_design/02-responsive-and-mobile.md](../_design/02-responsive-and-mobile.md) for the platform-wide requirements. Business Head, Business Staff, and CDO personas are significant mobile consumers of the assistant.

**Assistant-specific consequences:**
- `@`-binding typeahead anchors to the bottom of the viewport on mobile (not to the cursor position).
- Conversation search opens as a full-screen overlay on mobile with the keyboard raised.
- Mermaid diagrams are horizontally scrollable on mobile — never scaled to illegibility.
- Vega-Lite charts use `width: "container"` for responsive sizing.

---

## P6 — Consistency with the DDA design system

The chat interface inherits the DDA platform's visual language. No new visual language is introduced. This is a **DDA platform standard** — see [_design/01-design-system.md](../_design/01-design-system.md).

**Assistant-specific consequence:**
- Participant colour assignments in shared conversations use the DDA design system's participant palette (up to nine distinct colours).

---

## P7 — Progressive disclosure

Long responses use progressive disclosure. Diagrams collapse to thumbnails. Tool call disclosures collapse by default. JSON trees collapse to two levels. The user is never overwhelmed by a single response.

**Consequences:**
- Tool call disclosure cards are collapsed by default; users expand to inspect detail.
- Mermaid diagrams collapse to a thumbnail with an expand control; full-screen view available.
- JSON inspector trees default to two levels collapsed; expand as needed.
- Data tables paginate — no unbounded scroll.
- Suggested follow-up chips (max 3) appear beneath each assistant response, not inline.

---

## P8 — Human-gated improvement

No change to the system prompt, entity master, or guided prompts is applied automatically. All improvement recommendations are raised as GitHub issues and follow the DDA product approval pipeline.

**Consequences:**
- Improvement signals (explicit ratings, retry patterns, tool failures, corrections, out-of-scope responses) are captured and queued — never applied directly.
- Automatically detected signals below the confidence threshold go to manual review before a GitHub issue is raised.
- Explicit user reports (via the report icon on any turn) always generate a GitHub issue (no threshold).
- The CDAiO reviews signal issues weekly. Changes enter the standard 13-stage DDA product approval pipeline before any modification is deployed.

---

## Principle interactions

| Principle | Most common tension | Resolution |
|-----------|-------------------|-----------|
| P1 (transparency) vs UX conciseness | Tool call disclosures add visual weight | Disclose via collapsible cards — present but not obtrusive |
| P3 (rendered output) vs mobile (P5) | Charts may not render well at narrow widths | Vega-Lite `width: "container"` + horizontal scroll for tables; diagrams scrollable |
| P4 (audit completeness) vs storage cost | Full binary attachment storage is expensive | Retention aligned to DDA audit log policy; scheduled archival at expiry |
| P7 (progressive disclosure) vs P4 (audit completeness) | Collapsed content could obscure audit data | Collapse is a UI affordance only — all content is stored in full regardless of display state |
| P8 (human-gated) vs improvement velocity | Approval pipeline slows iteration | Accepted tradeoff — trust and governance integrity outweigh iteration speed on a compliance platform |
