# Internet Access MCP Server — Technical Constraints & Deployment

**Version:** 1.0
**Date:** June 2026
**Status:** Target State Design

---

## Deployment Context

The server is deployed as self-hosted infrastructure within an enterprise environment. It has no dependency on any external managed service for its core search and fetch capabilities. All components required for operation run within the enterprise's own infrastructure boundary.

The server is designed to run within existing enterprise network and security controls. It does not bypass or replace those controls — it operates within them and adds AI-specific access governance on top.

---

## MCP Protocol Conformance

The server implements the Model Context Protocol specification and exposes capabilities exclusively as MCP tools. It conforms to the MCP Authorization Specification (2025-11-25) for all authenticated interactions.

| Requirement | Implementation |
|---|---|
| MCP tool interface | All capabilities exposed as standard MCP tools |
| Transport: stdio | Supported — for local and single-client deployments |
| Transport: HTTP/SSE | Supported — for remote and multi-client deployments |
| Transport: Streamable HTTP | Supported — MCP spec 2025-03-26 and later |
| OAuth 2.1 with PKCE | Required for authenticated fetch via consumer providers |
| OAuth 2.0 OBO flow | Required for authenticated fetch via enterprise IdP |
| Dynamic client registration | Supported per MCP Authorization Specification |
| Protected resource metadata | Exposed at `/.well-known/oauth-protected-resource` |

---

## Search Backend

The search backend is pluggable. The server abstracts the backend behind a standard internal interface so that the MCP tool surface is identical regardless of which backend is active. The backend is selected and configured at deployment time by the Platform Administrator.

Target state supported backends:

| Backend Type | Description |
|---|---|
| Self-hosted metasearch (e.g. SearXNG) | Aggregates results from multiple search engines; no external API key required; fully self-hosted |
| Search API (e.g. Brave Search, Tavily) | External search API; API key required; managed by the vendor |
| Enterprise search index | Internal enterprise search system; for deployments requiring search over internal and external content |

The server does not require any specific backend. Deployments that require zero external API dependency configure a self-hosted metasearch backend.

---

## Fetch Backend

Static page fetch is performed by the server's own HTTP client. No browser automation is required for static HTML content.

For JavaScript-rendered pages (single-page applications, dynamic content), a browser automation backend is required. The browser automation backend is pluggable and configured at deployment time.

| Content Type | Fetch Mechanism |
|---|---|
| Static HTML | Built-in HTTP client |
| JavaScript-rendered pages | Configured browser automation backend (e.g. Playwright, Puppeteer) |
| PDFs and documents | Built-in document parser |

---

## Site Classification Backend

The classification backend is pluggable. One or more classification providers are configured at deployment time. Where multiple providers are configured, the most restrictive classification result applies.

Target state supported classification sources:

| Source Type | Description |
|---|---|
| Commercial classification database (e.g. zvelo, BrightCloud/OpenText) | High-coverage URL and domain classification with reputation scoring; OEM/partner access required |
| Open threat feeds (e.g. Google Safe Browsing, URLhaus, PhishTank, Spamhaus) | Free or low-cost feeds covering malware, phishing, and spam; primarily security-focused |
| Enterprise classification policy | Custom category and domain rules defined by the enterprise and applied locally |

---

## Summarisation Backend

The summarised fetch output format requires a configured language model backend. The LLM backend is pluggable and configured at deployment time. Deployments that do not configure an LLM backend return an error for summarised fetch requests.

---

## Compliance and Security

| Area | Requirement |
|---|---|
| Token handling | Tokens validated on every request per OAuth 2.1; no token passthrough to downstream services |
| Consent | User consent recorded per client and scope; consent registry maintained server-side |
| Audit logging | All tool calls, entitlement decisions, and classification decisions logged |
| Data in transit | All HTTP communication over TLS |
| Credentials | No credentials stored in plaintext; environment-variable or secrets-manager injection at deploy time |
| GDPR | Search queries and fetch URLs constitute user activity data; log retention policy configurable |
| Enterprise perimeter | Server operates within and subject to enterprise network and identity controls |

---

## Operational Requirements

| Requirement | Detail |
|---|---|
| Deployment packaging | Docker container; environment-variable-driven configuration |
| Configuration surface | All configurable parameters set via environment variables or mounted configuration file; no runtime UI |
| Health endpoint | Exposed health and readiness endpoints for integration with enterprise monitoring |
| Rate limiting | Configurable per caller identity and per tool; enforced server-side |
| Timeout configuration | Per-tool timeouts configurable; defaults provided |
| Log destination | Configurable: stdout, file, or external log sink (e.g. syslog, SIEM integration) |

---

## Locale

The server itself has no locale-specific behaviour. Search result language preferences are passed through to the backend where supported. Fetch content is returned in the language of the source page. No translation capability is provided by the server.

---

## Accessibility

Not applicable. The server exposes no user-facing interface. All interaction is via the MCP tool protocol.
