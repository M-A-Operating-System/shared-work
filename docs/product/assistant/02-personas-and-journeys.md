# 02 — Personas and User Journeys

## Personas

| Persona | Role | Primary need | Representative question |
|---------|------|--------------|------------------------|
| **Chief Data Officer** | Executive owner of the data governance function | Instant situational awareness of the data estate without platform navigation | *"Give me a governance health summary across all domains and flag anything that needs my attention."* |
| **Business Head** | Senior leader of a business unit accountable for data produced or consumed by their function | Plain-language answers about their domain's data assets, quality, and governance standing — without needing to understand the DDA platform | *"What data does my Finance team own and are there any quality issues I should know about?"* |
| **Business Staff** | Non-technical operational or analytical staff member who works with data governed by the DDA platform | Ability to find, understand, and act on data assets relevant to their day-to-day work without requiring data literacy | *"Where do I find the approved customer dataset for my report and who do I contact if something looks wrong?"* |
| **Data Practitioner** | Data engineer or analyst actively managing entities and models | Fast lookup and cross-entity navigation without losing context | *"Show me all entities in the Customer domain and flag any without a data owner."* |
| **Governance Officer** | Compliance or data governance lead responsible for policy adherence | Plain-language access to governance status and quality metrics | *"Which data models are missing a classification label and who owns them?"* |
| **New User / Onboarder** | Recently joined team member learning the DDA platform | Contextual explanation of platform concepts and guided navigation | *"What is an entity master and how do I find the entities I own?"* |

### Business persona design note

Business Head and Business Staff users have no expectation of data platform literacy. The chat interface must operate as their self-sufficient access layer — they will not navigate the DDA UI directly. Two consequences:

1. The system prompt suppresses platform-technical terminology (entityMaster, Display ID, MCP) in responses directed at these users. The `communication_style` field on the DDA user profile controls this — `business` and `executive` styles replace platform terms with business equivalents automatically.
2. `@`-binding (see [05-input-and-composition.md](./05-input-and-composition.md)) is their primary mechanism for referencing DDA objects precisely by name, without needing Display IDs or knowledge of internal structure.

---

## Representative User Journeys

### Journey A — CDO: morning governance review (5 minutes, mobile)

The CDO opens Data AI Assistant on mobile during their commute. They start a new conversation and type *"Give me a governance health summary for this week."*

The model invokes the DDA MCP governance summary tool. The response returns:
- A Vega-Lite chart of domain health scores
- A Mermaid diagram flagging three domains with outstanding quality issues

The CDO taps the Finance domain binding chip in the response, which opens the Finance domain record in the DDA UI. They follow up: *"Who owns the entities flagged in Finance?"* — the model returns a table of data owners with contact details.

Both artefacts appear in the session artefact tray. Total: four turns, two minutes.

**Personas served:** Chief Data Officer  
**Key features exercised:** Mobile layout, Vega-Lite rendering, Mermaid rendering, `@`-binding chip click-through to DDA UI, artefact tray

---

### Journey B — Business Staff: finding a data asset (1 turn, no platform navigation)

A Finance analyst needs the approved customer dataset for a quarterly report. They open Data AI Assistant and type `@Customer` — the `@`-binding typeahead opens and filters in real time. They select **Customer Master Entity** from the panel; a binding chip `@{Customer Master Entity}` is inserted. They submit:

> *"Is `@{Customer Master Entity}` approved for use in Finance reporting and where do I access it?"*

The model confirms classification and approval status, provides the data owner contact, and links to the entity record. No DDA platform navigation required.

Total: one turn.

**Personas served:** Business Staff  
**Key features exercised:** `@`-binding typeahead, binding chip resolution, single-turn self-service answer

---

### Journey C — Data Practitioner: cross-domain quality investigation (branching)

A data engineer suspects a quality issue affecting two domains. They type:

> *"Compare quality scores for `@{Finance Domain}` and `@{Operations Domain}` and show me any shared entities with issues."*

The model invokes multiple DDA MCP tool calls (visible as collapsed disclosure cards) and returns:
- A comparative Vega-Lite chart
- A Mermaid ERD of the shared entities

The engineer expands a tool call disclosure to inspect raw query parameters. They then edit their original message to scope the comparison to a single classification tier. This creates a **new branched conversation thread** pre-loaded with the original context. Both threads appear in the history panel; the original is untouched.

**Personas served:** Data Practitioner  
**Key features exercised:** Multi-entity `@`-binding, tool call disclosure cards, message edit → branched thread, parallel conversation history

---

### Journey D — Governance Officer: policy compliance check (guided workflow)

A governance officer opens Data AI Assistant to run a weekly compliance check. They open the **Guided Workflows drawer** from the DDA platform nav and click **Data Quality Assessment**. The guided workflow prompt is injected alongside a prompt to focus on the Customer domain.

The model runs a multi-step quality assessment, invoking several DDA MCP tools sequentially and returning a structured governance report with a Vega-Lite chart of quality rule pass rates and a table of failing entities.

The officer uses the **report icon** on one response where the model missed a known quality rule, submitting an explanation via the modal. This generates an improvement signal queued for CDAiO triage.

**Personas served:** Governance Officer  
**Key features exercised:** Guided workflow invocation from Guided Workflows drawer, multi-step MCP tool calls, structured report rendering, report icon improvement signal

---

### Journey E — New User: onboarding orientation (first visit)

A new joiner opens Data AI Assistant for the first time. The conversation area shows the onboarding welcome state: a one-sentence description of the CDO second brain concept, three suggested starter questions, and a link to the prompt library.

They click *"What is an entity master and how do I find the entities I own?"* and receive a plain-language explanation of the DDA entity master concept, a list of entity types with definitions, and a suggested follow-up: *"Show me the entities in my team's domain."*

**Personas served:** New User / Onboarder  
**Key features exercised:** First-visit onboarding state, suggested starter questions, suggested follow-ups, business-style communication

---

## Persona × Feature Matrix

| Feature | CDO | Business Head | Business Staff | Data Practitioner | Governance Officer | New User |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| Mobile-first layout | ✓ | ✓ | ✓ | | | |
| `@`-binding typeahead | ✓ | ✓ | ✓ | ✓ | ✓ | |
| Model switching | | | | ✓ | | |
| Document attachments | ✓ | ✓ | ✓ | ✓ | ✓ | |
| Guided workflow prompts | ✓ | ✓ | | ✓ | ✓ | ✓ |
| Tool call disclosures | | | | ✓ | ✓ | |
| Vega-Lite charts | ✓ | ✓ | | ✓ | ✓ | |
| Mermaid diagrams | | | | ✓ | ✓ | |
| Data tables | ✓ | ✓ | ✓ | ✓ | ✓ | |
| Conversation branching | | | | ✓ | ✓ | |
| Shared conversations | ✓ | ✓ | | ✓ | ✓ | |
| Onboarding welcome state | | | | | | ✓ |
| Thumbs-down feedback | ✓ | | | ✓ | ✓ | |
