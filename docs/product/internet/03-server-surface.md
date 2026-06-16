# 03 — Server Surface

**Product:** MAOS Internet Access MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  
**Author:** Andrew Bush / M&A Operating System

---

## Protocol and Capability Declaration

Transport: stdio (local deployments) and Streamable HTTP with SSE (remote and multi-client deployments). Message format: JSON-RPC 2.0. Auth: OAuth 2.1 + PKCE with RFC 8707 resource binding for remote deployments. Conforms to MCP Authorization Specification 2025-11-25.

```json
{
  "protocolVersion": "2025-03-26",
  "capabilities": {
    "tools": { "listChanged": false }
  },
  "serverInfo": {
    "name":    "maos-internet-mcp-server",
    "title":   "MAOS Internet Access MCP Server",
    "version": "1.0.0"
  },
  "instructions": "Provides controlled internet search and page fetch. All requests are subject to entitlement and site classification policy. Use search to retrieve ranked web results, fetch to retrieve page content in raw, markdown, chunked, or summarised format. Authenticated fetch requires a valid identity token and is available from v1."
}
```

---

## Tools

### `search`

Search the web and return a ranked list of results filtered through the active entitlement and classification policy.

**Input schema**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | The search query |
| `num_results` | integer | No | Number of results to return; default and maximum are deployment-configurable |
| `language` | string | No | Language preference for results |
| `time_range` | enum | No | Restrict results by recency: `day`, `week`, `month`, `year`, `any` |

**Response — `content`**

Plain-text summary of result count and any applied filters.

**Response — `structuredContent`**

```json
{
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "source_domain": "string",
      "classification": {
        "category": "string",
        "reputation_score": "number",
        "safety_flags": ["string"],
        "source": "string"
      }
    }
  ],
  "filter_applied": "boolean",
  "total_before_filtering": "integer",
  "provenance": {
    "query": "string",
    "executed_at": "string",
    "backend": "string",
    "result_count_returned": "integer",
    "result_count_before_filtering": "integer",
    "results_hash": "string"
  }
}
```

`provenance.executed_at` is an ISO 8601 UTC timestamp. `provenance.results_hash` is a SHA-256 hex digest of the canonically serialised result set after filtering — enabling callers and audit systems to verify the result set has not been modified in transit. `provenance.backend` identifies the search backend that served the query (e.g. `searxng`, `brave`, `enterprise-index`).

**Error conditions**

| Condition | Error type |
|---|---|
| Search backend unavailable | `backend_unavailable` |
| Query blocked by entitlement policy | `policy_rejection` |
| Zero results after filtering | Empty `results` array; `filter_applied: true` |

---

### `fetch`

Fetch a URL and return page content in the requested output format, subject to entitlement and classification checks.

**Input schema**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `url` | string | Yes | The URL to fetch |
| `format` | enum | No | Output format: `raw`, `markdown`, `chunked`, `summarised`. Default: `markdown` |
| `chunk_size` | integer | No | Token or character limit per chunk; only used when `format` is `chunked` |
| `start_chunk` | integer | No | Chunk index to begin from; enables pagination through large pages |

**Output formats**

| Format | Description |
|---|---|
| `raw` | Unprocessed HTTP response body; all HTML, scripts, and structure preserved |
| `markdown` | Page content converted to clean Markdown; navigation, advertisements, and boilerplate stripped |
| `chunked` | Markdown content segmented into discrete chunks; each chunk includes its index and total chunk count |
| `summarised` | LLM-generated summary of the page content; requires a configured LLM backend |

**Response — `content`**

The fetched page content in the requested format.

**Response — `structuredContent`**

```json
{
  "format": "string",
  "classification": {
    "category": "string",
    "reputation_score": "number",
    "safety_flags": ["string"],
    "source": "string"
  },
  "chunk_index": "integer | null",
  "chunk_total": "integer | null",
  "provenance": {
    "url": "string",
    "fetched_at": "string",
    "content_length_bytes": "integer",
    "content_hash": "string",
    "http_status": "integer",
    "redirected_from": "string | null"
  }
}
```

`provenance.fetched_at` is an ISO 8601 UTC timestamp. `provenance.content_hash` is a SHA-256 hex digest of the raw response body before any format conversion — enabling callers and audit systems to verify the content returned matches what the server received from the origin. `provenance.redirected_from` records the original URL when the target server issued a redirect.

**Error conditions**

| Condition | Error type |
|---|---|
| URL blocked by entitlement policy | `policy_rejection` |
| URL blocked by site classification | `classification_rejection` |
| Target server non-200 response | `fetch_error` with HTTP status code |
| Target server timeout | `timeout_error` |
| `summarised` format with no LLM backend configured | `capability_unavailable` |
| `start_chunk` beyond available chunks | `chunk_out_of_range` |

---

### `fetch_authenticated`

Fetch a URL using the caller's identity credentials. Available from v1. Applies the same entitlement and classification checks as `fetch` — authentication does not bypass access controls.

**Input schema**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `url` | string | Yes | The URL to fetch |
| `format` | enum | No | Output format: `raw`, `markdown`, `chunked`, `summarised`. Default: `markdown` |
| `chunk_size` | integer | No | Token or character limit per chunk |
| `start_chunk` | integer | No | Chunk index to begin from |
| `token` | string | No | Bearer token from the enterprise IdP; used for OBO token exchange if the target resource requires a different audience |

**Authentication modes**

| Mode | Mechanism |
|---|---|
| Enterprise IdP | Bearer token accepted from any OIDC-compliant provider; OBO exchange performed for resources requiring a different token audience |
| Consumer OAuth (v2) | OAuth 2.1 with PKCE; access token from the authorisation code flow stored in session context |
| Cookie/session forwarding (v2) | Serialised session state (cookies, localStorage) replayed against the target URL |

**Response shapes**

Identical to `fetch`. An additional `auth_method` field is included in `structuredContent` indicating which authentication mode was used. The `provenance` block is always present and identical in structure to `fetch` — authentication does not alter provenance recording.

**Error conditions**

| Condition | Error type |
|---|---|
| Invalid or expired token | `auth_error` |
| Consent not granted for requesting client scope | `consent_required` |
| URL blocked by entitlement or classification policy | `policy_rejection` / `classification_rejection` |

---

## Cross-Cutting Behaviours

### Error Response Shape

All error conditions return a structured MCP tool response. No unhandled exceptions are surfaced to the caller.

```json
{
  "error_type": "string",
  "reason": "string",
  "detail": {}
}
```

### Provenance

Every successful `search`, `fetch`, and `fetch_authenticated` response includes a `provenance` block in `structuredContent`. The provenance block is the authoritative record of what was requested, when, and what was returned:

| Field | Present in | Description |
|---|---|---|
| `query` | `search` | The exact query string submitted to the backend |
| `executed_at` | `search` | ISO 8601 UTC timestamp of query execution |
| `backend` | `search` | Identifier of the search backend that served the query |
| `result_count_returned` | `search` | Number of results returned after filtering |
| `result_count_before_filtering` | `search` | Number of results received from the backend before entitlement and classification filtering |
| `results_hash` | `search` | SHA-256 hex digest of the canonically serialised filtered result set |
| `url` | `fetch`, `fetch_authenticated` | Final URL fetched, after any server-side redirects |
| `fetched_at` | `fetch`, `fetch_authenticated` | ISO 8601 UTC timestamp of the fetch |
| `content_length_bytes` | `fetch`, `fetch_authenticated` | Size of the raw response body in bytes |
| `content_hash` | `fetch`, `fetch_authenticated` | SHA-256 hex digest of the raw response body before format conversion |
| `http_status` | `fetch`, `fetch_authenticated` | HTTP status code returned by the origin server |
| `redirected_from` | `fetch`, `fetch_authenticated` | Original URL if a redirect occurred; `null` otherwise |

The provenance block is returned to the caller in every successful response and is independently recorded in the audit log. This enables downstream consumers — agents, audit systems, and compliance tooling — to verify that the content they received matches what the server retrieved from the origin, and to establish an unambiguous chain of custody from request to response.

### Audit Logging

Every tool call — including policy rejections, classification blocks, and authentication failures — is written to the audit log. Each audit log entry includes: timestamp, tool name, caller identity (where available), query or URL, entitlement outcome, classification outcome, response status, and the full provenance block for successful responses. Log destination is configurable at deployment time (stdout, file, or external log sink).

### Rate Limiting

Configurable per caller identity and per tool. A structured `rate_limit_exceeded` response is returned when the threshold is reached.
