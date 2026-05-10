# 11 — Audit and Storage

## Governing principle

Conversations on the AI Chat Platform are **auditable records**, not transient chat logs. Every conversation turn is a self-contained, reproducible record. A reviewer can reconstruct what the user submitted, what files they provided, what tools were invoked, and what was produced — without referring to any external system (P4 — audit completeness).

---

## Multi-tenant isolation

Every record in the `assistant` schema carries a `tenant_id` column. Row-Level Security (RLS) enforces that users can only access records belonging to their own tenant. No cross-tenant data access is possible through the platform's API.

The `assistant` schema is isolated from all platform infrastructure schemas and from any host application data schemas. No shared tables exist between the `assistant` schema and other schemas.

---

## Storage policy

All conversation content is retained in full at write time. Nothing is reconstructed on demand.

### Per-turn stored elements

| Element | Stored as |
|---------|----------|
| User prompt (raw) | Exact text including `@`-binding chip markers |
| User prompt (resolved) | Message as sent to the model — bindings expanded to structured context blocks from `contextTemplate` |
| Assistant response | Full markdown text including all content blocks |
| Rendered content blocks | Mermaid source, Vega-Lite specs, CSV, code — typed JSONB records |
| Tool call log | Tool name, input parameters, response payload, latency, success/error per invocation |
| Attached input files | Full binary stored in platform object storage |
| Output artefacts | Full content stored in turn record |
| Model version | Exact model string (e.g. `claude-sonnet-4-6-20260501`) |
| Token counts | Input, output, cache read, cache write — per turn and running session totals |
| Improvement signals | Detected signals with confidence score and lifecycle status |
| Author | `user_id` FK on every turn (critical for shared conversations) |
| Tenant | `tenant_id` on every record — enforces multi-tenant isolation |

### Partial turns

When a user stops generation mid-stream, the partial response is saved to the audit trail as a **partial turn** with a `status: partial` flag. It is not discarded.

---

## Retention

| Rule | Specification |
|------|--------------|
| Retention period | Configured per tenant via `conversations.retentionDays` in the application config. Platform default: **1,095 days (3 years)**. Tenants may configure a shorter or longer period within platform-level limits. |
| Retention tag | Each conversation record is tagged with a `retention_expiry_date` at write time |
| Archival | A scheduled platform function handles expiry and archival per tenant's configured retention period |
| User-initiated deletion | Users may delete conversations subject to the tenant's retention minimum; physical deletion is deferred to retention expiry |
| Turn-level deletion | Not permitted — conversations are append-only at the turn level. Editing creates a new branched thread. |
| Object storage | Binary artefacts (attached documents, generated outputs) follow the same tenant-configured retention schedule |

---

## Access control

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

## Database schema overview

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

### RLS policies (summary)

- All tables require `tenant_id` to match the authenticated user's tenant claim from their JWT.
- Users can `SELECT`, `INSERT` on their own conversations and turns.
- Accepted participants can `SELECT`, `INSERT` on shared conversation records within the same tenant.
- Application Admins can `SELECT` all records within their tenant.
- Platform Admins can `SELECT` all records across all tenants.
- No user can `UPDATE` or `DELETE` turn records.
- `assistant.conversation_participants` records are append-only — departure is recorded as `departed_at` timestamp, not row deletion.

---

## Object storage conventions

Binary artefacts are stored in platform object storage under the following path convention:

```
{tenant_id}/conversations/{conversation_id}/{turn_id}/{artefact_id}/{filename}
```

- Storage is private — access is mediated by signed URLs generated per-request with short expiry.
- Files are not publicly accessible.
- Storage paths are stored in `assistant.artefacts.storage_path`.

---

## Audit trail for shared conversations

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

## Tenant config version history

Every version of a tenant's application config is retained in `assistant.tenants.config_history` (append-only array). This allows platform administrators and Application Admins to trace exactly which config version was active during any historical conversation session.

The config version active at session start is stored in `assistant.conversations.config_version`.
