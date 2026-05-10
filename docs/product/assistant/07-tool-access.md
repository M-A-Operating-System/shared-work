# 07 — Tool Access

## DDA MCP server — always-on

The DDA MCP server is the **primary tool provider** for every Data AI Assistant session. It cannot be disabled.

- The model accesses all tools exposed via `entityMeta.ts` (generated from `entityRegistry.ts`) for the authenticated user's permission level.
- Tool access is entitlement-aware — what a user can see in the DDA UI, they can access via MCP. What they cannot, they cannot.
- See [docs/product/mcp/](../mcp/README.md) for the full DDA MCP server design specification.

### What the DDA MCP server provides

| Tool category | Exposure | Typical invocation |
|--------------|---------|-------------------|
| Entity lookup | All entities with an `mcp` block in `entityMeta.ts` (generated from `entityRegistry.ts`) | *"Find all entities in the Customer domain"* |
| Entity detail | Single entity by Display ID | *"Tell me about DMD00000001"* |
| Survey objects | Survey records — title, scope, response summary, key findings, strategic recommendations | *"What did the Q2 data maturity survey say about the Finance domain?"* |
| Governance summary | Cross-domain health, quality metrics, compliance status | *"Give me a governance health summary for this week"* |
| Guided prompts (5) | Pre-built governance workflow prompts | *"Run a data quality assessment for the Finance domain"* |
| Semantic search | pgvector RAG — not active; `search_model` stub returns empty | Not available |
| Resources (7) | Static markdown governance resources | *"What is the DDA classification framework?"* |
| Policy and standards | Codified organisational policy, data standards, and business process documentation structured as DDA records — accessible via MCP as a planned capability. Enables Andi to reason about compliance and process questions against the authoritative policy corpus rather than relying on model training data. | *"Does our data retention policy cover customer contact records?"* (planned) |
| Entity update (CRUD) | Update and status-change operations exposed through the DDA MCP server. Andi enforces the same DDA security model as the DDA UI — users can only update records they have write access to. Every proposed update displays a before/after confirmation step before the MCP write call is made. | *"Update the data owner for DMD00000001 to Jane Smith"* |

---

## Additional tools — opt-in per session

Additional MCP tools beyond the always-on DDA server are defined in the **build-time MCP tool registry** (see [13-mcp-tool-registry.md](./13-mcp-tool-registry.md)).

| Behaviour | Specification |
|-----------|--------------|
| Default state | **Off** — no additional tools active at session start |
| Activation | Per-session — enabled by the user via the tool selection panel |
| Persistence | **Does not persist across sessions** — users re-enable tools each session |
| Access | The tool selection panel opens via the tool icon in the input area |

The opt-in model means that the model's tool context starts minimal and grows only when the user explicitly requests additional capability. This keeps the model's available tool surface predictable and auditable.

---

## Guided workflows

Five DDA guided workflow prompts are available from the **Guided Workflows drawer**, opened via the **DDA platform nav** (left side). The drawer slides in over the history panel — it is not part of the right sidebar, which is reserved for conversation-specific content.

| Invocation method | How it works |
|------------------|-------------|
| Click in Guided Workflows drawer | Single click injects the full workflow prompt into the input field; drawer closes; user submits |
| `@`-binding | Typing `@Data Quality Assessment` and selecting from typeahead injects the workflow prompt on submission |
| Natural language | Phrasing that matches a guided workflow trigger (e.g. *"run a quality check"*) causes the model to invoke the workflow pattern |

Guided workflows are **platform-managed** — the prompts are version-controlled and deployed centrally. Users cannot create or modify guided workflows.

### Current guided workflows (v1)

The five guided workflow prompts cover the most common DDA governance patterns. They are designed for the full persona range — from CDO to Business Staff — not data modellers only. Each workflow has been reviewed against the existing MCP prompt library (`docs/product/mcp/06-prompts.md`) and updated or extended as noted.

| # | Workflow name | Primary persona | MCP prompt basis | Key improvements for Andi |
|---|--------------|----------------|-----------------|--------------------------|
| 1 | **Governance Health Check** | CDO, Governance Officer | Extends `explore_domain` | Reoriented from data-model exploration to executive governance summary. Triggers cross-domain health scoring, quality flags, and ownership gaps in one workflow. Argument: optional `domain` scope (defaults to all domains). |
| 2 | **Data Quality Assessment** | Data Practitioner, Governance Officer | Extends `concept_coverage_gaps` | Broadened from concept completeness gaps to full quality rule pass/fail analysis with Vega-Lite chart output. Argument: `domain` (required). |
| 3 | **Entity Ownership Review** | CDO, Governance Officer | New — no MCP equivalent | Surfaces all entities missing a data owner, or where the assigned owner has left the organisation. Returns a table and a remediation prompt. No arguments. |
| 4 | **Classification Compliance Audit** | Governance Officer, Data Practitioner | Extends `find_pii_attributes` | Expanded from PII-only to full classification label audit — finds unclassified entities, misclassified assets, and entities missing a sensitivity tier. Argument: optional `classification_tier`. |
| 5 | **New User Orientation** | New User / Onboarder | Extends `onboard_me` | Rewritten from data-model tour to DDA platform orientation for non-technical users. Explains governance concepts in plain language, lists the user's owned entities (if any), and suggests first actions. No arguments. |

**Not carried forward from MCP prompts:**
- `trace_lineage` — available as a natural-language MCP tool call; not needed as a guided workflow
- `compare_concepts` — available via `@`-binding two entities; not needed as a guided workflow

See [ROADMAP.md](./ROADMAP.md) for planned additions to the guided workflow library.

---

## Tool call transparency

Every MCP tool invocation renders as a **collapsible disclosure card** in the conversation thread. This is mandatory — tool calls are never hidden (P1 — governance-first transparency).

### Disclosure card anatomy

```
┌─────────────────────────────────────────────────────┐
│ 🔧 DDA MCP · list_entities          ✓ 12 results  ▼ │
└─────────────────────────────────────────────────────┘
```

On expansion:

```
┌─────────────────────────────────────────────────────┐
│ 🔧 DDA MCP · list_entities          ✓ 12 results  ▲ │
├─────────────────────────────────────────────────────┤
│ Input parameters                                    │
│   domain: "Finance"                                 │
│   classification: "Gold"                            │
│   limit: 50                                         │
├─────────────────────────────────────────────────────┤
│ Response status: 200 OK · 145ms                     │
│ Result: 12 entities returned (total: 12)            │
└─────────────────────────────────────────────────────┘
```

| Card element | Content |
|-------------|---------|
| Tool name | MCP server name + tool name (e.g. `DDA MCP · list_entities`) |
| Status icon | ✓ success / ✗ error / ⏳ in-progress |
| Result summary | Brief outcome (e.g. `12 results`, `error: permission denied`) |
| Expand/collapse | Chevron — collapsed by default |
| Input parameters | Full parameter object |
| Response status | HTTP status code + latency |
| Result detail | Full result summary or error detail |

### Error states in disclosures

When a tool call fails, the disclosure card shows error status with full detail. The model surfaces the error to the user in plain language, citing the specific tool and the nature of the failure.

MCP server unavailability triggers a **degraded-mode banner** on the session — the session continues in text-only mode from system prompt context. No silent failure. The banner is persistent until connectivity is restored.

---

## Tool access in shared sessions

The active model and enabled opt-in tools apply to the session as a whole. The user who submits a message determines the tool context for that turn based on their current tool panel state. Other participants see the tool call disclosure cards in the thread.

Participants cannot access MCP tools beyond their own DDA permission level. If a tool call succeeds for the submitting user but would return restricted data for another participant, the other participant sees the disclosure card with a `[Restricted — insufficient permissions]` notice on the result summary.
