# CPG Manufacturing Operations — Data Design Document

## About This Document

Supplied text not available.

## Version

|  |  |
|---|---|
| Domain | CPG Manufacturing Operations |
| Document date | 24 September 2026 |
| Package reference | cpg-bdd |
| Method version | 1.0 |
| Edition | lite |

## Table of Contents

- [1 Introduction](#1-introduction)
  - [1.1 About M&A Operating System](#11-about-ma-operating-system)
    - [M&A Operating System — AI & Data Advisory Practice](#ma-operating-system--ai--data-advisory-practice)
    - [Find Out More](#find-out-more)
  - [1.2 About the MAOS Practical Data Modelling Approach](#12-about-the-maos-practical-data-modelling-approach)
    - [About the M&A Operating System Practical Data Modelling Approach](#about-the-ma-operating-system-practical-data-modelling-approach)
    - [The Five-Step Process](#the-five-step-process)
  - [1.3 Summary of Findings](#13-summary-of-findings)
- [2 Scope](#2-scope)
  - [2.1 The business](#21-the-business)
  - [2.2 In scope](#22-in-scope)
  - [2.3 Out of scope](#23-out-of-scope)
  - [2.4 Shared with other models](#24-shared-with-other-models)
  - [2.5 Assumptions](#25-assumptions)
  - [2.6 Open questions](#26-open-questions)
- [3 Business Requirements](#3-business-requirements)
- [4 Data Requirements](#4-data-requirements)
- [5 Data Model](#5-data-model)
  - [5.1 Subject Domains](#51-subject-domains)
  - [5.2 Canonical Roles](#52-canonical-roles)
  - [5.3 Role–Verb–Role Relationships](#53-roleverbrole-relationships)
  - [5.4 Concepts](#54-concepts)
  - [5.5 Lookups and Values](#55-lookups-and-values)
  - [5.6 Diagrams](#56-diagrams)
    - [5.6.1 Domains Data Model](#561-domains-data-model)
    - [5.6.2 Roles Data Model](#562-roles-data-model)
    - [5.6.3 Concept Models by Domain](#563-concept-models-by-domain)
- [10 Outstanding Decisions](#10-outstanding-decisions)
- [11 Approval](#11-approval)
- [Appendix A — Sources](#appendix-a--sources)
- [Appendix E — Business Test Cases](#appendix-e--business-test-cases)

**What this edition leaves out.** This is the lite edition, written for the business owner and the data steward reviewing the design. The full edition adds *Source Validation*, *Existing Model Findings*, *Conformance to DDA Standards*, *Exceptions*, *DDA Domain Definitions*, *Standards*, *Subject Domain Proposals* and the *Data Dictionary* of every attribute. Nothing here is abridged — whole sections are left out, never part of a table. Ask for the full edition to review any of them; the Data Governance Committee approves on the full edition.

## 1 Introduction

### 1.1 About M&A Operating System

#### M&A Operating System — AI & Data Advisory Practice

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

#### Find Out More

To learn more about how M&A Operating System can help your organization turn data into measurable business outcomes, visit [maoperatingsystem.com](https://www.maoperatingsystem.com).

For a direct conversation about your data, analytics, or AI priorities, contact [cdao-advisory@maoperatingsystem.com](mailto:cdao-advisory@maoperatingsystem.com).

### 1.2 About the MAOS Practical Data Modelling Approach

#### About the M&A Operating System Practical Data Modelling Approach

The **M&A Operating System Practical Data Modelling Approach** is our proprietary, business-led methodology for translating business outcomes and challenges into data requirements and approved logical data models.

We engage business stakeholders and data-consuming groups to understand what they expect data services to make possible. Their needs are captured as plain-English business requirements, then translated through a controlled, traceable sequence of analysis and design activities. The methodology deliberately avoids overly technical terminology and modelling techniques, presenting the information in a business-readable, plain-English form. The resulting data modelling document follows the same sequence, allowing business stakeholders and data practitioners to understand, challenge, and approve the design.

#### The Five-Step Process

##### Step 1 — Gather and Approve Business Requirements

We identify the outcomes stakeholders expect, the challenges they need to solve, and the business activities that data services must support. These are documented as plain-English requirements and approved as the scope and source of knowledge for the design.

##### Step 2 — Identify Actors, Objects, and Roles

Using **Subject-Based Data Modelling**, we identify the actors, roles, and objects in the business lifecycle and map them to domains representing the immutable subjects of the data. Domains describe the enduring people, organizations, things, places, and other subjects the business needs to understand—not the specific reason they appear in a single process.

Actors and objects are aligned to their underlying mastered subjects. Roles describe the capacity in which a subject participates in a relationship, process, or context. The same subject can perform several roles without being modelled repeatedly.

##### Step 3 — Identify Relationships

We identify the relationships between actors and objects and express them as clear business verbs—such as owns, manages, supplies, purchases, or is party to. This makes their meaning understandable and reviewable by business and data stakeholders.

##### Step 4 — Identify Lifecycle Events

We identify the events that actors, roles, and objects pass through as they live their natural lives and interact within business processes. These events include when an object is created, changed, activated, transferred, or retired; a subject assumes or ceases a role; or a relationship is established, modified, or ended. This determines what data must be captured at each stage.

##### Step 5 — Design Logical Data Models

The approved requirements, subjects, roles, relationships, and lifecycle events form the logical data model, documented through four connected components:

- **Data Domains** — governed groupings representing the immutable subjects of the data
- **Data Concepts** — the unique logical elements that make up the data known and recorded about each subject
- **Data Relationships** — the business connections between concepts, including the roles they perform
- **Data Attributes** — the individual data elements that describe each concept or relationship

Each component remains traceable to the requirement that established its need. The completed document provides the shared record business stakeholders and data practitioners use to review and approve the data requirements and model design.

### 1.3 Summary of Findings

The model covers the making of consumer packaged goods across five subgroups, in the organisation's own factories and at outside manufacturers. It reuses five DDA domains and proposes five more, and the chain of what goes into what stops at anything bought in, where the supplier's declaration takes over.

|  | Count |
|---|---|
| Business requirements | 69 |
| Data requirements | 36 |
| Subject domains | 5 in DDA · 5 new |
| Canonical roles | 70 |
| Relationships | 38 |
| Concepts | 66 |
| Lookups | 9 |
| Business test cases | 38 pass · 3 with a limit or a gap |
| Sources | 40 |

Status: **published with accepted limits**, as a reference model.

## 2 Scope

### 2.1 The business

A manufacturer of consumer packaged goods. It buys materials, makes and tests product, and releases it for despatch, through its own factories and through outside manufacturers.

Subgroups covered, equally: Food and beverage, Household and cleaning products, Personal care and cosmetics, Pet care, Beauty.

### 2.2 In scope

| ID | In scope |
|---|---|
| SCI001 | Buying materials, and deciding which suppliers may supply them |
| SCI002 | Defining products — what they are made from and what they must be |
| SCI003 | Defining how products are made — the steps, the settings and the recipes |
| SCI004 | The layout of each factory and the machines in it |
| SCI005 | Making product, and what each batch actually used and produced |
| SCI006 | Testing, recording problems, putting them right, and releasing product |
| SCI007 | Tracing any batch back to its ingredients and forward to where it went |
| SCI008 | Stock held at the organisation's own sites |
| SCI009 | Product made or packed by outside manufacturers |

### 2.3 Out of scope

| ID | Out of scope | Belongs to |
|---|---|---|
| SCO001 | Trade spending, promotions and pricing with retailers | The commercial model |
| SCO002 | What happens on the shelf in store | The commercial model |
| SCO003 | Market share and sales data bought from research firms | The commercial model |
| SCO004 | Marketing, campaigns and advertising | The digital marketing model |
| SCO005 | Accounts, ledgers and statutory reporting | The finance model |
| SCO006 | Research and development before a product is formally defined | Not modelled |

### 2.4 Shared with other models

| ID | Object | DDA |
|---|---|---|
| SCS001 | People | [DMD000000001](https://datadesign.maoperatingsystem.com/domains/DMD000000001) |
| SCS002 | Legal entities | [DMD000000012](https://datadesign.maoperatingsystem.com/domains/DMD000000012) |
| SCS003 | Documents | [DMD000000016](https://datadesign.maoperatingsystem.com/domains/DMD000000016) |
| SCS004 | Events | [DMD000000020](https://datadesign.maoperatingsystem.com/domains/DMD000000020) |
| SCS005 | Transactions | [DMD000000022](https://datadesign.maoperatingsystem.com/domains/DMD000000022) |

### 2.5 Assumptions

| ID | Assumption |
|---|---|
| SCA001 | The factory, laboratory, quality and maintenance systems already in place stay in place. This model holds what they record; it does not replace them. |
| SCA002 | Material held by a supplier or outside manufacturer is theirs. It becomes the organisation's on receipt, and the organisation holds no stock at any party it does not operate. |
| SCA003 | Something bought as an ingredient or part may be another company's finished product. What it is made from is theirs and may not be known here. |
| SCA004 | This is research-only work. No business owner has reviewed the requirements. |

### 2.6 Open questions

| ID | Question |
|---|---|
| SCQ001 | Is finished output identified individually, or only by batch? The model supports both; how much of Instances is used depends on the answer. |
| SCQ002 | What proportion of output is made by outside manufacturers? Where it is most of it, the organisation holds little production record of its own. |
| SCQ003 | State transitions could not be read from the platform, so the change package carries no preconditions. |

## 3 Business Requirements

Each states something true of the business, in words a business owner can agree or disagree with. The cases that show each one is met are in Appendix E, under the same requirement ID.

| ID | Category | Business requirement | Owner | Subgroup | Sources |
|---|---|---|---|---|---|
| <a id="req070"></a>REQ070 | Cost | What a product costs to make is built up from what went into it and what was done to it, and expected and actual cost differ. | Finance lead |  | [SRC014](https://www.fabrico.io/de/blog/non-conformance-report/) · [SRC018](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) |
| <a id="req033"></a>REQ033 | Equipment | A plant is organised into areas, lines and units, and work happens at each level. | Plant manager |  | [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) · [SRC004](https://www.fabrico.io/blog/isa-88/) |
| <a id="req034"></a>REQ034 | Equipment | A place on a line and the machine standing in it are different things, and machines are replaced. | Maintenance lead |  | [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) · [SRC004](https://www.fabrico.io/blog/isa-88/) |
| <a id="req035"></a>REQ035 | Equipment | A machine has a repair history, a record of how it fails and a working life that follow it wherever it goes. | Maintenance lead |  | [SRC018](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) · [SRC016](https://oxmaint.com/industries/manufacturing-plant/manufacturing-execution-system-maintenance-integration-mes) |
| <a id="req036"></a>REQ036 | Equipment | Some equipment matters more than others — because it stops the line, costs more to repair, or its failure is a safety issue. | Maintenance lead |  | [SRC018](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) |
| <a id="req037"></a>REQ037 | Equipment | A stoppage is recorded by production as lost output and by maintenance as work, and both must agree it was one stoppage. | Plant manager |  | [SRC016](https://oxmaint.com/industries/manufacturing-plant/manufacturing-execution-system-maintenance-integration-mes) |
| <a id="req038"></a>REQ038 | Equipment | Why a line stopped matters as much as that it stopped, and the reasons must be recorded consistently. | Plant manager |  | [SRC017](https://oxmaint.com/industries/steel-plant/oee-data-accuracy-best-practices) · [SRC018](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) |
| <a id="req039"></a>REQ039 | Equipment | Maintenance is planned, prompted by a condition, or done after a failure, and these are different kinds of work. | Maintenance lead |  | [SRC016](https://oxmaint.com/industries/manufacturing-plant/manufacturing-execution-system-maintenance-integration-mes) · [SRC018](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) |
| <a id="req068"></a>REQ068 | Identity | Two records may turn out to describe the same material, supplier or place. | Data steward |  | [SRC005](https://sgsystemsglobal.com/?p=15659) |
| <a id="req069"></a>REQ069 | Identity | An identifier issued by an outside authority is the strongest evidence of what something is. | Data steward |  | [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) · [SRC011](https://support.famoussoftware.com/article/fsma-204-general-summary) |
| <a id="req001"></a>REQ001 | Material | Everything the organisation buys, makes or sells is something it holds, counts and can run out of — ingredients, packaging, part-made goods and finished goods. | Supply chain lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC039](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) |
| <a id="req002"></a>REQ002 | Material | A product is made from a defined set of inputs in defined quantities, and that definition changes over time. | Technical lead |  | [SRC002](https://en.wikipedia.org/wiki/ISA-88) · [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC008](https://www.ibm.com/topics/mes-system) |
| <a id="req003"></a>REQ003 | Material | An input may itself be made from other inputs, to any depth, before anything is finished. | Technical lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC006](https://gevernova.com/software/blog/mes-traceability-genealogy) |
| <a id="req004"></a>REQ004 | Material | Using an input means using all of it as it is defined. What goes into an input cannot be adjusted by whoever uses it; needing it different means needing a different input. | Technical lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) |
| <a id="req005"></a>REQ005 | Material | The same input goes into many different products, and a product may be sold as it is and also used inside another. | Technical lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC006](https://gevernova.com/software/blog/mes-traceability-genealogy) |
| <a id="req006"></a>REQ006 | Material | What a recipe says should go in and what a batch actually used differ, and the difference matters. | Plant manager |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req007"></a>REQ007 | Material | An approved alternative may be used in place of a specified input, and which one was used on a batch must be known. | Technical lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req008"></a>REQ008 | Material | A material may be bought from several approved suppliers, and approval may lapse or be suspended. | Procurement lead |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) · [SRC029](https://ukpetfood.org/asset/14810E67%2DFA8C%2D48E8%2D924792E5213FFF43) |
| <a id="req009"></a>REQ009 | Material | A material arrives with the supplier's statement of what it is, and the organisation may or may not check it. | Quality manager |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) · [SRC039](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) |
| <a id="req010"></a>REQ010 | Material | Something bought as an ingredient or part may be another company's finished product, and what it is made from may not be known. | Technical lead |  | [SRC023](https://prod.ryder.com/en-us/insights/blogs/logistics/turnkey-vs-tolling) · [SRC024](https://prod.ryder.com/en-us/logistics/co-packaging/contract-manufacturing) |
| <a id="req011"></a>REQ011 | Material | Properties of an input carry through to what is made from it — allergens and other hazards, certifications, origin, and the date by which it must be used. | Quality manager |  | [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) · [SRC035](https://www.hoganlovells.com/en/publications/fda-releases-draft-compliance-policy-guide-for-major-food-allergen-labeling-and-cross-contact) · [SRC007](https://www.cleverence.com/amp/articles/business-blogs/how-to-batch-tracking-for-manufacturing-7284/) |
| <a id="req012"></a>REQ012 | Material | Food allergens must be declared on a product by the food they come from, including those that arrive inside another ingredient. | Quality manager | Food and beverage | [SRC034](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-555250-statement-policy-labeling-and-preventing-cross-contact-common-food-allergens) · [SRC035](https://www.hoganlovells.com/en/publications/fda-releases-draft-compliance-policy-guide-for-major-food-allergen-labeling-and-cross-contact) · [SRC008](https://www.ibm.com/topics/mes-system) |
| <a id="req013"></a>REQ013 | Material | Household cleaning products must disclose each ingredient and how much of it there is, and some may be withheld as confidential. | Regulatory lead | Household and cleaning products | [SRC025](https://www.dwt.com/blogs/energy--environmental-law-blog/2019/11/california-cleaning-products-right-to-know-act) · [SRC026](https://extapps.dec.ny.gov/docs/materials_minerals_pdf/cpidbmps.pdf) |
| <a id="req014"></a>REQ014 | Material | The hazard rules a product must follow depend on what kind of product it is; food allergen rules do not apply to pet food, cosmetics or household cleaners. | Regulatory lead |  | [SRC036](https://www.thefdalawblog.com/2022/12/fda-issues-two-guidance-documents-on-food-allergen-labeling-requirements/) · [SRC019](https://www.registrarcorp.com/blog/cosmetics/iso-22716/iso22716-batch-traceability/) · [SRC025](https://www.dwt.com/blogs/energy--environmental-law-blog/2019/11/california-cleaning-products-right-to-know-act) · [SRC028](https://www.foodengineeringmag.com/articles/99611-managing-pet-food-ingredients) |
| <a id="req015"></a>REQ015 | Material | The shortest-lived input limits how long the finished product lasts. | Quality manager |  | [SRC007](https://www.cleverence.com/amp/articles/business-blogs/how-to-batch-tracking-for-manufacturing-7284/) · [SRC039](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) |
| <a id="req016"></a>REQ016 | Material | A batch may be split or combined for handling, and every part stays traceable to where it came from. | Supply chain lead |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC007](https://www.cleverence.com/amp/articles/business-blogs/how-to-batch-tracking-for-manufacturing-7284/) |
| <a id="req017"></a>REQ017 | Material | Ingredients, part-made goods and finished goods are each held at places, and each is counted separately. | Supply chain lead |  | [SRC039](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) · [SRC005](https://sgsystemsglobal.com/?p=15659) |
| <a id="req018"></a>REQ018 | Material | Stock at one place may be available, on hold or rejected, and these are separate quantities rather than one quantity with a label. | Quality manager |  | [SRC040](https://sgsystemsglobal.com/traceability/) · [SRC014](https://www.fabrico.io/de/blog/non-conformance-report/) |
| <a id="req060"></a>REQ060 | Outside manufacture | Product may be made or packed by an outside manufacturer, who buys the materials and delivers finished product to the organisation's specification. | Procurement lead |  | [SRC023](https://prod.ryder.com/en-us/insights/blogs/logistics/turnkey-vs-tolling) · [SRC024](https://prod.ryder.com/en-us/logistics/co-packaging/contract-manufacturing) |
| <a id="req061"></a>REQ061 | Outside manufacture | What the organisation buys becomes its own when it arrives; what a supplier or outside manufacturer holds before then is theirs. | Finance lead |  | [SRC023](https://prod.ryder.com/en-us/insights/blogs/logistics/turnkey-vs-tolling) · [SRC024](https://prod.ryder.com/en-us/logistics/co-packaging/contract-manufacturing) |
| <a id="req062"></a>REQ062 | Outside manufacture | Outside manufacturers are held to the same good practice as the organisation's own plants, and their records must be available when needed. | Quality manager |  | [SRC022](https://sgsystemsglobal.com/?p=16831) |
| <a id="req063"></a>REQ063 | Outside manufacture | How far back a product can be traced depends on the supplier's own records once it is outside the organisation's sight. | Quality manager |  | [SRC009](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-proposed-rule-food-traceability) · [SRC011](https://support.famoussoftware.com/article/fsma-204-general-summary) |
| <a id="req064"></a>REQ064 | People | People are qualified to do particular work, and qualifications expire. | Plant manager |  | [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) · [SRC022](https://sgsystemsglobal.com/?p=16831) |
| <a id="req065"></a>REQ065 | Place | A site, a warehouse and a storage place are all places, and they sit inside one another. | Supply chain lead |  | [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) · [SRC039](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) |
| <a id="req066"></a>REQ066 | Place | Where something is stored affects how long it lasts and whether it stays fit to use. | Quality manager |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) |
| <a id="req067"></a>REQ067 | Place | A place may be identified differently by the organisation, a supplier and a regulator. | Data steward |  | [SRC011](https://support.famoussoftware.com/article/fsma-204-general-summary) |
| <a id="req025"></a>REQ025 | Process | Making a product is a sequence of steps, and the order matters as much as the ingredients. | Technical lead |  | [SRC002](https://en.wikipedia.org/wiki/ISA-88) · [SRC003](https://sgsystemsglobal.com/?p=16813) |
| <a id="req026"></a>REQ026 | Process | A step needs particular equipment, particular people and particular materials. | Plant manager |  | [SRC002](https://en.wikipedia.org/wiki/ISA-88) · [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) |
| <a id="req027"></a>REQ027 | Process | The same step is used in making many different products. | Technical lead |  | [SRC003](https://sgsystemsglobal.com/?p=16813) · [SRC004](https://www.fabrico.io/blog/isa-88/) |
| <a id="req028"></a>REQ028 | Process | A step has settings — a temperature, a time, a speed — and the values differ by product and by line. | Technical lead |  | [SRC003](https://sgsystemsglobal.com/?p=16813) · [SRC004](https://www.fabrico.io/blog/isa-88/) |
| <a id="req029"></a>REQ029 | Process | A formulation is written once and made at several sites on several lines, and what is carried out differs at each. | Technical lead |  | [SRC002](https://en.wikipedia.org/wiki/ISA-88) · [SRC003](https://sgsystemsglobal.com/?p=16813) |
| <a id="req030"></a>REQ030 | Process | The instructions issued for one batch are a specific thing, separate from the formulation they came from. | Plant manager |  | [SRC003](https://sgsystemsglobal.com/?p=16813) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req031"></a>REQ031 | Process | The order in which products run on a line matters, because what ran before can contaminate what runs next. | Quality manager | Food and beverage | [SRC034](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-555250-statement-policy-labeling-and-preventing-cross-contact-common-food-allergens) |
| <a id="req032"></a>REQ032 | Process | Changing a line from one product to another takes time and may need cleaning, and both are part of the cost of making. | Plant manager |  | [SRC034](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-555250-statement-policy-labeling-and-preventing-cross-contact-common-food-allergens) · [SRC017](https://oxmaint.com/industries/steel-plant/oee-data-accuracy-best-practices) |
| <a id="req019"></a>REQ019 | Product identity | The same thing is sold in several sizes and pack formats, related to each other but made and counted separately. | Commercial lead |  | [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) · [SRC031](https://www.gs1nz.org/assets/Resources/Services/GS1NZ_Fact-sheet-gtin-allocation-rules.-V2.pdf) |
| <a id="req020"></a>REQ020 | Product identity | Some changes make a product a different thing — a change to its declared ingredients, net content, certification or pack count — and others do not. | Regulatory lead |  | [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) · [SRC031](https://www.gs1nz.org/assets/Resources/Services/GS1NZ_Fact-sheet-gtin-allocation-rules.-V2.pdf) |
| <a id="req021"></a>REQ021 | Product identity | What a product is made from changes over time while it remains the same product. | Technical lead |  | [SRC030](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) · [SRC002](https://en.wikipedia.org/wiki/ISA-88) |
| <a id="req022"></a>REQ022 | Product identity | What was actually made is a fact about the batch; what should have been made is a fact about the definition. | Quality manager |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req023"></a>REQ023 | Product identity | Some things are identified individually and some only by the batch they came from, and one product may contain both. | Quality manager |  | [SRC007](https://www.cleverence.com/amp/articles/business-blogs/how-to-batch-tracking-for-manufacturing-7284/) · [SRC037](https://www.linxglobal.com/en/solutions/coding-types/gs1/) |
| <a id="req024"></a>REQ024 | Product identity | A pack may carry its own serial number as well as its batch, and retailers increasingly expect to read it, though no law requires it. | Commercial lead |  | [SRC037](https://www.linxglobal.com/en/solutions/coding-types/gs1/) · [SRC038](https://www.qrstuff.com/feeds/blog/gs1-sunrise-2027) |
| <a id="req040"></a>REQ040 | Production | Making something is instructed, carried out and recorded, and the three may differ. | Plant manager |  | [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) · [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC021](https://fda.gov/media/86366/download) · [SRC027](https://www.canr.msu.edu/news/fsma-legal-ramifications-of-cgmps-are-important-to-pet-food-safety) |
| <a id="req041"></a>REQ041 | Production | Who carried out each step of a batch, and whether they were qualified to, must be recoverable. | Plant manager |  | [SRC006](https://gevernova.com/software/blog/mes-traceability-genealogy) · [SRC001](https://reference.opcfoundation.org/specs/OPC-10030/7) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req042"></a>REQ042 | Production | Goods move between plants, warehouses and storage places, and each movement has a time and a place. | Supply chain lead |  | [SRC009](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-proposed-rule-food-traceability) · [SRC040](https://sgsystemsglobal.com/traceability/) |
| <a id="req044"></a>REQ044 | Quality | A material or product must meet a stated specification, and what it must be changes over time. | Quality manager |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) · [SRC012](https://simplerqms.com/non-conformance/) |
| <a id="req045"></a>REQ045 | Quality | Meeting a specification is shown by testing, and a test has a method as well as a result. | Quality manager |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) · [SRC022](https://sgsystemsglobal.com/?p=16831) |
| <a id="req046"></a>REQ046 | Quality | A departure from a procedure and a failure against a specification are different things, and both must be recorded. | Quality manager |  | [SRC012](https://simplerqms.com/non-conformance/) · [SRC013](https://gmpinsiders.com/deviation-management-process/) |
| <a id="req047"></a>REQ047 | Quality | Material that fails must be held back, a decision made about it, and that decision made by someone with the authority to make it. | Quality manager |  | [SRC014](https://www.fabrico.io/de/blog/non-conformance-report/) · [SRC013](https://gmpinsiders.com/deviation-management-process/) |
| <a id="req048"></a>REQ048 | Quality | Every departure from procedure must be investigated, with conclusions and follow-up recorded. | Quality manager |  | [SRC015](https://www.pharmaceutical-technology.com/?p=1983) · [SRC013](https://gmpinsiders.com/deviation-management-process/) |
| <a id="req049"></a>REQ049 | Quality | A significant or recurring problem needs its cause found, action taken, and the action shown to have worked before it is closed. | Quality manager |  | [SRC014](https://www.fabrico.io/de/blog/non-conformance-report/) · [SRC013](https://gmpinsiders.com/deviation-management-process/) |
| <a id="req050"></a>REQ050 | Quality | Output is not available to sell until someone releases it, and release is a decision someone makes. | Quality manager |  | [SRC005](https://sgsystemsglobal.com/?p=15659) · [SRC003](https://sgsystemsglobal.com/?p=16813) |
| <a id="req051"></a>REQ051 | Quality | When a batch is implicated in a food safety issue, the records of what went into it and where it went must be produced within twenty-four hours. | Quality manager | Food and beverage | [SRC009](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-proposed-rule-food-traceability) · [SRC010](https://foodbusiness.ces.ncsu.edu/news/fda-fsma-204-food-traceability-rule/) |
| <a id="req052"></a>REQ052 | Quality | Traceability records must be kept for two years. | Quality manager | Food and beverage | [SRC011](https://support.famoussoftware.com/article/fsma-204-general-summary) |
| <a id="req053"></a>REQ053 | Quality | A lot code is assigned when a product is first packed or transformed, and must be carried at every later movement. | Quality manager | Food and beverage | [SRC011](https://support.famoussoftware.com/article/fsma-204-general-summary) · [SRC009](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-proposed-rule-food-traceability) |
| <a id="req054"></a>REQ054 | Quality | A complaint may concern a specific batch, and that link is what connects experience of the product to how it was made. | Quality manager |  | [SRC022](https://sgsystemsglobal.com/?p=16831) · [SRC005](https://sgsystemsglobal.com/?p=15659) |
| <a id="req055"></a>REQ055 | Quality | Some records must be signed, and a signature must show who signed, what, when and what the signature meant. | Compliance officer |  | [SRC032](https://sgsystemsglobal.com/glossary/21-cfr-part-11-electronic-records-signatures/) · [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req056"></a>REQ056 | Quality | Once recorded, an entry stays visible and unaltered; a correction is a new entry, not an edit. | Compliance officer |  | [SRC032](https://sgsystemsglobal.com/glossary/21-cfr-part-11-electronic-records-signatures/) |
| <a id="req057"></a>REQ057 | Quality | Some steps must be checked by a second qualified person or by approved equipment. | Quality manager |  | [SRC033](https://casrai.org/dictionary/term/electronic-batch-record-ebr) |
| <a id="req058"></a>REQ058 | Supplier | A supplier is assessed before being used and reassessed afterwards. | Procurement lead |  | [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) · [SRC029](https://ukpetfood.org/asset/14810E67%2DFA8C%2D48E8%2D924792E5213FFF43) |
| <a id="req059"></a>REQ059 | Supplier | A problem with a supplier is raised with them formally and their response followed up. | Procurement lead |  | [SRC014](https://www.fabrico.io/de/blog/non-conformance-report/) · [SRC020](https://www.registrarcorp.com/iso-22716-raw-materials/) |

## 4 Data Requirements

| ID | Must record | Must answer | As at | Must prevent | Business Requirements | Prevented by |
|---|---|---|---|---|---|---|
| DRQ001 | Every recipe line: the product made, the input, and how much of the input goes into one of the product<br>The version of the recipe each line belongs to | What goes into this product, and how much of each input ends up in one finished unit? | both | A product that contains itself, however many steps away<br>A recipe read from lines belonging to two different versions | [REQ002](#req002) · [REQ003](#req003) · [REQ005](#req005) | composition — [REL001](#53-roleverbrole-relationships)<br>parent-cardinality — [SBJ015](#54-concepts) |
| DRQ002 | The same recipe lines, read from the input upwards | Which finished products contain this ingredient, by any route? | current | — | [REQ003](#req003) · [REQ005](#req005) | — |
| DRQ003 | Use of an input as a whole, never of what lies inside it | Which products use this intermediate, and are any using a variant of it that should be its own product? | current | Adjusting what goes into an input from inside the product that uses it | [REQ004](#req004) | composition — [REL001](#53-roleverbrole-relationships) |
| DRQ004 | The quantity the recipe specified for each input<br>The quantity each batch actually used | How much more or less of each input did this batch use than the recipe specified? | as-at | — | [REQ006](#req006) · [REQ022](#req022) | — |
| DRQ005 | Which input actually filled each place in the recipe on each batch<br>Approved alternatives and the conditions for using them | Which batches used an alternative input, and for which ingredient? | as-at | An alternative used without approval | [REQ007](#req007) | mandatory-attribute — ATR042 |
| DRQ006 | Each supplier's approval for each material, with the dates it held<br>Each assessment of a supplier, its scope and how long it is valid | Was this supplier approved for this material on the day it was received? | as-at | An approval treated as current after it lapsed | [REQ008](#req008) · [REQ058](#req058) | dates — [REL003](#53-roleverbrole-relationships) |
| DRQ007 | What a supplier's document states about a batch, who issued it, and whether the organisation checked it | Which of this batch's stated properties were tested here, and which were taken on the supplier's word? | current | A supplier's claim reported as though it were the organisation's own test | [REQ009](#req009) | mandatory-attribute — ATR014 |
| DRQ008 | Which inputs are bought in finished, with contents the organisation does not know | Which products depend on a bought-in ingredient whose contents we rely on the supplier to declare? | current | — | [REQ010](#req010) · [REQ063](#req063) | — |
| DRQ009 | The allergens, other hazards, certifications and origin of each input, and which rules apply to each kind of product | What allergens, hazards and certifications does this product carry, and from which inputs? | both | A product declared free of something one of its inputs contains | [REQ011](#req011) · [REQ012](#req012) · [REQ014](#req014) | composition — [REL001](#53-roleverbrole-relationships) |
| DRQ010 | Each ingredient of a household product, how much of it there is, and whether it is withheld as confidential | What must be disclosed for this household product, and what is withheld? | current | — | [REQ013](#req013) | — |
| DRQ011 | The use-by date of each batch, and the inputs that set it | What is the latest date this finished batch can be used, given what went into it? | current | — | [REQ015](#req015) | — |
| DRQ012 | Every split and every combination of batches, with the quantities of each part | Which batches came from this one, and which batches made up this combined one? | current | A split that produces a quantity with no batch it came from | [REQ016](#req016) | relationship-cardinality — [REL001](#53-roleverbrole-relationships) |
| DRQ013 | How much of each item is held, in what condition, at which place, at what time | How much of this material is available, on hold, or rejected at each site right now? | both | Stock on hold counted as available | [REQ001](#req001) · [REQ017](#req017) · [REQ018](#req018) | parent-cardinality — [SBJ048](#54-concepts) |
| DRQ014 | Each size and pack as its own product, related to its family<br>Each change to a product, and whether it made a new product or a new version, and why | Which pack sizes of this product exist, and did this change create a new product or a new version? | as-at | — | [REQ019](#req019) · [REQ020](#req020) | — |
| DRQ015 | The versions of each recipe, when each took effect, and which version each batch was made to | What recipe was this batch made to, and what was it meant to contain at the time? | as-at | — | [REQ021](#req021) · [REQ022](#req022) | — |
| DRQ016 | Each individually identified unit, the product it is a unit of, and which unit or batch filled each part of it | What exactly is inside this individual unit, and which batch did each part come from? | as-at | A unit recorded with a part its definition does not call for | [REQ023](#req023) · [REQ024](#req024) | relationship-cardinality — [REL015](#53-roleverbrole-relationships) |
| DRQ017 | The steps of each method in order, what each step needs, and its settings for each product on each line | What steps, equipment, qualifications and settings does making this product need on this line? | current | — | [REQ025](#req025) · [REQ026](#req026) · [REQ027](#req027) · [REQ028](#req028) | — |
| DRQ018 | The four levels of each recipe, and which level each came from | Which instructions were issued for this batch, and which formulation did they come from? | as-at | — | [REQ029](#req029) · [REQ030](#req030) | — |
| DRQ019 | The rules about what may run after what on each line, and why<br>Each changeover and each clean, with how long it took | What ran on this line just before this batch, and was the line cleaned in between? | as-at | A product free of an allergen run straight after one containing it, with no clean between | [REQ031](#req031) · [REQ032](#req032) | mandatory-attribute — ATR058 |
| DRQ020 | Each place in the plant and what it sits within<br>Which machine stood in each place, from when to when | Which machine was in this place on the day this batch was made? | as-at | — | [REQ033](#req033) · [REQ034](#req034) | — |
| DRQ021 | Each machine's failures and how it failed, its repairs, its readings, and how much it matters | Which machines cause the most unplanned stoppage, and how do they fail? | both | — | [REQ035](#req035) · [REQ036](#req036) · [REQ039](#req039) | — |
| DRQ022 | One record of each stoppage — start, end, and reason from a set list — with the lost output and the repair both tied to it | How long did this line stop, why, and what did maintenance do about it? | as-at | One stoppage recorded twice<br>A stoppage with no reason | [REQ037](#req037) · [REQ038](#req038) | relationship-cardinality — [REL031](#53-roleverbrole-relationships)<br>lookup — [LKP006](#55-lookups-and-values) |
| DRQ023 | What each step of a batch was told to do, what it did, what resulted, who did it, and whether they were qualified at the time | Who carried out each step of this batch, and were they qualified on that day? | as-at | Work by someone not qualified going unnoticed | [REQ040](#req040) · [REQ041](#req041) · [REQ064](#req064) | dates — [REL021](#53-roleverbrole-relationships) |
| DRQ024 | Each movement of goods — from where, to where, when, how much, which batch | Where has this batch been, and where is it now? | both | — | [REQ042](#req042) · [REQ065](#req065) | — |
| DRQ025 | Each version of a specification, and each test with its method, sample, sampling plan and result | Did this batch meet the specification in force when it was made, and by what test? | as-at | — | [REQ044](#req044) · [REQ045](#req045) | — |
| DRQ026 | Departures from procedure against the batch run, and failures against specification against the batch made — separately, each with how serious it is and how it was contained | What went wrong on this batch — a procedure not followed, the product out of specification, or both? | current | The two being recorded as one | [REQ046](#req046) · [REQ048](#req048) | platform capability |
| DRQ027 | Each hold, the decision taken, the reason, and who approved it | What was decided about this failed material, why, and by whom? | current | A decision with no named approver | [REQ047](#req047) | mandatory-attribute — ATR010 |
| DRQ028 | For each corrective action: the cause, what was done, the check that it worked, and when it was closed | Which corrective actions are open, and were any closed without checking they worked? | current | Closing an action before checking it worked | [REQ049](#req049) · [REQ059](#req059) | mandatory-attribute — ATR113 |
| DRQ029 | Each release — who released it, when, on what basis, and what it covered | Who released this batch, when, and on what basis? | current | Stock treated as available because a batch finished | [REQ050](#req050) | mandatory-attribute — ATR115 |
| DRQ030 | The lot code given at first packing or transformation, carried at every later movement, kept for two years | Every batch this ingredient batch went into, and everywhere those went — within twenty-four hours | current | A movement recorded without its lot code | [REQ051](#req051) · [REQ052](#req052) · [REQ053](#req053) | mandatory-attribute — ATR029 |
| DRQ031 | Each complaint, and the batch where the person can supply it | Which complaints concern this batch, and what else was made from the same inputs? | current | — | [REQ054](#req054) | — |
| DRQ032 | Each signature — who, what, when, and what it meant — each second check, and each correction as a new entry | Who signed this record, what did it mean, and has anything been corrected since? | as-at | An entry altered without a correction being recorded | [REQ055](#req055) · [REQ056](#req056) · [REQ057](#req057) | relationship-cardinality — [REL035](#53-roleverbrole-relationships) |
| DRQ033 | Which party made or packed each batch, the specification they were given, and when the goods became the organisation's | Which of our finished batches were made by an outside manufacturer, to which specification, and when did they become ours? | as-at | — | [REQ060](#req060) · [REQ061](#req061) · [REQ062](#req062) | — |
| DRQ034 | The conditions each place must keep, and any breach against the stock held there | Was this batch ever stored outside its permitted conditions? | as-at | — | [REQ066](#req066) | — |
| DRQ035 | The identifiers each place and each product carries, and who issued each | Which place or product is this, whatever identifier the supplier or regulator used? | current | — | [REQ067](#req067) · [REQ069](#req069) | — |
| DRQ036 | The expected and actual cost of each product, by element | What did this batch cost against its standard, and why? | as-at | — | [REQ070](#req070) | — |

## 5 Data Model

### 5.1 Subject Domains

The domains come first, because everything after them is said in their terms: a role is played by a domain, a relationship runs between two, a concept hangs under one.

| Domain ID | Domain | DDA | Anchor concept | Definition | Shared | Roles | Concepts |
|---|---|---|---|---|---|---|---|
| DOM003 | Documents | [DMD000000016](https://datadesign.maoperatingsystem.com/domains/DMD000000016) | Document | Documents (including Contracts, Agreements, Amendments, etc). The Documents Domain contains records that provide documentary evidence or support for business processes including Legal, Transactional, Regulatory, Identification and Commercial. | yes | [1](#52-canonical-roles) | [2](#54-concepts) |
| DOM008 | Equipment | `NEW` | EquipmentPosition | Equipment covers the places in a plant where work is performed — site, area, work centre, work unit and equipment module — what each is able to do, and the rules that constrain what may run there. Includes the plant structure as ISA-95 defines it. Excludes the machines that stand in those places, which are Instances, and the geographic places goods are held at, which are Locations. | no | [6](#52-canonical-roles) | [5](#54-concepts) |
| DOM004 | Events | [DMD000000020](https://datadesign.maoperatingsystem.com/domains/DMD000000020) | Event | Events describe meaningful events in the lifecycle of various data assets including Mergers, Births, Deaths, Stock-Splits etc. | yes | [13](#52-canonical-roles) | [18](#54-concepts) |
| DOM007 | Instances | `NEW` | Instance | Instances are individually identified physical things — a serial-numbered pack, a machine, a vessel, a tool — each made to a product definition and traceable as itself for its whole life. Includes what is fitted into each and what condition it is in. Excludes the product definition it is made to, which is a Product, and the batch it belongs to where it is not individually identified, which is a concept of Products. | no | [5](#52-canonical-roles) | [5](#54-concepts) |
| DOM002 | LegalEntities | [DMD000000012](https://datadesign.maoperatingsystem.com/domains/DMD000000012) | LegalEntity | Legal Entities (incl. Relationships, Companies, Funds, Charities, Governments, Agencies etc.). The LegalEntities Domain defines the different entities involved in business transactions, services or other processes in any capacity. | yes | [8](#52-canonical-roles) | [5](#54-concepts) |
| DOM010 | Locations | `NEW` | Location | Locations are identifiable geographic places at which things are held or handled — a site, a plant, a warehouse, a storage position within one — the conditions each must keep, and the identifiers each is known by. Includes places operated by other organisations where goods are received from or delivered to. Excludes the production structure within a site, which is Equipment. | no | [8](#52-canonical-roles) | [3](#54-concepts) |
| DOM001 | People | [DMD000000001](https://datadesign.maoperatingsystem.com/domains/DMD000000001) | Person | People (incl Family Units). The People Domain contains information about individuals. | yes | [3](#52-canonical-roles) | [4](#54-concepts) |
| DOM009 | Processes | `NEW` | ProcessSegment | Processes are the defined steps of work by which products are made — mixing, pasteurising, filling, labelling — the order they run in, the settings they run at, and the recipes that state them at each level of specificity from formulation to the instructions issued for one batch. Includes what each step requires of equipment, people and materials. Excludes what a product is made from, which is Products, and the record of a step actually being performed, which is an Event. | no | [8](#52-canonical-roles) | [7](#54-concepts) |
| DOM006 | Products | `NEW` | Product | Products are the things an organisation buys, makes or sells, at every level of processing and packing — ingredients, packaging components, part-made goods, finished packs and cases — together with what each is defined to be and what it is made from. Includes the batches in which they are made or received. Excludes the individual serial-numbered units made to a product definition, which are Instances, and the financial instruments an organisation issues or trades, which are Instruments. | no | [17](#52-canonical-roles) | [14](#54-concepts) |
| DOM005 | Transactions | [DMD000000022](https://datadesign.maoperatingsystem.com/domains/DMD000000022) | Transaction | Transactions are records of an individual trade/transaction which represents a transfer of ownership or investment usually in return for capital. | yes | [1](#52-canonical-roles) | [3](#54-concepts) |

### 5.2 Canonical Roles

One row per role. A role is canonical in its own right; the pairs it forms live in the relationships below.

| Domain | Role ID | Role | Definition | Also called | Requirements |
|---|---|---|---|---|---|
| Documents | <a id="rol067"></a>ROL067 | Declaring Document (Declaring Documents) | A document is a Declaring Document while it declares properties of a product batch, which is its Declared Batch. | — | [REQ009](#req009) · [REQ010](#req010) |
| Equipment | <a id="rol017"></a>ROL017 | Approved Position (Approved Positions) | A place in the plant is an Approved Position while it is approved for a step, which is its Approved Step. | — | [REQ026](#req026) · [REQ029](#req029) |
| Equipment | <a id="rol020"></a>ROL020 | Contained Position (Contained Positions) | A place in the plant is a Contained Position while it is within another, which is its Containing Position. | — | [REQ033](#req033) |
| Equipment | <a id="rol021"></a>ROL021 | Containing Position (Containing Positions) | A place in the plant is a Containing Position while it contains another, which is its Contained Position. | — | [REQ033](#req033) |
| Equipment | <a id="rol022"></a>ROL022 | Occupied Position (Occupied Positions) | A place in the plant is an Occupied Position while it is occupied by a machine, which is its Installed Machine. | — | [REQ034](#req034) |
| Equipment | <a id="rol047"></a>ROL047 | Running Position (Running Positions) | A place in the plant is a Running Position while a run ran at it, which is its Production Run. | — | [REQ040](#req040) · [REQ034](#req034) |
| Equipment | <a id="rol024"></a>ROL024 | Sited Position (Sited Positions) | A place in the plant is a Sited Position while it is sited at a place, which is its Housing Site. | — | [REQ033](#req033) · [REQ065](#req065) |
| Events | <a id="rol059"></a>ROL059 | Complaint (Complaints) | An occurrence is a Complaint while it reports a problem with a product batch, which is its Complained-of Batch. | — | [REQ054](#req054) |
| Events | <a id="rol051"></a>ROL051 | Consuming Run (Consuming Runs) | An occurrence is a Consuming Run while it consumed a product batch, which is its Input Batch. | — | [REQ006](#req006) · [REQ022](#req022) |
| Events | <a id="rol064"></a>ROL064 | Corrected Record (Corrected Records) | An occurrence is a Corrected Record while a correction corrects it, which is its Correction. | — | [REQ056](#req056) |
| Events | <a id="rol063"></a>ROL063 | Correction (Corrections) | An occurrence is a Correction while it corrects a record, which is its Corrected Record. | — | [REQ056](#req056) |
| Events | <a id="rol057"></a>ROL057 | Finding (Findings) | An occurrence is a Finding while it is raised against a product batch, which is its Affected Batch. | — | [REQ046](#req046) · [REQ047](#req047) |
| Events | <a id="rol049"></a>ROL049 | Performed Work (Performed Works) | An occurrence is Performed Work while it was performed by a person, who is its Performer. | — | [REQ041](#req041) · [REQ047](#req047) · [REQ050](#req050) · [REQ057](#req057) |
| Events | <a id="rol053"></a>ROL053 | Producing Run (Producing Runs) | An occurrence is a Producing Run while it produced a product batch, which is its Output Batch. | — | [REQ022](#req022) |
| Events | <a id="rol046"></a>ROL046 | Production Run (Production Runs) | An occurrence is a Production Run while it ran at a place in the plant and under a recipe, which are its Running Position and Issued Instructions. | — | [REQ040](#req040) |
| Events | <a id="rol061"></a>ROL061 | Response (Responses) | An occurrence is a Response while it responds to another occurrence, which is its Trigger. | — | [REQ049](#req049) |
| Events | <a id="rol055"></a>ROL055 | Stoppage (Stoppages) | An occurrence is a Stoppage while it stopped a machine, which is its Stopped Machine. | — | [REQ037](#req037) · [REQ038](#req038) |
| Events | <a id="rol069"></a>ROL069 | Storage Breach (Storage Breaches) | An occurrence is a Storage Breach while it exposed a product batch, which is its Exposed Batch. | — | [REQ066](#req066) |
| Events | <a id="rol065"></a>ROL065 | Supplier Finding (Supplier Findings) | An occurrence is a Supplier Finding while it is raised with an organisation, which is its Responsible Supplier. | — | [REQ059](#req059) |
| Events | <a id="rol062"></a>ROL062 | Trigger (Triggers) | An occurrence is a Trigger while it prompted another occurrence, which is its Response. | — | [REQ049](#req049) |
| Instances | <a id="rol028"></a>ROL028 | Assembled Unit (Assembled Units) | A unit is an Assembled Unit while it is built from another unit or incorporates a batch, which are its Fitted Unit and Incorporated Batch. | — | [REQ023](#req023) |
| Instances | <a id="rol029"></a>ROL029 | Fitted Unit (Fitted Units) | A unit is a Fitted Unit while it is built into another unit, which is its Assembled Unit. | — | [REQ023](#req023) |
| Instances | <a id="rol026"></a>ROL026 | Individual Unit (Individual Units) | A unit is an Individual Unit while it is a unit of a product, which is its Defining Product. | — | [REQ023](#req023) · [REQ024](#req024) |
| Instances | <a id="rol023"></a>ROL023 | Installed Machine (Installed Machines) | A machine is an Installed Machine while it occupies a place in the plant, which is its Occupied Position. | — | [REQ034](#req034) · [REQ035](#req035) |
| Instances | <a id="rol056"></a>ROL056 | Stopped Machine (Stopped Machines) | A machine is a Stopped Machine while a stoppage stopped it, which is its Stoppage. | — | [REQ035](#req035) · [REQ037](#req037) |
| LegalEntities | <a id="rol006"></a>ROL006 | Approved Supplier (Approved Suppliers) | An organisation is an Approved Supplier while it may supply a product, which is its Sourced Material. | — | [REQ008](#req008) · [REQ058](#req058) |
| LegalEntities | <a id="rol009"></a>ROL009 | Certifying Body (Certifying Bodies) | An organisation is a Certifying Body while it certifies a product or a place, which is its Certified Product or Certified Site. | — | [REQ011](#req011) |
| LegalEntities | <a id="rol038"></a>ROL038 | Employer (Employers) | An organisation is an Employer while a person works for it, who is its Employee. | — | [REQ041](#req041) |
| LegalEntities | <a id="rol011"></a>ROL011 | Outside Manufacturer (Outside Manufacturers) | An organisation is an Outside Manufacturer while it manufactures a product for this organisation, which is its Contracted Product. | — | [REQ060](#req060) · [REQ062](#req062) |
| LegalEntities | <a id="rol036"></a>ROL036 | Registering Authority (Registering Authorities) | An organisation is a Registering Authority while it registers a place, which is its Registered Place. | — | [REQ067](#req067) |
| LegalEntities | <a id="rol066"></a>ROL066 | Responsible Supplier (Responsible Suppliers) | An organisation is a Responsible Supplier while a finding is raised with it, which is its Supplier Finding. | — | [REQ059](#req059) |
| LegalEntities | <a id="rol033"></a>ROL033 | Site Operator (Site Operators) | An organisation is a Site Operator while it operates a place, which is its Operated Site. | — | [REQ060](#req060) · [REQ062](#req062) |
| LegalEntities | <a id="rol042"></a>ROL042 | Trading Party (Trading Parties) | An organisation is a Trading Party while an exchange is transacted with it, which is its Recorded Exchange. | — | [REQ061](#req061) |
| Locations | <a id="rol008"></a>ROL008 | Certified Site (Certified Sites) | A place is a Certified Site while it is certified by an organisation, which is its Certifying Body. | — | [REQ011](#req011) |
| Locations | <a id="rol031"></a>ROL031 | Contained Place (Contained Places) | A place is a Contained Place while it is within another place, which is its Containing Place. | — | [REQ065](#req065) |
| Locations | <a id="rol032"></a>ROL032 | Containing Place (Containing Places) | A place is a Containing Place while it contains another place, which is its Contained Place. | — | [REQ065](#req065) |
| Locations | <a id="rol044"></a>ROL044 | Despatching Place (Despatching Places) | A place is a Despatching Place while an exchange ships from it, which is its Recorded Exchange. | — | [REQ042](#req042) |
| Locations | <a id="rol025"></a>ROL025 | Housing Site (Housing Sites) | A place is a Housing Site while it houses a place in the plant, which is its Sited Position. | — | [REQ065](#req065) |
| Locations | <a id="rol034"></a>ROL034 | Operated Site (Operated Sites) | A place is an Operated Site while it is operated by an organisation, which is its Site Operator. | — | [REQ062](#req062) |
| Locations | <a id="rol045"></a>ROL045 | Receiving Place (Receiving Places) | A place is a Receiving Place while an exchange is delivered to it, which is its Recorded Exchange. | — | [REQ042](#req042) |
| Locations | <a id="rol035"></a>ROL035 | Registered Place (Registered Places) | A place is a Registered Place while it is registered with an organisation, which is its Registering Authority. | — | [REQ067](#req067) |
| People | <a id="rol037"></a>ROL037 | Employee (Employees) | A person is an Employee while they work for an organisation, which is their Employer. | — | [REQ041](#req041) |
| People | <a id="rol050"></a>ROL050 | Performer (Performers) | A person is a Performer while they performed an occurrence, which is their Performed Work. | — | [REQ041](#req041) · [REQ047](#req047) · [REQ050](#req050) |
| People | <a id="rol039"></a>ROL039 | Qualified Person (Qualified People) | A person is a Qualified Person while they are qualified for a step of work, which is their Qualified Work. | — | [REQ064](#req064) · [REQ041](#req041) |
| Processes | <a id="rol016"></a>ROL016 | Approved Step (Approved Steps) | A step is an Approved Step while it is approved at a place in the plant, which is its Approved Position. | — | [REQ026](#req026) · [REQ029](#req029) |
| Processes | <a id="rol018"></a>ROL018 | Derived Recipe (Derived Recipes) | A recipe is a Derived Recipe while it is derived from another recipe, which is its Source Recipe. | — | [REQ029](#req029) · [REQ030](#req030) |
| Processes | <a id="rol015"></a>ROL015 | Earlier Step (Earlier Steps) | A step is an Earlier Step while it precedes another step, which is its Later Step. | — | [REQ025](#req025) |
| Processes | <a id="rol048"></a>ROL048 | Issued Instructions (Issued Instructions) | A recipe is Issued Instructions while a run ran under it, which is its Production Run. | — | [REQ030](#req030) |
| Processes | <a id="rol014"></a>ROL014 | Later Step (Later Steps) | A step is a Later Step while it follows another step, which is its Earlier Step. | — | [REQ025](#req025) |
| Processes | <a id="rol013"></a>ROL013 | Making Method (Making Methods) | A method is a Making Method while it makes a product, which is its Routed Product. | — | [REQ025](#req025) · [REQ027](#req027) |
| Processes | <a id="rol040"></a>ROL040 | Qualified Work (Qualified Works) | A step is Qualified Work while it may be performed by a person, who is its Qualified Person. | — | [REQ064](#req064) |
| Processes | <a id="rol019"></a>ROL019 | Source Recipe (Source Recipes) | A recipe is a Source Recipe while it is the source of another recipe, which is its Derived Recipe. | — | [REQ029](#req029) |
| Products | <a id="rol058"></a>ROL058 | Affected Batch (Affected Batches) | A product batch is an Affected Batch while a finding is raised against it, which is its Finding. | — | [REQ046](#req046) |
| Products | <a id="rol007"></a>ROL007 | Certified Product (Certified Products) | A product is a Certified Product while it is certified by an organisation, which is its Certifying Body. | — | [REQ011](#req011) |
| Products | <a id="rol060"></a>ROL060 | Complained-of Batch (Complained-of Batches) | A product batch is a Complained-of Batch while a complaint reports a problem with it, which is its Complaint. | — | [REQ054](#req054) |
| Products | <a id="rol010"></a>ROL010 | Contracted Product (Contracted Products) | A product is a Contracted Product while it is manufactured by an organisation, which is its Outside Manufacturer. | — | [REQ060](#req060) |
| Products | <a id="rol068"></a>ROL068 | Declared Batch (Declared Batches) | A product batch is a Declared Batch while a document declares its properties, which is its Declaring Document. | — | [REQ009](#req009) |
| Products | <a id="rol027"></a>ROL027 | Defining Product (Defining Products) | A product is a Defining Product while individually identified units are made to it, which are its Individual Units. | — | [REQ023](#req023) |
| Products | <a id="rol070"></a>ROL070 | Exposed Batch (Exposed Batches) | A product batch is an Exposed Batch while a storage breach exposed it, which is its Storage Breach. | — | [REQ066](#req066) |
| Products | <a id="rol004"></a>ROL004 | Family (Families) | A product is a Family while it has variant products, which are its Variants. | — | [REQ019](#req019) |
| Products | <a id="rol030"></a>ROL030 | Incorporated Batch (Incorporated Batches) | A product batch is an Incorporated Batch while it is incorporated into a unit, which is its Assembled Unit. | — | [REQ023](#req023) |
| Products | <a id="rol052"></a>ROL052 | Input Batch (Input Batches) | A product batch is an Input Batch while a run consumed it, which is its Consuming Run. | — | [REQ022](#req022) · [REQ051](#req051) |
| Products | <a id="rol001"></a>ROL001 | Input Material (Input Materials) | A product is an Input Material while it is used in another product, which is its Output Product. | — | [REQ002](#req002) · [REQ003](#req003) · [REQ005](#req005) |
| Products | <a id="rol054"></a>ROL054 | Output Batch (Output Batches) | A product batch is an Output Batch while a run produced it, which is its Producing Run. | — | [REQ022](#req022) · [REQ053](#req053) |
| Products | <a id="rol002"></a>ROL002 | Output Product (Output Products) | A product is an Output Product while it is made from another product, which is its Input Material. | — | [REQ002](#req002) · [REQ004](#req004) |
| Products | <a id="rol012"></a>ROL012 | Routed Product (Routed Products) | A product is a Routed Product while it is made by a method, which is its Making Method. | — | [REQ025](#req025) |
| Products | <a id="rol005"></a>ROL005 | Sourced Material (Sourced Materials) | A product is a Sourced Material while it may be sourced from an organisation, which is its Approved Supplier. | — | [REQ008](#req008) |
| Products | <a id="rol043"></a>ROL043 | Traded Product (Traded Products) | A product is a Traded Product while an exchange concerns it, which is its Recorded Exchange. | — | [REQ042](#req042) |
| Products | <a id="rol003"></a>ROL003 | Variant (Variants) | A product is a Variant while it is a variant within a family product, which is its Family. | — | [REQ019](#req019) |
| Transactions | <a id="rol041"></a>ROL041 | Recorded Exchange (Recorded Exchanges) | An exchange is a Recorded Exchange while it is transacted with an organisation, in a place, or concerns a product — its Trading Party, Despatching or Receiving Place, and Traded Product. | — | [REQ042](#req042) · [REQ061](#req061) |

### 5.3 Role–Verb–Role Relationships

Each row reads as a sentence: source domain as source role, forward verb, destination domain as target role.

| ID | Data Req. ID | Source Domain | Source role | Forward verb | Target role | Destination Domain | Inverse verb | Forward view | Mirror view | Cardinality | Dates | DDA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <a id="rel037"></a>REL037 | DRQ007 | Documents | [ROL067](#rol067) Declaring Document | declares properties of | [ROL068](#rol068) Declared Batch | Products | is declared by | DocumentDeclaredBatches | ProductDeclaringDocuments | MANY_TO_MANY | no | `NEW` |
| <a id="rel010"></a>REL010 | DRQ020 | Equipment | [ROL020](#rol020) Contained Position | is within | [ROL021](#rol021) Containing Position | Equipment | contains | EquipmentPositionContainingPositions | EquipmentPositionContainedPositions | MANY_TO_ONE | no | `NEW` |
| <a id="rel011"></a>REL011 | DRQ020 | Equipment | [ROL022](#rol022) Occupied Position | is occupied by | [ROL023](#rol023) Installed Machine | Instances | occupies | EquipmentPositionInstalledMachines | InstanceOccupiedPositions | MANY_TO_MANY | yes | `NEW` |
| <a id="rel012"></a>REL012 | DRQ020 | Equipment | [ROL024](#rol024) Sited Position | is sited at | [ROL025](#rol025) Housing Site | Locations | houses | EquipmentPositionHousingSites | LocationSitedPositions | MANY_TO_ONE | no | `NEW` |
| <a id="rel033"></a>REL033 | DRQ031 | Events | [ROL059](#rol059) Complaint | reports a problem with | [ROL060](#rol060) Complained-of Batch | Products | is complained about in | EventComplained-ofBatches | ProductComplaints | MANY_TO_ONE | no | `NEW` |
| <a id="rel029"></a>REL029 | DRQ004 · DRQ030 | Events | [ROL051](#rol051) Consuming Run | consumed | [ROL052](#rol052) Input Batch | Products | was consumed by | EventInputBatches | ProductConsumingRuns | MANY_TO_MANY | no | `NEW` |
| <a id="rel035"></a>REL035 | DRQ032 | Events | [ROL063](#rol063) Correction | corrects | [ROL064](#rol064) Corrected Record | Events | is corrected by | EventCorrectedRecords | EventCorrections | MANY_TO_ONE | no | `NEW` |
| <a id="rel032"></a>REL032 | DRQ026 · DRQ027 | Events | [ROL057](#rol057) Finding | is raised against | [ROL058](#rol058) Affected Batch | Products | is subject of | EventAffectedBatches | ProductFindings | MANY_TO_MANY | no | `NEW` |
| <a id="rel028"></a>REL028 | DRQ023 · DRQ027 · DRQ029 | Events | [ROL049](#rol049) Performed Work | was performed by | [ROL050](#rol050) Performer | People | performed | EventPerformers | PersonPerformedWorks | MANY_TO_MANY | yes | `NEW` |
| <a id="rel030"></a>REL030 | DRQ030 | Events | [ROL053](#rol053) Producing Run | produced | [ROL054](#rol054) Output Batch | Products | was produced by | EventOutputBatches | ProductProducingRuns | MANY_TO_MANY | no | `NEW` |
| <a id="rel026"></a>REL026 | DRQ020 · DRQ023 | Events | [ROL046](#rol046) Production Run | ran at | [ROL047](#rol047) Running Position | Equipment | ran | EventRunningPositions | EquipmentPositionProductionRuns | MANY_TO_ONE | no | `NEW` |
| <a id="rel027"></a>REL027 | DRQ018 | Events | [ROL046](#rol046) Production Run | ran under | [ROL048](#rol048) Issued Instructions | Processes | governed | EventIssuedInstructions | ProcessSegmentProductionRuns | MANY_TO_ONE | no | `NEW` |
| <a id="rel034"></a>REL034 | DRQ028 | Events | [ROL061](#rol061) Response | responds to | [ROL062](#rol062) Trigger | Events | prompted | EventTriggers | EventResponses | MANY_TO_MANY | no | `NEW` |
| <a id="rel031"></a>REL031 | DRQ021 · DRQ022 | Events | [ROL055](#rol055) Stoppage | stopped | [ROL056](#rol056) Stopped Machine | Instances | was stopped in | EventStoppedMachines | InstanceStoppages | MANY_TO_ONE | no | `NEW` |
| <a id="rel038"></a>REL038 | DRQ034 | Events | [ROL069](#rol069) Storage Breach | exposed | [ROL070](#rol070) Exposed Batch | Products | was exposed in | EventExposedBatches | ProductStorageBreaches | MANY_TO_MANY | no | `NEW` |
| <a id="rel036"></a>REL036 | DRQ028 | Events | [ROL065](#rol065) Supplier Finding | is raised with | [ROL066](#rol066) Responsible Supplier | LegalEntities | received | EventResponsibleSuppliers | LegalEntitySupplierFindings | MANY_TO_ONE | yes | `NEW` |
| <a id="rel014"></a>REL014 | DRQ016 | Instances | [ROL028](#rol028) Assembled Unit | is built from | [ROL029](#rol029) Fitted Unit | Instances | is built into | InstanceFittedUnits | InstanceAssembledUnits | MANY_TO_MANY | yes | `NEW` |
| <a id="rel015"></a>REL015 | DRQ016 | Instances | [ROL028](#rol028) Assembled Unit | incorporates batch | [ROL030](#rol030) Incorporated Batch | Products | is incorporated into | InstanceIncorporatedBatches | ProductAssembledUnits | MANY_TO_MANY | no | `NEW` |
| <a id="rel013"></a>REL013 | DRQ016 | Instances | [ROL026](#rol026) Individual Unit | is a unit of | [ROL027](#rol027) Defining Product | Products | is made as | InstanceDefiningProducts | ProductIndividualUnits | MANY_TO_ONE | no | `NEW` |
| <a id="rel019"></a>REL019 | DRQ033 | LegalEntities | [ROL033](#rol033) Site Operator | operates | [ROL034](#rol034) Operated Site | Locations | is operated by | LegalEntityOperatedSites | LocationSiteOperators | MANY_TO_MANY | yes | `NEW` |
| <a id="rel017"></a>REL017 | DRQ006 | Locations | [ROL008](#rol008) Certified Site | is certified by | [ROL009](#rol009) Certifying Body | LegalEntities | certifies | LocationCertifyingBodies | LegalEntityCertifiedSites | MANY_TO_MANY | yes | `NEW` |
| <a id="rel016"></a>REL016 | DRQ024 | Locations | [ROL031](#rol031) Contained Place | is within | [ROL032](#rol032) Containing Place | Locations | contains | LocationContainingPlaces | LocationContainedPlaces | MANY_TO_ONE | no | `NEW` |
| <a id="rel018"></a>REL018 | DRQ035 | Locations | [ROL035](#rol035) Registered Place | is registered with | [ROL036](#rol036) Registering Authority | LegalEntities | registers | LocationRegisteringAuthorities | LegalEntityRegisteredPlaces | MANY_TO_MANY | yes | `NEW` |
| <a id="rel020"></a>REL020 | DRQ023 | People | [ROL037](#rol037) Employee | works for | [ROL038](#rol038) Employer | LegalEntities | employs | PersonEmployers | LegalEntityEmployees | MANY_TO_MANY | yes | `NEW` |
| <a id="rel021"></a>REL021 | DRQ023 | People | [ROL039](#rol039) Qualified Person | is qualified for | [ROL040](#rol040) Qualified Work | Processes | may be performed by | PersonQualifiedWorks | ProcessSegmentQualifiedPeople | MANY_TO_MANY | yes | `NEW` |
| <a id="rel008"></a>REL008 | DRQ017 | Processes | [ROL016](#rol016) Approved Step | is approved at | [ROL017](#rol017) Approved Position | Equipment | is approved for | ProcessSegmentApprovedPositions | EquipmentPositionApprovedSteps | MANY_TO_MANY | yes | `NEW` |
| <a id="rel009"></a>REL009 | DRQ018 | Processes | [ROL018](#rol018) Derived Recipe | is derived from | [ROL019](#rol019) Source Recipe | Processes | is the source of | ProcessSegmentSourceRecipes | ProcessSegmentDerivedRecipes | MANY_TO_ONE | yes | `NEW` |
| <a id="rel007"></a>REL007 | DRQ017 | Processes | [ROL014](#rol014) Later Step | follows | [ROL015](#rol015) Earlier Step | Processes | precedes | ProcessSegmentEarlierSteps | ProcessSegmentLaterSteps | MANY_TO_MANY | no | `NEW` |
| <a id="rel004"></a>REL004 | DRQ009 | Products | [ROL007](#rol007) Certified Product | is certified by | [ROL009](#rol009) Certifying Body | LegalEntities | certifies | ProductCertifyingBodies | LegalEntityCertifiedProducts | MANY_TO_MANY | yes | `NEW` |
| <a id="rel005"></a>REL005 | DRQ033 | Products | [ROL010](#rol010) Contracted Product | is manufactured by | [ROL011](#rol011) Outside Manufacturer | LegalEntities | manufactures | ProductOutsideManufacturers | LegalEntityContractedProducts | MANY_TO_MANY | yes | `NEW` |
| <a id="rel001"></a>REL001 | DRQ001 · DRQ002 · DRQ003 | Products | [ROL002](#rol002) Output Product | is made from | [ROL001](#rol001) Input Material | Products | is used in | ProductInputMaterials | ProductOutputProducts | MANY_TO_MANY | yes | `NEW` |
| <a id="rel006"></a>REL006 | DRQ017 | Products | [ROL012](#rol012) Routed Product | is made by | [ROL013](#rol013) Making Method | Processes | makes | ProductMakingMethods | ProcessSegmentRoutedProducts | MANY_TO_ONE | yes | `NEW` |
| <a id="rel003"></a>REL003 | DRQ006 | Products | [ROL005](#rol005) Sourced Material | may be sourced from | [ROL006](#rol006) Approved Supplier | LegalEntities | may supply | ProductApprovedSuppliers | LegalEntitySourcedMaterials | MANY_TO_MANY | yes | `NEW` |
| <a id="rel002"></a>REL002 | DRQ014 | Products | [ROL003](#rol003) Variant | is a variant within | [ROL004](#rol004) Family | Products | has variant | ProductFamilies | ProductVariants | MANY_TO_ONE | yes | `NEW` |
| <a id="rel022"></a>REL022 | DRQ033 | Transactions | [ROL041](#rol041) Recorded Exchange | is transacted with | [ROL042](#rol042) Trading Party | LegalEntities | transacts | TransactionTradingParties | LegalEntityRecordedExchanges | MANY_TO_MANY | no | `NEW` |
| <a id="rel023"></a>REL023 | DRQ024 | Transactions | [ROL041](#rol041) Recorded Exchange | concerns | [ROL043](#rol043) Traded Product | Products | is traded in | TransactionTradedProducts | ProductRecordedExchanges | MANY_TO_MANY | no | `NEW` |
| <a id="rel024"></a>REL024 | DRQ024 | Transactions | [ROL041](#rol041) Recorded Exchange | ships from | [ROL044](#rol044) Despatching Place | Locations | despatches | TransactionDespatchingPlaces | LocationRecordedExchanges | MANY_TO_ONE | no | `NEW` |
| <a id="rel025"></a>REL025 | DRQ024 | Transactions | [ROL041](#rol041) Recorded Exchange | is delivered to | [ROL045](#rol045) Receiving Place | Locations | receives | TransactionReceivingPlaces | LocationRecordedExchanges | MANY_TO_ONE | no | `NEW` |

### 5.4 Concepts

Every concept in scope, whether DDA already holds it or this model proposes it. Each definition states the grain — one record per what.

| Domain | Concept ID | Concept | DDA | Definition | Parent | Cardinality to parent | Kind | Mastery | From |
|---|---|---|---|---|---|---|---|---|---|
| Documents | <a id="sbj010"></a>SBJ010 | Document | [DMC000000142](https://datadesign.maoperatingsystem.com/concepts/DMC000000142) | One document — a certificate of analysis, a specification sheet, a safety data sheet. One record per document. | — | — | subject | ingested | DRQ007 |
| Documents | <a id="sbj011"></a>SBJ011 | DocumentDeclarations | `NEW` | One property a document states about a batch or product, and whether the organisation verified it. One record per document per property. | Document | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ007 · DRQ008 |
| Equipment | <a id="sbj031"></a>SBJ031 | EquipmentPosition | `NEW` | One place in a plant where work is performed — a site level, an area, a work centre, a work unit, an equipment module. One record per place in the plant structure. | — | — | subject | mastered | DRQ020 |
| Equipment | <a id="sbj033"></a>SBJ033 | EquipmentCapabilities | `NEW` | One thing a place is able to do, and how much of it. One record per place per capability. | EquipmentPosition | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ017 |
| Equipment | <a id="sbj035"></a>SBJ035 | EquipmentMaintenancePlans | `NEW` | One planned maintenance regime for a place, and what triggers it. One record per place per plan. | EquipmentPosition | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ021 |
| Equipment | <a id="sbj032"></a>SBJ032 | EquipmentPositionIdentifiers | `NEW` | One identifier by which a place is known, in one scheme. One record per place per scheme per identifier. | EquipmentPosition | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ020 |
| Equipment | <a id="sbj034"></a>SBJ034 | EquipmentSequencingRules | `NEW` | One constraint on what may run after what at a place, with the reason. One record per place per constraint. | EquipmentPosition | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ019 |
| Events | <a id="sbj049"></a>SBJ049 | Event | `NEW` | One thing that happened in the operation, at a time and a place. One record per occurrence. | — | — | occurrence | ingested | DRQ023 |
| Events | <a id="sbj053"></a>SBJ053 | EventBatchSplits | `NEW` | One batch divided into parts, or several combined into one. One record per split or combination. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ012 |
| Events | <a id="sbj054"></a>SBJ054 | EventChangeovers | `NEW` | One change of a place from one product to another, including any clean. One record per changeover. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ019 |
| Events | <a id="sbj064"></a>SBJ064 | EventComplaints | `NEW` | One report from outside the organisation about a product. One record per complaint. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ031 |
| Events | <a id="sbj065"></a>SBJ065 | EventCorrections | `NEW` | One correction to something already recorded, replacing it without erasing it. One record per correction. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ032 |
| Events | <a id="sbj061"></a>SBJ061 | EventCorrectiveActions | `NEW` | One response to a problem — its cause, what was done, the check that it worked, and its closure. One record per corrective action. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ028 |
| Events | <a id="sbj058"></a>SBJ058 | EventDeviations | `NEW` | One departure from a defined procedure during a run. One record per departure. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ026 |
| Events | <a id="sbj060"></a>SBJ060 | EventDispositions | `NEW` | One decision about failed material, with its reason and its approver. One record per decision. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ027 |
| Events | <a id="sbj056"></a>SBJ056 | EventMaintenanceWork | `NEW` | One piece of maintenance work — what prompted it, what was found, what was done. One record per piece of work. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ021 · DRQ022 |
| Events | <a id="sbj052"></a>SBJ052 | EventMaterialConsumptions | `NEW` | One quantity of one input batch used in one run, filling one place in the recipe. One record per run per input batch per recipe position. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ004 · DRQ005 |
| Events | <a id="sbj059"></a>SBJ059 | EventNonConformances | `NEW` | One failure of a batch or material against its specification. One record per failure. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ026 |
| Events | <a id="sbj050"></a>SBJ050 | EventProductionOrders | `NEW` | One instruction to make a quantity of a product. One record per order. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ023 |
| Events | <a id="sbj051"></a>SBJ051 | EventProductionRuns | `NEW` | One batch actually made — what was instructed, what was done, and what came out. One record per batch run. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ004 · DRQ023 |
| Events | <a id="sbj063"></a>SBJ063 | EventRecalls | `NEW` | One safety or quality incident, its scope and its resolution. One record per incident. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ030 |
| Events | <a id="sbj062"></a>SBJ062 | EventReleases | `NEW` | One act of making output available, by one person, on a stated basis. One record per release. | Event | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ029 |
| Events | <a id="sbj055"></a>SBJ055 | EventStoppages | `NEW` | One stop in production at one place — start, end, and why. One record per stoppage. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ022 |
| Events | <a id="sbj066"></a>SBJ066 | EventStorageBreaches | `NEW` | One period a place failed to keep its required conditions. One record per breach. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ034 |
| Events | <a id="sbj057"></a>SBJ057 | EventTests | `NEW` | One test against a specification — its method, its sample and its result. One record per test. | Event | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ025 |
| Instances | <a id="sbj026"></a>SBJ026 | Instance | `NEW` | One individually identified physical thing — a serialised pack or a machine — made to a product definition. One record per individually identified unit. | — | — | subject | mastered | DRQ016 · DRQ020 |
| Instances | <a id="sbj028"></a>SBJ028 | InstanceConditions | `NEW` | One reading of a unit's state — hours run, cycles, wear, calibration result. One record per unit per reading. | Instance | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ021 |
| Instances | <a id="sbj030"></a>SBJ030 | InstanceCriticalities | `NEW` | One assessment of how much a machine matters — to output, to safety, and whether a spare exists. One record per machine per assessment. | Instance | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ021 |
| Instances | <a id="sbj029"></a>SBJ029 | InstanceFailureModes | `NEW` | One way a machine characteristically fails, and what that failure causes. One record per machine per failure mode. | Instance | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ021 |
| Instances | <a id="sbj027"></a>SBJ027 | InstanceIdentifiers | `NEW` | One identifier by which a unit is individually known, in one scheme. One record per unit per scheme per identifier. | Instance | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ016 |
| LegalEntities | <a id="sbj005"></a>SBJ005 | LegalEntity | [DMC000000106](https://datadesign.maoperatingsystem.com/concepts/DMC000000106) | One organisation — a supplier, an outside manufacturer, a certifying body, or one of the organisation's own companies. One record per organisation. | — | — | subject | ingested | DRQ006 · DRQ033 |
| LegalEntities | <a id="sbj007"></a>SBJ007 | LegalEntityAddress | [DMC000000108](https://datadesign.maoperatingsystem.com/concepts/DMC000000108) | One address of an organisation. One record per organisation per address type. | LegalEntity | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ006 |
| LegalEntities | <a id="sbj008"></a>SBJ008 | LegalEntityAssessments | `NEW` | One assessment of a supplier or outside manufacturer — its scope, its result, and how long it is valid. One record per organisation per assessment. | LegalEntity | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ006 |
| LegalEntities | <a id="sbj006"></a>SBJ006 | LegalEntityIdentifiers | [DMC000000023](https://datadesign.maoperatingsystem.com/concepts/DMC000000023) | One identifier by which an organisation is known, in one scheme. One record per organisation per scheme per identifier. | LegalEntity | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ035 |
| LegalEntities | <a id="sbj009"></a>SBJ009 | LegalEntitySupplierRequests | `NEW` | One problem formally raised with a supplier, with their response and its closure. One record per request. | LegalEntity | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ028 |
| Locations | <a id="sbj043"></a>SBJ043 | Location | `NEW` | One identifiable place — a site, a plant, a warehouse, a storage position. One record per place. | — | — | subject | mastered | DRQ024 |
| Locations | <a id="sbj044"></a>SBJ044 | LocationIdentifiers | `NEW` | One identifier by which a place is known, and who issued it. One record per place per scheme per identifier. | Location | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ035 |
| Locations | <a id="sbj045"></a>SBJ045 | LocationStorageConditions | `NEW` | One condition a place must keep — temperature, humidity — with its limits. One record per place per condition. | Location | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ034 |
| People | <a id="sbj001"></a>SBJ001 | Person | [DMC000000143](https://datadesign.maoperatingsystem.com/concepts/DMC000000143) | One natural person — an operator, a technician, a supplier's contact. One record per person. | — | — | subject | mastered | DRQ023 |
| People | <a id="sbj002"></a>SBJ002 | PersonQualificationRecords | `NEW` | One qualification a person holds to perform particular work, with the basis on which it was awarded. One record per person per qualification per award. | Person | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ023 |
| People | <a id="sbj003"></a>SBJ003 | PersonShiftAssignments | `NEW` | One period a person was assigned to work at a place. One record per person per shift. | Person | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ023 |
| People | <a id="sbj004"></a>SBJ004 | PersonSignatures | `NEW` | One signature a person applied to a record — what was signed, when, and what the signature meant. One record per signature. | Person | ONE_TO_MANY_OPTIONAL | occurrence | ingested | DRQ032 |
| Processes | <a id="sbj036"></a>SBJ036 | ProcessSegment | `NEW` | One step of work, defined independently of any product — mixing, pasteurising, filling. One record per step. | — | — | subject | mastered | DRQ017 |
| Processes | <a id="sbj042"></a>SBJ042 | ProcessParameterValues | `NEW` | One value set for a setting at one recipe level, for one product at one place. One record per recipe level per setting. | ProcessRecipeLevels | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ017 · DRQ018 |
| Processes | <a id="sbj041"></a>SBJ041 | ProcessRecipeLevels | `NEW` | One statement of a routing at one level of specificity — general, site, master, or the instructions for one batch. One record per routing per level per scope. | ProcessRoutings | ONE_TO_MANY_MANDATORY | subject | mastered | DRQ018 |
| Processes | <a id="sbj038"></a>SBJ038 | ProcessParameters | `NEW` | One setting a step can be run at, with the range allowed. One record per step per setting. | ProcessSegment | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ017 |
| Processes | <a id="sbj040"></a>SBJ040 | ProcessRoutings | `NEW` | The steps, in order, that turn a product's inputs into the product. One record per routing. | ProcessSegment | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ017 |
| Processes | <a id="sbj039"></a>SBJ039 | ProcessSamplingPlans | `NEW` | One rule stating what is sampled at a step, when, how much, and against which specification. One record per step per sampling plan. | ProcessSegment | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ025 |
| Processes | <a id="sbj037"></a>SBJ037 | ProcessSegmentRequirements | `NEW` | One thing a step needs to run — a capability, a qualification, a kind of material. One record per step per requirement. | ProcessSegment | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ017 |
| Products | <a id="sbj012"></a>SBJ012 | Product | `NEW` | One thing the organisation buys, makes or sells, at one level of processing or packing. One record per product. | — | — | subject | mastered | DRQ001 · DRQ013 |
| Products | <a id="sbj016"></a>SBJ016 | ProductBatches | `NEW` | One quantity made or received as one unit of traceability, with its lot code and date. One record per product per lot code. | Product | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ012 · DRQ030 |
| Products | <a id="sbj024"></a>SBJ024 | ProductCostings | `NEW` | The expected or actual cost of a product, by element, for a period. One record per product per cost element per period. | Product | ONE_TO_MANY_OPTIONAL | subject | derived | DRQ036 |
| Products | <a id="sbj019"></a>SBJ019 | ProductDisclosures | `NEW` | One ingredient a product must disclose, how much of it there is, and whether it is withheld as confidential. One record per product per disclosed ingredient. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ010 |
| Products | <a id="sbj018"></a>SBJ018 | ProductHazards | `NEW` | One hazard a product carries — an allergen, an irritant, a classified chemical — with the basis of the declaration. One record per product per hazard. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ009 |
| Products | <a id="sbj013"></a>SBJ013 | ProductIdentifiers | `NEW` | One identifier by which a product is known, in one scheme. One record per product per scheme per identifier. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ014 · DRQ035 |
| Products | <a id="sbj025"></a>SBJ025 | ProductIdentityChanges | `NEW` | One change to a product, and whether it made a new product or a new version of what goes in. One record per product per change. | Product | ONE_TO_MANY_OPTIONAL | occurrence | mastered | DRQ014 |
| Products | <a id="sbj020"></a>SBJ020 | ProductOrigins | `NEW` | One stated country or region of origin, with the basis of the statement. One record per product per origin claim. | Product | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ009 |
| Products | <a id="sbj021"></a>SBJ021 | ProductShelfLives | `NEW` | How long a product lasts under one set of storage conditions. One record per product per storage condition. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ011 |
| Products | <a id="sbj014"></a>SBJ014 | ProductSpecifications | `NEW` | One version of what a product must be, with its limits and how conformance is checked. One record per product per specification version. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ025 |
| Products | <a id="sbj015"></a>SBJ015 | ProductStructureVersions | `NEW` | One complete statement of what goes into a product, for a site, market or period. One record per product per version. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ001 · DRQ015 |
| Products | <a id="sbj022"></a>SBJ022 | ProductSubstitutions | `NEW` | One approved alternative for an input, with the conditions for using it. One record per product per approved alternative. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ005 |
| Products | <a id="sbj023"></a>SBJ023 | ProductVariantAxes | `NEW` | One way the members of a family differ — size, format, pack count — and the values allowed. One record per family per axis. | Product | ONE_TO_MANY_OPTIONAL | subject | mastered | DRQ014 |
| Products | <a id="sbj017"></a>SBJ017 | ProductSubBatches | `NEW` | One part of a batch separated for handling, retaining its link to the batch. One record per batch per part. | ProductBatches | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ012 |
| Transactions | <a id="sbj046"></a>SBJ046 | Transaction | `NEW` | One exchange of goods of a stated kind — a purchase, a receipt, an issue to production, a transfer, a despatch. One record per exchange. | — | — | occurrence | ingested | DRQ024 · DRQ033 |
| Transactions | <a id="sbj048"></a>SBJ048 | TransactionInventoryPositions | `NEW` | One quantity of a product, in one condition, at one place, at one time. One record per product per condition per place per count. | Transaction | ONE_TO_MANY_OPTIONAL | subject | ingested | DRQ013 |
| Transactions | <a id="sbj047"></a>SBJ047 | TransactionLines | `NEW` | One line of an exchange: one product, one quantity, one batch. One record per exchange per line. | Transaction | ONE_TO_MANY_MANDATORY | occurrence | ingested | DRQ024 |

### 5.5 Lookups and Values

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP009 | UniversalUnitOfMeasure | universal | The unit a quantity is expressed in. Used wherever a quantity is recorded. | ProductBillOfMaterialsUnitOfMeasure | `NEW` | DRQ001 · DRQ004 · DRQ013 |

| Code | Name | Definition |
|---|---|---|
| KG | Kilogram | Mass in kilograms. |
| G | Gram | Mass in grams. |
| L | Litre | Volume in litres. |
| ML | Millilitre | Volume in millilitres. |
| EA | Each | A count of units. |
| CASE | Case | A count of cases. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP005 | EquipmentPositionLevelType | concept | The level of a place in the plant structure, following ISA-95. | EquipmentPositionLevel | `NEW` | DRQ020 |

| Code | Name | Definition |
|---|---|---|
| SITE | Site | One manufacturing location. |
| AREA | Area | A part of a site — processing, packing, storage. |
| PROCESSCELL | Process cell | A work centre for batch production. |
| PRODUCTIONLINE | Production line | A work centre for repetitive production. |
| STORAGEZONE | Storage zone | A work centre for holding material. |
| WORKUNIT | Work unit | One part of a work centre performing one function. |
| EQUIPMENTMODULE | Equipment module | One part of a unit performing one task. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP007 | EventDispositionsDecisionType | concept | What is done with material that failed its specification. | EventDispositionsDecision | `NEW` | DRQ027 |

| Code | Name | Definition |
|---|---|---|
| USEASIS | Use as is | Accepted despite the failure, on a stated justification. |
| REWORK | Rework | Returned to production to be brought into specification. |
| REGRADE | Regrade | Accepted against a different specification. |
| SCRAP | Scrap | Destroyed or disposed of. |
| RETURN | Return to supplier | Sent back to the party that supplied it. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP006 | EventStoppagesReasonType | concept | Why production stopped, from a governed list. | EventStoppagesReason | `NEW` | DRQ022 |

| Code | Name | Definition |
|---|---|---|
| CHANGEOVER | Changeover | Moving the line between products. |
| CLEANING | Cleaning | Scheduled cleaning or sanitation. |
| PLANNEDMAINT | Planned maintenance | Work scheduled against a plan. |
| BREAKDOWN | Breakdown | A machine ceased to perform its function. |
| MATERIALSHORT | Material shortage | An input was unavailable. |
| QUALITYHOLD | Quality hold | Stopped pending a quality decision. |
| UPSTREAM | Upstream blockage | Starved by a preceding place. |
| DOWNSTREAM | Downstream blockage | Blocked by a following place. |
| LABOUR | Labour unavailable | No qualified operator available. |
| UTILITY | Utility failure | Power, water, steam or air unavailable. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP004 | ProcessRecipeLevelsType | concept | How specific a recipe is, following ISA-88. | ProcessRecipeLevelsLevel | `NEW` | DRQ018 |

| Code | Name | Definition |
|---|---|---|
| GENERAL | General recipe | The formulation and method, naming no factory. |
| SITE | Site recipe | Adapted to the materials and constraints of one site. |
| MASTER | Master recipe | Bound to one work centre, with its settings. |
| CONTROL | Control recipe | The instructions issued for one batch. This is what runs. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP002 | ProductHazardType | concept | The kind of hazard a product carries, and therefore which declaration regime applies to it. | ProductHazardsType | `NEW` | DRQ009 |

| Code | Name | Definition |
|---|---|---|
| FOODALLERGEN | Food allergen | One of the major food allergens, declared by the food it comes from. |
| SENSITISER | Skin sensitiser | A substance that may cause a reaction on contact. |
| CLASSIFIEDCHEMICAL | Classified chemical | A substance carrying a hazard classification requiring disclosure. |
| PHYSICAL | Physical hazard | A foreign body or sharp-edge risk. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP003 | ProductIdentifiersType | concept | The scheme an identifier belongs to. | ProductIdentifiersType | `NEW` | DRQ014 · DRQ035 |

| Code | Name | Definition |
|---|---|---|
| GTIN | Trade item number | The global trade item number allocated under GS1 rules. |
| MATERIALNUMBER | Internal material number | The organisation's own number for the product. |
| SUPPLIERPART | Supplier part number | The supplier's number for what it sells. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP001 | ProductKindType | concept | What a product is to this organisation, deciding whether it may be bought, made, used or sold. A product may be more than one kind at once. | ProductKind | `NEW` | DRQ001 · DRQ013 |

| Code | Name | Definition |
|---|---|---|
| RAWMATERIAL | Raw material | An ingredient or substance that enters a formulation. |
| PACKCOMPONENT | Packaging component | A container, closure, label, case or divider. |
| INDIRECT | Indirect material | Used in production without entering the product. |
| INTERMEDIATE | Part-made good | Made and used internally; neither bought nor sold. |
| CONSUMERUNIT | Consumer unit | The unit a consumer buys. |
| CASE | Case | The unit a customer orders. |
| PALLET | Pallet | The unit that ships. |
| FAMILY | Family | Not a physical thing: the group a set of variants belongs to. |

| Lookup ID | Lookup | Scope | Definition | Used by | DDA | From |
|---|---|---|---|---|---|---|
| LKP008 | TransactionKindType | concept | What kind of exchange a transaction is. | TransactionKind | `NEW` | DRQ024 · DRQ033 |

| Code | Name | Definition |
|---|---|---|
| PURCHASE | Purchase | An order placed with a supplier. |
| RECEIPT | Receipt | Goods arriving and becoming the organisation's. |
| ISSUE | Issue to production | Material released to a run. |
| TRANSFER | Transfer | A move between the organisation's own places. |
| DESPATCH | Despatch | Goods leaving for a customer. |

### 5.6 Diagrams

Every diagram is drawn the same way: a box names the thing on its first line and qualifies it on the second, and an edge carries the verb.

#### 5.6.1 Domains Data Model

One node per subject domain, each edge carrying the roles the arrangement confers. Domains DDA holds are solid; new domains are dashed.

```mermaid
flowchart LR
  DOM001("Person<br>PEOPLE")
  DOM002("LegalEntity<br>LEGALENTITIES")
  DOM003("Document<br>DOCUMENTS")
  DOM004("Event<br>EVENTS")
  DOM005("Transaction<br>TRANSACTIONS")
  DOM006("Product<br>PRODUCTS")
  DOM007("Instance<br>INSTANCES")
  DOM008("EquipmentPosition<br>EQUIPMENT")
  DOM009("ProcessSegment<br>PROCESSES")
  DOM010("Location<br>LOCATIONS")
  DOM006 -->|"Output Product → is made from → Input Material"| DOM006
  DOM006 -->|"Variant → is a variant within → Family"| DOM006
  DOM006 -->|"Sourced Material → may be sourced from → Approved Supplier"| DOM002
  DOM006 -->|"Certified Product → is certified by → Certifying Body"| DOM002
  DOM006 -->|"Contracted Product → is manufactured by → Outside Manufacturer"| DOM002
  DOM006 -->|"Routed Product → is made by → Making Method"| DOM009
  DOM009 -->|"Later Step → follows → Earlier Step"| DOM009
  DOM009 -->|"Approved Step → is approved at → Approved Position"| DOM008
  DOM009 -->|"Derived Recipe → is derived from → Source Recipe"| DOM009
  DOM008 -->|"Contained Position → is within → Containing Position"| DOM008
  DOM008 -->|"Occupied Position → is occupied by → Installed Machine"| DOM007
  DOM008 -->|"Sited Position → is sited at → Housing Site"| DOM010
  DOM007 -->|"Individual Unit → is a unit of → Defining Product"| DOM006
  DOM007 -->|"Assembled Unit → is built from → Fitted Unit"| DOM007
  DOM007 -->|"Assembled Unit → incorporates batch → Incorporated Batch"| DOM006
  DOM010 -->|"Contained Place → is within → Containing Place"| DOM010
  DOM010 -->|"Certified Site → is certified by → Certifying Body"| DOM002
  DOM010 -->|"Registered Place → is registered with → Registering Authority"| DOM002
  DOM002 -->|"Site Operator → operates → Operated Site"| DOM010
  DOM001 -->|"Employee → works for → Employer"| DOM002
  DOM001 -->|"Qualified Person → is qualified for → Qualified Work"| DOM009
  DOM005 -->|"Recorded Exchange → is transacted with → Trading Party"| DOM002
  DOM005 -->|"Recorded Exchange → concerns → Traded Product"| DOM006
  DOM005 -->|"Recorded Exchange → ships from → Despatching Place"| DOM010
  DOM005 -->|"Recorded Exchange → is delivered to → Receiving Place"| DOM010
  DOM004 -->|"Production Run → ran at → Running Position"| DOM008
  DOM004 -->|"Production Run → ran under → Issued Instructions"| DOM009
  DOM004 -->|"Performed Work → was performed by → Performer"| DOM001
  DOM004 -->|"Consuming Run → consumed → Input Batch"| DOM006
  DOM004 -->|"Producing Run → produced → Output Batch"| DOM006
  DOM004 -->|"Stoppage → stopped → Stopped Machine"| DOM007
  DOM004 -->|"Finding → is raised against → Affected Batch"| DOM006
  DOM004 -->|"Complaint → reports a problem with → Complained-of Batch"| DOM006
  DOM004 -->|"Response → responds to → Trigger"| DOM004
  DOM004 -->|"Correction → corrects → Corrected Record"| DOM004
  DOM004 -->|"Supplier Finding → is raised with → Responsible Supplier"| DOM002
  DOM003 -->|"Declaring Document → declares properties of → Declared Batch"| DOM006
  DOM004 -->|"Storage Breach → exposed → Exposed Batch"| DOM006
  classDef indda fill:#1f3a5f,stroke:#0d1f33,stroke-width:2px,color:#fff
  classDef prop fill:#3d2b56,stroke:#241733,stroke-width:2px,color:#fff,stroke-dasharray:5 3
  class DOM001,DOM002,DOM003,DOM004,DOM005 indda
  class DOM006,DOM007,DOM008,DOM009,DOM010 prop
```

#### 5.6.2 Roles Data Model

Every role once, joined by the verbs between them, so a party can be followed from one arrangement into the next.

```mermaid
flowchart LR
  ROL001("Input Material<br>PRODUCTS")
  ROL002("Output Product<br>PRODUCTS")
  ROL003("Variant<br>PRODUCTS")
  ROL004("Family<br>PRODUCTS")
  ROL005("Sourced Material<br>PRODUCTS")
  ROL006("Approved Supplier<br>LEGALENTITIES")
  ROL007("Certified Product<br>PRODUCTS")
  ROL008("Certified Site<br>LOCATIONS")
  ROL009("Certifying Body<br>LEGALENTITIES")
  ROL010("Contracted Product<br>PRODUCTS")
  ROL011("Outside Manufacturer<br>LEGALENTITIES")
  ROL012("Routed Product<br>PRODUCTS")
  ROL013("Making Method<br>PROCESSES")
  ROL014("Later Step<br>PROCESSES")
  ROL015("Earlier Step<br>PROCESSES")
  ROL016("Approved Step<br>PROCESSES")
  ROL017("Approved Position<br>EQUIPMENT")
  ROL018("Derived Recipe<br>PROCESSES")
  ROL019("Source Recipe<br>PROCESSES")
  ROL020("Contained Position<br>EQUIPMENT")
  ROL021("Containing Position<br>EQUIPMENT")
  ROL022("Occupied Position<br>EQUIPMENT")
  ROL023("Installed Machine<br>INSTANCES")
  ROL024("Sited Position<br>EQUIPMENT")
  ROL025("Housing Site<br>LOCATIONS")
  ROL026("Individual Unit<br>INSTANCES")
  ROL027("Defining Product<br>PRODUCTS")
  ROL028("Assembled Unit<br>INSTANCES")
  ROL029("Fitted Unit<br>INSTANCES")
  ROL030("Incorporated Batch<br>PRODUCTS")
  ROL031("Contained Place<br>LOCATIONS")
  ROL032("Containing Place<br>LOCATIONS")
  ROL033("Site Operator<br>LEGALENTITIES")
  ROL034("Operated Site<br>LOCATIONS")
  ROL035("Registered Place<br>LOCATIONS")
  ROL036("Registering Authority<br>LEGALENTITIES")
  ROL037("Employee<br>PEOPLE")
  ROL038("Employer<br>LEGALENTITIES")
  ROL039("Qualified Person<br>PEOPLE")
  ROL040("Qualified Work<br>PROCESSES")
  ROL041("Recorded Exchange<br>TRANSACTIONS")
  ROL042("Trading Party<br>LEGALENTITIES")
  ROL043("Traded Product<br>PRODUCTS")
  ROL044("Despatching Place<br>LOCATIONS")
  ROL045("Receiving Place<br>LOCATIONS")
  ROL046("Production Run<br>EVENTS")
  ROL047("Running Position<br>EQUIPMENT")
  ROL048("Issued Instructions<br>PROCESSES")
  ROL049("Performed Work<br>EVENTS")
  ROL050("Performer<br>PEOPLE")
  ROL051("Consuming Run<br>EVENTS")
  ROL052("Input Batch<br>PRODUCTS")
  ROL053("Producing Run<br>EVENTS")
  ROL054("Output Batch<br>PRODUCTS")
  ROL055("Stoppage<br>EVENTS")
  ROL056("Stopped Machine<br>INSTANCES")
  ROL057("Finding<br>EVENTS")
  ROL058("Affected Batch<br>PRODUCTS")
  ROL059("Complaint<br>EVENTS")
  ROL060("Complained-of Batch<br>PRODUCTS")
  ROL061("Response<br>EVENTS")
  ROL062("Trigger<br>EVENTS")
  ROL063("Correction<br>EVENTS")
  ROL064("Corrected Record<br>EVENTS")
  ROL065("Supplier Finding<br>EVENTS")
  ROL066("Responsible Supplier<br>LEGALENTITIES")
  ROL067("Declaring Document<br>DOCUMENTS")
  ROL068("Declared Batch<br>PRODUCTS")
  ROL069("Storage Breach<br>EVENTS")
  ROL070("Exposed Batch<br>PRODUCTS")
  ROL002 -->|"is made from"| ROL001
  ROL003 -->|"is a variant within"| ROL004
  ROL005 -->|"may be sourced from"| ROL006
  ROL007 -->|"is certified by"| ROL009
  ROL010 -->|"is manufactured by"| ROL011
  ROL012 -->|"is made by"| ROL013
  ROL014 -->|"follows"| ROL015
  ROL016 -->|"is approved at"| ROL017
  ROL018 -->|"is derived from"| ROL019
  ROL020 -->|"is within"| ROL021
  ROL022 -->|"is occupied by"| ROL023
  ROL024 -->|"is sited at"| ROL025
  ROL026 -->|"is a unit of"| ROL027
  ROL028 -->|"is built from"| ROL029
  ROL028 -->|"incorporates batch"| ROL030
  ROL031 -->|"is within"| ROL032
  ROL008 -->|"is certified by"| ROL009
  ROL035 -->|"is registered with"| ROL036
  ROL033 -->|"operates"| ROL034
  ROL037 -->|"works for"| ROL038
  ROL039 -->|"is qualified for"| ROL040
  ROL041 -->|"is transacted with"| ROL042
  ROL041 -->|"concerns"| ROL043
  ROL041 -->|"ships from"| ROL044
  ROL041 -->|"is delivered to"| ROL045
  ROL046 -->|"ran at"| ROL047
  ROL046 -->|"ran under"| ROL048
  ROL049 -->|"was performed by"| ROL050
  ROL051 -->|"consumed"| ROL052
  ROL053 -->|"produced"| ROL054
  ROL055 -->|"stopped"| ROL056
  ROL057 -->|"is raised against"| ROL058
  ROL059 -->|"reports a problem with"| ROL060
  ROL061 -->|"responds to"| ROL062
  ROL063 -->|"corrects"| ROL064
  ROL065 -->|"is raised with"| ROL066
  ROL067 -->|"declares properties of"| ROL068
  ROL069 -->|"exposed"| ROL070
```

#### 5.6.3 Concept Models by Domain

**Documents**

```mermaid
flowchart LR
  DOM003A("Document<br>DOCUMENTS")
  SBJ011("DocumentDeclarations<br>DOCUMENTS")
  DOM003A -->|"ONE_TO_MANY_OPTIONAL"| SBJ011
```

**Equipment**

```mermaid
flowchart LR
  DOM008A("EquipmentPosition<br>EQUIPMENT")
  SBJ032("EquipmentPositionIdentifiers<br>EQUIPMENT")
  SBJ033("EquipmentCapabilities<br>EQUIPMENT")
  SBJ034("EquipmentSequencingRules<br>EQUIPMENT")
  SBJ035("EquipmentMaintenancePlans<br>EQUIPMENT")
  DOM008A -->|"ONE_TO_MANY_OPTIONAL"| SBJ032
  DOM008A -->|"ONE_TO_MANY_OPTIONAL"| SBJ033
  DOM008A -->|"ONE_TO_MANY_OPTIONAL"| SBJ034
  DOM008A -->|"ONE_TO_MANY_OPTIONAL"| SBJ035
```

**Events**

```mermaid
flowchart LR
  DOM004A("Event<br>EVENTS")
  SBJ050("EventProductionOrders<br>EVENTS")
  SBJ051("EventProductionRuns<br>EVENTS")
  SBJ052("EventMaterialConsumptions<br>EVENTS")
  SBJ053("EventBatchSplits<br>EVENTS")
  SBJ054("EventChangeovers<br>EVENTS")
  SBJ055("EventStoppages<br>EVENTS")
  SBJ056("EventMaintenanceWork<br>EVENTS")
  SBJ057("EventTests<br>EVENTS")
  SBJ058("EventDeviations<br>EVENTS")
  SBJ059("EventNonConformances<br>EVENTS")
  SBJ060("EventDispositions<br>EVENTS")
  SBJ061("EventCorrectiveActions<br>EVENTS")
  SBJ062("EventReleases<br>EVENTS")
  SBJ063("EventRecalls<br>EVENTS")
  SBJ064("EventComplaints<br>EVENTS")
  SBJ065("EventCorrections<br>EVENTS")
  SBJ066("EventStorageBreaches<br>EVENTS")
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ050
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ051
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ052
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ053
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ054
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ055
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ056
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ057
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ058
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ059
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ060
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ061
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ062
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ063
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ064
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ065
  DOM004A -->|"ONE_TO_MANY_OPTIONAL"| SBJ066
```

**Instances**

```mermaid
flowchart LR
  DOM007A("Instance<br>INSTANCES")
  SBJ027("InstanceIdentifiers<br>INSTANCES")
  SBJ028("InstanceConditions<br>INSTANCES")
  SBJ029("InstanceFailureModes<br>INSTANCES")
  SBJ030("InstanceCriticalities<br>INSTANCES")
  DOM007A -->|"ONE_TO_MANY_OPTIONAL"| SBJ027
  DOM007A -->|"ONE_TO_MANY_OPTIONAL"| SBJ028
  DOM007A -->|"ONE_TO_MANY_OPTIONAL"| SBJ029
  DOM007A -->|"ONE_TO_MANY_OPTIONAL"| SBJ030
```

**LegalEntities**

```mermaid
flowchart LR
  DOM002A("LegalEntity<br>LEGALENTITIES")
  SBJ006("LegalEntityIdentifiers<br>LEGALENTITIES")
  SBJ007("LegalEntityAddress<br>LEGALENTITIES")
  SBJ008("LegalEntityAssessments<br>LEGALENTITIES")
  SBJ009("LegalEntitySupplierRequests<br>LEGALENTITIES")
  DOM002A -->|"ONE_TO_MANY_OPTIONAL"| SBJ006
  DOM002A -->|"ONE_TO_MANY_OPTIONAL"| SBJ007
  DOM002A -->|"ONE_TO_MANY_OPTIONAL"| SBJ008
  DOM002A -->|"ONE_TO_MANY_OPTIONAL"| SBJ009
```

**Locations**

```mermaid
flowchart LR
  DOM010A("Location<br>LOCATIONS")
  SBJ044("LocationIdentifiers<br>LOCATIONS")
  SBJ045("LocationStorageConditions<br>LOCATIONS")
  DOM010A -->|"ONE_TO_MANY_OPTIONAL"| SBJ044
  DOM010A -->|"ONE_TO_MANY_OPTIONAL"| SBJ045
```

**People**

```mermaid
flowchart LR
  DOM001A("Person<br>PEOPLE")
  SBJ002("PersonQualificationRecords<br>PEOPLE")
  SBJ003("PersonShiftAssignments<br>PEOPLE")
  SBJ004("PersonSignatures<br>PEOPLE")
  DOM001A -->|"ONE_TO_MANY_OPTIONAL"| SBJ002
  DOM001A -->|"ONE_TO_MANY_OPTIONAL"| SBJ003
  DOM001A -->|"ONE_TO_MANY_OPTIONAL"| SBJ004
```

**Processes**

```mermaid
flowchart LR
  DOM009A("ProcessSegment<br>PROCESSES")
  SBJ037("ProcessSegmentRequirements<br>PROCESSES")
  SBJ038("ProcessParameters<br>PROCESSES")
  SBJ039("ProcessSamplingPlans<br>PROCESSES")
  SBJ040("ProcessRoutings<br>PROCESSES")
  SBJ041("ProcessRecipeLevels<br>PROCESSES")
  SBJ042("ProcessParameterValues<br>PROCESSES")
  DOM009A -->|"ONE_TO_MANY_OPTIONAL"| SBJ037
  DOM009A -->|"ONE_TO_MANY_OPTIONAL"| SBJ038
  DOM009A -->|"ONE_TO_MANY_OPTIONAL"| SBJ039
  DOM009A -->|"ONE_TO_MANY_OPTIONAL"| SBJ040
  SBJ040 -->|"ONE_TO_MANY_MANDATORY"| SBJ041
  SBJ041 -->|"ONE_TO_MANY_OPTIONAL"| SBJ042
```

**Products**

```mermaid
flowchart LR
  DOM006A("Product<br>PRODUCTS")
  SBJ013("ProductIdentifiers<br>PRODUCTS")
  SBJ014("ProductSpecifications<br>PRODUCTS")
  SBJ015("ProductStructureVersions<br>PRODUCTS")
  SBJ016("ProductBatches<br>PRODUCTS")
  SBJ017("ProductSubBatches<br>PRODUCTS")
  SBJ018("ProductHazards<br>PRODUCTS")
  SBJ019("ProductDisclosures<br>PRODUCTS")
  SBJ020("ProductOrigins<br>PRODUCTS")
  SBJ021("ProductShelfLives<br>PRODUCTS")
  SBJ022("ProductSubstitutions<br>PRODUCTS")
  SBJ023("ProductVariantAxes<br>PRODUCTS")
  SBJ024("ProductCostings<br>PRODUCTS")
  SBJ025("ProductIdentityChanges<br>PRODUCTS")
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ013
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ014
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ015
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ016
  SBJ016 -->|"ONE_TO_MANY_OPTIONAL"| SBJ017
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ018
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ019
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ020
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ021
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ022
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ023
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ024
  DOM006A -->|"ONE_TO_MANY_OPTIONAL"| SBJ025
```

**Transactions**

```mermaid
flowchart LR
  DOM005A("Transaction<br>TRANSACTIONS")
  SBJ047("TransactionLines<br>TRANSACTIONS")
  SBJ048("TransactionInventoryPositions<br>TRANSACTIONS")
  DOM005A -->|"ONE_TO_MANY_MANDATORY"| SBJ047
  DOM005A -->|"ONE_TO_MANY_OPTIONAL"| SBJ048
```

## 10 Outstanding Decisions

| ID | Decision | Options |
|---|---|---|
| DEC001 | Approve EXC001 and EXC002, or route them back. | approve · route back |
| DEC002 | Certification of the requirement set cannot pass in research-only mode. Publish as a reference model, or appoint a business owner. | publish as reference model · appoint an owner |
| DEC003 | Five domains and two anchor concepts in existing domains need the Data Governance Committee. | approve · decline |
| DEC004 | Instances takes the prefix UNT because INS is held by Instruments. | confirm UNT · reassign |
| DEC005 | Is finished output identified individually, or only by batch? (SCQ001) | individually · batch only · both |
| DEC006 | The total cost of poor quality is asked for and no artefact answers it. Bring it into scope, or state it as out of scope. | in scope · out of scope |
| DEC007 | State transitions could not be read: list_model(stateTransitions) returned "An internal error occurred". The change package therefore carries no preconditions. | retry before applying · apply without preconditions |
| DEC008 | The Events and Transactions domain definitions in DDA are written for financial services. Propose broadening them. | propose update · leave as is |

## 11 Approval

| Block | Certifies | Status |
|---|---|---|
| Business requirements | The requirement set is complete and correct | Not certified — research-only, see DEC002 |
| Data requirements | Accepted for implementation | Awaiting the exceptions carried in the full edition |
| Data Governance Committee | Five subject domains and two anchor concepts | Awaiting, on the full edition |

This edition carries the approval block for signature. The Committee approves on the full edition, which carries the conformance statement, the exceptions, the domain proposals and the change package.

## Appendix A — Sources

| ID | Title | Organisation | Type | Why included | Establishes | Cited by |
|---|---|---|---|---|---|---|
| SRC001 | [OPC 10030 ISA-95 Common Object Model — ISA-95 Base Information Model](https://reference.opcfoundation.org/specs/OPC-10030/7) | OPC Foundation | standard | The formal standard for how a factory is structured. The only source defining the levels of the plant, and the basis for keeping a place on a line separate from the machine in it. | ISA-95 sets out a role-based equipment hierarchy — enterprise, site, area, work centre, work unit, equipment module and control module — and records a person's qualifications alongside results. | 27 |
| SRC002 | [ISA-88](https://en.wikipedia.org/wiki/ISA-88) | Wikipedia | reference-model | The standard for how batch recipes are structured. It establishes the four levels of a recipe and that a recipe names the equipment it needs. | A batch procedure is an ordered set of unit procedures, operations and phases; recipes are general, site, master or control, and carry a formula, equipment requirements and a procedure. | 28 |
| SRC003 | [ISA-88 (S88) Batch Control Standard](https://sgsystemsglobal.com/?p=16813) | SG Systems Global | practitioner | A practitioner reading of ISA-88. It confirms that recipes and equipment are held apart in practice and that parameters carry limits. | S88 separates what is to be done from how equipment is driven, with parameter limits, recipe hierarchy, and batch records under electronic-record rules. | 22 |
| SRC004 | [ISA-88](https://www.fabrico.io/blog/isa-88/) | Fabrico | practitioner | Shows the recipe and the method used across several products on one tank, and that the plant structure maps onto how maintenance records machines. | The equipment model says what the plant can do and the recipe says what to do; a recipe asks for 'heat to 80 for 20 minutes' and a new product variant becomes a new recipe, not new code. | 14 |
| SRC005 | [Batch Genealogy](https://sgsystemsglobal.com/?p=15659) | SG Systems Global | practitioner | The clearest source separating what a batch should have used from what it did use. Also the main source on splitting and merging lots. | Genealogy links every raw-material lot, intermediate, step, test, packaging operation and shipping unit; the bill of materials defines expected links and the batch record the links that actually occurred, including splits and merges. | 47 |
| SRC006 | [MES Traceability and Genealogy](https://gevernova.com/software/blog/mes-traceability-genealogy) | GE Vernova | practitioner | States the questions a plant is asked in plain terms. Several data requirements are those questions. | Manufacturers need to answer which raw-material lots went into a batch, which finished products were affected, which operators and equipment were involved, and whether checks were completed. | 4 |
| SRC007 | [How to do batch tracking for manufacturing](https://www.cleverence.com/amp/articles/business-blogs/how-to-batch-tracking-for-manufacturing-7284/) | Cleverence | practitioner | The only source stating that serial and batch tracking are mixed within one operation. | Many manufacturers track some parts by serial number and bulk materials by batch; a blend of two lots must record both; returned stock keeps its batch identity and remaining shelf life. | 18 |
| SRC008 | [What is a manufacturing execution system?](https://www.ibm.com/topics/mes-system) | IBM | reference-model | A general reference placing recipes, formulation and allergen control together in food manufacturing. | Food and beverage production systems manage recipes, formulation, lot traceability and allergen control. | 2 |
| SRC009 | [FSMA Final Rule on Requirements for Additional Traceability Records for Certain Foods](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-proposed-rule-food-traceability) | US Food and Drug Administration | regulatory | The regulation setting the twenty-four-hour limit on traceability records. The primary legal source for recall. | Businesses handling listed foods must keep key data elements for critical tracking events and provide them to the FDA within 24 hours, and must share information with supply-chain partners. | 12 |
| SRC010 | [FDA FSMA 204 Food Traceability Rule](https://foodbusiness.ces.ncsu.edu/news/fda-fsma-204-food-traceability-rule/) | NC State Extension | regulatory | Gives the current compliance date, which the model must be ready for. | The FDA has proposed extending the FSMA 204 compliance date to 20 July 2028; critical tracking events include packing, shipping and receiving. | 2 |
| SRC011 | [FSMA 204 General Summary](https://support.famoussoftware.com/article/fsma-204-general-summary) | Famous Software | practitioner | States when lot codes are assigned, how long they are kept, and that places are identified by several authorities. | A traceability lot code is assigned at initial packing or transformation, linked at each tracking event, exchanged between trading partners, and kept for two years; its source may be identified by registration number, location number or web address. | 17 |
| SRC012 | [Nonconformance: Definition, Types, Causes, and Process](https://simplerqms.com/non-conformance/) | SimplerQMS | practitioner | Draws the line between a departure from procedure and a failure against specification. | A deviation is a departure from an approved procedure; a nonconformance is a failure to meet a requirement; nonconformances are classified minor, major or critical. | 8 |
| SRC013 | [Deviation Management Process in GMP](https://gmpinsiders.com/deviation-management-process/) | GMP Insiders | practitioner | Connects a departure from procedure to investigation, corrective action and the decision on the batch. | Deviations are recorded, risk-classified and investigated, lead to corrective action, and support decisions about what to do with the batch. | 10 |
| SRC014 | [Non-conformance report](https://www.fabrico.io/de/blog/non-conformance-report/) | Fabrico | practitioner | Sets out the disposition choices and that each needs approval. | Affected material is contained, a disposition decided — use as is, rework, repair, scrap or return to supplier — with approvals, root cause found for significant or repeat issues, and closure verified. | 26 |
| SRC015 | [Deviation management](https://www.pharmaceutical-technology.com/?p=1983) | Pharmaceutical Technology | practitioner | The regulatory basis for investigating every departure from procedure. | US GMP rule 21 CFR 211.192 requires a thorough investigation of any deviation, with conclusions and follow-up recorded. | 1 |
| SRC016 | [MES and CMMS integration](https://oxmaint.com/industries/manufacturing-plant/manufacturing-execution-system-maintenance-integration-mes) | OxMaint | practitioner | The source for recording a stoppage once, seen by production and maintenance alike. | The production system often knows a line stopped with a reason code while the maintenance system still shows the machine as available; connecting them makes one stoppage drive both. | 15 |
| SRC017 | [OEE data accuracy best practices](https://oxmaint.com/industries/steel-plant/oee-data-accuracy-best-practices) | OxMaint | practitioner | Establishes that stoppage reasons must come from a governed list. | Downtime reasons must be standardised into tiers; when operators pick from many vague reasons, a changeover is logged four different ways. | 7 |
| SRC018 | [Food plant production uptime](https://oxmaint.com/industries/food-manufacturing/food-plant-production-uptime-cmms-guide-2026) | OxMaint | practitioner | Food-specific evidence on critical machines and failure recording. | Equipment effectiveness is availability times performance times quality; food plants start with structured failure codes on every stoppage and focus on their most critical machines. | 19 |
| SRC019 | [ISO 22716 batch traceability](https://www.registrarcorp.com/blog/cosmetics/iso-22716/iso22716-batch-traceability/) | Registrar Corp | standard | Evidence that the traceability structures used in food also apply to cosmetics. | ISO 22716 requires documentation of every stage of cosmetic production from raw materials to distribution, and US cosmetics law now aligns with it on traceability. | 1 |
| SRC020 | [ISO 22716 and raw material management](https://www.registrarcorp.com/iso-22716-raw-materials/) | Registrar Corp | standard | The main source on qualifying suppliers and checking what arrives. | Raw materials require supplier qualification, testing against specification, documented receipt, controlled storage, and batch tracking with deviation management. | 40 |
| SRC021 | [Guidance for Industry: Cosmetic Good Manufacturing Practices](https://fda.gov/media/86366/download) | US Food and Drug Administration | regulatory | The US regulator's position on cosmetics records. | Documentation should capture every aspect of manufacturing so that problems can be traced and corrected. | 1 |
| SRC022 | [ISO 22716 — Cosmetics GMP](https://sgsystemsglobal.com/?p=16831) | SG Systems Global | standard | The only source putting outside manufacturers under the same good-practice rules as own plants. | ISO 22716 covers personnel, premises, equipment and maintenance, materials, production, quality control, contract and outsourced activities, recalls and complaints, and expects any batch to be reconstructable. | 18 |
| SRC023 | [Turnkey vs. Tolling — Which Makes Sense for Me?](https://prod.ryder.com/en-us/insights/blogs/logistics/turnkey-vs-tolling) | Ryder | practitioner | Defines the two arrangements. The scope settles on turnkey. | In tolling the brand supplies its own raw materials; in turnkey manufacturing the contract manufacturer provides them. | 7 |
| SRC024 | [Contract Manufacturing Solutions](https://prod.ryder.com/en-us/logistics/co-packaging/contract-manufacturing) | Ryder | practitioner | States who does what in turnkey manufacturing. | In turnkey contract manufacturing the manufacturer sources materials, makes, checks and packs the product; the client provides specifications and approvals. | 9 |
| SRC025 | [California Cleaning Products Right to Know Act](https://www.dwt.com/blogs/energy--environmental-law-blog/2019/11/california-cleaning-products-right-to-know-act) | Davis Wright Tremaine | regulatory | The household-products regime for ingredient disclosure — a subgroup otherwise unsourced. | Household cleaning manufacturers must disclose each ingredient, its CAS number, its function and a link to its safety data sheet; some may be withheld as confidential under a generic name. | 6 |
| SRC026 | [Cleansing Product Information Disclosure Program: Recommended Best Management Practices](https://extapps.dec.ny.gov/docs/materials_minerals_pdf/cpidbmps.pdf) | New York State Department of Environmental Conservation | regulatory | A second state regime confirming ingredient disclosure by weight for household products. | Manufacturers of household cleansing products furnish each ingredient and its content by weight; confidential business information may be withheld. | 3 |
| SRC027 | [FSMA: legal ramifications of cGMPs are important to pet food safety](https://www.canr.msu.edu/news/fsma-legal-ramifications-of-cgmps-are-important-to-pet-food-safety) | Michigan State University Extension | regulatory | The regulatory basis for pet food manufacturing — a subgroup otherwise unsourced. | Facilities making animal food, including pet food, must comply with good manufacturing practice under 21 CFR Part 507. | 1 |
| SRC028 | [Managing pet food ingredients](https://www.foodengineeringmag.com/articles/99611-managing-pet-food-ingredients) | Food Engineering | practitioner | Evidence that pet food carries the same ingredient and control structures as human food. | Pet food uses more than 500 ingredients; manufacturers identify hazards and put preventive controls such as heat treatment in place; the FDA regulates both finished pet food and its ingredients. | 1 |
| SRC029 | [Good pet food manufacturing practice](https://ukpetfood.org/asset/14810E67%2DFA8C%2D48E8%2D924792E5213FFF43) | UK Pet Food | practitioner | Industry-body evidence for supplier approval and batch records in pet food. | Responsible pet food makers run supplier approval, precise formulation, and batch records of finished product and where it went. | 4 |
| SRC030 | [The GTIN management handbook](https://www.gs1uk.org/sites/default/files/The_GTIN_management_handbook.pdf) | GS1 UK | standard | The external rule for when a change makes a new product rather than a new version. | A change to declared formulation — such as adding nuts, which introduces an allergen — net content, a certification mark or pack quantity requires a new product number at every packing level. | 26 |
| SRC031 | [GTIN allocation rules](https://www.gs1nz.org/assets/Resources/Services/GS1NZ_Fact-sheet-gtin-allocation-rules.-V2.pdf) | GS1 New Zealand | standard | Confirms the same rule and defines formulation. | Formulation is the list of ingredients or components used to create a trade item; any change to the declared net content requires a new product number. | 8 |
| SRC032 | [21 CFR Part 11](https://sgsystemsglobal.com/glossary/21-cfr-part-11-electronic-records-signatures/) | SG Systems Global | regulatory | The regulatory basis for signatures and for never altering a recorded entry. | Part 11 sets when electronic records and signatures are acceptable — identity, authority, auditability and retention — across food, cosmetics and other regulated manufacturing. | 10 |
| SRC033 | [Electronic Batch Record](https://casrai.org/dictionary/term/electronic-batch-record-ebr) | CASRAI | reference-model | Defines what a batch record must hold. | A batch record documents each step — by whom or by which equipment, when, with what materials and quantities, and with what results — including checks by a second qualified person. | 27 |
| SRC034 | [CPG Sec. 555.250 Statement of Policy for Labeling and Preventing Cross-contact of Common Food Allergens](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cpg-sec-555250-statement-policy-labeling-and-preventing-cross-contact-common-food-allergens) | US Food and Drug Administration | regulatory | The regulator's statement that the order products run in is a safety matter. | Allergens must be declared; cross-contact arises from rework, carry-over on shared equipment and production sequencing. | 9 |
| SRC035 | [FDA Releases Draft Compliance Policy Guide for Major Food Allergen Labeling and Cross-contact](https://www.hoganlovells.com/en/publications/fda-releases-draft-compliance-policy-guide-for-major-food-allergen-labeling-and-cross-contact) | Hogan Lovells | regulatory | Establishes that an allergen is declared by its source, including when it arrives inside another ingredient. | Nine major food allergens must be declared by the food they come from — whey must be declared as milk. | 6 |
| SRC036 | [FDA Issues Two Guidance Documents on Food Allergen Labeling Requirements](https://www.thefdalawblog.com/2022/12/fda-issues-two-guidance-documents-on-food-allergen-labeling-requirements/) | Hyman, Phelps & McNamara (FDA Law Blog) | regulatory | The only source stating that hazard declaration rules differ by subgroup. | Food allergen labelling rules do not apply to pet foods, animal feeds, cosmetics, drugs or household cleaning products. | 1 |
| SRC037 | [GS1 2D code printing](https://www.linxglobal.com/en/solutions/coding-types/gs1/) | Linx | standard | Evidence that individual serial numbers are becoming readable on consumer packs. | A GS1 2D code carries the product number, batch, production date, expiry date and serial number; retailers are to accept 2D codes by the end of 2027. | 8 |
| SRC038 | [GS1 Sunrise 2027](https://www.qrstuff.com/feeds/blog/gs1-sunrise-2027) | QRStuff | practitioner | Establishes that individual identification is expected commercially rather than required by law. | Sunrise 2027 is not a legal requirement, but major retailers are aligning to it, with packs carrying both codes during the transition. | 1 |
| SRC039 | [Guide to batch tracking](https://www.cleverence.com/amp/articles/business-blogs/guide-batch-tracking-5829/) | Cleverence | practitioner | The source for what is captured when material arrives and where it is kept. | At receipt, capture supplier lot, quantity, expiry and certificate reference; record exact storage locations; issue lot-tracked materials to production orders. | 26 |
| SRC040 | [Traceability — End-to-End Lot Genealogy](https://sgsystemsglobal.com/traceability/) | SG Systems Global | practitioner | Establishes that stock carries a status such as quarantined or released, separate from its identity. | Traceability links identity (product number, lot, serial), status (quarantined, released) and events (receipt, consume, transform, pack, ship, return). | 8 |

## Appendix E — Business Test Cases

One row per requirement a case reaches, so every requirement shows its own evidence.

| REQ ID | Case ID | Question | Kind | As at | Walked through | Result | Note |
|---|---|---|---|---|---|---|---|
| [REQ001](#req001) | SCN013 | How much of this material is available, on hold, or rejected at each site right now? | designed | as-at | ATR089 → SBJ012 → SBJ048 → ATR017 → ATR090 | Pass | — |
| [REQ002](#req002) | SCN001 | What goes into this product, and how much of each input ends up in one finished unit? | designed | as-at | REL001 → SBJ012 → SBJ015 → ATR001 → ATR002 | Pass | — |
| [REQ003](#req003) | SCN001 | What goes into this product, and how much of each input ends up in one finished unit? | designed | as-at | REL001 → SBJ012 → SBJ015 → ATR001 → ATR002 | Pass | — |
| [REQ003](#req003) | SCN002 | Which finished products contain this ingredient, by any route? | designed | current | REL001 | Pass | — |
| [REQ004](#req004) | SCN003 | Which products use this intermediate, and are any using a variant of it that should be its own product? | designed | current | REL001 | Pass | — |
| [REQ005](#req005) | SCN001 | What goes into this product, and how much of each input ends up in one finished unit? | designed | as-at | REL001 → SBJ012 → SBJ015 → ATR001 → ATR002 | Pass | — |
| [REQ005](#req005) | SCN002 | Which finished products contain this ingredient, by any route? | designed | current | REL001 | Pass | — |
| [REQ006](#req006) | SCN004 | How much more or less of each input did this batch use than the recipe specified? | designed | as-at | ATR001 → SBJ051 → SBJ052 → REL029 → ATR011 → ATR012 | Pass | — |
| [REQ007](#req007) | SCN005 | Which batches used an alternative input, and for which ingredient? | designed | as-at | ATR003 → SBJ022 → SBJ052 → ATR005 → ATR042 | Pass | — |
| [REQ008](#req008) | SCN006 | Was this supplier approved for this material on the day it was received? | designed | as-at | REL003 → SBJ005 → SBJ007 → REL017 → ATR007 → ATR080 | Pass | — |
| [REQ009](#req009) | SCN007 | Which of this batch's stated properties were tested here, and which were taken on the supplier's word? | designed | current | SBJ010 → SBJ011 → REL037 → ATR014 → ATR083 | Pass | — |
| [REQ010](#req010) | SCN008 | Which products depend on a bought-in ingredient whose contents we rely on the supplier to declare? | designed | current | SBJ011 → ATR018 → ATR036 | Pass | — |
| [REQ010](#req010) | SCN037 | What is inside the chocolate coating we buy in finished? | awkward | as-at | ATR036 → SBJ011 → ATR018 | **Accepted limit** | The chain of what goes into what stops at anything bought in. Only what the supplier has declared is known here, and that is recorded with who declared it and whether it was checked. |
| [REQ010](#req010) | SCN038 | A supplier recalls a sugar batch used inside a coating they sold us. Which of our batches are affected? | awkward | as-at | ATR012 → SBJ016 → SBJ063 → REL029 → REL030 → ATR029 | **Accepted limit** | Our record reaches the coating batch we received. Whether that batch contains the recalled sugar is in the supplier's records, so the twenty-four-hour answer depends on them. |
| [REQ011](#req011) | SCN009 | What allergens, hazards and certifications does this product carry, and from which inputs? | designed | as-at | REL004 → SBJ018 → SBJ020 → ATR034 → ATR035 | Pass | — |
| [REQ012](#req012) | SCN009 | What allergens, hazards and certifications does this product carry, and from which inputs? | designed | as-at | REL004 → SBJ018 → SBJ020 → ATR034 → ATR035 | Pass | — |
| [REQ013](#req013) | SCN010 | What must be disclosed for this household product, and what is withheld? | designed | current | SBJ019 → ATR037 → ATR038 | Pass | — |
| [REQ014](#req014) | SCN009 | What allergens, hazards and certifications does this product carry, and from which inputs? | designed | as-at | REL004 → SBJ018 → SBJ020 → ATR034 → ATR035 | Pass | — |
| [REQ015](#req015) | SCN011 | What is the latest date this finished batch can be used, given what went into it? | designed | current | SBJ021 → ATR031 → ATR041 | Pass | — |
| [REQ016](#req016) | SCN012 | Which batches came from this one, and which batches made up this combined one? | designed | current | SBJ016 → SBJ017 → ATR030 → ATR032 | Pass | — |
| [REQ017](#req017) | SCN013 | How much of this material is available, on hold, or rejected at each site right now? | designed | as-at | ATR089 → SBJ012 → SBJ048 → ATR017 → ATR090 | Pass | — |
| [REQ018](#req018) | SCN013 | How much of this material is available, on hold, or rejected at each site right now? | designed | as-at | ATR089 → SBJ012 → SBJ048 → ATR017 → ATR090 | Pass | — |
| [REQ019](#req019) | SCN014 | Which pack sizes of this product exist, and did this change create a new product or a new version? | designed | as-at | REL002 → SBJ013 → SBJ023 → ATR019 → ATR043 | Pass | — |
| [REQ020](#req020) | SCN014 | Which pack sizes of this product exist, and did this change create a new product or a new version? | designed | as-at | REL002 → SBJ013 → SBJ023 → ATR019 → ATR043 | Pass | — |
| [REQ021](#req021) | SCN015 | What recipe was this batch made to, and what was it meant to contain at the time? | designed | as-at | ATR004 → SBJ015 → ATR026 → ATR027 | Pass | — |
| [REQ022](#req022) | SCN004 | How much more or less of each input did this batch use than the recipe specified? | designed | as-at | ATR001 → SBJ051 → SBJ052 → REL029 → ATR011 → ATR012 | Pass | — |
| [REQ022](#req022) | SCN015 | What recipe was this batch made to, and what was it meant to contain at the time? | designed | as-at | ATR004 → SBJ015 → ATR026 → ATR027 | Pass | — |
| [REQ023](#req023) | SCN016 | What exactly is inside this individual unit, and which batch did each part come from? | designed | as-at | REL014 → SBJ026 → SBJ027 → REL013 → REL015 → ATR006 | Pass | — |
| [REQ024](#req024) | SCN016 | What exactly is inside this individual unit, and which batch did each part come from? | designed | as-at | REL014 → SBJ026 → SBJ027 → REL013 → REL015 → ATR006 | Pass | — |
| [REQ025](#req025) | SCN017 | What steps, equipment, qualifications and settings does making this product need on this line? | designed | current | SBJ033 → SBJ036 → REL006 → REL007 → ATR056 → ATR060 | Pass | — |
| [REQ026](#req026) | SCN017 | What steps, equipment, qualifications and settings does making this product need on this line? | designed | current | SBJ033 → SBJ036 → REL006 → REL007 → ATR056 → ATR060 | Pass | — |
| [REQ027](#req027) | SCN017 | What steps, equipment, qualifications and settings does making this product need on this line? | designed | current | SBJ033 → SBJ036 → REL006 → REL007 → ATR056 → ATR060 | Pass | — |
| [REQ028](#req028) | SCN017 | What steps, equipment, qualifications and settings does making this product need on this line? | designed | current | SBJ033 → SBJ036 → REL006 → REL007 → ATR056 → ATR060 | Pass | — |
| [REQ029](#req029) | SCN018 | Which instructions were issued for this batch, and which formulation did they come from? | designed | as-at | REL009 → SBJ041 → SBJ042 → REL027 → ATR064 → ATR065 | Pass | — |
| [REQ030](#req030) | SCN018 | Which instructions were issued for this batch, and which formulation did they come from? | designed | as-at | REL009 → SBJ041 → SBJ042 → REL027 → ATR064 → ATR065 | Pass | — |
| [REQ031](#req031) | SCN019 | What ran on this line just before this batch, and was the line cleaned in between? | designed | as-at | ATR057 → SBJ034 → SBJ054 → ATR058 → ATR097 | Pass | — |
| [REQ032](#req032) | SCN019 | What ran on this line just before this batch, and was the line cleaned in between? | designed | as-at | ATR057 → SBJ034 → SBJ054 → ATR058 → ATR097 | Pass | — |
| [REQ033](#req033) | SCN020 | Which machine was in this place on the day this batch was made? | designed | as-at | REL011 → SBJ026 → SBJ031 → REL010 → REL012 → ATR009 | Pass | — |
| [REQ034](#req034) | SCN020 | Which machine was in this place on the day this batch was made? | designed | as-at | REL011 → SBJ026 → SBJ031 → REL010 → REL012 → ATR009 | Pass | — |
| [REQ035](#req035) | SCN021 | Which machines cause the most unplanned stoppage, and how do they fail? | designed | as-at | ATR013 → SBJ028 → SBJ029 → REL031 → ATR050 → ATR051 | Pass | — |
| [REQ036](#req036) | SCN021 | Which machines cause the most unplanned stoppage, and how do they fail? | designed | as-at | ATR013 → SBJ028 → SBJ029 → REL031 → ATR050 → ATR051 | Pass | — |
| [REQ037](#req037) | SCN022 | How long did this line stop, why, and what did maintenance do about it? | designed | as-at | ATR013 → SBJ055 → SBJ056 → REL031 → ATR099 → ATR100 | Pass | — |
| [REQ038](#req038) | SCN022 | How long did this line stop, why, and what did maintenance do about it? | designed | as-at | ATR013 → SBJ055 → SBJ056 → REL031 → ATR099 → ATR100 | Pass | — |
| [REQ039](#req039) | SCN021 | Which machines cause the most unplanned stoppage, and how do they fail? | designed | as-at | ATR013 → SBJ028 → SBJ029 → REL031 → ATR050 → ATR051 | Pass | — |
| [REQ040](#req040) | SCN023 | Who carried out each step of this batch, and were they qualified on that day? | designed | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | — |
| [REQ040](#req040) | SCN040 | Two products are recorded as running at the same moment on a line and on a unit inside it. Which was it? | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Both runs are held with their places and times, and the place hierarchy says one is inside the other. Whether they may overlap is a value-level rule, authored against the model in DDA. |
| [REQ040](#req040) | SCN041 | An operator ran a step the day after their qualification expired. | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Recorded as it happened. The qualification's dates show it had expired, so the run is answerable rather than blocked after the event. |
| [REQ041](#req041) | SCN023 | Who carried out each step of this batch, and were they qualified on that day? | designed | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | — |
| [REQ041](#req041) | SCN040 | Two products are recorded as running at the same moment on a line and on a unit inside it. Which was it? | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Both runs are held with their places and times, and the place hierarchy says one is inside the other. Whether they may overlap is a value-level rule, authored against the model in DDA. |
| [REQ041](#req041) | SCN041 | An operator ran a step the day after their qualification expired. | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Recorded as it happened. The qualification's dates show it had expired, so the run is answerable rather than blocked after the event. |
| [REQ042](#req042) | SCN024 | Where has this batch been, and where is it now? | designed | as-at | ATR085 → SBJ043 → SBJ046 → REL016 → REL023 → ATR069 | Pass | — |
| [REQ044](#req044) | SCN025 | Did this batch meet the specification in force when it was made, and by what test? | designed | as-at | ATR023 → SBJ014 → SBJ039 → ATR024 → ATR025 | Pass | — |
| [REQ045](#req045) | SCN025 | Did this batch meet the specification in force when it was made, and by what test? | designed | as-at | ATR023 → SBJ014 → SBJ039 → ATR024 → ATR025 | Pass | — |
| [REQ046](#req046) | SCN026 | What went wrong on this batch — a procedure not followed, the product out of specification, or both? | designed | current | SBJ058 → SBJ059 → REL032 → ATR106 → ATR107 | Pass | — |
| [REQ047](#req047) | SCN027 | What was decided about this failed material, why, and by whom? | designed | current | SBJ060 → REL028 → REL032 → ATR010 → ATR110 | Pass | — |
| [REQ048](#req048) | SCN026 | What went wrong on this batch — a procedure not followed, the product out of specification, or both? | designed | current | SBJ058 → SBJ059 → REL032 → ATR106 → ATR107 | Pass | — |
| [REQ049](#req049) | SCN028 | Which corrective actions are open, and were any closed without checking they worked? | designed | current | SBJ009 → SBJ061 → REL034 → REL036 → ATR082 → ATR112 | Pass | — |
| [REQ050](#req050) | SCN029 | Who released this batch, when, and on what basis? | designed | current | SBJ062 → REL028 → ATR010 → ATR115 | Pass | — |
| [REQ051](#req051) | SCN030 | Every batch this ingredient batch went into, and everywhere those went — within twenty-four hours | designed | current | SBJ016 → SBJ063 → REL029 → REL030 → ATR012 → ATR029 | Pass | — |
| [REQ051](#req051) | SCN038 | A supplier recalls a sugar batch used inside a coating they sold us. Which of our batches are affected? | awkward | as-at | ATR012 → SBJ016 → SBJ063 → REL029 → REL030 → ATR029 | **Accepted limit** | Our record reaches the coating batch we received. Whether that batch contains the recalled sugar is in the supplier's records, so the twenty-four-hour answer depends on them. |
| [REQ052](#req052) | SCN030 | Every batch this ingredient batch went into, and everywhere those went — within twenty-four hours | designed | current | SBJ016 → SBJ063 → REL029 → REL030 → ATR012 → ATR029 | Pass | — |
| [REQ052](#req052) | SCN038 | A supplier recalls a sugar batch used inside a coating they sold us. Which of our batches are affected? | awkward | as-at | ATR012 → SBJ016 → SBJ063 → REL029 → REL030 → ATR029 | **Accepted limit** | Our record reaches the coating batch we received. Whether that batch contains the recalled sugar is in the supplier's records, so the twenty-four-hour answer depends on them. |
| [REQ053](#req053) | SCN030 | Every batch this ingredient batch went into, and everywhere those went — within twenty-four hours | designed | current | SBJ016 → SBJ063 → REL029 → REL030 → ATR012 → ATR029 | Pass | — |
| [REQ053](#req053) | SCN038 | A supplier recalls a sugar batch used inside a coating they sold us. Which of our batches are affected? | awkward | as-at | ATR012 → SBJ016 → SBJ063 → REL029 → REL030 → ATR029 | **Accepted limit** | Our record reaches the coating batch we received. Whether that batch contains the recalled sugar is in the supplier's records, so the twenty-four-hour answer depends on them. |
| [REQ054](#req054) | SCN031 | Which complaints concern this batch, and what else was made from the same inputs? | designed | current | SBJ064 → REL033 → ATR118 | Pass | — |
| [REQ055](#req055) | SCN032 | Who signed this record, what did it mean, and has anything been corrected since? | designed | as-at | ATR077 → SBJ004 → SBJ065 → REL035 → ATR078 → ATR079 | Pass | — |
| [REQ056](#req056) | SCN032 | Who signed this record, what did it mean, and has anything been corrected since? | designed | as-at | ATR077 → SBJ004 → SBJ065 → REL035 → ATR078 → ATR079 | Pass | — |
| [REQ057](#req057) | SCN032 | Who signed this record, what did it mean, and has anything been corrected since? | designed | as-at | ATR077 → SBJ004 → SBJ065 → REL035 → ATR078 → ATR079 | Pass | — |
| [REQ058](#req058) | SCN006 | Was this supplier approved for this material on the day it was received? | designed | as-at | REL003 → SBJ005 → SBJ007 → REL017 → ATR007 → ATR080 | Pass | — |
| [REQ059](#req059) | SCN028 | Which corrective actions are open, and were any closed without checking they worked? | designed | current | SBJ009 → SBJ061 → REL034 → REL036 → ATR082 → ATR112 | Pass | — |
| [REQ060](#req060) | SCN033 | Which of our finished batches were made by an outside manufacturer, to which specification, and when did they become ours? | designed | as-at | REL005 → SBJ005 → SBJ046 → REL019 → REL022 → ATR008 | Pass | — |
| [REQ061](#req061) | SCN033 | Which of our finished batches were made by an outside manufacturer, to which specification, and when did they become ours? | designed | as-at | REL005 → SBJ005 → SBJ046 → REL019 → REL022 → ATR008 | Pass | — |
| [REQ062](#req062) | SCN033 | Which of our finished batches were made by an outside manufacturer, to which specification, and when did they become ours? | designed | as-at | REL005 → SBJ005 → SBJ046 → REL019 → REL022 → ATR008 | Pass | — |
| [REQ063](#req063) | SCN008 | Which products depend on a bought-in ingredient whose contents we rely on the supplier to declare? | designed | current | SBJ011 → ATR018 → ATR036 | Pass | — |
| [REQ063](#req063) | SCN037 | What is inside the chocolate coating we buy in finished? | awkward | as-at | ATR036 → SBJ011 → ATR018 | **Accepted limit** | The chain of what goes into what stops at anything bought in. Only what the supplier has declared is known here, and that is recorded with who declared it and whether it was checked. |
| [REQ063](#req063) | SCN038 | A supplier recalls a sugar batch used inside a coating they sold us. Which of our batches are affected? | awkward | as-at | ATR012 → SBJ016 → SBJ063 → REL029 → REL030 → ATR029 | **Accepted limit** | Our record reaches the coating batch we received. Whether that batch contains the recalled sugar is in the supplier's records, so the twenty-four-hour answer depends on them. |
| [REQ064](#req064) | SCN023 | Who carried out each step of this batch, and were they qualified on that day? | designed | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | — |
| [REQ064](#req064) | SCN040 | Two products are recorded as running at the same moment on a line and on a unit inside it. Which was it? | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Both runs are held with their places and times, and the place hierarchy says one is inside the other. Whether they may overlap is a value-level rule, authored against the model in DDA. |
| [REQ064](#req064) | SCN041 | An operator ran a step the day after their qualification expired. | awkward | as-at | REL020 → SBJ001 → SBJ002 → REL021 → REL026 → ATR010 | Pass | Recorded as it happened. The qualification's dates show it had expired, so the run is answerable rather than blocked after the event. |
| [REQ065](#req065) | SCN024 | Where has this batch been, and where is it now? | designed | as-at | ATR085 → SBJ043 → SBJ046 → REL016 → REL023 → ATR069 | Pass | — |
| [REQ066](#req066) | SCN034 | Was this batch ever stored outside its permitted conditions? | designed | as-at | ATR015 → SBJ045 → SBJ066 → REL038 → ATR072 → ATR073 | Pass | — |
| [REQ067](#req067) | SCN035 | Which place or product is this, whatever identifier the supplier or regulator used? | designed | current | SBJ006 → SBJ013 → REL018 → ATR019 → ATR020 | Pass | — |
| [REQ069](#req069) | SCN035 | Which place or product is this, whatever identifier the supplier or regulator used? | designed | current | SBJ006 → SBJ013 → REL018 → ATR019 → ATR020 | Pass | — |
| [REQ070](#req070) | SCN036 | What did this batch cost against its standard, and why? | designed | as-at | ATR044 → SBJ024 → ATR045 | Pass | — |
| [REQ070](#req070) | SCN039 | What did poor quality cost across the plant last year? | awkward | as-at | ATR044 → SBJ024 → ATR045 | **Gap** | Scrap, rework, stoppages and complaints are each held, but nothing brings them together as one measure, and adding them up is a different question. |
