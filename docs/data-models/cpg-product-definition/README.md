# CPG - Product Definition Data Model - Working Folder

Package for the **CPG - Product Definition** data model (Food and Beverage; DDA model DMM000000005, which DDA currently names "CPG Food & Beverage Products"). It sits beside `../cpg-manufacturing/`, the model for factories, batches, packing and the supply chain. Product Definition owns what a product is, what it is made from and what it must be; Manufacturing owns where and how it is made and moved.

| File | Purpose |
|---|---|
| `*.json` (16 files) | The package: scope, sources, requirements, data requirements, domains, subjects, roles, verbs, attributes, lookups, country regions, state, baseline, validation, derived and the DDA change package |
| `cpg-product-definition-data-design-document.md` | The Data Design Document, lite edition, projected from the package. Regenerate it, never edit it. The PDF is built from it by the repository's own workflow |
| `supporting/previous-document/` | The earlier document (28 September 2026), markdown and PDF, moved here from `docs/data-models/`. **Out of date** |
| `supporting/editorial-review.md` | The same-agent reading of the 10 November 2026 version. It applies to that version only |
| `supporting/render-scripts/` | `render.py <package> <static-source.md> <out.md>` and the static source it copies the cover and sections 1.1 and 1.2 from |

## Status (2026-11-16)

- Validator v31.5 (`validate.py <package>`): **0 blocking, 0 material, 2 advisory** (the word *entity* in one concept and one list definition, the field's own word).
- Run with `--document`, the document reports the same hits the template carries (Appendix B and the full-edition section names, "review" in the supplied cover paragraph, "changed" in section 1.1) and one more, ER02: the document has one more decision row (DEC004) than the version the editorial review read.
- 42 requirements, 27 data requirements, 3 domains (all reused), 20 concepts (4 reused, 16 new), 18 roles, 9 relationships, 85 attributes, 18 lists of values (14 new, 2 extended, 2 reused), 43 sources, 38 test cases (35 pass, 3 accepted limits). The change package has 145 operations.
- Reconciled with DDA on 2026-11-16: the baseline (13 domains, 86 lookup types, 28 standards) is refreshed. The unit-of-measure list is `UniversalUnitOfMeasureCodes` (DLT000000156), shared with Manufacturing.

## Decisions

- **DEC002** (open): what to record when a supplier says what is inside its ingredient now differs from what was specified.
- **DEC003** (decided): the unit-of-measure list is shared with CPG Manufacturing and Supply Chain.
- **DEC004** (open): Product is proposed here and by Manufacturing because DDA's Products domain holds no concept. Which model creates it, and which refers to it. Matches DEC009 in `../cpg-manufacturing/`.

## Still open

- The model name: DDA says "CPG Food & Beverage Products"; the package says "CPG - Product Definition".
- The editorial review should be read again against the current document.
- The change package is unapplied.
