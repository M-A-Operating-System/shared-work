# Internet Access MCP Server — Product Overview

**Version:** 1.0
**Date:** June 2026
**Status:** Target State Design

---

## Problem Statement

AI agents and conversational AI interfaces have no controlled, self-hosted mechanism for accessing live internet content during interactions. Without it they operate only on training data, and users must manually retrieve and paste web content into conversations. Autonomous agents have no mechanism to retrieve current information during pipeline execution.

## Solution

A self-hosted MCP server that exposes web search and page fetch as production-grade, infrastructure-controlled capabilities. Built-in entitlements and site classification govern what internet content AI agents and users can access and consume. No external API dependency is required for core operation.

## Primary Consumers

Two distinct runtime consumers:

**End users via AI assistants** — knowledge workers and professionals interacting with an AI interface that calls this server on their behalf. They receive current, grounded responses without leaving the conversation or performing manual retrieval.

**Autonomous AI agents** — software agents executing within agentic pipelines or multi-agent orchestrations that require live internet content as a step in task execution. The agent issues tool calls and receives structured content without human involvement.

## Deployment Model

The server is deployed as shared enterprise infrastructure by a platform or AI infrastructure team. It is not a commercial SaaS product. It runs self-hosted within the enterprise environment and is consumed by any MCP-compatible client — AI assistants, coding agents, orchestration frameworks — operating within that environment.

## Layered Control Model

The server operates within a two-layer control model:

**Layer 1 — Enterprise perimeter controls.** Network, proxy, firewall, and identity policies that govern all outbound internet access for the infrastructure on which the server runs. The server inherits and is subject to these controls automatically by virtue of where it is deployed.

**Layer 2 — Server-managed controls.** Entitlements and site classification operating specifically against AI interactions — governing what content the server will search, fetch, and return to agents and interfaces. These controls are additive to the enterprise perimeter, not a replacement for it.

This layering means the server can be deployed within an organisation that already enforces outbound internet policy, and the server's own controls then address the AI-specific access surface on top of that foundation.

## Success Metric

Volume of webpages successfully fetched per deployment — demonstrating active grounding of AI interactions in live internet content.

## Current State Without This Product

No controlled mechanism exists. Users manually copy and paste web content into conversations. Autonomous agents cannot retrieve live internet content during execution and either fail or produce responses based solely on training data.
