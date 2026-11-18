# CPG Manufacturing and Supply Chain Data Model - Working Folder

Package for the **CPG Manufacturing and Supply Chain** data model (package reference `cpg-manufacturing`), corrected on 2026-11-16 after the design review in `supporting/cpg-manufacturing-design-review.md`. The package files in this folder are the source; the Data Design Document (lite edition) was regenerated from them on 2026-11-16 by `supporting/fix-scripts/render_mfg.py`.

| File | Purpose |
|---|---|
| `*.json` (15 files) | The package: scope, sources, requirements, data requirements, domains, subjects, roles, verbs, attributes, lookups, state, baseline, validation, derived and the DDA change package |
| `cpg-manufacturing-data-design-document.md` | The Data Design Document, lite edition, projected from the package. Regenerate it, never edit it. The PDF is built from it by the repository's own workflow |
| `supporting/first-pass-document/` | The document as first rendered (24 September 2026), in markdown and PDF. **Out of date**: kept only as the record of what the review examined |
| `supporting/cpg-manufacturing-design-review.md` | The 22-finding review of the first-pass document that drove the corrections |
| `supporting/fix-scripts/` | The scripts that applied the corrections, in order: `fix1`, `fix2`, `fix2b`, `fix3`, `fix4`/`fix5`, `apply_reread` (the DDA reconciliation of 2026-11-16), `build`. `defs.py` holds every definition. `common.py` points at the working copy used to run them. `render_mfg.py <package> <static-source.md> <out.md>` renders the document |
| `supporting/cpg-pass/`, `supporting/cpg-run/` | The first pass report and the research run that preceded the package |

## Status

- Validator v31.5 (`validate.py <package>`): **0 blocking, 0 material, 8 advisory**. Run with `--document` against the regenerated document it reports 2 blocking hits, both in the practice's supplied text, which is reproduced verbatim and not altered: the word "review" in the cover paragraph (RN07) and "changed" in section 1.1 (RN03). Nothing the package projects triggers a rendering check.
- `derived.json` and `dda-changeset.json` were rebuilt by `supporting/fix-scripts/build.py` (219 operations as of 18 November 2026, with one precondition, that the CPG - Product Definition change package is applied first because it creates Product: 44 roles, 42 concepts, 29 relationships, 91 attributes, 8 new lists of values, 2 new domains, 1 model, and updates to Locations and the unit-of-measure list). `render_mfg.py` reads `dda-changeset.json` for the operation count and does not rewrite either file.
- The eight advisory items are the word *Instances* in two domain definitions (the domain's own name), *entity* in one concept definition and in two role definitions (the field's own word, and DDA's own wording for the two reused roles), and three sibling pairs whose data requirements sit inside one another (REL029/REL030, SBJ055/SBJ056 and the reused Transaction against Location), kept because each says something the other does not.

## What was corrected

| Area | Correction |
|---|---|
| Scope | Food and beverage is the one subgroup. Household, personal care, pet care and beauty are out of scope for a later extension. Product definition and cost are out of scope, with owners named. Pack levels and supplier sites are in scope |
| Evidence | Ten sources that were not regulators or standards bodies are labelled as practitioner sources. A Wikipedia source is replaced by the ISA catalogue. Six sources are new: Regulation (EC) 178/2002 Article 18, the UK Food Standards Agency traceability page, the FDA 24-hour document, the NC State page on the proposed compliance date, the ISA standards list and the FDA preventive controls rule. Sources no active requirement cites are withdrawn |
| Requirements | 14 requirements withdrawn (product definition, cost and the other four subgroups); five reworded; REQ071 (supplier and customer traceability) and REQ072 (pack levels) added; the `certified` marks are dropped |
| Data requirements | 9 withdrawn; DRQ004, 005, 006 and 035 reworked; DRQ037 (pack levels) added; four prevent-resolutions pointed at structure that exists |
| Domains | Products reused as DDA holds it (DMD000000032). Locations extended to hold each factory down to the shop floor (DMD000000034). The Equipment domain is removed and recorded as a rejected candidate. Instances and Processes are the two proposed domains |
| Concepts | 66 to 49. Eleven product-definition concepts withdrawn; the plant structure merged into Location; failure criticality folded into Instance; production orders and material consumptions merged away; deviations and non-conformances merged into one Findings concept that says which each is; pack levels added |
| Roles and relationships | Roles 70 to 48 and relationships 38 to 31. All batch ends play one role, Traced Batch. Role definitions now stand alone and name no counterpart. Five view names are overridden because one role is played at several ends |
| Attributes and lists | 120 to 93 attributes and 9 to 10 lists. Cost, product definition and typed text references are withdrawn; the unit of measure and the quantity the recipe called for move onto the link between a run and a batch; whether an alternative input was used is recorded on that link |
| Definitions | Every concept, role, attribute and list is written in the three-part form of `references/definitions.md`, with the reuse search and the distinct need recorded |
| Reconciliation with DDA (2026-11-16) | DDA re-read: 13 domains, 86 lookup types, 28 standards (texts unchanged). Transaction is reused from DDA (DMC000000031) and goods movements are created beneath it as `TransactionGoodsMovement`, since DDA's Transaction is a movement of money or holdings (DEC013). Employment (REL020) and the trading party (REL022, direction reversed) are DDA's own relationships DMR000000005 and DMR000000037, and four roles take DDA's wording: Organization Employee, Organization Employer, Transaction and Transaction Party. DDA's Locations, Products and Events domains hold no concept, so Location, Product and Event are created (DEC010 decided). The change package now creates the roles and a model, skips reused items, and carries the fields DDA requires |
| Regeneration | Requirement REQ071 was used twice (a withdrawn one and the new traceability requirement); the new one is now REQ073. The six reused domains now carry a sentence on what this model uses each for. Two source descriptions no longer use the word *approval*. The unit-of-measure list is now `UniversalUnitOfMeasureCodes`, created in DDA as lookup type DLT000000156 on 2026-11-16 and shared with CPG - Product Definition; this model extends it with seven values (DEC012 decided) |
| State | The 32 test cases are re-walked against the new structure (30 pass, 2 accepted limits); the cost case is withdrawn with its scope. Exceptions and decisions are restated against the current DDA principles; conformance entries are written against the full standard text. A minimality sweep is recorded for both passes |

## Compared with the Private Equity folder (2026-11-16)

Counts are active items only.

| Measure | Private Equity | CPG Manufacturing, first pass | CPG Manufacturing, corrected |
|---|---|---|---|
| Passes run | 3 (stable for 2) | 1 | 2 |
| Business requirements | 13 | 69 | 57 |
| Data requirements | 8 | 36 | 28 |
| Domains | 3, all reused | 10 (5 proposed) | 9: 6 reused, 1 extended, 2 proposed |
| Roles | 10 | 70 | 48 (4 take DDA's wording) |
| Relationships | 8 | 38 | 31 (2 reused) |
| Concepts | 8 | 66 | 49 (6 reused, 43 new) |
| Attributes | 38 | 120 | 93 (about 2 per concept) |
| Lists of values | 15 | 9 | 10 |
| Sources | 16 | 40 | 38 (26 practitioner, 7 regulatory, 4 standard, 1 reference model) |
| Requirements resting on practitioner sources alone | 2 of 13 | 26 of 69 | 26 of 57 |
| Test cases | 27 pass | 38 pass, 2 accepted, 1 fail | 30 pass, 2 accepted limits |
| Validation | 1 blocking, 22 advisory | 10 blocking, 679 material, 24 advisory (v31.5) | 0 blocking, 0 material, 8 advisory |

## Assumptions made for the open decisions in the review

The review's decisions D1 to D6 were not answered. The corrections follow the direction stated earlier for this model, and each is easy to reverse:

1. **Subgroup.** Food and beverage first, the other four subgroups later (D1).
2. **Plant structure.** One location hierarchy down to the shop floor, with machines held with Instances (D2).
3. **Batches.** A batch stays beneath Product with one Traced Batch role and EXC002 recorded. A domain of its own fails the domain tests, and the review's earlier recommendation of one is withdrawn (D3; DEC001 keeps the question open).
4. **Markets.** United States, United Kingdom and European Union are the sample markets (D4).
5. **Cost.** The total cost of poor quality and every other cost is out of scope (D5; DEC006).
6. **Supplier approval.** Whether a supplier held a valid assessment is held. Approved-supplier lists and certifications belong to product definition (D6).

## Still open

- **Evidence is still thin.** 26 of 57 requirements rest on practitioner sources alone. The six new sources cover traceability and preventive controls; the quality, maintenance and process requirements still need regulator or standards sources.
- **Retention.** The two-year retention in REQ052 is not confirmed from the rule's own text, which could not be retrieved (DEC011). The compliance date of 20 July 2028 is a proposal in the source, and the document states it as proposed.
- **Product (DEC009, decided 18 November 2026).** CPG - Product Definition owns Product and the hierarchy of products and ingredients, and this model builds on it and holds the logistics of making finished products from ingredients. Product is a reference here (`dda_action` reuse with no DDA identifier, `proposed_by` naming the owner); its change package creates the concept first. `ProductKind` and `ProductIsPurchased` and the product-kind list are withdrawn because they say what a product is. Batches, sub-batches and pack levels stay beneath it.
- **Concept depth.** About 2 attributes per concept remains, and 15 event concepts remain, several with one attribute. The recall, complaint, correction and storage-breach concepts are the candidates for a further merge.
- **Decisions DEC001, 004, 005, 007, 008, 011 and 013** are open; DEC006, DEC009, DEC010 and DEC012 are decided. DEC013 asks whether goods movements and stock positions stay beneath DDA's Transaction.
- **Baseline.** Refreshed on 2026-11-16 (domains, lookup types, retrieval date). The standards are the 28 September texts, which DDA still holds unchanged, so their hashes stand; the hash method of the original read could not be reproduced, so the hashes were kept and not recomputed.
- **Principles appendix.** The lite edition under validator v31.5 carries no principles table; the two departures (EXC002, EXC003) are stated in section 6.2. The principles table is in the full edition, which has no renderer yet.
- **The change package is unapplied** and carries no preconditions (DEC007).
