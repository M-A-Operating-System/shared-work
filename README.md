# M&A Operating System — Product Design Specifications

This repository contains the product design specification series for the **M&A Operating System** platform. Documents cover intended design, architecture, and behaviour and are intended for internal distribution across product, engineering, and design review functions.

These are living specifications. They reflect design intent at the time of publication and are updated as the platform evolves.

---

## About M&A Operating System

M&A Operating System is a boutique advisory firm focused on helping organizations modernize the operational foundations required for scalable analytics, trusted enterprise information, and practical AI adoption.

Our work sits at the intersection of enterprise data strategy, information architecture, operating model modernization, and transformation execution. We specialize in helping organizations design practical, business-aligned approaches to enterprise information management that support operational scalability, analytics enablement, governance, and modern AI capabilities.

A core part of our approach is the recognition that successful data and AI initiatives are not driven solely by technology platforms. Long-term success depends on how well organizations structure, model, govern, operationalize, and align information with real business processes and decision-making.

Our approach combines:

- Enterprise data and AI strategy
- Subject-based data modeling and information architecture
- Semantic and operational data design
- Governance and organizational alignment
- Operating model modernization
- Transformation execution and delivery leadership
- Practical AI operationalization and readiness

Our goal is simple: help organizations build practical, scalable, and trusted information foundations that improve operational effectiveness, accelerate analytics and AI adoption, and support better business outcomes.

[maoperatingsystem.com](https://maoperatingsystem.com)

---

## Product Areas

| Product | Description | Specification |
|---|---|---|
| [AI Analytics Platform](docs/product/analytics/README.md) | A deterministic semantic computation engine for AI-native enterprise analytics. Exposes governed, role-aware analytical capabilities to MCP-compatible consumers through a headless API backed by a federated query planner and a governed Semantic Metrics Repository. Eliminates Text-to-SQL as an architectural pattern for regulated analytics. | `docs/product/analytics/` |
| [AI Chat Platform](docs/product/assistant/README.md) | A white-label, embeddable conversational AI layer that any application can adopt. Host applications bring their own domain scope, MCP tooling, and branding. The platform provides the conversation engine, content rendering, audit storage, and memory management. | `docs/product/assistant/` |
| [Knowledge MCP Server](docs/product/knowledge/README.md) | A centralised MCP server exposing a structured knowledge directory as resources, prompts, skills, commands, and agent definitions. Serves as the single source of truth for all reusable AI assets across the platform — eliminating local copies and providing governed access over the Model Context Protocol. | `docs/product/knowledge/` |

---

## Repository Structure

```
docs/
└── product/
    ├── about.md                  # Company background
    ├── analytics/                # AI Analytics Platform specification
    ├── assistant/                # AI Chat Platform specification
    └── knowledge/                # Knowledge MCP Server specification
```

---

*Confidential — internal distribution only*
