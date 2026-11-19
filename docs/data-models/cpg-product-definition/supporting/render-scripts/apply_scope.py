"""Make the three covered markets an explicit scope statement in the Product Definition package.

Usage: python3 apply_scope.py <package-dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PKG = Path(sys.argv[1])
MARKETS = "the United States, the European Union and the United Kingdom"

scope: dict[str, Any] = json.loads((PKG / "scope.json").read_text())

assert not any(i["id"] == "SCI011" for i in scope["in_scope"])
scope["in_scope"].append({
    "id": "SCI011",
    "statement": (f"The markets covered: {MARKETS}. For each, what a product must declare on pack, which allergens it must name, "
                  "the language of the pack and who is named on it as responsible, and the dates and channels it is sold through there"),
})

assert not any(i["id"] == "SCO013" for i in scope["out_of_scope"])
scope["out_of_scope"].append({
    "id": "SCO013",
    "statement": (f"Every market other than {MARKETS}, and the labelling rules of those markets. "
                  "The design is built so that a country or a wider region can be added by adding values to its lists, without changing its structure, "
                  "but none is included here by choice."),
    "owned_by": "Not owned by another model. Left for a later extension",
})

for a in scope["assumptions"]:
    if a["id"] == "SCA008":
        a["statement"] = (f"The markets covered are {MARKETS}, and no others. A market is a country, or a wider region of the world, in which a product is intended to be sold. "
                          "Requirements, allergen lists and label rules are provided for these three markets only. "
                          "The design can hold any other country or wider region in the same way, by adding a value to the lists, so it can be extended without being changed. "
                          "No other market is included here by choice.")
(PKG / "scope.json").write_text(json.dumps(scope, indent=2, ensure_ascii=False) + "\n")

OLD = "and the three markets are samples."
NEW = "and the design covers three markets."
for name in ("scope", "sources", "requirements", "data-requirements"):
    p = PKG / f"{name}.json"
    t = p.read_text()
    p.write_text(t.replace(OLD, NEW))
print("scope applied")
