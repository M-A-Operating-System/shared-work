# 06 — Open Decisions

**Product:** MAOS Internet Access MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

Decisions that must be resolved before or during build. Each decision has a priority indicating the urgency of resolution relative to the build sequence.

| # | Decision Needed | What It Affects | Priority |
|---|---|---|---|
| 1 | Which self-hosted metasearch engine is the reference implementation for MVP search backend? The research identified SearXNG as the strongest candidate but this should be confirmed as the default before build begins. | MVP search capability; deployment documentation; Docker compose configuration | HIGH |
| 2 | Which open threat feed(s) are bundled as the default classification provider in MVP? Google Safe Browsing, URLhaus, and PhishTank are candidates. The selection affects what is blocked by default and the completeness of MVP safety coverage. | MVP site classification; default safety posture; deployment defaults | HIGH |
| 3 | What is the default fetch posture for JavaScript-rendered pages in MVP — fail with an informative error, or partially return available static content? This affects whether a browser automation backend is a hard MVP dependency. | MVP fetch capability; deployment complexity; user experience for JS-heavy sites | HIGH |
| 4 | What is the default entitlement posture — open (deny list only) or closed (allow list required)? This is a security architecture decision that affects how the server behaves on first deployment before an administrator has configured rules. | Entitlements; first-run behaviour; security posture | HIGH |
| 5 | What LLM backend is supported for summarised fetch in v1? The summarisation capability requires a configured language model — the server needs to define which providers are supported (local model, OpenAI-compatible API, etc.) and what the default is. | v1 fetch — summarised format; deployment requirements | MEDIUM |
| 6 | How is the classification threshold policy expressed in configuration? A decision is needed on whether thresholds are defined as numeric score cutoffs, category blocklists, named policy profiles, or a combination. This affects the configuration schema and the administrator experience. | Entitlements; site classification; operator UX | MEDIUM |
| 7 | What is the audit log schema? The log format needs to be defined before build so that downstream SIEM and observability integrations can be designed against a stable schema. | Audit logging; operational integration; compliance | MEDIUM |
| 8 | Which enterprise IdP providers are explicitly tested and documented for v1 authenticated fetch? Entra ID and Okta are the expected primary targets but the scope of tested providers should be confirmed before v1 build. | v1 authenticated fetch; enterprise integration documentation | MEDIUM |
| 9 | What consumer OAuth providers are supported in v2 authenticated fetch beyond Google and GitHub? The scope of supported providers affects the OAuth proxy and dynamic client registration implementation. | v2 authenticated fetch | LOW |
| 10 | Is multi-tenant entitlement and classification policy isolation a v2 or future consideration? If multiple business units within an enterprise need isolated policies, this significantly affects the configuration and identity model. | Roadmap; future architecture | LOW |
