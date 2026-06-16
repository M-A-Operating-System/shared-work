# Internet Access MCP Server — Decisions Log

**Version:** 1.0
**Date:** June 2026
**Status:** Target State Design

---

Significant product decisions made during the discovery and design session.

| Topic | Decision | Rationale |
|---|---|---|
| Product framing | The server is a general-purpose MCP infrastructure component, not a product tied to any specific platform or application stack | Ensures broad applicability across enterprise deployments and avoids coupling the design to any single consuming system |
| Scope — MVP capabilities | Search and fetch are the MVP. Entitlements and site classification are included in MVP as safety controls, not Phase 2 features | Site classification is a content safety and data security control, not an enrichment feature. Enterprise deployment without content safety controls is not acceptable. |
| Site classification role | Classification is a safety gate — content that fails classification is blocked server-side before being returned to the LLM | LLMs must not consume dangerous, malicious, or policy-violating content. Classification enforcement belongs at the server layer, not delegated entirely to the consuming agent or UI. |
| Classification metadata return | Classification metadata is returned alongside permitted content in all responses, even when content passes the safety threshold | Enables consuming agents and UIs to make their own downstream policy decisions in addition to the server's enforcement |
| Fetch output formats | Four output formats in target state: raw, markdown, chunked, summarised | Different consumers have different needs — agents processing content need markdown; large pages need chunking; bandwidth-constrained or summary-oriented interactions need summarisation; raw is required for callers doing their own parsing |
| Layered control model | The server's entitlement and classification controls are explicitly additive to enterprise perimeter controls, not a replacement | Enterprises already have network and identity controls. The server addresses the AI-specific access surface on top of that foundation — it does not attempt to replace what the enterprise already enforces |
| Authenticated fetch scope | Target state covers both enterprise IdP (Entra ID, Okta, OIDC) and consumer OAuth providers (Google, GitHub). MVP does not include authenticated fetch. | Authenticated fetch is technically complex and requires significant OAuth implementation. The core value — public internet search and fetch — does not depend on it. It is correctly a v1 and v2 capability. |
| Token handling | OAuth 2.0 OBO flow for enterprise IdP; OAuth 2.1 with PKCE for consumer providers; no token passthrough permitted | Follows MCP Authorization Specification (2025-11-25) and OAuth 2.1 security requirements. Token passthrough is an explicit anti-pattern in the MCP security model. |
| Search backend | Pluggable — the server abstracts the backend behind a standard interface | Prevents vendor lock-in and allows enterprises to deploy with zero external API dependency using a self-hosted metasearch backend |
| Classification backend | Pluggable — multiple providers configurable; most restrictive wins | Allows enterprises to combine open feeds with commercial databases; most-restrictive-wins prevents gaps between providers from creating safety holes |
| Document set | Five documents: Overview, Core Capabilities, Technical Constraints and Deployment, Roadmap, Open Decisions | The product is an infrastructure MCP server. It does not have onboarding flows, notification systems, or account structures. The standard 14-document spec template is over-engineered for this product type. |
