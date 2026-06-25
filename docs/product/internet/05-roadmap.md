# 05 — Roadmap

**Product:** MAOS Internet Access MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## MVP — Initial Release

The MVP establishes the core capability pair — search and fetch — with the content safety controls necessary for enterprise deployment. The MVP is deployable as production infrastructure immediately upon release.

**Search**
- Query submission and ranked result return
- Configurable result count and time range filtering
- Pluggable search backend (self-hosted metasearch or search API)
- Entitlement filtering applied to results before return

**Fetch**
- URL fetch with output format selection: raw and markdown
- Boilerplate stripping and HTML-to-Markdown conversion
- Configurable timeout and error handling
- Entitlement checks before fetch execution

**Entitlements**
- Domain allow list and deny list
- URL pattern rules
- Configurable default posture (open or closed)
- Policy rejection responses with reason

**Site Classification**
- Integration with at least one open threat feed (Google Safe Browsing, URLhaus, or equivalent)
- Safety flag enforcement: malware, phishing blocked by default
- Classification metadata returned alongside results and fetch responses
- Configurable classification threshold policy

**Operational Foundations**
- stdio and HTTP/SSE transport
- Audit logging to stdout and file
- Docker packaging with environment-variable configuration
- Health and readiness endpoints
- Rate limiting per caller

---

## v1 — Capability Completion

v1 completes the fetch output format set, extends classification coverage, and adds authenticated fetch for enterprise identity providers.

**Fetch extensions**
- Chunked output format with pagination support
- Summarized output format (requires configured LLM backend)
- Browser automation backend for JavaScript-rendered pages
- PDF and document fetch and parsing

**Classification extensions**
- Integration with commercial classification database (zvelo, BrightCloud/OpenText, or equivalent)
- Multi-provider classification with most-restrictive-wins logic
- Content category blocking (adult, gambling, hate speech, and configurable categories)
- Reputation score threshold enforcement

**Authenticated Fetch — Enterprise IdP**
- OAuth 2.1 / OIDC token acceptance from enterprise identity providers (Entra ID, Okta)
- On-Behalf-Of (OBO) token exchange for downstream resource access
- Consent registry per user and client scope
- MCP Authorization Specification (2025-11-25) conformance

**Operational extensions**
- External log sink integration (syslog, SIEM)
- Per-tool rate limit configuration
- Configurable log retention policy

---

## v2 — Authenticated Fetch Completion and Ecosystem Integration

v2 extends authenticated fetch to consumer OAuth providers and adds integration surface for enterprise search and classification ecosystems.

**Authenticated Fetch — Consumer OAuth**
- OAuth 2.1 with PKCE for consumer providers: Google, GitHub, and configurable providers
- Cookie/session forwarding for sites without OAuth support
- Dynamic client registration for MCP-compatible clients

**Enterprise search backend**
- Integration with enterprise internal search indexes
- Unified result set combining internal and external search results

**Classification ecosystem**
- Pluggable classification provider API for custom enterprise classification sources
- Classification override rules for enterprise-specific domain policies

**Observability**
- Structured telemetry output (OpenTelemetry)
- Per-tool usage metrics
- Classification decision audit trail with provider attribution

---

## Future Considerations

Capabilities identified as potentially valuable but not yet scheduled:

- Caching layer for frequently accessed pages with configurable TTL
- Search result re-ranking using a local ML model
- Automatic language detection and translation of fetched content
- Webhook or event notification for classification policy violations
- Multi-tenant deployment model with per-tenant entitlement and classification policy isolation
