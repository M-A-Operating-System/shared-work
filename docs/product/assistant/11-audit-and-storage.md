# 11 — Audit and Storage

## Governing principle

Data AI Assistant conversations are **governance artefacts**, not transient chat logs. Every conversation turn is a self-contained, reproducible record. A governance reviewer can reconstruct what the user submitted, what files they provided, what the model queried, and what was produced — without referring to any external system (P4 — audit completeness).

---

## Storage policy

All conversation content is retained in full at write time. Nothing is reconstructed on demand.

### Per-turn stored elements

| Element | Stored as |
|---------|----------|
| User prompt (raw) | Exact text including `@`-binding chip markers |
| User prompt (resolved) | Message as sent to the model — bindings expanded to structured context blocks |
| Assistant response | Full markdown text including all content blocks |
| Rendered content blocks | Mermaid source, Vega-Lite specs, CSV, code — typed JSONB records |
| Tool call log | Tool name, input parameters, response payload, latency, success/error per invocation |
| Attached input files | Full binary stored in Supabase Storage |
| Output artefacts | Full content stored in turn record |
| Model version | Exact Claude model string (e.g. `claude-sonnet-4-20260501`) |
| Token counts | Input, output, cache read, cache write — per turn and running session totals |
| Improvement signals | Detected signals with confidence score and lifecycle status |
| Author (shared conversations) | `user_id` FK to `auth.users` on every turn |

### Partial turns

When a user stops generation mid-stream, the partial response is saved to the audit trail as a **partial turn** with a `status: partial` flag. It is not discarded.

---

## Retention

| Rule | Specification |
|------|--------------|
| Retention period | **3 years** — working guide confirmed by CDAiO; exact window to be ratified by compliance before launch. Each record is tagged with a `retention_expiry_date` at write time based on this period. |
| Retention tag | Each conversation record is tagged with a `retention_expiry_date` at write time |
| Archival | A scheduled Supabase function handles expiry and archival |
| User-initiated deletion | Users may delete conversations subject to the retention policy minimum; physical deletion is deferred to retention expiry |
| Turn-level deletion | Not permitted — conversations are append-only at the turn level. Editing creates a new branched thread. |
| Supabase Storage | Binary artefacts (attached documents, output files) follow the same retention schedule |

---

## Access control

| Access level | Capability |
|-------------|-----------|
| Authenticated user | Read and write access to their own conversation records only |
| Shared conversation participant | Read and write access to all turns within conversations they have accepted an invitation to |
| DDA audit-role administrator | Read access to all conversation records across all users |
| No user | May edit or delete individual turn records — turns are immutable once written |

Row-Level Security (RLS) is enabled on all tables in the `assistant` Postgres schema. The `assistant` schema is isolated from the DDA governance schema with no shared tables.

---

## Database schema overview

The full schema is specified in the companion technical specification (Appendix D of Issue #216). The `assistant` schema contains the following tables:

| Table | Purpose |
|-------|---------|
| `assistant.conversations` | One row per conversation thread; title, owner, created/updated timestamps, retention expiry |
| `assistant.turns` | One row per turn (user or assistant); conversation FK, author FK, model, token counts, status |
| `assistant.artefacts` | One row per artefact; turn FK, type, content/storage path, auto-generated name |
| `assistant.bindings` | One row per `@`-binding chip in a turn; object type, Display ID, resolved context snapshot |
| `assistant.tool_calls` | One row per MCP tool invocation; turn FK, tool name, input params, response payload, latency, status |
| `assistant.improvement_signals` | One row per signal; turn FK, signal type, confidence score, lifecycle status, GitHub issue ref |
| `assistant.session_tools` | One row per opt-in MCP tool activation; conversation FK, tool ID, activated by, activated at |
| `assistant.conversation_participants` | One row per participant per conversation; user FK, invited_by FK, invited_at, accepted_at, departed_at |

### RLS policies (summary)

- Users can `SELECT`, `INSERT` on their own conversations and turns.
- Accepted participants can `SELECT`, `INSERT` on shared conversation records.
- Audit administrators can `SELECT` all records.
- No user can `UPDATE` or `DELETE` turn records.
- `assistant.conversation_participants` records are append-only — departure is recorded as `departed_at` timestamp, not row deletion.

---

## Supabase Storage conventions

Binary artefacts are stored in Supabase Storage under the following path convention:

```
assistant/{conversation_id}/{turn_id}/{artefact_id}/{filename}
```

- Storage is private — access is mediated by signed URLs generated per-request with short expiry.
- Files are not publicly accessible.
- Storage paths are stored in `assistant.artefacts.storage_path`.

---

## Audit trail for shared conversations

In shared conversations, the `user_id` on each turn records the specific participant who submitted it. The `assistant.conversation_participants` table records the full invitation lifecycle:

| Column | Content |
|--------|---------|
| `user_id` | The participant's DDA user ID |
| `invited_by` | The user ID of the person who invited them |
| `invited_at` | Timestamp of invitation |
| `accepted_at` | Timestamp of acceptance (null if not yet accepted or declined) |
| `departed_at` | Timestamp of departure (null if still active) |

There are no role columns. All participants are equal. The audit record reflects actions taken, not role assignments.
