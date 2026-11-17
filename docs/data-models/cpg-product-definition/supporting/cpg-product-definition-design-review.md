# Review of the CPG - Product Definition Data Design Document, read as a client-ready final design

| | |
|---|---|
| Document reviewed | CPG - Product Definition Data Model Design Document, lite edition, package `fnb-bdd`, method version 31.5, regenerated 17 November 2026 (931 lines) |
| Location | `docs/data-models/cpg-product-definition/` in M-A-Operating-System/shared-work (pull request [#51](https://github.com/M-A-Operating-System/shared-work/pull/51)) |
| Review date | 17 November 2026 |
| Reviewed as | A senior business architect preparing the document for presentation to a client: is it true, is it defensible under questioning, and does it read as a design rather than a work report |
| Reviewed against | The package JSON; the sister design `../cpg-manufacturing/` and its [review](../../cpg-manufacturing/supporting/cpg-manufacturing-design-review.md); DDA as read on 16 November 2026; the primary sources linked in section 8 |
| Reviewer | Claude (the same agent that produced the package; **not an independent reader**) |

## 1 Conclusion

**The design is sound and close to presentable. It should not go to a client until six things are put right.** The structure is strong: 42 requirements each traced to a source, 27 data requirements, 20 concepts, and 35 of 38 test cases passing with the three failures recorded honestly as limits. The package passes the validator (0 blocking, 0 material). Definitions are written in the business's words, and the Manufacturing design's worst faults (93% mandatory attributes, "one record per" definitions, a status block) are absent. The weaknesses are in what the document *claims*:

1. **The headline question is overclaimed.** Section 1.3 opens with "We reformulate to cut sugar by 30%. Which claims and labels does that reach?" The model cannot answer it as stated (finding M01).
2. **The "worked out, never stored" statement is contradicted by the design.** Four derived values are stored as fields (M02).
3. **Claims and comparison rules rest on Australian and Hong Kong sources**, while the covered markets are the United States, the United Kingdom and the European Union. The governing EU/GB regulation and 21 CFR 101 are not cited (E01).
4. **A statement about Northern Ireland is unsupported and probably wrong** (S02). It matters now that the United Kingdom is explicitly in scope.
5. **Product is created by both CPG models** and the document does not say so (X01).
6. **The document names a DDA model that DDA names differently**, and I could not re-check it today (D01).

None needs a redesign. Findings M01 to M04 can be fixed in the package and the document regenerated; E01 to E03 need source work; X01 and D01 need a decision from Andrew.

## 2 Scope decision applied in this pass

Andrew's instruction of 17 November: the scope is **the United States, the United Kingdom and the European Union**. The model is designed to extend across regions, and other regions are deliberately not included.

| Where | What now says it |
|---|---|
| §2.2 In scope, new **SCI011** | The markets covered are the United States, the European Union and the United Kingdom: what a product must declare on pack, which allergens it must name, the language of the pack, who is named as responsible, and the dates and channels it is sold through there. Traced to SRC027, SRC028 and SRC039 |
| §2.3 Out of scope, new **SCO013** | Every other market, and its labelling rules. The design holds a market as a value in its lists, so it extends without a change of structure, but none is included by choice |
| §2.5 **SCA008** (rewritten) | "The markets covered are … and no others." The earlier wording called the three "samples" |
| §1.3 Summary | "The design covers three markets … and no others." It no longer says "shown with" |
| Version table | Document date is 17 November 2026 (it carried 11 November) |

The validator on the package after the change: 0 blocking, 0 material, 2 advisory. The document-level checks report the same hits as before (RN03 "changed" from the supplied §1.1 text, RN06, RN07 "review" from the supplied cover paragraph, ER02), and none from the new wording. A first wording ("can be added") tripped the change-vocabulary check, RN03, and was reworded.

Consequences of the decision are in findings S01 to S03 and E01.

## 3 The test applied

A client-ready final design states the design and nothing about how it was produced; every statement is true and checkable against a source; it holds the fewest roles, concepts and attributes that meet the requirements; and it can be defended line by line by the person presenting it. Severity:

- **Blocking**: a statement a client could show to be wrong, or a decision that must be taken before the document is shown.
- **Major**: needs rework before approval; can be presented with the caveat spoken aloud.
- **Minor**: correct in the same pass.

## 4 Findings

### 4.1 Scope and markets

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| S01 | Major | **The European Union is one market, but the language and responsible-business rules depend on the country.** SCA012 lists a product once for the Union and does not map member countries. REQ041 says label language is decided by the country where the food is sold, and REQ042 says the importer is named where the business is not established in the market. | A product sold in France and Germany has one market row. The design records a language for each label item (DRQ025), but cannot say which pack, in which language, is for which member country. | Either record this as a stated limit beside SCA012, or let a market row name a country inside a region. Decide before presenting; EU buyers will ask first. |
| S02 | Major | **SCA014 is unsupported and likely wrong.** "The United Kingdom keeps one allergen list, the list for Great Britain. Northern Ireland has no list of its own." | The cited FSA page covers Great Britain and mentions Northern Ireland only for goods moved under the Windsor Framework. [nibusinessinfo.co.uk](https://www.nibusinessinfo.co.uk/content/labelling-food-products) says "all food produced in Northern Ireland continues to apply EU food and feed law". It names no regulation, so the allergen list that applies in Northern Ireland is **not confirmed**. REQ040 and DRQ024 already say "Great Britain". | With the UK now in scope, state it plainly: either the UK market means Great Britain, or Northern Ireland follows the EU entry. Fetch the FSA or DAERA position before choosing. Remove the "has no list" sentence until it has a source. |
| S03 | Minor | The business statement still says the design "is shown with food and beverage products", while the markets are now stated as scope. | `scope.json` `business`. | State food and beverage as the covered subgroup, in the same words as the markets. Not changed in this pass. |

### 4.2 Evidence

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| E01 | Blocking | **Claims requirements rest on sources outside the covered markets.** REQ015 cites SRC012 (Centre for Food Safety, Hong Kong); REQ017 cites SRC013 (Australian Food and Grocery Council) alone; REQ018 cites SRC014 (Hong Kong). The package lists Regulation (EU) 1169/2011 and 21 CFR 101 as external standards but cites neither for claims. | [Article 9 of Regulation (EC) 1924/2006](https://legislation.gov.uk/eur/2006/1924/article/9/data.htm) requires comparisons between foods of the same category, taking account of a range of foods of that category, and a stated difference. I read this text; the 21 CFR 101.13 page was refused by the fetch tool and **was not read**. | Replace SRC012–SRC014 with the covered markets' own rules, cite 1924/2006 and 21 CFR 101, and re-test REQ015, REQ017 and REQ018 against them. |
| E02 | Major | **Source types are mislabelled, so the evidence looks stronger than it is.** Regask (SRC004, SRC005), Hogan Lovells (SRC008) and AFGC (SRC013) are typed "Regulator or law". SRC012 is a regulator typed "Industry standard"; SRC045 is an FAO news story typed "Industry standard". | `sources.json`: 21 regulatory, 12 standard, 9 practitioner, 1 reference model as typed. | Retype honestly and recompute. Where a requirement loses its only regulator, cite the primary text. |
| E03 | Major | **Five requirements rest on practitioner material only**: REQ006, REQ025, REQ031, REQ032 as typed, and REQ017 once AFGC is retyped. | Sources are a blog, a forum post, a vendor guide and a consultancy summary (SRC019, SRC020, SRC021, SRC026). The document says candidly for SRC021 and SRC026 that they are secondary. | Either find a primary or standard source, or mark the requirement as practitioner-based in its own row. |
| E04 | Major | **REQ009 is unverified.** It says a change to the net quantity makes a different product, and it is the basis of EXC001 and of the identity-changes concept. | The [GS1 decision page](https://gs1.org/1/hcgtinrules/en/decision-support/decision/4) sets the 20% threshold for dimensions and gross weight only, and refers net content to a separate "Declared Net Content" rule. I did not read SRC001 (GS1 UK handbook) itself. | Read the "Declared Net Content" rule in the GS1 standard and quote it, or restate REQ009. |
| E05 | Minor | **REQ004 is right but cites weak sources.** | [Annex VII Part A, row 6](https://www.legislation.gov.uk/eur/2011/1169/annex/VII): ingredients under 2% "may be listed in a different order after the other ingredients". The requirement cites a local-authority leaflet, a vendor (Regask) and Food Label Maker. | Cite Annex VII, and the 21 CFR 101.4 equivalent once read. |
| E06 | Verified | REQ040 and REQ047: Great Britain lists fourteen allergens, as does the European Union; the United States list has nine. | [FSA allergen labelling](https://food.gov.uk/business-guidance/allergen-labelling) (fourteen, "Directly applicable EU legislation no longer applies in GB"). | None. |

### 4.3 Model design

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| M01 | Blocking | **The headline question is overclaimed.** SCN023 passes on the reason that "the nutrition values, the ingredient order and every claim resting on them are worked out from the formulation". | A claim's condition (`ProductClaimsCondition`) is long free text, so no claim can be matched to the nutrient it rests on. The test path ends at `ProductClaimsConditionMet`, a stored yes/no. SCA003 says the calculation is not kept. What the model *can* do: list every claim and label item of the changed product, and of every product that uses it. | Reword the question to what it can answer ("which products, claims and label items sit downstream of this change"), and record SCN023 as an accepted limit, or hold the nutrient a claim rests on as a list value. |
| M02 | Major | **"Worked out and never stored" is contradicted.** The model description says which labels and claims a change reaches and which allergens must be declared "are worked out from these arrangements and never stored". Four attributes are `derived` and stored: `ProductCompositionDeclarationOrder`, `ProductClaimComparatorsDifference`, `ProductAllergensIsFromIngredient`, `ProductClaimsConditionMet`. Allergens are also kept as rows (SBJ005). | `attributes.json`, `nature` = derived: 4 of 85. | Remove the four fields and let consumers derive them, or reword the description and DRQ008/DRQ010 to say these are held as a convenience. |
| M03 | Major | **Cycle prevention is claimed "by structure" but is not structural.** DRQ001: "A product cannot be listed as an ingredient of itself, directly or through other products." The formulation version on a line (`ProductCompositionFormulationVersion`) is plain text, not a reference to SBJ003, so "every line belongs to exactly one version" is not enforced either. | REL001 is many-to-many, dated, with `is_composition` set. I could not confirm that DDA enforces a no-cycle rule for composition relationships. | Say who enforces both rules, or make the version a reference to the formulation-version concept. |
| M04 | Major | **`ProductIsLogical` stores a role on the subject.** The Logical Product role already says a product is one while it stands for a group, and DRQ019 says a product that is only a grouping is never made, bought or sold. | The method's role test: roles are never stored as a flag on the subject. | Withdraw the attribute, or record why a flag is needed beyond the role. |
| M05 | Major | **18 roles serve 9 relationships**, each relationship carrying its own pair. Twelve of the roles are played by a product: Made Product, Ingredient, Variant, Logical Product, Replaceable Ingredient, Permitted Alternative, Claiming Product, Comparator, Bought Material, Certification Holder, Labelled Product, Declared Product. | Same fault as Manufacturing F11 (70 roles for 38 relationships). Andrew's convention is one shared role per subject and capacity. | Challenge each pair. Candidates: Replaceable Ingredient and Permitted Alternative against Ingredient; Claiming Product and Comparator against one claim-comparison role. Keep a role only where the requirements treat the capacities as different. |
| M06 | Major | **Claim kinds stop at two** (nutrition content; comparative). Health claims and reduction-of-disease-risk claims are neither modelled nor excluded, and REQ019 (no medicinal claims) has no data. | Regulation 1924/2006 is the regulation on nutrition *and health* claims, and the European Union is in scope. | Add the kinds, or state in scope that health claims are not held. |
| M07 | Major | **The comparator rule is only half modelled.** One comparator product plus a free-text basis ("a named product, the average of leading brands, or a food composition database"). | Article 9 (above) also requires the same category of foods and account to be taken of a range. | Hold the category the comparison is made within, or state that the basis text carries it. |
| M08 | Minor | **Attributes are invisible in the lite edition.** 85 attributes (71% mandatory, 32 free text, 21 lists of values; Manufacturing: 93% and 43%) are counted but not shown, so a client cannot see what is kept. | `attributes.json`. | Offer the full edition at the presentation, or add a short attributes summary per concept. |
| M09 | Minor | **`CASE` in the unit-of-measure values** is a pack level, which SCO010 gives to Manufacturing. Same fault as Manufacturing F16. | §5.6, "Units of measure". | Remove `CASE` here and agree the shared list with Manufacturing (DEC003). |
| M10 | Minor | Lists used by relationship facts (LKP007 "Product Variants"; LKP010, LKP012 "Product Responsible Businesses") name groups of facts that are not in the concepts table. §5.6 explains it, but a reader cannot find them. | §5.6 introduction. | Name the relationship in the "Used for" column. |

### 4.4 Cross-model seam

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| X01 | Blocking | **Both CPG models create the `Product` concept** with different attributes, so the two change packages collide in DDA. §2.4 lists Products as shared and does not say Manufacturing also proposes it. DEC004 here matches DEC009 in `../cpg-manufacturing/`. | DDA's Products domain still holds no concept (read 16 November). | Decide: **Product Definition creates Product and Manufacturing refers to it.** This model owns what a product is. State it in §2.4 and close both decisions together. |
| X02 | Major | **The join between a batch and a formulation version is not stated.** SCN025 (batches containing a recalled ingredient) is an accepted limit that depends on it. Manufacturing holds recipe quantities, and SCA007 reads a bill of materials as the formulation held here, so the two hold the same quantities twice. | `../cpg-manufacturing/` recipe concepts. | Name the point of contact in §2.4 (a batch refers to a product and its formulation version) and remove the duplicated quantities from one side. |

### 4.5 Presentation

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P01 | Major | **The lite document fails three of the method's own rendering checks**, all from supplied house text: Appendix B and the full-edition section names (RN06), "review" in the cover paragraph (RN07), "changed" in §1.1 (RN03). | Validator with `--document`. The Manufacturing review recommended adding the principles appendix to match this design, so house practice and method v31.5 disagree. | Andrew to decide: keep Appendix B in the lite edition as house practice, or follow the method. Either way, record the decision. |
| P02 | Minor | The Version table shows the package reference `fnb-bdd`, an internal working name. | §Version. | Remove the row, or use the model's own name. |
| P03 | Minor | Typo in ROL001: "the parts of a finished product are found,." | §5.3. | Fix in the role definition. |
| P04 | Minor | All 18 role definitions end with the same "stops being … and the earlier … remains on record". | §5.3. | Keep it only where it adds meaning, or state it once above the table. |
| P05 | Minor | Identifier gaps (REQ034, REQ036–038, REQ044; SCI008; SCO009; SCA011; DRQ020–022, DRQ028; SBJ018; SRC031–034, SRC040) look like missing content. | Withdrawn items are never shown. | Add one line at the head of each table that numbers are not reused, or renumber. |
| P06 | Minor | Open matters sit in two sections: SCQ005 in §2.6 and DEC002, DEC004 in §6. | §2.6, §6. | Merge into §6. |

### 4.6 Fitness for DDA

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| D01 | Blocking | **The document names the DDA model "CPG - Product Definition (DMM000000005)"; DDA named it "CPG Food & Beverage Products" when read on 16 November.** | `scope.json` `model`; README. The DDA session lapsed, so the name was **not re-checked today**. | Reconnect DDA and read the record. Then update the DDA name, or reword §5. |
| D02 | Major | **The editorial review is stale and not independent.** It applies to the 10 November version; the document has since gained DEC004, the 16 November DDA reconciliation and today's scope change (validator ER02). | `supporting/editorial-review.md`. | A fresh reading by someone who did not produce the package, after the fixes above. |
| D03 | Minor | The change package (145 operations) is unapplied and its preconditions were last checked against DDA on 16 November. | `dda-changeset.json`. | Re-check after D01. |

## 5 What is sound and should be kept

- **Traceability.** Every requirement cites a source; every data requirement cites a requirement. Reused concept identifiers exist in DDA, and the Successor field `DMA000000910` exists.
- **The two-layer product** (versions each a product in their own right, a definition above them never sold) and its stated exception EXC001.
- **The allergen design**: a universal list of foods, a list per market that names the food each allergen is, and a contains / may-contain status (REQ045, REQ047). It is consistent with the EU and GB lists as read from the FSA page.
- **Honest limits**: a bought-in coating's contents, shelf life from ingredients, and batches within a recall are stated, not hidden.
- **Restraint**: no concept without an attribute except the three reused from DDA; only 8 of 85 attributes are classified internal and 45 critical, each tied to a legal or safety duty.

## 6 Recommended path

1. **Decide** D-1 to D-5 below.
2. **Fix in the package and regenerate:** M01–M04, M09, P02, P03, S03, P06.
3. **Re-source:** E01–E05, with S02 once the Northern Ireland position is read.
4. **Settle the seam with Manufacturing:** X01 and X02, together with DEC004 and DEC009.
5. **Reconnect DDA**, read DMM000000005, and close D01.
6. **Re-run the validator, then take an independent reading** of the regenerated document (D02).

## 7 Decisions needed from Andrew

| ID | Decision | Options | Reviewer's recommendation |
|---|---|---|---|
| D-1 | Which model creates Product? (DEC004 / DEC009) | Product Definition · Manufacturing | Product Definition |
| D-2 | Is the United Kingdom market Great Britain only, or does it include Northern Ireland? | Great Britain only · UK with Northern Ireland on the EU entry | Read the FSA/DAERA position first; if Northern Ireland follows EU law, the second |
| D-3 | Do health claims fall inside the scope? | In · out, stated | Out, stated, unless a client needs them |
| D-4 | Keep Appendix B in the lite edition? | Keep (house practice) · drop (method v31.5) | Keep, and record the exception |
| D-5 | Apply M01–M04 and regenerate? | Yes · wait for the decisions above | Yes: they do not depend on D-1 to D-4 |

## 8 Limits of this review

- **Not independent.** The same agent produced the package and read it.
- **DDA not reachable today.** The model name and the state of the Products domain rest on the 16 November read.
- **Sources partly verified.** Read and confirmed: [FSA allergen labelling](https://food.gov.uk/business-guidance/allergen-labelling), [Annex VII](https://www.legislation.gov.uk/eur/2011/1169/annex/VII), [Article 9 of 1924/2006](https://legislation.gov.uk/eur/2006/1924/article/9/data.htm), the [GS1 decision page](https://gs1.org/1/hcgtinrules/en/decision-support/decision/4) and [nibusinessinfo](https://www.nibusinessinfo.co.uk/content/labelling-food-products). **Not read:** 21 CFR 101.13 (the fetch was refused), the GS1 UK handbook, and the package's other 38 sources.
- **Northern Ireland** is not settled: the page I read says EU food law applies to food produced there but names no regulation.
- **Counts** are active items from the package JSON: 42 requirements, 27 data requirements, 20 concepts (4 reused), 18 roles, 9 relationships, 85 attributes, 18 lists of values, 43 sources, 38 test cases, 145 operations.

## Sources

- [Food Standards Agency — Allergen labelling](https://food.gov.uk/business-guidance/allergen-labelling)
- [Regulation (EU) 1169/2011, Annex VII (legislation.gov.uk)](https://www.legislation.gov.uk/eur/2011/1169/annex/VII)
- [Regulation (EC) 1924/2006, Article 9 (legislation.gov.uk)](https://legislation.gov.uk/eur/2006/1924/article/9/data.htm)
- [GS1 — GTIN decision support: when a change needs a new GTIN](https://gs1.org/1/hcgtinrules/en/decision-support/decision/4)
- [nibusinessinfo — Labelling food products (Northern Ireland)](https://www.nibusinessinfo.co.uk/content/labelling-food-products)
- [Review of the CPG Manufacturing design](../../cpg-manufacturing/supporting/cpg-manufacturing-design-review.md)
- [Package pull request #51](https://github.com/M-A-Operating-System/shared-work/pull/51)
