# CPG Manufacturing and Supply Chain Data Model - Working Folder

Package for the **CPG Manufacturing and Supply Chain** data model (package reference `cpg-manufacturing`), corrected on 2026-11-16 after the design review in `supporting/cpg-manufacturing-design-review.md`. The package files in this folder are the source; the Data Design Document is regenerated from them.

| File | Purpose |
|---|---|
| `*.json` (15 files) | The package: scope, sources, requirements, data requirements, domains, subjects, roles, verbs, attributes, lookups, state, baseline, validation, derived and the DDA change package |
| `supporting/first-pass-document/` | The Data Design Document as first rendered (24 September 2026). **Out of date**: it describes the package before the corrections below and must be regenerated, not edited |
| `supporting/cpg-manufacturing-design-review.md` | The 22-finding review of the first-pass document that drove the corrections |
| `supporting/fix-scripts/` | The scripts that applied the corrections, in order: `fix1`, `fix2`, `fix2b`, `fix3`, `fix4`/`fix5`, `build`. `defs.py` holds every definition. `common.py` points at the working copy used to run them |
| `supporting/cpg-pass/`, `supporting/cpg-run/` | The first pass report and the research run that preceded the package |

`../cpg-manufacturing-data-design-document.pdf` is the PDF of the first-pass document and is out of date for the same reason.

## Status

- Validator v31.5 (`validate.py <package>`): **0 blocking, 0 material, 5 advisory**. The validator was run on the package alone; the document checks (RN03, RN06, RN07, ER02) run when the regenerated document is validated with `--document`.
- `derived.json` and `dda-changeset.json` were rebuilt by `supporting/fix-scripts/build.py` (180 operations, no preconditions). They are the same shape as before, not the output of the document renderer; the renderer should overwrite `derived.json` on regeneration.
- The five advisory items are the word *Instances* in two domain definitions (the domain's own name), *legal entity* in one concept definition (the field's own word), and two sibling pairs whose data requirements sit inside one another (REL029/REL030 and SBJ055/SBJ056), kept because each says something the other does not.

## What was corrected

| Area | Correction |
|---|---|
| Scope | Food and beverage is the one subgroup. Household, personal care, pet care and beauty are out of scope for a later extension. Product definition and cost are out of scope, with owners named. Pack levels and supplier sites are in scope |
| Evidence | Ten sources that were not regulators or standards bodies are labelled as practitioner sources. A Wikipedia source is replaced by the ISA catalogue. Six sources are new: Regulation (EC) 178/2002 Article 18, the UK Food Standards Agency traceability page, the FDA 24-hour document, the NC State page on the proposed compliance date, the ISA standards list and the FDA preventive controls rule. Sources no active requirement cites are withdrawn |
| Requirements | 14 requirements withdrawn (product definition, cost and the other four subgroups); five reworded; REQ071 (supplier and customer traceability) and REQ072 (pack levels) added; the `certified` marks are dropped |
| Data requirements | 9 withdrawn; DRQ004, 005, 006 and 035 reworked; DRQ037 (pack levels) added; four prevent-resolutions pointed at structure that exists |
| Domains | Products reused as DDA holds it (DMD000000032). Locations extended to hold each factory down to the shop floor (DMD000000034). The Equipment domain is removed and recorded as a rejected candidate. Instances and Processes are the two proposed domains |
| Concepts | 66 to 48. Eleven product-definition concepts withdrawn; the plant structure merged into Location; failure criticality folded into Instance; production orders and material consumptions merged away; deviations and non-conformances merged into one Findings concept that says which each is; pack levels added |
| Roles and relationships | Roles 70 to 48 and relationships 38 to 31. All batch ends play one role, Traced Batch. Role definitions now stand alone and name no counterpart. Five view names are overridden because one role is played at several ends |
| Attributes and lists | 120 to 93 attributes and 9 to 10 lists. Cost, product definition and typed text references are withdrawn; the unit of measure and the quantity the recipe called for move onto the link between a run and a batch; whether an alternative input was used is recorded on that link |
| Definitions | Every concept, role, attribute and list is written in the three-part form of `references/definitions.md`, with the reuse search and the distinct need recorded |
| State | The 32 test cases are re-walked against the new structure (30 pass, 2 accepted limits); the cost case is withdrawn with its scope. Exceptions and decisions are restated against the current DDA principles; conformance entries are written against the full standard text. A minimality sweep is recorded for both passes |

## Compared with the Private Equity folder (2026-11-16)

Counts are active items only.

| Measure | Private Equity | CPG Manufacturing, first pass | CPG Manufacturing, corrected |
|---|---|---|---|
| Passes run | 3 (stable for 2) | 1 | 2 |
| Business requirements | 13 | 69 | 57 |
| Data requirements | 8 | 36 | 28 |
| Domains | 3, all reused | 10 (5 proposed) | 9: 6 reused, 1 extended, 2 proposed |
| Roles | 10 | 70 | 48 |
| Relationships | 8 | 38 | 31 |
| Concepts | 8 | 66 | 48 (5 reused, 43 new) |
| Attributes | 38 | 120 | 93 (about 2 per concept) |
| Lists of values | 15 | 9 | 10 |
| Sources | 16 | 40 | 38 (26 practitioner, 7 regulatory, 4 standard, 1 reference model) |
| Requirements resting on practitioner sources alone | 2 of 13 | 26 of 69 | 26 of 57 |
| Test cases | 27 pass | 38 pass, 2 accepted, 1 fail | 30 pass, 2 accepted limits |
| Validation | 1 blocking, 22 advisory | 10 blocking, 679 material, 24 advisory (v31.5) | 0 blocking, 0 material, 5 advisory |

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
- **DDA could not be read.** The connection was down for this work, so the reuse searches are against the baseline read on 28 September 2026, which holds no concepts for Products or Locations. DEC009 (which model creates Product) and DEC010 (what Locations already holds) are to be settled before the change package is applied.
- **Concept depth.** About 2 attributes per concept remains, and 15 event concepts remain, several with one attribute. The recall, complaint, correction and storage-breach concepts are the candidates for a further merge.
- **Decisions DEC001, 004, 005, 007, 008 to 011** are open. The manufacturing document's introduction text still needs the standard boilerplate, which the renderer supplies.
- **The change package is unapplied** and carries no preconditions (DEC007).
