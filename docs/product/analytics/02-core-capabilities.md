# 2. Proposed Architecture and Capabilities

## Purpose and Boundaries

This section defines the proposed logical architecture for governed AI-enabled analytics and data mining. It explains each component's responsibility and the contracts between components. It is implementation-neutral: it names required behavior, inputs, outputs, and evidence without selecting products, programming languages, frameworks, storage services, or deployment patterns. [Section 3](./03-technical-implementation.md) maps these responsibilities to an illustrative technology stack.

The design separates AI-assisted interpretation from governed computation. A language model may match a question to an approved operation and summarize a completed result. Registered definitions, deterministic software, and controlled data services perform the calculation. A structured caller may bypass natural-language interpretation, but it may not bypass entitlements, validation, controls, execution evidence, or other mandatory stages.

Component names identify logical responsibilities. They do not require one independently deployed service per component. Required behaviors describe the proposal, not verified features of a released product.

## Platform Roles

The operating model separates analytical use, definition ownership, access policy, governance, integration, and platform operation. One person may hold several roles, but the organization must review combinations that create conflicts of interest.

| Role | Primary Responsibility |
|---|---|
| Analytical End User | Requests governed analysis and views results within assigned permissions. |
| Power Analyst | Performs deeper exploration, drilldown, and authorized evidence export. |
| Data Modeller | Maintains business and physical data metadata in the Semantic Data Repository (SDR). |
| Metrics Modeller | Authors metric, dimension, operation, and dataset definitions for review. |
| Entitlements Manager | Maintains analytical access, row-scope, and masking policies. |
| Analytics Governance | Approves definitions and oversees analytical quality and catalog integrity. |
| Integration Engineer | Registers supported source connections and physical mappings. |
| Platform Admin | Operates the service within governance policy. This role does not confer analytical data access. |

Production access must come from approved entitlement policy, not from an authoring or administrative role alone.

### Role and Capability Boundaries

| Activity | Accountable Role | Required Separation |
|---|---|---|
| Use approved analytics | Analytical End User or Power Analyst | Access remains limited by DES policy. |
| Author data metadata and mappings | Data Modeller | Production approval remains with the designated governance process. |
| Author metrics and operations | Metrics Modeller | The author cannot make a definition available merely by submitting it. |
| Approve analytical definitions | Analytics Governance | Approval is recorded against a versioned definition. |
| Maintain entitlement policy | Entitlements Manager | Platform administration does not imply authority to grant data access. |
| Register source connections | Integration Engineer | Credentials remain inside the controlled execution boundary. |
| Operate platform services | Platform Admin | Administrative access does not imply permission to run analytical queries. |

The implementation must record who proposed, reviewed, approved, deprecated, and used each governed definition. Organizations may assign these responsibilities differently, but they must preserve accountable approval and prevent infrastructure privileges from becoming analytical entitlements.

## Architecture and Request Flow

The governed path applies the same controls to conversational users, autonomous agents, and custom applications.

```mermaid
flowchart TD
    subgraph Consumers["AI Consumers"]
        direction LR
        Chat["Conversational Assistant"]
        Agents["Autonomous Agents and Data Mining"]
        Apps["Custom Applications"]
    end

    subgraph Platform["AI Analytics Platform"]
        direction TB
        MCP["MCP Capability Layer\nAuthentication, tools, and response contract"]
        IRA["Intent Resolution Agent (IRA)\nCandidate retrieval, ranking, parameters, and purpose signal"]
        RAPL["Role-Aware Projection Layer (RAPL)\nMetric, dimension, row, classification, and masking permissions"]
        SVL["Semantic Validation Layer (SVL)\nApproved definition resolution and Logical Query Plan"]
        SCL["Semantic Controls Layer (SCL)\nScale, complexity, classification, compliance, and concurrency"]
        PQP["Physical Query Planner (PQP)\nApproved mappings and source sub-plans"]
        FQE["Federated Query Engine (FQE)\nControlled execution and result assembly"]
        DVL["Data Visualization Language (DVL)\nGoverned chart or table contract"]
        NSA["Narrative Synthesis Agent (NSA)\nOptional result-grounded summary"]
        ALS[("Analytical Lineage Store (ALS)\nCorrelated decisions, execution, and terminal outcomes")]
        PAS["Provenance Artifact Service (PAS)\nSigned compliance-purpose evidence"]
        Response(["Structured Response\nData, display, narrative, lineage, and compliance state"])
    end

    subgraph Context["Governed Context"]
        direction LR
        SMR[("Semantic Metrics Repository (SMR)\nApproved metrics, dimensions, operations, and datasets")]
        SDR[("Semantic Data Repository (SDR)\nData meaning, quality, structure, and mappings")]
        DES[("Data Entitlements Store (DES)\nAccess, row scope, masks, and classification ceilings")]
        SMR -. "approved mapping references" .-> SDR
    end

    Model["External Language Model Service\nIntent ranking and narrative synthesis"]
    Renderer["Optional Rendering Service\nDisplay specification to SVG or PNG"]

    subgraph Sources["Registered Data Sources"]
        direction LR
        Relational[("Relational Analytical Store")]
        DataAPI[("Approved Data Service")]
        Specialized[("Relationship or Multidimensional Store")]
    end

    Consumers -->|"authenticated analytical request"| MCP
    MCP -->|"natural-language request"| IRA
    MCP -->|"structured request bypasses IRA"| RAPL
    IRA -->|"approved candidate retrieval"| SMR
    IRA -->|"ranking and purpose classification"| Model
    IRA -->|"resolved operation and parameters"| RAPL
    RAPL -->|"policy lookup"| DES
    RAPL -->|"entitlement projection"| SVL
    RAPL -->|"entitlement evidence"| ALS
    SVL -->|"definition resolution"| SMR
    SVL -->|"Logical Query Plan"| SCL
    SVL -->|"validation and plan evidence"| ALS
    SCL -->|"approved plan and execution budget"| PQP
    SCL -->|"controls evidence"| ALS
    PQP -->|"mapping resolution"| SMR
    PQP -->|"physical execution envelope"| FQE
    FQE -->|"controlled source execution"| Sources
    FQE -->|"execution evidence"| ALS
    FQE -->|"typed result"| DVL
    FQE -->|"typed result"| NSA
    NSA -->|"bounded synthesis request"| Model
    ALS -->|"compliance-triggered event set"| PAS
    DVL -->|"display specification"| Response
    NSA -->|"validated narrative or omission state"| Response
    ALS -->|"lineage reference"| Response
    PAS -->|"sealed artifact state"| Response
    Response -->|"response package"| MCP
    MCP -->|"structured consumer response"| Consumers
    Consumers -. "optional render request" .-> Renderer
    Renderer -. "SVG or PNG" .-> Consumers

    style Platform fill:#dbeafe,stroke:#2563eb
    style Context fill:#f8fafc,stroke:#64748b
    style Sources fill:#f8fafc,stroke:#64748b
```

### Component Interaction Map

The architecture is not a strictly linear sequence. Some components provide lookups, several write evidence during the request, structured requests bypass IRA, and presentation components run in parallel. The component contracts below therefore associate inputs and outputs with the component that owns them rather than with a numbered step.

| Component | Business Role | Receives | Provides |
|---|---|---|---|
| AI Consumers | Start governed analysis and present the answer. | Business question or approved operation; structured response | Authenticated analytical request; optional render request |
| MCP Capability Layer | Govern the platform boundary and public contract. | Authenticated request; assembled response package | Correlated request to IRA or RAPL; structured response to consumer |
| Intent Resolution Agent (IRA) | Translate business language into an approved analytical request. | Natural-language request; approved candidates from SMR; bounded model output | Resolved operation and parameters; confidence and purpose evidence; clarification request when needed |
| Semantic Metrics Repository (SMR) | Govern reusable analytical meaning and versions. | Authoring changes; discovery and definition lookups; mapping lookups | Approved operations, metrics, dimensions, datasets, and mapping references |
| Semantic Data Repository (SDR) | Govern data meaning, structure, quality, and mapping context. | Approved data metadata and lineage updates | Versioned data context and mapping targets referenced by SMR and PQP |
| Data Entitlements Store (DES) | Govern business-level analytical access policy independently. | Approved role and access-policy changes | Versioned metric, dimension, row-scope, mask, and classification policies |
| Role-Aware Projection Layer (RAPL) | Determine the caller's permitted analytical scope. | Resolved request; authenticated identity; DES policies | Entitlement projection to SVL; entitlement evidence to ALS |
| Semantic Validation Layer (SVL) | Turn an entitled request into a valid logical calculation. | Resolved request; entitlement projection; approved SMR definitions | Logical Query Plan to SCL; validation and plan evidence to ALS; structured rejection |
| Semantic Controls Layer (SCL) | Decide whether a valid plan may execute under current policy and conditions. | Logical Query Plan; versioned controls; profiling evidence; operating state | Approved plan and budget to PQP; controls evidence to ALS; structured rejection |
| Physical Query Planner (PQP) | Translate logical calculations into bounded source instructions. | Approved Logical Query Plan; execution budget; SMR and SDR mapping context | Physical execution envelope to FQE; plan integrity evidence |
| Federated Query Engine (FQE) | Execute approved source instructions and assemble controlled results. | Physical execution envelope; registered source connections | Typed result to DVL and NSA; execution evidence to ALS; explicit terminal outcome |
| Registered Data Sources | Execute bounded operations over governed business data. | Authorized source instructions from FQE | Typed source data or explicit failure to FQE |
| Data Visualization Language (DVL) | Define a consistent governed presentation. | Typed result; resolved intent; approved labels and units | Display specification to response assembly |
| Narrative Synthesis Agent (NSA) | Produce an optional result-grounded explanation. | Bounded result content; bounded model draft | Validated narrative or omission state to response assembly; narrative evidence to ALS |
| External Language Model Service | Support bounded language ranking and drafting. | Candidate-ranking request from IRA; synthesis request from NSA | Ranking or draft text back to the requesting component |
| Analytical Lineage Store (ALS) | Preserve the correlated evidence chain across the request. | Intent, entitlement, validation, controls, plan, execution, and presentation events | Lineage reference to response assembly; event set to PAS and audit export |
| Provenance Artifact Service (PAS) | Seal additional evidence for compliance-purpose results. | Active compliance trigger; correlated ALS event set | Sealed artifact or failure state to response assembly; export state |
| Structured Response | Assemble the governed delivery package. | Typed result; display; narrative; lineage; compliance state; warnings and errors | Response package to MCP Capability Layer |
| Optional Rendering Service | Produce a static visual without joining analytical computation. | Self-contained display specification from a consumer | SVG or PNG to the consumer |

The running example uses one request throughout. Each primary flow component shows both its input and output as technology-neutral JSON. When one component emits a request, definition, projection, plan, result, or evidence reference, the receiving component repeats the same field name and value so the handoff is visible. Identifiers and values are illustrative, not implementation defaults.

A result is repeatable only when the request, source snapshot, definition versions, effective permissions, configuration, and execution software are preserved. Deterministic planning does not compensate for changed data or definitions.

## AI Consumers

**Business definition.** AI consumers are the channels through which people and automated processes request and use governed analysis.

**Why this role exists.** The architecture separates the user experience from analytical governance so that several interfaces can use the same approved definitions, permissions, controls, and evidence.

**Input and output.** A consumer starts with a business question or a known approved operation and the caller's authenticated context. It outputs a governed analytical request and later renders the structured response without recalculating or reinterpreting its values.

AI consumers include conversational assistants, autonomous agents, data-mining workflows, and custom applications. They provide the user experience; they do not own analytical definitions, permissions, query planning, or execution.

A consumer may submit natural language or an approved operation identifier with typed parameters. It passes the caller's authenticated context, preserves the returned result identifier for follow-up actions, and distinguishes governed results from exploratory output produced outside this platform.

### Input and Output Example

The running example asks the platform to compare the caller's equity portfolios with their benchmarks for the current quarter:

```json
{
  "input": {
    "business_request": "Compare my equity portfolios with their benchmarks this quarter",
    "requested_experience": "analysis with presentation and narrative"
  },
  "output": {
    "analytical_request_id": "request-draft-001",
    "question": "Compare my equity portfolios with their benchmarks this quarter"
  }
}
```

The authentication and identity context travels through the trusted transport. It is not embedded in the analytical request body.

The consumer request becomes the MCP Capability Layer input, beginning the governed pipeline.

## MCP Capability Layer (MCP)

> **Governing principles:** [P1 - Semantic abstraction](./01-overview.md#design-principles), [P2 - Controls before execution](./01-overview.md#design-principles), and [P5 - Role-aware by default](./01-overview.md#design-principles)

**Business definition.** The MCP Capability Layer is the governed front door to the analytical service.

**Why it exists.** It gives every consumer one consistent contract and prevents conversational, automated, or custom interfaces from creating alternative paths around authentication and governance.

**Input and output.** It receives an authenticated natural-language or structured request. It outputs a correlated request to the correct pipeline stage and, after processing, a structured response to the consumer.

The MCP Capability Layer is the single governed analytical entry point. The transport authenticates the caller before tool routing and passes identity through trusted request context. Bearer tokens are not analytical tool arguments.

### Tool Catalog

| Tool | Purpose |
|---|---|
| run_analytics | Accepts either a natural-language question or an approved operation with typed parameters. Natural language is resolved by the IRA before governed execution begins. |
| list_operations | Lists operations and parameters available to the caller. |
| drilldown | Creates a governed follow-up request from a prior result and hierarchy selection. |

A drilldown inherits analytical context but receives a new request identifier and passes the current entitlement and controls pipeline again. Prior approval never authorizes a later request automatically.

### Execution Profiles

| Profile | Result |
|---|---|
| data_retrieval | Returns a typed, paginated dataset governed by an approved dataset contract. |
| metric_query | Returns calculated data and a DVL display specification. |
| full_analytical | Adds an optional governed narrative to the metric response. |

Execution profiles control optional response assembly, not governance. Every profile uses the complete entitlement, validation, controls, planning, execution, and lineage path. PAS invocation is compliance-driven and independent of presentation profile.

### Intent Confirmation

When the IRA cannot select one operation confidently, the MCP layer returns ranked confirmation cards containing the proposed operation, bound parameters, material filters, and presentation preview. Refinement does not execute a backend query. The selected request still passes all downstream controls.

Confidence thresholds, candidate counts, and refinement limits require evaluation. They are not accuracy guarantees.

A confirmation card contains the candidate operation, resolved parameter values, time period, material filters, confidence, and a presentation preview. It must not expose physical schemas or executable queries. The session binds the candidate set to the authenticated caller and expires after a short configured interval.

The consumer may select a candidate, refine the question, or cancel. Selection resumes the original governed request; refinement produces a new ranked candidate set without querying a backend. Operations marked as requiring confirmation always present a card, regardless of confidence.

### Capability Governance

The capability layer exposes only registered tools and approved operation metadata. Tool discovery is entitlement-aware. Request limits, session limits, and allowed response sizes are versioned platform controls. Changes to tool contracts follow the same review and compatibility process as other public interfaces.

### Input and Output Example

The MCP layer accepts the natural-language request and creates a correlation identifier before routing it to the IRA:

```json
{
  "input": {
    "authenticated_context_ref": "caller-context",
    "analytical_request_id": "request-draft-001",
    "question": "Compare my equity portfolios with their benchmarks this quarter"
  },
  "output": {
    "request_id": "req-20260518-093241",
    "route": "natural_language",
    "analytical_request_id": "request-draft-001",
    "question": "Compare my equity portfolios with their benchmarks this quarter"
  }
}
```

For natural-language requests, the correlated request becomes the IRA input. A structured request proceeds directly to RAPL.

## Intent Resolution Agent (IRA)

> **Governing principles:** [P1 - Semantic abstraction](./01-overview.md#design-principles) and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The IRA translates a user's business language into a registered analytical operation and its typed parameters.

**Why it exists.** Users should not need to know catalog identifiers, but the platform must not let a language model invent calculations or executable queries. The IRA bridges that gap and asks for confirmation when meaning is uncertain.

**Input and output.** It receives a natural-language request and the approved definitions discoverable by the caller. It outputs a resolved operation, parameters, confidence evidence, and purpose signal, or a clarification request.

The IRA is the only AI step before computation. It retrieves candidate operations from the SMR, ranks them against the user's request, binds parameters, and returns either a resolved request or a confirmation choice. It does not receive credentials, execute queries, or generate executable SQL.

The IRA uses registered descriptions rather than physical schemas. Caller-dependent phrases such as "my portfolios" remain unresolved until RAPL evaluates the authenticated identity. The output contains an approved operation identifier, typed parameters, candidate evidence, model details, and a confidence score.

The IRA also estimates whether the stated purpose is compliance-related. Ambiguous purpose requires clarification. The score is an input to a deterministic control; the model does not make the final control decision. Structured callers bypass the IRA and declare purpose through a validated field.

### Resolution Pipeline

| Stage | Required Behavior | Evidence Retained |
|---|---|---|
| Candidate retrieval | Search approved SMR operation and metric descriptions within the caller's discoverable scope. | Query embedding version, retrieved identifiers, and retrieval scores. |
| Candidate ranking | Rank candidates and bind parameters using the natural-language request and registered descriptions. | Model and prompt-template versions, ranked identifiers, confidence, and bound parameters. |
| Ambiguity check | Compare the leading candidates and apply operation-specific confirmation rules. | Thresholds, score difference, and confirmation decision. |
| Purpose classification | Estimate whether the stated purpose is compliance-related. | Purpose score and any clarification outcome. |
| Output validation | Validate the selected operation identifier and typed parameters against the SMR contract. | Validation result and rejection reason when applicable. |

Retrieval narrows the model's choice set; it does not approve a definition or establish that the chosen intent is correct. Evaluation must measure top-candidate accuracy, correct-candidate coverage, clarification quality, and false certainty across representative language and user roles.

### Input and Output Example

The IRA resolves the question to an approved comparison operation. The symbolic caller-dependent scope remains unresolved:

```json
{
  "input": {
    "request_id": "req-20260518-093241",
    "question": "Compare my equity portfolios with their benchmarks this quarter",
    "discoverable_catalog_ref": "approved-operations-for-caller"
  },
  "output": {
    "resolved_request_id": "resolved-20260518-093242",
    "request_id": "req-20260518-093241",
    "operation_id": "compare_portfolio_to_benchmark",
    "parameters": {
      "portfolio_scope": "caller_authorized_portfolios",
      "asset_class": "EQUITY",
      "time_period": "current_quarter"
    },
    "confidence": 0.93,
    "compliance_purpose_score": 0.08,
    "confirmation_required": false
  }
}
```

The IRA uses the SMR to limit interpretation to approved analytical choices. Its resolved operation then becomes part of the RAPL input.

## Semantic Metrics Repository (SMR)

> **Governing principles:** [P1 - Semantic abstraction](./01-overview.md#design-principles), [P3 - Deterministic metric resolution](./01-overview.md#design-principles), and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The SMR is the organization's governed rulebook for analytical meaning: what a metric, dimension, operation, or dataset means and which approved version applies.

**Why it exists.** Without a shared catalog, each report, application, or AI interaction can reconstruct the same business concept differently. The SMR makes approved definitions reusable and versioned.

**Input and output.** Authors submit proposed definitions through governance. At runtime, the IRA, SVL, and PQP submit approved identifiers or discovery queries. The SMR outputs discoverable operation metadata, pinned semantic definitions, and approved mapping references.

In a governed AI-enabled analytics situation, the Semantic Metrics Repository (SMR) provides a catalog of approved metrics, dimensions, operations, and dataset contracts. It is the authoritative source for concepts that the governed path can resolve.

| Definition Type | Required Content |
|---|---|
| Metric | Formula or governed measure, aggregation, units, dimensions, classification, source affinity, owner, version, and approval state. |
| Dimension | Business meaning, hierarchy, compatible metrics, and mapping information. |
| Operation | Parameter contract, supported metrics and dimensions, execution profile, and confirmation requirements. |
| Dataset | Approved fields, classifications, selection rules, mapping, refresh expectations, and pagination policy. |

Only approved versions are resolvable for new governed requests. Historical versions remain available to authorized reviewers for lineage reconstruction.

### Definition Lifecycle and Versioning

| State | Meaning |
|---|---|
| Proposed | An author has submitted a draft that cannot be used for governed execution. |
| In Review | Named reviewers are assessing meaning, sources, tests, ownership, and access implications. |
| Approved | The exact version may be resolved by governed requests. |
| Deprecated | Existing evidence remains interpretable, but new use is discouraged or blocked according to policy. |
| Retired | The version is unavailable for new execution and retained only for authorized historical reconstruction. |

Approving a new version does not rewrite earlier lineage. Each request pins the versions it resolved. Compatibility rules determine whether consumers must change when parameters, dimensions, units, formulas, mappings, or classifications change.

### Minimum Definition Contract

Every definition carries a stable identifier, semantic version, owner, approval state, effective period, classification, and change history. Metrics additionally declare their formula or governed measure, aggregation behavior, units, compatible dimensions, source affinity, physical mapping reference, and tests. Operations declare typed parameters, output expectations, execution profile, permitted drilldowns, and whether confirmation is mandatory. Dataset contracts declare approved fields, classifications, selection rules, ordering, pagination, and freshness expectations.

The SMR and Semantic Data Repository (SDR) are separate stores within the Data Context Store (DCS). The SMR defines analytical meaning; the SDR describes organizational data and its physical structure. Approved mappings link the two without exposing physical schema details through the normal AI interface.

### Formula Language

The formula language expresses metric logic using registered metric identifiers, logical fields, arithmetic, conditions, safe division, time windows, filtered aggregation, and other explicitly supported operations. It does not accept arbitrary SQL or backend-specific expressions.

A formula is human-readable and audit-visible, but registration does not prove correctness. Approval requires accountable ownership, test cases, source validation, and comparison with independently verified results.

### Authoring and Discovery

Metrics Modellers submit definitions through an authenticated workflow. Analytics Governance reviews and approves them. Consumers discover only approved operations available under their entitlements. Search indexes and embeddings may improve discovery; they do not change approval state or access rights.

### Input and Output Example

The resolved operation references two approved metrics without exposing their physical implementation:

```json
{
  "input": {
    "operation_id": "compare_portfolio_to_benchmark",
    "required_state": "approved"
  },
  "output": {
    "operation_definition_ref": "smr:operation:compare_portfolio_to_benchmark@1.3.0",
    "operation_id": "compare_portfolio_to_benchmark",
    "version": "1.3.0",
    "status": "approved",
    "metrics": [
      {
        "metric_id": "portfolio_return",
        "version": "2.1.0"
      },
      {
        "metric_id": "benchmark_return",
        "version": "1.4.2"
      }
    ],
    "dimensions": [
      "portfolio"
    ],
    "required_parameters": [
      "portfolio_scope",
      "asset_class",
      "time_period"
    ],
    "execution_profile": "full_analytical"
  }
}
```

The approved operation definition and resolved request now move to RAPL, where the caller's permitted analytical scope is determined.

## Role-Aware Projection Layer (RAPL)

> **Governing principle:** [P5 - Role-aware by default](./01-overview.md#design-principles)

**Business definition.** RAPL converts organizational access policy into the exact analytical scope permitted for the current caller and request.

**Why it exists.** Permission to reach a data service does not explain which business metrics, dimensions, populations, or fields a person may use. RAPL makes those business-level restrictions explicit before planning begins.

**Input and output.** It receives the resolved request, authenticated identity context, and versioned DES policies. It outputs an entitlement projection containing approved concepts, row scope, masks, classification ceiling, and decision evidence.

RAPL converts authenticated identity claims and policies from the Data Entitlements Store (DES) into an effective entitlement projection. It validates identity context, retrieves role definitions, merges them according to policy, resolves claim-based row scopes, and records the decision.

| Restriction | Proposed Treatment |
|---|---|
| Data and metric access | Deny any required domain, classification, or metric outside the effective access set. |
| Dimension access | Reject a required unauthorized dimension; do not silently change the question. |
| Row scope | Resolve typed predicates from trusted claims and attach them to the plan. |
| Column masking | Carry each required mask and its policy basis into planning and execution. |
| Classification ceiling | Preserve the effective ceiling for validation and controls. |

The proposed multi-role rule uses union for granted data, metrics, and dimensions; strict intersection for row scopes; and union for masks, so any applicable mask remains in force. Explicit-deny and missing-claim behavior must be defined consistently in DES policy and tested independently of role order.

Row scopes are typed predicates, not interpolated query fragments. Masks are enforced before protected values leave the controlled execution boundary. Each projection records the roles, policy versions, resolved scopes, masks, and decision basis in the ALS.

### Multi-Role Merge and Deny Behavior

| Entitlement | Proposed Merge Rule |
|---|---|
| Data domains, metrics, and dimensions | Union of grants, subject to explicit-deny policy and classification ceiling. |
| Row scopes | Strict intersection. Every applicable population restriction remains in force. |
| Column masks | Union. A mask required by any applicable role remains active. |
| Classification ceiling | Most restrictive applicable ceiling unless policy explicitly defines another reviewed rule. |

The merge must be independent of role order and must fail closed when a required role definition or claim cannot be resolved. The design decision about whether an explicit deny overrides every grant must be uniform across DES, RAPL, tests, and audit explanations.

### Column Masking Modes

| Mode | Result Treatment |
|---|---|
| null replacement | Replace the protected value with null while preserving the field. |
| redacted label | Replace the value with a fixed approved label. |
| excluded | Remove the field from the returned schema. |
| hash replacement | Replace the value with a deterministic one-way representation when approved grouping behavior is required. |

Masking changes what downstream consumers can observe. The selected mode, protected field, policy version, and enforcement location therefore form part of the analytical evidence.

### Input and Output Example

RAPL resolves the symbolic portfolio scope from the authenticated caller's policy and claims:

```json
{
  "input": {
    "resolved_request_id": "resolved-20260518-093242",
    "request_id": "req-20260518-093241",
    "operation_definition_ref": "smr:operation:compare_portfolio_to_benchmark@1.3.0",
    "authenticated_context_ref": "caller-context",
    "entitlement_policy_ref": "current-policy-snapshot"
  },
  "output": {
    "entitlement_projection_ref": "projection:req-20260518-093241",
    "request_id": "req-20260518-093241",
    "policy_version": "portfolio-access-7.2",
    "approved_metrics": [
      "portfolio_return",
      "benchmark_return"
    ],
    "approved_dimensions": [
      "portfolio"
    ],
    "row_scope": {
      "field": "portfolio_id",
      "operator": "in",
      "values": [
        "GLOB_EQ_OPP",
        "UK_CORE_INC",
        "ASIA_PAC_GRW",
        "EUR_BAL_INC"
      ]
    },
    "column_masks": [],
    "classification_ceiling": "INTERNAL",
    "decision": "approved"
  }
}
```

The entitlement projection becomes an SVL input alongside the resolved request and pinned SMR definitions.

## Semantic Validation Layer (SVL)

> **Governing principles:** [P2 - Controls before execution](./01-overview.md#design-principles) and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The SVL is the semantic quality gate that turns an entitled business request into a precise, technology-neutral calculation plan.

**Why it exists.** A recognized intent can still be incomplete, incompatible, unapproved, or inconsistent with the caller's permissions. The SVL stops those requests before physical planning or source access.

**Input and output.** It receives the resolved request, entitlement projection, and pinned SMR definitions. It outputs a backend-independent Logical Query Plan or a structured rejection.

The SVL validates a fully qualified request and compiles it into a platform-independent LQP. No AI model runs in this component.

The SVL validates structure and parameter types; resolves operations, metrics, dimensions, and datasets to approved versions; checks semantic compatibility; applies the RAPL projection; attaches validated compliance inputs; and creates a directed plan containing logical concepts rather than SQL, connection details, or physical identifiers.

Unknown, unapproved, incompatible, or unauthorized required concepts cause a structured rejection. The SVL does not return a partial calculation that changes the requested meaning. Its validation shows conformity to registered definitions; it does not establish that the definitions or source data are correct.

### Validation Stages

| Stage | Checks | Output |
|---|---|---|
| Request validation | Required fields, types, parameter ranges, and operation contract. | A well-formed request or structured rejection. |
| Semantic resolution | Approval state, pinned versions, metric-dimension compatibility, and dataset contract. | Fully resolved logical identifiers. |
| Entitlement application | Permitted concepts, row predicates, masks, and classification ceiling. | An entitlement-constrained request. |
| Plan generation | Logical scans, filters, calculations, joins, sorts, limits, and output shape. | A backend-independent LQP. |

The LQP also carries definition versions, data-affinity hints, mask directives, compliance inputs, and a preliminary impact indicator. It contains no credentials, connection endpoints, physical table names, or executable SQL.

### Input and Output Example

The SVL converts the qualified request into a backend-independent plan:

```json
{
  "input": {
    "resolved_request_id": "resolved-20260518-093242",
    "operation_definition_ref": "smr:operation:compare_portfolio_to_benchmark@1.3.0",
    "entitlement_projection_ref": "projection:req-20260518-093241"
  },
  "output": {
    "lqp_id": "lqp-20260518-093243",
    "request_id": "req-20260518-093241",
    "operation_id": "compare_portfolio_to_benchmark",
    "metric_versions": {
      "portfolio_return": "2.1.0",
      "benchmark_return": "1.4.2"
    },
    "steps": [
      {
        "type": "metric_scan",
        "metrics": [
          "portfolio_return",
          "benchmark_return"
        ]
      },
      {
        "type": "filter",
        "field": "asset_class",
        "operator": "eq",
        "value": "EQUITY"
      },
      {
        "type": "row_scope",
        "field": "portfolio_id",
        "operator": "in",
        "value_ref": "projection:req-20260518-093241"
      },
      {
        "type": "sort",
        "field": "portfolio_return",
        "direction": "descending"
      }
    ],
    "time_period": {
      "type": "relative",
      "value": "current_quarter"
    },
    "column_masks": []
  }
}
```

The completed Logical Query Plan becomes the SCL input for the mandatory release decision.

## Semantic Controls Layer (SCL)

> **Governing principles:** [P2 - Controls before execution](./01-overview.md#design-principles), [P8 - Explainability at every layer](./01-overview.md#design-principles), and [P9 - Administrator sovereignty within governance bounds](./01-overview.md#design-principles)

**Business definition.** The SCL is the operational and governance release gate for an otherwise valid analytical plan.

**Why it exists.** Entitlement and semantic validity do not address excessive scale, unsafe complexity, operating capacity, classification boundaries, or compliance-purpose handling. The SCL decides whether the plan may proceed under current policy and conditions.

**Input and output.** It receives the Logical Query Plan, versioned control policy, profiling evidence, and operating state. It outputs an approved plan with an execution budget or a structured rejection, together with a recorded decision.

The SCL is the mandatory release gate between logical validation and physical planning. It evaluates every LQP against versioned controls and records the decision before execution.

| Control | Decision |
|---|---|
| Data scale | Compare an evidence-based scan estimate with the configured limit. |
| Complexity | Check plan nodes, join depth, source count, and other bounded measures. |
| Classification | Compare the highest required classification with the permitted ceiling. |
| Compliance | Evaluate approved metric metadata and declared or classified purpose. |
| Concurrency | Check active work against the operating limit. |
| Timeout | Assign a bounded execution budget after blocking checks pass. |

Estimates are not exact measurements. The record identifies the source and freshness of the statistics used. Rejections return structured reasons and safe ways to narrow the request.

The proposed compliance trigger requires both a compliance-relevant metric and a compliance purpose. For natural-language requests, the SCL evaluates the IRA score against a configured threshold; structured requests declare purpose explicitly. The SCL records both signals and invokes PAS when both are active. Whether this rule is sufficient for a jurisdiction or activity remains a deployment-specific compliance decision.

### Control Decision Contract

Each control records its configured limit, observed or estimated value, data source, evaluation version, outcome, and reason. The SCL evaluates all controls needed for a useful explanation, even when one failure is sufficient to block execution. Sensitive platform state, such as other tenants' workload details, is not returned to the caller.

The data-scale estimate uses current SDR profiling statistics and the resolved row scope. The complexity control considers structural cost separately from volume. The classification control applies both platform boundaries and the caller's effective ceiling. The concurrency control protects shared execution resources without weakening tenant isolation. After all blocking controls pass, the SCL assigns a timeout and writes the signed or integrity-protected decision record before releasing the plan.

No interactive user, automated agent, administrator, cache path, or internal retry bypasses this release decision. A retried or modified request receives its own decision record.

### Input and Output Example

The SCL records each decision and assigns the execution budget:

```json
{
  "input": {
    "lqp_id": "lqp-20260518-093243",
    "controls_policy_ref": "current-controls",
    "operating_state_ref": "current-capacity"
  },
  "output": {
    "controls_decision_ref": "controls:lqp-20260518-093243",
    "lqp_id": "lqp-20260518-093243",
    "decision": "approved",
    "checks": {
      "data_scale": {
        "estimate": 412000,
        "limit": 50000000,
        "result": "pass"
      },
      "complexity": {
        "score": 4,
        "limit": 50,
        "result": "pass"
      },
      "classification": {
        "required": "INTERNAL",
        "ceiling": "INTERNAL",
        "result": "pass"
      },
      "compliance": {
        "metric_signal": false,
        "purpose_signal": false,
        "result": "standard"
      },
      "concurrency": {
        "active": 3,
        "limit": 20,
        "result": "pass"
      }
    },
    "timeout_seconds": 30
  }
}
```

An approved controls decision releases the Logical Query Plan and execution budget to the PQP.

## Physical Query Planner (PQP)

> **Governing principles:** [P1 - Semantic abstraction](./01-overview.md#design-principles) and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The PQP translates an approved business calculation into bounded instructions that registered data sources can execute.

**Why it exists.** Business definitions should remain stable when physical schemas or source technologies change. The PQP contains that translation boundary and keeps physical details away from AI consumers and language models.

**Input and output.** It receives the approved Logical Query Plan, execution budget, pinned mappings, and source capabilities. It outputs a physical execution envelope containing source sub-plans, protection directives, and integrity evidence.

The PQP is the boundary between logical concepts and physical execution. It resolves the approved physical mapping associated with each pinned definition version, expands logical time expressions, groups work by source affinity, and compiles source-specific sub-plans.

The PQP applies row predicates and masking requirements to each relevant sub-plan. Where a source can enforce masking, the generated query performs it before values leave that source. Otherwise, an approved controlled execution stage applies the mask before returning data outside the FQE boundary.

A repeatable physical plan requires the same LQP, definition and mapping versions, planner version, configuration, and source capabilities. The PQP records those dependencies. It does not hold source credentials or execute plans.

### Compilation Stages

| Stage | Responsibility |
|---|---|
| Mapping resolution | Resolve each logical scan and measure against the mapping pinned to the approved definition version. |
| Predicate binding | Bind typed dimension filters and RAPL row scopes using backend-safe parameters. |
| Time resolution | Expand relative periods against the recorded evaluation timestamp and calendar. |
| Source grouping | Group compatible work by data affinity and identify required cross-source assembly. |
| Source instruction compilation | Produce a bounded sub-plan in the registered instruction format for each source group. |
| Plan sealing | Create an integrity digest and record planner, instruction-format, mapping, and configuration versions. |

An implementation may delegate federation to one execution service or create several source sub-plans with an explicit assembly contract. Both approaches implement the same logical responsibility; Section 3 proposes a specific choice.

### Input and Output Example

The PQP resolves the approved mappings and creates a technology-neutral execution envelope:

```json
{
  "input": {
    "lqp_id": "lqp-20260518-093243",
    "controls_decision_ref": "controls:lqp-20260518-093243",
    "mapping_set_ref": "approved-mappings"
  },
  "output": {
    "plan_id": "plan-20260518-093244",
    "lqp_id": "lqp-20260518-093243",
    "controls_decision_ref": "controls:lqp-20260518-093243",
    "mapping_versions": [
      "portfolio-mapping-4.6"
    ],
    "sub_plans": [
      {
        "source_id": "portfolio-performance-source",
        "metrics": [
          "portfolio_return",
          "benchmark_return"
        ],
        "filters": [
          "asset_class",
          "authorized_portfolios",
          "resolved_date_range"
        ]
      }
    ],
    "resolved_date_range": {
      "from": "2026-04-01",
      "to": "2026-05-18"
    },
    "column_masks": [],
    "timeout_seconds": 30
  }
}
```

The physical execution envelope becomes the FQE input; no upstream component executes against a data source.

## Federated Query Engine (FQE)

> **Governing principles:** [P1 - Semantic abstraction](./01-overview.md#design-principles), [P4 - Complete analytical lineage](./01-overview.md#design-principles), and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The FQE is the controlled execution boundary that runs approved source instructions and assembles their results.

**Why it exists.** Source credentials, timeouts, federation, caching, masking, and failure handling require one accountable boundary. Concentrating them here prevents upstream components and AI consumers from gaining direct backend access.

**Input and output.** It receives an approved physical execution envelope. It outputs a typed result or an explicit terminal outcome, plus execution evidence for the ALS.

The FQE is the only logical component with access to registered backend connections. It validates source availability, executes approved sub-plans within the assigned timeout, joins compatible results on governed dimensions, enforces any remaining masks within its controlled boundary, and records execution outcomes.

Caching uses a canonical key that includes the effective plan, tenant, entitlement projection, definition versions, and relevant configuration. A cache hit still passes current authorization and produces a new lineage event. Compliance-purpose queries bypass the cache unless approved policy provides equivalent evidence and freshness guarantees.

Source failure is visible. The response identifies incomplete sources and affected metrics. A partial result may be returned only when the approved operation contract permits partial semantics; otherwise, the request fails rather than representing missing values as a complete answer.

The FQE records source identifiers, plan hashes, timing, row counts, cache status, errors, and mask application. It does not expose credentials or unrestricted physical schema details to consumers or language models.

### Execution Pipeline

| Stage | Required Behavior |
|---|---|
| Plan admission | Verify plan integrity, source registration, timeout, tenant, and control approval. |
| Cache evaluation | Check an entitlement-safe canonical key and current policy before reuse. |
| Source execution | Run sub-plans within their time and resource budgets. |
| Assembly | Join or combine results only on approved compatible dimensions. |
| Final protection | Apply any remaining masks and verify the returned schema before release. |
| Evidence write | Record the outcome before returning the result or terminal failure. |

Supported source categories may include relational analytical stores, governed semantic services, approved data APIs, relationship stores, and multidimensional analytical engines. Technical connectivity does not make a source usable automatically. Each connection requires approved mappings, credentials, classifications, timeout behavior, and failure semantics.

Result-size limits determine whether the engine returns inline data, paginates an approved dataset, streams within a controlled protocol, or rejects the request. These choices are part of the operation contract and response evidence.

### Input and Output Example

The FQE executes the approved plan and returns typed result rows:

```json
{
  "input": {
    "plan_id": "plan-20260518-093244",
    "controls_decision_ref": "controls:lqp-20260518-093243"
  },
  "output": {
    "result_id": "res-20260518-093247",
    "request_id": "req-20260518-093241",
    "plan_id": "plan-20260518-093244",
    "status": "complete",
    "sources_used": [
      "portfolio-performance-source"
    ],
    "cache_status": "miss",
    "rows": [
      {
        "portfolio_id": "GLOB_EQ_OPP",
        "portfolio": "Global Equity Opportunities",
        "portfolio_return": 0.0421,
        "benchmark_return": 0.0385
      },
      {
        "portfolio_id": "ASIA_PAC_GRW",
        "portfolio": "Asia Pacific Growth",
        "portfolio_return": 0.0367,
        "benchmark_return": 0.039
      },
      {
        "portfolio_id": "UK_CORE_INC",
        "portfolio": "UK Core Income",
        "portfolio_return": 0.0287,
        "benchmark_return": 0.0254
      },
      {
        "portfolio_id": "EUR_BAL_INC",
        "portfolio": "EUR Balanced Income",
        "portfolio_return": 0.0193,
        "benchmark_return": 0.0231
      }
    ]
  }
}
```

The typed result now branches to presentation and evidence components. DVL determines how consumers should display it.

## Data Visualization Language (DVL)

> **Governing principle:** [P7 - Deterministic visualization](./01-overview.md#design-principles)

**Business definition.** The DVL turns a governed result into a consistent chart or table contract that consumers can render.

**Why it exists.** Presentation choices can change interpretation. A governed display contract prevents each consumer or language model from independently choosing labels, units, ordering, thresholds, and chart form.

**Input and output.** It receives the approved intent, typed result schema, values, and presentation metadata. It outputs a versioned display specification or the governed table fallback.

The DVL produces a structured chart or table specification from the approved intent and result schema. A registry maps comparison, trend, distribution, threshold, attribution, relationship, and composition patterns to compatible presentation contracts. A governed table is the fallback.

Contract selection is deterministic for the same intent, result schema, registry version, and configuration. Labels and units come from approved definitions, not physical fields. An authorized analyst may request an allowed compatible override; the platform rejects incompatible choices and records accepted overrides.

The DVL returns a specification, not a rendered image. Consumer applications render it directly or pass it to an independently governed rendering service.

### Intent Pattern Taxonomy

| Pattern | Purpose | Typical Contract |
|---|---|---|
| Comparison | Compare measures across discrete categories. | Grouped bar chart or governed table. |
| Trend | Show change over an ordered time dimension. | Line chart. |
| Distribution | Show spread, frequency, or concentration. | Histogram or governed table. |
| Threshold | Compare observations with a limit or benchmark. | Threshold matrix, bar chart, or table. |
| Attribution | Decompose a total into contributing factors. | Waterfall chart. |
| Relationship | Show association between two measures. | Scatter plot. |
| Composition | Show part-to-whole structure. | Treemap or governed table. |

### Chart Contract Selection

Each registered contract declares compatible patterns, required field types, cardinality limits, axis or column bindings, sorting, interaction behavior, accessibility requirements, and fallback behavior. The selector evaluates the most specific compatible contract first. If none matches, it returns the governed table contract rather than asking a language model to invent a display.

Themes may change approved colors and typography without changing the analytical contract. Threshold colors, units, labels, ordering, and benchmark semantics come from governed metadata and must remain interpretable in accessible and monochrome presentations.

### Input and Output Example

The DVL selects the registered comparison contract from the intent and result shape:

```json
{
  "input": {
    "result_id": "res-20260518-093247",
    "intent_pattern": "comparison",
    "presentation_metadata_ref": "approved-labels-and-units"
  },
  "output": {
    "display_spec_ref": "display:res-20260518-093247",
    "result_id": "res-20260518-093247",
    "type": "chart",
    "contract": "multi_series_comparison",
    "contract_version": "2.0",
    "mark": "bar",
    "category": {
      "field": "portfolio",
      "label": "Portfolio"
    },
    "measures": [
      {
        "field": "portfolio_return",
        "label": "Portfolio Return",
        "format": "percentage"
      },
      {
        "field": "benchmark_return",
        "label": "Benchmark Return",
        "format": "percentage"
      }
    ],
    "sort": {
      "field": "portfolio_return",
      "direction": "descending"
    }
  }
}
```

In parallel with DVL, the NSA receives the bounded result content needed for an optional narrative.

## Narrative Synthesis Agent (NSA)

> **Governing principles:** [P6 - Governed narrative](./01-overview.md#design-principles) and [P10 - Deterministic computation, not generation](./01-overview.md#design-principles)

**Business definition.** The NSA provides an optional plain-language explanation of a completed result.

**Why it exists.** A concise explanation makes analysis easier to consume, but narrative generation must remain separate from calculation and must not introduce unsupported values or conclusions.

**Input and output.** It receives only approved result labels, values, units, dimensions, and permitted derivations. It outputs a validated narrative or an explicit omission state.

The NSA optionally produces a concise plain-language summary after computation. Its input is limited to approved result labels, values, units, and dimensions. It does not calculate metrics or change the result.

A validator checks every stated number against the returned data or an independently recomputed permitted derivation. If validation fails, the service may retry once and then omits the narrative while recording the failure. Quantitative matching reduces unsupported claims but does not prove that wording, emphasis, or causal interpretation is correct. Evaluation therefore includes semantic review, not numeric matching alone.

Disabling the NSA has no effect on calculation, display specification, lineage, or compliance evidence.

### Anchoring and Validation

The narrative contract separates a short lead statement, supporting detail, and the result identifiers to which each claim is anchored. Validation covers numbers, units, dimension labels, comparison direction, and permitted derived counts. It rejects invented causes, recommendations, forecasts, or significance claims unless the approved operation explicitly provides those outputs.

The lineage record captures the model, prompt-template version, validation outcome, retry count, and omission reason. Model selection may vary by result complexity, but changing models must not alter computed data or the DVL contract.

### Input and Output Example

The NSA summarizes only statements supported by the result rows:

```json
{
  "input": {
    "result_id": "res-20260518-093247",
    "allowed_content": [
      "approved labels",
      "result values",
      "units",
      "permitted derived counts"
    ]
  },
  "output": {
    "narrative_ref": "narrative:res-20260518-093247",
    "result_id": "res-20260518-093247",
    "narrative": {
      "lead": "Two of four equity portfolios outperformed their benchmarks this quarter.",
      "detail": "Global Equity Opportunities returned 4.21% compared with 3.85% for its benchmark. UK Core Income returned 2.87% compared with 2.54%.",
      "anchored_to": [
        "GLOB_EQ_OPP",
        "UK_CORE_INC",
        "ASIA_PAC_GRW",
        "EUR_BAL_INC"
      ]
    },
    "validation": {
      "numbers": "passed",
      "units": "passed",
      "dimension_labels": "passed"
    }
  }
}
```

The presentation outcome joins the decisions and execution events already written to the ALS throughout the request.

## Analytical Lineage Store (ALS)

> **Governing principles:** [P4 - Complete analytical lineage](./01-overview.md#design-principles) and [P8 - Explainability at every layer](./01-overview.md#design-principles)

**Business definition.** The ALS is the evidence ledger for how each governed request was interpreted, authorized, controlled, planned, executed, and presented.

**Why it exists.** A result cannot be traced or assessed for repeatability if its definitions, permissions, decisions, source references, and terminal outcome are scattered or overwritten.

**Input and output.** It receives correlated events from each stage. It outputs an authorized lineage chain, searchable references, integrity evidence, and the event set used by PAS and audit export.

The ALS preserves correlated events for every accepted request, including entitlement decisions, controls decisions, execution, presentation, and terminal failure. Records use a common request identifier so an authorized reviewer can reconstruct the sequence without treating one final payload as the complete history.

By default, lineage stores hashes, definition and policy versions, bounded summaries, source references, plan identifiers, decisions, and timing rather than full raw requests or results. An approved policy may require additional content. The design minimizes sensitive data while preserving evidence for its intended review.

Claims of immutability depend on storage enforcement. Write-once retention, versioning, signatures, encryption, tenant-scoped authorization, key management, reconciliation, and tested recovery provide the required integrity properties. Application convention alone is insufficient. Corrections create linked amendment records rather than altering prior evidence.

Retention varies by record class, jurisdiction, and business purpose. Definition versions and references needed to interpret retained results remain available for at least the corresponding evidence period.

### Stored Event Types

| Event | Minimum Evidence |
|---|---|
| Request accepted | Tenant, caller reference, tool, operation, parameters or bounded request representation, and timestamp. |
| Intent resolved | Candidate set, selected operation, model evidence, confidence, and confirmation history. |
| Entitlement projected | Policy versions, active roles, resolved row scopes, masks, ceiling, and decision. |
| Controls evaluated | Each control input, limit, outcome, reason, and assigned timeout. |
| Plan compiled | Logical and physical plan digests plus definition, mapping, planner, and instruction-format versions. |
| Execution completed | Sources, timings, row counts, cache status, failures, and result digest. |
| Presentation assembled | DVL contract, narrative validation, artifact state, and response status. |
| Request terminated | Rejection, cancellation, timeout, or failure stage and structured reason. |

### Isolation, Retention, and Audit Export

Every index entry and object key is tenant-scoped. Authorization applies to both search metadata and stored objects. Audit export is a separately authorized capability; possession of a result identifier does not grant access to its evidence.

Retention policy defines periods for request events, controls decisions, execution evidence, result artifacts, blocked requests, and definition versions. A shorter result-data period may be appropriate, but retained evidence must state when source data or result payloads are no longer available for exact reconstruction. Legal hold, deletion, amendment, and key-rotation behavior require explicit design and testing.

An audit export includes the selected event chain, referenced definition and policy versions, verification material, export scope, and exporter's identity. The platform signs the export package and records the export as a new auditable event.

### Input and Output Example

The ALS correlates stage records without storing the full result by default:

```json
{
  "input": {
    "request_id": "req-20260518-093241",
    "result_id": "res-20260518-093247",
    "display_spec_ref": "display:res-20260518-093247",
    "narrative_ref": "narrative:res-20260518-093247",
    "correlated_stage_events_ref": "events:req-20260518-093241"
  },
  "output": {
    "lineage_ref": "lineage:req-20260518-093241",
    "request_id": "req-20260518-093241",
    "result_id": "res-20260518-093247",
    "events": [
      {
        "type": "intent_resolved",
        "record_id": "evt-intent-001"
      },
      {
        "type": "entitlement_projected",
        "record_id": "evt-access-001"
      },
      {
        "type": "controls_approved",
        "record_id": "evt-controls-001"
      },
      {
        "type": "plan_compiled",
        "record_id": "evt-plan-001"
      },
      {
        "type": "execution_completed",
        "record_id": "evt-execution-001"
      },
      {
        "type": "presentation_assembled",
        "record_id": "evt-presentation-001"
      }
    ],
    "result_digest": "digest:<illustrative-value>",
    "retention_policy": "analytical-evidence-standard"
  }
}
```

When both compliance signals are active, the correlated ALS event set becomes the PAS input.

## Provenance Artifact Service (PAS)

> **Governing principles:** [P2 - Controls before execution](./01-overview.md#design-principles), [P4 - Complete analytical lineage](./01-overview.md#design-principles), and [P9 - Administrator sovereignty within governance bounds](./01-overview.md#design-principles)

**Business definition.** PAS packages the evidence required for a compliance-purpose result into a sealed, independently verifiable artifact.

**Why it exists.** Standard lineage supports operational review, while regulated uses may require a fixed schema, named framework references, a digital signature, and an export gate.

**Input and output.** It receives the active compliance trigger and the correlated ALS event set. It outputs a sealed artifact with verification metadata and an explicit export state, or a failure state that keeps export blocked.

PAS assembles additional evidence for a request whose two compliance signals are active. It reads the relevant ALS events, adds the metric, framework, intent, policy, plan, execution, and result references required by the approved artifact schema, and signs the canonical artifact bytes.

The platform enforces the export gate. A compliance-purpose result cannot be exported until PAS confirms that the artifact is complete and sealed. The response identifies the artifact, schema version, signing key, algorithm, and verification status.

A valid signature shows that the signed bytes have not changed since sealing. It does not prove that the calculation is correct or that the artifact satisfies a legal requirement. The organization validates the schema, retention, signing controls, and approval process for each intended framework.

### Compliance Artifact Contract

| Field | Purpose |
|---|---|
| compliance purpose and intent score | Records the purpose input and threshold decision. |
| triggered metrics and frameworks | Identifies the approved metadata that activated the additional evidence path. |
| regulatory trace identifier | Correlates the artifact with the retained event chain. |
| artifact schema version | Identifies the structure used by reviewers and verification software. |
| definition, policy, plan, and result references | Binds the artifact to the governed computation. |
| signing key, algorithm, and signature | Supports independent integrity verification. |
| export status | Shows whether sealing completed and export is permitted. |

If assembly or signing fails, the result remains non-exportable and the ALS records the terminal artifact state. Amendments create a new signed artifact that references the original; they do not replace sealed evidence.

### Input and Output Example

The portfolio comparison reaches the compliance decision with both signals inactive. No artifact is assembled, and the explicit compliance state continues to response assembly:

```json
{
  "input": {
    "request_id": "req-20260518-093241",
    "lineage_ref": "lineage:req-20260518-093241",
    "compliance_trigger": {
      "metric_signal": false,
      "purpose_signal": false
    }
  },
  "output": {
    "compliance_state_ref": "compliance:req-20260518-093241",
    "request_id": "req-20260518-093241",
    "artifact_required": false,
    "artifact_id": null,
    "export_status": "permitted",
    "reason": "two_signal_trigger_not_active"
  }
}
```

The result, presentation outputs, lineage reference, and any compliance artifact now become the response-assembly input.

## MCP Response Format

**Business definition.** The MCP response is the governed delivery contract between the analytical platform and its consumers.

**Why it exists.** Consumers need one unambiguous way to distinguish data, presentation, narrative, evidence, warnings, compliance state, and terminal status without reconstructing analytical meaning.

**Input and output.** Response assembly receives the typed result or terminal outcome plus presentation and evidence references. It outputs one structured envelope that the consumer can render, retain, or pass to an authorized follow-up action.

The platform is headless. It returns a structured response that lets different consumers present the same governed result without reinterpreting its meaning.

| Response Element | Purpose |
|---|---|
| request_id and result_id | Correlate the response, follow-up actions, and evidence. |
| status | Distinguishes complete, incomplete, rejected, failed, and timed-out outcomes. |
| data | Contains typed, paginated rows or an approved dataset extract. |
| display_spec | Contains the DVL chart or table contract when required. |
| narrative | Contains the optional validated NSA summary. |
| lineage | References the authorized analytical evidence. |
| compliance | Reports artifact and export-gate state when applicable. |
| warnings and errors | Identify limitations, affected sources, and remediation. |

### DVL Specification Format

A DVL specification is a discriminated chart or table envelope. It contains approved labels, units, formatting hints, encodings or columns, interaction rules, and the contract version. It may contain result data or a controlled reference, depending on response size and consumer capability. It never substitutes physical field names for governed labels.

### Response Status and Failure Semantics

Complete, incomplete, rejected, failed, and timed-out are distinct states. An incomplete response identifies missing sources or metrics and appears only when the operation contract permits partial semantics. A rejection means a governance or validation rule prevented execution. A failure or timeout means approved execution did not complete. Consumers must present these states explicitly and must not render an incomplete or failed response as a complete governed answer.

### Input and Output Example

The final response combines the computed result with its governed presentation and evidence references:

```json
{
  "input": {
    "request_id": "req-20260518-093241",
    "result_id": "res-20260518-093247",
    "display_spec_ref": "display:res-20260518-093247",
    "narrative_ref": "narrative:res-20260518-093247",
    "lineage_ref": "lineage:req-20260518-093241",
    "compliance_state_ref": "compliance:req-20260518-093241"
  },
  "output": {
    "request_id": "req-20260518-093241",
    "result_id": "res-20260518-093247",
    "status": "complete",
    "data_ref": "result:res-20260518-093247",
    "display_spec_ref": "display:res-20260518-093247",
    "narrative_ref": "narrative:res-20260518-093247",
    "lineage": {
      "record_ref": "lineage:req-20260518-093241",
      "available_to_caller": true
    },
    "compliance": {
      "state_ref": "compliance:req-20260518-093241",
      "triggered": false,
      "export_status": "permitted"
    },
    "warnings": [],
    "errors": []
  }
}
```

The MCP Capability Layer returns this response to the consumer, completing the governed request flow.

## External Components

External components remain outside the Analytics Engine boundary and retain their own ownership and controls.

### Conversational AI - Chat Front End

**Business definition and purpose.** The chat front end is a consumer experience for people who request analysis conversationally. It exists to manage dialogue and presentation without owning analytical meaning or controls.

**Input and output.** It receives a user's question, confirmation choices, and structured platform responses. It outputs authenticated analytical requests, rendered answers, and governed follow-up actions such as drilldown. It does not resolve definitions, enforce entitlements, plan queries, or gain access to backend credentials and schemas.

### Semantic Data Repository (SDR)

**Business definition and purpose.** The SDR is the governed description of the organization's data assets. It exists so analytical definitions can connect to understood data structures, quality expectations, and lineage rather than undocumented source fields.

**Input and output.** It receives approved data models, critical data elements, quality rules, structural metadata, and data-lineage references. It outputs versioned context and mapping targets used by SMR definitions and physical planning. The proposal does not assume that every organization already has a suitable SDR; readiness assessment establishes its coverage, ownership, freshness, and mapping quality.

### Data Entitlements Store (DES)

**Business definition and purpose.** The DES is the independent policy source for who may use which analytical concepts and data populations. It exists to keep access decisions separate from metric authorship and platform administration.

**Input and output.** It receives approved policies for metrics, dimensions, row scopes, masks, and classification ceilings. It outputs versioned role and policy definitions to RAPL. Policies reference logical concepts rather than physical table and column names.

### External Language Model Service

**Business definition and purpose.** The external language model service provides bounded language interpretation and synthesis. It exists to support natural interaction while remaining outside calculation, authorization, controls, and source execution.

**Input and output.** For IRA, it receives approved candidate descriptions and the user's question and returns ranking and parameter suggestions. For NSA, it receives bounded result content and returns a draft narrative. IRA and NSA validate those outputs before the flow continues.

### Registered Data Sources

**Business definition and purpose.** Registered data sources hold the governed business data on which approved analytics operate. They remain systems of record or analytical services rather than becoming part of the AI layer.

**Input and output.** They receive bounded, authorized source instructions from the FQE and return typed data or explicit failures. They do not receive natural-language questions, model prompts, or consumer credentials.

### Optional Rendering Service

**Business definition and purpose.** The optional rendering service converts a governed display contract into a static visual for consumers that cannot render it directly. It exists as a presentation utility, not as part of analytical computation.

**Input and output.** It receives a self-contained display specification and outputs SVG or PNG. It has no access to analytical definitions, source credentials, or execution backends. Section 3 identifies an illustrative product and implementation for this role.

## Design Decisions Requiring Evaluation

The proposal leaves several choices for implementation and governance teams to validate:

- role combinations and separation of duties;
- interaction between explicit denies and multi-role grants;
- operation contracts that may return partial results;
- evidence and freshness rules for caching;
- source snapshot retention and reconstruction;
- supported formula operations and source instruction formats;
- confidence and compliance-purpose thresholds;
- storage controls for evidence integrity and retention; and
- artifact schemas and approval processes for each intended regulatory use.

These are evaluation questions, not hidden implementation details. Section 4 defines measures for testing the architecture before broader adoption.

---

*Governed AI-Enabled Analytics and Data Mining - Technical White Paper - Draft*
