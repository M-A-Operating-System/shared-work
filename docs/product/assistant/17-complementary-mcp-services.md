# 17 — Complementary MCP Services

The AI Chat Platform assumes the availability of three ecosystem-level MCP services that operate alongside the platform and host application MCP servers. These services are not owned or operated by the AI Chat Platform itself, nor by individual host applications — they are shared infrastructure within the broader MCP ecosystem. The platform is designed to work with them, and host applications are expected to benefit from them, but none is a hard dependency for platform operation.

---

## MCP Repository

### Overview

The **MCP Repository** is a centralised, discoverable catalogue of MCP servers available within the ecosystem. It serves as the primary discovery mechanism for host teams when they are configuring their tenant's MCP tool registry — providing a searchable directory of tools that have already been built, tested, and published, rather than requiring every host team to build their own MCP servers from scratch.

The MCP Repository is a **config-time service**: host teams use it when setting up or updating their application config, not as a runtime tool invoked during user conversations. Its value is in accelerating the time between "we want to add this capability to our assistant" and "this capability is live for our users."

### What the MCP Repository provides

The MCP Repository holds metadata records for each published MCP server, including:

- **Server identity:** Name, publisher, version, and a plain-language description of what the server provides
- **Capability catalogue:** The specific tools exposed by the server, with descriptions and example invocations
- **Integration metadata:** The server's MCP endpoint URL, supported authentication types (`bearer`, `api-key`, `none`), and any pre-conditions for integration (e.g. required host-side configuration)
- **Quality indicators:** Verification status, uptime history, average latency, and known compatibility notes with the AI Chat Platform
- **Suggested descriptions:** Pre-written `description` field text optimised for injection into the AI Chat Platform's system prompt — host teams can use these as-is or customise them

### How host teams use the MCP Repository

When a host team wants to add a new capability to their assistant, the typical flow is:

1. Search the MCP Repository for a server that provides the needed capability
2. Review the server's capability catalogue and quality indicators
3. Copy the server's endpoint URL, suggested `description`, and recommended `authType` into the `mcpServers` entry in the application config
4. Submit the updated config via the Config Editor UI or Admin API — the platform validates endpoint reachability as part of config submission
5. Monitor tool invocation quality via improvement signals in the first weeks of use

### Publishing to the MCP Repository

MCP server publishers — whether internal platform teams, host application developers, or third parties — submit their server records via the MCP Repository's submission API. Submitted records are reviewed for:
- Correctness and completeness of metadata
- MCP protocol compliance
- Endpoint stability and availability
- Security posture (auth requirements, data exposure scope)

Approved records are published and immediately searchable in the Repository. Publishers are responsible for keeping their records current as their server's endpoint or capability changes.

### Relationship to the per-tenant tool registry

The MCP Repository and the per-tenant tool registry ([13-mcp-tool-registry.md](./13-mcp-tool-registry.md)) are distinct:

| MCP Repository | Per-tenant registry |
|---------------|---------------------|
| Ecosystem-wide catalogue of all available servers | Tenant-specific list of servers active for that host application |
| Read at config time by host teams | Resolved at session runtime by the platform |
| Covers all publishers and server types | Covers only what the host application has chosen to enable |
| Not invoked during user conversations | The source of truth for what tools a session can use |

---

## MCP Resources Service

### Overview

The **MCP Resources Service** is a centralised MCP server that provides shared, reusable assets across the MCP ecosystem — skills, guidance documents, prompt templates, and other static artefacts that are useful across many different host applications and conversation types.

Unlike the MCP Repository (which helps teams find and configure tools at setup time), the MCP Resources Service is a **runtime service** — it can be registered as an MCP server in a tenant's tool registry and invoked during user conversations to retrieve resources on demand.

### What the MCP Resources Service provides

The MCP Resources Service organises its content into three categories:

**Skills**
Pre-built structured reasoning patterns that the assistant can invoke to approach complex tasks consistently. Skills are prompt fragments with defined input parameters and expected output structures. Examples include:
- Structured root-cause analysis prompts
- Stakeholder communication drafting frameworks
- Risk assessment scoring rubrics
- Data quality evaluation methodologies

Skills are not model-specific — they are designed to work across Anthropic, OpenAI, and Gemini models. When the assistant retrieves a skill from the MCP Resources Service, it uses the skill's prompt structure to guide its reasoning for that turn.

**Guidance documents**
Static reference documents that apply across many host applications and are impractical for each host to maintain independently. Examples include:
- AI assistant usage guidelines and responsible use principles
- Data privacy handling guidance for AI-assisted workflows
- Model capability and limitation reference cards
- Prompt engineering best practices for domain-specific applications
- **Uncertainty handling guidance** — instructions for how the assistant should communicate the limits of its knowledge, signal when data may be outdated, and offer next steps (such as web search) when it cannot answer with confidence. This document is injected as a resource at session start by hosts that want consistent, domain-appropriate uncertainty behaviour beyond the platform's non-overridable baseline.

Guidance documents are versioned by the MCP Resources Service. When retrieved in a conversation, the document version is recorded in the tool call log.

**Prompt templates**
Reusable prompt structures that host teams can adopt as starting points for guided workflows in their application config. These are published as MCP resource objects and can be retrieved, reviewed, and adapted before being embedded in the `workflows` section of a tenant's config.

### How host applications integrate the MCP Resources Service

Host applications that want their end users to benefit from MCP Resources Service content register the service as an MCP server in their tenant's tool registry — typically as an `opt-in` server, since not every conversation will require it:

```json
{
  "id":          "mcp-resources",
  "name":        "Platform Resources",
  "description": "Provides shared skills, guidance documents, and prompt templates from the platform ecosystem. Use when you need a structured reasoning approach, usage guidance, or reference material.",
  "endpoint":    "https://resources.mcp-ecosystem.io/mcp",
  "authType":    "bearer",
  "accessTier":  "opt-in",
  "roles":       []
}
```

The MCP Resources Service endpoint is published in the MCP Repository. The suggested `description` field text above is available in the Repository record and optimised for AI Chat Platform injection.

### Content governance

The MCP Resources Service is governed by the platform ecosystem team responsible for its operation. Content goes through an editorial review before publication:
- Skills and templates are tested against the platform's AI provider models before publication
- Guidance documents are reviewed for accuracy and applicability across a range of host application types
- All content is versioned; breaking changes to existing resources trigger a deprecation period before removal
- Tenants that have retrieved a specific resource version continue to receive that version until they explicitly update to a newer version

Host applications and their users cannot modify MCP Resources Service content. Feedback and content requests are submitted via the ecosystem's standard issue process.

### Relationship to the platform

The MCP Resources Service is independent of the AI Chat Platform — the platform does not own or operate it. However, the platform is designed to work with it cleanly:
- Resources returned by the service are rendered using the platform's standard content rendering rules (prose, code blocks, data tables as appropriate)
- Resource retrievals appear in the tool call disclosure card with the server name and tool name
- Retrieved resources are added to the session artefact tray for download
- Resource retrievals are included in the tenant's MCP tool error rate metric and improvement signal pipeline

If the MCP Resources Service is unavailable, it behaves like any other unavailable opt-in MCP server — an error is shown in the tool call disclosure card, and the session continues without it.

---

## Web Search Service

### Overview

The **Web Search Service** is an ecosystem-level MCP server that provides the assistant with real-time access to web search results. It is registered as a host application MCP server like any other — the distinction is that it is a shared, ecosystem-managed service rather than a server built and operated by the host team.

Web search complements the platform's primary data access pattern (structured MCP tool calls against the host application's own data) in situations where current information is needed that the host's tools and the model's training knowledge cannot provide — recent news, current pricing, up-to-date documentation, or any query that requires information beyond the host application's data scope.

### What the Web Search Service provides

| Tool | Description |
|------|-------------|
| `web_search` | Executes a web search query and returns a ranked list of results: title, URL, snippet, and publication date |
| `fetch_page` | Retrieves and extracts the readable text content of a specific URL from search results or user-provided links |

Results are returned as structured MCP tool output — they appear in a tool call disclosure card and are cited inline using the platform's standard source citation mechanism (superscript numerals linking to the disclosure card). The model does not present web results as its own knowledge.

### How host applications integrate the Web Search Service

Host applications register the Web Search Service as an MCP server in their tenant tool registry. It is typically configured as `opt-in` — the end user enables it per session when real-time information is needed — though hosts may configure it `always-on` if their use case depends on current information in every session:

```json
{
  "id":          "web-search",
  "name":        "Web Search",
  "description": "Searches the web for current information. Use when the user needs up-to-date facts, recent news, current documentation, or any information beyond the host application's data and the model's training knowledge. Always cite the source URL.",
  "endpoint":    "https://search.mcp-ecosystem.io/mcp",
  "authType":    "api-key",
  "accessTier":  "opt-in",
  "roles":       []
}
```

The Web Search Service endpoint and API key are available from the MCP Repository. The suggested `description` field text above is optimised for system prompt injection and is published in the Repository record.

### Transparency and citation

Web search results follow the platform's mandatory tool call transparency rules — every search invocation and every page fetch appears as a collapsible disclosure card in the conversation thread. The model is instructed (via the platform-managed system prompt layer) to:
- Cite all web-sourced claims with inline source citations linking to the disclosure card
- Acknowledge when search results are recent vs. when the model is supplementing with training knowledge
- Not present search result content as the model's own knowledge

### Relationship to the platform

The Web Search Service is independent of the AI Chat Platform. When unavailable, it behaves like any other unavailable MCP server — an error in the disclosure card and the session continues without it. Web results rendered as prose are subject to the platform's standard content rendering rules; results rendered as structured data (tables, lists) use the platform's data table rendering.
