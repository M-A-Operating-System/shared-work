# CPG Manufacturing Operations Data Model - Working Folder

Working folder for the CPG Manufacturing Operations data model. This is the **first-pass package** (document dated 24 September 2026, method version 1.0). It was produced before the product definition was separated into its own model, so its scope is wider than the manufacturing model now intended (see "Scope drift" below).

| File | Purpose |
|---|---|
| `cpg-manufacturing-data-design-document.md` | Full edition of the Data Design Document (package `cpg-bdd`) |
| `cpg-manufacturing-data-design-document-lite.md` | Lite edition of the same document: scope, requirements, model, open decisions |
| `*.json` | Package definition files (domains, subjects, roles, verbs, attributes, lookups, requirements, data requirements, sources, state, validation and so on) |
| `dda-changeset.json` | The changes DDA would need to hold this design (233 operations, no preconditions) |
| `supporting/cpg-pass/` | The pass 1 report, the pass 2 delta and the sources added in pass 2 |
| `supporting/cpg-run/` | The earlier research run that preceded the package (scope, sources, requirements, subjects, verbs) |

A PDF of the document is held one level up: `../cpg-manufacturing-data-design-document.pdf`.

## Compared with the Private Equity folder (2026-11-16)

Counts are active items only. The Private Equity folder is the reference for how a package folder is laid out; both folders hold the same 15 package files.

| Measure | Private Equity (PE-STRUCT-20261114-01) | CPG Manufacturing (cpg-bdd) |
|---|---|---|
| Passes run | 3 (stable for 2) | 1 |
| Business requirements | 13 | 69 |
| Data requirements | 8 | 36 |
| Domains | 3, all reused from DDA | 10: 5 reused, 5 proposed (Products, Instances, Equipment, Processes, Locations) |
| Roles | 10 | 70 |
| Relationships | 8 | 38 |
| Concepts | 8 (4 reused, 2 extended, 2 new) | 66 (5 reused, 61 new) |
| Attributes | 38 (about 5 per concept) | 120 (about 2 per concept) |
| Lists of values | 15 | 9 |
| Sources | 16: 9 practitioner, 5 standard, 2 regulatory | 40: 20 practitioner, 10 regulatory, 7 standard, 3 reference model |
| Requirements resting on practitioner sources alone | 2 of 13 | 26 of 69 |
| Business test cases | 27 pass | 38 pass, 2 accepted limits, 1 fail (SCN039, total cost of poor quality) |
| Validation | 1 blocking (RN03), 22 advisory | 3 blocking (RN03 and the unapproved exceptions EXC001, EXC002), 1 material (SCN039) |
| Requirement owners | 7 named roles | 11 named roles; Quality manager owns 23 of 69 |
| Comparison with DDA | Section in README, retirements listed | None yet; DDA models list shows no manufacturing model |

What the comparison shows:

- **Size.** The manufacturing package is roughly three to eight times larger than the Private Equity one on every count except lists of values, which it has fewer of (9 against 15). It proposes five new domains where Private Equity proposes none.
- **Concept depth.** Manufacturing concepts hold few attributes (about 2 each against about 5). 24 of the 66 concepts are occurrences, and 18 of those sit in the Events domain, one concept per kind of event (stoppage, deviation, release and so on). Private Equity has two occurrence concepts.
- **Roles.** Many manufacturing roles exist for one relationship only (for example Corrected Record and Correction, Trigger and Response). Most Private Equity roles are names the field itself uses (Fund, GP, LP, Investor, PortCo).
- **Evidence.** Over a third of manufacturing requirements rest only on vendor and practitioner articles. Private Equity is about one in seven.
- **Maturity.** Private Equity has been through convergence passes and a comparison with DDA. Manufacturing has had one pass and its three blocking validation defects are open.

## Scope drift to resolve before the next pass

The package covers five subgroups equally (food and beverage, household and cleaning, personal care and cosmetics, pet care, beauty) and includes product definition (scope item SCI002), which the CPG - Product Definition model now owns. Items in this package that overlap that model:

- Domain `Products` and its concepts: `Product`, `ProductIdentifiers`, `ProductHazards`, `ProductSpecifications`, `ProductShelfLives`, `ProductStructureVersions`, `ProductSubstitutions`, `ProductVariantAxes`, `ProductIdentityChanges`, `ProductOrigins`, `ProductDisclosures`
- `DocumentDeclarations` and the supplier approval roles and relationships
- Data requirements met only by `Products` concepts: DRQ001 (recipe lines), DRQ009 (hazards and origin), DRQ010 (household disclosure), DRQ011 (shelf life), DRQ014 (sizes and identity changes), DRQ015 (recipe versions) and DRQ036 (cost). Met partly by them: DRQ005 (alternatives), DRQ012 (batch splits), DRQ013 (stock), DRQ025 (specifications and tests), DRQ030 (lot codes) and DRQ035 (identifiers). Cost (DRQ036) and batch-related items fit the manufacturing direction below rather than the product definition.

Direction stated for the manufacturing model: factories and the shop-floor location hierarchy, supplier sites, batches, packing and pack levels such as case and pallet, and the wider supply chain. This package splits plant structure (`Equipment`) from places (`Locations`), where the stated direction is a single location hierarchy that runs down to the shop floor.

## Not yet done

- `validation.json` records the blocking defects above and has not been re-run.
- The design document's introduction text reads "Supplied text not available" because the standard boilerplate was not available to the run.
- The change package was not compared with what DDA now holds, and nothing in it has been applied.
- Open decisions DEC001 to DEC008 in section 10 of the document are unanswered, including whether finished output is identified individually or by batch (SCQ001).
- The Events and Transactions domain definitions in DDA are written for financial services; broadening them is proposed (DEC008) and not decided.
- The generator scripts that produce these files are not in this folder.
