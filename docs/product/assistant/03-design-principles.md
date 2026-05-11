# 03 — Design Principles

These nine principles govern all design decisions for the AI Chat Platform. Where a proposed feature conflicts with a principle, the principle takes precedence. Deviations require an explicit decision record.

---

## P1 — Transparency first

Every action the platform takes is visible. Tool calls are shown, not hidden. The assistant never implies a write operation has occurred if it has not. Opacity is a trust risk on any platform where users are making decisions based on the assistant's output.

**Consequences:**
- Every MCP tool invocation renders as a collapsible disclosure card in the conversation thread — tool name, input parameters, response status, result summary.
- The assistant may not summarise tool call activity without providing access to the full disclosure.
- Every write operation proposed by the assistant displays a **confirmation step** showing the before/after state before any MCP write call is executed. The assistant never implies a write has occurred if it has not.

---

## P2 — Host-scoped by design

Each deployment is a specialist, not a generalist. The platform provides the engine; the host application defines the domain. When a query falls outside the host-configured scope, the assistant explains clearly and redirects constructively.

**Consequences:**
- The host system prompt establishes domain scope and instructs the model to decline out-of-scope queries with a constructive redirect (configurable via `scope.outOfScopeRedirect`).
- Out-of-scope responses are captured as improvement signals to inform system prompt refinement.
- No platform-level general-purpose prompt library. All guided workflows are host-defined.

---

## P3 — Rendered output over raw text

Plain text answers to structured data queries are a regression from most application UIs the platform is embedded in. The default mode is rendered — charts, diagrams, tables — with prose reserved for narrative explanation. Every structured output has a rendered form.

**Consequences:**
- The rendering decision ruleset ([10-content-rendering.md](./10-content-rendering.md)) is applied to every assistant response before display.
- Mermaid, Vega-Lite, and tabular data are always rendered — never displayed as raw source.
- The system prompt instructs the model to prefer structured outputs (Vega-Lite for metrics, Mermaid for relationships, tables for entity lists) over prose equivalents when the data supports it.

---

## P4 — Audit completeness

Every conversation turn is a self-contained, reproducible record: raw prompt, resolved prompt, attached files, model response, tool call log, output artefacts. A reviewer can reconstruct any turn without referring to an external system.

**Consequences:**
- Storage policy ([11-audit-and-storage.md](./11-audit-and-storage.md)) retains all turn elements at write time — nothing is generated on demand.
- Conversations are append-only at the turn level. Editing creates a new branched thread; the original is untouched.
- Turn-level deletion is not permitted. Users may archive or delete conversations subject to the tenant's configured retention period.
- The `assistant` Postgres schema is isolated from platform infrastructure schemas with RLS enabled on all tables.

---

## P5 — Mobile-first and responsive

The assistant is fully functional on mobile and tablet. Hosts embed the platform in products consumed across device types. Business users, field workers, and mobile-first users are significant populations.

**Assistant-specific consequences:**
- `@`-binding typeahead anchors to the bottom of the viewport on mobile (not to the cursor position).
- Conversation search opens as a full-screen overlay on mobile with the keyboard raised.
- Mermaid diagrams are horizontally scrollable on mobile — never scaled to illegibility.
- Vega-Lite charts use `width: "container"` for responsive sizing.
- All input controls are thumb-reachable on mobile; no critical control is hidden behind secondary menus.

---

## P6 — Consistency with the host design system

The `<ai-chat>` web component inherits the host application's visual language via branding tokens. The component introduces no new visual language of its own. End users should experience the assistant as a natural extension of the host application, not a foreign product embedded inside it.

**Consequences:**
- All colour, typography, border radius, and logo tokens are provided by the host application config (`branding` section).
- Participant colour assignments in shared conversations use the host's primary colour as an anchor; the platform generates a compliant palette from it.
- Platform-default styles are used only as fallbacks when the host has not provided a token.

---

## P7 — Progressive disclosure

Long responses use progressive disclosure. Diagrams collapse to thumbnails. Tool call disclosures collapse by default. JSON trees collapse to two levels. The user is never overwhelmed by a single response.

**Consequences:**
- Tool call disclosure cards are collapsed by default; users expand to inspect detail.
- Mermaid diagrams collapse to a thumbnail with an expand control; full-screen view available.
- JSON inspector trees default to two levels collapsed.
- Data tables paginate — no unbounded scroll.
- Suggested follow-up chips (max 3) appear beneath each assistant response, not inline.

---

## P8 — Human-gated improvement

No change to the system prompt, tool registry, or guided workflow prompts is applied automatically. All improvement recommendations enter a triage pipeline and require human review before any change is deployed.

**Consequences:**
- Improvement signals (explicit ratings, retry patterns, tool failures, corrections, out-of-scope responses) are captured and queued — never applied directly.
- Automatically detected signals below the confidence threshold go to manual review before an improvement issue is raised.
- Explicit user reports (via the report icon) always generate an issue (no threshold).
- Application Admins review signal issues on a regular cadence. All changes enter the host application's standard approval process before deployment.

---

## P9 — Host sovereignty

The host application has final authority over the assistant's configuration, scope, and behaviour within its tenant. The platform enforces safety and audit requirements as non-negotiable constraints, but within those constraints the host is in control.

**Consequences:**
- The application config schema gives hosts control of system prompt, tools, bindings, workflows, branding, models, and feature flags.
- Platform-managed instructions (safety clauses, tool transparency, audit logging) are injected alongside — never instead of — the host system prompt. They are not user-configurable or host-overridable.
- Hosts may restrict capabilities (disable features, lock model selection, limit participant count) but may not exceed platform-level maximums.
- New platform-level defaults that would change existing tenant behaviour require a config migration path and advance notice.

---

## Principle interactions

| Principle | Most common tension | Resolution |
|-----------|-------------------|-----------|
| P1 (transparency) vs UX conciseness | Tool call disclosures add visual weight | Disclose via collapsible cards — present but not obtrusive |
| P3 (rendered output) vs P5 (mobile) | Charts may not render well at narrow widths | Vega-Lite `width: "container"` + horizontal scroll for tables and diagrams |
| P4 (audit completeness) vs storage cost | Full binary attachment storage is expensive | Retention is tenant-configurable; scheduled archival at expiry |
| P6 (host design system) vs accessibility | Host colour tokens may not meet contrast requirements | Platform validates contrast ratios at config submission; warnings surfaced to host |
| P7 (progressive disclosure) vs P4 (audit completeness) | Collapsed content could obscure audit data | Collapse is a UI affordance only — all content is stored in full regardless of display state |
| P8 (human-gated improvement) vs velocity | Approval pipeline slows iteration | Accepted tradeoff — trust and data integrity outweigh iteration speed on platforms where users act on assistant output |
| P9 (host sovereignty) vs P1 (transparency) | Host may wish to hide tool calls from end users | Tool call disclosure is mandatory and non-configurable — hosts may not suppress MCP disclosures |
