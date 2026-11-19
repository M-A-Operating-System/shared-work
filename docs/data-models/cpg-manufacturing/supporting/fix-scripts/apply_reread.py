"""Reconcile the manufacturing package with DDA as read on 16 November 2026.

Run once against the working copy named by common.PKG:
    python3 -I apply_reread.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from common import PKG

READ_DATE = "2026-11-16"
OLD_BASE = "the DDA baseline read on 28 September 2026"
NEW_BASE = "DDA as read on 16 November 2026"
DDA_CONCEPTS = Path("/tmp/dda-concepts.json")
LOOKUP_TYPES = Path("/root/.claude/projects/-home-claude/4770b2d2-f54e-5ec8-aa89-f4fc7cefb22c/tool-results/toolu_01MMK4kYw9HdCPT58qxNP7Pv.json")

Row = dict[str, Any]


def load(name: str) -> Any:
    return json.loads((Path(PKG) / f"{name}.json").read_text())


def save(name: str, data: Any) -> None:
    (Path(PKG) / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def by_id(rows: list[Row]) -> dict[str, Row]:
    return {r["id"]: r for r in rows}


def rebase(obj: Any) -> Any:
    """Replace the old baseline wording in every reuse_search string."""
    if isinstance(obj, dict):
        return {k: (v.replace(OLD_BASE, NEW_BASE) if k == "reuse_search" and isinstance(v, str) else rebase(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rebase(v) for v in obj]
    return obj


# ----------------------------------------------------------------- checks against the DDA read
dda_concepts: list[Row] = json.loads(DDA_CONCEPTS.read_text())
dda_codes = {c["concept_code"] for c in dda_concepts}
dda_ids = {c["concept_id"] for c in dda_concepts}
subjects: list[Row] = load("subjects")
for s in subjects:
    if s["status"] != "active":
        continue
    if s["dda_action"] == "reuse":
        assert s["dda_id"] in dda_ids, f"{s['id']} reuses {s['dda_id']}, which DDA does not hold"
    elif s["id"] != "SBJ046":
        assert s["code"] not in dda_codes, f"{s['id']} {s['code']} collides with a DDA concept code"
assert "DMC000000031" in dda_ids

# ----------------------------------------------------------------- subjects
sb = by_id(subjects)
old = sb["SBJ046"]
movement: Row = {
    **old,
    "id": "SBJ068",
    "code": "TransactionGoodsMovements",
    "definition": ("There is one of these for each time goods are received, issued, moved, bought or despatched, with the time it happened. "
                   "If you need to know where goods went and when, this is what you go by. How much of an item is held at a point in time is held as stock positions. "
                   "It is a movement of goods; a movement of money or of a holding is the transaction it sits beneath."),
    "is_anchor": False,
    "parent_id": "SBJ046",
    "parent_cardinality": "ONE_TO_ONE_OPTIONAL",
    "singled_out_by": None,
    "independence": ("The movement lines, the places goods moved from and to, the products moved and the parties to the movement all refer to it, "
                     "and DDA's transaction is for money and holdings, so these facts cannot sit on it."),
    "dda_action": "create",
    "dda_id": None,
    "reuse_search": (f"Searched {NEW_BASE} for a concept holding movements of goods. Transaction (DMC000000031) and TransactionLeg (DMC000000032) hold movements of money "
                     "and holdings between two parties, with legs that balance, so goods movements are created beneath Transaction as the more specific kind its definition anticipates. "
                     "Searched this model's own concepts for the same need; none holds it."),
    "distinct_need": "Holds each movement of goods; DDA's transaction holds movements of money and holdings, and stock held is a separate count.",
    "data_requirement_ids": ["DRQ024", "DRQ033"],
}
old.update({
    "definition": ("There is one of these for each movement of money or of a holding between two parties on a date. If you need to know what moved, between whom and when, this is what you go by. "
                   "A holding's balance is worked out from these and is not kept here; the more specific kinds, such as movements of goods, are held beneath it."),
    "dda_action": "reuse",
    "dda_id": "DMC000000031",
    "reuse_search": f"Searched {NEW_BASE}: Transaction is held by DDA and is reused as it stands.",
    "data_requirement_ids": ["DRQ024"],
})
old.pop("distinct_need", None)
subjects.append(movement)
sb = by_id(subjects)
sb["SBJ047"]["parent_id"] = "SBJ068"
sb["SBJ047"]["code"] = "TransactionGoodsMovementLines"
sb["SBJ043"]["reuse_search"] = (f"Searched {NEW_BASE} for a concept named Location or Place in DDA's Locations domain; the domain holds no concepts. "
                                "Searched this model's own concepts: the places in the plant that were held separately are merged here.")
sb["SBJ012"]["reuse_search"] = (f"Searched {NEW_BASE} for a concept named Product in DDA's Products domain; the domain holds no concepts. "
                                "Searched this model's own concepts for the same need; none holds it.")
sb["SBJ049"]["reuse_search"] = (f"Searched {NEW_BASE} for a concept named Event in DDA's Events domain; the domain holds no concepts. "
                                "Searched this model's own concepts for the same need; none holds it.")
save("subjects", rebase(subjects))

# ----------------------------------------------------------------- domains
domains = load("domains")
for d in domains["domains"]:
    if d["id"] == "DOM005":
        d["subject_ids"] = ["SBJ046", "SBJ068", "SBJ047", "SBJ048"]
        d["used_here"] = "Holds the exchanges of goods the organisation records, with their lines and the stock position each one leaves."
save("domains", rebase(domains))

# ----------------------------------------------------------------- attributes
renames = {"TransactionKind": "TransactionGoodsMovementsKind", "TransactionOccurredAt": "TransactionGoodsMovementsOccurredAt",
           "TransactionTitlePassesOnReceipt": "TransactionGoodsMovementsTitlePassesOnReceipt",
           "TransactionLinesQuantity": "TransactionGoodsMovementLinesQuantity"}
attrs: list[Row] = load("attributes")
for a in attrs:
    if a["code"] in renames:
        a["code"] = renames[a["code"]]
    if a["id"] in ("ATR085", "ATR086", "ATR087"):
        a["subject_id"] = "SBJ068"
save("attributes", rebase(attrs))

# the renamed codes also appear in lists of values and in the state's test-case text
for name in ("lookups", "state", "data-requirements", "requirements"):
    text = json.dumps(load(name), ensure_ascii=False)
    for old_code, new_code in renames.items():
        text = re.sub(rf"(?<![A-Za-z]){old_code}(?![A-Za-z])", new_code, text)
    save(name, json.loads(text))

# ----------------------------------------------------------------- roles (DDA holds the wording on its relationships)
roles: list[Row] = load("roles")
RENAME: dict[str, tuple[str, str, str, str, str]] = {
    "ROL037": ("Organization Employee", "Organization Employees", "DMO000000001",
               "A person is an Organization Employee while it works for a company. It says that the person is employed by a company. "
               "That is not the same as being a Performer, which says a person who did a piece of work, whoever employs them.", "OrgEmployee"),
    "ROL038": ("Organization Employer", "Organization Employers", "DMO000000002",
               "A company is an Organization Employer while it employs people. It says that the company has people working for it. "
               "That is not the same as being a Site Operator, which says a company that runs a place, whether or not it employs the people in it.", "OrgEmployer"),
    "ROL041": ("Transaction", "Transactions", "DMO000000016",
               "A movement of goods is a Transaction while it records goods moving between places and companies. It says that goods moved, and when. "
               "That is not the same as being a Production Run, which says goods made, not moved.", "Transaction"),
    "ROL042": ("Transaction Party", "Transaction Parties", "DMO000000017",
               "A company is a Transaction Party while it is on the other side of a movement of goods. It says that the company sold to, bought from or received goods from the organisation. "
               "That is not the same as being an Outside Manufacturer, which says a company that makes goods for the organisation under contract.", "TransactionParty"),
}
for r in roles:
    if r["id"] in RENAME:
        name, plural, dda_id, definition, code = RENAME[r["id"]]
        r.update({"name": name, "plural": plural, "definition": definition, "dda_id": dda_id, "dda_code": code})
        r["distinct_need"] = r["distinct_need"].replace("that the person is employed by a company", "that a person is employed by a company")
save("roles", rebase(roles))

# ----------------------------------------------------------------- relationships
verbs: list[Row] = load("verbs")
for v in verbs:
    if v["id"] == "REL020":
        v.update({"code": "LegalEntityEmployment", "forward_verb": "Employed By", "inverse_verb": "Employs", "dda_action": "reuse", "dda_id": "DMR000000005",
                  "dates": True, "forward_view": "PersonEmployerOrganizations", "mirror_view": "LegalEntityEmployees",
                  "reuse_search": f"Searched {NEW_BASE}: LegalEntityEmployment says that a person is employed by an organization, and is reused as it stands."})
    if v["id"] == "REL022":
        v.update({"code": "LegalEntityTransactionParty", "source_domain_id": "DOM002", "destination_domain_id": "DOM005",
                  "source_role_id": "ROL042", "target_role_id": "ROL041", "forward_verb": "Is Party To", "inverse_verb": "Has Party",
                  "cardinality": "MANY_TO_MANY", "dates": False, "dda_action": "reuse", "dda_id": "DMR000000037",
                  "forward_view": "LegalEntityTransactions", "mirror_view": "TransactionLegalEntityParties",
                  "reuse_search": f"Searched {NEW_BASE}: LegalEntityTransactionParty says that a legal entity takes part in a transaction, and is reused as it stands."})
save("verbs", rebase(verbs))

# ----------------------------------------------------------------- lists of values
lookups: list[Row] = load("lookups")
save("lookups", rebase(lookups))
for name in ("attributes", "data-requirements", "requirements"):
    save(name, rebase(load(name)))

# ----------------------------------------------------------------- state: decisions
state: Row = load("state")
for d in state["decisions"]:
    if d["id"] == "DEC004":
        d["question"] = ("Instances takes the prefix UNT because INS is held by Instruments. DDA as read on 16 November 2026 holds no domain with UNT, "
                         "and none with PRC, the prefix proposed for Processes.")
    if d["id"] == "DEC009":
        d["question"] = ("Product is proposed both here and by CPG - Product Definition, because DDA's Products domain still holds no concept "
                         "(read on 16 November 2026). Which model creates it, and which refers to it?")
    if d["id"] == "DEC010":
        d.update({"status": "decided", "decision": "confirmed none",
                  "by": "DDA read on 16 November 2026: the Locations domain holds no concept, so Location is created and the domain is extended.",
                  "date": READ_DATE})
state["decisions"].append({
    "id": "DEC013",
    "question": ("DDA's Transaction is a movement of money or of a holding between two parties, with legs that balance, and says balances are never stored on it. "
                 "Goods movements sit beneath it as the more specific kind it anticipates, and stock positions sit beneath it as counts. "
                 "Keep both beneath Transaction, or propose a separate home for goods."),
    "options": ["keep beneath Transaction", "separate home for goods"],
    "raised_at_pass": 2, "status": "open", "decision": "", "by": "", "date": "",
})
save("state", rebase(state))
print("applied; subjects", len([s for s in subjects if s["status"] == "active"]))
