# Review of the CPG Manufacturing Operations Data Design Document, read as a final design

| | |
|---|---|
| Document reviewed | CPG Manufacturing Operations — Data Design Document (full and lite editions), package `cpg-bdd`, dated 24 September 2026, method version 1.0 |
| Location | `docs/data-models/cpg-manufacturing/` in M-A-Operating-System/shared-work (pull request [#51](https://github.com/M-A-Operating-System/shared-work/pull/51)) |
| Review date | 16 November 2026 |
| Reviewed against | The method rules for a final design (target state, design only, minimum set, canonical); the CPG - Product Definition design of 11 November 2026; the Private Equity design of 14 November 2026; Andrew's modelling conventions and boundary decisions |
| Reviewer | Claude (same agent that handled the package; not an independent reader) |

## 1 Conclusion

**The document is not fit to stand as a final design in its present form.** The requirement set and the traceability chain behind it are a sound starting point. The design built on them has four faults that cannot be fixed by editing text:

1. **It models the wrong scope.** It covers five product subgroups and re-models the product definition, which now belongs to CPG - Product Definition. It splits the factory floor from locations, against the stated direction of one location hierarchy down to the shop floor. It omits packing and pack levels, which the Product Definition design assigns to manufacturing.
2. **It reads as a work report, not a design.** It carries a status line, an approval block marked "Not certified — research-only", and a placeholder where the standard introduction belongs.
3. **Its evidence is thinner than it looks.** Only 7 of 40 sources come from a regulator or standards body, and 48 of 69 requirements cite none. No source covers the UK or EU.
4. **Its shape departs from the other two designs.** It uses seven different role names for a batch, 28 concepts with a single attribute, 93% mandatory attributes and 9 lists of values against 120 attributes.

**Recommendation:** re-baseline it as the **CPG Manufacturing and Supply Chain** model. Keep the evidence-backed requirements as input and rework scope, roles, concepts and sources as set out in section 5. Do not patch the present document.

## 2 The test applied

A final design in this method is the target state: it leads DDA rather than following it, states the design and nothing about how it was produced, holds the fewest domains, roles, relationships, concepts, attributes and lists that meet the requirements, and defines each in the business's own words. The Private Equity folder is the working reference for layout. The Product Definition design is the reference for the boundary.

## 3 Findings

Severity: **Blocking** means the document cannot be approved as a final design until it is resolved. **Major** means it needs rework before approval. **Minor** can be corrected in the same pass.

### 3.1 Scope and boundary

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F01 | Blocking | The document re-models product definition. Scope item SCI002 ("Defining products — what they are made from and what they must be") and the `Products` domain, proposed as new, hold hazards, shelf life, specifications, identifiers, variant axes, substitutions and origins. | The Product Definition design records that DDA already holds a Products domain (DMD000000032) and that product definition, variants, ingredients, allergens, shelf life and storage temperature sit in that model. Seven data requirements are met only by `Products` concepts: DRQ001, DRQ009, DRQ010, DRQ011, DRQ014, DRQ015, DRQ036. | Withdraw the product-definition concepts from this design. Keep `Batches`, sub-batches and any cost, and refer to Product Definition for the rest. |
| F02 | Blocking | The five subgroups (food and beverage, household, personal care, pet care, beauty) are covered equally, while Product Definition is food and beverage only. | Scope section 2.1; REQ013 (household disclosure) and the ISO 22716 cosmetics sources. | Decide the scope (D1). If food and beverage only, withdraw the household, cosmetics and pet requirements. If all CPG, state that the Product Definition model covers one subgroup of it. |
| F03 | Major | Equipment (the plant structure) and Locations are separate domains, each with its own containment relationship and identifier concept. | REL010 and REL016 both say "is within"; `EquipmentPositionIdentifiers` and `LocationIdentifiers` duplicate each other; REL012 links a plant position to a site. The stated direction is a single location hierarchy that runs down to the shop-floor location. | Merge plant positions into one Locations hierarchy. Keep machines (Instances) and their capabilities separate from places. |
| F04 | Major | Packing and pack levels are missing. | Product Definition's out-of-scope item SCO010 names packing and the levels case and pallet as owned by this model. The manufacturing design has one list value, `CASE`, in a unit-of-measure list and no pack-level concept. The word "pallet" appears once. | Add a requirement and a concept for pack levels and what each level contains, citing GS1 sources. |
| F05 | Major | Batches are not anchored. Seven relationships point at a batch concept that sits beneath Product, so the design carries an exception (EXC002). | Seven role names for the same thing: Incorporated Batch, Input Batch, Output Batch, Affected Batch, Complained-of Batch, Declared Batch, Exposed Batch. | Use one role, Traced Batch, for every batch end, and keep the batch beneath Product with EXC002 stated against the current standards (D3). A domain of its own fails the domain tests, because a batch has no existence apart from its product. |

### 3.2 Conformance as a final design

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F06 | Blocking | The document reports on its own process. | A "Status" line ("published with accepted limits"); a section "11 Approval" with "Not certified — research-only"; assumption SCA004 ("research-only work"); DEC002 (certification "cannot pass in research-only mode"); DEC007 (a tool error). The Private Equity and Product Definition designs contain none of these. | Remove them. State assumptions and decisions about the business, not about how the work was done. |
| F07 | Blocking | The standard introduction is missing. | "About This Document" reads "Supplied text not available." | Insert the standard text before issue. |
| F08 | Major | Definitions use modelling vocabulary. | "One record per …" appears 67 times (Private Equity: 0; Product Definition: 0). Section 5.4 says each definition "states the grain". | Rewrite each definition in the business's words: what the thing is, what can be relied on it for, and what looks like it but is not. |
| F09 | Minor | Section numbering jumps from 5 to 10 and 11, and from Appendix A to Appendix E. Appendix B (the principles) is absent. | Table of contents. | Renumber, and add the principles appendix as in the Product Definition design. |
| F10 | Blocking | Two exceptions are unapproved and the validator reports three blocking defects and one material defect (RN03; X01 for EXC001 and EXC002; Q02 for SCN039). | `validation.json`. | Resolve the exceptions (F05, D3) and re-run validation. |

### 3.3 Model design

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F11 | Major | Roles are named for one relationship each instead of once for the thing. | 70 roles for 38 relationships (Private Equity: 10 for 8). Pairs such as Correction and Corrected Record, Trigger and Response. Andrew's convention is one shared role name for the same subject wherever it appears. | Reduce to one role per subject and capacity. A batch should be one role; a place one or two; a machine one. |
| F12 | Major | Many concepts hold almost nothing. | 28 of 66 concepts have one attribute; two created concepts have none (`EquipmentPositionIdentifiers`, `EventProductionOrders`); the anchors `Event`, `Location` and `ProcessSegment` each hold one. The Private Equity average is about five. | Test each thin concept against the minimum-set rule: fold it into a neighbour or give it the fields the requirement asks for. |
| F13 | Major | Events are modelled as one concept per kind of event (18 in the Events domain). | `EventStoppages`, `EventReleases`, `EventRecalls`, `EventCorrections` and others, each a child of `Event`. | Keep separate concepts only where a requirement says the kinds are different things (REQ040 instructed, carried out and recorded; REQ046 departure against failure; REQ037 one stoppage). Fold the rest, with a kind list. Note the DDA Events domain is defined for financial services (DEC008). |
| F14 | Major | Almost every attribute is mandatory, and over half are not typed. | 111 of 120 attributes are mandatory (93%; Private Equity 68%). 77 are critical. 51 are free text (43%; Private Equity 1 of 38). Only 9 are lists of values (Private Equity 19 of 38). Six category-like attributes (failure mode, reasons, requirement kind) are free text. | Mark mandatory only what the requirement says must never be missing. Replace the six with lists of values. |
| F15 | Minor | The costing concept holds derived values. | `ProductCostings` has mastery "derived". The failed case SCN039 (total cost of poor quality) is a calculation across scrap, rework, stoppages and complaints. | State cost of poor quality as out of scope, and hold only what is observed (D4). |
| F16 | Minor | The unit-of-measure list has six values, one of them `CASE`, which is a pack level, not a unit. | Section 5.5. | Reuse the universal unit list in DDA if it exists; move `CASE` to pack levels. |

### 3.4 Evidence

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F17 | Blocking | Source types are mislabelled, so the evidence looks stronger than it is. The package counts 10 regulatory and 7 standard sources. Four are regulators (FDA ×3, New York DEC) and three come from standards bodies (OPC Foundation, GS1 UK, GS1 New Zealand). | Typed "regulatory" but not regulators: NC State Extension, Michigan State Extension, two law firms, a law blog, a software vendor. Typed "standard" but not standards bodies: Registrar Corp, a software vendor, a code-printing vendor. A Wikipedia article is the source for the batch process model. | Retype the sources honestly and replace the non-primary ones. 48 of 69 requirements cite no regulator or standards body, so recompute coverage after retyping. |
| F18 | Blocking | No UK or EU source, and none for outside-manufacturer assurance outside the US. The Product Definition design has three sample markets. | No source URL in the package is an EU or UK authority. EU and UK law require one-step-back, one-step-forward traceability: [Article 18 of Regulation (EC) No 178/2002](https://www.legislation.gov.uk/eur/2002/178/article/18) and the [UK Food Standards Agency guidance](https://www.gov.uk/government/publications/food-traceability-for-businesses/food-traceability-for-businesses). | Add the EU and UK traceability sources and decide whether the requirements are market-specific (D6). |
| F19 | Major | The US traceability requirements may be stale and are not scoped. REQ051 to REQ053 cite the FDA page whose link still carries "proposed rule", though the rule is final. The two-year retention (REQ052) rests on a software vendor's page. The rule applies to foods on the FDA's Food Traceability List, not to all food. The FDA has proposed moving the compliance date from 20 January 2026 to [20 July 2028](https://foodbusiness.ces.ncsu.edu/news/fda-fsma-204-food-traceability-rule-july-20-2028/); the source describes this as a proposal. | The [FDA document](https://fda.gov/media/183514/download) confirms the 24-hour electronic sortable spreadsheet on request. I could not retrieve the FDA's own page or the rule text, so the retention period and the date are unverified from a primary source. | Cite the rule text (21 CFR Part 1, Subpart S) and the FDA's page, state that it applies to listed foods, and give the compliance date. |
| F20 | Minor | The process-model sources are weak. ISA-88 is cited through Wikipedia. | SRC002. | Cite the publisher's catalogue page: the [ISA standards list](https://isa.org/standards-and-publications/isa-standards/list-of-all-isa-standards). |

### 3.5 Fitness for DDA

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F21 | Major | The change package is out of date. Its 233 operations were built on a baseline of September 2026 and have no preconditions because state transitions could not be read. It creates a `Products` domain that DDA now holds, and no model record. | `dda-changeset.json`; DEC007; DMM000000005 is the Product Definition model in DDA. | Rebuild the package after the redesign, with a model record named CPG Manufacturing and Supply Chain. |
| F22 | Minor | Where the design already depends on the Master concept's new Successor field (merged or replaced materials, suppliers, places), the package has no reference to it. | Requirement REQ068 (two records for the same material, supplier or place). | Use Successor rather than a manufacturing-specific merge concept. |

## 4 What is sound and should be kept

- **The traceability chain.** Every concept traces to a data requirement, a business requirement and a source. No source is uncited.
- **The requirements that name real distinctions:** a place on a line is not the machine in it (REQ034); a plan, an issued instruction and a performed record are three things (REQ030, REQ040); a departure from procedure is not a failure against specification (REQ046); one stoppage is recorded once and seen by both production and maintenance (REQ037); a supplier's approval holds for dates (REQ008); a recipe exists at four levels of specificity (REQ029).
- **The business test cases.** 38 of 41 pass, and two of the others are honest limits (what a bought-in coating contains; a supplier's own batch records).
- **The boundary rules** the document already states: suppliers as companies, outside-manufacturer ownership of materials until receipt (REQ061).

## 5 Recommended path

1. **Decide D1 to D6** (below).
2. **Re-scope.** Name the model CPG Manufacturing and Supply Chain. Withdraw product-definition content (F01) and carry forward batches, sub-batches, production, quality, equipment, locations and movement.
3. **Re-source.** Retype sources (F17); add EU and UK authorities (F18); fix the US traceability citations (F19); cite the ISA publisher (F20). Re-test every requirement that loses its only source.
4. **Redesign roles and concepts.** One role per subject (F11); one Traced Batch role (F05); merge plant positions into Locations (F03); fold thin concepts and event kinds (F12, F13); add pack levels (F04).
5. **Rewrite for a final design.** Remove status and approval content (F06, F07); rewrite definitions (F08); renumber and add the principles appendix (F09); re-set mandatory and typed attributes (F14).
6. **Rebuild and re-validate** the change package against the live DDA (F21), then run an independent reading of the document.

## 6 Decisions needed from Andrew

| ID | Decision | Options | Reviewer's recommendation |
|---|---|---|---|
| D1 | Which subgroups does the manufacturing model cover? | Food and beverage only · all consumer packaged goods | Food and beverage first, to match Product Definition; extend later by adding requirements |
| D2 | Is the plant structure part of the Locations hierarchy? | Merge into Locations · keep Equipment separate | Merge, per the stated direction |
| D3 | Do batches become the anchor of their own domain? | Yes · keep under Products and keep EXC002 | Keep under Products and keep EXC002 |
| D4 | Is total cost of poor quality in scope? | In · out | Out; hold observed costs only |
| D5 | Keep one concept per event kind? | Keep all · keep only those a requirement distinguishes | Keep only those a requirement distinguishes |
| D6 | Which markets does the model cover? | US only · US, UK and EU as sample markets | US, UK and EU, as in Product Definition |

## 7 Limits of this review

- **Not independent.** The same agent produced the package archive and read it; an independent reading of the reworked document is still needed.
- **DDA not reachable.** The DDA session had lapsed, so I could not compare live DDA records. The Products domain (DMD000000032) is taken from the Product Definition design of 11 November.
- **Sources partly verified.** I confirmed the 24-hour requirement from an FDA document and the proposed July 2028 date from a university extension page. I did not retrieve the FDA's own page or the rule text, the EUR-Lex text of Regulation 178/2002 (I cite the UK legislation.gov.uk copy), or any of the package's 40 sources.
- **Counts.** All counts are active items taken from the package JSON; the lite document's own summary counts 69 requirements and 41 test cases.

## Sources

- [FDA — food traceability rule document (24-hour spreadsheet requirement)](https://fda.gov/media/183514/download)
- [NC State Extension — FDA FSMA 204 proposed compliance date of 20 July 2028](https://foodbusiness.ces.ncsu.edu/news/fda-fsma-204-food-traceability-rule-july-20-2028/)
- [Regulation (EC) No 178/2002, Article 18 (legislation.gov.uk)](https://www.legislation.gov.uk/eur/2002/178/article/18)
- [Food Standards Agency — Food traceability for businesses](https://www.gov.uk/government/publications/food-traceability-for-businesses/food-traceability-for-businesses)
- [ISA — list of all ISA standards (ISA-88, ISA-95)](https://isa.org/standards-and-publications/isa-standards/list-of-all-isa-standards)
- [Package pull request #51](https://github.com/M-A-Operating-System/shared-work/pull/51)
