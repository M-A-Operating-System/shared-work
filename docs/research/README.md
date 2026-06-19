# AI Research

This folder is the home of the weekly AI product research catalog — an automated, continuously updated survey of the enterprise AI ecosystem. Each week, an agentic research pipeline searches for real-world implementations, vendor products, open source tools and emerging capabilities across a rotating set of domains, then updates the catalog with verified findings.

The catalog covers AI products across experience, knowledge, agentic, integration, governance and operations domains, with a focus on enterprise-grade and regulated-industry use cases.

## Pages

- [Research Overview](inventory.md) — introduction to the catalog structure, domains and how the research is organised
- [Research Results Table](research-table.md) — full catalog of AI products with reference implementations, capabilities and tags
- [Research Prompt](weekly-agentic-ai-research.md) — the prompt and instructions used by the weekly research agent

## How it works

The weekly research GitHub Action runs every Monday (or on demand). It uses a two-phase approach:

1. **Phase 1 — Gather** (Claude Sonnet): searches the web for new products and implementations across the current domain rotation using Exa and/or Tavily, then summarises findings
2. **Phase 2 — Update** (Claude Opus with extended thinking): applies the findings to the structured catalog, validating against the JSON schema before writing

Results are committed directly to this folder. Only the files in this folder are ever touched by the automated process.
