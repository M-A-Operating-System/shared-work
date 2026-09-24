# Contract Management Data Model

This document presents the business scope and logical data model for third-party IT, cloud and SaaS contracts. It moves from the business problem to the objects, domains and concepts needed to manage contract data, then provides the full data dictionary.

## M&A Operating System — AI & Data Advisory Practice

**M&A Operating System (MAOS) helps organizations turn data into measurable business outcomes.**

Our **AI & Data Advisory Practice** works with senior business, data, analytics, and technology leaders to improve how their organizations use information to grow revenue, understand customers, make better decisions, reduce operating cost, manage risk, and enable analytics and AI.

Most organizations do not lack data. They struggle to turn the data they already have into information the business can consistently trust and use. Customer information is fragmented, reports disagree, data is repeatedly copied and transformed, and business definitions vary across teams. Analytics and AI initiatives then inherit the same problems.

We start with the business outcome and work backwards to the information, architecture, governance, operating model, and technology changes required to achieve it. That may mean improving customer identity to support segmentation and personalization, creating more reliable management information, simplifying complex data flows, or establishing the trusted business context required for AI.

Our work typically includes:

- Improving customer identity, segmentation, personalization, and revenue-growth capabilities
- Solving complex data management and data content design issues for Legal Entity, Beneficial Owner, People, Securities, Product Definition and transactional data
- Creating more consistent, timely, and trusted information for reporting, analytics, forecasting, and decision-making
- Designing and maintaining business-aligned data models for operational, analytical, and AI needs
- Resolving data quality, reliability, and performance issues caused by complex data flows, fragmented connectivity, duplication, and uncontrolled data propagation
- Establishing trusted views of customers, legal entities, products, accounts, agreements, and other critical business subjects
- Simplifying data architectures and reducing unnecessary movement, duplication, and technology complexity
- Establishing practical data governance, ownership, and AI readiness aligned to business priorities

Our goal is not simply to modernize data technology. It is to make information work better for the business.

**The value of a data program should ultimately be measured by what the business can do better because of it.**

### Find Out More

To learn more about how M&A Operating System can help your organization turn data into measurable business outcomes, visit [maoperatingsystem.com](https://www.maoperatingsystem.com).

For a direct conversation about your data, analytics, or AI priorities, contact [cdao-advisory@maoperatingsystem.com](mailto:cdao-advisory@maoperatingsystem.com).

## About the M&A Operating System Practical Data Modelling Approach

The **M&A Operating System Practical Data Modelling Approach** is our proprietary, business-led methodology for translating business outcomes and challenges into data requirements and approved logical data models.

We engage business stakeholders and data-consuming groups to understand what they expect data services to make possible. Their needs are captured as plain-English business requirements, then translated through a controlled, traceable sequence of analysis and design activities. The methodology deliberately avoids overly technical terminology and modelling techniques, presenting the information in a business-readable, plain-English form. The resulting data modelling document follows the same sequence, allowing business stakeholders and data practitioners to understand, challenge, and approve the design.

## The Five-Step Process

### Step 1 — Gather and Approve Business Requirements

We identify the outcomes stakeholders expect, the challenges they need to solve, and the business activities that data services must support. These are documented as plain-English requirements and approved as the scope and source of knowledge for the design.

### Step 2 — Identify Actors, Objects, and Roles

Using **Subject-Based Data Modelling**, we identify the actors, roles, and objects in the business lifecycle and map them to domains representing the immutable subjects of the data. Domains describe the enduring people, organizations, things, places, and other subjects the business needs to understand—not the specific reason they appear in a single process.

Actors and objects are aligned to their underlying mastered subjects. Roles describe the capacity in which a subject participates in a relationship, process, or context. The same subject can perform several roles without being modelled repeatedly.

### Step 3 — Identify Relationships

We identify the relationships between actors and objects and express them as clear business verbs—such as owns, manages, supplies, purchases, or is party to. This makes their meaning understandable and reviewable by business and data stakeholders.

### Step 4 — Identify Lifecycle Events

We identify the events that actors, roles, and objects pass through as they live their natural lives and interact within business processes. These events include when an object is created, changed, activated, transferred, or retired; a subject assumes or ceases a role; or a relationship is established, modified, or ended. This determines what data must be captured at each stage.

### Step 5 — Design Logical Data Models

The approved requirements, subjects, roles, relationships, and lifecycle events form the logical data model, documented through four connected components:

- **Data Domains** — governed groupings representing the immutable subjects of the data
- **Data Concepts** — the unique logical elements that make up the data known and recorded about each subject
- **Data Relationships** — the business connections between concepts, including the roles they perform
- **Data Attributes** — the individual data elements that describe each concept or relationship

Each component remains traceable to the requirement that established its need. The completed document provides the shared record business stakeholders and data practitioners use to review and approve the data requirements and model design.

## 1 Business Scope

A buyer organisation acquires IT, cloud and SaaS services from third-party providers under written agreements, and must know at any date what each executed agreement obliges, permits, costs and protects, and be able to show the words in the signed original that say so.

### In scope

| ID | Business scope |
|---|---|
| SCI001 | The executed agreement as an original artefact (the signed PDF) with its renditions, execution status and signature evidence |
| SCI002 | The documents that make up an agreement: master agreement, order forms and statements of work, schedules, amendments, renewals and successor agreements, and terms incorporated by reference from the provider's website |
| SCI003 | The parties to an agreement and what each is to it: service provider, signing recipient, consuming entity, subcontractor, data processor, signatory and internal owner |
| SCI004 | The clauses of an agreement classified against a governed clause taxonomy, and the rights, obligations and prohibitions they create |
| SCI005 | The service definition: contracted services, ICT service type, deployment model, service levels, service credits, data locations, security, resilience and audit terms |
| SCI006 | Commercial and risk-allocation terms: fees, licence metrics and quantities, pricing and price change, payment, liability caps and heads of loss, indemnities and insurance |
| SCI007 | Lifecycle terms: effective and expiry dates, renewal, notice, termination rights, change regime for online terms, exit and data return |
| SCI008 | Evidence of each structured term: the clause, page, words and extraction method in the executed original, and whether a reviewer has verified it |

### Out of scope

| ID | Excluded subject | Owned by |
|---|---|---|
| SCO001 | Sourcing events, RFPs, bids and negotiation workflow before execution | A procurement process; its outcomes arrive here as documents |
| SCO002 | Invoices, payments and spend transactions | Transactions domain (DMD000000022) |
| SCO003 | Measured service performance, credits claimed and obligation fulfilment events | Metrics domain (DMD000000030) and Events domain (DMD000000020) |
| SCO004 | Master data of parties themselves: legal names, identifiers (LEI, EUID), group structure, addresses | LegalEntities (DMD000000012) and People (DMD000000001), referenced not redefined |
| SCO005 | Third-party risk assessments, due diligence, criticality assessments of business functions, exit-plan testing and audit findings | A third-party risk management model (not yet in DDA); see DEC004 |
| SCO006 | The provider's service catalogue as an enterprise subject independent of any agreement | A future Services or Products domain (not yet in DDA); see DEC003 |
| SCO007 | Sell-side customer contracts and non-IT contract types (leases, employment, M&A) | Later extensions of the same Documents model |

### Business requirement coverage

The discovery package contains 41 sourced business requirements. The table below shows their coverage by business topic.

| Business topic | Requirements |
|---|---|
| Agreement structure | 3 |
| Change of terms | 3 |
| Clauses | 1 |
| Commercial | 3 |
| Data protection | 3 |
| Evidence | 4 |
| Formation and execution | 3 |
| Governing law | 1 |
| Identification | 1 |
| Obligations | 1 |
| Oversight | 2 |
| Parties | 2 |
| Records retention | 2 |
| Regulatory reporting | 1 |
| Risk allocation | 3 |
| Security and resilience | 1 |
| Service definition | 1 |
| Service levels | 2 |
| Term and renewal | 2 |
| Termination and exit | 2 |

## 2 Object Model

The object model separates the commercial arrangement from the instruments and files that evidence it. Collections organize the arrangement. Documents represent independently identifiable instruments. A Document Version is subordinate to exactly one Document and represents a substantive state or edition of that Document; it is not a separate legal instrument. Files represent stored renditions of a Version.

| Object | Business meaning | Examples |
|---|---|---|
| Collection | A governed grouping administered as one arrangement or sub-arrangement. | Provider relationship, framework agreement, order, statement of work |
| Document | One independently identifiable legal or operational instrument. | MSA, order form, amendment, DPA, SLA, notice |
| Document Version | A substantive state or published edition of the same Document. | Draft, redline, agreed form, executed version, online edition |
| File | A stored rendition of one Document Version. | Signed PDF, native file, OCR copy, web snapshot |
| Legal Entity | A company or other legal person participating in an arrangement. | Provider, customer entity, subcontractor, processor |
| Person | An individual acting in relation to a contract. | Signatory, contract owner |
| Contracted Service | The agreement-specific service purchased from a provider. | Cloud hosting, SaaS subscription, managed service |
| Clause and Citation | The provision and source evidence supporting a structured term. | Clause number, page, quoted words, verification |

```mermaid
flowchart LR
  C[Collection] -->|contains| C2[Subordinate Collection]
  C -->|contains| D[Document]
  D -->|has| V[Document Version]
  V -->|represented by| F[File]
  D -->|contains| CL[Clause]
  CL -->|supports| T[Structured Term]
  T -->|evidenced by| CI[Citation]
  C -->|covers| S[Contracted Service]
  LE[Legal Entity] -->|participates in| C
  LE -->|provides| S
  LE -->|consumes| S
  P[Person] -->|signs| V
```

### Attribute consolidation and roll-up

Business attributes may be recorded at Collection, Document or Document Version level. The value made available at a parent level is a logical consolidation and overlay of the applicable values held at that level and at the levels beneath it. A Collection can therefore present a consolidated view of its member Documents and their Versions, while a Document can present the applicable view across its Versions.

Roll-up does not move, duplicate or overwrite the source facts. Every consolidated value must remain traceable to the Collection, Document or Version at which it was recorded. The consolidation, precedence, conflict-resolution and aggregation rules must be defined by document type because different instruments treat dates, parties, monetary terms, obligations and status differently. Where no valid rule exists, the model must preserve the distinct source values rather than manufacture a single answer.

```mermaid
flowchart LR
  V[Document Version] -->|version of| D[Document]
  D -->|member of| C[Collection]
  V -.-> VC([Consolidate and overlay Version attributes])
  VC -.->|document-type rules| D
  D -.-> DC([Aggregate and consolidate Document attributes])
  DC -.->|document-type rules| C
```

## 3 Domain Model

The model requires three enterprise domains. Service Provider, Customer, Consumer, Subcontractor, Processor, Signatory and Contract Owner are roles established by relationships; they are not separate masters.

| Domain | Anchor subject | Scope in this model |
|---|---|---|
| Documents | Document | A single document that evidences or forms part of an agreement: for an executed agreement, the executed original as signed, together with what it states. Extended from 'basic details about a single document including its name, type, brief description and link' to hold execution status, dates and the fingerprint of the executed original. |
| LegalEntities | LegalEntity | Reused as held in DDA: the primary concept for all legal entities. |
| People | Person | Reused as held in DDA: fundamental information about a real person. |

```mermaid
flowchart LR
  DOC[Documents Domain]
  LE[LegalEntities Domain]
  PEO[People Domain]
  LE -->|supplies services under| DOC
  LE -->|procures services under| DOC
  LE -->|consumes services under| DOC
  LE -->|performs subcontracted services under| DOC
  LE -->|processes personal data under| DOC
  PEO -->|signs| DOC
  DOC -->|is owned by| PEO
  DOC -->|governs amends incorporates supersedes| DOC
```

### Domain relationships

| ID | Source role | Forward verb | Target role | Inverse verb | Cardinality |
|---|---|---|---|---|---|
| REL001 | Service Provider | supplies services under | Service Contract | engages | MANY_TO_MANY |
| REL002 | Service Recipient | procures services under | Service Contract | is procured by | MANY_TO_MANY |
| REL003 | Service Consumer | consumes services under | Service Contract | is consumed by | MANY_TO_MANY |
| REL004 | Subcontractor | performs subcontracted services under | Head Contract | is subcontracted to | MANY_TO_MANY |
| REL005 | Data Processor | processes personal data under | Processing Agreement | appoints | MANY_TO_MANY |
| REL006 | Signatory | signs | Signed Instrument | is signed by | MANY_TO_MANY |
| REL007 | Owned Contract | is owned by | Contract Owner | owns | MANY_TO_ONE |
| REL008 | Amendment | amends | Amended Agreement | is amended by | MANY_TO_MANY |
| REL009 | Subordinate Agreement | is governed by | Master Agreement | governs | MANY_TO_ONE |
| REL010 | Incorporating Agreement | incorporates | Incorporated Terms | is incorporated into | MANY_TO_MANY |
| REL011 | Successor Agreement | supersedes | Predecessor Agreement | is succeeded by | MANY_TO_MANY |

## 4 Concept Model

The Documents domain contains the concepts needed to describe documentary evidence, lifecycle, commercial terms, services, risk allocation, data protection and continuing obligations. Document Versions are subordinate to Documents and sit between Document and Document Files. Recursive Document composition supports Collections containing Documents and subordinate Collections. The LegalEntities domain adds supplier profile, corporate relationship, governance, risk, performance, financial, compliance, intelligence, strategy, action and QBR concepts derived from the supplier profile template. Contract-specific dates, values, renewal terms and service levels remain in the Documents domain and can be consolidated into supplier views without being duplicated. Portfolio annual spend, contract expiry and heatmap zone are logical views derived from the underlying contract, assessment and health data. Attributes recorded at Version, Document and Collection level participate in the governed logical roll-up described in the Object Model.

```mermaid
flowchart TD
  D[Document] --> DV[Document Versions]
  DV --> DF[Document Files]
  D --> DC[Document Clauses]
  D --> CIT[Document Citations]
  D --> LIFE[Lifecycle Terms]
  LIFE --> REN[Renewal Terms]
  LIFE --> TER[Termination Rights]
  LIFE --> EXIT[Exit Terms]
  D --> COMM[Commercial Terms]
  COMM --> SVC[Contracted Services]
  SVC --> SLA[Service Levels]
  SLA --> CR[Service Credits]
  COMM --> PA[Price Adjustments]
  COMM --> LC[Liability Caps]
  COMM --> LH[Liability Heads]
  COMM --> IND[Indemnities]
  COMM --> INS[Insurance Requirements]
  D --> DATA[Data and Supplier Controls]
  DATA --> LOC[Data Locations]
  DATA --> DP[Data Protection Terms]
  DATA --> SUB[Subcontracting Terms]
  DATA --> AUD[Audit Rights]
  DATA --> RES[Resilience Terms]
  D --> OBL[Obligations]
  D --> CHG[Change Notice Rules]
  D --> DIS[Dispute Terms]
  LE[Legal Entity] --> SP[Supplier Profile]
  LE --> SS[Supplier Stakeholders]
  LE --> SV[Supplier Services]
  LE --> SR[Supplier Risk Assessments]
  LE --> PF[Supplier Performance Assessments]
  LE --> SF[Supplier Financial Assessments]
  LE --> SC[Supplier Compliance Assessments]
  LE --> SI[Supplier Intelligence]
  LE --> ST[Supplier Strategic Assessments]
  LE --> SA[Supplier Actions]
  LE --> QBR[Supplier QBR Metrics]
  LE --> CORP[Supplier Corporate Relationships]
```

### Concepts

| ID | Concept | Parent | Cardinality | Definition |
|---|---|---|---|---|
| SBJ033 | DocumentVersions | Document | ONE_TO_MANY | A substantive state, edition, publication or execution form of one Document. One record exists per recognized Version. |
| SBJ010 | DocumentFiles | DocumentVersions | ONE_TO_MANY_OPTIONAL | A stored file of the document: the executed original or another rendition of it (FRBR manifestation and item). |
| SBJ011 | DocumentClauses | Document | ONE_TO_MANY_OPTIONAL | A provision of the document at a numbered place in it, classified against the governed clause taxonomy. |
| SBJ012 | DocumentCitations | Document | ONE_TO_MANY_OPTIONAL | The evidence for one abstracted term value: where in the executed original it is stated, how it was extracted and whether it has been verified. |
| SBJ013 | DocumentRenewalTerms | Document | ONE_TO_ONE_OPTIONAL | The term and renewal provisions the document states. |
| SBJ014 | DocumentTerminationRights | Document | ONE_TO_MANY_OPTIONAL | A right to terminate the document held by one side on a stated trigger. |
| SBJ015 | DocumentExitTerms | Document | ONE_TO_ONE_OPTIONAL | What happens when the agreement ends: transition, assistance, data return and deletion. |
| SBJ016 | DocumentCommercialTerms | Document | ONE_TO_ONE_OPTIONAL | The document-level commercial terms: currency, value and payment. |
| SBJ017 | DocumentServices | Document | ONE_TO_MANY_OPTIONAL | A service the document contracts for: the service definition and its commercial line. |
| SBJ018 | DocumentServiceLevels | DocumentServices | ONE_TO_MANY_OPTIONAL | A service level committed for a contracted service. |
| SBJ019 | DocumentServiceCredits | DocumentServiceLevels | ONE_TO_MANY_OPTIONAL | A tier of service credit payable when achieved performance falls within a band. |
| SBJ020 | DocumentPriceAdjustments | Document | ONE_TO_MANY_OPTIONAL | A mechanism by which prices change during the term or at renewal. |
| SBJ021 | DocumentLiabilityCaps | Document | ONE_TO_MANY_OPTIONAL | A cap on one side's liability under the document. |
| SBJ022 | DocumentLiabilityHeads | Document | ONE_TO_MANY_OPTIONAL | A head of loss the document excludes or removes from the cap. |
| SBJ023 | DocumentIndemnities | Document | ONE_TO_MANY_OPTIONAL | An indemnity one side gives the other under the document. |
| SBJ024 | DocumentInsuranceRequirements | Document | ONE_TO_MANY_OPTIONAL | Insurance the provider must maintain under the document. |
| SBJ025 | DocumentDataLocations | Document | ONE_TO_MANY_OPTIONAL | A location where the document permits services to be provided or data to be stored or processed. |
| SBJ026 | DocumentDataProtectionTerms | Document | ONE_TO_ONE_OPTIONAL | The document's data-protection and data-use terms. |
| SBJ027 | DocumentSubcontractingTerms | Document | ONE_TO_ONE_OPTIONAL | The document's terms on subcontracting. |
| SBJ028 | DocumentAuditRights | Document | ONE_TO_MANY_OPTIONAL | A right of access, inspection or audit granted by the document. |
| SBJ029 | DocumentResilienceTerms | Document | ONE_TO_ONE_OPTIONAL | The document's continuity, incident and security-cooperation terms. |
| SBJ030 | DocumentObligations | Document | ONE_TO_MANY_OPTIONAL | A continuing commitment the document imposes: an obligation, a right or a prohibition binding one side. |
| SBJ031 | DocumentChangeNoticeRules | Document | ONE_TO_MANY_OPTIONAL | The notice the provider must give, and the customer's right, for one kind of change to online terms or services. |
| SBJ032 | DocumentDisputeTerms | Document | ONE_TO_ONE_OPTIONAL | Governing law and dispute resolution terms of the document. |
| SBJ034 | LegalEntitySupplierProfile | LegalEntity | ONE_TO_ONE_OPTIONAL | The core supplier profile for a Legal Entity that acts as a supplier. |
| SBJ035 | LegalEntitySupplierStakeholders | LegalEntity | ONE_TO_MANY_OPTIONAL | People assigned business, vendor-management, procurement, contract or executive-sponsor responsibilities for the supplier. |
| SBJ036 | LegalEntitySupplierServices | LegalEntity | ONE_TO_MANY_OPTIONAL | Products, services, supported capabilities, integrations and data exchanges associated with the supplier. |
| SBJ037 | LegalEntitySupplierRiskAssessments | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated assessments of supplier criticality, inherent risk, residual risk and fourth-party dependency. |
| SBJ038 | LegalEntitySupplierPerformanceAssessments | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated supplier-level performance and health results consolidated from services and contracts. |
| SBJ039 | LegalEntitySupplierFinancialAssessments | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated observations of supplier financial condition and financial risk. |
| SBJ040 | LegalEntitySupplierComplianceAssessments | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated supplier-level security, resilience, insurance and privacy assurance results. |
| SBJ041 | LegalEntitySupplierIntelligence | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated market, corporate, leadership, industry and regulatory intelligence concerning the supplier. |
| SBJ042 | LegalEntitySupplierStrategicAssessments | LegalEntity | ONE_TO_MANY_OPTIONAL | Dated assessments of strategic importance, switching complexity, innovation contribution and recommended treatment. |
| SBJ043 | LegalEntitySupplierActions | LegalEntity | ONE_TO_MANY_OPTIONAL | Risks, issues, renewal actions and executive escalations requiring tracking for the supplier. |
| SBJ044 | LegalEntitySupplierQBRMetrics | LegalEntity | ONE_TO_MANY_OPTIONAL | Supplier review metrics, targets, actual results, weights, scores, ownership and commentary for a review period. |
| SBJ045 | LegalEntitySupplierCorporateRelationships | LegalEntity | ONE_TO_MANY_OPTIONAL | Corporate relationships between the supplier and other Legal Entities, including its parent company. |

## 5 Data Dictionary

All attributes are listed once under their final owning concept or relationship.

| Attribute ID | Concept or relationship | Owner type | Attribute | Data type | Lookup | Definition |
|---|---|---|---|---|---|---|
| ATR207 | Document | Concept | DocumentCollectionPurpose | LOOKUP | DocumentCollectionPurposes | Purpose of a Collection, such as provider relationship, agreement, framework, order, statement of work or assurance pack. |
| ATR002 | Document | Concept | DocumentDescription | LONGTEXT |  | A short statement of what the document covers. |
| ATR007 | Document | Concept | DocumentExpirationDate | DATE |  | The date on which the document's initial or current stated term ends, if not perpetual. |
| ATR008 | Document | Concept | DocumentIsPerpetual | BOOLEAN |  | True when the document has no fixed end date (CUAD answer 'Perpetual'). |
| ATR009 | Document | Concept | DocumentLanguage | LOOKUP | DLT000000082 | The language of the executed text. |
| ATR010 | Document | Concept | DocumentPageCount | INTEGER |  | Number of pages in the executed original. |
| ATR206 | Document | Concept | DocumentRepresentationType | LOOKUP | DocumentRepresentationTypes | Whether the Document represents a governed Collection or one Individual instrument. |
| ATR016 | Document | Concept | DocumentReviewDate | DATE |  | The date the review status was reached. |
| ATR015 | Document | Concept | DocumentReviewStatus | LOOKUP | LKP003 | How far the whole document has been read and its terms abstracted and verified. |
| ATR012 | Document | Concept | DocumentSourceUrl | URL |  | For a document published online and incorporated by reference, the web address it is published at. |
| ATR001 | Document | Concept | DocumentTitle | TEXT |  | The title the document gives itself, e.g. 'Master Subscription Agreement'. |
| ATR003 | Document | Concept | DocumentType | LOOKUP | LKP001 | The form of the instrument, e.g. Order Form or Data Processing Agreement. |
| ATR202 | DocumentAmendment | Relationship | DocumentAmendmentModificationType | LOOKUP | LKP042 | The kind of textual change the amendment makes. |
| ATR201 | DocumentAmendment | Relationship | DocumentAmendmentSequence | INTEGER |  | Order in which the amendment applies to the amended document (1 for the first). |
| ATR151 | DocumentAuditRights | Concept | DocumentAuditRightsAuditParty | LOOKUP | LKP037 | Who may exercise the right. |
| ATR156 | DocumentAuditRights | Concept | DocumentAuditRightsCertificationOnly | BOOLEAN |  | True when the provider may satisfy the right with certifications or reports alone. |
| ATR154 | DocumentAuditRights | Concept | DocumentAuditRightsCostAllocation | LOOKUP | LKP038 | Who bears the cost. |
| ATR152 | DocumentAuditRights | Concept | DocumentAuditRightsFrequency | LOOKUP | LKP050 | How often the right may be exercised. |
| ATR153 | DocumentAuditRights | Concept | DocumentAuditRightsNoticeDays | INTEGER |  | Days of notice before an audit. |
| ATR155 | DocumentAuditRights | Concept | DocumentAuditRightsOnsiteAccess | BOOLEAN |  | True when on-site inspection is allowed. |
| ATR174 | DocumentChangeNoticeRules | Concept | DocumentChangeNoticeRulesChangeType | LOOKUP | LKP039 | The kind of change. |
| ATR177 | DocumentChangeNoticeRules | Concept | DocumentChangeNoticeRulesCustomerRight | LOOKUP | LKP040 | What the customer may do in response. |
| ATR175 | DocumentChangeNoticeRules | Concept | DocumentChangeNoticeRulesNoticeDays | INTEGER |  | Days of notice before the change binds. |
| ATR176 | DocumentChangeNoticeRules | Concept | DocumentChangeNoticeRulesNoticeMethod | LOOKUP | LKP011 | How notice of the change is given. |
| ATR037 | DocumentCitations | Concept | DocumentCitationsBoundingRegion | TEXT |  | Polygon on the page enclosing the quoted words. |
| ATR036 | DocumentCitations | Concept | DocumentCitationsCharLength | INTEGER |  | Length in characters of the quoted words. |
| ATR035 | DocumentCitations | Concept | DocumentCitationsCharOffset | INTEGER |  | Character offset of the quoted words in the document text. |
| ATR031 | DocumentCitations | Concept | DocumentCitationsCitedAttributeCode | TEXT |  | The DDA attribute code of the term value evidenced, e.g. DocumentLiabilityCapsFixedAmount. |
| ATR032 | DocumentCitations | Concept | DocumentCitationsCitedRecordKey | TEXT |  | Where the evidenced concept holds many records per document, the key of the record evidenced (e.g. the service or tier). |
| ATR033 | DocumentCitations | Concept | DocumentCitationsClauseNumber | TEXT |  | The number of the provision that states the value. |
| ATR040 | DocumentCitations | Concept | DocumentCitationsConfidence | FLOAT |  | Confidence from 0 to 1 reported by an automated extraction. |
| ATR039 | DocumentCitations | Concept | DocumentCitationsExtractionMethod | LOOKUP | LKP007 | How the value was taken from the original. |
| ATR034 | DocumentCitations | Concept | DocumentCitationsPageNumber | INTEGER |  | Page of the executed original on which the value is stated (1-indexed). |
| ATR038 | DocumentCitations | Concept | DocumentCitationsQuotedText | LONGTEXT |  | The words of the executed original that state the value. |
| ATR041 | DocumentCitations | Concept | DocumentCitationsVerificationStatus | LOOKUP | LKP008 | Whether a reviewer has confirmed the passage states the value. |
| ATR042 | DocumentCitations | Concept | DocumentCitationsVerifiedBy | USER |  | The reviewer who reached the verification status. |
| ATR043 | DocumentCitations | Concept | DocumentCitationsVerifiedDate | DATE |  | The date the reviewer reached the verification status. |
| ATR030 | DocumentClauses | Concept | DocumentClausesActivityClass | LOOKUP | LKP006 | Whether the provision calls for action in normal performance or only when something goes wrong. |
| ATR026 | DocumentClauses | Concept | DocumentClausesClauseHeading | TEXT |  | The heading of the provision as written. |
| ATR025 | DocumentClauses | Concept | DocumentClausesClauseNumber | TEXT |  | The number or reference the document gives the provision, e.g. '11.2' or 'Schedule 3, para 4'. |
| ATR027 | DocumentClauses | Concept | DocumentClausesClauseText | LONGTEXT |  | The full text of the provision as written in the executed original. |
| ATR024 | DocumentClauses | Concept | DocumentClausesClauseType | LOOKUP | LKP005 | The governed type of the provision. |
| ATR029 | DocumentClauses | Concept | DocumentClausesPageEnd | INTEGER |  | Page on which the provision ends. |
| ATR028 | DocumentClauses | Concept | DocumentClausesPageStart | INTEGER |  | Page of the executed original on which the provision begins. |
| ATR071 | DocumentCommercialTerms | Concept | DocumentCommercialTermsAnnualValue | CURRENCY |  | Annual value of the fees, as stated or annualised; the DORA register's annual expense. |
| ATR073 | DocumentCommercialTerms | Concept | DocumentCommercialTermsBillingFrequency | LOOKUP | LKP050 | How often fees are invoiced. |
| ATR069 | DocumentCommercialTerms | Concept | DocumentCommercialTermsCurrency | LOOKUP | DLT000000072 | Currency of the fees. |
| ATR075 | DocumentCommercialTerms | Concept | DocumentCommercialTermsFeesNonCancellable | BOOLEAN |  | True when fees are non-cancellable and non-refundable. |
| ATR074 | DocumentCommercialTerms | Concept | DocumentCommercialTermsLateInterestPercent | FLOAT |  | Interest rate charged on late payment, per month. |
| ATR072 | DocumentCommercialTerms | Concept | DocumentCommercialTermsPaymentDays | INTEGER |  | Days after invoice within which payment is due. |
| ATR070 | DocumentCommercialTerms | Concept | DocumentCommercialTermsTotalValue | CURRENCY |  | Total value the document commits over its stated term. |
| ATR216 | DocumentComposition | Relationship | DocumentCompositionApplicabilityScope | LONGTEXT |  | The services, entities or circumstances to which the membership applies. |
| ATR213 | DocumentComposition | Relationship | DocumentCompositionIsConstitutive | BOOLEAN |  | True when the member forms part of the governed arrangement rather than being retained only as supporting material. |
| ATR215 | DocumentComposition | Relationship | DocumentCompositionIsPrimary | BOOLEAN |  | True when the member is the primary governing Document or subordinate Collection. |
| ATR212 | DocumentComposition | Relationship | DocumentCompositionMembershipRole | LOOKUP | DocumentCompositionMembershipRoles | The member's function in the Collection. |
| ATR214 | DocumentComposition | Relationship | DocumentCompositionSequence | INTEGER |  | Display or processing order of the member within its immediate Collection. |
| ATR137 | DocumentDataLocations | Concept | DocumentDataLocationsChangeNoticeDays | INTEGER |  | Days of notice the provider must give before changing the location. |
| ATR135 | DocumentDataLocations | Concept | DocumentDataLocationsCountry | LOOKUP | DLT000000071 | The country. |
| ATR134 | DocumentDataLocations | Concept | DocumentDataLocationsPurpose | LOOKUP | LKP032 | What happens at the location. |
| ATR136 | DocumentDataLocations | Concept | DocumentDataLocationsRegion | TEXT |  | Region or data-centre area within the country, where stated. |
| ATR143 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsAiTrainingUse | LOOKUP | LKP035 | Whether the provider may use customer data to train AI models. |
| ATR138 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsBreachNotificationHours | INTEGER |  | Hours within which the provider must notify a personal-data or security breach. |
| ATR139 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsEncryptionAtRestRequired | BOOLEAN |  | True when data must be encrypted at rest. |
| ATR140 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsEncryptionInTransitRequired | BOOLEAN |  | True when data must be encrypted in transit. |
| ATR141 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsMultiFactorAuthRequired | BOOLEAN |  | True when multi-factor authentication is required for access to customer data. |
| ATR142 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsTransferMechanism | LOOKUP | LKP033 | Legal basis for international transfers of personal data. |
| ATR144 | DocumentDataProtectionTerms | Concept | DocumentDataProtectionTermsUsageDataAggregation | LOOKUP | LKP035 | Whether the provider may aggregate and use usage data. |
| ATR182 | DocumentDisputeTerms | Concept | DocumentDisputeTermsArbitrationRules | TEXT |  | Arbitration rules named, e.g. ICC, LCIA. |
| ATR178 | DocumentDisputeTerms | Concept | DocumentDisputeTermsGoverningLawCountry | LOOKUP | DLT000000071 | Country whose law governs the document. |
| ATR179 | DocumentDisputeTerms | Concept | DocumentDisputeTermsGoverningLawRegion | TEXT |  | State, province or legal system within the country, e.g. 'England and Wales', 'New York'. |
| ATR181 | DocumentDisputeTerms | Concept | DocumentDisputeTermsMechanism | LOOKUP | LKP046 | How disputes are resolved. |
| ATR180 | DocumentDisputeTerms | Concept | DocumentDisputeTermsVenue | TEXT |  | Courts or seat named for disputes. |
| ATR061 | DocumentExitTerms | Concept | DocumentExitTermsAssistanceChargeBasis | LOOKUP | LKP016 | How exit assistance is charged. |
| ATR064 | DocumentExitTerms | Concept | DocumentExitTermsDataDeletionDays | INTEGER |  | Days after termination by which the provider must delete customer data. |
| ATR063 | DocumentExitTerms | Concept | DocumentExitTermsDataExportFormat | TEXT |  | The format in which data is returned. |
| ATR062 | DocumentExitTerms | Concept | DocumentExitTermsDataExportWindowDays | INTEGER |  | Days after termination during which the customer may export its data. |
| ATR065 | DocumentExitTerms | Concept | DocumentExitTermsDeletionCertified | BOOLEAN |  | True when the provider must certify deletion. |
| ATR066 | DocumentExitTerms | Concept | DocumentExitTermsExitPlanRequired | BOOLEAN |  | True when the provider must maintain an exit plan. |
| ATR068 | DocumentExitTerms | Concept | DocumentExitTermsInsolvencyDataReturn | BOOLEAN |  | True when the customer keeps access to and recovery of its data on the provider's insolvency, resolution or discontinuation (DORA Art 30(2)(d)). |
| ATR067 | DocumentExitTerms | Concept | DocumentExitTermsStressedExitCovered | BOOLEAN |  | True when the exit provisions apply on the provider's failure or insolvency as well as on planned exit. |
| ATR060 | DocumentExitTerms | Concept | DocumentExitTermsTransitionPeriodMonths | INTEGER |  | Months the provider must continue the service after termination to allow migration. |
| ATR022 | DocumentFiles | Concept | DocumentFilesCapturedDate | DATE |  | For a web snapshot, the date the online document was captured as published; for other files, the date the file was produced. |
| ATR020 | DocumentFiles | Concept | DocumentFilesFileHash | TEXT |  | SHA-256 fingerprint of the file content. |
| ATR018 | DocumentFiles | Concept | DocumentFilesFileName | TEXT |  | The file name as stored. |
| ATR017 | DocumentFiles | Concept | DocumentFilesFileRole | LOOKUP | LKP004 | What the file is: executed original, certified copy, preservation copy, text rendition, web snapshot or signature evidence. |
| ATR023 | DocumentFiles | Concept | DocumentFilesIsPdfA | BOOLEAN |  | True when the file conforms to PDF/A for long-term preservation. |
| ATR019 | DocumentFiles | Concept | DocumentFilesMediaType | TEXT |  | IANA media type of the file, e.g. application/pdf. |
| ATR021 | DocumentFiles | Concept | DocumentFilesStorageLocation | URL |  | Where the file is held in the authoritative repository. |
| ATR204 | DocumentIncorporation | Relationship | DocumentIncorporationIncorporationMode | LOOKUP | LKP041 | How the document is incorporated. |
| ATR203 | DocumentIncorporation | Relationship | DocumentIncorporationPrecedenceRank | INTEGER |  | Rank of the incorporated document in the order of precedence of the incorporating agreement (1 prevails over 2). |
| ATR128 | DocumentIndemnities | Concept | DocumentIndemnitiesCapTreatment | LOOKUP | LKP029 | How the indemnity stands against the liability cap. |
| ATR127 | DocumentIndemnities | Concept | DocumentIndemnitiesClaimType | LOOKUP | LKP030 | The kind of claim covered. |
| ATR130 | DocumentIndemnities | Concept | DocumentIndemnitiesExclusions | LONGTEXT |  | Circumstances the indemnity does not cover. |
| ATR126 | DocumentIndemnities | Concept | DocumentIndemnitiesIndemnifyingSide | LOOKUP | LKP009 | The side giving the indemnity. |
| ATR129 | DocumentIndemnities | Concept | DocumentIndemnitiesRemedies | LONGTEXT |  | Remedies the indemnifier may elect, e.g. procure a licence, modify, or refund. |
| ATR133 | DocumentInsuranceRequirements | Concept | DocumentInsuranceRequirementsCurrency | LOOKUP | DLT000000072 | Currency of the minimum cover. |
| ATR131 | DocumentInsuranceRequirements | Concept | DocumentInsuranceRequirementsInsuranceType | LOOKUP | LKP031 | The type of insurance. |
| ATR132 | DocumentInsuranceRequirements | Concept | DocumentInsuranceRequirementsMinimumAmount | CURRENCY |  | Minimum cover required. |
| ATR122 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsBasisPeriodMonths | INTEGER |  | Months of fees the cap is measured over, e.g. 12. |
| ATR117 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsCapType | LOOKUP | LKP025 | How the cap is expressed. |
| ATR119 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsCurrency | LOOKUP | DLT000000072 | Currency of the fixed amount. |
| ATR121 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsFeeBasis | LOOKUP | LKP027 | Which fees a fee-based cap is measured against. |
| ATR120 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsFeeMultiplier | FLOAT |  | Multiple of fees, e.g. 1.25 for 125% of charges. |
| ATR118 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsFixedAmount | CURRENCY |  | The fixed amount of the cap, where it has one. |
| ATR116 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsScope | LOOKUP | LKP026 | Which liability the cap limits. |
| ATR115 | DocumentLiabilityCaps | Concept | DocumentLiabilityCapsSide | LOOKUP | LKP009 | The side whose liability is capped. |
| ATR123 | DocumentLiabilityHeads | Concept | DocumentLiabilityHeadsHeadType | LOOKUP | LKP028 | The head of loss. |
| ATR125 | DocumentLiabilityHeads | Concept | DocumentLiabilityHeadsSide | LOOKUP | LKP009 | The side whose liability the treatment applies to. |
| ATR124 | DocumentLiabilityHeads | Concept | DocumentLiabilityHeadsTreatment | LOOKUP | LKP029 | How the head stands against the cap. |
| ATR173 | DocumentObligations | Concept | DocumentObligationsClauseNumber | TEXT |  | The provision stating the commitment. |
| ATR168 | DocumentObligations | Concept | DocumentObligationsDescription | LONGTEXT |  | What must, may or must not be done. |
| ATR172 | DocumentObligations | Concept | DocumentObligationsFirstDueDate | DATE |  | The first date the commitment falls due. |
| ATR170 | DocumentObligations | Concept | DocumentObligationsFrequency | LOOKUP | LKP050 | How often a recurring commitment falls due. |
| ATR169 | DocumentObligations | Concept | DocumentObligationsIsRecurring | BOOLEAN |  | True when the commitment recurs. |
| ATR165 | DocumentObligations | Concept | DocumentObligationsModality | LOOKUP | LKP045 | Obligation, right or prohibition. |
| ATR166 | DocumentObligations | Concept | DocumentObligationsObligatedSide | LOOKUP | LKP009 | The side bound by the commitment. |
| ATR167 | DocumentObligations | Concept | DocumentObligationsObligationType | LOOKUP | LKP044 | The kind of commitment. |
| ATR171 | DocumentObligations | Concept | DocumentObligationsTriggerEvent | TEXT |  | The event that brings an event-driven commitment into play. |
| ATR108 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsBasis | LOOKUP | LKP012 | The mechanism. |
| ATR111 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsCapPercent | FLOAT |  | Maximum increase per adjustment, in percent. |
| ATR114 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsFirstReviewDate | DATE |  | Date of the first adjustment the mechanism allows. |
| ATR112 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsFrequency | LOOKUP | LKP050 | How often adjustments may be made. |
| ATR110 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsIndexName | TEXT |  | The index followed, e.g. 'UK CPI'. |
| ATR113 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsNoticeDays | INTEGER |  | Days of notice required before an adjustment takes effect. |
| ATR109 | DocumentPriceAdjustments | Concept | DocumentPriceAdjustmentsTiming | LOOKUP | LKP013 | When the mechanism applies. |
| ATR044 | DocumentRenewalTerms | Concept | DocumentRenewalTermsInitialTermMonths | INTEGER |  | Length of the initial term in months. |
| ATR047 | DocumentRenewalTerms | Concept | DocumentRenewalTermsMaximumRenewals | INTEGER |  | Maximum number of renewals; empty when unlimited. |
| ATR048 | DocumentRenewalTerms | Concept | DocumentRenewalTermsNonRenewalNoticeDays | INTEGER |  | Days before expiry by which notice of non-renewal must be given. |
| ATR049 | DocumentRenewalTerms | Concept | DocumentRenewalTermsNoticeDayBasis | LOOKUP | LKP010 | Whether the notice period counts calendar or business days. |
| ATR052 | DocumentRenewalTerms | Concept | DocumentRenewalTermsNoticeDeadline | DATE |  | The last date on which notice of non-renewal can be given: the expiry date less the notice period on its day basis. |
| ATR050 | DocumentRenewalTerms | Concept | DocumentRenewalTermsNoticeMethod | LOOKUP | LKP011 | How non-renewal notice must be given. |
| ATR046 | DocumentRenewalTerms | Concept | DocumentRenewalTermsRenewalPeriodMonths | INTEGER |  | Length of each renewal period in months. |
| ATR051 | DocumentRenewalTerms | Concept | DocumentRenewalTermsRenewalPriceBasis | LOOKUP | LKP012 | How prices are set for a renewal period. |
| ATR045 | DocumentRenewalTerms | Concept | DocumentRenewalTermsRenewalType | LOOKUP | LKP014 | How the document renews at the end of a term. |
| ATR164 | DocumentResilienceTerms | Concept | DocumentResilienceTermsAuthorityCooperation | BOOLEAN |  | True when the provider must cooperate fully with competent and resolution authorities. |
| ATR157 | DocumentResilienceTerms | Concept | DocumentResilienceTermsBcpRequired | BOOLEAN |  | True when the provider must maintain a business continuity plan. |
| ATR158 | DocumentResilienceTerms | Concept | DocumentResilienceTermsBcpTestFrequency | LOOKUP | LKP050 | How often the plan must be tested. |
| ATR161 | DocumentResilienceTerms | Concept | DocumentResilienceTermsIncidentAssistanceChargeBasis | LOOKUP | LKP016 | How incident assistance is charged. |
| ATR162 | DocumentResilienceTerms | Concept | DocumentResilienceTermsPenetrationTestParticipation | BOOLEAN |  | True when the provider must take part in the customer's threat-led penetration testing. |
| ATR160 | DocumentResilienceTerms | Concept | DocumentResilienceTermsRecoveryPointHours | FLOAT |  | Recovery point objective in hours. |
| ATR159 | DocumentResilienceTerms | Concept | DocumentResilienceTermsRecoveryTimeHours | FLOAT |  | Recovery time objective in hours. |
| ATR163 | DocumentResilienceTerms | Concept | DocumentResilienceTermsSecurityTrainingParticipation | BOOLEAN |  | True when the provider must take part in the customer's security awareness training. |
| ATR107 | DocumentServiceCredits | Concept | DocumentServiceCreditsCreditApplication | LOOKUP | LKP024 | How the credit is given. |
| ATR106 | DocumentServiceCredits | Concept | DocumentServiceCreditsCreditPercent | FLOAT |  | Credit as a percentage of the fee for the period. |
| ATR104 | DocumentServiceCredits | Concept | DocumentServiceCreditsLowerBound | FLOAT |  | Lowest achieved value in the tier (inclusive). |
| ATR105 | DocumentServiceCredits | Concept | DocumentServiceCreditsUpperBound | FLOAT |  | Highest achieved value in the tier (exclusive). |
| ATR102 | DocumentServiceLevels | Concept | DocumentServiceLevelsChronicFailureThreshold | TEXT |  | Number of failures in a number of periods that gives a right to terminate. |
| ATR099 | DocumentServiceLevels | Concept | DocumentServiceLevelsClaimWindowDays | INTEGER |  | Days after the failure within which a credit must be claimed. |
| ATR100 | DocumentServiceLevels | Concept | DocumentServiceLevelsCreditCapPercent | FLOAT |  | Maximum total credit as a percentage of the fee for the period. |
| ATR101 | DocumentServiceLevels | Concept | DocumentServiceLevelsCreditsSoleRemedy | BOOLEAN |  | True when credits are the customer's sole and exclusive remedy for the failure. |
| ATR103 | DocumentServiceLevels | Concept | DocumentServiceLevelsEarnBackAvailable | BOOLEAN |  | True when the provider may earn back credits by over-performance. |
| ATR098 | DocumentServiceLevels | Concept | DocumentServiceLevelsExclusions | LONGTEXT |  | Events excluded from measurement, e.g. scheduled maintenance. |
| ATR097 | DocumentServiceLevels | Concept | DocumentServiceLevelsMeasurementBasis | LOOKUP | LKP023 | How the metric is computed. |
| ATR096 | DocumentServiceLevels | Concept | DocumentServiceLevelsMeasurementPeriod | LOOKUP | LKP050 | The period over which performance is measured. |
| ATR091 | DocumentServiceLevels | Concept | DocumentServiceLevelsMetricType | LOOKUP | LKP021 | What the service level measures. |
| ATR092 | DocumentServiceLevels | Concept | DocumentServiceLevelsObjectiveType | LOOKUP | LKP022 | Quantitative objective or qualitative commitment. |
| ATR093 | DocumentServiceLevels | Concept | DocumentServiceLevelsScope | TEXT |  | What the commitment covers, e.g. 'region, multi-zone deployment'. |
| ATR095 | DocumentServiceLevels | Concept | DocumentServiceLevelsTargetUnit | TEXT |  | Unit of the target, e.g. percent, minutes, hours. |
| ATR094 | DocumentServiceLevels | Concept | DocumentServiceLevelsTargetValue | FLOAT |  | The committed target, e.g. 99.95. |
| ATR086 | DocumentServices | Concept | DocumentServicesBillingFrequency | LOOKUP | LKP050 | How often the service is invoiced. |
| ATR084 | DocumentServices | Concept | DocumentServicesCurrency | LOOKUP | DLT000000072 | Currency of the unit price. |
| ATR080 | DocumentServices | Concept | DocumentServicesDeploymentModel | LOOKUP | LKP018 | Cloud deployment model of the service. |
| ATR078 | DocumentServices | Concept | DocumentServicesDescription | LONGTEXT |  | What the service does, as described in the document. |
| ATR089 | DocumentServices | Concept | DocumentServicesEndDate | DATE |  | Date the service line ends. |
| ATR079 | DocumentServices | Concept | DocumentServicesIctServiceType | LOOKUP | LKP017 | Type of ICT service per the DORA register taxonomy. |
| ATR081 | DocumentServices | Concept | DocumentServicesLicenceMetric | LOOKUP | LKP019 | The unit the service is licensed or consumed against. |
| ATR087 | DocumentServices | Concept | DocumentServicesOverageRate | CURRENCY |  | Charge per unit of use beyond the contracted quantity. |
| ATR085 | DocumentServices | Concept | DocumentServicesPricingModel | LOOKUP | LKP020 | How charges for the service are calculated. |
| ATR077 | DocumentServices | Concept | DocumentServicesProviderServiceCode | TEXT |  | The provider's product or SKU code for the service. |
| ATR082 | DocumentServices | Concept | DocumentServicesQuantity | FLOAT |  | Quantity of the metric contracted. |
| ATR076 | DocumentServices | Concept | DocumentServicesServiceName | TEXT |  | The name of the service as the document states it. |
| ATR088 | DocumentServices | Concept | DocumentServicesStartDate | DATE |  | Date the service line starts. |
| ATR090 | DocumentServices | Concept | DocumentServicesSupportsCriticalFunction | BOOLEAN |  | True when the customer has assessed the service as supporting a critical or important function, which brings DORA Art 30(3) provisions into play. |
| ATR083 | DocumentServices | Concept | DocumentServicesUnitPrice | CURRENCY |  | Price per unit of the metric. |
| ATR149 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsFlowDownRequired | BOOLEAN |  | True when the provider must flow the document's obligations down to subcontractors. |
| ATR146 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsNoticeDays | INTEGER |  | Days of notice of a new or replacement subcontractor. |
| ATR147 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsObjectionDays | INTEGER |  | Days within which the customer may object. |
| ATR145 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsPermission | LOOKUP | LKP036 | Whether and on what consent subcontracting is allowed. |
| ATR150 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsProviderRemainsResponsible | BOOLEAN |  | True when the provider stays fully responsible for subcontracted services. |
| ATR148 | DocumentSubcontractingTerms | Concept | DocumentSubcontractingTermsTerminationOnObjection | BOOLEAN |  | True when the customer may terminate if a change goes ahead despite objection. |
| ATR205 | DocumentSupersession | Relationship | DocumentSupersessionReason | LOOKUP | LKP043 | Why the successor supersedes the predecessor. |
| ATR056 | DocumentTerminationRights | Concept | DocumentTerminationRightsCureDays | INTEGER |  | Period the other side has to remedy a breach before the right arises. |
| ATR057 | DocumentTerminationRights | Concept | DocumentTerminationRightsDayBasis | LOOKUP | LKP010 | Whether the notice and cure periods count calendar or business days. |
| ATR058 | DocumentTerminationRights | Concept | DocumentTerminationRightsFeePayable | BOOLEAN |  | True when exercising the right triggers a termination fee. |
| ATR055 | DocumentTerminationRights | Concept | DocumentTerminationRightsNoticeDays | INTEGER |  | Notice period for exercising the right. |
| ATR059 | DocumentTerminationRights | Concept | DocumentTerminationRightsPrepaidFeesRefunded | BOOLEAN |  | True when prepaid fees for the remaining term are refunded on exercise. |
| ATR053 | DocumentTerminationRights | Concept | DocumentTerminationRightsSide | LOOKUP | LKP009 | The side of the agreement that holds the right. |
| ATR054 | DocumentTerminationRights | Concept | DocumentTerminationRightsTrigger | LOOKUP | LKP015 | The ground on which the right arises. |
| ATR006 | DocumentVersions | Concept | DocumentVersionsEffectiveDate | DATE |  | The date from which the document states it takes effect. |
| ATR005 | DocumentVersions | Concept | DocumentVersionsExecutionDate | DATE |  | The date the last required signature was applied, making the document fully executed. Derived from the signing times on the signing relationship. |
| ATR004 | DocumentVersions | Concept | DocumentVersionsExecutionStatus | LOOKUP | LKP002 | How far the document has been executed. |
| ATR210 | DocumentVersions | Concept | DocumentVersionsIsAuthoritative | BOOLEAN |  | True when this is the Version approved for operational use. |
| ATR211 | DocumentVersions | Concept | DocumentVersionsIsLegallyEffective | BOOLEAN |  | Derived from execution, effective dates and supersession. |
| ATR014 | DocumentVersions | Concept | DocumentVersionsPublicationDate | DATE |  | The date the publisher states this version was published or last amended. |
| ATR208 | DocumentVersions | Concept | DocumentVersionsSequence | INTEGER |  | Order of the Version within the Document. |
| ATR209 | DocumentVersions | Concept | DocumentVersionsState | LOOKUP | DocumentVersionStates | Draft, redline, agreed form, executed, published, withdrawn or superseded. |
| ATR013 | DocumentVersions | Concept | DocumentVersionsVersionLabel | TEXT |  | The version or edition the publisher gives the document, e.g. 'November 2025' or 'v3.2'. |
| ATR193 | LegalEntityDataProcessing | Relationship | LegalEntityDataProcessingDataSubjectCategories | LONGTEXT |  | Categories of data subjects. |
| ATR192 | LegalEntityDataProcessing | Relationship | LegalEntityDataProcessingPersonalDataTypes | LONGTEXT |  | Types of personal data processed. |
| ATR191 | LegalEntityDataProcessing | Relationship | LegalEntityDataProcessingPurposes | LONGTEXT |  | Purposes of the processing. |
| ATR194 | LegalEntityDataProcessing | Relationship | LegalEntityDataProcessingSccModule | LOOKUP | LKP034 | Module of the standard contractual clauses used, where transfers occur. |
| ATR190 | LegalEntityDataProcessing | Relationship | LegalEntityDataProcessingSubjectMatter | LONGTEXT |  | Subject matter and nature of the processing. |
| ATR184 | LegalEntityServiceProcurement | Relationship | LegalEntityServiceProcurementReferenceName | TEXT |  | The name the document uses for the customer entity. |
| ATR183 | LegalEntityServiceProvision | Relationship | LegalEntityServiceProvisionReferenceName | TEXT |  | The name the document uses for the provider, e.g. 'Supplier' or 'AWS'. |
| ATR188 | LegalEntitySubcontracting | Relationship | LegalEntitySubcontractingProcessesPersonalData | BOOLEAN |  | True when the subcontractor processes personal data (a sub-processor). |
| ATR185 | LegalEntitySubcontracting | Relationship | LegalEntitySubcontractingRank | INTEGER |  | Place in the supply chain: 2 for a subcontractor of the direct provider, 3 for its subcontractor, and so on (the direct provider is rank 1). |
| ATR186 | LegalEntitySubcontracting | Relationship | LegalEntitySubcontractingRecipientProvider | MASTERID |  | Master ID of the legal entity to which this subcontractor provides the subcontracted service (the next link up the chain). |
| ATR189 | LegalEntitySubcontracting | Relationship | LegalEntitySubcontractingServiceCountry | LOOKUP | DLT000000071 | Country from which the subcontractor performs the services. |
| ATR187 | LegalEntitySubcontracting | Relationship | LegalEntitySubcontractingServicesPerformed | LONGTEXT |  | What the subcontractor performs. |
| ATR272 | LegalEntitySupplierActions | Concept | LegalEntitySupplierActionsActionType | LOOKUP | LegalEntitySupplierActionTypes | Whether the item is an open risk, open issue, renewal action or executive escalation. |
| ATR273 | LegalEntitySupplierActions | Concept | LegalEntitySupplierActionsDescription | LONGTEXT |  | The action, issue, risk or escalation to be tracked. |
| ATR276 | LegalEntitySupplierActions | Concept | LegalEntitySupplierActionsDueDate | DATE |  | The date by which the item should be resolved or completed. |
| ATR275 | LegalEntitySupplierActions | Concept | LegalEntitySupplierActionsOwnerPersonReference | IDENTIFIER |  | Reference to the Person accountable for the item. |
| ATR274 | LegalEntitySupplierActions | Concept | LegalEntitySupplierActionsStatus | LOOKUP | ActionStatuses | The current status of the tracked item. |
| ATR254 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsAssessmentDate | DATE |  | The effective date of the supplier compliance assessment. |
| ATR259 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsBCPDRTested | BOOLEAN |  | Whether the supplier's business-continuity or disaster-recovery arrangements have been tested. |
| ATR258 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsCyberInsuranceStatus | LOOKUP | AssuranceStatuses | The supplier's cyber-insurance status. |
| ATR257 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsISO27001Status | LOOKUP | AssuranceStatuses | The supplier's ISO 27001 certification status. |
| ATR260 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsPrivacyReviewDate | DATE |  | The date of the supplier's latest privacy review. |
| ATR255 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsSOC1Status | LOOKUP | AssuranceStatuses | The supplier's SOC 1 assurance status. |
| ATR256 | LegalEntitySupplierComplianceAssessments | Concept | LegalEntitySupplierComplianceAssessmentsSOC2Status | LOOKUP | AssuranceStatuses | The supplier's SOC 2 assurance status. |
| ATR289 | LegalEntitySupplierCorporateRelationships | Concept | LegalEntitySupplierCorporateRelationshipsEndDate | DATE |  | The date on which the corporate relationship ended, when applicable. |
| ATR286 | LegalEntitySupplierCorporateRelationships | Concept | LegalEntitySupplierCorporateRelationshipsRelatedLegalEntityReference | IDENTIFIER |  | Reference to the related Legal Entity, such as the supplier's parent company. |
| ATR287 | LegalEntitySupplierCorporateRelationships | Concept | LegalEntitySupplierCorporateRelationshipsRelationshipType | LOOKUP | LegalEntityCorporateRelationshipTypes | The corporate relationship type, such as parent, subsidiary or affiliate. |
| ATR288 | LegalEntitySupplierCorporateRelationships | Concept | LegalEntitySupplierCorporateRelationshipsStartDate | DATE |  | The date from which the corporate relationship applies. |
| ATR248 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsAnnualRevenue | DECIMAL |  | The supplier's reported annual revenue. |
| ATR247 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsAssessmentDate | DATE |  | The effective date of the supplier financial assessment. |
| ATR252 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsCreditRating | TEXT |  | The supplier's reported external or internal credit rating. |
| ATR253 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsFinancialRiskRating | LOOKUP | LegalEntitySupplierRiskRatings | The assessed financial risk of the supplier. |
| ATR251 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsProfitability | LOOKUP | LegalEntitySupplierProfitabilityStatuses | The assessed profitability of the supplier. |
| ATR249 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsRevenueCurrency | LOOKUP | Currencies | The currency of reported annual revenue. |
| ATR250 | LegalEntitySupplierFinancialAssessments | Concept | LegalEntitySupplierFinancialAssessmentsRevenueTrend | LOOKUP | LegalEntitySupplierRevenueTrends | The assessed direction of supplier revenue. |
| ATR261 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceAsOfDate | DATE |  | The date as of which the supplier intelligence applies. |
| ATR265 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceIndustryEvents | LONGTEXT |  | Industry events material to the supplier relationship. |
| ATR262 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceKeyCompetitors | LONGTEXT |  | Key competitors identified for the supplier. |
| ATR264 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceLeadershipChanges | LONGTEXT |  | Material supplier leadership changes. |
| ATR263 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceRecentAcquisitions | LONGTEXT |  | Recent acquisitions involving the supplier. |
| ATR266 | LegalEntitySupplierIntelligence | Concept | LegalEntitySupplierIntelligenceRegulatoryImpacts | LONGTEXT |  | Regulatory changes or events that may affect the supplier relationship. |
| ATR241 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsAssessmentDate | DATE |  | The effective date of the supplier performance assessment. |
| ATR242 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsAvailabilityResult | DECIMAL |  | The consolidated availability result for the supplier and assessment period. |
| ATR244 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsCustomerSatisfaction | DECIMAL |  | The customer-satisfaction result for the supplier and assessment period. |
| ATR243 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsIncidentResponseResult | DECIMAL |  | The consolidated incident-response result for the supplier and assessment period. |
| ATR246 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsOverallHealthScore | DECIMAL |  | The overall supplier health score for the assessment period. |
| ATR245 | LegalEntitySupplierPerformanceAssessments | Concept | LegalEntitySupplierPerformanceAssessmentsQBRScore | DECIMAL |  | The consolidated QBR score for the supplier and assessment period. |
| ATR225 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileAsOfDate | DATE |  | The date as of which the supplier profile information applies. |
| ATR219 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileCategory | LOOKUP | LegalEntitySupplierCategories | The category used to segment and manage the supplier. |
| ATR218 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileDisplayName | TEXT |  | The supplier name used in vendor-management reporting. |
| ATR223 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileEmployeeCount | INTEGER |  | The supplier's reported employee count as of the profile date. |
| ATR221 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileHeadquarters | TEXT |  | The supplier's reported headquarters location. |
| ATR224 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileOwnershipType | LOOKUP | LegalEntitySupplierOwnershipTypes | Whether the supplier is public, private or another ownership type. |
| ATR217 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileSupplierID | TEXT |  | The supplier identifier used by the vendor-management organization. |
| ATR220 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileWebsite | URL |  | The supplier's primary website. |
| ATR222 | LegalEntitySupplierProfile | Concept | LegalEntitySupplierProfileYearFounded | INTEGER |  | The year the supplier was founded. |
| ATR280 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsActual | DECIMAL |  | The actual value for the performance indicator. |
| ATR285 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsComments | LONGTEXT |  | Commentary supporting the performance result. |
| ATR278 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsKPI | LOOKUP | LegalEntitySupplierQBRKPIs | The supplier-review performance indicator. |
| ATR284 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsOwnerPersonReference | IDENTIFIER |  | Reference to the Person accountable for the performance indicator. |
| ATR277 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsReviewDate | DATE |  | The date or period of the supplier review. |
| ATR282 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsScore | DECIMAL |  | The normalized score for the performance indicator. |
| ATR279 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsTarget | DECIMAL |  | The target value for the performance indicator. |
| ATR283 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsWeightedScore | DECIMAL |  | The performance-indicator score adjusted by its assigned weight. |
| ATR281 | LegalEntitySupplierQBRMetrics | Concept | LegalEntitySupplierQBRMetricsWeightPercent | DECIMAL |  | The percentage weight assigned to the performance indicator. |
| ATR235 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsAssessmentDate | DATE |  | The effective date of the supplier risk assessment. |
| ATR236 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsCriticalityTier | LOOKUP | LegalEntitySupplierCriticalityTiers | The supplier's criticality tier at the assessment date. |
| ATR240 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsFourthPartyDependencies | LONGTEXT |  | Material fourth-party dependencies identified for the supplier. |
| ATR238 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsInherentRiskRating | LOOKUP | LegalEntitySupplierRiskRatings | The supplier risk before controls or mitigation. |
| ATR239 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsResidualRiskRating | LOOKUP | LegalEntitySupplierRiskRatings | The supplier risk remaining after controls and mitigation. |
| ATR237 | LegalEntitySupplierRiskAssessments | Concept | LegalEntitySupplierRiskAssessmentsRiskTier | LOOKUP | LegalEntitySupplierRiskTiers | The supplier's overall risk tier at the assessment date. |
| ATR232 | LegalEntitySupplierServices | Concept | LegalEntitySupplierServicesBusinessCapability | TEXT |  | The business capability supported by the product or service. |
| ATR234 | LegalEntitySupplierServices | Concept | LegalEntitySupplierServicesDataShared | LONGTEXT |  | Data shared with or received from the supplier for the product or service. |
| ATR233 | LegalEntitySupplierServices | Concept | LegalEntitySupplierServicesIntegration | LONGTEXT |  | A key integration involving the supplier product or service. |
| ATR230 | LegalEntitySupplierServices | Concept | LegalEntitySupplierServicesPrimaryService | BOOLEAN |  | Whether this is the supplier's primary service for the organization. |
| ATR231 | LegalEntitySupplierServices | Concept | LegalEntitySupplierServicesProductOrService | TEXT |  | A product or service provided by the supplier. |
| ATR229 | LegalEntitySupplierStakeholders | Concept | LegalEntitySupplierStakeholdersEndDate | DATE |  | The date the responsibility ended, when applicable. |
| ATR227 | LegalEntitySupplierStakeholders | Concept | LegalEntitySupplierStakeholdersPersonReference | IDENTIFIER |  | Reference to the Person assigned the supplier responsibility. |
| ATR226 | LegalEntitySupplierStakeholders | Concept | LegalEntitySupplierStakeholdersRole | LOOKUP | LegalEntitySupplierStakeholderRoles | The person's role for the supplier, such as business owner, vendor manager, procurement owner, contract owner or executive sponsor. |
| ATR228 | LegalEntitySupplierStakeholders | Concept | LegalEntitySupplierStakeholdersStartDate | DATE |  | The date the responsibility started. |
| ATR267 | LegalEntitySupplierStrategicAssessments | Concept | LegalEntitySupplierStrategicAssessmentsAssessmentDate | DATE |  | The effective date of the strategic assessment. |
| ATR270 | LegalEntitySupplierStrategicAssessments | Concept | LegalEntitySupplierStrategicAssessmentsInnovationContribution | LOOKUP | LegalEntitySupplierInnovationContributionLevels | The supplier's assessed contribution to innovation. |
| ATR271 | LegalEntitySupplierStrategicAssessments | Concept | LegalEntitySupplierStrategicAssessmentsRecommendation | LONGTEXT |  | The current management recommendation for the supplier. |
| ATR268 | LegalEntitySupplierStrategicAssessments | Concept | LegalEntitySupplierStrategicAssessmentsStrategicImportance | LOOKUP | LegalEntitySupplierStrategicImportanceLevels | The supplier's assessed strategic importance. |
| ATR269 | LegalEntitySupplierStrategicAssessments | Concept | LegalEntitySupplierStrategicAssessmentsSwitchingComplexity | LOOKUP | LegalEntitySupplierSwitchingComplexityLevels | The assessed complexity of replacing the supplier. |
| ATR199 | PersonDocumentSigning | Relationship | PersonDocumentSigningAssuranceLevel | LOOKUP | LKP048 | Legal assurance level of an electronic signature. |
| ATR196 | PersonDocumentSigning | Relationship | PersonDocumentSigningCapacity | TEXT |  | The capacity or title in which the person signed, e.g. 'Chief Procurement Officer'. |
| ATR197 | PersonDocumentSigning | Relationship | PersonDocumentSigningOnBehalfOf | MASTERID |  | Master ID of the legal entity for which the person signed. |
| ATR200 | PersonDocumentSigning | Relationship | PersonDocumentSigningPadesLevel | LOOKUP | LKP049 | PAdES baseline level of the PDF signature. |
| ATR198 | PersonDocumentSigning | Relationship | PersonDocumentSigningSignatureMethod | LOOKUP | LKP047 | How the signature was applied. |
| ATR195 | PersonDocumentSigning | Relationship | PersonDocumentSigningSignedDateTime | DATETIME |  | When the signature was applied. |
