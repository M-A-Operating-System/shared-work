"""Record that Product Definition owns the core product and ingredient hierarchy (decision of 18 November 2026).

Usage: python3 apply_ownership.py <package-dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PKG = Path(sys.argv[1])


def load(name: str) -> Any:
    return json.loads((PKG / f"{name}.json").read_text())


def save(name: str, data: Any) -> None:
    (PKG / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


scope = load("scope")
assert not any(i["id"] == "SCI012" for i in scope["in_scope"])
scope["in_scope"].append({
    "id": "SCI012",
    "statement": ("The core product, and the hierarchy of what goes into what: which products and ingredients make up each product, to any depth. "
                  "This design holds both, and other models, including CPG Manufacturing and Supply Chain, refer to them and do not hold their own"),
})
save("scope", scope)

sources = load("sources")
for s in sources:
    if s["id"] in ("SRC002", "SRC003") and "SCI012" not in s["scope_ids"]:
        s["scope_ids"].append("SCI012")
save("sources", sources)

state = load("state")
for d in state["decisions"]:
    if d["id"] == "DEC004":
        d.update({
            "status": "decided",
            "decision": ("This model creates Product and holds the hierarchy of products and ingredients. "
                         "CPG Manufacturing and Supply Chain refers to them."),
            "by": "Andrew Bush",
            "date": "2026-11-18",
        })
save("state", state)
print("ownership applied")
