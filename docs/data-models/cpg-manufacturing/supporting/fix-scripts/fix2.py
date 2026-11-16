"""Stage 2 — structure: subjects, roles, verbs, attributes, lookups, domains (findings F03 to F16)."""
from __future__ import annotations

from typing import Any

from common import active, by_id, load, save, withdraw

PD = "Held by the CPG - Product Definition model, which owns what a product is, what it is made from and what it must be."
EQ = "Plant structure is held in the Locations hierarchy, which runs down to the shop floor."

subjects = load("subjects")
roles = load("roles")
verbs = load("verbs")
attrs = load("attributes")
lookups = load("lookups")
domains_doc = load("domains")
drqs = load("data-requirements")

SB, RL, VB, AT, LK = by_id(subjects), by_id(roles), by_id(verbs), by_id(attrs), by_id(lookups)
DOMS = by_id(domains_doc["domains"])
DRQ_ACTIVE = {d["id"] for d in active(drqs)}
DR = by_id(drqs)

# ------------------------------------------------------------------ lookups
withdraw(LK["LKP002"], PD)
withdraw(LK["LKP003"], PD)
LK["LKP001"]["values"] = [v for v in LK["LKP001"]["values"] if v["code"] not in {"CASE", "PALLET", "FAMILY"}]
LK["LKP001"]["data_requirement_ids"] = ["DRQ008", "DRQ013"]
LK["LKP005"]["code"] = "LocationLevelType"
LK["LKP005"]["data_requirement_ids"] = ["DRQ020"]
LK["LKP009"]["data_requirement_ids"] = ["DRQ004"]
LK["LKP009"]["evidence_source_ids"] = LK["LKP009"].get("evidence_source_ids") or ["SRC005"]
lookups += [
    {"id": "LKP010", "code": "EventFindingsKindType", "scope": "concept",
     "definition": "", "values": [
         {"code": "DEVIATION", "name": "Deviation", "definition": "A departure from the written procedure while a batch was being made."},
         {"code": "NONCONFORMANCE", "name": "Non-conformance", "definition": "A batch, material or result that fails its specification."}],
     "dda_action": "create", "dda_id": None, "reuse_search": "", "data_requirement_ids": ["DRQ026"],
     "evidence_source_ids": ["SRC016"], "status": "active", "withdrawn_reason": None},
    {"id": "LKP011", "code": "ProductPackLevelsLevelType", "scope": "concept",
     "definition": "", "values": [
         {"code": "UNIT", "name": "Unit", "definition": "The single pack a shopper buys."},
         {"code": "INNER", "name": "Inner pack", "definition": "A group of units packed together inside a case, such as a multipack."},
         {"code": "CASE", "name": "Case", "definition": "The outer carton units are shipped in."},
         {"code": "LAYER", "name": "Layer", "definition": "One layer of cases on a pallet."},
         {"code": "PALLET", "name": "Pallet", "definition": "The pallet cases are moved and stored on."}],
     "dda_action": "create", "dda_id": None, "reuse_search": "", "data_requirement_ids": ["DRQ037"],
     "evidence_source_ids": ["SRC030", "SRC031"], "status": "active", "withdrawn_reason": None},
    {"id": "LKP012", "code": "InstanceKindType", "scope": "concept",
     "definition": "", "values": [
         {"code": "MACHINE", "name": "Machine", "definition": "A machine, vessel or tool that stands in a place in the plant."},
         {"code": "UNIT", "name": "Individual unit", "definition": "A single item of product that is identified on its own, such as by a serial number."}],
     "dda_action": "create", "dda_id": None, "reuse_search": "", "data_requirement_ids": ["DRQ016", "DRQ020"],
     "evidence_source_ids": ["SRC018", "SRC037"], "status": "active", "withdrawn_reason": None},
]

# ------------------------------------------------------------------ subjects
for sid in ("SBJ013", "SBJ014", "SBJ015", "SBJ018", "SBJ019", "SBJ020", "SBJ021", "SBJ022", "SBJ023", "SBJ024", "SBJ025"):
    withdraw(SB[sid], PD if sid != "SBJ024" else "Cost is not held in this model.")
withdraw(SB["SBJ030"], "Folded into Instance: how much a machine matters is one figure on the machine.")
withdraw(SB["SBJ031"], "Merged into Location, which holds the places down to the shop floor. " + EQ)
withdraw(SB["SBJ032"], "Merged into LocationIdentifiers. " + EQ)
withdraw(SB["SBJ033"], "A rated capacity is not asked for by any data requirement that remains.")
withdraw(SB["SBJ035"], "No data requirement asks for maintenance plans; the repairs themselves are recorded as work done.")
withdraw(SB["SBJ050"], "Holds nothing of its own; the production run records what was made.")
withdraw(SB["SBJ052"], "Merged into EventProductionRuns: how much each batch used is held on the link between run and batch.")
withdraw(SB["SBJ059"], "Merged into EventFindings, which holds both kinds of finding and says which each is.")

SB["SBJ034"].update({"domain_id": "DOM010", "parent_id": "SBJ043", "code": "LocationSequencingRules"})
SB["SBJ058"]["code"] = "EventFindings"
SB["SBJ012"]["data_requirement_ids"] = ["DRQ008", "DRQ013"]
SB["SBJ043"]["data_requirement_ids"] = ["DRQ020", "DRQ024"]
SB["SBJ026"]["data_requirement_ids"] = ["DRQ016", "DRQ020", "DRQ021"]

subjects.append({
    "id": "SBJ067", "code": "ProductPackLevels", "definition": "", "kind": "subject", "mastery": "mastered",
    "domain_id": "DOM006", "is_anchor": False, "parent_id": "SBJ012", "parent_cardinality": "ONE_TO_MANY_OPTIONAL",
    "singled_out_by": "ATR123", "independence": None,
    "distinct_need": "Holds the levels a product is packed in and how many of the level below each holds; nothing else in the model holds pack levels.",
    "template_dda_id": None, "dda_action": "create", "dda_id": None, "reuse_search": "",
    "data_requirement_ids": ["DRQ037"], "evidence_source_ids": ["SRC030", "SRC031"], "status": "active", "withdrawn_reason": None,
})

SINGLED = {  # how one record is told from another under the same parent
    "SBJ002": "dates and ATR074", "SBJ003": "dates", "SBJ004": "dates", "SBJ006": "dates", "SBJ007": "dates",
    "SBJ008": "dates", "SBJ009": "dates", "SBJ011": "ATR083", "SBJ016": "dates", "SBJ017": "dates",
    "SBJ027": "dates", "SBJ028": "dates", "SBJ029": "dates", "SBJ034": "dates", "SBJ037": "ATR061",
    "SBJ038": "dates", "SBJ039": "dates", "SBJ040": "dates", "SBJ041": "ATR065", "SBJ042": "dates",
    "SBJ044": "dates", "SBJ045": "dates", "SBJ047": "dates", "SBJ048": "dates", "SBJ067": "ATR123",
}
for s in subjects:
    s.pop("grain", None)
    if s["id"] in SINGLED:
        s["singled_out_by"] = SINGLED[s["id"]]
    elif s.get("parent_id"):
        s["singled_out_by"] = "dates"
    s["data_requirement_ids"] = [d for d in s["data_requirement_ids"] if d in DRQ_ACTIVE]
# every Events concept is told apart by when it happened
for s in subjects:
    if s["domain_id"] == "DOM004" and s.get("parent_id"):
        s["singled_out_by"] = "dates"

# ------------------------------------------------------------------ roles
for rid in ("ROL001", "ROL002", "ROL003", "ROL004", "ROL005", "ROL006", "ROL007", "ROL008", "ROL009"):
    withdraw(RL[rid], PD)
for rid in ("ROL020", "ROL021", "ROL024", "ROL025"):
    withdraw(RL[rid], EQ)
for rid in ("ROL030", "ROL051", "ROL052", "ROL053", "ROL054", "ROL058", "ROL060", "ROL068", "ROL070"):
    withdraw(RL[rid], "Every batch in a traced link is a Traced Batch; one role covers them all.")
withdraw(RL["ROL065"], "A finding raised with a supplier is the same Finding as any other.")
RL["ROL016"]["name"], RL["ROL016"]["plural"] = "Permitted Step", "Permitted Steps"
RL["ROL017"].update({"name": "Permitted Place", "plural": "Permitted Places", "played_by_domain_ids": ["DOM010"]})
RL["ROL022"].update({"name": "Occupied Place", "plural": "Occupied Places", "played_by_domain_ids": ["DOM010"]})
RL["ROL047"].update({"name": "Production Place", "plural": "Production Places", "played_by_domain_ids": ["DOM010"]})
roles.append({"id": "ROL071", "name": "Traced Batch", "plural": "Traced Batches", "definition": "",
              "played_by_domain_ids": ["DOM006"], "distinct_need": "", "aliases": [],
              "established_by": [], "stated_in": ["REQ016", "REQ027", "REQ051"], "evidence_source_ids": ["SRC005", "SRC009"],
              "status": "active", "withdrawn_reason": None})
for r in roles:
    r.pop("counterpart_role_ids", None)
    r.pop("is_symmetric", None)

# ------------------------------------------------------------------ relationships
for rid in ("REL001", "REL002", "REL003", "REL004"):
    withdraw(VB[rid], PD)
for rid in ("REL010", "REL012"):
    withdraw(VB[rid], EQ)
withdraw(VB["REL017"], "Which body certified a place is not asked for by any data requirement that remains.")

VB["REL008"].update({"code": "ProcessSegmentPlaces", "destination_domain_id": "DOM010", "forward_verb": "may be run at",
                     "inverse_verb": "may run", "target_role_id": "ROL017"})
VB["REL011"].update({"code": "LocationInstallations", "source_domain_id": "DOM010", "source_role_id": "ROL022"})
VB["REL026"].update({"code": "EventRunPlaces", "destination_domain_id": "DOM010"})
for rid, src in (("REL029", "ROL046"), ("REL030", "ROL046"), ("REL032", "ROL057"), ("REL033", "ROL059"),
                 ("REL037", "ROL067"), ("REL038", "ROL069"), ("REL015", "ROL028")):
    VB[rid].update({"source_role_id": src, "target_role_id": "ROL071"})
VB["REL036"]["source_role_id"] = "ROL057"
VB["REL029"]["quantified"] = VB["REL030"]["quantified"] = VB["REL015"]["quantified"] = True
for v in verbs:
    v["data_requirement_ids"] = [d for d in v["data_requirement_ids"] if d in DRQ_ACTIVE]
VB["REL012"]["data_requirement_ids"] = VB["REL012"]["data_requirement_ids"] or ["DRQ020"]

# establish roles from the live relationships
est: dict[str, list[str]] = {}
for v in active(verbs):
    for end in ("source_role_id", "target_role_id"):
        est.setdefault(v[end], []).append(v["id"])
for r in roles:
    r["established_by"] = sorted(set(est.get(r["id"], [])))
    if r.get("status", "active") == "active" and not r["established_by"]:
        withdraw(r, "No relationship in this model establishes it.")

# ------------------------------------------------------------------ attributes
def wa(aid: str, reason: str = PD) -> None:
    withdraw(AT[aid], reason)

for aid in ("ATR001", "ATR003", "ATR004", "ATR005", "ATR007", "ATR016", "ATR019", "ATR020", "ATR021", "ATR022", "ATR023", "ATR024",
            "ATR025", "ATR026", "ATR027", "ATR028", "ATR031", "ATR034", "ATR035", "ATR036", "ATR037", "ATR038", "ATR039", "ATR040",
            "ATR041", "ATR042", "ATR043", "ATR046", "ATR047"):
    wa(aid, PD + (" The date a batch may be used until is worked out from the shelf life held there." if aid == "ATR031" else ""))
wa("ATR044", "Cost is not held in this model.")
wa("ATR045", "Cost is not held in this model.")
wa("ATR055", "Merged into LocationName.")
wa("ATR056", "A rated capacity is not asked for by any data requirement that remains.")
wa("ATR059", "The maintenance plan is not held.")
wa("ATR102", "A stoppage is tied to its repair through the link between the two, not through a typed reference.")
wa("ATR108", "Merged into EventFindingsClassification.")
wa("ATR109", "Merged into EventFindingsContainedAt.")

# moved or renamed
AT["ATR002"].update({"subject_id": None, "relationship_id": "REL029", "code": "EventBatchInputsUnitOfMeasure",
                     "data_requirement_ids": ["DRQ004"]})
AT["ATR053"].update({"subject_id": "SBJ026", "code": "InstanceCriticalityScore", "mandatory": False, "temporality": "as-at"})
AT["ATR054"].update({"subject_id": "SBJ043", "code": "LocationLevel"})
AT["ATR069"]["data_requirement_ids"] = ["DRQ020", "DRQ024"]
AT["ATR057"].update({"code": "LocationSequencingRulesReason"})
AT["ATR058"].update({"code": "LocationSequencingRulesRequiresClean"})
AT["ATR095"].update({"subject_id": "SBJ051", "code": "EventProductionRunsYieldVariance", "derived_from": ["ATR011", "ATR012"]})
AT["ATR105"].update({"nature": "observed", "derived_from": []})
AT["ATR106"].update({"code": "EventFindingsClassification"})
AT["ATR107"].update({"code": "EventFindingsContainedAt"})
AT["ATR011"]["data_requirement_ids"] = ["DRQ004"]
AT["ATR010"]["data_requirement_ids"] = ["DRQ023", "DRQ027", "DRQ029"]
AT["ATR017"]["data_requirement_ids"] = ["DRQ013"]
AT["ATR018"]["data_requirement_ids"] = ["DRQ008"]
AT["ATR036"] = AT["ATR036"]

def na(aid: str, owner: dict[str, str], code: str, dt: str, nature: str, mand: bool, crit: bool, tmp: str, drq: list[str],
       src: list[str], lookup: str | None = None) -> None:
    attrs.append({"id": aid, "subject_id": owner.get("s"), "relationship_id": owner.get("r"), "code": code, "definition": "",
                  "datatype": dt, "lookup_id": lookup, "nature": nature, "derived_from": [], "temporality": tmp,
                  "mandatory": mand, "critical": crit, "classification": None, "dda_action": "create", "dda_id": None,
                  "reuse_search": "", "data_requirement_ids": drq, "evidence_source_ids": src,
                  "status": "active", "withdrawn_reason": None})

na("ATR121", {"r": "REL029"}, "EventBatchInputsQuantitySpecified", "FLOAT", "observed", True, True, "as-at", ["DRQ004"], ["SRC005"])
na("ATR122", {"r": "REL029"}, "EventBatchInputsIsAlternative", "BOOLEAN", "observed", True, True, "as-at", ["DRQ005"], ["SRC005"])
na("ATR123", {"s": "SBJ067"}, "ProductPackLevelsLevel", "LOOKUP", "observed", True, True, "current", ["DRQ037"], ["SRC030"], "LKP011")
na("ATR124", {"s": "SBJ067"}, "ProductPackLevelsIdentifier", "TEXT", "observed", True, True, "current", ["DRQ037"], ["SRC030", "SRC031"])
na("ATR125", {"s": "SBJ067"}, "ProductPackLevelsUnitsPerLevel", "INTEGER", "observed", True, True, "current", ["DRQ037"], ["SRC030"])
na("ATR126", {"s": "SBJ056"}, "EventMaintenanceWorkDescription", "LONGTEXT", "observed", True, False, "as-at", ["DRQ021", "DRQ022"], ["SRC018"])
na("ATR127", {"s": "SBJ026"}, "InstanceKind", "LOOKUP", "observed", True, True, "current", ["DRQ016", "DRQ020"], ["SRC018"], "LKP012")
na("ATR128", {"s": "SBJ057"}, "EventTestsSpecificationVersion", "TEXT", "observed", True, True, "as-at", ["DRQ025"], ["SRC016"])
na("ATR129", {"s": "SBJ058"}, "EventFindingsKind", "LOOKUP", "observed", True, True, "as-at", ["DRQ026"], ["SRC016"], "LKP010")
na("ATR130", {"s": "SBJ029"}, "InstanceFailureModesName", "TEXT", "observed", True, True, "as-at", ["DRQ021"], ["SRC018"])

for a in attrs:
    a["data_requirement_ids"] = [d for d in a["data_requirement_ids"] if d in DRQ_ACTIVE]
    if a.get("status", "active") == "active" and not a["data_requirement_ids"]:
        raise SystemExit(f"{a['id']} has no active data requirement")

# ------------------------------------------------------------------ data requirement fixes that follow the structure
DR["DRQ012"]["prevent_resolution"] = [{"must_prevent_index": 0, "expressed_by": "parent-cardinality", "artefact_id": "SBJ017"}]
DR["DRQ013"]["prevent_resolution"] = [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR089"}]
DR["DRQ016"]["must_prevent"] = ["A batch built into a unit with no quantity recorded"]
DR["DRQ016"]["prevent_resolution"] = [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR006"}]
DR["DRQ025"]["must_record"] = ["Each test with its method, sample, sampling plan and result, and the version of the specification it was judged against"]
DR["DRQ025"]["must_answer"] = ["Did this batch meet the specification in force when it was made, and by what test?"]
DR["DRQ026"]["prevent_resolution"] = [{"must_prevent_index": 0, "expressed_by": "mandatory-attribute", "artefact_id": "ATR129"}]
DR["DRQ021"]["must_record"] = ["Each machine's failures and how it failed, its repairs, its readings, and how much it matters"]

# ------------------------------------------------------------------ domains
dom_list = domains_doc["domains"]
withdraw(DOMS["DOM008"], "Plant structure is held in Locations, and machines in Instances. " + EQ)
DOMS["DOM008"]["anchor_subject_id"] = None
DOMS["DOM006"].update({"dda_id": "DMD000000032", "dda_action": "reuse", "code": "Products", "prefix": "PRD", "definition": None,
                       "definition_update": None, "shared": True, "admission_gate": None, "domain_tests": None, "reuse_considered": []})
DOMS["DOM006"]["anchor_subject_id"] = "SBJ012"
DOMS["DOM010"].update({
    "dda_id": "DMD000000034", "dda_action": "extend", "code": "Locations", "prefix": "LOC", "shared": True,
    "definition": None, "admission_gate": None, "domain_tests": None,
    "definition_update": ("The Locations domain also holds the structure of each factory down to the shop floor: the site, its areas, "
                          "production lines, rooms and storage positions, each place inside the one above it, with the conditions each "
                          "place must keep and the identifiers each is known by. Machines that stand in these places are held with Instances."),
    "reuse_considered": [{"dda_id": "DMD000000034", "why_not": "Reused as the home of every place. Extended so that the places inside a factory, below the site, are held in the same hierarchy as the site itself."}],
})
for d in dom_list:
    d.pop("committee_decision", None)
    d["subject_ids"] = [s["id"] for s in active(subjects) if s["domain_id"] == d["id"]]
    if d.get("status", "active") == "active" and not d["subject_ids"]:
        raise SystemExit(f"{d['id']} has no concepts")
# DOM007 and DOM009 texts that named the withdrawn Equipment domain
for d in dom_list:
    if d["id"] in {"DOM007", "DOM009"}:
        txt = repr(d)
        for k, v in list(d.items()):
            pass
import json
for d in dom_list:
    if d["id"] in {"DOM007", "DOM009"}:
        raw = json.dumps(d, ensure_ascii=False)
        raw = (raw.replace("an Equipment position", "a place in the plant").replace("the place is an Equipment position", "the place is a Location")
               .replace("Equipment position", "Location").replace("equipment positions", "places in the plant")
               .replace("what each step requires of equipment, people and materials", "what each step requires of machines, people and materials"))
        d.update(json.loads(raw))
for c in domains_doc["rejected_candidates"]:
    c["reason"] = c["reason"].replace("an Equipment position", "a Location").replace("Equipment position", "Location")
    if c.get("placed_in_domain_id") == "DOM008":
        c["placed_in_domain_id"] = "DOM010"
domains_doc["rejected_candidates"].append({
    "name": "Equipment",
    "failed_tests": ["DT2", "DT3"],
    "reason": "A place in the plant is a Location, one level of the same hierarchy as the site, and a machine is an Instance. Neither needs a domain of its own.",
    "placed_in_domain_id": "DOM010", "prompted_by_subject_ids": ["SBJ031"], "rejected_by": "agent"})

for name, data in (("subjects", subjects), ("roles", roles), ("verbs", verbs), ("attributes", attrs), ("lookups", lookups),
                   ("domains", domains_doc), ("data-requirements", drqs)):
    save(name, data)
print("stage 2 done:", {k: len(active(v)) for k, v in (("concepts", subjects), ("roles", roles), ("relationships", verbs),
                                                        ("attributes", attrs), ("lookups", lookups))})
