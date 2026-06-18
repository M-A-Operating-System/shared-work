# 01 — Overview, Personas, and Principles

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Overview

### Conversational AI for any application

The **AI Chat Platform** enables any application to give its users a persistent, context-aware conversational interface — without building AI infrastructure. The experience is modelled on the best native AI desktop applications: rich rendered output, transparent tool usage, and a conversation that remembers where you left off. It is not a general-purpose assistant layer — each deployment is a **specialist** tuned to its host application's domain.

> **Governing intent:** Give any application team the ability to drop a production-grade AI assistant into their product within days — fully branded, scoped to their domain, connected to their data, and backed by a complete audit trail.

### What the platform is and is not

| It is | It is not |
|-------|-----------|
| A white-label assistant layer any application can embed as a web component | A standalone AI product with its own brand or identity |
| A multi-tenant platform where each host application brings its own scope, tools, and branding | A shared assistant all host applications configure from a single pool |
| A complete audit trail for every conversation turn and artefact | A transient chat tool with no persistent record |
| A controlled, host-configured MCP integration surface | An open API that allows arbitrary tool connections without host approval |
| A read-and-write assistant — queries, reasoning, and actions via host-registered MCP tools | A system that bypasses host application security models or acts without user confirmation |

### The assistant has no platform name

The platform has no end-user-facing name. Every tenant names their own assistant in their application config (`identity.assistantName`). End users see only that name. **[AssistantName]** is used as a placeholder throughout this spec wherever the assistant name would appear.

---

> **Guiding principles at a glance:** host-scoped by default, audit completeness, transparent tool usage, confirmation before action, no privileged data path, and consumer-rendered governed display. These are specified in full in the [Design principles](#design-principles) chapter below.

---

### Scope

#### In scope

- Embeddable `<ai-chat>` web component with full branding token support
- Multi-tenant architecture with complete per-tenant data isolation
- Persistent, named conversation threads scoped to the authenticated user within their tenant
- Conversation branching via message edit or regeneration — preserving the complete audit trail
- Full-text search across all user conversations within the tenant
- Host-configured `@`-binding for application-defined object types
- Host-configured Display ID pattern detection and auto-resolution
- Document attachments (PDF, Excel, Word, images) stored as platform artefacts
- Model switching within the host-configured allowed model set; provider-agnostic architecture
- Communication style and verbosity driven by host-provided user profile claims
- Host-registered MCP servers with always-on and opt-in access tiers
- Host-defined guided workflow prompts accessible from the Workflow Library panel
- Tool call transparency — every MCP invocation rendered as a collapsible disclosure card
- Write operations — actions via host MCP tools with explicit user confirmation before execution
- Shared conversations — up to ten participants within the same tenant, equal-participant model
- Personal memory (user-managed) and application context (Application Admin-managed)
- Session artefact tray accumulating all input and output artefacts
- Document canvas — iteratable working-document surface in the conversation panel; versioned, editable, model-revisable
- Three-zone responsive layout (history panel, conversation area, conversation panel) embedded within host app UI
- Rich content rendering: diagrams, chart specifications (SCL), structured data, syntax-highlighted code, formatted prose, mathematical notation
- Continuous improvement signal capture and per-tenant improvement issue pipeline
- Full audit trail per turn: raw prompt, resolved prompt, tool call log, output artefacts, token counts
- Complementary MCP ecosystem services: MCP Repository (tool discovery), MCP Knowledge (shared skills and artefacts), and MCP Internet Fetch & Search (real-time web search)

#### Out of scope

- Semantic search over application data (pgvector RAG) — structured MCP tool calls are the primary data access pattern in v1
- Conversation export (PDF or markdown) — planned; data classification complexity must be resolved first
- Voice or multimodal input
- Context globbing (pulling context from multiple past conversations into one session)
- Incognito or temporary chat (no-history mode) — conflicts with audit completeness
- Platform-owned web search — available via the Web Search complementary MCP service registered by the host (see [08-platform-operations.md](./08-platform-operations.md))
- Image or content generation
- Code execution sandbox
- Public shareable links — all sharing is participant-controlled and tenant-scoped
- Read receipts in shared conversations
- Dark mode — not in v1

---

### Platform architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Host Application                          │
│                                                              │
│   ┌────────────────────────────────────────┐                 │
│   │        <ai-chat> web component         │                 │
│   │   (embedded in host application UI)    │                 │
│   └────────────────┬───────────────────────┘                 │
│                    │ Authentication bridge (JWT + claims)    │
└────────────────────┼─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│                  AI Chat Platform                             │
│                                                              │
│  ┌─────────────────┐   ┌──────────────────────────────────┐  │
│  │  Conversation   │   │  AI Provider Edge Function        │  │
│  │  Engine         │◀──│  (provider-agnostic abstraction;  │  │
│  │                 │   │   fast / standard / powerful tier)│  │
│  └────────┬────────┘   └──────────────────────────────────┘  │
│           │                                                  │
│  ┌────────▼────────┐   ┌──────────────────────────────────┐  │
│  │  Audit Storage  │   │  Per-tenant tool registry         │  │
│  │  (multi-tenant) │   │  (from application config)        │  │
│  └─────────────────┘   └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                     │
     ┌───────────────┼────────────────────┐
     │               │                    │
┌────▼────┐   ┌──────▼──────┐   ┌────────▼───────┐
│ Host    │   │ Host MCP    │   │ Complementary     │
│ App     │   │ Server(s)   │   │ MCP Services      │
│ API     │   │ (registered │   │ (Repository +     │
│         │   │  in config) │   │  Resources +      │
│         │   │             │   │  Web Search)      │
└─────────┘   └─────────────┘   └───────────────────┘
```

#### Components

**AI Chat Platform** owns the conversational surface, content rendering, audit trail, shared conversation model, memory management, and improvement signal pipeline. It depends on, but does not duplicate, the capabilities of the host application or its MCP servers.

**Host Application** owns the user identity model, application business logic, and MCP server endpoints. It embeds the platform via the web component and passes user context via the authentication bridge.

**Host MCP Servers** are the host application's data and action providers. The platform routes tool calls to these servers and surfaces the results transparently in the conversation thread.

**Complementary MCP Services** — the MCP Repository, MCP Knowledge, and MCP Internet Fetch & Search — are ecosystem-level services that operate alongside both the platform and host MCP servers. They are not owned by the platform or by individual host applications. See [08-platform-operations.md](./08-platform-operations.md).

---

### Dependencies

| Dependency | Role |
|------------|------|
| **AI provider** | Provider-agnostic abstraction exposing three model tiers: `fast`, `standard` (default), `powerful`. The platform maps tiers to the tenant's configured provider's current models. Multiple providers planned — see [ROADMAP.md](./ROADMAP.md). |
| **Platform storage** | Relational database with row-level security for conversation records; object storage for binary artefacts. |
| **Platform edge function** | JWT handling, AI provider API request construction, SSE stream passthrough, MCP call routing. Provider-agnostic interface. |
| **Host authentication** | The host application issues JWTs for its users. The platform validates these tokens and trusts the embedded claims. The platform performs no re-authentication. |
| **Host MCP server(s)** | The host's registered MCP endpoints providing data access and action capabilities. |
| **MCP Repository** | Complementary ecosystem service — discoverable registry of available MCP tools. |
| **MCP Knowledge** | Complementary ecosystem service — centralised skills, guidance documents, and reusable prompt artefacts. |
| **MCP Internet Fetch & Search** | Complementary ecosystem service — real-time web search and page retrieval; registered by hosts as an opt-in or always-on MCP server. |

---

## Personas and user journeys

Personas are described at two levels: **platform-level archetypes** (roles that exist across all deployments) and **illustrative host application journeys** (examples of how different host applications use the platform).

---

### Platform-level personas

These archetypes exist in every deployment regardless of the host application's domain.

| Persona | Role | Primary need |
|---------|------|--------------|
| **End User** | Authenticated user of the host application using the assistant as their primary access point | Ask questions and get immediate, accurate answers about the host application's domain without leaving the page |
| **Power User** | Experienced end user who regularly uses advanced features | Multi-turn investigation, `@`-binding for precise object references, branching threads, tool call inspection |
| **Application Admin** | Privileged user within the tenant responsible for the assistant's quality and application context | Manage application context (org-level memory), triage improvement signals, maintain workflow quality |
| **Host Developer** | Engineer at the host application team responsible for config and integration | Register MCP servers, maintain the application config, manage bindable types and guided workflows |
| **Platform Admin** | AI Chat Platform team member with cross-tenant visibility | Platform health, tenant onboarding, infrastructure, improvement pipeline |

#### Application Admin design note

The Application Admin role is the platform's equivalent of a product owner for the assistant within the tenant. They are not necessarily a technical user. Key responsibilities:

- Managing application context (organisation-wide memory items that all users benefit from)
- Reviewing and approving application context items proposed by colleagues
- Triaging improvement signals generated by end users within their tenant
- Updating the application config via the Config Editor UI (non-technical admins) or Admin API (technical admins)

This role must exist in every tenant before go-live. Host teams should designate at least one Application Admin at registration time.

---

### Illustrative host application journeys

These journeys are illustrative — they show how different types of host application use the platform. They are not prescriptive for any specific deployment.

---

#### Journey A — Governance platform: executive morning briefing

**Host application type:** Data governance and compliance platform  
**Persona:** Executive leader  
**Setting:** Mobile, during commute (5 minutes)

The executive opens the assistant on their mobile. They type: *"Give me a governance health summary — anything that needs my attention this week."*

The assistant invokes the host's governance MCP server, retrieves domain health scores and open quality issues, and returns:
- A Vega-Lite chart of domain health scores
- A bullet summary of the three domains requiring attention, ranked by severity

The executive taps one of the domain binding chips in the response, which the host application has configured to navigate to the domain detail page. They follow up: *"Who owns the entities flagged in the Finance domain?"* — the assistant returns a table of owners with contact details.

Both artefacts appear in the session artefact tray.

**Features exercised:** Mobile layout, Vega-Lite rendering, `@`-binding chip click-through to host app, artefact tray, always-on MCP server.

---

#### Journey B — Customer support platform: self-service knowledge lookup

**Host application type:** Internal customer support tooling  
**Persona:** Support agent (End User)  
**Setting:** Desktop, between calls

A support agent needs to know the current policy for handling a specific type of refund request. They type `@Refund Policy` — the `@`-binding typeahead opens and filters instantly. They select **Standard Refund Policy** from the panel; the binding chip `@{Standard Refund Policy}` is inserted. They submit:

> *"Can I apply `@{Standard Refund Policy}` to orders over 90 days old, or does that need manager escalation?"*

The assistant retrieves the resolved policy context (host-configured `contextTemplate`) and answers directly: yes for up to 180 days; manager escalation required beyond that. No knowledge base navigation required.

Total: one turn.

**Features exercised:** `@`-binding typeahead, single-turn self-service answer, policy binding type.

---

#### Journey C — Engineering platform: cross-service incident investigation (branching)

**Host application type:** Internal engineering observability and incident management  
**Persona:** On-call engineer (Power User)

An on-call engineer is investigating an incident affecting two services. They submit:

> *"Compare error rates for `@{Payment Service}` and `@{Notification Service}` over the last hour and show any shared dependencies."*

The assistant invokes the host's observability MCP server (multiple tool calls, each visible as a collapsed disclosure card) and returns:
- A comparative Vega-Lite chart of error rates over time
- A Mermaid dependency graph of shared services

The engineer expands one of the tool call disclosure cards to inspect the raw parameters sent to the MCP server. They then edit their original message to narrow the time range to the last 20 minutes. This creates a **new branched conversation thread** pre-loaded with the original context. Both threads appear in the history panel — the original is untouched.

**Features exercised:** Multi-entity `@`-binding, tool call disclosure inspection, message edit → branched thread, Mermaid and Vega-Lite rendering.

---

#### Journey D — Legal and compliance platform: guided compliance check

**Host application type:** Contract and regulatory compliance management  
**Persona:** Compliance officer (End User)

A compliance officer needs to run a weekly GDPR compliance check across active contracts. They open the **Workflow Library** panel and click **GDPR Compliance Audit** — a workflow defined by the host application in their config.

A parameter form appears requesting a contract category scope. The officer selects "Customer Agreements" and launches the workflow.

The assistant runs a multi-step analysis, invoking several host MCP tools sequentially, and returns a structured compliance report with a data table of non-compliant clauses and a Vega-Lite chart of compliance rates by category.

The officer clicks the report icon on one assistant response where the model missed a known clause type and submits an explanation. This generates an improvement signal queued for the Application Admin to triage.

**Features exercised:** Guided workflow with parameters, multi-step MCP tool calls, structured report rendering, improvement signal via report icon.

---

#### Journey E — HR platform: new employee onboarding

**Host application type:** HR and people management platform  
**Persona:** New employee (End User, first visit)

A new employee opens the assistant for the first time. The conversation area shows the onboarding welcome state: the host-configured assistant name and description, and three starter questions drawn from the host's `features.starterQuestions` config.

They click *"What benefits am I eligible for and how do I enrol?"* and receive a plain-language explanation of their benefits package, eligibility dates, and a link to the enrolment workflow, which the host has registered as a guided workflow.

**Features exercised:** First-visit onboarding state, starter questions from host config, suggested follow-ups, guided workflow invocation from response.

---

#### Journey F — Shared review: multi-participant governance session

**Host application type:** Any platform requiring collaborative decision-making  
**Persona:** Power User (conversation owner) + End Users (participants)

A governance lead shares an active conversation with two colleagues to collaborate on an entity ownership review. The lead clicks the share icon in the input area, searches for their colleagues by name within the tenant, and sends invitations.

Both colleagues receive in-platform notifications and accept — seeing the full conversation history from the beginning (with the acceptance disclaimer). Each participant now submits their own turns. Because each user's `@`-binding typeahead is scoped to their individual permissions, one participant sees a **[Restricted object]** chip for a binding they cannot access in the host application.

At the end of the session, the lead downloads all artefacts from the tray as a zip archive.

**Features exercised:** Shared conversations, participant invitation, permission-scoped `@`-binding, message attribution, artefact download.

---

### Persona × Feature Matrix

| Feature | End User | Power User | App Admin | Host Developer |
|---------|:--------:|:----------:|:---------:|:--------------:|
| Mobile-first layout | ✓ | ✓ | ✓ | |
| `@`-binding typeahead | ✓ | ✓ | ✓ | |
| Model switching | | ✓ | | |
| Document attachments | ✓ | ✓ | ✓ | |
| Guided workflow prompts | ✓ | ✓ | ✓ | |
| Tool call disclosure inspection | | ✓ | ✓ | ✓ |
| Vega-Lite charts | ✓ | ✓ | ✓ | |
| Mermaid diagrams | | ✓ | ✓ | |
| Data tables | ✓ | ✓ | ✓ | |
| Conversation branching | | ✓ | ✓ | |
| Shared conversations | ✓ | ✓ | ✓ | |
| Personal memory management | ✓ | ✓ | ✓ | |
| Application context management | | | ✓ | |
| Improvement signal triage | | | ✓ | |
| Application config management | | | ✓ | ✓ |
| Onboarding welcome state | ✓ | | | |
| Report icon feedback | ✓ | ✓ | ✓ | |

---

## Design principles

These nine principles govern all design decisions for the AI Chat Platform. Where a proposed feature conflicts with a principle, the principle takes precedence. Deviations require an explicit decision record.

---

### P1 — Transparency first

Every action the platform takes is visible. Tool calls are shown, not hidden. The assistant never implies a write operation has occurred if it has not. Opacity is a trust risk on any platform where users are making decisions based on the assistant's output.

**Consequences:**
- Every MCP tool invocation renders as a collapsible disclosure card in the conversation thread — tool name, input parameters, response status, result summary.
- The assistant may not summarise tool call activity without providing access to the full disclosure.
- Every write operation proposed by the assistant displays a **confirmation step** showing the before/after state before any MCP write call is executed. The assistant never implies a write has occurred if it has not.

---

### P2 — Host-scoped by design

Each deployment is a specialist, not a generalist. The platform provides the engine; the host application defines the domain. When a query falls outside the host-configured scope, the assistant explains clearly and redirects constructively.

**Consequences:**
- The host system prompt establishes domain scope and instructs the model to decline out-of-scope queries with a constructive redirect (configurable via `scope.outOfScopeRedirect`).
- Out-of-scope responses are captured as improvement signals to inform system prompt refinement.
- No platform-level general-purpose prompt library. All guided workflows are host-defined.

---

### P3 — Rendered output over raw text

Plain text answers to structured data queries are a regression from most application UIs the platform is embedded in. The default mode is rendered — charts, diagrams, tables — with prose reserved for narrative explanation. Every structured output has a rendered form.

**Consequences:**
- The rendering decision ruleset ([06-interface-and-rendering.md](./06-interface-and-rendering.md)) is applied to every assistant response before display.
- Mermaid, Vega-Lite, and tabular data are always rendered — never displayed as raw source.
- The system prompt instructs the model to prefer structured outputs (Vega-Lite for metrics, Mermaid for relationships, tables for entity lists) over prose equivalents when the data supports it.

---

### P4 — Audit completeness

Every conversation turn is a self-contained, reproducible record: raw prompt, resolved prompt, attached files, model response, tool call log, output artefacts. A reviewer can reconstruct any turn without referring to an external system.

**Consequences:**
- Storage policy ([08-platform-operations.md](./08-platform-operations.md)) retains all turn elements at write time — nothing is generated on demand.
- Conversations are append-only at the turn level. Editing creates a new branched thread; the original is untouched.
- Turn-level deletion is not permitted. Users may archive or delete conversations subject to the tenant's configured retention period.
- The `assistant` Postgres schema is isolated from platform infrastructure schemas with RLS enabled on all tables.

---

### P5 — Mobile-first and responsive

The assistant is fully functional on mobile and tablet. Hosts embed the platform in products consumed across device types. Business users, field workers, and mobile-first users are significant populations.

**Assistant-specific consequences:**
- `@`-binding typeahead anchors to the bottom of the viewport on mobile (not to the cursor position).
- Conversation search opens as a full-screen overlay on mobile with the keyboard raised.
- Mermaid diagrams are horizontally scrollable on mobile — never scaled to illegibility.
- Vega-Lite charts use `width: "container"` for responsive sizing.
- All input controls are thumb-reachable on mobile; no critical control is hidden behind secondary menus.

---

### P6 — Consistency with the host design system

The `<ai-chat>` web component inherits the host application's visual language via branding tokens. The component introduces no new visual language of its own. End users should experience the assistant as a natural extension of the host application, not a foreign product embedded inside it.

**Consequences:**
- All colour, typography, border radius, and logo tokens are provided by the host application config (`branding` section).
- Participant colour assignments in shared conversations use the host's primary colour as an anchor; the platform generates a compliant palette from it.
- Platform-default styles are used only as fallbacks when the host has not provided a token.

---

### P7 — Progressive disclosure

Long responses use progressive disclosure. Diagrams collapse to thumbnails. Tool call disclosures collapse by default. JSON trees collapse to two levels. The user is never overwhelmed by a single response.

**Consequences:**
- Tool call disclosure cards are collapsed by default; users expand to inspect detail.
- Mermaid diagrams collapse to a thumbnail with an expand control; full-screen view available.
- JSON inspector trees default to two levels collapsed.
- Data tables paginate — no unbounded scroll.
- Suggested follow-up chips (max 3) appear beneath each assistant response, not inline.

---

### P8 — Human-gated improvement

No change to the system prompt, tool registry, or guided workflow prompts is applied automatically. All improvement recommendations enter a triage pipeline and require human review before any change is deployed.

**Consequences:**
- Improvement signals (explicit ratings, retry patterns, tool failures, corrections, out-of-scope responses) are captured and queued — never applied directly.
- Automatically detected signals below the confidence threshold go to manual review before an improvement issue is raised.
- Explicit user reports (via the report icon) always generate an issue (no threshold).
- Application Admins review signal issues on a regular cadence. All changes enter the host application's standard approval process before deployment.

---

### P9 — Host sovereignty

The host application has final authority over the assistant's configuration, scope, and behaviour within its tenant. The platform enforces safety and audit requirements as non-negotiable constraints, but within those constraints the host is in control.

**Consequences:**
- The application config schema gives hosts control of system prompt, tools, bindings, workflows, branding, models, and feature flags.
- Platform-managed instructions (safety clauses, tool transparency, audit logging) are injected alongside — never instead of — the host system prompt. They are not user-configurable or host-overridable.
- Hosts may restrict capabilities (disable features, lock model selection, limit participant count) but may not exceed platform-level maximums.
- New platform-level defaults that would change existing tenant behaviour require a config migration path and advance notice.

---

### Principle interactions

| Principle | Most common tension | Resolution |
|-----------|-------------------|-----------|
| P1 (transparency) vs UX conciseness | Tool call disclosures add visual weight | Disclose via collapsible cards — present but not obtrusive |
| P3 (rendered output) vs P5 (mobile) | Charts may not render well at narrow widths | Vega-Lite `width: "container"` + horizontal scroll for tables and diagrams |
| P4 (audit completeness) vs storage cost | Full binary attachment storage is expensive | Retention is tenant-configurable; scheduled archival at expiry |
| P6 (host design system) vs accessibility | Host colour tokens may not meet contrast requirements | Platform validates contrast ratios at config submission; warnings surfaced to host |
| P7 (progressive disclosure) vs P4 (audit completeness) | Collapsed content could obscure audit data | Collapse is a UI affordance only — all content is stored in full regardless of display state |
| P8 (human-gated improvement) vs velocity | Approval pipeline slows iteration | Accepted tradeoff — trust and data integrity outweigh iteration speed on platforms where users act on assistant output |
| P9 (host sovereignty) vs P1 (transparency) | Host may wish to hide tool calls from end users | Tool call disclosure is mandatory and non-configurable — hosts may not suppress MCP disclosures |

---

## Platform decisions

| ID | Decision |
|----|---------|
| **D1** | Host applications configure everything via a JSON application config. The platform provides mechanisms; hosts provide content (system prompt, tools, bindings, workflows, branding). |
| **D2** | The platform has no end-user-facing name. Each host application names its own assistant in its config. |
| **D3** | The platform is multi-tenant. One deployment serves many host applications, each fully isolated by `tenant_id` with row-level security. |
| **D4** | Conversations and artefacts are stored in the platform's own database. Host applications do not manage storage. |
| **D5** | The web component is the only supported embedding model in v1. Direct iframe embedding is not supported. |
| **D6** | The authentication bridge passes host-authenticated user identity to the component. The platform trusts the host's JWT; it does not re-authenticate users independently. |
| **D7** | No MCP server is always-on by default. Host applications designate which of their registered servers should be always-on in their config. If no always-on server is registered, the platform operates in prompt-only mode. |
| **D8** | Conversations are append-only at the turn level. Message editing creates a new branched thread; the original is preserved. |
| **D9** | Improvement signals generated by the platform are routed to the platform team and optionally forwarded to the host application via webhook. |
| **D10** | Retention period is configurable per tenant in the application config. The platform default is 3 years. |
| **D11** | Conversation sharing is scoped to users within the same tenant. Cross-tenant invitations are not supported. |
| **D12** | The MCP Repository, MCP Knowledge, and MCP Internet Fetch & Search are complementary ecosystem services — the platform assumes their availability but does not own or operate them. |
