# 08 — Platform Operations

**Product:** AI Chat Platform  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Audit and storage

### Governing principle

Conversations on the AI Chat Platform are **auditable records**, not transient chat logs. Every conversation turn is a self-contained, reproducible record. A reviewer can reconstruct what the user submitted, what files they provided, what tools were invoked, and what was produced — without referring to any external system (P4 — audit completeness).

---

### Multi-tenant isolation

Every record in the `assistant` schema carries a `tenant_id` column. Row-Level Security (RLS) enforces that users can only access records belonging to their own tenant. No cross-tenant data access is possible through the platform's API.

The `assistant` schema is isolated from all platform infrastructure schemas and from any host application data schemas. No shared tables exist between the `assistant` schema and other schemas.

---

### Storage policy

All conversation content is retained in full at write time. Nothing is reconstructed on demand.

#### Per-turn stored elements

| Element | Stored as |
|---------|----------|
| User prompt (raw) | Exact text including `@`-binding chip markers |
| User prompt (resolved) | Message as sent to the model — bindings expanded to structured context blocks from `contextTemplate` |
| Assistant response | Full markdown text including all content blocks |
| Rendered content blocks | Mermaid source, Vega-Lite specs, CSV, code — typed JSONB records |
| Tool call log | Tool name, input parameters, response payload, latency, success/error per invocation |
| Attached input files | Full binary stored in platform object storage |
| Output artefacts | Full content stored in turn record |
| Canvas version | If the turn produces or accepts a canvas revision, a `canvas_versions` row is written linked to this turn |
| Model version | Exact provider model string (e.g. `provider-name:model-id:version`) and resolved tier (`fast` / `standard` / `powerful`) |
| Token counts | Input, output, cache read, cache write — per turn and running session totals |
| Improvement signals | Detected signals with confidence score and lifecycle status |
| Author | `user_id` FK on every turn (critical for shared conversations) |
| Tenant | `tenant_id` on every record — enforces multi-tenant isolation |

#### Partial turns

When a user stops generation mid-stream, the partial response is saved to the audit trail as a **partial turn** with a `status: partial` flag. It is not discarded.

---

### Retention

| Rule | Specification |
|------|--------------|
| Retention period | Configured per tenant via `conversations.retentionDays` in the application config. Platform default: **1,095 days (3 years)**. Tenants may configure a shorter or longer period within platform-level limits. |
| Retention tag | Each conversation record is tagged with a `retention_expiry_date` at write time |
| Archival | A scheduled platform function handles expiry and archival per tenant's configured retention period |
| User-initiated deletion | Users may delete conversations subject to the tenant's retention minimum; physical deletion is deferred to retention expiry |
| Turn-level deletion | Not permitted — conversations are append-only at the turn level. Editing creates a new branched thread. |
| Object storage | Binary artefacts (attached documents, generated outputs) follow the same tenant-configured retention schedule |

---

### Access control

| Access level | Capability |
|-------------|-----------|
| Authenticated end user | Read and write access to their own conversation records within their tenant only |
| Shared conversation participant | Read and write access to all turns within conversations they have accepted an invitation to |
| Application Admin | Read access to all conversation records within their own tenant (audit view); no write access to turn records |
| Platform Admin | Read access to all records across all tenants for operational purposes; no write access to turn records |
| No user | May edit or delete individual turn records — turns are immutable once written |

Row-Level Security (RLS) is enabled on all tables in the `assistant` Postgres schema. Policies enforce:
- `tenant_id` isolation across all tables
- Per-user and per-participant access within a tenant
- Append-only semantics for turn records

---

### Database schema overview

The `assistant` schema contains the following tables:

| Table | Purpose |
|-------|---------|
| `assistant.tenants` | One row per registered host application; tenant config snapshot, API key reference |
| `assistant.conversations` | One row per conversation thread; `tenant_id`, title, owner, timestamps, retention expiry, CSAT |
| `assistant.turns` | One row per turn; `tenant_id`, conversation FK, author FK, model, token counts, status |
| `assistant.artefacts` | One row per artefact; `tenant_id`, turn FK, type, content/storage path, auto-generated name |
| `assistant.bindings` | One row per `@`-binding chip in a turn; `tenant_id`, object type, Display ID, resolved context snapshot |
| `assistant.tool_calls` | One row per MCP tool invocation; `tenant_id`, turn FK, server ID, tool name, input params, response, latency, status |
| `assistant.improvement_signals` | One row per signal; `tenant_id`, turn FK, signal type, confidence score, lifecycle status, issue reference |
| `assistant.session_tools` | One row per opt-in MCP tool activation; `tenant_id`, conversation FK, server ID, activated_by, activated_at |
| `assistant.conversation_participants` | One row per participant per conversation; `tenant_id`, user FK, invited_by FK, lifecycle timestamps |
| `assistant.user_memory` | One row per personal memory item; `tenant_id`, user_id, content, category, status |
| `assistant.app_context` | One row per application context item; `tenant_id`, content, category, status, approval workflow fields |
| `assistant.app_context_versions` | Version history for application context items |
| `assistant.canvas_documents` | One row per document canvas open in a conversation; `tenant_id`, conversation FK, title, current version reference |
| `assistant.canvas_versions` | One row per canvas version; `tenant_id`, canvas FK, turn FK (the turn that produced or accepted this version), full markdown content, author (`user` or `model`), created_at |

#### RLS policies (summary)

- All tables require `tenant_id` to match the authenticated user's tenant claim from their JWT.
- Users can `SELECT`, `INSERT` on their own conversations and turns.
- Accepted participants can `SELECT`, `INSERT` on shared conversation records within the same tenant.
- Application Admins can `SELECT` all records within their tenant.
- Platform Admins can `SELECT` all records across all tenants.
- No user can `UPDATE` or `DELETE` turn records.
- `assistant.conversation_participants` records are append-only — departure is recorded as `departed_at` timestamp, not row deletion.
- `assistant.canvas_versions` records are append-only — each edit creates a new version row; no version row is modified after insertion.

---

### Object storage conventions

Binary artefacts are stored in platform object storage under the following path convention:

```
{tenant_id}/conversations/{conversation_id}/{turn_id}/{artefact_id}/{filename}
```

- Storage is private — access is mediated by signed URLs generated per-request with short expiry.
- Files are not publicly accessible.
- Storage paths are stored in `assistant.artefacts.storage_path`.

---

### Audit trail for shared conversations

In shared conversations, the `user_id` on each turn records the specific participant who submitted it. The `assistant.conversation_participants` table records the full invitation lifecycle:

| Column | Content |
|--------|---------|
| `user_id` | The participant's platform user ID |
| `invited_by` | The user ID of the person who invited them |
| `invited_at` | Timestamp of invitation |
| `accepted_at` | Timestamp of acceptance (null if not yet accepted or declined) |
| `departed_at` | Timestamp of departure (null if still active) |

There are no role columns — all participants are equal. The audit record reflects actions taken, not role assignments.

---

### Tenant config version history

Every version of a tenant's application config is retained in `assistant.tenants.config_history` (append-only array). This allows platform administrators and Application Admins to trace exactly which config version was active during any historical conversation session.

The config version active at session start is stored in `assistant.conversations.config_version`.

---

## Continuous improvement

### Principle

The AI Chat Platform is a living system. Every session generates signal data. **No change is applied automatically** — every recommendation enters a triage pipeline and requires human review before any change is deployed (P8 — human-gated improvement).

The improvement framework generates: **signal → triage → issue → approval → deploy**. It does not generate signal → auto-patch.

---

### Improvement signals

Five types of improvement signal are captured automatically from day one:

| Signal type | Detection | Auto-issue? |
|-------------|----------|-------------|
| **Explicit turn report** | User clicks the report icon on any turn and submits the modal — optionally with a written explanation | Always |
| **Query retry / rephrase** | User submits a substantially similar query within two turns | If confidence ≥ threshold |
| **MCP tool failure or empty result** | Tool call log shows error or zero-result set where results were expected | If confidence ≥ threshold |
| **In-conversation correction** | User explicitly corrects the assistant mid-session | If confidence ≥ threshold |
| **Out-of-scope response** | Response contains no tool invocation and no domain-specific content for a query that should have triggered one | If confidence ≥ threshold |

#### Explicit turn report — detail

The report icon appears on every turn (user and assistant). When a user submits a report:

- The turn `id`, `conversation_id`, `tenant_id`, `reporter_user_id`, optional `explanation` text, and a timestamp are stored in `assistant.improvement_signals`
- The signal always generates an improvement issue — no confidence threshold
- The improvement issue includes: the full turn content, the reporter's explanation (if provided), the preceding and following turns for context, and the MCP tool call log for the turn

The written explanation is the most valuable signal — it describes the problem in plain language without inference. Users should be encouraged (via the modal copy) to describe what was wrong and why.

#### Signal lifecycle

Each signal is stored in `assistant.improvement_signals` with a lifecycle status:

```
new → triaged → issued → resolved
```

| Status | Description |
|--------|-------------|
| `new` | Signal captured; awaiting triage |
| `triaged` | Reviewed; decision made on whether to raise an improvement issue |
| `issued` | Improvement issue created; signal linked to issue reference |
| `resolved` | Underlying change deployed and validated |

#### Confidence threshold

Automatically detected signals below the confidence threshold queue for **manual review first** before an improvement issue is raised. The exact threshold is set at launch and adjusted based on signal volume.

Explicit user reports bypass the confidence threshold and **always generate an improvement issue**.

---

### Improvement issue pipeline

Qualifying signals are processed into an improvement issue containing:

| Issue element | Content |
|--------------|---------|
| Failure description | Signal type, turn summary, and assistant output excerpt |
| Full conversation turn | Raw prompt, resolved prompt, tool call log, and assistant response |
| MCP tool call log | All tool invocations for the turn (server name, tool name, params, result, latency) |
| System-generated recommendation | Most likely remediation target — see table below |
| Tenant context | `tenant_id`, application name, config version active at the time |

#### Remediation targets

| Remediation target | When recommended |
|-------------------|-----------------|
| Host system prompt | Assistant goes out of scope, misrepresents capabilities, uses wrong terminology for the user's communication style |
| MCP tool description | Assistant chooses the wrong tool or fails to invoke a tool when it should |
| Guided workflow prompt | A workflow returns unhelpful or incomplete output |
| Bindable type `contextTemplate` | Binding resolution provides insufficient or incorrect context for the model |
| Application context | Out-of-date or missing application-level memory causing incorrect assumptions |

#### Routing

Improvement issues are:
1. **Always** visible to the Platform team for platform-level patterns
2. **Optionally forwarded to the host application** via the tenant's configured improvement webhook (see below)

Host applications that configure an improvement webhook receive structured JSON payloads for each qualifying signal, enabling their Application Admin to triage within their own tooling.

#### Improvement webhook (optional)

Host applications configure an improvement webhook endpoint via the Platform Admin API. When configured:
- Qualifying improvement signals (above threshold or explicit user reports) trigger a POST to the webhook URL with a structured JSON payload
- The payload includes: `tenant_id`, `signal_type`, `turn_summary`, `remediation_recommendation`, `issue_id`
- Authentication: the platform signs webhook payloads with an HMAC key provided at registration

---

### Improvement cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | Application Admin reviews new improvement issues for their tenant; advances high-confidence items | Application Admin (per tenant) |
| **Weekly** | Platform team reviews platform-level patterns across all tenants | Platform team |
| **Monthly** | Aggregate signal analysis; identify systemic patterns; set remediation priorities | Application Admin + Platform team |
| **Per release** | Post-change validation — monitor signal volume for the affected signal type for two weeks after deployment | Host development team + Platform team |

---

### What the improvement framework does not do

| Action | Status |
|--------|--------|
| Auto-update the host system prompt based on signals | Not permitted — all changes require host team review and config update |
| Auto-retrain or fine-tune the AI model | Not in scope — the platform uses foundation AI provider models |
| Apply changes to guided workflow prompts automatically | Not permitted — workflow changes require host team config update |
| Apply changes to MCP tool descriptions automatically | Not permitted |
| Close improvement issues without human triage | Not permitted — every issue requires Application Admin or Platform team review |
| Share improvement signal content across tenants | Not permitted — signals are tenant-scoped and never exposed to other tenants |

---

## Success metrics

### Governing principle

Metrics are captured from day one at both the platform level (across all tenants) and at the application level (per tenant). Platform-level targets reflect the health of the infrastructure and ecosystem. Application-level targets reflect the value each host application is delivering to its users. Baseline targets for new tenants are set at the end of month 1 based on observed behaviour.

---

### Platform-level metrics

These metrics are tracked across all tenants by the platform team.

| Metric | Definition | Target |
|--------|-----------|--------|
| **Active tenants** | Tenants with at least one active session in the 7-day window | Growth metric — tracked weekly |
| **Platform uptime** | API availability (p99 latency < 2s; error rate < 0.1%) | 99.9% |
| **MCP tool error rate (platform)** | Tool invocations with non-2xx response across all tenants | < 3% |
| **Cache hit rate (platform)** | `cache_read_input_tokens` ÷ total input tokens across all tenants | ≥ 40% by month 2 |
| **Tenant onboarding time** | Time from tenant registration to first active session | Baseline month 1 |
| **Improvement signal volume** | Total signals across all tenants per week | Baseline month 1; monitor trend |
| **Config validation failure rate** | Config submissions that fail validation ÷ total submissions | < 10% |

---

### Application-level metrics

These metrics are tracked per tenant and reported to the Application Admin via the tenant analytics dashboard.

| Metric | Definition | Target |
|--------|-----------|--------|
| **Weekly active users (WAU)** | Distinct users opening a session in a 7-day window | 40% of the tenant's eligible user base by day 90 |
| **Queries per session** | Mean user messages per conversation | ≥ 4 |
| **Workflow invocation rate** | Sessions invoking at least one guided workflow | ≥ 25% where workflows are configured |
| **Binding click-through** | Sessions where user clicks a binding chip (fires `binding-click` event) | ≥ 30% |
| **MCP tool error rate (application)** | Tool invocations with error in the tenant | < 3% |
| **User satisfaction (CSAT)** | Post-session rating (1–5) where offered | Mean ≥ 4.0 |
| **Improvement signal rate** | Improvement signals per 100 turns | Baseline month 1; reduction month-over-month |
| **Cache hit rate (application)** | Cache hit rate for this tenant's sessions | ≥ 40% by month 2 |
| **Document attachment rate** | Sessions with at least one document attachment | Baseline month 1 |
| **Artefact download rate** | Sessions with at least one artefact download | ≥ 20% |
| **Mobile session share** | Sessions on mobile/tablet viewport | Baseline month 1 |
| **Shared conversation rate** | Conversations with at least one invitation sent | Baseline month 1 |
| **Participant acceptance rate** | Invitations accepted ÷ total invitations sent | ≥ 70% |

---

### Metric definitions

#### Weekly active users
A user is counted once per 7-day window regardless of session count. "Active" means at least one user message submitted — opening the component without sending a message does not count.

#### Queries per session
Total user messages ÷ total conversation sessions in the period. Excludes sessions with zero user messages.

#### Workflow invocation rate
A session counts if at least one guided workflow was invoked via any method: Workflow Library click, `@`-binding, or natural-language trigger.

#### Binding click-through
A session counts if at least one binding chip in an assistant response was clicked (firing the `binding-click` event to the host application). Tracks whether users are using the assistant as a gateway into the host application, not just a standalone Q&A surface.

#### MCP tool error rate
Tool invocations with a non-2xx response or an empty result set (where results were expected) ÷ total tool invocations. The "expected results" qualifier requires a confidence classifier — baseline tracks simple error rate only until the classifier is calibrated.

#### User satisfaction (CSAT)
Post-session rating prompt (1–5 stars) shown to a random sample configured via `features.csatSampleRate` (default: 20% of sessions).

#### Improvement signal rate
Total improvement signals (all types) per 100 conversation turns, tracked by signal type. Month-over-month reduction in signal rate per type indicates the improvement pipeline is working.

#### Cache hit rate
`cache_read_input_tokens` ÷ (`input_tokens` + `cache_read_input_tokens`) per the AI provider API response. Tracked at session level and rolling daily average. A target of ≥ 40% by month 2 reflects the expectation that the system prompt and tool descriptions will be consistently cached after the first turn in each session.

#### Document attachment rate
Sessions where the user attached at least one document (PDF, Excel, Word, or image). Baseline metric — no target until month 1 data is available.

#### Artefact download rate
Sessions where the user downloaded at least one artefact from the artefact tray. Tracks whether users find rendered outputs useful enough to take away.

#### Mobile session share
Sessions where the viewport width is < 768px (mobile) or 768px–1023px (tablet) at any point during the session. Baseline metric to validate mobile-first investment.

#### Shared conversation rate
Conversations where at least one invitation was sent (regardless of acceptance). Tracks collaborative usage.

#### Participant acceptance rate
Invitations accepted ÷ total invitations sent. A low rate may indicate users are inviting the wrong people, or that the invitation UX needs improvement.

---

### Measurement responsibilities

| Metric | Source | Owner |
|--------|--------|-------|
| WAU, queries per session, CSAT, attachment rate, artefact download, mobile share, shared rate, acceptance rate | `assistant` schema + session analytics | Platform Engineering |
| Workflow invocation rate, binding click-through | `assistant.tool_calls` + binding click events | Platform Engineering |
| MCP tool error rate | `assistant.tool_calls.status` | Platform Engineering |
| Improvement signal rate | `assistant.improvement_signals` | Platform team + Application Admin |
| Cache hit rate | AI provider API response metadata stored in `assistant.turns` | Platform Engineering |
| Platform uptime, config validation failure rate | Platform infrastructure monitoring | Platform Engineering |

---

### Review cadence

| Cadence | Activity | Owner |
|---------|----------|-------|
| **Weekly** | WAU, tool error rate, CSAT per tenant — operational health | Platform Engineering |
| **Weekly** | Application Admin reviews improvement signal issues for their tenant | Application Admin |
| **Monthly** | Full metric review; signal rate analysis; cache hit trend | Platform team + Application Admins |
| **Day 90 (per tenant)** | Activation target assessment (40% WAU); decision on next feature priorities | Application Admin + Platform team |

---

### Tenant analytics dashboard

Each tenant's Application Admin has access to a **read-only analytics dashboard** showing their tenant's application-level metrics over time:
- WAU trend (30-day rolling)
- Queries per session trend
- CSAT distribution
- Top improvement signal types
- MCP tool error rate by server
- Cache hit rate trend

Platform-level metrics (cross-tenant) are visible to the Platform team only.

---

## Complementary MCP services

Three ecosystem-level MCP services operate alongside the platform and host application MCP servers. They are shared infrastructure — not owned by the platform or by individual host applications. None is a hard dependency for platform operation, but host applications benefit from registering them.

Two of these services have full product specifications in this repository:

- **[MCP Knowledge](../knowledge/01-overview.md)** — the centralised knowledge and skills server
- **[MCP Internet Fetch & Search](../internet/01-overview.md)** — the controlled web search and page fetch server

---

### MCP Repository

#### Overview

The **MCP Repository** is a centralised, discoverable catalogue of MCP servers available within the ecosystem. It serves as the primary discovery mechanism for host teams when they are configuring their tenant's MCP tool registry — providing a searchable directory of tools that have already been built, tested, and published, rather than requiring every host team to build their own MCP servers from scratch.

The MCP Repository is a **config-time service**: host teams use it when setting up or updating their application config, not as a runtime tool invoked during user conversations. Its value is in accelerating the time between "we want to add this capability to our assistant" and "this capability is live for our users."

#### What the MCP Repository provides

The MCP Repository holds metadata records for each published MCP server, including:

- **Server identity:** Name, publisher, version, and a plain-language description of what the server provides
- **Capability catalogue:** The specific tools exposed by the server, with descriptions and example invocations
- **Integration metadata:** The server's MCP endpoint URL, supported authentication types (`bearer`, `api-key`, `none`), and any pre-conditions for integration (e.g. required host-side configuration)
- **Quality indicators:** Verification status, uptime history, average latency, and known compatibility notes with the AI Chat Platform
- **Suggested descriptions:** Pre-written `description` field text optimised for injection into the AI Chat Platform's system prompt — host teams can use these as-is or customise them

#### How host teams use the MCP Repository

When a host team wants to add a new capability to their assistant, the typical flow is:

1. Search the MCP Repository for a server that provides the needed capability
2. Review the server's capability catalogue and quality indicators
3. Copy the server's endpoint URL, suggested `description`, and recommended `authType` into the `mcpServers` entry in the application config
4. Submit the updated config via the Config Editor UI or Admin API — the platform validates endpoint reachability as part of config submission
5. Monitor tool invocation quality via improvement signals in the first weeks of use

#### Publishing to the MCP Repository

MCP server publishers — whether internal platform teams, host application developers, or third parties — submit their server records via the MCP Repository's submission API. Submitted records are reviewed for:
- Correctness and completeness of metadata
- MCP protocol compliance
- Endpoint stability and availability
- Security posture (auth requirements, data exposure scope)

Approved records are published and immediately searchable in the Repository. Publishers are responsible for keeping their records current as their server's endpoint or capability changes.

#### Relationship to the per-tenant tool registry

The MCP Repository and the per-tenant tool registry ([05-tools-and-memory.md](./05-tools-and-memory.md)) are distinct:

| MCP Repository | Per-tenant registry |
|---------------|---------------------|
| Ecosystem-wide catalogue of all available servers | Tenant-specific list of servers active for that host application |
| Read at config time by host teams | Resolved at session runtime by the platform |
| Covers all publishers and server types | Covers only what the host application has chosen to enable |
| Not invoked during user conversations | The source of truth for what tools a session can use |

---

### MCP Knowledge

#### Overview

**[MCP Knowledge](../knowledge/01-overview.md)** is a centralised MCP server that provides shared, reusable assets across the MCP ecosystem — skills, guidance documents, prompt templates, and other static artefacts that are useful across many different host applications and conversation types.

Unlike the MCP Repository (which helps teams find and configure tools at setup time), MCP Knowledge is a **runtime service** — it can be registered as an MCP server in a tenant's tool registry and invoked during user conversations to retrieve resources on demand.

#### What the MCP Knowledge provides

The MCP Knowledge organises its content into three categories:

**Skills**
Pre-built structured reasoning patterns that the assistant can invoke to approach complex tasks consistently. Skills are prompt fragments with defined input parameters and expected output structures. Examples include:
- Structured root-cause analysis prompts
- Stakeholder communication drafting frameworks
- Risk assessment scoring rubrics
- Data quality evaluation methodologies

Skills are not model-specific — they work across Anthropic, OpenAI, and Gemini models. When the assistant retrieves a skill from the MCP Knowledge, it uses the skill's prompt structure to guide its reasoning for that turn.

**Guidance documents**
Static reference documents that apply across many host applications and are impractical for each host to maintain independently. Examples include:
- AI assistant usage guidelines and responsible use principles
- Data privacy handling guidance for AI-assisted workflows
- Model capability and limitation reference cards
- Prompt engineering best practices for domain-specific applications
- **Uncertainty handling guidance** — instructions for how the assistant should communicate the limits of its knowledge, signal when data may be outdated, and offer next steps (such as web search) when it cannot answer with confidence. This document is injected as a resource at session start by hosts that want consistent, domain-appropriate uncertainty behaviour beyond the platform's non-overridable baseline.

Guidance documents are versioned by the MCP Knowledge. When retrieved in a conversation, the document version is recorded in the tool call log.

**Prompt templates**
Reusable prompt structures that host teams can adopt as starting points for guided workflows in their application config. These are published as MCP resource objects and can be retrieved, reviewed, and adapted before being embedded in the `workflows` section of a tenant's config.

#### How host applications integrate the MCP Knowledge

Host applications that want their end users to benefit from MCP Knowledge content register the service as an MCP server in their tenant's tool registry — typically as an `opt-in` server, since not every conversation will require it:

```json
{
  "id":          "mcp-knowledge",
  "name":        "MCP Knowledge",
  "description": "Provides shared skills, guidance documents, and prompt templates from the platform knowledge base. Use when you need a structured reasoning approach, usage guidance, or reference material.",
  "endpoint":    "https://knowledge-mcp.maoperatingsystem.com/mcp",
  "authType":    "bearer",
  "accessTier":  "opt-in",
  "roles":       []
}
```

The MCP Knowledge endpoint and connection details are documented in the [MCP Knowledge specification](../knowledge/README.md). The suggested `description` field text above is optimised for AI Chat Platform system prompt injection.

#### Content governance

The MCP Knowledge is governed by the platform ecosystem team responsible for its operation. Content goes through an editorial review before publication:
- Skills and templates are tested against the platform's AI provider models before publication
- Guidance documents are reviewed for accuracy and applicability across a range of host application types
- All content is versioned; breaking changes to existing resources trigger a deprecation period before removal
- Tenants that have retrieved a specific resource version continue to receive that version until they explicitly update to a newer version

Host applications and their users cannot modify MCP Knowledge content. Feedback and content requests are submitted via the ecosystem's standard issue process.

#### Relationship to the platform

MCP Knowledge is independent of the AI Chat Platform — the platform does not own or operate it. The platform integrates with it cleanly:
- Resources returned by the service are rendered using the platform's standard content rendering rules (prose, code blocks, data tables as appropriate)
- Resource retrievals appear in the tool call disclosure card with the server name and tool name
- Retrieved resources are added to the session artefact tray for download
- Resource retrievals are included in the tenant's MCP tool error rate metric and improvement signal pipeline

If the MCP Knowledge is unavailable, it behaves like any other unavailable opt-in MCP server — an error is shown in the tool call disclosure card, and the session continues without it.

---

### MCP Internet Fetch & Search

#### Overview

**[MCP Internet Fetch & Search](../internet/01-overview.md)** is an ecosystem-level MCP server that provides the assistant with real-time access to web search results and page content. It is registered as a host application MCP server like any other — the distinction is that it is a shared, ecosystem-managed service rather than a server built and operated by the host team.

Web access complements the platform's primary data access pattern (structured MCP tool calls against the host application's own data) in situations where current information is needed that the host's tools and the model's training knowledge cannot provide — recent news, current pricing, up-to-date documentation, or any query that requires information beyond the host application's data scope.

#### What the MCP Internet Fetch & Search provides

| Tool | Description |
|------|-------------|
| `search` | Executes a web search query and returns a ranked list of results: title, URL, snippet, source domain, and site classification metadata |
| `fetch` | Retrieves and returns the content of a specific URL in raw, markdown, chunked, or summarised format |
| `fetch_authenticated` | Retrieves content from sites requiring authentication, using the caller's enterprise IdP or consumer OAuth credentials (v1+) |

Results are returned as structured MCP tool output — they appear in a tool call disclosure card and are cited inline using the platform's standard source citation mechanism (superscript numerals linking to the disclosure card). The model does not present web results as its own knowledge.

#### How host applications integrate the MCP Internet Fetch & Search

Host applications register the MCP Internet Fetch & Search as an MCP server in their tenant tool registry. It is typically configured as `opt-in` — the end user enables it per session when real-time information is needed — though hosts may configure it `always-on` if their use case depends on current information in every session:

```json
{
  "id":          "mcp-internet",
  "name":        "MCP Internet Fetch & Search",
  "description": "Searches the web and fetches page content for current information. Use when the user needs up-to-date facts, recent news, current documentation, or any information beyond the host application's data and the model's training knowledge. Always cite the source URL.",
  "endpoint":    "https://<your-deployment>/mcp",
  "authType":    "bearer",
  "accessTier":  "opt-in",
  "roles":       []
}
```

MCP Internet Fetch & Search is a self-hosted deployment — the endpoint is determined by the enterprise infrastructure team. Connection details and deployment guidance are documented in the [MCP Internet Fetch & Search specification](../internet/README.md).

#### Transparency and citation

Web search results follow the platform's mandatory tool call transparency rules — every search invocation and every page fetch appears as a collapsible disclosure card in the conversation thread. The model is instructed (via the platform-managed system prompt layer) to:
- Cite all web-sourced claims with inline source citations linking to the disclosure card
- Acknowledge when search results are recent vs. when the model is supplementing with training knowledge
- Not present search result content as the model's own knowledge

#### Relationship to the platform

The MCP Internet Fetch & Search is independent of the AI Chat Platform. When unavailable, it behaves like any other unavailable MCP server — an error in the disclosure card and the session continues without it. Web results rendered as prose are subject to the platform's standard content rendering rules; results rendered as structured data (tables, lists) use the platform's data table rendering.
