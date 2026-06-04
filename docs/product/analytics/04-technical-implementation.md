# 4. Proposed Technical Implementation

This chapter describes one reference implementation of the AI Analytics Platform. Stack choices are concrete but not prescriptive. The product specification is intentionally stack-agnostic. Any conformant implementation that satisfies the specified behaviours, governance guarantees, and interface contracts is valid. Technology substitutions at any layer require no changes to the product specification.

The product specification (component behaviours, interface contracts, governance requirements) is in [Chapter 2 -- Core Platform Capabilities](./02-core-capabilities.md). The design principles governing every decision are in [Platform Overview — Design Principles](./00-overview.md#design-principles).

---

## 4.1 Architecture Overview

```mermaid
flowchart TD
    Consumer["Consumer\nAI Chat Platform (Claude) · autonomous agent · custom application"]

    subgraph analytics["AI Analytics Platform"]
        MCP["MCP Capability Layer\nPython 3.12 · FastMCP 2.x + Uvicorn · MCP Streamable HTTP · port 8000\nJWT validation — python-jose · JWKS endpoint · RS256"]
        SIL["Semantic Intent Layer\nPython · Pydantic v2 · JSON Schema validation\nSMR resolution · compliance intent scoring · LQP generation"]
        RAPL["Role-Aware Projection Layer\nPython · asyncpg · PostgreSQL role_policies\nJWT claims → row predicate injection · column masking"]
        SCL["Semantic Controls Layer\nPython · Redis (concurrency semaphore)\nperformance impact · classification · compliance checks"]
        FQE["Federated Query Engine\nPython · asyncio fan-out\nApache Calcite (SQL plan optimisation, within adapters)\nSnowflake (primary) · dbt MetricFlow · REST/OData · Neo4j"]
        DVL["Data Visualization Language (DVL)\nPython · ontology evaluation · Vega-Lite v5\ndeterministic chart contract selection"]
        NSE["Narrative Synthesis Engine\nAnthropic Claude Haiku 4.5 — simple queries\nAnthropic Claude Sonnet 4.6 — complex queries"]
        Cache[("Result Cache\nRedis · SHA-256 cache key · 5-min TTL\ncompliance queries bypass")]
        LS[("Analytical Lineage Store (ALS)\nAWS S3 — JSON record per query\nPostgreSQL lineage_index — scalar search")]
        Result(["MCP tool response\ndisplay_spec + narrative + result_id\n+ compliance block if Provenance Artifact active"])
    end

    vega2img["vega2img (optional) · port 8001\nPython · FastMCP · vega-embed · Playwright (headless Chromium)\nStandalone MCP render service — not part of Analytics Platform"]

    subgraph dcs["Data Context Store (DCS)"]
        SMR[("Semantic Metrics Repository (SMR)\nJSON documents: analytical_metric · analytical_dimension · analytical_operation\nlifecycle: proposed → in_review → approved → deprecated")]
        SDR[("Semantic Data Repository (SDR)\nJSON documents: data models · object models\ncritical data elements · physical schemas · data lineage")]
        SDR -->|"SMR extends SDR"| SMR
    end

    subgraph backends["Execution Backends"]
        SQL["Snowflake — primary SQL warehouse\nBigQuery · Databricks · Redshift (alternatives)"]
        SemLayer["dbt Semantic Layer — MetricFlow\nCube.js"]
        ODA["OpenData API\nREST JSON · OData v4"]
        GDA["Graph Data API\nNeo4j Bolt · Amazon Neptune SPARQL"]
    end

    Consumer -->|"POST /v1/mcp (JWT + MCP tool call)"| MCP
    Consumer -->|"render tool call (display_spec)"| vega2img
    MCP -->|"validated tool call parameters"| SIL
    MCP -->|"JWT claims"| RAPL
    RAPL -->|"row predicates + column masks"| SIL
    SIL -->|"metric + dimension ID resolution"| SMR
    SIL -->|"Logical Query Plan (LQP)"| SCL
    SCL -->|"controls decision record"| LS
    SCL -->|"approved LQP"| FQE
    FQE -->|"physicalMapping lookup"| SMR
    FQE <-->|"cache read / write"| Cache
    FQE --> SQL & SemLayer & ODA & GDA
    FQE -->|"execution record"| LS
    FQE -->|"assembled result"| DVL
    FQE -->|"assembled result"| NSE
    DVL -->|"DVL display spec"| Result
    NSE -->|"governed narrative"| Result
```

The Semantic Data Repository (SDR) is a pre-existing platform component: the organisation's general-purpose registry for semantic definitions. The Analytics Platform registers metric definitions as a new `analytical_metric` type in the SDR, reusing its versioned storage, full-text search, cross-definition relationships, and scoped access control. The SMR governance layer adds the approval workflow, metric-specific schema validation, and the Admin API surface on top.

---

## 4.2 Layer-by-Layer Stack Decisions

### MCP Capability Layer

> **Specification:** [§MCP Capability Layer](./02-core-capabilities.md#mcp-capability-layer)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Runtime** | Python · FastMCP + Uvicorn | Lightweight ASGI service; minimal dependencies; deploys as a Kubernetes pod or serverless container |
| **Protocol** | MCP Streamable HTTP | Standard MCP interoperability; supports request/response and streaming |
| **Auth** | JWT validation at request ingress | Stateless; validated before any platform computation begins |
| **Tools** | Three tools: `run_analytics` (SMR-driven execution), `list_operations` (discovery), `drilldown` (result navigation) | SMR owns all operation definitions; code is the execution engine |
| **Resources** | Knowledge artifacts only — guides, skills definitions, compliance reference | Static; no user data; embedded in AI consumer context before analytical tasks; no controls pipeline |
| **Prompts** | Pre-built analytical and regulatory assistant templates | Inject available metrics and governance constraints at session start |

FastMCP (`pip install fastmcp`) provides the `@mcp.tool()`, `@mcp.resource()`, and `@mcp.prompt()` decorators and handles MCP Streamable HTTP transport. Each analytical capability is a decorated Python function; the framework serialises schemas and routes calls automatically.

The separation of tools and resources is intentional. All analytical execution goes through `run_analytics`, a single tool that delegates to the SMR for every operation definition. Resources expose static knowledge artifacts from the Knowledge Store; they contain no user data and require no governance evaluation. The SMR owns what operations exist, what parameters they require, and how deeply they run through the pipeline. The code owns only the execution engine.

#### Tools

Three tools cover the entire analytical surface. The SMR owns every operation definition: what parameters it needs, what metrics and dimensions it supports, and how deeply it runs through the pipeline. No operation type is hardcoded in the execution layer.

```python
from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP(
    name="Analytics Platform",
    instructions=(
        "Governed analytical execution engine. All operations are defined in the Semantic Metrics Repository. "
        "Call list_operations to discover available operations and their required parameters before "
        "calling run_analytics."
    ),
)

# ── Tool input models ─────────────────────────────────────────────────────────

class RunAnalyticsInput(BaseModel):
    operation_id: str   # SMR operation ID — discover via list_operations
    params:       dict  # operation parameters; validated against SMR operation schema by SIL

class ListOperationsInput(BaseModel):
    domain: str | None = None  # optional filter by analytical domain

class DrilldownInput(BaseModel):
    result_id:      str
    hierarchy:      str
    selected_value: str | None = None

# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def run_analytics(input: RunAnalyticsInput, jwt: str) -> dict:
    """Execute an SMR-registered analytical operation.
    Call list_operations first to discover valid operation_id values and their required params.
    The execution pipeline depth — data retrieval, metric query, or full analytical — is determined
    by the operation's execution_profile in the SMR, not by this tool."""
    claims    = validate_jwt(jwt)
    operation = await smr.get_operation(input.operation_id, claims)
    # RAPL runs after SIL: SIL builds the LQP, RAPL injects role predicates into it before SCL sees it
    return await pipeline_executor.run(operation, input.params, claims)

@mcp.tool()
async def list_operations(input: ListOperationsInput, jwt: str) -> dict:
    """List all SMR-registered operations available to the current user's role.
    Returns operation IDs, display names, required parameters, supported metrics,
    supported dimensions, and execution profiles."""
    claims = validate_jwt(jwt)
    return await smr.list_operations(claims, domain=input.domain)

@mcp.tool()
async def drilldown(input: DrilldownInput, jwt: str) -> dict:
    """Navigate into a dimension hierarchy from a prior result.
    All filters, role predicates, and entitlement context from the original result are preserved."""
    claims = validate_jwt(jwt)
    return await drilldown_service.execute(input, claims)
```

#### JWT Validation

Library: `python-jose[cryptography]`. The JWKS endpoint is fetched once at startup and cached with a 1-hour TTL. Required claims: `sub`, `org_id`. Optional but consumed claims: `analytics_roles`, `managed_portfolios`.

```python
from jose import jwt, JWTError

JWKS_URI     = config["auth"]["jwks_uri"]       # e.g. https://auth.example.com/.well-known/jwks.json
JWT_AUDIENCE = config["auth"]["audience"]
JWT_ISSUER   = config["auth"]["issuer"]

jwks_cache = {}  # { "keys": [...], "fetched_at": timestamp }

async def validate_jwt(token: str) -> dict:
    if not jwks_cache or time.time() - jwks_cache["fetched_at"] > 3600:
        jwks_cache.update({"keys": await fetch_jwks(JWKS_URI), "fetched_at": time.time()})

    try:
        claims = jwt.decode(token, jwks_cache["keys"], algorithms=["RS256"],
                            audience=JWT_AUDIENCE, issuer=JWT_ISSUER)
    except JWTError as e:
        raise AuthenticationError(str(e))

    required = ["sub", "org_id"]
    missing  = [k for k in required if k not in claims]
    if missing:
        raise AuthenticationError(f"Missing required JWT claims: {missing}")

    return claims   # { sub, org_id, analytics_roles: [...], managed_portfolios: [...], ... }
```

#### Pipeline Executor

The MCP layer routes JWT claims to `validate_jwt` and validated parameters to the pipeline; within the pipeline, RAPL operates post-SIL rather than in parallel — SIL must produce a valid LQP before RAPL can inject role predicates into it.

```python
class PipelineExecutor:
    def __init__(self, sil, rapl, scl, fqe, dvl, nse, als):
        ...

    async def run(self, operation: dict, params: dict, claims: dict) -> dict:
        lqp = await sil.resolve(operation, params, claims)
        lqp = await rapl.project(lqp, claims)

        profile = operation["execution_profile"]

        if profile == "data_retrieval":
            result = await fqe.execute(lqp)
            return {"result_id": result["result_id"], "rows": result["rows"], "schema": result["schema"]}

        if profile == "metric_query":
            result  = await fqe.execute(lqp)
            display = dvl.evaluate(result, operation)
            return {"result_id": result["result_id"], "rows": result["rows"], "display_spec": display}

        if profile == "full_analytical":
            lqp    = await scl.approve(lqp, claims)
            await als.write_controls_decision(lqp, claims)
            result              = await fqe.execute(lqp)
            display, narrative  = await asyncio.gather(
                asyncio.to_thread(dvl.evaluate, result, operation),
                nse.synthesise(result, operation),
            )
            return {
                "result_id":    result["result_id"],
                "rows":         result["rows"],
                "schema":       result["schema"],
                "display_spec": display,
                "narrative":    narrative,
                "export_requires_lineage": lqp.get("require_lineage_for_export", False),
            }

        raise ValueError(f"Unknown execution_profile: {profile}")
```

DVL is synchronous (CPU-bound ontology evaluation); `asyncio.to_thread` runs it on the thread pool so it does not block the event loop during the concurrent NSE API call.

#### Drilldown Service

```python
class DrilldownService:
    def __init__(self, als, fqe, dvl, rapl, smr):
        ...

    async def execute(self, input: DrilldownInput, claims: dict) -> dict:
        # Load original lineage record to recover the LQP and governance context
        lineage   = await als.fetch(input.result_id, claims["org_id"])
        orig_lqp  = lineage["lqp_id"]

        # Rebuild a refined LQP: add a filter node for the selected hierarchy value
        refined_lqp = deepcopy(lineage["request_payload"]["lqp"])
        refined_lqp["lqp_id"] = generate_id("lqp")
        refined_lqp["nodes"].append({
            "op":         "filter",
            "predicates": [f"{input.hierarchy} = {repr(input.selected_value)}"],
        })

        # Role predicates from original lineage are already embedded — do not re-project
        # Re-run FQE and DVL only; SCL approval is inherited from the original query
        result  = await fqe.execute(refined_lqp)
        display = dvl.evaluate(result, lineage["operation"])
        return {
            "result_id":    result["result_id"],
            "parent_id":    input.result_id,
            "rows":         result["rows"],
            "display_spec": display,
        }
```

#### Execution profiles

Each SMR operation carries an `execution_profile` that tells the pipeline executor which stages to invoke. Profile definitions are in [§MCP Capability Layer](./02-core-capabilities.md#mcp-capability-layer).

#### Resources

Resources are used for **knowledge artifacts** — static reference material, skills definitions, and workflow guides that AI consumers embed in their context to understand how to use the platform effectively. Dynamic data lookups (metric definitions, lineage records, dimension catalogues) are handled by tools, not resources.

```python
@mcp.resource("guide://analytics/platform-overview")
async def guide_platform_overview() -> str:
    """What the Analytics Platform does, how it governs queries, and when to use
    each analytical capability. Load this before helping a user with any analytical task."""
    return knowledge_store.get("guide/platform-overview")

@mcp.resource("guide://analytics/analytical-domains")
async def guide_analytical_domains() -> str:
    """Reference guide to the six analytical domains (portfolio, performance, risk,
    regulatory, counterparty, benchmarks) — what each covers, which metrics belong
    to it, and the governance constraints that apply."""
    return knowledge_store.get("guide/analytical-domains")

@mcp.resource("guide://analytics/query-patterns")
async def guide_query_patterns() -> str:
    """Common analytical query patterns with worked examples: time-period comparisons,
    benchmark-relative performance, risk attribution, regulatory ratio queries.
    Use this to choose the right tool and parameter structure for a given user request."""
    return knowledge_store.get("guide/query-patterns")

@mcp.resource("skills://analytics/portfolio-performance-review")
async def skills_portfolio_performance() -> str:
    """Step-by-step skills definition for conducting a portfolio performance review:
    which metrics to query, which dimensions to apply, how to interpret the results,
    and when to drilldown. Designed for AI assistants supporting portfolio managers."""
    return knowledge_store.get("skills/portfolio-performance-review")

@mcp.resource("skills://analytics/risk-analysis")
async def skills_risk_analysis() -> str:
    """Skills definition for risk metric analysis: VaR, tracking error, expected
    shortfall, issuer concentration. Covers query construction, result interpretation,
    threshold context, and escalation patterns."""
    return knowledge_store.get("skills/risk-analysis")

@mcp.resource("skills://analytics/regulatory-reporting")
async def skills_regulatory_reporting() -> str:
    """Skills definition for regulatory metric queries under MiFID II and Basel III/IV:
    required dimensions, compliance mode constraints, business justification requirements,
    and how to surface lineage references in regulatory responses."""
    return knowledge_store.get("skills/regulatory-reporting")

@mcp.resource("guide://compliance/mifid2")
async def guide_mifid2() -> str:
    """MiFID II compliance mode reference: which query types require a business
    justification, best-execution dimension requirements, what the mifid2_trace
    record captures, and how to explain compliance constraints to users."""
    return knowledge_store.get("guide/compliance-mifid2")

@mcp.resource("guide://compliance/basel3")
async def guide_basel3() -> str:
    """Basel III/IV compliance mode reference: entity dimension requirements,
    regulatory snapshot writes, stress scenario classification rules, and
    how to structure LCR and NSFR queries correctly."""
    return knowledge_store.get("guide/compliance-basel3")
```

Knowledge artifacts are stored in a versioned content store (`knowledge_store`) managed via the Admin API. Administrators can extend or override the default guides and skills definitions. Resources do not require JWT authentication (they contain no user data), but are scoped to the platform's public knowledge surface.

#### Prompts

Prompts provide pre-built instruction templates that AI consumers can load to anchor their analytical behaviour before making tool calls.

```python
@mcp.prompt()
async def analytical_assistant(jwt: str) -> str:
    """System prompt for an AI assistant using the Analytics Platform.
    Injects the organisation's available metrics and governance constraints."""
    claims  = validate_jwt(jwt)
    metrics = await smr.list_approved_summary(claims)   # id + label + description
    return f"""You are a governed analytical assistant. You answer quantitative questions
by calling the Analytics Platform tools — never by estimating or generating numbers.

Available operations and metrics (call list_operations for full detail including required parameters):
{metrics}

Rules:
- Only reference metric IDs that appear in the list above.
- Do not invent metric values. Every number must come from a tool result.
- When a result includes a narrative field, surface it as the primary response — do not paraphrase or restate.
- When a result includes a result_id, offer to drilldown or inspect lineage if relevant.
- If an operation or metric is not available, tell the user it is not registered and suggest list_operations."""

@mcp.prompt()
async def regulatory_reporting_assistant(jwt: str) -> str:
    """System prompt for a compliance-focused assistant operating under MiFID II or Basel III/IV.
    Adds regulatory framing and prohibits investment recommendations."""
    claims  = validate_jwt(jwt)
    metrics = await smr.list_approved_summary(claims, domain="regulatory")
    return f"""You are a regulatory reporting assistant operating under strict compliance constraints.

Available regulatory metrics:
{metrics}

Additional rules beyond the standard analytical assistant:
- Do not generate investment recommendations under any circumstances.
- For client-related queries, remind the user that a business justification will be required.
- Cite the result_id and lineage_url in every response that references a computed metric value.
- If a compliance mode error is returned, explain the constraint in plain English before retrying."""

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

#### Error Handling

All tool call failures return a structured error envelope. The MCP framework serialises Python exceptions as tool error responses; the platform maps exception classes to stable error codes before they leave the service boundary.

```python
class AnalyticsError(Exception):
    code:    str   # stable string identifier consumed by AI clients
    message: str   # human-readable; safe to surface to end users

class AuthenticationError(AnalyticsError):        code = "AUTH_FAILED"
class AccessDeniedError(AnalyticsError):          code = "ACCESS_DENIED"
class OperationNotAvailableError(AnalyticsError): code = "OPERATION_NOT_FOUND"
class MetricNotFoundError(AnalyticsError):        code = "METRIC_NOT_FOUND"
class PerformanceImpactCeilingExceeded(AnalyticsError): code = "CONTROLS_REJECTED"
class UserPerformanceImpactBudgetExceeded(AnalyticsError): code = "BUDGET_EXCEEDED"
class ConcurrentQueryLimitExceeded(AnalyticsError): code = "CAPACITY_LIMIT"
class NarrativeValidationError(AnalyticsError):   code = "NARRATIVE_FAILED"
class ClassificationGateError(AnalyticsError):    code = "CLASSIFICATION_BLOCKED"

def handle_tool_error(exc: Exception) -> dict:
    if isinstance(exc, AnalyticsError):
        return {"error": {"code": exc.code, "message": str(exc)}}
    return {"error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred."}}
```

Error code reference table:

| Code | Raised by | Consumer action |
|------|-----------|-----------------|
| `AUTH_FAILED` | JWT validation | Re-authenticate; do not retry with same token |
| `ACCESS_DENIED` | RAPL | Inform user; do not retry |
| `OPERATION_NOT_FOUND` | SMR | Call `list_operations` to discover valid operation IDs |
| `METRIC_NOT_FOUND` | SMR | Call `list_operations` to check available metrics |
| `CONTROLS_REJECTED` | SCL | Reduce metric count or time range; inform user |
| `BUDGET_EXCEEDED` | SCL | Inform user their hourly query budget is exhausted |
| `CAPACITY_LIMIT` | SCL | Retry with exponential back-off |
| `NARRATIVE_FAILED` | NSE | Return result without narrative; log for operator review |
| `CLASSIFICATION_BLOCKED` | SCL | Inform user the requested metric requires elevated access |
| `INTERNAL_ERROR` | Any | Log `result_id` if available; operator investigation required |

---

### Semantic Intent Layer

> **Specification:** [§Semantic Intent Layer](./02-core-capabilities.md#semantic-intent-layer)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Parameter validation** | JSON Schema + Pydantic | Strict schema enforcement against MCP tool input models; structured error responses |
| **SMR resolution** | Direct SMR service call | Synchronous lookup against the metric registry; rejects unregistered IDs before LQP generation |
| **LQP generation** | Custom Python | Backend-agnostic DAG construction from validated parameters; deterministic for any given input |

```python
class SemanticIntentLayer:
    def __init__(self, smr: "SemanticMetricsRegistry"):
        self.smr = smr

    async def resolve(self, operation: dict, params: dict, claims: dict) -> dict:
        self._validate_params(params, operation["required_params"])
        resolved_metrics = [
            await self.smr.get_metric(m, claims)
            for m in params.get("metrics", [])
        ]
        return self._build_lqp(operation, params, resolved_metrics)

    def _validate_params(self, params: dict, required: list[str]) -> None:
        missing = [k for k in required if k not in params]
        if missing:
            raise ValueError(f"Missing required params: {missing}")

    def _build_lqp(self, operation: dict, params: dict, metrics: list[dict]) -> dict:
        # Construct platform-agnostic DAG; each metric node carries physicalMapping from SMR
        nodes = []
        for metric in metrics:
            node = {
                "op":               "metric_scan",
                "metric_id":        metric["metric_id"],
                "metric_version":   metric["version"],
                "aggregation":      metric["aggregation"],
                "data_affinity":    metric["data_affinity"],
                "physical_mapping": metric["physical_mapping"],
            }
            if wm := metric.get("weight_metric_id"):
                node["weight_metric_id"] = wm
            nodes.append(node)
        # Append join, filter, time_expand, sort nodes from params
        ...
        return {"lqp_id": generate_id(), "nodes": nodes, "org_id": claims["org_id"]}
```

#### Stage 2b — Compliance Intent Classification

The SIL scores each resolved query for compliance intent using three independent signals. The score drives the SCL two-signal compliance gate without requiring the caller to declare compliance purpose explicitly.

```python
def _score_compliance_intent(self, operation: dict, resolved_metrics: list[dict], params: dict) -> float:
    # Signal sources: operation ID suffix, metric compliance_relevant flags, param keys
    score = 0.0
    if any(op in operation["operation_id"] for op in ["regulatory", "compliance", "audit", "report"]):
        score += 0.5
    if any(m.get("compliance_relevant") for m in resolved_metrics):
        score += 0.3
    if "justification" in params or "regulatory_period" in params:
        score += 0.2
    return min(score, 1.0)
```

`resolve()` attaches this score to the LQP before returning it:

```python
lqp["compliance_purpose_score"] = self._score_compliance_intent(operation, resolved_metrics, params)
lqp["resolved_metrics"]         = resolved_metrics   # retained for SCL compliance check
return lqp
```

---

### Narrative Synthesis Engine

> **Specification:** [§Narrative Synthesis Engine](./02-core-capabilities.md#narrative-synthesis-engine)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Provider** | Anthropic Claude | Reliable instruction-following for constrained summarisation tasks |
| **Standard queries** | Claude Haiku | Sub-200ms narrative generation for simple metric summaries |
| **Complex queries** | Claude Sonnet | Attribution decompositions and multi-portfolio results require richer prose |
| **Prompt construction** | Result-only context | Metric labels + row values + units injected; no user query, no physical schema |
| **Post-generation validation** | Custom Python | Every numeric value in narrative matched against result set; reject and retry once on failure |
| **Feature flag** | `features.narrativeSynthesis` | Platform-level on/off; disabled means NSE is never invoked |

```python
import anthropic

class NarrativeSynthesisEngine:
    def __init__(self, client: anthropic.AsyncAnthropic):
        self.client = client

    # Update model IDs on deprecation — or read from platform config models.narrativeSynthesisModel
    FAST_MODEL     = "claude-haiku-4-5-20251001"
    STANDARD_MODEL = "claude-sonnet-4-6"

    async def synthesise(self, result: dict, operation: dict) -> str:
        model  = self.FAST_MODEL if self._is_simple(result) else self.STANDARD_MODEL
        prompt = self._build_prompt(result, operation)

        for attempt in range(2):
            response  = await self.client.messages.create(
                model=model, max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            narrative = response.content[0].text
            try:
                self._validate_numbers(narrative, result["rows"])
                return narrative
            except NarrativeValidationError:
                if attempt == 1:
                    raise
        raise NarrativeValidationError("Narrative validation failed after 2 attempts")

    def _is_simple(self, result: dict) -> bool:
        # Route to Haiku for ≤5 metrics and ≤3 dimensions — matches Ch03 model selection spec
        schema = result.get("schema", [])
        metric_count    = sum(1 for f in schema if f.get("type") == "number")
        dimension_count = len(schema) - metric_count
        return metric_count <= 5 and dimension_count <= 3

    def _build_prompt(self, result: dict, operation: dict) -> str:
        # Inject metric labels + row values + units; no user query, no physical schema
        rows_text = "\n".join(str(row) for row in result["rows"])
        return f"Summarise this {operation['display_name']} result in 2-3 sentences:\n{rows_text}"

    def _validate_numbers(self, narrative: str, rows: list[dict]) -> None:
        # Every numeric value cited in the narrative must appear in result rows
        # Raise NarrativeValidationError; caller retries once before propagating
        ...
```

---

### Semantic Metrics Repository (SMR)

> **Specification:** [§Semantic Metrics Repository](./02-core-capabilities.md#semantic-metrics-registry)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Definition storage** | SDR (pre-existing) | Metric and operation definitions stored alongside existing data definitions — no duplicate semantic store |
| **Authoring and approval** | SDR native capabilities | Document creation, versioning, and approval workflow are handled by the existing SDR tooling — no new write layer needed |
| **Runtime reads** | Direct SDR API query by Semantic Intent Layer | Definitions from the authoritative source at resolution time |
| **Search** | SDR native search index | `list_operations` queries SDR directly — no separate search infrastructure |

The SMR is implemented as two new document types registered in the SDR. The SDR manages the full document lifecycle (draft → in review → approved → deprecated) for both types using its existing authoring and approval capabilities.

#### New SDR document type: `analytical_metric`

The core metric definition. One document per approved metric version. The `status` field follows the SDR approval lifecycle; the Semantic Intent Layer only resolves documents with `"status": "approved"`.

```json
{
  "type":                 "analytical_metric",
  "org_id":            "acme-wealth",
  "metric_id":            "var_95",
  "version":              2,
  "status":               "approved",
  "source":               "platform",
  "display_name":         "Value at Risk (95%)",
  "description":          "Maximum expected portfolio loss over a 1-day horizon at 95% confidence.",
  "domain":               "risk",
  "category":             "market_risk",
  "unit":                 "percentage",
  "decimals":             2,
  "aggregation":          "value_weighted_average",
  "weight_metric_id":     "market_value",
  "cost_weight":          3,
  "classification_level": "internal",
  "data_affinity":        "risk_metrics",
  "physical_mapping": {
    "source":  "risk-semantic-layer",
    "cube":    "risk_cube",
    "measure": "var_95_daily"
  },
  "formula":              "MAX(losses) WHERE confidence_level = 0.95",
  "compliance_relevant":  false,
  "regulatory_framework": [],
  "required_dimensions":  ["portfolio_id", "as_of_date"],
  "optional_dimensions":  ["asset_class", "geography", "sector", "currency"],
  "approved_by":          "cdo@acme.com",
  "approved_at":          "2026-05-14T09:00:00Z",
  "created_at":           "2026-05-13T14:32:00Z"
}
```

`status` is one of `"proposed"` | `"in_review"` | `"approved"` | `"deprecated"` | `"retired"`. The SDR enforces a uniqueness constraint: at most one document per `(org_id, metric_id)` may carry `"status": "approved"` at any point in time. All prior versions are retained as `"deprecated"` for lineage reconstruction. `source` is `"platform"` for Financial Services Reference Model entries and `"custom"` for organisation-customised definitions.

`weight_metric_id` is required when `aggregation` is `"value_weighted_average"` (or any other weighted aggregation variant) and must reference the `metric_id` of an approved `analytical_metric` in the platform's SDR. The SIL resolves and validates this reference at query time. If the weight metric is missing or unapproved, the query is rejected. The field is absent for non-weighted aggregations (`"sum"`, `"last"`, `"count"`, `"min"`, `"max"`, `"mean"`). The LQP generator emits a `weight_metric_id` key on the `metric_scan` node so that the execution backend can fetch the weighting values alongside the primary metric.

`formula` stores the business-logic expression defined in the [SMR formula language](./02-core-capabilities.md#formula-language). It is the human-readable and audit-visible definition of what the metric computes. At query time the FQE resolves the formula against the `physical_mapping` to generate the backend-specific query; the formula itself is never executed directly. Metrics backed entirely by a pre-computed measure in a semantic layer (e.g. a Cube.js measure) may leave `formula` as an empty string and rely solely on `physical_mapping`.

#### New SDR document type: `analytical_dimension`

Dimension definitions are the third new document type. They define the valid slicing axes referenced in `supported_dimensions` and `required_dimensions` on metrics and operations. The SIL validates dimension IDs against this catalogue at resolution time.

```json
{
  "type":             "analytical_dimension",
  "org_id":        "acme-wealth",
  "dimension_id":     "asset_class",
  "version":          1,
  "status":           "approved",
  "source":           "platform",
  "display_name":     "Asset Class",
  "description":      "Top-level asset class classification applied to holdings.",
  "data_affinity":    "portfolio",
  "physical_mapping": { "source": "primary-warehouse", "table": "dim_asset_classification", "column": "asset_class" },
  "values":           ["EQUITY", "FIXED_INCOME", "ALTERNATIVES", "CASH", "DERIVATIVES"],
  "hierarchical":     false,
  "parent_dimension": null
}
```

#### New SDR document type: `analytical_operation`

The operation catalogue. One document per approved operation. The `execution_profile` field tells the pipeline executor which stages to invoke. The `supported_metrics` and `supported_dimensions` lists are enforced by the Semantic Intent Layer. A `run_analytics` call referencing an out-of-catalogue value is rejected before LQP generation.

```json
{
  "type":              "analytical_operation",
  "org_id":         "acme-wealth",
  "operation_id":        "get_positions",
  "version":             1,
  "status":              "approved",
  "source":              "platform",
  "display_name":        "Portfolio Positions",
  "description":         "Fetch current or historical position data for a portfolio.",
  "execution_profile":   "data_retrieval",
  "required_params":     ["portfolio_id"],
  "optional_params":     ["as_of_date", "asset_class"],
  "supported_metrics":   [],
  "supported_dimensions": ["portfolio_id", "asset_class", "currency", "instrument_id", "as_of_date"]
}
```

```python
class SemanticMetricsRegistry:
    def __init__(self, sdr_client):
        self.sdr = sdr_client

    async def get_operation(self, operation_id: str, claims: dict) -> dict:
        doc = await self.sdr.get(
            document_type="analytical_operation",
            id=operation_id,
            org_id=claims["org_id"],
        )
        if doc["status"] != "approved":
            raise OperationNotAvailableError(operation_id)
        return doc

    async def list_operations(self, claims: dict, domain: str | None = None) -> list[dict]:
        return await self.sdr.search(
            document_type="analytical_operation",
            org_id=claims["org_id"],
            filters={"domain": domain} if domain else {},
        )

    async def get_metric(self, metric_id: str, claims: dict) -> dict:
        return await self.sdr.get(
            document_type="analytical_metric",
            id=metric_id,
            org_id=claims["org_id"],
        )

    async def list_metrics(self, claims: dict, **filters) -> list[dict]:
        return await self.sdr.search(
            document_type="analytical_metric",
            org_id=claims["org_id"],
            filters=filters,
        )

    async def list_approved_summary(self, claims: dict, domain: str | None = None) -> list[dict]:
        metrics = await self.list_metrics(claims, status="approved", domain=domain)
        return [{"id": m["metric_id"], "label": m["display_name"], "description": m["description"]}
                for m in metrics]
```

---

### Semantic Intent Layer and LQP Generator

No custom query language. The MCP tool call JSON (metric IDs, dimension IDs, time period, filters) is the analytical intent representation, consistent with Cube.js and MetricFlow conventions.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Intent format** | MCP tool call JSON | Standard AI tool-use format; no separate language needed |
| **Implementation** | Python (JSON schema + SMR resolution via SDR API) | Lightweight; no grammar or parser |
| **LQP format** | Custom DAG (JSON) | Engine-agnostic across SQL, OpenData, and Graph backends |

#### MCP input example

```json
{
  "tool": "run_analytics",
  "input": {
    "operation_id": "compare_portfolios",
    "params": {
      "portfolio_ids": ["GLOB_EQ_OPP", "UK_CORE_INC"],
      "metrics":       ["portfolio_return", "tracking_error"],
      "time_period":   "quarter_to_date"
    }
  }
}
```

The Semantic Intent Layer resolves metric IDs against the SMR, merges in role predicates from the RAPL, and emits an platform-agnostic LQP. The LQP carries resolved `physicalMapping` references, expanded time ranges, role-injected filters, and a performance impact estimate for governance validation.

#### LQP output example

```json
{
  "lqp_id": "lqp-20260514-093241-xyz",
  "org_id": "acme-wealth",
  "nodes": [
    {
      "id": "node-1",
      "op": "metric_scan",
      "metric_id": "portfolio_return",
      "metric_version": "2.1.0",
      "aggregation": "value_weighted_average",
      "data_affinity": "portfolio",
      "physical_mapping": { "source": "primary-warehouse", "table": "fact_portfolio_daily" }
    },
    {
      "id": "node-2",
      "op": "metric_scan",
      "metric_id": "tracking_error",
      "metric_version": "1.3.0",
      "aggregation": "value_weighted_average",
      "data_affinity": "risk_metrics",
      "physical_mapping": { "source": "risk-semantic-layer", "cube": "risk_cube" }
    },
    {
      "id": "node-3",
      "op": "join",
      "inputs": ["node-1", "node-2"],
      "join_keys": ["portfolio_id", "date"]
    },
    {
      "id": "node-4",
      "op": "filter",
      "input": "node-3",
      "predicates": [
        "portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC')",
        "asset_class = 'EQUITY'"
      ]
    },
    {
      "id": "node-5",
      "op": "time_expand",
      "input": "node-4",
      "period": "quarter_to_date",
      "as_of_date": "2026-05-14",
      "resolved_range": { "from": "2026-04-01", "to": "2026-05-14" }
    },
    {
      "id": "node-6",
      "op": "sort",
      "input": "node-5",
      "by": [{ "field": "portfolio_return", "direction": "desc" }]
    }
  ],
  "estimated_performance_impact": 850,
  "column_masks": [],
  "row_predicates_applied": true
}
```

```python
from datetime import date, timedelta

class LQPGenerator:
    def build(
        self,
        operation:  dict,
        params:     dict,
        metrics:    list[dict],
        dimensions: list[dict],
        claims:     dict,
    ) -> dict:
        nodes    = []
        node_seq = 0

        def next_id() -> str:
            nonlocal node_seq
            node_seq += 1
            return f"node-{node_seq}"

        # 1. One metric_scan node per resolved metric
        scan_ids = []
        for metric in metrics:
            nid  = next_id()
            node = {
                "id":               nid,
                "op":               "metric_scan",
                "metric_id":        metric["metric_id"],
                "metric_version":   metric["version"],
                "aggregation":      metric["aggregation"],
                "data_affinity":    metric["data_affinity"],
                "physical_mapping": metric["physical_mapping"],
            }
            if wm := metric.get("weight_metric_id"):
                node["weight_metric_id"] = wm   # present only for weighted aggregations
            nodes.append(node)
            scan_ids.append(nid)

        # 2. Join if metrics span multiple nodes
        current = scan_ids[0]
        if len(scan_ids) > 1:
            join_id = next_id()
            nodes.append({
                "id":        join_id,
                "op":        "join",
                "inputs":    scan_ids,
                "join_keys": self._infer_join_keys(metrics),
            })
            current = join_id

        # 3. Filter — from params["filters"] and any role predicates already merged in
        filters = params.get("filters", [])
        if filters:
            filter_id = next_id()
            nodes.append({
                "id":         filter_id,
                "op":         "filter",
                "input":      current,
                "predicates": [self._render_predicate(f) for f in filters],
            })
            current = filter_id

        # 4. Time expansion — resolve symbolic period to a concrete date range
        if "time_period" in params or "as_of_date" in params:
            time_id = next_id()
            nodes.append({
                "id":             time_id,
                "op":             "time_expand",
                "input":          current,
                "period":         params.get("time_period"),
                "as_of_date":     params.get("as_of_date"),
                "resolved_range": self._resolve_time(params),
            })
            current = time_id

        # 5. Sort — from operation default or params override
        sort_by = params.get("sort") or operation.get("default_sort")
        if sort_by:
            sort_id = next_id()
            nodes.append({"id": sort_id, "op": "sort", "input": current, "by": sort_by})
            current = sort_id

        return {
            "lqp_id":    generate_id("lqp"),
            "org_id": claims["org_id"],
            "nodes":     nodes,
            "output":    current,   # terminal node consumed by FQE
        }

    def _infer_join_keys(self, metrics: list[dict]) -> list[str]:
        # Intersection of required_dimensions across all metrics — safe shared join keys
        key_sets = [set(m.get("required_dimensions", [])) for m in metrics]
        keys = list(set.intersection(*key_sets)) if key_sets else []
        if not keys:
            raise ValueError(
                f"No shared required_dimensions across metrics — cannot infer join keys. "
                f"Ensure all co-queried metrics share at least one canonical dimension name. "
                f"Metrics: {[m['metric_id'] for m in metrics]}"
            )
        return keys

    def _render_predicate(self, f: dict) -> str:
        op_map = {
            "eq": "=", "neq": "!=", "gt": ">", "lt": "<", "gte": ">=", "lte": "<=",
            "in": "IN", "not_in": "NOT IN",
        }
        op  = op_map[f["operator"]]
        val = f"({', '.join(repr(v) for v in f['value'])})" if isinstance(f["value"], list) \
              else repr(f["value"])
        return f"{f['dimension']} {op} {val}"

    def _resolve_time(self, params: dict) -> dict:
        as_of  = date.fromisoformat(params.get("as_of_date", date.today().isoformat()))
        period = params.get("time_period", "")
        if period == "quarter_to_date":
            start = date(as_of.year, ((as_of.month - 1) // 3) * 3 + 1, 1)
        elif period == "month_to_date":
            start = as_of.replace(day=1)
        elif period == "year_to_date":
            start = as_of.replace(month=1, day=1)
        elif period == "trailing_12m":
            start = as_of.replace(year=as_of.year - 1)
        else:
            start = as_of   # point-in-time or caller-supplied range
        return {"from": start.isoformat(), "to": as_of.isoformat()}
```

---

### Role-Aware Projection Layer

> **Specification:** [§Role-Aware Projection Layer](./02-core-capabilities.md#role-aware-projection-layer)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom middleware (Python) | Thin, stateless; operates on the LQP before any backend query is generated |
| **Role resolution** | JWT claim extraction + PostgreSQL role config | Role claim field name is configurable |
| **Row predicates** | `{{user.claim_name}}` template interpolation at LQP build time | Resolved from JWT claims; injected into LQP `filters` |
| **Column masking** | Applied post-assembly in FQE result assembler | Post-assembly supports cross-backend result sets |
| **Default policy** | `defaultDenyAll: true` | No access unless a matching role is found |

#### Role policies schema

Role policy documents are stored in the PostgreSQL `role_policies` table. Each document maps directly to the following JSON shape:

```json
{
  "role_id":        "regional_analyst",
  "org_id":         "acme-wealth",
  "allowed_metrics": null,
  "denied_metrics":  ["var_99", "expected_shortfall"],
  "row_predicates": {
    "portfolio": "portfolio_id IN ({{user.managed_portfolios}})"
  },
  "column_masks": {
    "aum": {
      "condition":   "{{user.roles}} NOT CONTAINS 'senior_analyst'",
      "action":      "suppress",
      "replacement": null
    }
  },
  "created_at": "2026-05-14T09:00:00Z",
  "updated_at": "2026-05-14T09:00:00Z"
}
```

Field reference:

| Field | Type | Description |
|-------|------|-------------|
| `role_id` | string | Matches the role name in the JWT `analytics_roles` claim |
| `org_id` | string | Tenant scope — one policy per org per role |
| `allowed_metrics` | array \| null | Null = all metrics permitted; array = explicit allowlist |
| `denied_metrics` | array | Metric IDs denied regardless of allowedMetrics |
| `row_predicates` | object | Key = dimension name; value = `{{user.claim}}` template string |
| `column_masks` | object | Key = field name; value = mask rule with `action: "suppress"` or `"hash"` |

```python
class RoleAwareProjectionLayer:
    def __init__(self, pg_pool):
        self.pg = pg_pool

    async def project(self, lqp: dict, claims: dict) -> dict:
        # analytics_roles is an array claim — users may hold multiple roles
        # roleClaimField is configurable (see Ch04 §entitlements config)
        role_claim_field = self.config.get("roleClaimField", "analytics_roles")
        roles = claims.get(role_claim_field, [])
        if isinstance(roles, str):
            roles = [roles]  # normalise scalar claim to list

        policies = [p for p in [await self._load_policy(claims["org_id"], r) for r in roles] if p]
        if not policies:
            raise AccessDeniedError("No role policy found — defaultDenyAll")

        # Merge: metric access = union across roles; row predicates = intersection (most restrictive)
        merged = self._merge_policies(policies)
        lqp = self._inject_row_predicates(lqp, merged, claims)
        lqp["column_masks"] = merged.get("columnMasks", {})
        return lqp

    def _merge_policies(self, policies: list[dict]) -> dict:
        # Row predicates: intersection (AND — most restrictive role wins)
        # Column masks: union (masked by any role = masked for the user)
        # Metric access: union (permitted by any role = permitted)
        row_predicates = policies[0].get("rowPredicates", {})
        for p in policies[1:]:
            # Intersection: keep only predicates present in all role policies
            row_predicates = {k: v for k, v in row_predicates.items() if k in p.get("rowPredicates", {})}
        column_masks: dict = {}
        for p in policies:
            column_masks.update(p.get("columnMasks", {}))
        return {"rowPredicates": row_predicates, "columnMasks": column_masks}

    def _inject_row_predicates(self, lqp: dict, policy: dict, claims: dict) -> dict:
        for dimension, template in policy.get("rowPredicates", {}).items():
            predicate = self._interpolate(template, claims)
            lqp["nodes"].append({"op": "filter", "predicates": [predicate]})
        lqp["row_predicates_applied"] = True
        return lqp

    def _interpolate(self, template: str, claims: dict) -> str:
        # Replace {{user.claim_name}} tokens with JWT claim values
        ...

    async def _load_policy(self, org_id: str, role: str) -> dict | None:
        return await self.pg.fetchrow(
            "SELECT * FROM role_policies WHERE org_id=$1 AND role_id=$2",
            org_id, role,
        )
```

---

### Semantic Controls Layer

> **Specification:** [§Semantic Controls Layer](./02-core-capabilities.md#semantic-controls-layer)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Implementation** | Custom rules engine (Python) | Deterministic; config-driven; no ML inference |
| **Performance impact assessment** | `Σ(metric.costWeight × dimensionCardinality × timeRangeMultiplier)` | Pre-execution; calibrated against actual cost data |
| **Threshold** | Per-request ceiling + per-user hourly performance impact budget | Hard ceiling prevents runaway queries |
| **Config store** | SDR document store — `controls_config` document type | Platform-level thresholds stored as a JSON document alongside SMR documents |

Concurrent query enforcement uses a Redis-backed semaphore rather than an in-process counter, ensuring the limit applies across all running pods.

The platform has one controls config document. The Semantic Controls Layer reads it at startup and refreshes it on change events from the SDR:

```json
{
  "type":                       "controls_config",
  "org_id":                  "acme-wealth",
  "performance_impact_ceiling_per_query":     1000,
  "performance_impact_budget_per_user_hourly": 10000,
  "max_concurrent_queries":     20,
  "max_metrics_per_query":      10,
  "max_dimensions":             5,
  "classification_gate":        true,
  "blocked_classifications":    ["TOP_SECRET", "RESTRICTED"],
  "query_timeout_seconds":      60,
  "compliance_mode_enabled":     true,
  "require_lineage_for_export": true,
  "audit_all_queries":          true,
  "compliance_intent_threshold": 0.8
}
```

```python
class SemanticControlsLayer:
    def __init__(self, sdr_client, pg_pool, redis_client):
        self.sdr   = sdr_client
        self.pg    = pg_pool
        self.redis = redis_client

    async def _acquire_query_slot(self, org_id: str, config: dict) -> None:
        key     = f"query_slots:{org_id}"
        ceiling = config["max_concurrent_queries"]
        count   = await self.redis.incr(key)
        await self.redis.expire(key, config["query_timeout_seconds"] + 5)
        if count > ceiling:
            await self.redis.decr(key)
            raise ConcurrentQueryLimitExceeded(f"Org {org_id} at concurrent query limit ({ceiling})")

    async def _release_query_slot(self, org_id: str) -> None:
        await self.redis.decr(f"query_slots:{org_id}")

    async def approve(self, lqp: dict, claims: dict) -> dict:
        config = await self._load_config(claims["org_id"])
        await self._acquire_query_slot(claims["org_id"], config)
        try:
            pass  # existing checks below — slot released by FQE after execution completes
        except Exception:
            await self._release_query_slot(claims["org_id"])
            raise

        performance_impact = self._estimate_performance_impact(lqp, config)
        if performance_impact > config["performance_impact_ceiling_per_query"]:
            raise PerformanceImpactCeilingExceeded(performance_impact)

        spend = await self._hourly_spend(claims["sub"], claims["org_id"])
        if spend + performance_impact > config["performance_impact_budget_per_user_hourly"]:
            raise UserPerformanceImpactBudgetExceeded()

        self._check_classification(lqp, config)
        lqp = self._check_compliance(lqp, claims, config)

        lqp["estimated_performance_impact"] = performance_impact
        lqp["controls_approved"]            = True
        return lqp

    def _estimate_performance_impact(self, lqp: dict, config: dict) -> int:
        TIME_MULTIPLIERS = {
            "month_to_date":    1.0,
            "quarter_to_date":  2.0,
            "year_to_date":     4.0,
            "trailing_12m":     6.0,
            "trailing_3y":     18.0,
        }
        DIMENSION_CARDINALITY = {   # estimated cardinality per dimension type
            "portfolio_id":  10,
            "asset_class":    5,
            "sector":        11,
            "geography":    200,
            "currency":      50,
            "issuer":      5000,
        }

        metrics    = lqp.get("resolved_metrics", [])
        dimensions = [n for n in lqp["nodes"] if n["op"] == "filter"]
        time_node  = next((n for n in lqp["nodes"] if n["op"] == "time_expand"), None)

        time_multiplier = TIME_MULTIPLIERS.get(
            time_node["period"] if time_node else "", 1.0
        )
        dim_cardinality = sum(
            DIMENSION_CARDINALITY.get(dim, 100)
            for dim in lqp.get("requested_dimensions", [])
        ) or 1

        return int(sum(
            m.get("cost_weight", 1) * dim_cardinality * time_multiplier
            for m in metrics
        ))

    def _check_classification(self, lqp: dict, config: dict) -> None:
        # Reject if any metric classificationLevel is in blocked_classifications
        ...

    def _check_compliance(self, lqp: dict, claims: dict, config: dict) -> dict:
        # Two-signal compliance escalation:
        # Signal 1 — any resolved metric has compliance_relevant: true
        # Signal 2 — compliance_purpose_score meets configured threshold
        compliance_metrics = [
            m["metric_id"] for m in lqp.get("resolved_metrics", [])
            if m.get("compliance_relevant", False)
        ]
        threshold = config.get("compliance_intent_threshold", 0.8)
        intent_score = lqp.get("compliance_purpose_score", 0.0)
        compliance_purpose = intent_score >= threshold

        if compliance_metrics and compliance_purpose:
            # Escalate to Provenance Artifact generation
            triggered_frameworks = list({
                fw
                for m in lqp.get("resolved_metrics", [])
                if m.get("compliance_relevant")
                for fw in m.get("regulatory_framework", [])
            })
            lqp["compliance_tier"] = {
                "active":                  True,
                "intent_score":            intent_score,
                "triggered_by_metrics":    compliance_metrics,
                "triggered_by_frameworks": triggered_frameworks,
                "bypass_cache":            True,
            }
            # Enforce lineage-gated export regardless of platform config
            lqp["require_lineage_for_export"] = True
        else:
            lqp["compliance_tier"] = {"active": False}

        return lqp

    async def _load_config(self, org_id: str) -> dict:
        return await self.sdr.get(document_type="controls_config", org_id=org_id)

    async def _hourly_spend(self, user_sub: str, org_id: str) -> int:
        return await self.pg.fetchval(
            "SELECT COALESCE(SUM(performance_impact_units), 0) FROM analytics.lineage_index "
            "WHERE user_sub=$1 AND org_id=$2 AND created_at > now() - interval '1 hour'",
            user_sub, org_id,
        )
```

---

### Federated Query Engine (FQE)

> **Specification:** [§Federated Query Engine](./02-core-capabilities.md#federated-query-planner)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Plan optimiser** | Apache Calcite (within SQL warehouse adapters) | Battle-tested SQL plan optimisation; used by Trino, Flink, Beam. Calcite is invoked inside each SQL warehouse adapter to optimise the physical sub-plan SQL before execution — not at the Python FQE orchestration layer, which handles LQP decomposition and result assembly |
| **Backend adapters** | Custom adapter per backend type | Calcite handles SQL; custom adapters cover REST/OpenData/GraphQL/SPARQL |
| **Result assembly** | Custom (Python) | Fan-out/fan-in; no off-the-shelf library needed |

The FQE splits the LQP by `dataAffinity`, assigns each sub-plan to the matching registered backend, translates to the backend's native protocol (SQL, OData, SPARQL, etc.), fans out execution in parallel, and assembles results. Each execution backend implements a two-method adapter contract: `ping()` for health checking and `executeSubPlan()` for receiving a sub-plan fragment and returning a typed result set.

#### FQE input — approved LQP

The FQE receives the governance-approved LQP produced by the Semantic Intent Layer. It reads `data_affinity` on each metric node to determine which backend to route each sub-plan to:

```json
{
  "lqp_id": "lqp-20260514-093241-xyz",
  "org_id": "acme-wealth",
  "nodes": [
    {
      "id": "node-1", "op": "metric_scan",
      "metric_id": "portfolio_return", "metric_version": "2.1.0",
      "aggregation": "value_weighted_average", "weight_metric_id": "market_value",
      "data_affinity": "portfolio",
      "physical_mapping": { "source": "primary-warehouse", "table": "fact_portfolio_daily" }
    },
    {
      "id": "node-2", "op": "metric_scan",
      "metric_id": "tracking_error", "metric_version": "1.3.0",
      "aggregation": "value_weighted_average", "weight_metric_id": "market_value",
      "data_affinity": "risk_metrics",
      "physical_mapping": { "source": "risk-semantic-layer", "cube": "risk_cube" }
    },
    { "id": "node-3", "op": "join",   "inputs": ["node-1", "node-2"], "join_keys": ["portfolio_id", "date"] },
    { "id": "node-4", "op": "filter", "input": "node-3",
      "predicates": ["portfolio_id IN ('GLOB_EQ_OPP', 'UK_CORE_INC')", "asset_class = 'EQUITY'"] },
    { "id": "node-5", "op": "time_expand", "input": "node-4",
      "period": "quarter_to_date", "resolved_range": { "from": "2026-04-01", "to": "2026-05-14" } },
    { "id": "node-6", "op": "sort", "input": "node-5",
      "by": [{ "field": "portfolio_return", "direction": "desc" }] }
  ],
  "estimated_performance_impact": 850,
  "governance_approved": true,
  "row_predicates_applied": true,
  "column_masks": []
}
```

The FQE decomposes this into two sub-plans (one routed to `primary-warehouse`, nodes 1, 4, 5, 6, and one to `risk-semantic-layer`, node 2), executes them in parallel, and joins on `portfolio_id` and `date` at assembly.

#### FQE output — assembled result

After execution and result assembly the FQE returns a typed result envelope in parallel to the Data Visualization Language (DVL) and Narrative Synthesis Engine:

```json
{
  "result_id":      "res_20260514_093247_a1b2c3",
  "lqp_id":        "lqp-20260514-093241-xyz",
  "org_id":     "acme-wealth",
  "cache_hit":     false,
  "latency_ms":    1243,
  "performance_impact_units": 850,
  "backends_used": ["primary-warehouse", "risk-semantic-layer"],
  "schema": [
    { "field": "portfolio_id",     "type": "string"  },
    { "field": "portfolio_return", "type": "number", "unit": "percentage", "decimals": 2 },
    { "field": "tracking_error",   "type": "number", "unit": "percentage", "decimals": 2 }
  ],
  "rows": [
    { "portfolio_id": "GLOB_EQ_OPP", "portfolio_return": 4.21, "tracking_error": 3.18 },
    { "portfolio_id": "UK_CORE_INC", "portfolio_return": 2.87, "tracking_error": 1.94 }
  ],
  "sub_plans": [
    {
      "backend":    "primary-warehouse",
      "dialect":    "snowflake_sql",
      "query":      "SELECT portfolio_id, AVG(portfolio_return) AS portfolio_return FROM fact_portfolio_daily WHERE portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC') AND asset_class = 'EQUITY' AND date BETWEEN '2026-04-01' AND '2026-05-14' GROUP BY portfolio_id ORDER BY portfolio_return DESC",
      "latency_ms": 980,
      "row_count":  2
    },
    {
      "backend":    "risk-semantic-layer",
      "dialect":    "metricflow",
      "query":      { "metrics": ["tracking_error"], "group_by": ["portfolio_id"], "where": "portfolio_id IN ('GLOB_EQ_OPP','UK_CORE_INC')" },
      "latency_ms": 620,
      "row_count":  2
    }
  ]
}
```

#### Supported backend adapters

| Backend type | Adapter | Protocols |
|-------------|---------|-----------|
| **SQL warehouse** | Calcite SQL adapter | Snowflake, BigQuery, Databricks, Redshift, Trino, Starburst, PostgreSQL |
| **Semantic layer** | Semantic layer adapter | dbt Semantic Layer (MetricFlow), Cube.js |
| **OpenData API** | REST/OData adapter | REST JSON, OData v4, SOAP (via shim) |
| **Graph Data API** | Graph adapter | Neo4j Bolt, Amazon Neptune SPARQL, OpenCypher REST |
| **OLAP engine** | OLAP adapter | Apache Druid, ClickHouse, Pinot |
| **Custom** | Custom adapter interface | Any backend conforming to the `FQPBackendAdapter` contract |

#### SQL Warehouse Adapter — worked example

```python
import snowflake.connector    # swap for bigquery / databricks connector per target

class SnowflakeAdapter:
    def __init__(self, connection_params: dict):
        self.conn_params = connection_params

    async def ping(self) -> bool:
        try:
            conn = snowflake.connector.connect(**self.conn_params)
            conn.cursor().execute("SELECT 1")
            return True
        except Exception:
            return False

    async def execute_sub_plan(self, sub_plan: dict) -> dict:
        sql, params = self._render_sql(sub_plan)
        conn        = snowflake.connector.connect(**self.conn_params)
        cursor      = conn.cursor()
        cursor.execute(sql, params)
        columns = [d[0].lower() for d in cursor.description]
        rows    = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"affinity": sub_plan["affinity"], "rows": rows, "columns": columns}

    def _render_sql(self, sub_plan: dict) -> tuple[str, list]:
        # Build parameterised SQL from LQP node list
        metric_nodes = [n for n in sub_plan["nodes"] if n["op"] == "metric_scan"]
        filter_nodes = [n for n in sub_plan["nodes"] if n["op"] == "filter"]
        time_node    = next((n for n in sub_plan["nodes"] if n["op"] == "time_expand"), None)
        sort_node    = next((n for n in sub_plan["nodes"] if n["op"] == "sort"), None)

        # SELECT clause — one column per metric measure
        selects = [f"{n['physical_mapping']['measure']} AS {n['metric_id']}" for n in metric_nodes]
        table   = metric_nodes[0]["physical_mapping"]["table"]

        sql    = f"SELECT {', '.join(selects)} FROM {table}"
        params = []

        # WHERE clause — from filter node predicates
        where = []
        for node in filter_nodes:
            for pred in node.get("predicates", []):
                where.append(pred)
        if time_node:
            where.append(f"date BETWEEN %s AND %s")
            params += [time_node["resolved_range"]["from"], time_node["resolved_range"]["to"]]
        if where:
            sql += " WHERE " + " AND ".join(where)

        # ORDER BY
        if sort_node:
            by  = sort_node["by"][0]
            sql += f" ORDER BY {by['field']} {by['direction'].upper()}"

        return sql, params
```

```python
import asyncio

class FederatedQueryPlanner:
    def __init__(self, backend_registry: dict, lineage_store: "AnalyticalLineageStore"):
        self.backends = backend_registry   # data_affinity → FQPBackendAdapter
        self.lineage  = lineage_store

    async def execute(self, lqp: dict) -> dict:
        sub_plans = self._split_by_affinity(lqp)
        results   = await asyncio.gather(*[self._execute_sub_plan(sp) for sp in sub_plans])
        assembled = self._assemble(results, lqp)
        await self.lineage.write_execution(lqp, assembled)
        return assembled

    def _split_by_affinity(self, lqp: dict) -> list[dict]:
        # Group metric_scan nodes by data_affinity; each group becomes a sub-plan
        groups: dict[str, list] = {}
        for node in lqp["nodes"]:
            if node["op"] == "metric_scan":
                groups.setdefault(node["data_affinity"], []).append(node)
        return [{"affinity": aff, "nodes": nodes} for aff, nodes in groups.items()]

    async def _execute_sub_plan(self, sub_plan: dict) -> dict:
        adapter = self.backends[sub_plan["affinity"]]
        return await adapter.execute_sub_plan(sub_plan)

    def _assemble(self, results: list[dict], lqp: dict) -> dict:
        # Fan-in: join on shared keys, apply sort/limit, apply column masks
        ...


class FQPBackendAdapter:
    async def ping(self) -> bool: ...
    async def execute_sub_plan(self, sub_plan: dict) -> dict: ...
```

---

### Data Visualization Language (DVL)

> **Specification:** [§Data Visualization Language (DVL)](./02-core-capabilities.md#data-visualization-language-dvl)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Chart spec** | Vega-Lite v5 JSON | Industry-standard chart grammar; wide ecosystem for web, server-side, and image rendering |
| **Table spec** | Platform-defined `type: "table"` extension | Vega-Lite has no native table mark; same `data` + `columns` convention |

#### Data Visualization Language (DVL) input

The ontology evaluator receives the FQE assembled result alongside the resolved intent pattern. It uses the result schema and intent pattern to select the best-matching chart contract:

```json
{
  "intent_pattern": "COMPARISON",
  "schema": [
    { "field": "portfolio_id",     "type": "string"  },
    { "field": "portfolio_return", "type": "number", "unit": "percentage" },
    { "field": "tracking_error",   "type": "number", "unit": "percentage" }
  ],
  "rows": [
    { "portfolio_id": "GLOB_EQ_OPP", "portfolio_return": 4.21, "tracking_error": 3.18 },
    { "portfolio_id": "UK_CORE_INC", "portfolio_return": 2.87, "tracking_error": 1.94 }
  ],
  "sort": { "field": "portfolio_return", "direction": "desc" },
  "allowed_chart_types": ["bar", "line", "scatter", "heatmap", "treemap", "table"]
}
```

#### Data Visualization Language (DVL) output — DVL display spec

The evaluator matches the `COMPARISON` intent pattern and two-metric schema to the `BAR_MULTI_SERIES_COMPARISON` contract and emits a Vega-Lite v5 DVL display spec:

```json
{
  "type": "chart",
  "contract": "BAR_MULTI_SERIES_COMPARISON",
  "mark": "bar",
  "data": {
    "values": [
      { "portfolio_id": "GLOB_EQ_OPP", "metric": "Portfolio Return", "value": 4.21 },
      { "portfolio_id": "GLOB_EQ_OPP", "metric": "Tracking Error",   "value": 3.18 },
      { "portfolio_id": "UK_CORE_INC", "metric": "Portfolio Return", "value": 2.87 },
      { "portfolio_id": "UK_CORE_INC", "metric": "Tracking Error",   "value": 1.94 }
    ]
  },
  "encoding": {
    "x":      { "field": "portfolio_id", "type": "nominal",      "title": "Portfolio",     "sort": "-y" },
    "y":      { "field": "value",        "type": "quantitative", "title": "Value (%)",     "axis": { "format": ".2f" } },
    "color":  { "field": "metric",       "type": "nominal",      "title": "Metric" }
  },
  "colorScheme": ["#003f5c", "#bc5090"],
  "formatHints": {
    "portfolio_return": { "format": ".2%", "unit": "%" },
    "tracking_error":   { "format": ".2%", "unit": "%" }
  },
  "interactions": ["click:drilldown", "hover:tooltip", "select:multi-point"]
}
```

Full DVL examples including the `type: "table"` spec are in [Analytical Output Format](./02-core-capabilities.md#analytical-output-format). Full chart contract definitions are in [Data Visualization Language (DVL)](./02-core-capabilities.md#data-visualization-language-dvl).

```python
INTENT_CONTRACTS = {
    ("ATTRIBUTION",  1): "ATTRIBUTION_WATERFALL",
    ("COMPARISON",   2): "BAR_MULTI_SERIES_COMPARISON",
    ("TREND",        1): "LINE_TIME_SERIES",
    ("DISTRIBUTION", 1): "HISTOGRAM",
}

class DataVisualizationLanguage:
    def evaluate(self, result: dict, operation: dict) -> dict:
        intent   = self._infer_intent(operation)
        contract = self._match_contract(intent, result["schema"])
        return self._build_display_spec(contract, result, operation)

    def _infer_intent(self, operation: dict) -> str:
        intent_map = {
            "attribution_waterfall":       "ATTRIBUTION",
            "bar_multi_series_comparison": "COMPARISON",
            "line_time_series":            "TREND",
            "histogram":                   "DISTRIBUTION",
            "table":                       "TABLE",
        }
        return intent_map.get(operation.get("default_visualization", "table"), "TABLE")

    def _match_contract(self, intent: str, schema: list) -> str:
        num_metrics = sum(1 for f in schema if f["type"] == "number")
        return INTENT_CONTRACTS.get((intent, num_metrics), "TABLE")

    def _build_display_spec(self, contract: str, result: dict, operation: dict) -> dict:
        metric_fields = [f["field"] for f in result["schema"] if f["type"] == "number"]
        dim_field     = next(f["field"] for f in result["schema"] if f["type"] == "string")

        if contract == "TABLE":
            return {
                "type":    "table",
                "columns": [{"field": f["field"], "label": f["field"].replace("_", " ").title(),
                              "type": f["type"]} for f in result["schema"]],
                "data":    {"values": result["rows"]},
            }

        if contract == "BAR_MULTI_SERIES_COMPARISON":
            # Pivot to long form: one row per (dimension × metric)
            values = [
                {dim_field: row[dim_field], "metric": mf.replace("_", " ").title(), "value": row[mf]}
                for row in result["rows"]
                for mf in metric_fields
            ]
            return {
                "type":     "chart",
                "contract": contract,
                "mark":     "bar",
                "data":     {"values": values},
                "encoding": {
                    "x":     {"field": dim_field,  "type": "nominal",      "sort": "-y"},
                    "y":     {"field": "value",    "type": "quantitative", "axis": {"format": ".2f"}},
                    "color": {"field": "metric",   "type": "nominal"},
                },
                "formatHints":  {mf: {"format": ".2%"} for mf in metric_fields},
                "interactions": ["click:drilldown", "hover:tooltip", "select:multi-point"],
            }

        if contract == "LINE_TIME_SERIES":
            return {
                "type":     "chart",
                "contract": contract,
                "mark":     "line",
                "data":     {"values": result["rows"]},
                "encoding": {
                    "x":     {"field": "date",              "type": "temporal"},
                    "y":     {"field": metric_fields[0],    "type": "quantitative"},
                    "color": {"field": dim_field,           "type": "nominal"},
                },
            }

        return {"type": "table", "data": {"values": result["rows"]}}   # safe fallback
```

---

### Static Image Rendering (vega2img)

vega2img is a **standalone MCP render service**, not part of the Analytics Platform. Consumers that need static image output register it as a peer MCP server alongside the Analytics Platform.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Integration** | Standalone MCP server registered directly with consumers | Keeps rendering outside the Analytics Platform; consumers decide when to call it |
| **Implementation** | Vite + vega-embed + headless Chromium (Playwright) | Pixel-accurate SVG/PNG from Vega-Lite specs |
| **Table rendering** | Custom HTML template + Playwright screenshot | Styled table rendering |

| Consumer | Chart | Table | Static image |
|---------|-------|-------|------|
| AI Chat Platform | vega-embed | Native data table | vega2img (direct MCP call) |
| Custom UI | vega-embed (recommended) | Host's own grid | vega2img |
| Agentic consumers | vega2img | vega2img | vega2img |

```python
import json
import base64
from playwright.async_api import async_playwright
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Literal

mcp = FastMCP(
    name="vega2img",
    instructions="Render Vega-Lite display specs and tables to static PNG or SVG images.",
)

class RenderChartInput(BaseModel):
    display_spec: dict                      # Vega-Lite v5 DVL spec from Analytics Platform
    format:       Literal["png", "svg"] = "png"
    width:        int = 800
    height:       int = 400

class RenderTableInput(BaseModel):
    display_spec: dict                      # type: "table" DVL spec from Analytics Platform
    format:       Literal["png", "svg"] = "png"
    width:        int = 900

@mcp.tool()
async def render_chart(input: RenderChartInput) -> dict:
    """Render a Vega-Lite display spec from the Analytics Platform to a static image.
    Returns a base64-encoded image and MIME type."""
    html        = _vega_embed_html(input.display_spec, input.width, input.height)
    image_bytes = await _screenshot(html, input.format, input.width, input.height)
    return {
        "image":     base64.b64encode(image_bytes).decode(),
        "mime_type": "image/png" if input.format == "png" else "image/svg+xml",
    }

@mcp.tool()
async def render_table(input: RenderTableInput) -> dict:
    """Render a table display spec from the Analytics Platform to a static image.
    Returns a base64-encoded image and MIME type."""
    html        = _table_html(input.display_spec, input.width)
    image_bytes = await _screenshot(html, input.format, input.width, height=600)
    return {
        "image":     base64.b64encode(image_bytes).decode(),
        "mime_type": "image/png" if input.format == "png" else "image/svg+xml",
    }

def _vega_embed_html(spec: dict, width: int, height: int) -> str:
    return f"""<!DOCTYPE html><html><body style="margin:0">
<div id="vis"></div>
<script src="/vega/vega.min.js"></script>
<script src="/vega/vega-lite.min.js"></script>
<script src="/vega/vega-embed.min.js"></script>
<script>
  vegaEmbed('#vis', {json.dumps(spec)}, {{width: {width}, height: {height}, actions: false}});
</script></body></html>"""

def _table_html(spec: dict, width: int) -> str:
    # Build styled HTML table from spec["columns"] and spec["data"]["values"]
    ...

async def _screenshot(html: str, fmt: str, width: int, height: int) -> bytes:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page    = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html)
        await page.wait_for_selector("#vis canvas")   # wait for Vega render to complete
        image   = await page.locator("#vis").screenshot(type=fmt)
        await browser.close()
        return image

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
```

---

### Analytical Lineage Store

> **Specification:** [§Analytical Lineage Store (ALS)](./02-core-capabilities.md#analytical-lineage-store)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Lineage records** | S3-compatible object store — one JSON document per query | Write-once; append-only; cheap at scale; no schema migration required; natural fit for immutable audit records |
| **Object key** | `lineage/{org_id}/{yyyy}/{mm}/{dd}/{result_id}.json` | Date-partitioned; enables prefix-based listing by time window |
| **Search index** | Thin PostgreSQL table (scalar fields only, no JSON blobs) | Used by the Lineage Query REST API (see roadmap) for filtered search; full record always fetched from the object store |
| **Retention** | Object lifecycle policy — default 7 years (configurable per compliance mode) | MiFID II and equivalent regimes; enforced at the storage layer, not application code |

#### Lineage document schema

Each completed query writes a single JSON document to the object store at `lineage/{org_id}/{yyyy}/{mm}/{dd}/{result_id}.json`:

```json
{
  "result_id":          "res_20260514_093247_a1b2c3",
  "org_id":          "acme-wealth",
  "user_sub":           "auth0|user_xyz",
  "lqp_id":             "lqp-20260514-093241-xyz",
  "cache_hit":          false,
  "request_payload":    { "tool": "run_analytics", "input": { "operation_id": "compare_portfolios", "params": {"..."} } },
  "resolved_metrics":   [{ "metric_id": "portfolio_return", "version": "2.1.0" }],
  "governance_decision":{ "approved": true, "performance_impact_units": 850, "checks_passed": ["performance_impact_ceiling", "metric_count", "dimension_count", "classification_gate", "compliance_check"] },
  "sub_plans":          [{ "backend": "primary-warehouse", "query": "...", "latency_ms": 980 }],
  "result_summary":     { "row_count": 2, "schema": ["..."], "rows": ["..."] },
  "display_spec":       { "type": "chart", "contract": "BAR_MULTI_SERIES_COMPARISON", "..." },
  "error_code":         null,
  "regulatory_frameworks": ["mifid2"],
  "compliance_meta":    { "justification": "Quarterly review", "trace_id": "mifid2-trace-abc" },
  "created_at":         "2026-05-14T09:32:47Z",
  "expires_at":         "2033-05-14T09:32:47Z"
}
```

Records are written once and never mutated. Post-hoc compliance annotations are written as separate sibling documents (`{result_id}_amendment_{n}.json`) referencing the original `result_id`.

#### Search index schema

A lightweight PostgreSQL table (`analytics.lineage_index`) holds only the scalar fields required for the Lineage Query REST API (see roadmap). Full records are always retrieved from the S3 object store; this table is never the source of truth for record content. Each row corresponds to the following JSON shape:

```json
{
  "result_id":                "res_20260514_093247_a1b2c3",
  "org_id":                   "acme-wealth",
  "user_sub":                 "auth0|user_xyz",
  "regulatory_frameworks":    "mifid2,basel3",
  "performance_impact_units": 850,
  "error_code":               null,
  "cache_hit":                false,
  "created_at":               "2026-05-14T09:32:47Z",
  "expires_at":               "2033-05-14T09:32:47Z"
}
```

Field reference:

| Field | Type | Notes |
|-------|------|-------|
| `result_id` | string | Primary key; matches S3 object path |
| `org_id` | string | Tenant scope |
| `user_sub` | string | JWT `sub` claim of the requesting user |
| `regulatory_frameworks` | string \| null | Comma-separated framework tags from triggered metrics; null for non-compliance queries |
| `performance_impact_units` | integer \| null | Recorded for hourly budget tracking |
| `error_code` | string \| null | Null for successful queries |
| `cache_hit` | boolean | True if result was served from Redis cache |
| `created_at` | ISO 8601 | Query execution timestamp |
| `expires_at` | ISO 8601 | Computed from retention policy; enforced at S3 lifecycle layer |

Indexed on `(org_id, user_sub, created_at DESC)`, `(org_id, created_at DESC)`, and `(org_id, regulatory_frameworks)` for the compliance-filtered query pattern.

```python
import json

class AnalyticalLineageStore:
    def __init__(self, s3_client, pg_pool):
        self.s3 = s3_client
        self.pg = pg_pool

    async def write(self, record: dict) -> str:
        key = self._object_key(record["org_id"], record["result_id"], record["created_at"])
        await self.s3.put_object(Key=key, Body=json.dumps(record).encode())
        await self._index(record)
        return record["result_id"]

    async def fetch(self, result_id: str, org_id: str) -> dict:
        row = await self.pg.fetchrow(
            "SELECT * FROM analytics.lineage_index WHERE result_id=$1 AND org_id=$2",
            result_id, org_id,
        )
        key = self._object_key(row["org_id"], result_id, row["created_at"].isoformat())
        obj = await self.s3.get_object(Key=key)
        return json.loads(obj["Body"].read())

    async def write_controls_decision(self, lqp: dict, claims: dict) -> None:
        record = {
            "record_type":   "controls_decision",
            "result_id":     lqp["lqp_id"],        # keyed by lqp_id before result_id exists
            "org_id":        lqp["org_id"],
            "user_sub":      claims["sub"],
            "approved":      lqp["controls_approved"],
            "checks_passed": ["performance_impact_ceiling", "metric_count", "dimension_count",
                              "classification_gate", "compliance_check"],
            "estimated_performance_impact": lqp["estimated_performance_impact"],
            "compliance_tier":              lqp.get("compliance_tier"),
            "created_at":    utc_now(),
        }
        key = f"lineage/{lqp['org_id']}/controls/{lqp['lqp_id']}.json"
        await self.s3.put_object(Key=key, Body=json.dumps(record).encode())

    async def write_execution(self, lqp: dict, result: dict) -> None:
        record = {
            "record_type":       "execution",
            "result_id":         result["result_id"],
            "lqp_id":            lqp["lqp_id"],
            "org_id":            lqp["org_id"],
            "user_sub":          lqp.get("user_sub"),
            "cache_hit":         result.get("cache_hit", False),
            "performance_impact_units": lqp.get("estimated_performance_impact"),
            "regulatory_frameworks":    list({fw for m in lqp.get("resolved_metrics", [])
                                             if m.get("compliance_relevant")
                                             for fw in m.get("regulatory_framework", [])}),
            "sub_plans":         result.get("sub_plans", []),
            "result_summary":    {"row_count": len(result.get("rows", [])), "schema": result.get("schema")},
            "error_code":        result.get("error_code"),
            "created_at":        utc_now(),
            "expires_at":        compute_expiry(lqp),
        }
        await self.write(record)

    def _object_key(self, org_id: str, result_id: str, created_at: str) -> str:
        date = created_at[:10].replace("-", "/")
        return f"lineage/{org_id}/{date}/{result_id}.json"

    async def _index(self, record: dict) -> None:
        await self.pg.execute(
            """INSERT INTO analytics.lineage_index
               (result_id, org_id, user_sub, regulatory_frameworks, performance_impact_units,
                error_code, cache_hit, created_at, expires_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
            record["result_id"], record["org_id"], record["user_sub"],
            ",".join(record.get("regulatory_frameworks", [])) or None,
            record.get("performance_impact_units"),
            record.get("error_code"),
            record["cache_hit"], record["created_at"], record["expires_at"],
        )
```

---

### Knowledge Store

> **Used by:** MCP Resource handlers

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Storage** | S3-compatible object store (versioned Markdown or MDX files) | Human-readable; diffable; straightforward Admin API management |
| **Access** | Read-only at runtime via MCP resource handlers | No user data; no controls pipeline required |
| **Management** | Admin API — create, update, version knowledge artifacts | Administrators can extend or override default content |
| **Defaults** | Bundled at installation alongside the Financial Services Reference Model | Covers platform overview, all six analytical domains, core skills definitions, MiFID II and Basel III/IV compliance guides |

Each knowledge artifact is a versioned Markdown document identified by a URI path that maps directly to its MCP resource address (`guide://analytics/platform-overview` → `guide/analytics/platform-overview.md`). The active version for each artifact is controlled via the Admin API; previous versions are retained for audit purposes. Administrators may add custom skills definitions and workflow guides without modifying the platform defaults.

```python
class KnowledgeStore:
    def __init__(self, s3_client, bucket: str):
        self.s3     = s3_client
        self.bucket = bucket

    def get(self, artifact_path: str) -> str:
        key = f"knowledge/{artifact_path}.md"
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read().decode("utf-8")

    async def put(self, artifact_path: str, content: str, author: str) -> str:
        # Called via Admin API; previous version retained with version suffix in S3
        version = generate_version_id()
        key     = f"knowledge/{artifact_path}.md"
        await self.s3.put_object(
            Bucket=self.bucket, Key=key,
            Body=content.encode("utf-8"),
            Metadata={"author": author, "version": version},
        )
        return version
```

---

### Result Cache

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Store** | Redis (cluster mode) | Sub-millisecond read; TTL-native; cluster mode for HA |
| **Cache key** | SHA-256 of `(org_id + operation_id + canonical_params + role_hash)` | Role hash ensures two users with different entitlements never share a cached result |
| **TTL** | 5 minutes default; configurable per operation via `cache_ttl_seconds` on `analytical_operation` | Short TTL balances freshness against backend load |
| **Compliance bypass** | Queries with `compliance_tier.active: true` skip read and write | Provenance Artifact requires a fresh execution record |
| **Cache-aside pattern** | FQE checks before execution; writes after assembly | Cache is never on the critical governance path |

```python
import hashlib, json

class ResultCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, lqp: dict, claims: dict) -> str:
        role_hash   = hashlib.sha256(str(sorted(claims.get("analytics_roles", []))).encode()).hexdigest()[:8]
        payload     = json.dumps({"org": lqp["org_id"], "nodes": lqp["nodes"]}, sort_keys=True)
        return "arc:" + hashlib.sha256((payload + role_hash).encode()).hexdigest()

    async def get(self, lqp: dict, claims: dict) -> dict | None:
        if lqp.get("compliance_tier", {}).get("active"):
            return None                          # compliance queries always bypass cache
        data = await self.redis.get(self._key(lqp, claims))
        return json.loads(data) if data else None

    async def set(self, lqp: dict, claims: dict, result: dict, ttl: int = 300) -> None:
        if lqp.get("compliance_tier", {}).get("active"):
            return                               # never cache compliance query results
        await self.redis.setex(self._key(lqp, claims), ttl, json.dumps(result))
```

The FQE uses a cache-aside pattern: check before execution, write after assembly.

```python
async def execute(self, lqp: dict, claims: dict) -> dict:
    cached = await self.cache.get(lqp, claims)
    if cached:
        cached["cache_hit"] = True
        return cached

    sub_plans = self._split_by_affinity(lqp)
    results   = await asyncio.gather(*[self._execute_sub_plan(sp) for sp in sub_plans])
    assembled = self._assemble(results, lqp)
    await self.cache.set(lqp, claims, assembled, ttl=lqp.get("cache_ttl_seconds", 300))
    await self.lineage.write_execution(lqp, assembled)
    return assembled
```

---

### Admin API

The Admin API is a REST service authenticated with a platform service token (Bearer). It is the only write path for DCS documents (metric definitions, controls config, knowledge artifacts) outside of the normal SDR authoring workflow.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/admin/smr/seed` | Import a Financial Services Reference Model bundle. Body: JSON array of `analytical_metric`, `analytical_dimension`, or `analytical_operation` documents. Idempotent — existing approved documents are skipped. |
| `GET` | `/v1/admin/smr/metrics` | List all metrics for an org with status filter. Query: `?org_id=&status=proposed\|in_review\|approved\|deprecated` |
| `POST` | `/v1/admin/smr/metrics/{metric_id}/approve` | Transition a metric from `in_review` to `approved`. Body: `{ "approved_by": "user@example.com" }` |
| `PUT` | `/v1/admin/controls/config` | Replace the controls config document for an org. Body: `controls_config` JSON document. |
| `GET` | `/v1/admin/controls/config` | Fetch the current controls config for an org. |
| `POST` | `/v1/admin/knowledge/{artifact_path}` | Create or update a knowledge artifact. Body: Markdown text. Path maps to MCP resource URI. |
| `GET` | `/v1/admin/knowledge/{artifact_path}` | Fetch the current active version of a knowledge artifact. |
| `GET` | `/v1/admin/lineage/{result_id}` | Fetch a full lineage record from the object store by result ID. |
| `GET` | `/v1/admin/health` | Platform health check — returns status of all registered backends and DCS connectivity. |

```python
# Pseudo code — Admin API request handler shape
async def handle_seed_bundle(request: Request) -> Response:
    token   = verify_platform_token(request.headers["Authorization"])
    bundle  = await request.json()       # list of DCS documents

    results = {"seeded": [], "skipped": [], "errors": []}
    for doc in bundle:
        existing = await dcs.get(doc["type"], doc.get("metric_id") or doc.get("operation_id") or doc.get("dimension_id"), doc["org_id"])
        if existing and existing["status"] == "approved":
            results["skipped"].append(doc["metric_id"])
            continue
        try:
            await dcs.put(doc)
            results["seeded"].append(doc["metric_id"])
        except Exception as e:
            results["errors"].append({"id": doc.get("metric_id"), "error": str(e)})

    return JSONResponse(results, status_code=207)
```

---

### Service Startup and Dependency Wiring

```python
# app.py — dependency construction and service startup
import asyncio, asyncpg, boto3, redis.asyncio as aioredis
from anthropic import AsyncAnthropic
from fastmcp import FastMCP

async def build_app() -> FastMCP:
    cfg = load_config()                         # reads from env vars + config file

    # Infrastructure clients
    pg_pool     = await asyncpg.create_pool(cfg["postgres_dsn"])
    s3_client   = boto3.client("s3", **cfg["s3"])
    redis_client = await aioredis.from_url(cfg["redis_url"])
    dcs_client  = DCSClient(base_url=cfg["dcs_url"], api_key=cfg["dcs_api_key"])
    llm_client  = AsyncAnthropic(api_key=cfg["anthropic_api_key"])

    # Platform services
    als    = AnalyticalLineageStore(s3_client, pg_pool, bucket=cfg["lineage_bucket"])
    cache  = ResultCache(redis_client)
    smr    = SemanticMetricsRepository(dcs_client)
    rapl   = RoleAwareProjectionLayer(pg_pool)
    scl    = SemanticControlsLayer(dcs_client, pg_pool, redis_client)
    dvl    = DataVisualizationLanguage()
    nse    = NarrativeSynthesisEngine(llm_client)

    # FQE — register backend adapters by data_affinity name
    backend_registry = {
        "portfolio":    SnowflakeAdapter(cfg["backends"]["primary_warehouse"]),
        "risk_metrics": CubeJSAdapter(cfg["backends"]["risk_semantic_layer"]),
        "regulatory":   SnowflakeAdapter(cfg["backends"]["regulatory_data_store"]),
    }
    fqe = FederatedQueryPlanner(backend_registry, als, cache)

    pipeline = PipelineExecutor(
        sil=SemanticIntentLayer(smr),
        rapl=rapl, scl=scl, fqe=fqe, dvl=dvl, nse=nse, als=als,
    )

    # Wire into MCP app
    app = build_mcp_app(pipeline, smr, als, cfg)
    return app

if __name__ == "__main__":
    app = asyncio.run(build_app())
    app.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

Configuration is read from environment variables at startup. Required variables:

| Variable | Description |
|----------|-------------|
| `POSTGRES_DSN` | PostgreSQL connection string (lineage index + role policies) |
| `REDIS_URL` | Redis connection URL (cache + concurrency semaphore) |
| `DCS_URL` | Data Context Store base URL |
| `DCS_API_KEY` | DCS service-to-service API key |
| `S3_LINEAGE_BUCKET` | S3 bucket name for lineage records |
| `ANTHROPIC_API_KEY` | Anthropic API key for NSE |
| `JWT_JWKS_URI` | JWKS endpoint for JWT public key retrieval |
| `JWT_AUDIENCE` | Expected JWT audience claim |
| `JWT_ISSUER` | Expected JWT issuer claim |

---

## 4.3 Infrastructure

| Component | Choice | Rationale |
|-----------|--------|-----------|
| MCP service | Python · FastMCP + Uvicorn | Lightweight ASGI MCP surface; deploys as Kubernetes pod |
| Backend services | Kubernetes (cloud-agnostic) | FQE, governance, platform services as independently scalable pods |
| Primary database | PostgreSQL (Neon or RDS) | Lineage search index, role policy config, scheduled queries, user preferences, saved queries |
| Data Context Store (DCS) | Pre-existing platform component | SMR metric definitions, controls config, SMR search — reuses SDR versioned storage and native search |
| Knowledge Store | S3-compatible object store (versioned Markdown) | MCP resource content — guides, skills definitions, compliance reference |
| Object storage | S3-compatible | Lineage records (one JSON document per query), result artefacts, large cached result sets |
| Message queue | SQS / Pub/Sub | Async lineage writes, SDR change events |
| Secrets | HashiCorp Vault or cloud-native | Backend credentials, platform service keys |

### Kubernetes Deployment Summary

| Service | Container | Port | Min replicas | CPU request | Memory request | HPA trigger |
|---------|-----------|------|-------------|-------------|----------------|-------------|
| Analytics MCP | `analytics-mcp` | 8000 | 2 | 500m | 512Mi | CPU > 60% |
| vega2img (optional) | `vega2img` | 8001 | 1 | 1000m | 1Gi | CPU > 70% |
| Admin API | `analytics-admin` | 9000 | 1 | 250m | 256Mi | — |
| PostgreSQL | Managed (Neon / RDS) | 5432 | — | — | — | — |
| Redis | Managed (ElastiCache / Upstash) | 6379 | — | — | — | — |
| Object storage | S3-compatible | — | — | — | — | — |

Health check endpoint: `GET /health` on each container port. Returns `200 OK` with `{"status": "ok", "backends": {...}}` when all registered backends and DCS connectivity are confirmed.

All platform services run in a dedicated Kubernetes namespace (`analytics`). Backend credentials and API keys are injected via Kubernetes Secrets mounted as environment variables — never baked into container images.

### Financial Services Reference Model

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Packaging** | Versioned JSON document bundles (one per domain) | Conforms directly to the SDR `analytical_metric` schema; idempotently importable via `POST /v1/smr/seed`; selective per-domain activation |
| **Distribution** | Bundled at installation; updatable from Semantic Registry Service | Air-gapped deployments supported |
| **Activation** | `analyticalDomain` config triggers SMR import at initial platform setup | Bundle documents are written to the SDR in `proposed` state; Analytics Governance approves before metrics become resolvable |
| **Customisation** | Full edit/override via Admin API after import | Customised definitions marked `source: "custom"` in the SDR document |

Each bundle is a JSON array of SDR documents conforming to the schemas defined in [§Semantic Metrics Repository](./02-core-capabilities.md#semantic-metrics-registry). Bundles are seeded into the SDR in `"proposed"` state at initial platform setup; the Analytics Governance approves each document before it becomes resolvable by the Semantic Intent Layer.

> **Version format note:** Seed bundle documents use an integer `version` field (starting at `1`) as the bootstrap state. On first platform activation the platform converts these to semantic versioning (`"1.0.0"`). Subsequent versions follow semver — the `"2.1.0"` form used in Chapter 2 examples reflects a metric that has been through two major revisions post-activation.

#### Dimensions bundle (shared across all domains)

One bundle covers all analytical dimensions. Every domain bundle's metrics and operations reference these dimension IDs.

```json
[
  {
    "type":             "analytical_dimension",
    "org_id":        "acme-wealth",
    "dimension_id":     "asset_class",
    "version":          1,
    "status":           "approved",
    "source":           "platform",
    "display_name":     "Asset Class",
    "description":      "Top-level asset class classification applied to holdings.",
    "data_affinity":    "portfolio",
    "physical_mapping": { "source": "primary-warehouse", "table": "dim_asset_classification", "column": "asset_class" },
    "values":           ["EQUITY", "FIXED_INCOME", "ALTERNATIVES", "CASH", "DERIVATIVES"],
    "hierarchical":     false,
    "parent_dimension": null
  },
  {
    "type":             "analytical_dimension",
    "org_id":        "acme-wealth",
    "dimension_id":     "geography",
    "version":          1,
    "status":           "approved",
    "source":           "platform",
    "display_name":     "Geography",
    "description":      "Country of domicile of the issuer. Rolls up to region and continent.",
    "data_affinity":    "portfolio",
    "physical_mapping": { "source": "primary-warehouse", "table": "dim_geography", "column": "country_iso2" },
    "values":           null,
    "hierarchical":     true,
    "parent_dimension": null,
    "hierarchy_levels": ["continent", "region", "country"]
  },
  {
    "type":             "analytical_dimension",
    "org_id":        "acme-wealth",
    "dimension_id":     "sector",
    "version":          1,
    "status":           "approved",
    "source":           "platform",
    "display_name":     "Sector (GICS)",
    "description":      "GICS Level 1 sector classification.",
    "data_affinity":    "portfolio",
    "physical_mapping": { "source": "primary-warehouse", "table": "dim_sector", "column": "gics_sector" },
    "values":           ["ENERGY", "MATERIALS", "INDUSTRIALS", "CONSUMER_DISCRETIONARY", "CONSUMER_STAPLES",
                         "HEALTH_CARE", "FINANCIALS", "INFORMATION_TECHNOLOGY", "COMMUNICATION_SERVICES",
                         "UTILITIES", "REAL_ESTATE"],
    "hierarchical":     true,
    "parent_dimension": null,
    "hierarchy_levels": ["sector", "industry_group", "industry", "sub_industry"]
  },
  {
    "type":             "analytical_dimension",
    "org_id":        "acme-wealth",
    "dimension_id":     "currency",
    "version":          1,
    "status":           "approved",
    "source":           "platform",
    "display_name":     "Currency",
    "description":      "Denomination currency of the holding (ISO 4217).",
    "data_affinity":    "portfolio",
    "physical_mapping": { "source": "primary-warehouse", "table": "fact_portfolio_daily", "column": "currency_code" },
    "values":           null,
    "hierarchical":     false,
    "parent_dimension": null
  },
  {
    "type":             "analytical_dimension",
    "org_id":        "acme-wealth",
    "dimension_id":     "issuer",
    "version":          1,
    "status":           "approved",
    "source":           "platform",
    "display_name":     "Issuer",
    "description":      "Legal entity name of the security issuer. High cardinality — use with limit.",
    "data_affinity":    "portfolio",
    "physical_mapping": { "source": "primary-warehouse", "table": "dim_issuer", "column": "issuer_name" },
    "values":           null,
    "hierarchical":     false,
    "parent_dimension": null
  }
]
```

#### Performance domain bundle (`domain: "performance"`)

```json
[
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "market_value",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Market Value",
    "description":          "End-of-period market value of a portfolio or position in the portfolio base currency.",
    "domain":               "performance",
    "category":             "valuation",
    "unit":                 "currency",
    "decimals":             2,
    "aggregation":          "sum",
    "cost_weight":          1,
    "classification_level": "internal",
    "data_affinity":        "portfolio",
    "physical_mapping":     { "source": "primary-warehouse", "table": "fact_portfolio_daily", "measure": "market_value_base_ccy" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "currency", "sector"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "portfolio_return",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Portfolio Return",
    "description":          "Total return of a portfolio over the specified period, net of fees.",
    "domain":               "performance",
    "category":             "total_return",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          1,
    "classification_level": "internal",
    "data_affinity":        "portfolio",
    "physical_mapping":     { "source": "primary-warehouse", "table": "fact_portfolio_daily", "measure": "total_return_net" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "time_period"],
    "optional_dimensions":  ["benchmark_id", "asset_class"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "sharpe_ratio",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Sharpe Ratio",
    "description":          "Annualised excess return divided by annualised standard deviation.",
    "domain":               "performance",
    "category":             "risk_adjusted_return",
    "unit":                 "ratio",
    "decimals":             2,
    "aggregation":          "last",
    "cost_weight":          2,
    "classification_level": "internal",
    "data_affinity":        "portfolio",
    "physical_mapping":     { "source": "primary-warehouse", "table": "fact_portfolio_analytics", "measure": "sharpe_ratio_annualised" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "time_period"],
    "optional_dimensions":  [],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "volatility",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Volatility",
    "description":          "Annualised standard deviation of portfolio returns.",
    "domain":               "performance",
    "category":             "risk_adjusted_return",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          2,
    "classification_level": "internal",
    "data_affinity":        "portfolio",
    "physical_mapping":     { "source": "primary-warehouse", "table": "fact_portfolio_analytics", "measure": "volatility_annualised" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "time_period"],
    "optional_dimensions":  ["asset_class"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":              "analytical_operation",
    "org_id":         "acme-wealth",
    "operation_id":      "portfolio_return",
    "version":           1,
    "status":            "approved",
    "source":            "platform",
    "display_name":      "Portfolio Return",
    "description":       "Total return for a portfolio over a specified period.",
    "execution_profile": "metric_query",
    "required_params":   ["portfolio_id", "time_period"],
    "supported_metrics": ["portfolio_return"]
  },
  {
    "type":                  "analytical_operation",
    "org_id":             "acme-wealth",
    "operation_id":          "compare_portfolios",
    "version":               1,
    "status":                "approved",
    "source":                "platform",
    "display_name":          "Portfolio Comparison",
    "description":           "Compare one or more metrics across two or more portfolios, optionally against a benchmark.",
    "execution_profile":     "full_analytical",
    "required_params":       ["portfolio_ids", "metrics", "time_period"],
    "optional_params":       ["benchmark_id"],
    "supported_metrics":     ["portfolio_return", "tracking_error", "sharpe_ratio", "volatility", "beta"],
    "default_visualization": "bar_multi_series_comparison"
  },
  {
    "type":                  "analytical_operation",
    "org_id":             "acme-wealth",
    "operation_id":          "performance_attribution",
    "version":               1,
    "status":                "approved",
    "source":                "platform",
    "display_name":          "Performance Attribution",
    "description":           "BHB or Brinson-Fachler attribution decomposition for a portfolio versus its benchmark.",
    "execution_profile":     "full_analytical",
    "required_params":       ["portfolio_id", "benchmark_id", "attribution_by", "time_period"],
    "supported_dimensions":  ["asset_class", "sector", "geography", "currency"],
    "default_visualization": "attribution_waterfall"
  }
]
```

#### Risk domain bundle (`domain: "risk"`)

```json
[
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "var_95",
    "version":              2,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Value at Risk (95%)",
    "description":          "Maximum expected portfolio loss over a 1-day horizon at 95% confidence.",
    "domain":               "risk",
    "category":             "market_risk",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          3,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "var_95_daily" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "geography", "sector", "currency"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "var_99",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Value at Risk (99%)",
    "description":          "Maximum expected portfolio loss over a 1-day horizon at 99% confidence.",
    "domain":               "risk",
    "category":             "market_risk",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          4,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "var_99_daily" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "geography", "sector", "currency"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "tracking_error",
    "version":              2,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Tracking Error",
    "description":          "Annualised standard deviation of the difference between portfolio and benchmark returns.",
    "domain":               "risk",
    "category":             "relative_risk",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          2,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "tracking_error_annualised" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "benchmark_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "sector"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "expected_shortfall",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Expected Shortfall (CVaR 95%)",
    "description":          "Average loss in the worst 5% of outcomes over a 1-day horizon.",
    "domain":               "risk",
    "category":             "tail_risk",
    "unit":                 "percentage",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          4,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "cvar_95_daily" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "geography"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "beta",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Beta",
    "description":          "Market beta — sensitivity of portfolio returns to benchmark returns.",
    "domain":               "risk",
    "category":             "market_risk",
    "unit":                 "ratio",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          2,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "portfolio_beta" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "benchmark_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "sector"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "duration",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Modified Duration",
    "description":          "Modified duration of the portfolio — sensitivity of price to yield changes.",
    "domain":               "risk",
    "category":             "interest_rate_risk",
    "unit":                 "years",
    "decimals":             2,
    "aggregation":          "value_weighted_average",
    "weight_metric_id":     "market_value",
    "cost_weight":          2,
    "classification_level": "internal",
    "data_affinity":        "risk_metrics",
    "physical_mapping":     { "source": "risk-semantic-layer", "cube": "risk_cube", "measure": "modified_duration" },
    "compliance_relevant":  false,
    "regulatory_framework": [],
    "required_dimensions":  ["portfolio_id", "as_of_date"],
    "optional_dimensions":  ["asset_class", "currency"],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":              "analytical_operation",
    "org_id":         "acme-wealth",
    "operation_id":      "get_positions",
    "version":           1,
    "status":            "approved",
    "source":            "platform",
    "display_name":      "Portfolio Positions",
    "description":       "Fetch current or historical position data for a portfolio.",
    "execution_profile": "data_retrieval",
    "required_params":   ["portfolio_id"],
    "optional_params":   ["as_of_date", "asset_class"]
  },
  {
    "type":                  "analytical_operation",
    "org_id":             "acme-wealth",
    "operation_id":          "risk_breakdown",
    "version":               1,
    "status":                "approved",
    "source":                "platform",
    "display_name":          "Risk Breakdown",
    "description":           "Decompose a risk metric into factor contributions by the specified dimension.",
    "execution_profile":     "full_analytical",
    "required_params":       ["portfolio_id", "metrics", "attribution_by", "as_of_date"],
    "supported_metrics":     ["var_95", "var_99", "tracking_error", "beta", "duration", "expected_shortfall"],
    "supported_dimensions":  ["asset_class", "geography", "sector", "currency", "issuer"],
    "default_visualization": "attribution_waterfall"
  }
]
```

#### Regulatory domain bundle (`domain: "regulatory"`)

All regulatory metrics carry `"classification_level": "restricted"`, `"compliance_relevant": true`, and `"regulatory_framework": ["basel3"]`. The SCL classification gate is triggered for every query against these metrics.

```json
[
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "lcr",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Liquidity Coverage Ratio",
    "description":          "High-quality liquid assets as a percentage of net cash outflows over a 30-day stress period. Basel III minimum: 100%.",
    "domain":               "regulatory",
    "category":             "liquidity",
    "unit":                 "percentage",
    "decimals":             1,
    "aggregation":          "last",
    "cost_weight":          5,
    "classification_level": "restricted",
    "data_affinity":        "regulatory",
    "physical_mapping":     { "source": "regulatory-data-store", "table": "fact_regulatory_ratios", "measure": "lcr_ratio" },
    "compliance_relevant":  true,
    "regulatory_framework": ["basel3"],
    "required_dimensions":  ["entity_id", "reporting_date", "jurisdiction"],
    "optional_dimensions":  [],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "leverage_ratio",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Leverage Ratio",
    "description":          "Tier 1 capital as a percentage of total exposure. Basel III minimum: 3%.",
    "domain":               "regulatory",
    "category":             "capital_adequacy",
    "unit":                 "percentage",
    "decimals":             1,
    "aggregation":          "last",
    "cost_weight":          5,
    "classification_level": "restricted",
    "data_affinity":        "regulatory",
    "physical_mapping":     { "source": "regulatory-data-store", "table": "fact_regulatory_ratios", "measure": "leverage_ratio" },
    "compliance_relevant":  true,
    "regulatory_framework": ["basel3"],
    "required_dimensions":  ["entity_id", "reporting_date", "jurisdiction"],
    "optional_dimensions":  [],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                 "analytical_metric",
    "org_id":            "acme-wealth",
    "metric_id":            "nsfr",
    "version":              1,
    "status":               "approved",
    "source":               "platform",
    "display_name":         "Net Stable Funding Ratio",
    "description":          "Available stable funding as a percentage of required stable funding. Basel III minimum: 100%.",
    "domain":               "regulatory",
    "category":             "liquidity",
    "unit":                 "percentage",
    "decimals":             1,
    "aggregation":          "last",
    "cost_weight":          5,
    "classification_level": "restricted",
    "data_affinity":        "regulatory",
    "physical_mapping":     { "source": "regulatory-data-store", "table": "fact_regulatory_ratios", "measure": "nsfr_ratio" },
    "compliance_relevant":  true,
    "regulatory_framework": ["basel3"],
    "required_dimensions":  ["entity_id", "reporting_date", "jurisdiction"],
    "optional_dimensions":  [],
    "approved_by":          "cdo@acme.com",
    "approved_at":          "2026-05-14T09:00:00Z",
    "created_at":           "2026-05-13T14:32:00Z"
  },
  {
    "type":                  "analytical_operation",
    "org_id":             "acme-wealth",
    "operation_id":          "regulatory_report",
    "version":               1,
    "status":                "approved",
    "source":                "platform",
    "display_name":          "Regulatory Compliance Report",
    "description":           "Entity-level regulatory compliance metric report under MiFID II or Basel III/IV.",
    "execution_profile":     "full_analytical",
    "required_params":       ["metric_id", "entity_id", "reporting_date", "jurisdiction"],
    "supported_metrics":     ["lcr", "leverage_ratio", "nsfr"],
    "regulatory_framework":  ["mifid2", "basel3"],
    "required_feature_flag": "regulatory_reporting",
    "default_visualization": "table"
  }
]
```
