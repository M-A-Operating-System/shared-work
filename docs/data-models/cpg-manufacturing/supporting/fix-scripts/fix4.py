"""Stage 4 — definitions, distinct needs, reuse searches, wording that the document must not carry."""
from __future__ import annotations

import re

from common import active, by_id, load, save
from defs import ATTRIBUTES, CONCEPTS, LOOKUPS, ROLES

BASE = "the DDA baseline read on 28 September 2026"
subjects, roles, verbs, attrs, lookups = (load(n) for n in ("subjects", "roles", "verbs", "attributes", "lookups"))
domains_doc = load("domains")
drqs, reqs = load("data-requirements"), load("requirements")
SB, RL, AT, LK, DOMS = by_id(subjects), by_id(roles), by_id(attrs), by_id(lookups), by_id(domains_doc["domains"])
DOMCODE = {d["id"]: d.get("code", d["id"]) for d in domains_doc["domains"]}


def article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


# ---------------------------------------------------------------- renames for words the document must not carry
SB["SBJ004"]["code"] = "PersonSignings"
AT["ATR077"]["code"] = "PersonSigningsMeaning"
AT["ATR078"]["code"] = "PersonSigningsSignedAt"
AT["ATR079"]["code"] = "PersonSigningsIsSecondCheck"
AT["ATR009"]["code"] = "LocationInstallationsInstalledBy"
for r in drqs:
    r["must_record"] = [t.replace("Each signature", "Each signing").replace("signature", "signing") for t in r["must_record"]]

# ---------------------------------------------------------------- concepts
for sid, (text, need) in CONCEPTS.items():
    s = SB[sid]
    s["definition"] = text
    if s["dda_action"] == "create":
        s["distinct_need"] = need
        dom = DOMCODE.get(s["domain_id"], "")
        if sid == "SBJ043":
            s["reuse_search"] = (f"Searched {BASE} for a concept named Location or Place in DDA's Locations domain; the baseline holds no concepts "
                                 "for that domain, so the domain's concepts are to be read again before the change package is applied. "
                                 "Searched this model's own concepts: the places in the plant that were held separately are merged here.")
        else:
            s["reuse_search"] = (f"Searched {BASE} for a concept named {s['code']}, or one holding the same facts under another name, in {dom} and the "
                                 "domains it could sit in; none found. Searched this model's own concepts for the same need; none holds it.")
for s in active(subjects):
    if s["id"] not in CONCEPTS:
        raise SystemExit(f"no definition for {s['id']} {s['code']}")
    if s["dda_action"] == "reuse":
        s["reuse_search"] = s.get("reuse_search") or f"Searched {BASE}: {s['code']} is held by DDA and is reused as it stands."

# ---------------------------------------------------------------- roles
for r in active(roles):
    noun, verb, says, near, near_says = ROLES[r["id"]]
    r["definition"] = (f"{article(noun).capitalize()} {noun} is {article(r['name'])} {r['name']} while it {verb}. It says {says}. "
                       f"That is not the same as being {article(near)} {near}, which says {near_says}.")
    r["distinct_need"] = f"Names the capacity in which {says}; no other role in this model says it."
    r.pop("counterpart_role_ids", None)

# ---------------------------------------------------------------- attributes
owner_code = {s["id"]: s["code"] for s in subjects}
owner_code.update({v["id"]: v["code"] for v in verbs})
for a in active(attrs):
    a["definition"] = ATTRIBUTES[a["id"]]
    owner = a.get("subject_id") or a.get("relationship_id")
    a["reuse_search"] = (f"Searched {BASE} for an attribute named {a['code']}, or holding the same fact on {owner_code[owner]}; none found. "
                         "Searched this model's own attributes for the same fact; none holds it.")

# ---------------------------------------------------------------- relationships
code_by_dom = DOMCODE
for v in active(verbs):
    v["reuse_search"] = (f"Searched {BASE} for a relationship between {code_by_dom[v['source_domain_id']]} and {code_by_dom[v['destination_domain_id']]} "
                         f"that says {v['forward_verb']!r}; none found. Searched this model's own relationships for the same arrangement; none says it.")

# ---------------------------------------------------------------- lookups
for l in active(lookups):
    l["definition"] = LOOKUPS[l["id"]]
    l["reuse_search"] = (f"Searched {BASE} for a list of values for {l['code']}; none found. "
                         "Searched this model's own lists for the same terms; no other list holds them.")

# ---------------------------------------------------------------- domains
d10 = DOMS["DOM010"]
d10["definition"] = (
    "The Locations domain holds all physical points on earth that an organisation needs to identify, as DDA defines it. For this model it also holds "
    "the structure of each factory down to the shop floor: the site, its areas, production lines, rooms and storage positions, each place inside the one above it, "
    "with the conditions each place must keep and the identifiers each is known by. Machines standing in these places are held with Instances.")
for d in domains_doc["domains"]:
    if d.get("dda_action") == "create":
        d["reuse_search"] = d.get("reuse_search") or ""

save("subjects", subjects); save("roles", roles); save("verbs", verbs); save("attributes", attrs); save("lookups", lookups)
save("domains", domains_doc); save("data-requirements", drqs); save("requirements", reqs)

# ---------------------------------------------------------------- scan: words the document must not carry
PROCESS = [r"approval", r"approved", r"approve", r"certify", r"certified", r"certif\w*", r"sign-?off", r"signature", r"\bgate\b", r"committee",
           r"submitted for", r"awaiting", r"review\w*", r"converged", r"work queue", r"pass \d+", r"step \d+"]
CHANGE = ["added", "removed", "withdrawn", "superseded", "revised", "updated", "changed", "previously", "originally", "no longer", "new in this version"]
SCAN = ("scope", "requirements", "data-requirements", "domains", "subjects", "roles", "verbs", "attributes", "lookups", "state")
hits: list[str] = []


def walk(obj, path: str, status_ok: bool = True) -> None:
    if isinstance(obj, dict):
        if obj.get("status") == "withdrawn":
            return
        for k, v in obj.items():
            if k in {"withdrawn_reason", "reuse_search", "scenarios", "minimality", "material_changes_last_pass", "standards_conformance", "exceptions"}:
                continue
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        for pat in PROCESS:
            m = re.search(pat, obj, re.I)
            if m:
                hits.append(f"RN07 {path}: {m.group(0)!r} in {obj[:80]!r}")
        for w in CHANGE:
            if re.search(rf"\b{re.escape(w)}\b", obj, re.I):
                hits.append(f"RN03 {path}: {w!r} in {obj[:80]!r}")


for name in SCAN:
    walk(load(name), name)
print("stage 4 done;", len(hits), "wording hits")
for h in hits:
    print(" ", h)
