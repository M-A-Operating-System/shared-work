# 02 — Core Capabilities

**Product:** MAOS Internet Access MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Capability Model

The server exposes five capability areas as MCP tools. Each is described below with its purpose, inputs, outputs, behaviour, and acceptance criteria.

---

## 1. Search

### Purpose
Accept a natural language or keyword query and return a ranked list of web search results drawn from the configured search backend.

### Inputs
| Parameter | Type | Required | Description |
|---|---|---|---|
| query | string | Yes | The search query |
| num_results | integer | No | Number of results to return; default and maximum configurable at deployment |
| language | string | No | Language preference for results |
| time_range | string | No | Restrict results by recency (day, week, month, year, any) |

### Outputs
A ranked list of results, each containing:
- title
- url
- snippet
- source domain
- site classification metadata (category, reputation score, safety flag) — see Capability 4

### Behaviour
The search backend is configurable at deployment time. The server abstracts the backend — callers issue a standard MCP tool call regardless of which backend is active. Results are filtered through the active entitlement policy before being returned; results for blocked or restricted domains are silently excluded from the response. Results whose site classification falls below configured safety thresholds are excluded or flagged according to deployment policy.

### Unhappy Paths
- Backend unavailable: returns a structured error with reason; does not return partial or cached results unless caching is explicitly configured
- Query returns zero results after entitlement and classification filtering: returns empty results list with a filter-applied indicator
- Query violates entitlement policy entirely: returns a policy rejection response with no results

### Acceptance Criteria
- Given a valid query, when the tool is called, then a ranked list of results is returned within the configured timeout
- Given a valid query, when results include domains on the deny list, then those results are excluded before the response is returned
- Given a valid query, when results include URLs with a safety classification below threshold, then those results are excluded or flagged per deployment policy
- Given the search backend is unavailable, when the tool is called, then a structured error is returned and no partial results are served
- Given a query returning zero results after filtering, when the tool is called, then an empty results list with a filter-applied indicator is returned

---

## 2. Fetch

### Purpose
Accept a URL and return the page content in one of four caller-selected output formats, suitable for consumption by an LLM or downstream processing step.

### Inputs
| Parameter | Type | Required | Description |
|---|---|---|---|
| url | string | Yes | The URL to fetch |
| format | enum | No | Output format: raw, markdown, chunked, summarised. Default: markdown |
| chunk_size | integer | No | Token or character limit per chunk when format is chunked |
| start_chunk | integer | No | Chunk index to begin from, enabling pagination through large pages |

### Output Formats

**Raw** — The unprocessed HTTP response body as returned by the target server. Preserves all HTML, scripts, and structure. Intended for callers that perform their own parsing.

**Markdown** — The page content converted to clean Markdown. Navigation, advertisements, headers, footers, and boilerplate are stripped. The result is LLM-ready structured text preserving headings, lists, links, and code blocks.

**Chunked** — The Markdown-converted content segmented into discrete chunks of a configurable size. Each chunk includes its index and the total chunk count. Enables agents to paginate through large pages without exceeding context window limits.

**Summarised** — An LLM-generated summary of the page content. The server passes the Markdown-converted content to a configured language model and returns the summary. The model used is configurable at deployment time.

### Behaviour
Before executing a fetch, the server checks the URL against the active entitlement policy. If the URL or its domain is on the deny list, the fetch is rejected and a policy response is returned. If the URL's site classification falls below the configured safety threshold, the fetch is rejected or the response is flagged according to deployment policy. Fetch is performed using the server's own HTTP client — no browser automation is required for static content. JavaScript-rendered pages require a configured browser automation backend.

### Unhappy Paths
- URL blocked by entitlement policy: returns a policy rejection response with the reason
- URL blocked by site classification: returns a classification rejection response
- Target server returns non-200 response: returns a structured error including the HTTP status code
- Target server times out: returns a timeout error with the configured timeout value
- Summarised format requested but no LLM backend configured: returns an error indicating the capability is not available in this deployment
- Chunked format requested with start_chunk beyond available chunks: returns an error indicating the chunk index is out of range

### Acceptance Criteria
- Given a valid permitted URL, when fetch is called with format markdown, then clean Markdown content is returned with boilerplate stripped
- Given a valid permitted URL, when fetch is called with format raw, then the unprocessed HTTP response body is returned
- Given a valid permitted URL, when fetch is called with format chunked, then content is returned in segments with index and total chunk count in each response
- Given a valid permitted URL, when fetch is called with format summarised and an LLM backend is configured, then a summary of the page content is returned
- Given a URL on the deny list, when fetch is called, then a policy rejection response is returned and no content is fetched
- Given a URL with a site classification safety flag below threshold, when fetch is called, then the fetch is rejected per deployment policy
- Given a target server timeout, when fetch is called, then a structured timeout error is returned
- Given a chunked fetch with start_chunk beyond available chunks, when fetch is called, then an out-of-range error is returned

---

## 3. Entitlements

### Purpose
Define and enforce domain and URL-level access controls that govern what internet content the server will search and fetch on behalf of AI agents and users. These controls are specific to AI interactions and are additive to any enterprise perimeter controls already in place.

### Configuration Model
Entitlement rules are defined by the Platform Administrator at deployment time through server configuration. Rules are not modifiable at runtime by agents or users.

| Rule Type | Description |
|---|---|
| Domain allow list | Only domains on this list are accessible. All others are blocked. |
| Domain deny list | Domains on this list are always blocked. Other domains are accessible subject to classification. |
| URL pattern rules | Allow or deny rules applied at the URL path level using pattern matching |
| Default posture | When no allow list is defined: open (block only deny-listed domains) or closed (block all except allow-listed domains) |

### Behaviour
Entitlement checks run before any search result is returned or any fetch is executed. Blocked content is never retrieved or returned. The caller receives a structured policy response indicating the request was blocked; the reason (domain blocked, URL pattern blocked) is included in the response.

Search results for blocked domains are excluded from the result list before the response is returned — the caller does not see them and is not informed of their existence unless inspection-mode logging is enabled for audit purposes.

### Acceptance Criteria
- Given a domain deny list is configured, when a search or fetch is requested for a blocked domain, then the request is rejected with a policy response
- Given a domain allow list is configured, when a search or fetch is requested for a domain not on the list, then the request is rejected with a policy response
- Given URL pattern rules are configured, when a fetch is requested for a URL matching a deny pattern, then the request is rejected
- Given an open default posture with no allow list, when a fetch is requested for a domain not on the deny list, then the request proceeds subject to classification checks
- Given a closed default posture, when a fetch is requested for a domain not on the allow list, then the request is rejected

---

## 4. Site Classification

### Purpose
Provide category and reputation metadata for URLs accessed through search and fetch, enabling the server to enforce content safety policies and prevent LLMs from consuming dangerous, malicious, or policy-violating content.

### Classification Dimensions
| Dimension | Description |
|---|---|
| Content category | Topical classification of the site (e.g. news, finance, technology, adult, gambling) aligned to a standard taxonomy |
| Reputation score | A numerical score indicating the trustworthiness and safety history of the domain |
| Safety flags | Explicit flags for malware, phishing, spam, hate speech, and other threat categories |
| Classification source | The provider or database that supplied the classification |

### Behaviour
Classification is checked at two points: when search results are assembled, and before a fetch is executed. The deployment configuration defines threshold policies — which categories are blocked, which reputation score ranges are permitted, and which safety flags result in an automatic block.

Classification metadata is returned alongside search results and fetch responses, enabling consuming agents and UIs to make their own downstream policy decisions in addition to the server's enforcement. This supports scenarios where the enterprise wants both server-side safety enforcement and agent-layer awareness of content classification.

Classification data is sourced from one or more configured classification providers. The classification backend is pluggable at deployment time. Where multiple providers are configured, the most restrictive classification applies.

### Acceptance Criteria
- Given a search result URL with a safety flag for malware, when results are assembled, then that result is excluded per deployment policy
- Given a fetch request for a URL classified in a blocked category, when the fetch is requested, then a classification rejection response is returned
- Given a search result URL with a reputation score below the configured threshold, when results are assembled, then that result is excluded or flagged per deployment policy
- Given a permitted URL, when fetch is called, then classification metadata is returned alongside the content in the response
- Given multiple classification providers are configured, when classifications conflict, then the most restrictive classification applies

---

## 5. Authenticated Fetch

### Purpose
Enable the server to retrieve content from websites that require an authenticated user session — such as enterprise intranet pages, subscription services, or any site protected by OAuth or SSO — on behalf of a user who has legitimate access to that content.

### Authentication Modes

**Enterprise IdP (OAuth 2.1 / SAML / OIDC)**
The server accepts an access token issued by the enterprise identity provider (Entra ID, Okta, or any OIDC-compliant IdP) passed in the tool call context. For downstream resources that require a different token audience, the server performs an OAuth 2.0 On-Behalf-Of (OBO) token exchange — trading the inbound user token for a token scoped to the target resource — and uses that exchanged token to execute the fetch.

**Consumer OAuth Providers**
The server supports OAuth 2.1 with PKCE for consumer providers (Google, GitHub, and others). The user authenticates via the standard OAuth authorisation code flow through their AI client. The resulting access token is stored in the user's session context and used by the server to execute fetches on behalf of the user for the duration of the session.

**Cookie/Session Forwarding**
For sites where the user has an active browser session, the server accepts a serialised session state (cookies and localStorage) captured from the user's authenticated browser session. The server replays the session credentials when fetching the target URL. This mechanism is intended for local or single-user deployments where formal OAuth flows are not available for the target site.

### Behaviour
Authenticated fetch applies the same entitlement and classification checks as standard fetch. Authentication does not bypass access controls — a user with a valid session cannot fetch content from a blocked domain or a URL that fails classification policy.

Token handling follows the MCP Authorization Specification (2025-11-25). Tokens are validated on each request. Token passthrough to downstream services without validation is not permitted. The server maintains a consent registry mapping user identities to approved tool scopes.

### Acceptance Criteria
- Given a valid enterprise IdP token in the tool call context, when an authenticated fetch is requested for a permitted URL, then the server executes the fetch using the user's identity and returns the content
- Given a target resource requiring a different token audience, when an authenticated fetch is requested, then the server performs an OBO token exchange before executing the fetch
- Given a valid consumer OAuth session, when an authenticated fetch is requested for a permitted URL, then the server executes the fetch using the user's OAuth credentials
- Given an authenticated fetch request for a URL on the deny list, when the fetch is requested, then a policy rejection is returned regardless of the user's authentication status
- Given an expired or invalid token, when an authenticated fetch is requested, then a structured authentication error is returned and no fetch is executed
- Given a user has not granted consent for the requesting client scope, when an authenticated fetch is requested, then the request is rejected with a consent-required response

---

## Cross-Cutting Behaviours

### Audit Logging
All tool calls — search queries, fetch requests, classification decisions, entitlement rejections, and authentication events — are logged. Log entries include: timestamp, tool called, caller identity (where available), query or URL, entitlement outcome, classification outcome, and response status. Logs are written to a configurable destination (stdout, file, external log sink).

### Rate Limiting
The server enforces configurable rate limits per caller identity or per deployment. Rate limit thresholds are set by the Platform Administrator. When a rate limit is exceeded, a structured rate-limit response is returned. Rate limiting applies independently to search and fetch tool calls.

### Transport
The server supports both stdio transport (for local MCP client integration) and HTTP/SSE transport (for remote and multi-client deployments). Transport mode is configured at deployment time.

### Error Responses
All error conditions return a structured MCP tool response — never an unhandled exception. Every error response includes: error type, human-readable reason, and where applicable the specific policy, classification, or system condition that caused the failure.
