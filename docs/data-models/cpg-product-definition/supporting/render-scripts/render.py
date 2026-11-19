#!/usr/bin/env python3
"""Build the DDA change package and render the lite Data Design Document from a package directory.

Usage: render.py <package-dir> <previous-document.md> <output.md>
The static text (introduction, principles table) is read from the previous document;
every figure and every table is projected from the package.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

Json = Any
BASE = "https://datadesign.maoperatingsystem.com/models"
CARD = {"ONE_TO_MANY_OPTIONAL": "may have many, or none", "ONE_TO_ONE_OPTIONAL": "may have one, or none"}
CARD_ROW = {"ONE_TO_MANY_OPTIONAL": "may have many, or none", "ONE_TO_ONE_OPTIONAL": "may have one, or none"}
REL_CARD = {"MANY_TO_MANY": "Many to many", "MANY_TO_ONE": "Many to one", "ONE_TO_MANY": "One to many", "ONE_TO_ONE": "One to one"}
SRC_TYPE = {"standard": "Industry standard", "regulatory": "Regulator or law", "practitioner": "Industry practice",
            "reference-model": "Reference model", "failure-account": "Industry practice"}
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
         18: "eighteen", 19: "nineteen", 20: "twenty", 21: "twenty-one", 22: "twenty-two", 23: "twenty-three", 24: "twenty-four"}
CAT_ORDER = ["Product", "Identity", "Specification", "Declaration", "Shelf life", "Sourcing", "Governance"]
LOOKUP_TITLE = {
    "DocumentTypes": "Kinds of document", "ProductClaimsTypes": "Kinds of claim", "ProductFoodBevAllergens": "Allergens by market", "UniversalAllergens": "Universal allergens", "ProductAllergensPresenceTypes": "Whether an allergen is contained or may be present",
    "ProductLabelItemsTypes": "Label items", "ProductNutritionValuesBasisTypes": "How a nutrition value was arrived at",
    "ProductNutritionValuesNutrientTypes": "Nutrients", "ProductShelfLivesDateMarkTypes": "Date marks",
    "ProductVariantsAxisTypes": "Ways variants differ", "MasterCrossRefTypes": "Identifier types",
    "UniversalCountryCodes": "Country codes", "UniversalUnitOfMeasureCodes": "Units of measure", "UniversalRegions": "Wider markets",
    "UniversalLanguageCodes": "Languages", "ProductChannelsTypes": "Sales channels", "ProductImagesSides": "Sides of a product picture",
    "ProductImagesFileTypes": "Picture file types",
}
LOOKUP_ORDER = ["DocumentTypes", "ProductClaimsTypes", "UniversalAllergens", "ProductFoodBevAllergens", "ProductAllergensPresenceTypes", "ProductLabelItemsTypes", "ProductNutritionValuesBasisTypes",
                "ProductNutritionValuesNutrientTypes", "ProductShelfLivesDateMarkTypes", "ProductVariantsAxisTypes", "MasterCrossRefTypes",
                "UniversalCountryCodes", "UniversalRegions", "UniversalLanguageCodes", "ProductChannelsTypes", "ProductImagesSides",
                "ProductImagesFileTypes", "UniversalUnitOfMeasureCodes"]


def load(p: Path) -> Json:
    return json.loads(p.read_text(encoding="utf-8"))


def words(n: int) -> str:
    return WORDS.get(n, str(n))


def plain(code: str) -> str:
    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", code)


def anchor(i: str) -> str:
    return f'<a id="{i.lower()}"></a>'


def link(i: str) -> str:
    return f"[{i}](#{i.lower()})"


def article(w: str) -> str:
    return "an" if w[:1].lower() in "aeiou" else "a"


def active(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in items if x.get("status", "active") == "active"]


# ------------------------------------------------------------------ change package
def build_changeset(pkg: Path, countries: list[dict[str, Any]]) -> dict[str, Any]:
    subjects = active(load(pkg / "subjects.json"))
    verbs = active(load(pkg / "verbs.json"))
    attrs = active(load(pkg / "attributes.json"))
    lookups = active(load(pkg / "lookups.json"))
    roles = {r["id"]: r for r in load(pkg / "roles.json")}
    domains = {d["id"]: d for d in load(pkg / "domains.json")["domains"]}
    ops: list[dict[str, Any]] = []
    seq_of: dict[str, int] = {}

    def add(op: str, entity: str, local: str, dda: str | None, fields: dict[str, Any], deps: list[int]) -> int:
        n = len(ops) + 1
        ops.append({"seq": n, "op": op, "entity": entity, "local_id": local, "dda_id": dda, "fields": fields, "depends_on": deps})
        seq_of[local] = n
        return n

    for l in lookups:
        if l["dda_action"] == "create":
            vals = []
            for v in l["values"]:
                row = {"lookup_code": v["code"], "lookup_name": v["name"], "lookup_description": v["definition"]}
                if v.get("parent_lookup"):
                    row["lookup_parent"] = {"lookup_type": v["parent_lookup"], "lookup_code": v["parent_code"]}
                elif v.get("parent_code"):
                    row["lookup_parent_code"] = v["parent_code"]
                vals.append(row)
            lk_deps = sorted({seq_of[v["parent_lookup"]] for v in l["values"] if v.get("parent_lookup") and v["parent_lookup"] in seq_of})
            add("create", "lookupTypes", l["id"], None, {"lookup_type_code": l["code"], "lookup_type_name": l["code"],
                                                           "lookup_type_description": l["definition"], "lookups": vals}, lk_deps)
        elif l["dda_action"] == "extend":
            add("update", "lookupTypes", l["id"], l["dda_id"],
                {"lookups_to_add": [{"lookup_code": v["code"], "lookup_name": v["name"], "lookup_description": v["definition"]} for v in l["values"]]}, [])

    lk_by = {l["id"]: l for l in lookups}
    sb_by = {s["id"]: s for s in subjects}
    pending = [s for s in subjects if s["dda_action"] == "create"]
    done: set[str] = set()
    while pending:
        progressed = False
        for s in list(pending):
            par = s.get("parent_id")
            if par and sb_by[par]["dda_action"] == "create" and par not in done:
                continue
            f: dict[str, Any] = {"concept_code": s["code"], "concept_name": s["code"], "concept_description": s["definition"]}
            deps: list[int] = []
            if par:
                f["concept_parent"] = sb_by[par]["dda_id"] if sb_by[par]["dda_id"] else par
                f["concept_parent_rel"] = s["parent_cardinality"]
                if par in seq_of:
                    deps.append(seq_of[par])
            else:
                f["concept_parent"] = "DMC000000100"
                f["concept_parent_rel"] = "ONE_TO_ONE_OPTIONAL"
                f["concept_is_domain"] = domains[s["domain_id"]]["dda_id"]
            add("create", "concepts", s["id"], None, f, deps)
            done.add(s["id"])
            pending.remove(s)
            progressed = True
        if not progressed:
            raise SystemExit("concept parents do not resolve")

    def pascal(name: str) -> str:
        return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", name) if w)

    def title(verb: str) -> str:
        return " ".join(w[:1].upper() + w[1:] for w in verb.split())

    used_roles = sorted({x for r in verbs for x in (r["source_role_id"], r["target_role_id"])})
    for rid in used_roles:
        ro = roles[rid]
        add("create", "roles", rid, None, {
            "role_code": "CPG" + pascal(ro["name"]), "role_name": ro["name"], "role_description": ro["definition"],
            "role_domains": [domains[d]["dda_id"] for d in ro["played_by_domain_ids"]]}, [])

    for order, r in enumerate(verbs, start=1):
        deps = [seq_of[r["source_role_id"]], seq_of[r["target_role_id"]]]
        add("create", "relationships", r["id"], None, {
            "relationship_code": r["code"], "relationship_name": r.get("name_override") or r["code"],
            "relationship_description": r["definition"],
            "relationship_domain": domains[r["source_domain_id"]]["dda_id"],
            "relationship_destination_domain": domains[r["destination_domain_id"]]["dda_id"],
            "relationship_forward_verb": title(r["forward_verb"]), "relationship_inverse_verb": title(r["inverse_verb"]),
            "relationship_source_role": r["source_role_id"], "relationship_target_role": r["target_role_id"],
            "relationship_source_role_plural": roles[r["source_role_id"]]["plural"], "relationship_target_role_plural": roles[r["target_role_id"]]["plural"],
            "relationship_cardinality": r["cardinality"], "relationship_dates": r["dates"], "relationship_order": order}, sorted(set(deps)))

    # the model that DDA already holds for this field gathers the relationships; its roles are reached through them
    model = load(pkg / "scope.json")["model"]
    model_text = model["description"]
    add("update", "models", model["dda_id"], model["dda_id"], {
        "model_description": model_text, "model_relationships": [r["id"] for r in verbs]}, [seq_of[r["id"]] for r in verbs])

    for a in attrs:
        f = {"attribute_code": a["code"], "attribute_name": a["code"], "attribute_fqn_name": a["code"],
             "attribute_description": a["definition"], "attribute_type": a["datatype"]}
        deps: list[int] = []
        if a["lookup_id"]:
            l = lk_by[a["lookup_id"]]
            f["attribute_lookup_type"] = l["dda_id"] if l["dda_id"] else l["id"]
            if a["lookup_id"] in seq_of:
                deps.append(seq_of[a["lookup_id"]])
        if a.get("classification"):
            f["attribute_class"] = a["classification"]
        if a["subject_id"]:
            f["attribute_concept"] = a["subject_id"]
            if a["subject_id"] in seq_of:
                deps.insert(0, seq_of[a["subject_id"]])
        else:
            f["attribute_relationship"] = a["relationship_id"]
            deps.insert(0, seq_of[a["relationship_id"]])
        add("create", "attributes", a["id"], None, f, deps)

    # each country in the existing country list names the region it sits in
    reg = seq_of.get("LKP012")
    for c in countries:
        add("update", "lookups", f"LKP010:{c['country_code']}", c["dda_id"],
            {"lookup_parent": {"lookup_type": "LKP012", "lookup_code": c["region_code"]}}, [reg] if reg else [])
    return {"spec_version": "31.5", "package_ref": "fnb-bdd", "apply_mode": "web-ui", "preconditions": [], "operations": ops}


# ------------------------------------------------------------------ document
def render(pkg: Path, prev: Path, changeset: dict[str, Any]) -> str:
    scope = load(pkg / "scope.json")
    sources = active(load(pkg / "sources.json"))
    reqs = active(load(pkg / "requirements.json"))
    drqs = active(load(pkg / "data-requirements.json"))
    doms = load(pkg / "domains.json")["domains"]
    doms = sorted(active(doms), key=lambda d: ["DOM001", "DOM003", "DOM002", "DOM004"].index(d["id"]))
    subjects = active(load(pkg / "subjects.json"))
    roles = active(load(pkg / "roles.json"))
    verbs = active(load(pkg / "verbs.json"))
    attrs = active(load(pkg / "attributes.json"))
    lookups = active(load(pkg / "lookups.json"))
    state = load(pkg / "state.json")
    baseline = load(pkg / "baseline.json")
    countries = load(pkg / "country-regions.json")
    bd = {d["dda_id"]: d for d in baseline["domains"]}
    dom_by = {d["id"]: d for d in doms}
    role_by = {r["id"]: r for r in roles}
    sb_by = {s["id"]: s for s in subjects}
    req_by = {r["id"]: r for r in reqs}
    src_by = {s["id"]: s for s in sources}
    prev_text = prev.read_text(encoding="utf-8")

    def dname(did: str) -> str:
        return plain(dom_by[did]["code"])

    def dda_link(kind: str, i: str | None) -> str:
        return "New" if not i else f"[{i}]({BASE}/{kind}/{i})"

    def req_links(ids: list[str]) -> str:
        return " · ".join(link(i) for i in ids if i in req_by)

    out: list[str] = []
    w = out.append
    lines = prev_text.split("\n")

    # ---- cover, version, contents, introduction (static, with the dated rows replaced)
    start_13 = lines.index("### 1.3 Summary of Findings")
    head = "\n".join(lines[:start_13])
    today = datetime.date.today()
    head = re.sub(r"\| Document date \| [^|]+ \|", f"| Document date | {today.day} {today.strftime('%B %Y')} |", head)
    head = head.replace("what goes into it, what it must be, how long it lasts, who may supply its ingredients and what may be said about it on pack. The full",
                        "what goes into it, where it is sold, what it must be, how long it lasts, who may supply its ingredients and what may be said about it on pack. The full")
    w(head.rstrip("\n"))
    w("")

    # ---- 1.3 summary
    n_concept_new = sum(1 for s in subjects if s["dda_action"] == "create")
    n_rel_new = sum(1 for r in verbs if r["dda_action"] == "create")
    n_lk_new = sum(1 for l in lookups if l["dda_action"] == "create")
    n_lk_ext = sum(1 for l in lookups if l["dda_action"] == "extend")
    ext_vals = sum(len(l["values"]) for l in lookups if l["dda_action"] == "extend")
    n_dom_re = sum(1 for d in doms if d["dda_action"] == "reuse")
    n_con_re = sum(1 for s in subjects if s["dda_action"] == "reuse")
    n_lk_re = sum(1 for l in lookups if l["dda_action"] == "reuse")
    w("### 1.3 Summary of Findings")
    w("")
    w("This design covers what a food or beverage product is, what goes into it, where it is sold, what it must be, how long it lasts, who may supply its ingredients and what may be said about it on pack. "
      "The formulation, meaning the list of what goes into a product and how much, is at its heart. The order ingredients are listed in, the allergens, the nutrition values and the claims on a pack all follow from the formulation, "
      "so a change to it shows which labels and claims it reaches. Where an ingredient is bought in already made, the design relies on what the supplier declares is inside it, and records who declared it and whether it was checked.")
    w("")
    w("Products are held in two layers. Each size, pack and recipe is a product in its own right, with its own identifiers, formulation, allergens and label. "
      "A product definition above them groups the versions that belong together and is never made, bought or sold itself. "
      "A product is listed in markets, each named by a country or by a wider region, and the items on its pack, the claims it makes and the sales channels it uses hang from that listing. "
      "The design covers three markets, the United States, the European Union and the United Kingdom, and no others. It holds a market as a value in its lists, so it extends to any other country or wider region without a change of structure, but none is included here by choice.")
    w("")
    w("The design has three stated limits. It cannot say what is inside a bought-in ingredient beyond what the supplier declares. It finds every product that uses a recalled ingredient but not which batches. Batches, factories and the places inside them down to the shop floor, supplier sites and supply chain detail belong to the proposed CPG Manufacturing and Supply Chain model. "
      "It keeps a shelf life for each product and does not work one out from the shelf lives of its ingredients, because none of the sources describe a rule for doing so.")
    w("")
    w("**What the business can answer with this design**")
    w("")
    for q in ("We reformulate to cut sugar by 30%. Which claims and labels does that reach?",
              "A supplier changes what is inside an ingredient. Which of our labels does that reach?",
              "Which allergens must this product declare, and which ingredient brings each one?",
              "Which suppliers may supply this ingredient today, and which could on a past date?",
              "Which of this ingredient's stated properties did we check, and which did we take on the supplier's word?",
              "Where and through which channels is this product sold, and what must its pack say there?"):
        w(f"- {q}")
    w("")
    tail = (f"names the region each of the {len(countries)} countries in the existing country list sits in, and reuses " if countries else "and reuses ")
    lists_word = "list" if n_lk_re == 1 else "lists"
    w(f"This design creates {words(n_concept_new)} concepts, {words(len(roles))} roles, {words(n_rel_new)} relationships and {words(n_lk_new)} lists of values in DDA, gathers the relationships into the existing {load(pkg / 'scope.json')['model']['name']} model, adds {words(ext_vals)} values to {words(n_lk_ext)} existing {'list' if n_lk_ext == 1 else 'lists'}, "
      + tail + f"{words(n_dom_re)} existing domains, {words(n_con_re)} existing concepts and {words(n_lk_re)} existing {lists_word} of values.")
    w("")
    w("|  | Count |")
    w("|---|---|")
    w(f"| Business requirements | {len(reqs)} |")
    w(f"| Data requirements | {len(drqs)} |")
    w(f"| Areas of the business covered (domains) | {len(doms)} ({n_dom_re} already in DDA) |")
    w(f"| Roles, meaning the part something plays in a relationship | {len(roles)} |")
    w(f"| Relationships between roles | {len(verbs)} |")
    w(f"| Concepts, meaning groups of related facts | {len(subjects)} |")
    w(f"| Lists of allowed values | {len(lookups)} |")
    w(f"| Sources | {len(sources)} |")
    w("")

    # ---- 2 scope
    w("## 2 Scope")
    w("")
    w("### 2.1 The business")
    w("")
    w(scope["business"])
    w("")
    w("### 2.2 In scope")
    w("")
    w("| ID | In scope |")
    w("|---|---|")
    for i in scope["in_scope"]:
        w(f"| {i['id']} | {i['statement']} |")
    w("")
    w("### 2.3 Out of scope")
    w("")
    w("What this design leaves out, and the model that is intended to own it. The CPG Manufacturing and Supply Chain model is proposed and is not yet in DDA.")
    w("")
    w("| ID | Out of scope | Owned by another model |")
    w("|---|---|---|")
    for i in scope["out_of_scope"]:
        w(f"| {i['id']} | {i['statement']} | {i['owned_by']} |")
    w("")
    w("### 2.4 Shared with other models")
    w("")
    w("These are used as DDA already holds them.")
    w("")
    w("| ID | Shared area | In DDA |")
    w("|---|---|---|")
    for i in scope["shared_objects"]:
        w(f"| {i['id']} | {i['name'].title()} | [{i['dda_id']}]({BASE}/domains/{i['dda_id']}) |")
    w("")
    w("### 2.5 Assumptions")
    w("")
    w("| ID | Assumption |")
    w("|---|---|")
    for i in scope["assumptions"]:
        w(f"| {i['id']} | {i['statement']} |")
    w("")
    w("### 2.6 Open questions")
    w("")
    w("| ID | Question |")
    w("|---|---|")
    for i in scope["questions_unanswered"]:
        w(f"| {i['id']} | {i['note']} |")
    w("")

    # ---- 3 business requirements
    w("## 3 Business Requirements")
    w("")
    w("Each requirement can be checked against the source beside it. Which rules apply to a product depends on the market it is sold in (assumption SCA008).")
    w("")
    w("| ID | Category | Business requirement | Proposed owner | Sources |")
    w("|---|---|---|---|---|")
    for r in sorted(reqs, key=lambda r: (CAT_ORDER.index(r["category"]) if r["category"] in CAT_ORDER else 99, r["id"])):
        s = ", ".join(f"[{i}]({src_by[i]['url']})" for i in r["source_ids"])
        w(f"| {anchor(r['id'])}{r['id']} | {r['category']} | {r['statement']} | {r['owner']} | {s} |")
    w("")

    # ---- 4 data requirements
    w("## 4 Data Requirements")
    w("")
    w("What the business must keep, the questions it must be able to answer, and the mistakes the design prevents. Each links back to the requirements it serves.")
    w("")
    w("| ID | The business must keep | It must be able to answer | When | Mistakes it must prevent | How the design prevents them | Requirements |")
    w("|---|---|---|---|---|---|---|")
    when = {"current": "Today", "as-at": "On any past date", "both": "Today and on any past date"}

    def cell(items: list[str]) -> str:
        return "<br>".join(items) if items else "—"

    for d in drqs:
        w(f"| {anchor(d['id'])}{d['id']} | {cell(d['must_record'])} | {cell(d['must_answer'])} | {when[d['temporality']]} | {cell(d['must_prevent'])} | {cell(d['prevent_how'])} | {req_links(d['business_requirement_ids'])} |")
    w("")

    # ---- 5 data model
    w("## 5 Data Model")
    w("")
    sect5 = prev_text.split("## 5 Data Model\n\n")[1].split("\n\n### 5.1 Diagrams")[0]
    w(sect5)
    w("")
    mdl = load(pkg / "scope.json")["model"]
    w(f"**The model.** DDA already holds a model for this field, **{mdl['name']}** ({mdl['dda_id']}), with nothing yet in it. The design gathers the {words(len(verbs))} relationships in 5.4 into it, and the {words(len(roles))} roles in 5.3 are reached through them. Its description reads:")
    w("")
    w(f"> {mdl['description']}")
    w("")
    w("### 5.1 Diagrams")
    w("")
    w("The diagrams come first, as a map of the model. The tables that follow give every area, role, relationship and concept in full: areas in 5.2, roles in 5.3, relationships in 5.4, concepts in 5.5 and lists of values in 5.6.")
    w("")
    w("#### 5.1.1 Domains Data Model")
    w("")
    w("One box for each area of the business. Each arrow is one relationship, labelled with the role at each end and the verb between them. An arrow that returns to its own box is a relationship between two things of the same kind. Areas DDA already holds are solid.")
    w("")
    w("```mermaid")
    w("flowchart LR")
    order = [d for d in doms]
    for d in order:
        anc = sb_by[d["anchor_subject_id"]]
        w(f'  {d["id"]}("{plain(anc["code"])}<br>{dname(d["id"]).upper()}")')
    for r in verbs:
        w(f'  {r["source_domain_id"]} -->|"{role_by[r["source_role_id"]]["name"]} → {r["forward_verb"]} → {role_by[r["target_role_id"]]["name"]}"| {r["destination_domain_id"]}')
    w("  classDef indda fill:#1f3a5f,stroke:#0d1f33,stroke-width:2px,color:#fff")
    w("  classDef prop fill:#3d2b56,stroke:#241733,stroke-width:2px,color:#fff,stroke-dasharray:5 3")
    w("  class " + ",".join(d["id"] for d in order) + " indda")
    w("```")
    w("")
    w("#### 5.1.2 Roles Data Model")
    w("")
    w("One diagram of every role. Each box is an area of the business, and holds the roles that area plays. An arrow joins the two roles of a relationship, labelled with its verb, and runs between boxes wherever the two roles belong to different areas. The same product can play several roles at once, which is why its roles share a box.")
    w("")
    w("```mermaid")
    w("flowchart LR")
    for d in doms:
        rs = [r for r in roles if d["id"] in r["played_by_domain_ids"]]
        if not rs:
            continue
        w(f'  subgraph SG{d["id"]}["{dname(d["id"])}"]')
        for r in rs:
            w(f'    {r["id"]}("{r["name"]}")')
        w("  end")
    for r in verbs:
        w(f'  {r["source_role_id"]} -->|{r["forward_verb"]}| {r["target_role_id"]}')
    w("```")
    w("")
    w("#### 5.1.3 Concept Models by Domain")
    w("")
    w("One diagram per area: its main concept and the concepts beneath it, each arrow saying how many of the lower concept the upper one may have. Only the concepts this design uses are shown.")
    w("")
    for d in doms:
        ss = [s for s in subjects if s["domain_id"] == d["id"]]
        if len(ss) < 2:
            continue
        w(f"**{dname(d['id'])}**")
        w("")
        w("```mermaid")
        w("flowchart LR")
        for s in ss:
            w(f'  {s["id"]}("{plain(s["code"])}<br>{dname(d["id"]).upper()}")')
        for s in ss:
            if s["parent_id"]:
                w(f'  {s["parent_id"]} -->|"{CARD[s["parent_cardinality"]]}"| {s["id"]}')
        w("```")
        w("")

    # 5.2 domains
    w("### 5.2 Subject Domains")
    w("")
    w("| Domain | In DDA | Main concept | What it covers | Roles | Concepts |")
    w("|---|---|---|---|---|---|")
    for d in doms:
        nr = len([r for r in roles if d["id"] in r["played_by_domain_ids"]])
        ns = len([s for s in subjects if s["domain_id"] == d["id"]])
        w(f"| {anchor(d['id'])}{d['id']}<br>**{dname(d['id'])}** | {dda_link('domains', d['dda_id'])} | {plain(sb_by[d['anchor_subject_id']]['code'])} | {d['used_here']} | [{nr}](#53-canonical-roles) | [{ns}](#55-concepts) |")
    w("")

    # 5.3 roles
    w("### 5.3 Canonical Roles")
    w("")
    w("A role describes what something is while it is in a relationship. The same product can play several roles at once.")
    w("")
    w("| Area | Role | What it means | Requirements |")
    w("|---|---|---|---|")
    for r in roles:
        area = dname(r["played_by_domain_ids"][0])
        w(f"| {area} | {anchor(r['id'])}{r['id']}<br>**{r['name']}** | {r['definition']} | {req_links(r['stated_in'])} |")
    w("")

    # 5.4 relationships
    w("### 5.4 Role–Verb–Role Relationships")
    w("")
    w("Each relationship reads as two sentences, one in each direction. *How many* says how many on one side can link to the other. *Dates kept* says whether each link records when it starts and stops.")
    w("")
    w("| ID | How it reads | How many | Dates kept | Why it is needed | In DDA |")
    w("|---|---|---|---|---|---|")

    def rl(r: dict[str, Any], plural: bool) -> str:
        nm = r["plural"] if plural else r["name"]
        return f"[{nm.lower()}](#{r['id'].lower()})"

    for r in verbs:
        s, t = role_by[r["source_role_id"]], role_by[r["target_role_id"]]
        card = r["cardinality"]
        fwd_obj_plural = card not in ("MANY_TO_ONE", "ONE_TO_ONE")
        inv_obj_plural = card not in ("ONE_TO_MANY", "ONE_TO_ONE")
        a1 = article(s["name"]).capitalize()
        fwd_obj = rl(t, True) if fwd_obj_plural else f"{article(t['name'])} {rl(t, False)}"
        a2 = article(t["name"]).capitalize()
        inv_obj = rl(s, True) if inv_obj_plural else f"{article(s['name'])} {rl(s, False)}"
        read = f"{a1} {rl(s, False)} {r['forward_verb']} {fwd_obj}.<br>{a2} {rl(t, False)} {r['inverse_verb']} {inv_obj}."
        w(f"| {anchor(r['id'])}{r['id']} | {read} | {REL_CARD[card]} | {'Yes' if r['dates'] else 'No'} | {' · '.join(link(i) for i in r['data_requirement_ids'])} | {dda_link('relationships', r['dda_id'])} |")
    w("")

    # 5.5 concepts
    w("### 5.5 Concepts")
    w("")
    w("Every concept the design uses, whether DDA already has it or the design adds it. The code beneath each name is its DDA name.")
    w("")
    w("| Area | Concept | In DDA | What it is | Sits under | How many | Why it is needed |")
    w("|---|---|---|---|---|---|---|")
    singular = {"SBJ019": "product market", "SBJ001": "product", "SBJ013": "legal entity", "SBJ016": "document"}
    for d in doms:
        for s in [x for x in subjects if x["domain_id"] == d["id"]]:
            text = s["definition"] or s.get("used_here") or ""
            if s["parent_id"]:
                p = sb_by[s["parent_id"]]
                under = plain(p["code"]).replace("Product ", "Product ") if False else plain(p["code"])
                under_cell = under if p["code"] not in ("Product", "LegalEntity", "Document") else plain(p["code"])
                pn = singular.get(p["id"], plain(p["code"]).lower())
                how = f"Each {pn} {CARD_ROW[s['parent_cardinality']]}"
            else:
                under_cell, how = "—", "—"
            nm = plain(s["code"])
            w(f"| {dname(d['id'])} | {anchor(s['id'])}{s['id']}<br>**{nm}**<br>{s['code']} | {dda_link('concepts', s['dda_id'])} | {text} | {under_cell} | {how} | {' · '.join(link(i) for i in s['data_requirement_ids'])} |")
    w("")

    # 5.6 lookups
    w("### 5.6 Lookups and Values")
    w("")
    w("Each list is a fixed set of allowed answers, so the same thing is always described the same way. Where a list is used by a relationship rather than a concept, the name beside it is that relationship's own group of facts, such as Product Composition for the lines of a formulation.")
    w("")
    lk_by = {l["code"]: l for l in lookups}
    rel_by = {r["id"]: r for r in verbs}
    for code in LOOKUP_ORDER:
        l = lk_by.get(code)
        if not l:
            continue
        w(f"#### {LOOKUP_TITLE[code]}")
        w("")
        if l["dda_action"] == "extend":
            if code == "MasterCrossRefTypes":
                w("Adds three identifier types for products, the trade item number, the organisation's own material number and a supplier's part number, to the existing list of identifier types, which already covers identifiers of legal entities.")
            else:
                w(l["definition"] + " DDA already holds this list, created without values. CPG Manufacturing and Supply Chain contributes the same values.")
        elif l["dda_action"] == "reuse":
            w(l.get("used_here") or "")
        else:
            w(l["definition"])
        w("")
        used: list[str] = []
        for a in sorted(attrs, key=lambda x: 0 if x["subject_id"] else 1):
            if a["lookup_id"] == l["id"]:
                if a["subject_id"]:
                    nm = plain(sb_by[a["subject_id"]]["code"])
                else:
                    nm = plain(rel_by[a["relationship_id"]]["code"])
                if nm not in used:
                    used.append(nm)
        for other in lookups:
            if any(x.get("parent_lookup") == l["id"] for x in other["values"]) and LOOKUP_TITLE[other["code"]] not in used:
                used.append(LOOKUP_TITLE[other["code"]].lower() + " (each names one of these)")
        w("| List | In DDA | Used for |")
        w("|---|---|---|")
        w(f"| {anchor(l['id'])}{l['id']} {l['code']} | {dda_link('lookup-types', l['dda_id'])} | {', '.join(used)} |")
        w("")
        if l["dda_action"] == "reuse":
            w("The values are kept in DDA and are not repeated here.")
            w("")
            if code == "UniversalCountryCodes" and countries:
                w(f"This design also names the region each of the {len(countries)} countries sits in, using the list of regions below. The region is the country's parent in the list. The mapping is held in the change package.")
                w("")
            continue
        if l["dda_action"] == "extend":
            w("Values this design contributes to the existing list:")
            w("")
        w("| Value | Meaning |")
        w("|---|---|")
        lk_names = {x["id"]: {y["code"]: y["name"] for y in x["values"]} for x in lookups}
        for v in l["values"]:
            note = ""
            if v.get("parent_lookup"):
                note = f"<br>*Universal allergen: {lk_names[v['parent_lookup']][v['parent_code']]}*"
            elif v.get("parent_code"):
                note = f"<br>*Part of: {lk_names[l['id']][v['parent_code']]}*"
            w(f"| **{v['name']}**<br>{v['code']} | {v['definition']}{note} |")
        w("")
        if code == "UniversalRegions" and countries:
            conts = {v["code"]: v["name"] for v in l["values"] if not v.get("parent_code")}
            counts: dict[str, int] = {}
            for c in countries:
                counts[c["region_code"]] = counts.get(c["region_code"], 0) + 1
            w("Each country in the country list sits in one region, and each region on one continent. The number of countries in each region:")
            w("")
            w("| Region | Continent | Countries |")
            w("|---|---|---|")
            for v in l["values"]:
                if v.get("parent_code") and v["code"] != "EU":
                    w(f"| {v['name']} | {conts[v['parent_code']]} | {counts.get(v['code'], 0)} |")
            w(f"| Antarctica | Antarctica | {counts.get('ANTARCTICA', 0)} |")
            w("")

    # 6 decisions
    w("## 6 Outstanding Decisions")
    w("")
    w("Design choices that remain open.")
    w("")
    w("| ID | Decision | Options |")
    w("|---|---|---|")
    for d in state["decisions"]:
        if d["status"] == "open":
            w(f"| {d['id']} | {d['question']} | {' · '.join(d['options'])} |")
    w("")

    # Appendix A
    w("## Appendix A — Sources")
    w("")
    w("Every statement in this design rests on at least one of these. Each title links to the source.")
    w("")
    w("| ID | Source | Organisation | Type | Why it is included | Supports |")
    w("|---|---|---|---|---|---|")
    for s in sources:
        sup = [r["id"] for r in reqs if s["id"] in r["source_ids"]]
        w(f"| {s['id']} | [{s['title']}]({s['url']}) | {s['organisation']} | {SRC_TYPE[s['type']]} | {s['why_included']} | {req_links(sup)} |")
    w("")

    # Appendix B (static, with the figures refreshed)
    appb = "## Appendix B" + prev_text.split("## Appendix B", 1)[1]
    act = attrs
    n_class = sum(1 for a in act if a["classification"])
    n_crit = sum(1 for a in act if a["critical"])
    appb = re.sub(r"design starts from \d+ published sources", f"design starts from {len(sources)} published sources", appb)
    appb = re.sub(r"There are \w+ relationships \(section 5\.4\)", f"There are {words(len(verbs))} relationships (section 5.4)", appb)
    appb = re.sub(r"\(\d+ steps in dependency order\)", f"({len(changeset['operations'])} steps in dependency order)", appb)
    appb = re.sub(r"Sensitivity is set on \d+ of the facts the design keeps, where it applies, and \d+ are marked critical",
                  f"Sensitivity is set on {n_class} of the facts the design keeps, where it applies, and {n_crit} are marked critical", appb)
    appb = appb.replace("Suppliers, certifying bodies and the business named on a pack are Legal Entities playing roles in the same way.",
                        "Suppliers, certifying bodies and the business named on a pack are Legal Entities playing roles in the same way.")
    w(appb.rstrip("\n"))
    w("")
    return "\n".join(out)


def main(pkg: Path, prev: Path, dest: Path) -> None:
    countries = load(pkg / "country-regions.json")
    cs = build_changeset(pkg, countries)
    (pkg / "dda-changeset.json").write_text(json.dumps(cs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = render(pkg, prev, cs)
    dest.write_text(md, encoding="utf-8")
    h = hashlib.sha256(md.encode("utf-8")).hexdigest()
    print("changeset ops:", len(cs["operations"]), "| document bytes:", len(md.encode()), "| sha256:", h[:12])


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
