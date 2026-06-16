# 04 — Implementation Reference

**Product:** MAOS Knowledge MCP Server  
**Version:** 1.0  
**Date:** 2026-06-16  

---

## Security Model

### Transport

All remote connections use TLS. HTTP is rejected in all environments. The `MCP-Protocol-Version: 2025-06-18` header is required on every HTTP request — missing or unsupported version returns `400 Bad Request`. stdio connections (local, same-machine) rely on OS process isolation.

### Authentication

OAuth 2.1 with PKCE (S256 method, mandatory) for all remote clients. Token issuance is delegated to an external authorisation server. Every access token is bound to this server via the RFC 8707 resource indicator:

```
resource=https://knowledge-mcp.maoperatingsystem.com
```

Tokens without a resource indicator, or bound to a different server, are rejected. The server publishes its authorization server metadata at `/.well-known/oauth-authorization-server`.

### Path Traversal Prevention

Every incoming URI is validated before any filesystem operation, in order:

1. URI must begin with `file:///knowledge/`
2. URI is URL-decoded and `.`/`..` segments resolved
3. Resolved absolute path must begin with `KNOWLEDGE_ROOT`
4. Any failure at steps 1–3 returns `-32602` immediately with no filesystem access

### Scopes

| Scope | Access |
|---|---|
| `knowledge:read` | All content types — default for MAOS platform clients |
| `knowledge:resources:read` | Resources only |
| `knowledge:prompts:read` | Prompts only |
| `knowledge:skills:read` | Skills only |
| `knowledge:commands:read` | Commands only |
| `knowledge:agents:read` | Agent definitions only |

### Rate Limits

| Limit | Default |
|---|---|
| Requests per minute | 120 |
| Search requests per minute | 20 |
| Concurrent SSE connections | 5 |
| Max response size | 10 MB |

Exceeded limits return HTTP `429` with a `Retry-After` header.

### Error Codes

| Code | Meaning |
|---|---|
| `-32002` | Resource not found |
| `-32602` | Invalid params — URI prefix violation, path traversal, missing required argument |
| `-32603` | Internal error — filesystem I/O or search index failure |
| HTTP `400` | Missing or invalid `MCP-Protocol-Version` header |
| HTTP `401` | Missing or invalid bearer token |
| HTTP `403` | Valid token, insufficient scope |
| HTTP `429` | Rate limit exceeded |

---

## Project Structure

```
knowledge-mcp-server/
├── src/
│   └── knowledge_mcp/
│       ├── server.py           # FastMCP entry point
│       ├── config.py           # Pydantic settings, env vars
│       ├── errors.py           # JSON-RPC error constants
│       ├── auth/
│       │   ├── middleware.py   # OAuth 2.1 + PKCE validation
│       │   └── scopes.py       # Scope enforcement
│       ├── registry/
│       │   ├── scanner.py          # Filesystem scanner, content index
│       │   ├── watcher.py          # watchfiles integration, notifications
│       │   ├── search.py           # SQLite FTS5 index manager
│       │   ├── embeddings.py       # v2 — embedding generation, pgvector upsert
│       │   └── chunker.py          # v2 — section/paragraph splitting strategy
│       ├── primitives/
│       │   ├── resources.py    # resources/* handlers
│       │   └── prompts.py      # prompts/* handlers
│       ├── tools/
│       │   ├── resource_tools.py   # extend get_resource with query/top_k (v2)
│       │   ├── prompt_tools.py
│       │   ├── skill_tools.py
│       │   ├── command_tools.py
│       │   ├── agent_tools.py
│       │   ├── search_tools.py     # search_knowledge + five typed shortcuts
│       │   └── search_tools_v2.py  # v2 — hybrid_search
│       └── content/
│           ├── types.py        # ContentKind enum, ContentEntry dataclass
│           ├── resolver.py     # URI validation and path resolution
│           ├── renderer.py     # Front-matter parsing, template substitution
│           └── mime.py         # MIME detection and allowlist
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Key Implementation Modules

### Configuration

```python
# src/knowledge_mcp/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    knowledge_root:          Path
    server_name:             str  = "maos-knowledge-mcp-server"
    server_version:          str  = "1.0.0"
    host:                    str  = "0.0.0.0"
    port:                    int  = 8080
    oauth_issuer:            str
    oauth_audience:          str   # Must match RFC 8707 resource indicator
    oauth_jwks_uri:          str
    fts_db_path:             Path = Path("/tmp/knowledge-fts.db")
    rate_limit_rpm:          int  = 120
    rate_limit_search_rpm:   int  = 20
    rate_limit_sse_connections: int = 5

    # v2 — pgvector / hybrid search
    supabase_url:               Optional[str] = None
    supabase_service_key:       Optional[str] = None
    embedding_model:            str           = "text-embedding-3-small"
    embedding_dimensions:       int           = 1536
    chunk_size_tokens:          int           = 512
    chunk_overlap_tokens:       int           = 64
    hybrid_search_enabled:      bool          = False  # set True when pgvector is provisioned

    class Config:
        env_prefix = "KNOWLEDGE_MCP_"
```

> `hybrid_search` and chunk retrieval via `get_resource` both return `-32603` with message `"Not available — pgvector not configured"` when `hybrid_search_enabled` is `False`. `search_knowledge` and all typed shortcuts remain operational via FTS5 regardless of this flag.

### Content Types

```python
# src/knowledge_mcp/content/types.py
from enum import StrEnum
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional

class ContentKind(StrEnum):
    RESOURCE = "resource"
    PROMPT   = "prompt"
    SKILL    = "skill"
    COMMAND  = "command"
    AGENT    = "agent"

KIND_FOLDER_MAP: dict[str, ContentKind] = {
    "resources": ContentKind.RESOURCE,
    "prompts":   ContentKind.PROMPT,
    "skills":    ContentKind.SKILL,
    "commands":  ContentKind.COMMAND,
    "agents":    ContentKind.AGENT,
}

@dataclass(frozen=True)
class ContentEntry:
    uri:           str
    abs_path:      Path
    kind:          ContentKind
    name:          str
    title:         Optional[str]
    description:   Optional[str]
    mime_type:     str
    size:          int
    last_modified: datetime
    front_matter:  dict = field(default_factory=dict)
```

### URI Resolver

```python
# src/knowledge_mcp/content/resolver.py
from pathlib import Path
from urllib.parse import urlparse, unquote

class URIResolver:
    def __init__(self, knowledge_root: Path) -> None:
        self._root = knowledge_root.resolve()

    def to_path(self, uri: str) -> Path:
        """
        Validate and resolve a file:// URI to an absolute filesystem path.
        Raises KnowledgeMCPError(-32602) on prefix violation or traversal.
        """
        if not uri.startswith("file:///knowledge/"):
            raise KnowledgeMCPError(code=-32602,
                message=f"URI must begin with file:///knowledge/. Got: {uri}")
        decoded   = unquote(urlparse(uri).path)
        candidate = (self._root / decoded.lstrip("/")).resolve()
        if not str(candidate).startswith(str(self._root)):
            raise KnowledgeMCPError(code=-32602, message="Path traversal detected")
        return candidate

    def to_uri(self, path: Path) -> str:
        return f"file:///knowledge/{path.relative_to(self._root)}"
```

### Template Renderer

```python
# src/knowledge_mcp/content/renderer.py
import re
from typing import Any

TEMPLATE_PATTERN = re.compile(r"\{\{(\w+)\}\}")

def render_template(template: str, arguments: dict[str, Any]) -> str:
    """
    Substitute {{argument_name}} references. Unresolved references are
    left in place. Raises KeyError if a required argument is missing
    (caller surfaces as -32602).
    """
    def substitute(match: re.Match) -> str:
        key = match.group(1)
        return str(arguments[key]) if key in arguments else match.group(0)
    return TEMPLATE_PATTERN.sub(substitute, template)
```

### Filesystem Watcher

```python
# src/knowledge_mcp/registry/watcher.py
import asyncio
from pathlib import Path
from watchfiles import awatch

async def watch_and_notify(
    knowledge_root: Path,
    registry,
    notify_list_changed: callable,
    notify_resource_updated: callable,
) -> None:
    async for changes in awatch(knowledge_root):
        for _, changed_path in changes:
            path = Path(changed_path)
            registry.reindex(path)
            await notify_resource_updated(registry.to_uri(path))
        await notify_list_changed()
```

---

## Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[server]"
COPY src/ src/
VOLUME ["/knowledge"]
EXPOSE 8080
ENV KNOWLEDGE_MCP_KNOWLEDGE_ROOT=/knowledge
CMD ["uvicorn", "knowledge_mcp.server:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# docker-compose.yml
services:
  knowledge-mcp:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - type: bind
        source: ./knowledge
        target: /knowledge
        read_only: true
    environment:
      KNOWLEDGE_MCP_OAUTH_ISSUER:   "${OAUTH_ISSUER}"
      KNOWLEDGE_MCP_OAUTH_AUDIENCE: "https://knowledge-mcp.maoperatingsystem.com"
      KNOWLEDGE_MCP_OAUTH_JWKS_URI: "${OAUTH_JWKS_URI}"
    restart: unless-stopped
    healthcheck:
      test:     ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout:  10s
      retries:  3
```

Health endpoint at `GET /health` returns:
```json
{ "status": "ok", "version": "1.0.0", "indexed_entries": 247, "last_scan": "2026-06-16T09:00:00Z" }
```
