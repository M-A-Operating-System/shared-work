"""Take Ingredient out of the CPGProductType list (19 November 2026).

Usage: python3 apply_cpg_kind_roles.py <package-dir>

An ingredient is a role a product plays in the formulation relationship, so it is found from the formulations a product
appears in and is not recorded as a kind. The list keeps Logical and Local. A product that only goes into other products
has no kind, so the field is optional. DEC005 (sold and used as an ingredient) no longer arises and is withdrawn.
"""
from __future__ import annotations

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


lookups: list[Row] = load("lookups")
for l in lookups:
    if l["id"] == "LKP019":
        l["definition"] = ("The two kinds of consumer goods product that set a product apart by what it is: a grouping of related sizes and packs, and a "
                           "version that can be sold. You can rely on it to say which of the two a product is. It is not whether the product is an "
                           "ingredient, which is found from the formulations it appears in, nor the link from a version to its grouping, which is kept "
                           "separately between products.")
        l["values"] = [v for v in l["values"] if v["code"] != "INGREDIENT"]
        assert [v["code"] for v in l["values"]] == ["LOGICAL", "LOCAL"]
        l["reuse_search"] = ("Read the 83 lookup types in DDA; none lists whether a product is a grouping or a version that can be sold, "
                             "and no other list in this model does.")
        l["evidence_source_ids"] = ["SRC030", "SRC001"]
save("lookups", lookups)

subjects: list[Row] = load("subjects")
for s in subjects:
    if s["id"] == "SBJ022":
        s["definition"] = swap(s["definition"], "whether it is a Logical, Local or Ingredient product,", "whether it is a Logical or a Local product,")
save("subjects", subjects)

attrs: list[Row] = load("attributes")
for a in attrs:
    if a["id"] == "ATR098":
        a["definition"] = ("Whether the product is a Logical product, a grouping of related sizes and packs that is never sold, or a Local product, "
                           "a version of a logical product that can be sold, chosen from a list. A product that only goes into other products has "
                           "neither, because that it is an ingredient is found from the formulations it appears in. "
                           "This fact is kept in this one place for a product.")
        a["mandatory"] = False
        a["reuse_search"] = ("The parent is new to DDA, so it holds no attributes yet. The groupings and the versions are also found from the "
                             "arrangements between products, and this holds the kind the product is recorded as. "
                             "No other attribute in this model holds this fact.")
        a["evidence_source_ids"] = ["SRC030", "SRC001"]
save("attributes", attrs)

drqs: list[Row] = load("data-requirements")
for d in drqs:
    if d["id"] == "DRQ032":
        d["business_requirement_ids"] = ["REQ035", "REQ008"]
        d["must_record"] = ["For each consumer goods product, whether it is a grouping of related sizes and packs or a version that can be sold"]
        d["must_answer"] = ["Which of our products are groupings, and which are versions that can be sold?"]
save("data-requirements", drqs)

state: Row = load("state")
for sc in state["scenarios"]:
    if sc["id"] == "SCN043":
        sc["question"] = "Which products are groupings, and which are the versions that can be sold?"
        sc["path"] = ["SBJ001", "SBJ022", "ATR098", "REL002"]
dec5 = next(d for d in state["decisions"] if d["id"] == "DEC005")
state["decisions"] = [d for d in state["decisions"] if d["id"] != "DEC005"]
state["withdrawn_decisions"].append({**dec5, "status": "withdrawn",
    "withdrawn_reason": ("Ingredient is a role a product plays in the formulation relationship, so it is no longer a kind. A product sold and used as "
                         "an ingredient is a Local product and is an ingredient by its formulations.")})
for d in state["decisions"]:
    if d["id"] == "DEC006":
        d["question"] = ("A Local product is a version of a logical product that can be sold. A product that is sold in a single size and format has no "
                         "logical product above it. Should every sold product have a logical product above it, even where there is only one version, "
                         "or may a sold product stand alone?")
save("state", state)

scope: Row = load("scope")
for a in scope["assumptions"]:
    if a["id"] == "SCA018":
        a["statement"] = ("Product is used by every industry, so the facts only a consumer goods product has are held in its consumer goods definition. "
                          "The kind recorded there, Logical or Local, says what the product is in the business. The roles Logical Product and Variant "
                          "come from how products are arranged with one another, and the two are expected to agree; the design does not enforce it. "
                          "That a product is an Ingredient is a role found from the formulations it appears in, and is not recorded as a kind.")
scope["model"]["description"] = swap(scope["model"]["description"], "a Logical, Local or Ingredient product", "a Logical or a Local product")
save("scope", scope)
print("kind list reduced to Logical and Local")
