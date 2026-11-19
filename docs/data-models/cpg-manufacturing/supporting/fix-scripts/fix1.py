"""Stage 1 — evidence, scope and requirements (findings F01, F02, F04, F06, F17 to F20)."""
from __future__ import annotations

import shutil
from pathlib import Path

from common import PKG, TODAY, active, by_id, load, save, withdraw

PD = "Held by the CPG - Product Definition model, which owns what a product is, what it is made from and what it must be."
NF = "Outside the food and beverage focus of this model."

# ---------------------------------------------------------------- baseline: take the newer platform read
shutil.copy(Path(PKG.parent) / "pkgwork" / "baseline.json", PKG / "baseline.json")

# ---------------------------------------------------------------- sources
sources = load("sources")
S = by_id(sources)

RETYPE = {  # not regulators or standards bodies: relabelled to what they are
    "SRC010": "practitioner", "SRC019": "practitioner", "SRC020": "practitioner", "SRC022": "practitioner",
    "SRC025": "practitioner", "SRC027": "practitioner", "SRC032": "practitioner", "SRC035": "practitioner",
    "SRC036": "practitioner", "SRC037": "practitioner",
}
for sid, kind in RETYPE.items():
    S[sid]["type"] = kind

NEW_SOURCES = [
    {
        "id": "SRC041",
        "title": "Regulation (EC) No 178/2002, Article 18 — Traceability (Great Britain text)",
        "organisation": "UK Government (legislation.gov.uk, The National Archives)",
        "url": "https://www.legislation.gov.uk/eur/2002/178/article/18",
        "scope_ids": ["SCI007"], "type": "regulatory",
        "establishes": "A food business must be able to identify who supplied it and which businesses it supplied, must have systems that give that information to the authorities on demand, and must label or identify food placed on the market so that it can be traced.",
        "why_included": "The legal basis for one step back, one step forward traceability in Great Britain and, in the same words, the European Union. The package had no source outside the United States for traceability.",
    },
    {
        "id": "SRC042",
        "title": "Food traceability for businesses",
        "organisation": "UK Food Standards Agency (GOV.UK)",
        "url": "https://www.gov.uk/government/publications/food-traceability-for-businesses/food-traceability-for-businesses",
        "scope_ids": ["SCI007"], "type": "regulatory",
        "establishes": "Food businesses keep records that identify the supplier and customer, the product, the quantities, the delivery or dispatch dates and the batch, lot or consignment codes where they exist, and can produce them promptly when an authorised officer asks.",
        "why_included": "The United Kingdom regulator's statement of what a traceability record holds. It sets no retention period, so the design does not state one for the United Kingdom.",
    },
    {
        "id": "SRC043",
        "title": "FDA FSMA 204 Food Traceability Rule — compliance date of 20 July 2028",
        "organisation": "NC State Extension",
        "url": "https://foodbusiness.ces.ncsu.edu/news/fda-fsma-204-food-traceability-rule-july-20-2028/",
        "scope_ids": ["SCI007"], "type": "practitioner",
        "establishes": "The United States food traceability rule applies to foods on the FDA Food Traceability List, requires records within 24 hours of a request, and the FDA has proposed moving the compliance date from 20 January 2026 to 20 July 2028.",
        "why_included": "States which foods the rule covers and the date from which it applies. The date is a proposal in this source, so it is stated here as proposed.",
    },
    {
        "id": "SRC044",
        "title": "FDA document 183514 on the food traceability rule (electronic sortable spreadsheet within 24 hours)",
        "organisation": "US Food and Drug Administration",
        "url": "https://fda.gov/media/183514/download",
        "scope_ids": ["SCI007"], "type": "regulatory",
        "establishes": "During an outbreak, recall or other threat to public health, traceability information must be given to the FDA as an electronic sortable spreadsheet within 24 hours of its request, or within a reasonable time the FDA agrees.",
        "why_included": "The regulator's own statement of the 24-hour requirement, replacing reliance on trade summaries for that point.",
    },
    {
        "id": "SRC045",
        "title": "List of all ISA standards (ISA-88 batch control; ISA-95 enterprise-control system integration)",
        "organisation": "International Society of Automation (ISA)",
        "url": "https://isa.org/standards-and-publications/isa-standards/list-of-all-isa-standards",
        "scope_ids": ["SCI003", "SCI004"], "type": "standard",
        "establishes": "ISA publishes ISA-88 for batch control, including general and site recipe models and batch production records, and ISA-95 for enterprise-control system integration, which is also published as IEC 62264.",
        "why_included": "The publisher's own catalogue for the standards behind the recipe levels and the plant structure. It replaces a Wikipedia article as the source for ISA-88.",
    },
    {
        "id": "SRC046",
        "title": "FSMA Final Rule for Preventive Controls for Human Food",
        "organisation": "US Food and Drug Administration",
        "url": "https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-preventive-controls-human-food",
        "scope_ids": ["SCI001", "SCI006"], "type": "regulatory",
        "establishes": "Food manufacturers must have qualified and trained staff, a written food safety plan, documented corrective actions that keep food out of commerce when its safety cannot be assured, a supply-chain programme for the suppliers that control a hazard, and a recall plan.",
        "why_included": "The primary United States regulator source for good manufacturing practice, corrective action and supplier control in food. Most of the quality requirements rested on vendor and cosmetics-industry pages.",
    },
]
for s in NEW_SOURCES:
    s.update({"retrieved": TODAY, "status": "active", "withdrawn_reason": None})
    sources.append(s)
S = by_id(sources)
withdraw(S["SRC002"], "A Wikipedia article. Replaced by the publisher's own catalogue (SRC045).")

# ---------------------------------------------------------------- requirements
reqs = load("requirements")
R = by_id(reqs)
for r in reqs:
    r.pop("certified", None)

for rid in ("REQ002", "REQ003", "REQ004", "REQ005", "REQ008", "REQ011", "REQ012", "REQ015", "REQ019", "REQ020", "REQ021"):
    withdraw(R[rid], PD)
withdraw(R["REQ013"], NF)
withdraw(R["REQ014"], NF)
withdraw(R["REQ070"], "A cost is a calculation over what happened, not something observed. What happened is held; the sum is not.")

R["REQ007"]["statement"] = "Where a specified input is replaced on a batch, which input was actually used must be known."
R["REQ055"]["statement"] = "Some records must be signed, and the signing must show who signed, what was signed, when, and what the signing meant."
R["REQ057"]["statement"] = "Some steps must be checked by a second qualified person or by equipment qualified for the purpose."
R["REQ051"]["statement"] = "For foods covered by the United States food traceability rule, the records of what went into a batch and where it went must be produced within twenty-four hours of the regulator's request."
R["REQ051"]["source_ids"] = ["SRC009", "SRC010", "SRC044", "SRC043"]
R["REQ052"]["statement"] = "For foods covered by the United States food traceability rule, traceability records must be kept for two years."
R["REQ052"]["source_ids"] = ["SRC011", "SRC009"]
R["REQ068"]["statement"] = "Two records may turn out to describe the same place, supplier or machine, and one record then stands in for the other."

for rid in ("REQ046", "REQ047", "REQ048", "REQ049", "REQ058", "REQ059", "REQ064"):
    if "SRC046" not in R[rid]["source_ids"]:
        R[rid]["source_ids"].append("SRC046")
for r in reqs:
    if "SRC002" in r.get("source_ids", []):
        r["source_ids"] = [("SRC045" if x == "SRC002" else x) for x in r["source_ids"]]

reqs.append({"id": "REQ071", "category": "Quality", "statement": "A food business must be able to identify who supplied it and which businesses it supplied, and give that information to the authorities when asked.",
             "owner": "Regulatory lead", "subgroup_id": None, "satisfied_by": "model", "source_ids": ["SRC041", "SRC042"], "status": "active", "withdrawn_reason": None})
reqs.append({"id": "REQ072", "category": "Product identity", "statement": "A product is packed in levels — a single unit, a case of units, a pallet of cases — and each level is identified, counted and moved as a thing in its own right.",
             "owner": "Supply chain lead", "subgroup_id": None, "satisfied_by": "model", "source_ids": ["SRC030", "SRC031"], "status": "active", "withdrawn_reason": None})

# sources no longer cited by an active requirement are withdrawn, never deleted
cited = {sid for r in active(reqs) for sid in r["source_ids"]}
for s in sources:
    if s.get("status", "active") == "active" and s["id"] not in cited:
        withdraw(s, "No active requirement cites it after the scope was narrowed to food and beverage and product definition moved to CPG - Product Definition.")

# ---------------------------------------------------------------- data requirements
drqs = load("data-requirements")
D = by_id(drqs)
for did in ("DRQ001", "DRQ002", "DRQ003", "DRQ009", "DRQ010", "DRQ011", "DRQ014", "DRQ015"):
    withdraw(D[did], PD)
withdraw(D["DRQ036"], "Cost is not held in this model (REQ070 is withdrawn).")

D["DRQ004"]["must_record"] = ["The quantity the recipe called for, as it stood when the batch was made", "The quantity each batch actually used"]
D["DRQ004"]["business_requirement_ids"] = ["REQ006", "REQ022"]

D["DRQ005"].update({
    "business_requirement_ids": ["REQ007"],
    "must_record": ["Which input actually filled each place in the recipe on each batch, and whether it was the specified input or an alternative"],
    "must_answer": ["Which batches used an alternative input, and for which ingredient?"],
    "must_prevent": ["A batch that used an alternative input with nothing recording that it did"],
    "prevent_resolution": [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR122"}],
})
D["DRQ006"].update({
    "business_requirement_ids": ["REQ058"],
    "must_record": ["Each assessment of a supplier or outside manufacturer, its scope and how long it is valid"],
    "must_answer": ["Did this supplier hold a valid assessment on the day a delivery was received?"],
    "must_prevent": ["An assessment treated as current after it lapsed"],
    "prevent_resolution": [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR081"}],
})
D["DRQ035"].update({
    "business_requirement_ids": ["REQ067", "REQ069"],
    "must_record": ["The identifiers each place and each machine carries, and who issued each"],
    "must_answer": ["Which place or machine is this, whatever identifier the supplier or regulator used?"],
})
D["DRQ030"]["business_requirement_ids"] = sorted(set(D["DRQ030"]["business_requirement_ids"]) | {"REQ071"})
drqs.append({"id": "DRQ037", "business_requirement_ids": ["REQ072"],
             "must_record": ["Each level a product is packed in, such as unit, case and pallet", "How many of the next level down each level holds"],
             "must_answer": ["How many units are in a case of this product, and how many cases on a pallet?"],
             "temporality": "current",
             "must_prevent": ["A level that holds nothing, or holds itself"],
             "status": "active",
             "prevent_resolution": [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR125"}],
             "withdrawn_reason": None})

# ---------------------------------------------------------------- scope
scope = load("scope")
scope.pop("mode", None)
scope.pop("certifier", None)
scope["domain"] = "CPG Manufacturing and Supply Chain"
scope["business"] = ("A manufacturer of food and beverage products. It receives materials, makes, packs and tests product, "
                     "and releases it for despatch, through its own factories and through outside manufacturers.")
scope["subgroups"] = [{"id": "SCG001", "name": "Food and beverage", "is_primary": True}]
scope["in_scope"] = [
    {"id": "SCI001", "statement": "Receiving materials from suppliers, and assessing the suppliers"},
    {"id": "SCI003", "statement": "Defining how products are made — the steps, the settings and the recipes"},
    {"id": "SCI004", "statement": "The places in each factory down to the shop floor, and the machines in them"},
    {"id": "SCI005", "statement": "Making product, and what each batch actually used and produced"},
    {"id": "SCI006", "statement": "Testing, recording problems, putting them right, and releasing product"},
    {"id": "SCI007", "statement": "Tracing any batch back to its ingredients and forward to where it went"},
    {"id": "SCI008", "statement": "Stock held at the organisation's own sites"},
    {"id": "SCI009", "statement": "Product made or packed by outside manufacturers"},
    {"id": "SCI010", "statement": "Packing, and the levels a product is packed in for handling — unit, case and pallet"},
    {"id": "SCI011", "statement": "The sites that suppliers and outside manufacturers make and ship from"},
]
scope["out_of_scope"] = scope["out_of_scope"] + [
    {"id": "SCO007", "statement": "Defining products — what they are made from, what they must be, how long they last and what their packs say", "owned_by": "The CPG - Product Definition model"},
    {"id": "SCO008", "statement": "The total cost of poor quality, and any other cost worked out by adding up what happened", "owned_by": "The finance model"},
    {"id": "SCO009", "statement": "Household and cleaning products, personal care and cosmetics, pet care and beauty", "owned_by": "A later extension of this model"},
]
scope["shared_objects"] = scope["shared_objects"] + [
    {"id": "SCS006", "name": "Products", "dda_id": "DMD000000032"},
    {"id": "SCS007", "name": "Locations", "dda_id": "DMD000000034"},
]
scope["candidate_dda_domains"] = scope["candidate_dda_domains"] + ["DMD000000032", "DMD000000034"]
scope["assumptions"] = [a for a in scope["assumptions"] if a["id"] != "SCA004"] + [
    {"id": "SCA004", "statement": "The product definition — what a product is made from, what it must be, how long it lasts and what its pack says — is held by CPG - Product Definition. This model refers to a product and does not define it again."},
    {"id": "SCA005", "statement": "A manufacturing bill of materials is read as the formulation held in CPG - Product Definition. This model holds how a batch compares with it: what was used, and in what quantity."},
    {"id": "SCA006", "statement": "Food traceability duties differ by market. The United States, the United Kingdom and the European Union are the sample markets, and others are added by adding requirements, not by changing the design."},
    {"id": "SCA007", "statement": "Costs are not held. What each stoppage, failure, rework and complaint was is recorded; adding them up is a calculation outside this model."},
]
scope["questions_unanswered"] = [q for q in scope["questions_unanswered"] if q["id"] != "SCQ003"]

for name, data in (("sources", sources), ("requirements", reqs), ("data-requirements", drqs), ("scope", scope)):
    save(name, data)
print("stage 1 done:", len(active(reqs)), "active requirements,", len(active(drqs)), "active data requirements,",
      len(active(sources)), "active sources")
