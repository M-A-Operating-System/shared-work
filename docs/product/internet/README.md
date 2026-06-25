# MAOS Internet Access MCP Server — Technical Specification

**Version:** 1.0 | **Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

This server is the **MCP Internet Fetch & Search** service referenced by the [AI Chat Platform](../assistant/01-overview.md). Host applications register it in their MCP tool registry to give end users controlled access to real-time web search and page fetch during conversations.

---

## Document Index

| # | Document | Contents |
|---|---|---|
| 01 | [Overview](01-overview.md) | Problem, solution, deployment model, layered control model, system context, decisions log |
| 02 | [Core Capabilities](02-core-capabilities.md) | Detailed specification of all five capability areas: search, fetch, entitlements, site classification, authenticated fetch |
| 03 | [Server Surface](03-server-surface.md) | MCP capability declaration, tool definitions with input schemas and response shapes, error format |
| 04 | [Technical Constraints and Deployment](04-technical-constraints-and-deployment.md) | MCP protocol conformance, pluggable backend architecture, compliance, operational requirements |
| 05 | [Roadmap](05-roadmap.md) | MVP through v2 and future considerations |
| 06 | [Open Decisions](06-open-decisions.md) | Decisions that must be resolved before or during build, with priority |

---

## Quick Reference

**Tools:**

| Tool | Available From | Description |
|---|---|---|
| `search` | MVP | Web search returning ranked, filtered results |
| `fetch` | MVP | Page fetch in raw, markdown, chunked, or summarized format |
| `fetch_authenticated` | v1 | Fetch with enterprise IdP or consumer OAuth credentials |

**Key rules:**
- All requests are subject to entitlement and site classification checks before content is returned
- Server-managed controls are additive to enterprise perimeter controls, not a replacement
- Authentication does not bypass entitlement or classification policy
- Search backend, fetch backend, classification backend, and LLM backend are all pluggable at deployment time
- OAuth 2.1 + PKCE required for remote deployments; RFC 8707 resource binding enforced

---

## References

| Resource | URL |
|---|---|
| MCP Specification 2025-03-26 | https://modelcontextprotocol.io/specification/2025-03-26 |
| MCP Authorization Specification 2025-11-25 | https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization |
| OAuth 2.1 | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1 |
| OAuth 2.0 Token Exchange (OBO) | https://datatracker.ietf.org/doc/html/rfc8693 |
| RFC 8707 Resource Indicators | https://datatracker.ietf.org/doc/html/rfc8707 |
