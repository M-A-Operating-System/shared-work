# Editorial review — CPG Food and Beverage — Product and Ingredient Data Model Design Document, lite edition (third reading)

| | |
|---|---|
| Document reviewed | `fnb-product-data-design-document-lite.md` |
| SHA-256 before the review | `8346c18809d241796b1fe3cbc346c8f5c74b2e52a8fb6594b4e2db7731bbf59f` |
| Reviewed | 10 November 2026 |
| Reviewer | A same-agent read. **Not independent.** The agent that rebuilt the document also wrote this review. |
| Earlier review | `archive/previous-version-2026-09-28/editorial-review.md`, of the previous version of this document. It applied to that version only. |
| Wording adjusted after the read | Before the hash above was taken, six wordings were tightened where the read had found them to be process vocabulary (*approved*, *certified*, *added*) and the places re-read. The hash is of the final document. |
| After the read | The full reading covered the 10 November version. The 11 November version differs in these places only, and only they were read again: the name and cover details, sections 2.3 and 2.4 (scope entries SCO011, SCO012, SCA008, SCA014 to SCA016, SCQ005), requirements REQ045 to REQ047 and data requirements DRQ029 to DRQ031, the Product Allergens, Product Nutrition Values and Product Shelf Lives definitions, five lists (universal allergens, allergens by market, whether an allergen is contained or may be present, the country list note and wider markets), and sources SRC043 to SRC048. REQ044, DRQ028 and the country-to-region mapping are gone. |
| What this review changes | Nothing. The document was hashed before this was written and is checked again after. |
| What changed in the document since the second reading | Products are held in two layers (a product definition above its sizes and packs). A product is listed in markets, each a country or a wider region, with sales channels beneath the listing. Product pictures are a concept. The United Kingdom is a third market, with its own allergen list. A list of world regions is created and every country is placed in one. Requirements run to REQ044, data requirements to DRQ028, sources to SRC042. Then: each of the twenty roles ends with a sentence saying when something stops playing it; section 5 now states the model DDA already holds for this field (DMM000000005) and quotes its description; the summary counts the roles and the model. Factories, the places inside them down to the shop floor, supplier sites, batches and supply chain detail are out of scope and owned by the detailed manufacturing model; the Locations area, the site and operating-business roles, four site relationships, the location concept, three data requirements, three business requirements and their test cases are no longer in the document, and a supplier is held only as a company. Section 2.1 now describes the business as consumer packaged goods and says the design records the product definition, its variants and its ingredients, and not how a product is made. The scope lines are aligned to it: the first two in-scope lines name variants and the formulation, the factory and supplier-site lines are folded into the manufacturing lines with the owner named the CPG Manufacturing model, and the assumption on manufacturing bills of materials is restated. The owner of what the design leaves out is now the proposed CPG Manufacturing and Supply Chain model, which also takes packing and pack levels such as case and pallet; the named successor of a product is stated as a general capability and not product information, with an open question (SCQ005) on where it is defined. The change list is 388 steps (eighteen role creates, nine relationship creates, sixteen concept creates and one model update). |

## 1 The reading

The document still reads in the right order and in one voice. The first page says what the design is and defines DDA, and section 1.3 is again the strongest part: what the design covers, the two-layer product idea, the three limits, six questions the business can put to it, and a count of what would be created in DDA. The new material is written in the same plain register as the rest, and the counts in 1.3 agree with the tables in section 5 (sixteen new concepts of twenty, nine relationships, sixteen lists of which thirteen are new).

The additions carry through the document without a seam. Each new requirement (REQ035 to REQ044) has its sources, each new data requirement names the mistakes it prevents and how, and each new concept and role has the "It is not a …" boundary sentence. A reader who follows a market from the summary to REQ039, DRQ023, the Product Markets concept and the Regions list finds the same story at every stop.

Where it loses a reader: section 5.6 now carries a thirty-value region list whose twenty-two regional definitions differ only by name, followed by a table of country counts that restates it. A careful reader skims both. The United States, European Union and United Kingdom are named as markets in the summary and scope, but the allergen list and one data requirement speak of Great Britain, so a reader has to work out that one is the other (SCQ004 now says so, but only in section 2.6). Section 1.2, which is supplied text, still describes a lifecycle-events step that no section reports.

## 2 Findings

**F01 — clarity — 1.3, 2.5 (SCA008) against 5.6 (allergens by market) and 4 (DRQ024)**

> "the United States, the European Union and the United Kingdom" … "Great Britain. Declared as celery."

- **What is wrong.** The market is named the United Kingdom, and the allergen values, requirement REQ040 and DRQ024 say Great Britain. Nothing in the main text says the second stands for the first. Only the open question SCQ004 touches it.
- **What a reader takes away.** That the United Kingdom and Great Britain are two different markets, or that Northern Ireland has been left out without saying so.
- **Suggested wording.** One sentence in 5.6 under the allergen list: "The Great Britain list is the list used for the United Kingdom market."
- **Cost.** wording only, no artefact changes

**F02 — substance — 5.6, Regions of the world**

> "Region of Africa in the United Nations list." (repeated, with the continent changed, for twenty-two regions)

- **What is wrong.** The regional meanings say only that each is a region of its continent, and the table of country counts that follows restates the same names, continents and parents.
- **What a reader takes away.** A long list that tells them nothing the count table does not, and a reason to skip the section.
- **Suggested wording.** Fold the meaning into the count table, and keep the list of values for the seven continents and the European Union only.
- **Cost.** a definition to rewrite (step 8)

**F03 — clarity — 5.6, Regions of the world, closing paragraph**

> "Each country in the country list sits in one region, and each region on one continent."

- **What is wrong.** Antarctica is the exception: its country entry sits directly under the continent, as the Antarctica value says several rows earlier. The count table then lists Antarctica as though it were a region.
- **What a reader takes away.** A rule with an unstated exception, and a table that does not match the rule.
- **Suggested wording.** "Each country sits in one region, except Antarctica, which sits directly under its continent."
- **Cost.** wording only, no artefact changes

**F04 — clarity — 4, DRQ023, and 5.5, Product Markets**

> "A market named by neither a country nor a region, or by both"

- **What is wrong.** A continent is also a value in the region list, so a market could be named "Europe" or "Africa". The document never says whether that is intended.
- **What a reader takes away.** That a whole continent can be a market, which is not what the requirement (a country or a wider region) suggests.
- **Cost.** a requirement to restate (step 3), or a note in 5.6 that continents are there to place regions and not to name markets

**F05 — language — 5.2, 5.3, 5.5 section headings; 5.3 title**

> "### 5.3 Canonical Roles"

- **What is wrong.** *Canonical* is modelling vocabulary, and the heading is fixed by the method's document layout. It was raised in the earlier reading and is unchanged.
- **Suggested wording.** *Roles*.
- **Cost.** document binding, which is how the method renders the document and sits outside the model

**F06 — language — Appendix A, SRC040**

> "Industry standard"

- **What is wrong.** The United Nations list of country and area codes is an international statistical standard, not an industry one.
- **What a reader takes away.** A small mismatch of kind, which makes a reader doubt the other labels.
- **Cost.** wording only, no artefact changes

**F07 — structure — 5.1.3, Products concept diagram**

- **What is wrong.** All fourteen arrows carry the same label, and the diagram now holds fifteen boxes. It shows that Product Markets sits between a product and its label items, claims and channels, but a reader has to find that out from the lines.
- **What a reader takes away.** A diagram that repeats the table.
- **Cost.** wording only; in the earlier reading this was already a partial finding (F28)

**F08 — clarity — 5 (The model) and 5.4**

> "The design gathers the thirteen relationships in 5.4 into it"

- **What is wrong.** The model description is quoted in section 5, but the table in 5.4 does not show the longer description each relationship carries in DDA (what it holds "for as long as", what it does not cover, and how to tell it apart). A reader sees the model's summary and the one-line readings, not the middle layer.
- **What a reader takes away.** That the relationships have no meaning beyond their two sentences.
- **Cost.** a column to add to 5.4, or a note that the full wording is in the change list

**Carried from the earlier reading.** Section 1.2 describes a lifecycle-events step that the design does not report (assumption SCA005 now says so). The roles are still eighteen definitions for nine relationships. The owners are job titles proposed from the sources. Nothing in the document says who decides the open decision DEC002, or by when.

## 3 Design observations

These are questions about the model itself, not defects in the document.

1. **A European Union listing and a listing for a member country are unrelated.** The Union is treated as one market (assumption SCA012) and its member countries are not mapped to it, so a product listed for Germany is not found by a question about the Union. That follows from the choice, but a business reader may expect it.
2. **Product definitions and sellable products are one concept.** A product definition that is "never made, bought or sold" lives beside the products that are. The roles tell them apart, but nothing in the concept itself stops an ingredient line pointing at a product definition. Is the role enough?
3. **A country's parent region is held as a value of a different list.** Whether DDA allows a value of one list to name a value of another as its parent is not established by anything read.

## 4 What works

- **Section 1.3.** The summary agrees with the body, which is the test of a summary. Do not disturb it.
- **The boundary sentence** ("It is not a …") on every concept and role, including the new ones.
- **The *Must answer* and *How the design prevents them* columns.** The new mistakes (a product in two product definitions, two businesses named responsible, two current pictures of one side) read as plain business rules.
- **The scope tables.** The in-scope and out-of-scope lines draw the boundary at factories, supplier sites, markets and pictures cleanly.
- **Internal links and numbering.** Every link resolves and the numbering runs straight through.

## 5 Every numbered section and appendix

The cover paragraph · Version · Table of Contents · 1 Introduction · 1.1 · 1.2 · 1.3 · 2 Scope · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 · 2.6 · 3 Business Requirements · 4 Data Requirements · 5 Data Model · 5.1 · 5.1.1 · 5.1.2 · 5.1.3 · 5.2 · 5.3 · 5.4 · 5.5 · 5.6 · 6 Outstanding Decisions · Appendix A · Appendix B (Data Modelling Principles, with the table of exceptions) — all read.
