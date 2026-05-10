# 00 — Host Application Configuration

Every tenant on the AI Chat Platform is defined by a **JSON application config** provided by the host application at registration time. The config is the single source of truth for how the assistant behaves within that application — its identity, scope, tools, bindings, workflows, branding, and feature flags.

---

## Config delivery

Configs are registered and updated via the **Platform Admin API** (authenticated by a platform API key scoped to the tenant). A web-based **Config Editor UI** provides a visual wrapper over the same API for non-technical Application Admins. Both target the same config document — there is no divergence between API and UI state.

Config takes effect on the **next new conversation session** after the update is applied. Active sessions are not interrupted by config changes.

---

## Config schema

```json
{
  "$schema": "https://chat-platform.io/config/v1/schema.json",
  "version": "1.0.0",

  "identity":      { ... },
  "branding":      { ... },
  "scope":         { ... },
  "bindableTypes": [ ... ],
  "mcpServers":    [ ... ],
  "workflows":     [ ... ],
  "renderers":     [ ... ],
  "models":        { ... },
  "userProfile":   { ... },
  "memory":        { ... },
  "conversations": { ... },
  "features":      { ... }
}
```

---

## `identity`

```json
{
  "identity": {
    "tenantId":             "acme-corp",
    "applicationName":      "Acme Data Hub",
    "assistantName":        "Atlas",
    "assistantDescription": "Your data governance assistant for Acme Corp.",
    "supportUrl":           "https://help.acme.com/atlas",
    "privacyPolicyUrl":     "https://acme.com/privacy"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `tenantId` | Yes | Unique slug identifier for this tenant on the platform |
| `applicationName` | Yes | Name of the host application — shown in platform admin UI |
| `assistantName` | Yes | The name end users see for the assistant (e.g. "Atlas", "Nova", "Sage") |
| `assistantDescription` | Yes | One-sentence description shown in the onboarding welcome state |
| `supportUrl` | No | URL linked from error states for end-user support |
| `privacyPolicyUrl` | No | URL displayed in the memory consent UI |

---

## `branding`

Design tokens applied to the `<ai-chat>` web component. The platform's default design system is used for any token not provided.

```json
{
  "branding": {
    "colorPrimary":        "#0057B8",
    "colorSurface":        "#FFFFFF",
    "colorSurfaceVariant": "#F4F6F9",
    "colorOnSurface":      "#111827",
    "colorAccent":         "#00A86B",
    "fontFamily":          "Inter, system-ui, sans-serif",
    "borderRadius":        "8px",
    "logoUrl":             "https://cdn.acme.com/logo.svg",
    "faviconUrl":          "https://cdn.acme.com/favicon.ico"
  }
}
```

All colour values accept hex, RGB, or HSL. Logo assets must be SVG or PNG and served from a CSP-compatible origin declared in the host's Content Security Policy. See [16-embedding-and-web-component.md](./16-embedding-and-web-component.md) for CSP requirements.

---

## `scope`

Defines the assistant's domain, what it should decline, and how it handles out-of-scope queries.

```json
{
  "scope": {
    "systemPrompt": "You are Atlas, the data governance assistant for Acme Corp. You help users find, understand, and act on data assets governed by the Acme Data Hub platform...",
    "inScopeDescription": "Data assets, governance policies, quality metrics, and data ownership within Acme Corp",
    "outOfScopeRedirect": "I'm here to help with Acme Corp's data governance. For general questions, please contact your team's relevant resource.",
    "language": "en"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `systemPrompt` | Yes | Base system prompt for the assistant. The platform appends tool descriptions, memory blocks, and platform-managed safety instructions. |
| `inScopeDescription` | Yes | Plain-language description of scope; used in the onboarding state and out-of-scope redirect messages |
| `outOfScopeRedirect` | No | Custom message for out-of-scope queries. The platform uses a generic fallback if not set. |
| `language` | No | BCP 47 language tag (default: `en`). Applies to UI strings and the assistant's response language hint. |

### System prompt authoring guidelines

- Establish the assistant's persona and domain clearly in the first 200 tokens
- Do not include tool descriptions — they are injected automatically at session start
- Do not include memory blocks — injected automatically
- Do not attempt to override platform safety, audit, or tool-transparency instructions
- Keep under 3,000 tokens to leave headroom for injected context, memory blocks, and tool descriptions
- Avoid referencing specific MCP tool names — describe capabilities in natural language so the model chooses the right tool

---

## `bindableTypes`

Defines the object types that end users can reference via `@`-binding in the input field. The platform provides the `@`-binding mechanism; the host defines what can be bound.

```json
{
  "bindableTypes": [
    {
      "id":              "data_domain",
      "label":           "Data Domain",
      "pluralLabel":     "Data Domains",
      "icon":            "database",
      "searchEndpoint":  "https://api.acme.com/chat/search/domains",
      "contextTemplate": "Data Domain: {{name}} (ID: {{displayId}})\nOwner: {{owner}}\nDescription: {{description}}",
      "displayIdPattern": "DOM-[0-9]+",
      "rank":            1
    },
    {
      "id":              "policy",
      "label":           "Policy",
      "pluralLabel":     "Policies",
      "icon":            "shield",
      "searchEndpoint":  "https://api.acme.com/chat/search/policies",
      "contextTemplate": "Policy: {{name}}\nStatus: {{status}}\nEffective: {{effectiveDate}}\nSummary: {{summary}}",
      "rank":            2
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier for this type within the tenant |
| `label` | Yes | Singular display label shown in the typeahead panel |
| `pluralLabel` | Yes | Plural label used in empty states and section headers |
| `icon` | No | Platform icon name or absolute URL for the chip icon |
| `searchEndpoint` | Yes | Host-provided HTTPS endpoint the platform calls to resolve `@`-binding searches. Must accept a `?q=` query parameter and return `{ items: [{ id, name, displayId?, inactive? }] }`. Called with the user's bearer token forwarded — the host endpoint enforces its own permission filtering. |
| `contextTemplate` | Yes | Mustache template for the context block injected into the model prompt when this binding is resolved. Use `{{fieldName}}` for any field returned by the search endpoint's item objects. |
| `displayIdPattern` | No | Regex; pasted text matching this pattern triggers an auto-lookup confirmation prompt |
| `rank` | No | Sort order in typeahead results (ascending). Defaults to alphabetical by label if omitted. |

### Permission model for bindable types

The `searchEndpoint` is called with the authenticated user's bearer token forwarded in the `Authorization` header. The host endpoint is responsible for filtering results to objects the user is permitted to access. The platform does not enforce bindable-type permissions independently — it trusts the host's endpoint response.

In shared conversations, if a binding chip resolves to an object another participant cannot access (because that participant's search endpoint would not have returned it), the restricted participant sees the chip labelled **[Restricted object]**. See [08-shared-conversations.md](./08-shared-conversations.md).

---

## `mcpServers`

Registers the MCP servers available within this tenant. The platform assumes no MCP servers by default — hosts must register at least one for the assistant to be useful beyond its system prompt knowledge.

Host teams can discover and browse available MCP servers in the **MCP Repository** (see [17-complementary-mcp-services.md](./17-complementary-mcp-services.md)) before registering them here.

```json
{
  "mcpServers": [
    {
      "id":          "governance-mcp",
      "name":        "Governance Platform",
      "description": "Provides access to data governance entities, quality metrics, ownership records, and policy objects. Use for any question about data assets, governance status, or compliance.",
      "endpoint":    "https://api.acme.com/mcp/governance",
      "authType":    "bearer",
      "accessTier":  "always-on",
      "roles":       []
    },
    {
      "id":          "warehouse-mcp",
      "name":        "Data Warehouse",
      "description": "Read-only access to the Acme data warehouse. Use to answer questions about actual data values, row counts, and sample records.",
      "endpoint":    "https://api.acme.com/mcp/warehouse",
      "authType":    "bearer",
      "accessTier":  "opt-in",
      "roles":       ["data_practitioner", "admin"]
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tenant |
| `name` | Yes | Display name shown in the tool selection panel |
| `description` | Yes | Plain-language description injected into the system prompt when the tool is active. Write it for the model — describe what it provides and when to use it. |
| `endpoint` | Yes | MCP-compliant HTTPS endpoint URL |
| `authType` | Yes | `bearer` — the user's host JWT is forwarded; `api-key` — the platform holds a key per tenant (configured separately in the Admin API); `none` — no authentication |
| `accessTier` | Yes | `always-on` — active in every session, cannot be disabled by the end user; `opt-in` — off by default, user enables per session via the tool selection panel |
| `roles` | No | Array of host-defined role identifiers (from user profile claims). If populated, only users whose role claim includes one of these values can see or activate this server. Empty array = available to all users. |

A tenant may have multiple `always-on` servers. If no `always-on` servers are configured, the platform operates in **prompt-only mode** — the assistant answers from system prompt knowledge only, with no live tool access.

---

## `workflows`

Guided workflows are host-defined conversation starters that launch a structured multi-turn interaction. They appear in the **Workflow Library** panel and as optional starters on the onboarding screen.

```json
{
  "workflows": [
    {
      "id":          "governance-health-check",
      "name":        "Governance Health Check",
      "description": "Summarise governance coverage, quality gaps, and policy compliance across a selected domain.",
      "icon":        "activity",
      "prompt":      "Run a governance health check for {{domain}}. Cover: (1) entity coverage, (2) data quality completeness, (3) ownership gaps, (4) classification compliance. Present as an executive summary with a traffic-light status for each area.",
      "parameters": [
        {
          "id":             "domain",
          "label":          "Data Domain",
          "type":           "binding",
          "bindableTypeId": "data_domain",
          "required":       true
        }
      ],
      "roles": []
    },
    {
      "id":          "weekly-status",
      "name":        "Weekly Status Report",
      "description": "Generate a plain-language weekly status summary for a selected team.",
      "icon":        "calendar",
      "prompt":      "Generate a weekly status report for {{team}}. Summarise open actions, recent completions, and any blockers.",
      "parameters": [
        {
          "id":       "team",
          "label":    "Team",
          "type":     "text",
          "required": true
        }
      ],
      "roles": []
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tenant |
| `name` | Yes | Display name in the Workflow Library |
| `description` | Yes | One-sentence description shown in the library and onboarding |
| `icon` | No | Platform icon name or URL |
| `prompt` | Yes | Mustache template for the prompt submitted on launch. References `parameters` by their `id`. |
| `parameters` | No | Parameters collected from the user before the workflow launches. Types: `binding` (opens an `@`-binding typeahead scoped to a `bindableTypeId`), `text` (free text field), `select` (dropdown; include an `options` array of `{ value, label }` objects) |
| `roles` | No | Role restriction. Empty array = available to all authenticated users. |

Workflow prompts are host-managed — users cannot create or modify them.

---

## `renderers`

Host applications may register **custom content renderers** that the platform loads at runtime. When the model produces a fenced code block tagged with a registered renderer's trigger, the platform invokes the host's renderer instead of its built-in pipeline. This enables domain-specific visualisations — risk gauges, org charts, Gantt views, financial waterfall charts, compliance scorecards — that the platform's built-in renderers do not cover.

See [10-content-rendering.md](./10-content-rendering.md) for the full runtime rendering contract and system prompt guidance injection.

```json
{
  "renderers": [
    {
      "id":                   "risk-gauge",
      "trigger":              "risk-gauge",
      "name":                 "Risk Gauge",
      "description":          "Interactive risk score gauge with traffic-light colouring",
      "moduleUrl":            "https://cdn.acme.com/ai-renderers/risk-gauge.js",
      "exportName":           "RiskGaugeRenderer",
      "systemPromptGuidance": "Use a ```risk-gauge block when asked for a risk score or risk assessment. The block must contain a JSON object: { \"score\": <0–100>, \"label\": \"<risk level label>\", \"breakdown\": [ { \"factor\": \"<name>\", \"score\": <0–100> } ] }. Only use this block when a numeric risk score is directly requested."
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tenant |
| `trigger` | Yes | Fenced code block tag that activates this renderer (e.g. `risk-gauge` → ` ```risk-gauge ` in the model output). Must be lowercase alphanumeric with hyphens; must not conflict with a built-in trigger (`mermaid`, `vega-lite`, `math`, `json`, `csv`, `table`). |
| `name` | Yes | Display name shown in the platform admin UI and in the content block header within the conversation thread |
| `description` | Yes | One-sentence description shown in the admin UI. Not injected into the system prompt. |
| `moduleUrl` | Yes | HTTPS URL to an ES module exporting the renderer. Must be served from an origin declared in the tenant's registered origins. Loaded once per session; cached for the session lifetime. |
| `exportName` | No | Named export from the module. Default: `"default"`. |
| `systemPromptGuidance` | No | Text injected verbatim into the system prompt to instruct the model when and how to produce this content type. Include the expected fenced block format and any content schema the renderer requires. If omitted, the platform injects a minimal generic instruction: *"You may produce `{trigger}` blocks using ` ```{trigger} ` fencing."* |

### Origin registration

The `moduleUrl` origin must be declared during tenant registration (or updated via the Platform Admin API). At config submission, the platform validates that the declared origin is reachable and that the module can be loaded. Modules served from unregistered origins are rejected. The host's CSP `script-src` must include the renderer origin — see [16-embedding-and-web-component.md](./16-embedding-and-web-component.md).

---

## `models`

```json
{
  "models": {
    "defaultModel":  "claude-sonnet-4-6",
    "allowedModels": ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5"],
    "userCanSwitch": true,
    "provider":      "anthropic"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `defaultModel` | Yes | Model used for new conversations unless the user switches |
| `allowedModels` | Yes | Array of model IDs users may switch to. Must include `defaultModel`. |
| `userCanSwitch` | No | Whether users can switch models mid-conversation (default: `true`). Set to `false` to lock all sessions to `defaultModel`. |
| `provider` | Yes | AI provider identifier. v1 supports `anthropic` only. Planned: `openai`, `gemini`. |

---

## `userProfile`

Describes how the platform should interpret user-profile claims for communication style personalisation. These claims are passed via the authentication bridge (see [16-embedding-and-web-component.md](./16-embedding-and-web-component.md)).

```json
{
  "userProfile": {
    "styleField": "communication_style",
    "styleValues": {
      "technical":  "Respond with technical precision. Include field names, IDs, and system details.",
      "business":   "Respond in plain business language. Avoid jargon. Use analogies where helpful.",
      "executive":  "Respond concisely in three to five sentences. Lead with the conclusion. Omit process detail."
    },
    "verbosityField": "response_verbosity",
    "verbosityValues": {
      "concise":   "Keep responses to the essential point. Tables preferred over prose lists.",
      "standard":  "Provide sufficient context for the response to stand alone.",
      "detailed":  "Include full explanation, examples, and supporting detail."
    }
  }
}
```

The `styleField` and `verbosityField` values must match claim keys passed in the user's JWT payload via the authentication bridge. If a user's JWT contains no matching claim, the platform uses its default tone (no style injection). If `userProfile` is omitted from the config entirely, style personalisation is disabled for the tenant.

---

## `memory`

Configures the memory system for this tenant. See [15-memory-and-recall.md](./15-memory-and-recall.md) for the full behaviour specification.

```json
{
  "memory": {
    "personalMemory": {
      "enabled":    true,
      "defaultOn":  false,
      "categories": ["Role", "Preference", "Correction", "Context"],
      "tokenBudget": 2000
    },
    "applicationContext": {
      "enabled":          true,
      "categories":       ["Terminology", "Policy", "Structure", "Domain context"],
      "tokenBudget":      4000,
      "approvalRequired": true
    }
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `personalMemory.enabled` | `true` | Enable the personal memory feature for this tenant |
| `personalMemory.defaultOn` | `false` | Whether personal memory injection is on or off when a user first enables it |
| `personalMemory.categories` | `["Role","Preference","Correction","Context"]` | Category labels for personal memory items (displayed in the management UI) |
| `personalMemory.tokenBudget` | `2000` | Maximum tokens for personal memory in the system prompt |
| `applicationContext.enabled` | `true` | Enable Application Context (tenant-wide org memory) |
| `applicationContext.categories` | `["Terminology","Policy","Structure","Domain context"]` | Category labels for application context items |
| `applicationContext.tokenBudget` | `4000` | Maximum tokens for application context in the system prompt |
| `applicationContext.approvalRequired` | `true` | Require a two-user approval workflow for new application context items |

---

## `conversations`

```json
{
  "conversations": {
    "maxTurnLimit":                 100,
    "maxParticipants":              10,
    "retentionDays":                1095,
    "allowSharing":                 true,
    "allowAttachments":             true,
    "maxAttachmentMbPerFile":       10,
    "maxAttachmentMbPerConversation": 100
  }
}
```

All fields have platform defaults (shown above). Hosts may lower limits but not exceed platform-level maximums.

---

## `features`

Feature flags that enable or disable platform capabilities for this tenant.

```json
{
  "features": {
    "atBinding":            true,
    "displayIdDetection":   true,
    "guidedWorkflows":      true,
    "sharedConversations":  true,
    "personalMemory":       true,
    "applicationContext":   true,
    "csatSurvey":           true,
    "csatSampleRate":       0.20,
    "artefactTray":         true,
    "starterWorkflows":     ["governance-health-check"],
    "starterQuestions": [
      "What are the highest-priority issues right now?",
      "Show me anything that needs my attention.",
      "What does my team own and are there any gaps?"
    ]
  }
}
```

| Flag | Default | Description |
|------|---------|-------------|
| `atBinding` | `true` | Enable `@`-binding typeahead. Requires at least one `bindableType` to be configured. |
| `displayIdDetection` | `true` | Enable auto-detection of pasted Display IDs matching `displayIdPattern` values |
| `guidedWorkflows` | `true` | Enable the Workflow Library panel. Requires at least one `workflow` to be configured. |
| `sharedConversations` | `true` | Enable conversation sharing with other users in the same tenant |
| `personalMemory` | `true` | Enable personal memory feature |
| `applicationContext` | `true` | Enable Application Context (managed by Application Admin) |
| `csatSurvey` | `true` | Enable post-session CSAT rating prompt |
| `csatSampleRate` | `0.20` | Fraction of sessions shown the CSAT prompt (0.0–1.0) |
| `artefactTray` | `true` | Enable the session artefact tray panel |
| `starterWorkflows` | `[]` | Workflow IDs shown as suggested starters on the onboarding screen (references `workflows[].id`) |
| `starterQuestions` | `[]` | Plain-text starter questions shown on onboarding (up to 3, shown only if `starterWorkflows` is empty or alongside them) |

---

## Config versioning

The config document uses semantic versioning in the `version` field:

| Change type | Increment | Example |
|-------------|-----------|---------|
| Description or prompt text edits; branding token updates | **Patch** | `1.0.0` → `1.0.1` |
| New bindable type, new MCP server, new workflow, new feature flag value | **Minor** | `1.0.0` → `1.1.0` |
| Structural schema changes; renamed or removed top-level fields | **Major** | `1.0.0` → `2.0.0` |

The platform stores a full version history for each tenant's config. Rollback to any prior version is available via the Platform Admin API.

---

## Config validation

Submitting a config via the Admin API runs **synchronous validation** before applying:

| Check | Description |
|-------|-------------|
| Schema conformance | All required fields present; field types match schema |
| Endpoint reachability | MCP server endpoints and `searchEndpoint` URLs respond to a health check |
| System prompt token count | Must be under 3,000 tokens |
| Model IDs in `allowedModels` | Must be available in the platform for the configured `provider` |
| `contextTemplate` syntax | Mustache syntax check for all bindable type templates |
| `starterWorkflows` references | All IDs in `starterWorkflows` must match a `workflows[].id` |
| Renderer trigger uniqueness | No two renderers may share the same `trigger`; no renderer `trigger` may match a built-in tag |
| Renderer module reachability | Each `moduleUrl` must respond to a HEAD request from the platform's validation origin; the origin must be registered for the tenant |

Validation errors return a structured response with field-level detail. The config is not applied until all validation checks pass.
