"""Add the ProductCPGDefinition concept to the Product Definition package (19 November 2026).

Usage: python3 apply_cpg_definition.py <package-dir>

Product is used across industries, so the facts only a consumer goods product has move to a one-to-one child concept,
ProductCPGDefinition. The child carries a required CPGProductType drop-down: Logical, Local or Ingredient.

Moved from Product: ATR018 legal name, ATR019 net quantity, ATR020 unit of measure (identifiers kept, codes renamed).
New: SBJ022 ProductCPGDefinition, ATR098 CPGProductType, LKP019 ProductCPGDefinitionCPGProductTypes,
one data requirement, SCN043, DEC005, DEC006, SCA018.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

PKG = Path(sys.argv[1])
Row = dict[str, Any]


def load(name: str) -> Any:
    return json.loads((PKG / f"{name}.json").read_text())


def save(name: str, data: Any) -> None:
    (PKG / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def swap(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old[:60]
    return text.replace(old, new)


# ------------------------------------------------------------------ data requirement
drqs: list[Row] = load("data-requirements")
NEW_DRQ = f"DRQ{max(int(d['id'][3:]) for d in drqs) + 1:03d}"
drqs.append({
    "id": NEW_DRQ, "business_requirement_ids": ["REQ035", "REQ008", "REQ002"],
    "must_record": ["For each consumer goods product, whether it is a grouping of related sizes and packs, a version that can be sold, or an ingredient that goes into another product"],
    "must_answer": ["Which of our products are groupings, which are versions that can be sold, and which are ingredients?"],
    "temporality": "as-at", "must_prevent": [], "status": "active", "withdrawn_reason": None,
    "prevent_how": [], "prevent_resolution": [],
})
save("data-requirements", drqs)

# ------------------------------------------------------------------ lookup
lookups: list[Row] = load("lookups")
assert not any(l["id"] == "LKP019" for l in lookups)
lkp: Row = copy.deepcopy(next(l for l in lookups if l["id"] == "LKP018"))
lkp.update({
    "id": "LKP019",
    "code": "ProductCPGDefinitionCPGProductTypes",
    "definition": ("The three kinds of consumer goods product: a grouping of related sizes and packs, a version that can be sold, and something that goes "
                   "into another product. You can rely on it to say which of the three a product is. It is not the link from a version to its grouping, "
                   "nor the lines of a formulation, which are kept separately between products."),
    "scope": "concept",
    "values": [
        {"code": "LOGICAL", "name": "Logical",
         "definition": ("A product that stands for a group of related sizes, formats and pack counts, each of which is a product in its own right. "
                        "It holds what the versions share and is never made, bought or sold."), "parent_code": None},
        {"code": "LOCAL", "name": "Local",
         "definition": ("A version of a logical product that can be sold, such as one size, format or pack count of it. "
                        "It is sold and counted on its own."), "parent_code": None},
        {"code": "INGREDIENT", "name": "Ingredient",
         "definition": "A product that goes into another product, whether a raw material, a bought-in ingredient or a packaging item.",
         "parent_code": None},
    ],
    "reuse_search": ("Read the 83 lookup types in DDA; none lists whether a product is a grouping, a version that can be sold or an ingredient, "
                     "and no other list in this model does."),
    "data_requirement_ids": [NEW_DRQ, "DRQ019"],
    "evidence_source_ids": ["SRC030", "SRC001", "SRC002"],
})
lookups.append(lkp)
save("lookups", lookups)

# ------------------------------------------------------------------ concept
subjects: list[Row] = load("subjects")
assert not any(s["id"] == "SBJ022" for s in subjects)
for s in subjects:
    if s["id"] == "SBJ001":
        s["definition"] = swap(
            s["definition"],
            "It is not a batch, which is one production run of a product.",
            "It is not a batch, which is one production run of a product, and it is not the facts that only a consumer goods product has, "
            "which the product's consumer goods definition holds.")
subjects.append({
    "id": "SBJ022", "code": "ProductCPGDefinition",
    "definition": ("There is one of these for each product that the consumer goods business makes, buys or sells; a product of another industry has none. "
                   "You can rely on it for the facts only a consumer goods product has: whether it is a Logical, Local or Ingredient product, "
                   "the name the law requires on its pack, and how much its pack contains. It is not the product's own name and identity, "
                   "which every industry shares, and it is not what the product is made from, its allergens or its labels, which are kept separately."),
    "kind": "subject", "mastery": "mastered", "domain_id": "DOM001", "is_anchor": False,
    "parent_id": "SBJ001", "parent_cardinality": "ONE_TO_ONE_OPTIONAL", "singled_out_by": None,
    "independence": ("It is governed apart from the product, which every industry uses, and it is held only for products of the consumer goods business."),
    "distinct_need": "Holds the facts only a consumer goods product has, so that Product stays usable by every industry.",
    "used_here": None, "template_dda_id": None, "dda_action": "create", "dda_id": None,
    "reuse_search": ("Read the Products domain in DDA on 16 November 2026: it holds no concept. The Product concept in this model is used across industries, "
                     "so it cannot carry the facts only a consumer goods product has. No other concept in this model holds them."),
    "data_requirement_ids": [NEW_DRQ, "DRQ019", "DRQ007"],
    "evidence_source_ids": ["SRC030", "SRC001", "SRC002", "SRC006"],
    "status": "active", "withdrawn_reason": None,
})
save("subjects", subjects)

# ------------------------------------------------------------------ attributes
attrs: list[Row] = load("attributes")
byid = {a["id"]: a for a in attrs}
assert "ATR098" not in byid
for old_id, new_code in (("ATR018", "ProductCPGDefinitionLegalName"), ("ATR019", "ProductCPGDefinitionNetQuantity"),
                         ("ATR020", "ProductCPGDefinitionUnitOfMeasure")):
    a = byid[old_id]
    assert a["subject_id"] == "SBJ001"
    a["subject_id"] = "SBJ022"
    a["code"] = new_code
    a["reuse_search"] = ("The parent is new to DDA, so it holds no attributes yet. The fact is only true of a consumer goods product, "
                         "so it is held here and not on Product, which every industry uses. No other attribute in this model holds this fact.")
attrs.append({
    "id": "ATR098", "subject_id": "SBJ022", "relationship_id": None, "code": "ProductCPGDefinitionCPGProductType",
    "definition": ("Which of three kinds the product is, chosen from a list: Logical, a grouping of related sizes and packs that is never sold; "
                   "Local, a version of a logical product that can be sold; or Ingredient, a product that goes into another product. "
                   "This fact is kept in this one place for a product."),
    "datatype": "LOOKUP", "lookup_id": "LKP019", "nature": "observed", "derived_from": [], "temporality": "as-at",
    "mandatory": True, "critical": True, "classification": "PUBLIC", "dda_action": "create", "dda_id": None,
    "reuse_search": ("The parent is new to DDA, so it holds no attributes yet. The groupings of related sizes and packs, the versions and the ingredients are "
                     "also found from the arrangements between products, and this holds the kind the product is recorded as. "
                     "No other attribute in this model holds this fact."),
    "data_requirement_ids": [NEW_DRQ, "DRQ019"], "evidence_source_ids": ["SRC030", "SRC001", "SRC002"],
    "status": "active", "withdrawn_reason": None,
})
save("attributes", attrs)

# ------------------------------------------------------------------ state: tests, decisions, minimality
state: Row = load("state")
ids = [s["id"] for s in state["scenarios"]] + [s["id"] for s in state["withdrawn_scenarios"]]
assert "SCN043" not in ids
for sc in state["scenarios"]:
    if sc["id"] == "SCN007":
        assert sc["path"] == ["REL007", "SBJ007", "ATR018", "ATR019"]
        sc["path"] = ["REL007", "SBJ007", "SBJ022", "ATR018", "ATR019"]
state["scenarios"].append({
    "id": "SCN043", "question": "Which products are Logical, which are Local versions that can be sold, and which are Ingredients?",
    "data_requirement_ids": [NEW_DRQ], "kind": "designed", "as_at": "as-at",
    "path": ["SBJ001", "SBJ022", "ATR098", "REL002", "REL001"], "result": "pass", "reason": "",
})
dec_ids = [d["id"] for d in state["decisions"]] + [d["id"] for d in state["withdrawn_decisions"]]
assert "DEC005" not in dec_ids and "DEC006" not in dec_ids
state["decisions"] += [
    {"id": "DEC005",
     "question": ("The kind of a product is one value: Logical, Local or Ingredient. A product that is both sold in its own right and used as an ingredient "
                  "in another product, such as sugar sold to shoppers and used in a biscuit, has to be recorded as one of them. Should the kind hold one value, "
                  "or more than one?"),
     "options": ["One value, the kind the product is mainly managed as", "More than one value"],
     "raised_at_pass": 55, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC006",
     "question": ("A Local product is a version of a logical product that can be sold. A product that is sold in a single size and format has no logical product "
                  "above it. Should every sold product have a logical product above it, even where there is only one version, or may a sold product stand alone?"),
     "options": ["Every sold product has a logical product above it", "A sold product may stand alone, and is then Local without a logical product"],
     "raised_at_pass": 55, "status": "open", "decision": "", "by": "", "date": ""},
]
last = state["minimality"][-1]
state["minimality"].append({
    "pass": 55,
    "counts": {**last["counts"], "concepts": last["counts"]["concepts"] + 1, "attributes": last["counts"]["attributes"] + 1,
               "lookups": last["counts"]["lookups"] + 1},
    "merged": [], "withdrawn": [], "growth_justified_by": [NEW_DRQ],
})
state["pass"] = 55
save("state", state)

# ------------------------------------------------------------------ scope: assumption and model wording
scope: Row = load("scope")
assert not any(a["id"] == "SCA018" for a in scope["assumptions"])
scope["assumptions"].append({
    "id": "SCA018",
    "statement": ("Product is used by every industry, so the facts only a consumer goods product has are held in its consumer goods definition. "
                  "The kind recorded there, Logical, Local or Ingredient, says what the product is in the business. The roles Logical Product, Variant and "
                  "Ingredient come from how products are arranged with one another. The two are expected to agree, and the design does not enforce it."),
})
scope["model"]["description"] = swap(
    scope["model"]["description"],
    "and each Ingredient is itself a product. ",
    "and each Ingredient is itself a product. Product is used across industries, so what only a consumer goods product has, including whether it is a "
    "Logical, Local or Ingredient product, is held in its consumer goods definition. ")
save("scope", scope)
print("consumer goods definition applied")
