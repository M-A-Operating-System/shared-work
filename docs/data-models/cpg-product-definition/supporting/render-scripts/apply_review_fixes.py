"""Apply the architect-review fixes M01-M04, S03 and P03 to the Product Definition package (19 November 2026).

Usage: python3 apply_review_fixes.py <package-dir>

M01  A claim names the nutrient it rests on, so the claims a nutrient change reaches can be found; the stored
     "condition met" value, which cannot be worked out from a condition held as wording, is withdrawn.
M02  The model description no longer says allergens are never stored.
M03  The two formulation rules say what the structure does.
M04  The logical-product flag is withdrawn; the Logical Product role says it.
S03  The business statement says the design covers food and beverage products.
P03  Typo in the Made Product role.
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


# ------------------------------------------------------------------ attributes
attrs: list[Row] = load("attributes")
byid = {a["id"]: a for a in attrs}
assert "ATR097" not in byid
byid["ATR052"].update({
    "status": "withdrawn",
    "withdrawn_reason": ("The condition a claim rests on is held as wording, so whether the declared values meet it cannot be worked out. "
                         "The person responsible for the claim judges it from the nutrition values the claim names."),
})
byid["ATR070"].update({
    "status": "withdrawn",
    "withdrawn_reason": ("A product is a grouping while it plays the Logical Product role in the variants relationship. "
                         "The role says it, so a flag on the product would say it twice."),
})
attrs.append({
    "id": "ATR097", "subject_id": "SBJ008", "relationship_id": None, "code": "ProductClaimsNutrientType",
    "definition": ("The nutrient the claim is about, where it is about one, such as sugars for a claim of reduced sugar. "
                   "This fact is kept in this one place for a claim. It lets the claims that a change to a nutrient reaches be found."),
    "datatype": "LOOKUP", "lookup_id": "LKP003", "nature": "observed", "derived_from": [], "temporality": "as-at",
    "mandatory": False, "critical": True, "classification": "PUBLIC", "dda_action": "create", "dda_id": None,
    "reuse_search": ("The parent is new to DDA, so it holds no attributes yet. The nutrient list already in this model is used for its value. "
                     "No other attribute in this model holds this fact."),
    "data_requirement_ids": ["DRQ010", "DRQ009"], "evidence_source_ids": ["SRC013", "SRC014"],
    "status": "active", "withdrawn_reason": None,
})
save("attributes", attrs)

lookups: list[Row] = load("lookups")
for l in lookups:
    if l["id"] == "LKP003" and "DRQ010" not in l["data_requirement_ids"]:
        l["data_requirement_ids"].append("DRQ010")
save("lookups", lookups)

# ------------------------------------------------------------------ concepts
subjects: list[Row] = load("subjects")
for s in subjects:
    if s["id"] == "SBJ008":
        s["definition"] = swap(s["definition"],
                               "the wording, the condition the claim rests on, and whether the declared values still meet that condition.",
                               "the wording, the nutrient it is about where it is about one, and the condition it rests on.")
save("subjects", subjects)

# ------------------------------------------------------------------ data requirements
drqs: list[Row] = load("data-requirements")
for d in drqs:
    if d["id"] == "DRQ010":
        d["must_record"] = ["Each claim made, the market it is made in, the nutrient and condition it rests on, and the product it is compared with where it compares"]
        d["must_answer"] = ["Which claims does this pack make, and what does each rest on?"]
        d["must_prevent"] = ["A claim made without the condition it rests on being stated"]
        d["prevent_how"] = ["Every claim must state the condition it rests on."]
        d["prevent_resolution"] = [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR051"}]
    if d["id"] == "DRQ019":
        d["must_record"] = ["Which products are the sizes, formats and pack counts of one product definition",
                            "Which products are only groupings, never made, bought or sold"]
    if d["id"] == "DRQ001":
        d["prevent_how"] = [
            "The relationship is a composition, which cannot loop back on itself, so a product cannot be listed as an ingredient of itself, directly or through other products.",
            "Every line of a formulation carries the one version number it belongs to.",
        ]
save("data-requirements", drqs)

# ------------------------------------------------------------------ test cases
state: Row = load("state")
for sc in state["scenarios"]:
    if sc["id"] == "SCN010":
        sc["question"] = "Which claims does this pack make, and what does each rest on?"
    if sc["id"] == "SCN023":
        sc["path"] = ["REL001", "SBJ006", "SBJ008", "ATR097"]
        sc["reason"] = ("The sugars value, the claims resting on sugars and the label items of the product are found directly, "
                        "and so are the products that use it as an ingredient. Whether a claim still meets its condition after the change "
                        "is judged by the person responsible, because the condition is held as wording.")
    if sc["id"] == "SCN026":
        sc["path"] = [p for p in sc["path"] if p != "ATR070"]
save("state", state)

# ------------------------------------------------------------------ scope: assumption, business and model wording
scope: Row = load("scope")
assert not any(a["id"] == "SCA017" for a in scope["assumptions"])
scope["assumptions"].append({
    "id": "SCA017",
    "statement": ("Whether a claim still meets its condition is judged by the person responsible for the claim, from the nutrition values the claim names. "
                  "The condition is held as wording, and the design does not evaluate it."),
})
scope["business"] = swap(scope["business"], "this design is shown with food and beverage products",
                         "this design covers food and beverage products")
scope["model"]["description"] = swap(
    scope["model"]["description"],
    "Which labels and claims a change to a recipe reaches, which allergens a product must declare and which suppliers may supply an ingredient on a given date "
    "are worked out from these arrangements and never stored.",
    "Which labels and claims a change to a recipe reaches and which suppliers may supply an ingredient on a given date are worked out from these "
    "arrangements and not kept as facts of their own. The allergens a product declares are kept for each market, and the ingredient that brings each one is worked out from the formulation.")
save("scope", scope)

# ------------------------------------------------------------------ roles
roles: list[Row] = load("roles")
for r in roles:
    if r["id"] == "ROL001":
        r["definition"] = swap(r["definition"], "are found,.", "are found.")
save("roles", roles)
print("review fixes applied")
