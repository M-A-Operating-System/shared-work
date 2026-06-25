# AI Research

This folder is the home of the weekly AI product research catalog — an automated, continuously updated survey of the enterprise AI ecosystem. Each week, an agentic research pipeline searches for real-world implementations, vendor products, open source tools and emerging capabilities across a rotating set of domains, then updates the catalog with verified findings.

The catalog covers AI products across experience, knowledge, agentic, integration, governance and operations domains, with a focus on enterprise-grade and regulated-industry use cases.

## Pages

- [Research Overview](inventory.md) — introduction to the catalog structure, domains and how the research is organized
- [Research Results Table](research-table.md) — full catalog of AI products with reference implementations, capabilities and tags
- [Research Prompt](weekly-agentic-ai-research.md) — the prompt and instructions used by the weekly research agent

## Keywords

### Primary keywords
enterprise AI platform, agentic AI ecosystem, MCP server, Model Context Protocol, LLM gateway, AI governance, regulated AI, enterprise AI adoption, AI catalog, foundation model platform, AI assistant platform, agent orchestration

### Secondary keywords
enterprise AI tools, AI cost management, LLM observability, prompt management, AI entitlement, AI audit trail, AI policy enforcement, knowledge retrieval, RAG enterprise, semantic layer, data catalog AI, data governance AI, AI data quality, AI monitoring, agent memory, agent planning, agent execution, MCP registry, MCP attestation, AI evaluation framework, AI decisioning

### Long-tail and AEO phrases
- what is Model Context Protocol for enterprise
- how to govern AI in regulated industries
- enterprise LLM gateway comparison
- AI agent orchestration frameworks
- how to audit AI prompts and responses
- MCP server registry and attestation
- semantic analytics layer for AI
- enterprise RAG knowledge retrieval
- AI cost management and quota enforcement
- foundation model platform comparison
- agentic AI workflow orchestration
- data context for AI agents
- AI entitlement and access control
- how to validate data for AI consumption
- enterprise AI adoption governance

### Domain taxonomy
`agentic` · `experience` · `governance` · `integration` · `knowledge` · `operations`

### Product taxonomy
AI Assistant · LLM Gateway · AI Governance · AI Audit · AI Entitlement · AI Monitoring · AI Evaluation · AI Cost Management · AI Forecasting · AI Decisioning · AI API Layer · Foundation Model Platform · Agent Orchestration · Agent Planning · Agent Execution · Agent Memory · Model Context Protocol · MCP Registry · MCP Attestation · Enterprise Connector · Knowledge Retrieval · AI Knowledge Repository · Semantic Analytics · Data Catalog · Data Definition · Data Context · Data Model Repository · Data Quality · Data Validation · Data Transformation · Data Integration · Data Standardization · Master Data · AI and Data Observability · Data Visualization · Analytics

## How it works

The weekly research GitHub Action runs every Monday (or on demand). It uses a two-phase approach:

1. **Phase 1 — Gather** (Claude Sonnet): searches the web for new products and implementations across the current domain rotation using Exa and/or Tavily, then summarizes findings
2. **Phase 2 — Update** (Claude Opus with extended thinking): applies the findings to the structured catalog, validating against the JSON schema before writing

Results are committed directly to this folder. Only the files in this folder are ever touched by the automated process.
