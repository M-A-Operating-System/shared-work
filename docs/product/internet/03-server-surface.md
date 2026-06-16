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
  "total_before_filtering": "integer"
}
```

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
  "url": "string",
  "format": "string",
  "classification": {
    "category": "string",
    "reputation_score": "number",
    "safety_flags": ["string"],
    "source": "string"
  },
  "chunk_index": "integer | null",
  "chunk_total": "integer | null"
}
```

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

Identical to `fetch`. An additional `auth_method` field is included in `structuredContent` indicating which authentication mode was used.

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

### Audit Logging

Every tool call is logged with: timestamp, tool name, caller identity (where available), query or URL, entitlement outcome, classification outcome, and response status. Log destination is configurable at deployment time.

### Rate Limiting

Configurable per caller identity and per tool. A structured `rate_limit_exceeded` response is returned when the threshold is reached.
