"""Stage 6 — derived.json and dda-changeset.json built from the corrected package."""
from __future__ import annotations

from typing import Any

from common import TODAY, active, by_id, load, save

subjects, roles, verbs = active(load("subjects")), active(load("roles")), active(load("verbs"))
attrs, lookups = active(load("attributes")), active(load("lookups"))
doms = [d for d in load("domains")["domains"] if d.get("status", "active") == "active"]
reqs, drqs, sources = active(load("requirements")), active(load("data-requirements")), active(load("sources"))
R = by_id(roles)
anchor = {s["domain_id"]: s["code"] for s in subjects if s.get("is_anchor")}
DOMCODE = {d["id"]: d["code"] for d in doms}

# ------------------------------------------------------------------ derived
views: dict[str, dict[str, str]] = {}
for v in verbs:
    if v.get("forward_view"):
        views[v["id"]] = {"forward": v["forward_view"], "mirror": v["mirror_view"]}
        continue
    if v.get("name_override"):
        views[v["id"]] = {"forward": v["name_override"], "mirror": v["name_override"] + "Of"}
        continue
    views[v["id"]] = {
        "forward": f"{anchor[v['source_domain_id']]}{R[v['target_role_id']]['plural'].replace(' ', '')}",
        "mirror": f"{anchor[v['destination_domain_id']]}{R[v['source_role_id']]['plural'].replace(' ', '')}",
    }
index: dict[str, list[str]] = {s["id"]: [] for s in sources}
for kind in (reqs, drqs, subjects, verbs, attrs, lookups, roles):
    for row in kind:
        for sid in row.get("source_ids", []) + row.get("evidence_source_ids", []):
            if sid in index:
                index[sid].append(row["id"])
derived = {
    "document_date": TODAY, "package_ref": "cpg-manufacturing", "views": views,
    "counts": {"requirements": len(reqs), "data_requirements": len(drqs), "roles": len(roles), "verbs": len(verbs),
               "subjects": len(subjects), "attributes": len(attrs), "lookups": len(lookups), "sources": len(sources)},
    "source_index": {k: sorted(set(v)) for k, v in index.items()},
}
save("derived", derived)

# ------------------------------------------------------------------ change package
ops: list[dict[str, Any]] = []
seq_of: dict[str, int] = {}


def add(entity: str, local_id: str, fields: dict[str, Any], deps: list[str], op: str = "create", dda_id: str | None = None) -> None:
    ops.append({"seq": len(ops) + 1, "op": op, "entity": entity, "local_id": local_id, "dda_id": dda_id, "fields": fields,
                "depends_on": sorted({seq_of[d] for d in deps if d in seq_of})})
    seq_of[local_id] = len(ops)


for d in doms:
    if d["dda_action"] == "create":
        add("domains", d["id"], {"domain_code": d["code"], "domain_name": d["code"], "domain_id_structure": d["prefix"],
                                 "domain_description": d["definition"]}, [])
    elif d["dda_action"] == "extend":
        add("domains", d["id"], {"domain_description_addition": d["definition_update"]}, [], op="update", dda_id=d["dda_id"])
for l in lookups:
    if l["dda_action"] == "reuse":
        continue
    if l["dda_action"] == "extend":
        add("lookupTypes", l["id"], {"lookups_to_add": [{"lookup_code": v["code"], "lookup_name": v["name"], "lookup_description": v["definition"]} for v in l["values"]]},
            [], op="update", dda_id=l["dda_id"])
    else:
        add("lookupTypes", l["id"], {"lookup_type_code": l["code"], "lookup_type_name": l["code"], "lookup_type_description": l["definition"], "values": len(l["values"])}, [])

DOMREF = {d["id"]: (d["dda_id"] if d.get("dda_id") else d["id"]) for d in doms}
ROLEREF: dict[str, str] = {}
for r in roles:
    if r.get("dda_id"):
        ROLEREF[r["id"]] = r["dda_id"]
        continue
    add("roles", r["id"], {"role_code": r["name"].replace(" ", ""), "role_name": r["name"], "role_description": r["definition"],
                           "role_domains": [DOMREF[d] for d in r["played_by_domain_ids"]]},
        [d for d in r["played_by_domain_ids"]])
    ROLEREF[r["id"]] = r["id"]

# concepts: parents before children
pending = [s for s in subjects if s["dda_action"] == "create"]
placed: set[str] = set()
while pending:
    progressed = False
    for s in list(pending):
        parent = s.get("parent_id")
        if parent and parent not in placed and any(p["id"] == parent for p in pending):
            continue
        base = [s["domain_id"]] + ([parent] if parent else [])
        sd = by_id(subjects)
        if s["is_anchor"]:
            pref = "Master"
        elif sd[parent]["dda_action"] == "reuse":
            pref = sd[parent]["dda_id"]
        else:
            pref = parent
        add("concepts", s["id"], {"concept_code": s["code"], "concept_name": s["code"], "concept_description": s["definition"],
                                  "concept_domain": DOMREF[s["domain_id"]], "concept_is_domain": s["domain_id"] if s["is_anchor"] else None, "concept_parent": pref,
                                  "concept_parent_rel": None if s["is_anchor"] else s["parent_cardinality"]}, base)
        placed.add(s["id"])
        pending.remove(s)
        progressed = True
    if not progressed:
        raise SystemExit("concept ordering failed")
# concept dependencies include the domain they are created in
SD = by_id(subjects)
anchors_by_dom = {s["domain_id"]: s["id"] for s in subjects if s.get("is_anchor")}
for v in verbs:
    if v["dda_action"] == "reuse":
        continue
    ends = [anchors_by_dom.get(v["source_domain_id"], ""), anchors_by_dom.get(v["destination_domain_id"], "")]
    add("relationships", v["id"], {"relationship_code": v["code"], "relationship_name": v["code"],
                                   "relationship_description": f"{R[v['source_role_id']]['name']} {v['forward_verb']} {R[v['target_role_id']]['name']}; {R[v['target_role_id']]['name']} {v['inverse_verb']} {R[v['source_role_id']]['name']}.",
                                   "relationship_domain": DOMREF[v["source_domain_id"]], "relationship_destination_domain": DOMREF[v["destination_domain_id"]],
                                   "relationship_forward_verb": v["forward_verb"], "relationship_inverse_verb": v["inverse_verb"],
                                   "relationship_source_role": ROLEREF[v["source_role_id"]], "relationship_target_role": ROLEREF[v["target_role_id"]],
                                   "relationship_cardinality": v["cardinality"], "relationship_dates": v["dates"],
                                   "relationship_forward_view": views[v["id"]]["forward"], "relationship_mirror_view": views[v["id"]]["mirror"]},
        ends + [v["source_role_id"], v["target_role_id"]])
for a in attrs:
    owner = a.get("subject_id") or a.get("relationship_id")
    add("attributes", a["id"], {"attribute_code": a["code"], "attribute_name": a["code"], "attribute_fqn_name": a["code"],
                                "attribute_description": a["definition"], "attribute_type": a["datatype"],
                                "attribute_lookup_type": a.get("lookup_id"), "attribute_concept": a.get("subject_id"),
                                "attribute_classification": a.get("classification")},
        [owner] + ([a["lookup_id"]] if a.get("lookup_id") else []))

model_roles = [ROLEREF[r["id"]] for r in roles]
model_rels = [v["dda_id"] if v["dda_action"] == "reuse" else v["id"] for v in verbs]
add("models", "MODEL001", {"model_code": "CPGManufacturingAndSupplyChain", "model_name": "CPG - Manufacturing and Supply Chain",
                           "model_description": "Factories, production runs, batches, packing and the supply chain for food and beverage manufacturers, with the traceability each batch needs.",
                           "model_roles": model_roles, "model_relationships": model_rels},
    [r["id"] for r in roles if not r.get("dda_id")] + [v["id"] for v in verbs if v["dda_action"] != "reuse"])

changeset = {"spec_version": "1.0", "package_ref": "cpg-manufacturing", "apply_mode": "web-ui", "preconditions": [],
             "preconditions_note": "State transitions could not be read from the platform; see DEC007.", "operations": ops}
save("dda-changeset", changeset)
print("built:", len(ops), "operations;", derived["counts"])
