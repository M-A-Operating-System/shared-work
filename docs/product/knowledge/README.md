# MAOS Knowledge MCP Server — Technical Specification

**Version:** 1.0 | **Date:** 2026-06-16 | **Protocol:** MCP 2025-06-18  
**Author:** Andrew Bush / M&A Operating System

---

## Document Index

| # | Document | Contents |
|---|---|---|
| 01 | [Overview](01_overview.md) | Problem, design principles, system context, stack, decisions log, open decisions |
| 02 | [Knowledge Directory and Content Types](02_knowledge_directory_and_content_types.md) | Folder layout, URI scheme, file schemas and rendering contracts for all five content types |
| 03 | [Server Surface](03_server_surface.md) | MCP primitives (resources, prompts, notifications) and all ten tools with input schemas and response shapes |
| 04 | [Implementation Reference](04_implementation_reference.md) | Security model, project structure, key modules with typed Python, Docker deployment |
| 05 | [Client Integration Guide](05_client_integration_guide.md) | Connection, common patterns, per-consumer guidance, error handling, roadmap |
| — | [Roadmap](roadmap.md) | Version-by-version evolution from embedded single-app deployment through centralised platform, semantic search, and governed authoring |

---

## Quick Reference

**Endpoint:** `https://knowledge-mcp.maoperatingsystem.com/mcp`

**URI root:** `file:///knowledge/{domain}/{subdomain}/{app}/{kind}/{+path}`

**Content types and folders:**

| Kind | Folder | File Types |
|---|---|---|
| Resource | `resources/` | Any |
| Prompt | `prompts/` | `.prompt.md`, `.prompt.json` |
| Skill | `skills/{name}/` | `SKILL.md` + support files |
| Command | `commands/` | `.cmd.md`, `.cmd.json` |
| Agent | `agents/` | `.agent.md`, `.agent.json` |

**Tools:**

```
search_knowledge    search*
search_resources    search_prompts
search_skills       search_commands
search_agents
get_skill           get_command
list_agents         load_agent
get_resource        get_prompt
```
* search — v2, requires pgvector infrastructure

**Key rules:**
- All URIs must begin with `file:///knowledge/`
- Trailing-slash folder URIs return directory listings from any tool or primitive
- Server is read-only — no tool writes to the knowledge directory
- OAuth 2.1 + PKCE required; tokens bound to this server via RFC 8707
- Chunk retrieval is an extension of `get_resource` — supply a `query` parameter to receive ranked sections instead of the full file. No separate tool exists for chunking.
- `MCP-Protocol-Version: 2025-06-18` header required on all HTTP requests

---

## References

| Resource | URL |
|---|---|
| MCP Specification 2025-06-18 | https://modelcontextprotocol.io/specification/2025-06-18 |
| MCP Resources | https://modelcontextprotocol.io/specification/2025-06-18/server/resources |
| MCP Prompts | https://modelcontextprotocol.io/specification/2025-06-18/server/prompts |
| MCP Tools | https://modelcontextprotocol.io/specification/2025-06-18/server/tools |
| MCP Lifecycle | https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle |
| Python MCP SDK | https://github.com/modelcontextprotocol/python-sdk |
| OAuth 2.1 | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1 |
| RFC 8707 Resource Indicators | https://datatracker.ietf.org/doc/html/rfc8707 |
