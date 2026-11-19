"""Make CPG - Product Definition the foundation of the manufacturing package (decision of 18 November 2026).

Product Definition owns the core product and the hierarchy of products and ingredients. Manufacturing refers to
that Product and holds the logistics of making finished products from ingredients.

Run once against the working copy named by common.PKG:
    python3 apply_foundation.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import PKG

Row = dict[str, Any]
OWNER = "CPG - Product Definition"
DECIDED = "2026-11-18"


def load(name: str) -> Any:
    return json.loads((Path(PKG) / f"{name}.json").read_text())


def save(name: str, data: Any) -> None:
    (Path(PKG) / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


WHY = (f"Held by {OWNER}, which owns the core product and the hierarchy of products and ingredients. "
       "This model refers to that Product.")

# ------------------------------------------------------------ subjects: Product becomes a reference
subjects: list[Row] = load("subjects")
for s in subjects:
    if s["id"] == "SBJ012":
        s.update({
            "definition": (f"One product, whether it is bought in, made or sold, as {OWNER} defines it. "
                          "This design uses it for the product a batch is of, the product a pack level is for and the product a production run makes."),
            "dda_action": "reuse", "dda_id": None,
            "proposed_by": OWNER,
            "reuse_search": (f"Searched DDA as read on 16 November 2026 for a concept named Product in DDA's Products domain; the domain holds no concepts. "
                             f"{OWNER} owns Product and the hierarchy of products and ingredients, and its change package creates the concept first. "
                             "This design refers to it and holds no concept of its own for it."),
        })
        s.pop("distinct_need", None)
save("subjects", subjects)

# ------------------------------------------------------------ attributes: what a product is belongs to Product Definition
attrs: list[Row] = load("attributes")
for a in attrs:
    if a["id"] in ("ATR017", "ATR018"):
        a.update({"status": "withdrawn", "withdrawn_reason": WHY})
save("attributes", attrs)

lookups: list[Row] = load("lookups")
for l in lookups:
    if l["id"] == "LKP001":
        l.update({"status": "withdrawn", "withdrawn_reason": WHY})
save("lookups", lookups)

# ------------------------------------------------------------ scenarios no longer walk the withdrawn attributes
state: Row = load("state")
for sc in state["scenarios"]:
    sc["path"] = [p for p in sc["path"] if p not in ("ATR017", "ATR018")]
for d in state["decisions"]:
    if d["id"] == "DEC009":
        d.update({"status": "decided",
                  "decision": (f"{OWNER} creates Product and holds the hierarchy of products and ingredients. "
                               "This model builds on it and holds the logistics of making finished products from ingredients."),
                  "by": "Andrew Bush", "date": DECIDED})
save("state", state)

# ------------------------------------------------------------ scope
scope: Row = load("scope")
assert not any(i["id"] == "SCI012" for i in scope["in_scope"])
scope["in_scope"].append({
    "id": "SCI012",
    "statement": (f"Turning ingredients into finished products: the logistics of receiving, making, packing and moving them, built on the product and the hierarchy "
                  f"of products and ingredients held by {OWNER}"),
})
scope["business"] = scope["business"].rstrip() + (f" What a product is and what goes into it is held by {OWNER}; this model holds the logistics of making "
                                                    "finished products from those ingredients.")
save("scope", scope)

sources: list[Row] = load("sources")
for s in sources:
    if s["id"] == "SRC005" and "SCI012" not in s["scope_ids"]:
        s["scope_ids"].append("SCI012")
save("sources", sources)
print("foundation applied")
