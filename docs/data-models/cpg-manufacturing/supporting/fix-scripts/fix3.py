"""Stage 3 — state: test cases, exceptions, decisions, standards conformance, minimality, summary."""
from __future__ import annotations

import json
from typing import Any

from common import PKG, active, by_id, load, save

state = load("state")
baseline = load("baseline")
pd_state = json.loads((PKG.parent / "pkgwork" / "state.json").read_text(encoding="utf-8"))
live = {k: len(active(load(k))) for k in ("subjects", "roles", "verbs", "attributes", "lookups")}
doms = [d for d in load("domains")["domains"] if d.get("status", "active") == "active"]

# ------------------------------------------------------------------ test cases
drop = {"SCN001", "SCN002", "SCN003", "SCN009", "SCN010", "SCN011", "SCN014", "SCN015", "SCN036", "SCN039"}
cases = [c for c in state["scenarios"] if c["id"] not in drop]
C = by_id(cases)
C["SCN004"]["path"] = ["ATR121", "SBJ051", "REL029", "ATR011", "ATR012", "ATR095"]
C["SCN005"]["path"] = ["SBJ051", "REL029", "ATR122", "ATR011"]
C["SCN006"]["path"] = ["SBJ005", "SBJ008", "ATR080", "ATR081"]
C["SCN006"]["question"] = "Did this supplier hold a valid assessment on the day a delivery was received?"
C["SCN008"]["path"] = ["SBJ012", "ATR018", "SBJ011", "ATR083"]
C["SCN017"]["path"] = ["SBJ036", "SBJ037", "REL006", "REL007", "ATR060", "ATR061", "ATR062"]
C["SCN020"]["path"] = ["REL011", "SBJ026", "SBJ043", "REL016", "ATR009"]
C["SCN021"]["path"] = ["ATR013", "SBJ028", "SBJ029", "REL031", "ATR050", "ATR051", "ATR053"]
C["SCN022"]["path"] = ["ATR013", "SBJ055", "SBJ056", "REL031", "REL034", "ATR099", "ATR100"]
C["SCN025"]["path"] = ["SBJ039", "SBJ057", "ATR103", "ATR104", "ATR128", "ATR105"]
C["SCN026"]["path"] = ["SBJ058", "REL032", "ATR129", "ATR106", "ATR107"]
C["SCN035"]["path"] = ["SBJ044", "ATR070", "ATR071", "REL018", "SBJ027", "ATR049"]
C["SCN035"]["question"] = "Which place or machine is this, whatever identifier the supplier or regulator used?"
C["SCN037"]["path"] = ["ATR018", "SBJ011", "ATR083", "ATR084"]
C["SCN038"]["path"] = ["ATR012", "SBJ016", "SBJ063", "REL029", "REL030", "ATR029"]
cases.append({"id": "SCN042", "question": "How many units are in a case of this product, and how many cases on a pallet?",
              "data_requirement_ids": ["DRQ037"], "kind": "designed", "as_at": "current",
              "path": ["SBJ012", "SBJ067", "ATR123", "ATR124", "ATR125"], "result": "pass", "reason": ""})
state["scenarios"] = cases

# ------------------------------------------------------------------ exceptions and decisions
state["exceptions"] = [
    {"id": "EXC001", "standard": "DMS000000169", "principle": 1, "kind": "conflict", "artefact_ids": ["SBJ012"],
     "justification": "The family grouping that once sat in Product is held by CPG - Product Definition, so Product here anchors only physical goods.",
     "consequence": "None for this model.", "owner": "Data Design Authority owner", "route_back": "None needed.",
     "status": "withdrawn", "withdrawn_reason": "No longer applies: Product in this model holds no family grouping."},
    {"id": "EXC002", "standard": "DMS000000169", "principle": 1, "kind": "conflict",
     "artefact_ids": ["SBJ016", "REL015", "REL029", "REL030", "REL032", "REL033", "REL037", "REL038"],
     "justification": "Tracing food forward and back is between batches, and a batch is a thing in its own right with its own life. DDA's Products domain has no place for it other than beneath the Product anchor, so every traced link points at a concept inside the domain and not at the anchor itself.",
     "consequence": "A reader following a traced link must read its destination as the batch within Products, not as a product. A batch cannot be shared with another domain without going through Product.",
     "owner": "Data Design Authority owner",
     "route_back": "A domain of its own for batches, if batches acquire identity and obligations that products do not share. It fails the domain tests today because a batch has no existence apart from the product it is a batch of."},
    {"id": "EXC003", "standard": "DMS000000169", "principle": 13, "kind": "not_met", "artefact_ids": [],
     "justification": "Principle 13 asks for stewardship, retention and provenance to be set as part of the design. This design names no steward for any concept and sets a retention period only for the lot-code records the United States food traceability rule covers.",
     "consequence": "Nobody is named as accountable for a definition, and nothing says how long the other dated records are kept.",
     "owner": "Data Design Authority owner",
     "route_back": "Naming a steward for each domain and setting a retention period for each kind of dated record."},
]
state["decisions"] = [
    {"id": "DEC001", "question": "Hold a batch beneath Product, with traced links pointing at it (EXC002), or give batches a domain of their own.",
     "options": ["beneath Product", "own domain"], "raised_at_pass": 1, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC004", "question": "Instances takes the prefix UNT because INS is held by Instruments.",
     "options": ["confirm UNT", "reassign"], "raised_at_pass": 1, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC005", "question": "Is finished output identified individually, or only by batch? (SCQ001)",
     "options": ["individually", "batch only", "both"], "raised_at_pass": 1, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC006", "question": "The total cost of poor quality is asked for and no artefact holds it. Costs are out of scope for this model.",
     "options": ["in scope", "out of scope"], "raised_at_pass": 1, "status": "decided", "decision": "out of scope",
     "by": "Stated direction for the model", "date": ""},
    {"id": "DEC007", "question": "State transitions could not be read from DDA, so the change package carries no preconditions.",
     "options": ["retry before applying", "apply without preconditions"], "raised_at_pass": 1, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC008", "question": "The Events and Transactions domain definitions in DDA are written for financial services. Broaden them to cover making and moving goods.",
     "options": ["broaden", "leave as is"], "raised_at_pass": 1, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC009", "question": "Product is proposed both here and by CPG - Product Definition, because DDA's Products domain holds no concept. Which model creates it, and which refers to it?",
     "options": ["CPG - Product Definition creates it", "this model creates it"], "raised_at_pass": 2, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC010", "question": "DDA's Locations domain could not be read in full. Confirm it holds no concept for a place before the change package is applied.",
     "options": ["confirmed none", "reuse what is held"], "raised_at_pass": 2, "status": "open", "decision": "", "by": "", "date": ""},
    {"id": "DEC011", "question": "Two years is the retention period given for traceability records. The rule's own text could not be read, so the period is unconfirmed.",
     "options": ["keep two years", "use the period in the rule"], "raised_at_pass": 2, "status": "open", "decision": "", "by": "", "date": ""},
]
for k in ("certification", "approvals"):
    state.pop(k, None)

# ------------------------------------------------------------------ standards conformance
hashes = {s["dda_id"]: s["content_hash"] for s in baseline["standards"]}
TEXT: dict[str, tuple[bool, str, str | None]] = {
    "DMS000000141": (True, "Every domain is a subject shared across the business: People, Legal Entities, Documents, Events, Transactions, Products and Locations are reused as DDA holds them, and the two proposed, Instances and Processes, are named for what they are and not for a department.", None),
    "DMS000000142": (True, "Each requirement names an accountable role, and what could not be checked is raised as an open decision rather than worked around.", None),
    "DMS000000146": (True, "Two domains are proposed, Instances and Processes. Each is set out with its ten domain tests and the domains considered instead, so that the body that decides domains has what it needs.", None),
    "DMS000000147": (True, "Every domain is named for a subject. Candidates shaped like an activity or a role — Quality, Maintenance, Production, Inventory, Suppliers, Equipment and Batches — were tested and are recorded with the test each failed and where their subjects sit.", None),
    "DMS000000149": (True, "Each concept sits in one domain and each domain has one anchor concept. Products holds no concept in DDA, so its anchor, Product, is proposed here as well as by CPG - Product Definition.", None),
    "DMS000000168": (True, "Lineage is held by the platform and is not modelled. Which batches went into which, and where they went, is traceability in the business sense and is held as links between production runs and batches.", None),
    "DMS000000151": (True, "Locations, Instances and Legal Entities each carry an identifiers concept with the issuer and dates, and each batch is known by its lot code.", None),
    "DMS000000152": (True, "Attributes that carry a duty to keep records or protect people — lot codes, quantities used and made, who signed and when, qualifications and their expiry, how long a supplier assessment is valid — are marked critical.", None),
    "DMS000000169": (True, "Each of the fourteen principles is addressed in turn. Four do not apply, because this design defines no reports, data products or publication. Two are not fully met and are set out as exceptions, each with its consequence and what would resolve it.", "EXC002, EXC003"),
}
entries: list[dict[str, Any]] = []
for e in pd_state["standards_conformance"]:
    sid = e["standard"]
    row = dict(e)
    if sid in TEXT:
        row["applies"], row["how_satisfied"], row["exception_id"] = TEXT[sid]
    row["read_hash"] = hashes[sid]
    row["artefact_ids"] = []
    row["covers"] = e.get("covers", [])
    row["how_satisfied"] = row["how_satisfied"].replace("This design", "This model").replace("this design", "this model")
    entries.append(row)
state["standards_conformance"] = entries

# ------------------------------------------------------------------ loop state
state["pass"] = 2
state["stable_pass_count"] = 0
state["next_action"] = {"step": 9, "reason": "validate the second pass"}
state["work_queue"] = []
state["escalated"] = []
state["gate_decision"] = None
state["converged"] = False
state["material_changes_last_pass"] = [
    "Product definition moved to CPG - Product Definition: 11 concepts, 5 relationships, 31 attributes and 2 lists of values withdrawn",
    "Plant structure merged into Locations; the Equipment domain withdrawn",
    "Cost withdrawn; pack levels added; batch roles merged into one Traced Batch role",
    "Findings merged into one concept; production-order and material-consumption concepts merged away",
]
state["document"] = {"edition": "lite", "requested_by": "Andrew Bush", "rendered": ""}
state["mechanics"] = "manual"
withdrawn_ids = sorted({r["id"] for k in ("subjects", "roles", "verbs", "attributes", "lookups") for r in load(k) if r.get("status") == "withdrawn"})
state["minimality"] = [
    {"pass": 1, "counts": {"domains": 10, "roles": 70, "relationships": 38, "concepts": 66, "attributes": 120, "lookups": 9},
     "merged": [], "withdrawn": [], "growth_justified_by": [d["id"] for d in active(load("data-requirements")) if d["id"] != "DRQ037"]},
    {"pass": 2, "counts": {"domains": len(doms), "roles": live["roles"], "relationships": live["verbs"], "concepts": live["subjects"],
                           "attributes": live["attributes"], "lookups": live["lookups"]},
     "merged": ["SBJ031 into SBJ043", "SBJ032 into SBJ044", "SBJ052 into SBJ051", "SBJ059 into SBJ058", "SBJ030 into SBJ026",
                "REL010 into REL016", "ROL051, ROL052, ROL053, ROL054, ROL058, ROL060, ROL068, ROL070, ROL030 into ROL071", "ROL065 into ROL057"],
     "withdrawn": withdrawn_ids,
     "growth_justified_by": ["DRQ037"]},
]
state["summary"] = (
    "The model covers how a food and beverage manufacturer receives materials, makes, packs, tests and releases product, in its own "
    "factories and through outside manufacturers, and how any batch is traced back to what went into it and forward to where it went. "
    "It reuses seven DDA domains, extends Locations to hold each factory down to the shop floor, and proposes two new domains, "
    "Instances and Processes. What a product is, and what it is made from, is held by CPG - Product Definition and is not repeated here."
)
save("state", state)
print("stage 3 done;", len(cases), "test cases;", len(entries), "conformance entries")
