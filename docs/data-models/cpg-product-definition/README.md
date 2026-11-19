# CPG - Product Definition Data Model - Working Folder

Package for the **CPG - Product Definition** data model (Food and Beverage; DDA model DMM000000005, which DDA currently names "CPG Food & Beverage Products"). It sits beside `../cpg-manufacturing/`, the model for factories, batches, packing and the supply chain. Product Definition owns what a product is, what it is made from and what it must be; Manufacturing owns where and how it is made and moved.

| File | Purpose |
|---|---|
| `*.json` (16 files) | The package: scope, sources, requirements, data requirements, domains, subjects, roles, verbs, attributes, lookups, country regions, state, baseline, validation, derived and the DDA change package |
| `cpg-product-definition-data-design-document.md` | The Data Design Document, lite edition, projected from the package. Regenerate it, never edit it. The PDF is built from it by the repository's own workflow |
| `supporting/previous-document/` | The earlier document (28 September 2026), markdown and PDF, moved here from `docs/data-models/`. **Out of date** |
| `supporting/cpg-product-definition-design-review.md` | Architect review of the 17 November 2026 document, findings ranked by severity, with decisions needed |
| `supporting/editorial-review.md` | The same-agent reading of the 10 November 2026 version. It applies to that version only |
| `supporting/render-scripts/` | `render.py <package> <static-source.md> <out.md>` and the static source it copies the cover and sections 1.1 and 1.2 from |

## Status (2026-11-19)

- **Consumer goods definition (19 November 2026):** Product is used across industries, so a new concept, `ProductCPGDefinition` (SBJ022), is a one-to-one child of Product and holds the facts only a consumer goods product has: the legal name, net quantity and unit (moved from Product, identifiers kept) and an optional drop-down, `CPGProductType` (ATR098, list LKP019), with the values Logical and Local. Local is a version of a logical product that can be sold. Ingredient is not a kind: it is a role found from the formulations a product appears in (SCA018). One question is open (DEC006). Applied by `supporting/render-scripts/apply_cpg_definition.py` and `apply_cpg_kind_roles.py`.

- **Review fixes (19 November 2026):** claims name the nutrient they rest on; the stored claim-condition value and the logical-product flag are withdrawn; the two formulation rules and the model description are reworded; one assumption added (SCA017). Applied by `supporting/render-scripts/apply_review_fixes.py`.

- **Scope (17 November 2026):** the markets covered are the United States, the United Kingdom and the European Union, and no others. The design extends to other markets by adding list values; none is included by choice (SCI011, SCO013, SCA008).

- Validator v31.5 (`validate.py <package>`): **0 blocking, 0 material, 2 advisory** (the word *entity* in one concept and one list definition, the field's own word).
- Run with `--document`, the document reports the same hits the template carries (Appendix B and the full-edition section names, "review" in the supplied cover paragraph, "changed" in section 1.1) and one more, ER02: the document has more decision rows (DEC004 and DEC006) than the version the editorial review read.
- 42 requirements, 28 data requirements, 3 domains (all reused), 21 concepts (4 reused, 17 new), 18 roles, 9 relationships, 85 attributes, 19 lists of values (15 new, 2 extended, 2 reused), 43 sources, 39 test cases (36 pass, 3 accepted limits). The change package has 147 operations.
- Reconciled with DDA on 2026-11-16: the baseline (13 domains, 86 lookup types, 28 standards) is refreshed. The unit-of-measure list is `UniversalUnitOfMeasureCodes` (DLT000000156), shared with Manufacturing.

## Decisions

- **DEC002** (open): what to record when a supplier says what is inside its ingredient now differs from what was specified.
- **DEC003** (decided): the unit-of-measure list is shared with CPG Manufacturing and Supply Chain.
- **DEC005** (withdrawn 19 November 2026): a product sold and used as an ingredient is Local, and an ingredient by its formulations.
- **DEC006** (open): whether every sold product has a logical product above it, or a single-version product may stand alone.
- **DEC004** (decided 18 November 2026): this model creates Product and holds the hierarchy of products and ingredients; CPG Manufacturing and Supply Chain refers to them. Manufacturing now refers to it (DEC009 decided the same day).

## Still open

- The model name: DDA says "CPG Food & Beverage Products"; the package says "CPG - Product Definition".
- The editorial review should be read again against the current document.
- The change package is unapplied.
