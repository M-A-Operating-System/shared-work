# AI Product Inventory Instructions

This folder contains the starting inventory model for AI-enabled products/functions that fit within an Agentic and MCP-enabled ecosystem for regulated data industries such as financial services.

The inventory uses a simple function-first model:

```text
Product / Function
  ├── Reference Implementations
  └── Capabilities
```

In this model, the `product_name` is the canonical functionality name. For example, `gateway`, `retrieval`, `workflow`, `audit`, or `entitlement`.

Reference implementations are the commercial products, open source projects, cloud services, MCP servers, internal tools, or frameworks that provide that function.

Capabilities belong directly to one product/function.

## Files

| File | Purpose |
|---|---|
| `sample-inventory.json` | Example inventory file with sample product/function entries. |
| `inventory.schema.json` | JSON Schema validator for inventory files. |
| `inventory.md` | Instructions for maintaining the inventory. |

## Core Rules

### 1. Use function-first product names

The product is the function.

Use:

```json
"product_name": "gateway"
```

Do not use:

```json
"product_name": "Trustbolt Gateway"
```

Trustbolt is a reference implementation of the `gateway` function.

### 2. Use canonical single-word names

Product names should be lowercase and stable.

Good examples:

```json
"gateway"
"retrieval"
"workflow"
"audit"
"entitlement"
```

Use underscores only when the concept cannot be expressed cleanly as one word.

Good example:

```json
"model_registry"
```

Avoid long product names such as:

```json
"enterprise_ai_model_routing_gateway"
```

### 3. Assign one primary domain

Each product/function must belong to one primary domain.

Allowed domains are:

```json
[
  "experience",
  "agentic",
  "knowledge",
  "integration",
  "governance",
  "operations"
]
```

Use `tags` for secondary associations.

### 4. Capabilities belong to one product/function

In this simple model, assume every capability belongs to only one product/function.

For example, `model_routing` belongs to `gateway`.

Do not also add `model_routing` under `agent`, `workflow`, or `model`.

If a capability appears to belong in multiple places, either:

1. Choose the product/function where it is primarily enforced.
2. Rename the capability so the meaning is specific to that product/function.
3. Consider whether the product/function taxonomy needs refinement.

### 5. Reference implementations are examples

A reference implementation is not the canonical inventory object.

Good:

```json
{
  "product_name": "gateway",
  "reference_implementations": [
    {
      "name": "Trustbolt",
      "implementation_type": "commercial"
    },
    {
      "name": "LiteLLM",
      "implementation_type": "open_source"
    }
  ]
}
```

Avoid creating separate product entries for each vendor unless the vendor represents a separate function.

### 6. Use enterprise architecture descriptions

Descriptions should define the role of the product/function in the ecosystem.

Good:

```text
Centralized control point between users, agents, tools and AI models.
```

Avoid marketing copy:

```text
The best platform for transforming AI productivity across the enterprise.
```

### 7. Mark required capabilities carefully

Use:

```json
"required": true
```

only when the capability is required for safe, controlled, or compliant use in a regulated industry.

Examples of capabilities that are often required:

- Policy enforcement
- Audit logging
- Entitlement control
- Source citation
- Approved model routing
- Cost tracking
- Content inspection

### 8. Add regulated relevance

Use `regulated_relevance` to explain why a capability matters in a regulated industry.

Good:

```json
"regulated_relevance": "Ensures users and agents only access approved models."
```

### 9. Keep implementation types controlled

Allowed implementation types are:

```json
[
  "commercial",
  "open_source",
  "cloud_service",
  "mcp_server",
  "internal",
  "framework"
]
```

### 10. Keep deployment models controlled

Allowed deployment models are:

```json
[
  "saas",
  "private_cloud",
  "on_prem",
  "self_hosted",
  "managed_cloud",
  "embedded",
  "api"
]
```

## Checklist for Adding a New Product/Function

Before adding a new entry, answer these questions:

1. What function does this provide in an Agentic, MCP-enabled, regulated AI ecosystem?
2. Can the function be named with a stable single-word canonical name?
3. Which one primary domain does it belong to?
4. What capabilities does this function provide?
5. Which capabilities are required for regulated-industry use?
6. Which reference implementations currently provide this function?
7. Is this truly a product/function, or is it only a vendor implementation of an existing function?

## Example Entry

```json
{
  "product_name": "audit",
  "display_name": "Audit",
  "domain": "governance",
  "description": "Records AI activity, decisions, prompts, tool calls and responses for review, supervision and compliance.",
  "reference_implementations": [
    {
      "name": "Internal Audit Log Service",
      "vendor": "Internal",
      "implementation_type": "internal",
      "deployment_models": [
        "private_cloud"
      ],
      "notes": "Enterprise audit logging service for AI interactions."
    }
  ],
  "capabilities": [
    {
      "capability_name": "activity_logging",
      "display_name": "Activity Logging",
      "description": "Captures user, agent, model and tool activity.",
      "regulated_relevance": "Supports supervision, investigation and compliance review.",
      "required": true
    }
  ],
  "tags": [
    "governance",
    "compliance",
    "regulated"
  ]
}
```

## Validation

Validate inventory files against:

```text
docs/inventory/inventory.schema.json
```

A valid inventory must include:

- `inventory_version`
- `inventory_name`
- At least one product/function
- At least one capability per product/function
- Valid domain values
- Valid implementation types
- Valid deployment models
