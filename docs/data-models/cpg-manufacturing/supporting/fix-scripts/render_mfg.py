#!/usr/bin/env python3
"""Render the lite Data Design Document for the CPG Manufacturing and Supply Chain package.

Usage: render_mfg.py <package-dir> <static-source.md> <output.md>

Every figure and table is projected from the package. The only static text is the cover paragraph,
sections 1.1 and 1.2 (supplied by the practice and reproduced verbatim from <static-source.md>).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

Json = Any
BASE = "https://datadesign.maoperatingsystem.com/models"
REL_CARD = {"MANY_TO_MANY": "Many to many", "MANY_TO_ONE": "Many to one", "ONE_TO_MANY": "One to many", "ONE_TO_ONE": "One to one"}
CARD_EDGE = {"ONE_TO_MANY_OPTIONAL": "may have many, or none", "ONE_TO_MANY_MANDATORY": "has one or many",
             "ONE_TO_ONE_OPTIONAL": "may have one, or none", "ONE_TO_ONE_MANDATORY": "has exactly one"}
CARD_ROW = {"ONE_TO_MANY_OPTIONAL": "many, or none", "ONE_TO_MANY_MANDATORY": "one or many",
            "ONE_TO_ONE_OPTIONAL": "one, or none", "ONE_TO_ONE_MANDATORY": "exactly one"}
SRC_TYPE = {"standard": "Industry standard", "regulatory": "Regulator or law", "practitioner": "Industry practice",
            "reference-model": "Reference model"}
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
         18: "eighteen", 19: "nineteen", 20: "twenty"}
TODAY = "18 November 2026"
WHEN = {"current": "Today", "as-at": "On any past date", "both": "Today and on any past date"}
RESULT = {"pass": "Pass", "accepted-limit": "Limit accepted"}
TITLE = "CPG Manufacturing and Supply Chain"


def load(p: Path) -> Json:
    return json.loads(p.read_text(encoding="utf-8"))


def words(n: int) -> str:
    return WORDS.get(n, str(n))


def plain(code: str) -> str:
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", code)


def anchor(i: str) -> str:
    return f'<a id="{i.lower()}"></a>'


def link(i: str) -> str:
    return f"[{i}](#{i.lower()})"


def article(w: str) -> str:
    return "an" if w[:1].lower() in "aeiou" else "a"


def active(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in items if x.get("status", "active") == "active"]


def slug(heading: str) -> str:
    s = re.sub(r"[^\w\s-]", "", heading.lower().replace("—", "").replace("–", ""))
    return re.sub(r"\s", "-", s.strip())


def render(pkg: Path, static: Path) -> tuple[str, int]:
    scope = load(pkg / "scope.json")
    sources = active(load(pkg / "sources.json"))
    reqs = active(load(pkg / "requirements.json"))
    drqs = active(load(pkg / "data-requirements.json"))
    doms = active(load(pkg / "domains.json")["domains"])
    subjects = active(load(pkg / "subjects.json"))
    roles = active(load(pkg / "roles.json"))
    verbs = active(load(pkg / "verbs.json"))
    attrs = active(load(pkg / "attributes.json"))
    lookups = active(load(pkg / "lookups.json"))
    state = load(pkg / "state.json")
    baseline = load(pkg / "baseline.json")
    changeset = load(pkg / "dda-changeset.json")
    bd = {d["dda_id"]: d for d in baseline["domains"]}
    dom_by = {d["id"]: d for d in doms}
    role_by = {r["id"]: r for r in roles}
    sb_by = {s["id"]: s for s in subjects}
    req_by = {r["id"]: r for r in reqs}
    drq_by = {d["id"]: d for d in drqs}
    src_by = {s["id"]: s for s in sources}
    rel_by = {r["id"]: r for r in verbs}
    lk_by = {l["id"]: l for l in lookups}
    at_by = {a["id"]: a for a in attrs}
    st = static.read_text(encoding="utf-8").split("\n")

    def dname(did: str) -> str:
        return plain(dom_by[did]["code"])

    def dda_link(kind: str, i: str | None) -> str:
        return "New" if not i else f"[{i}]({BASE}/{kind}/{i})"

    def req_links(ids: list[str]) -> str:
        return " · ".join(link(i) for i in ids if i in req_by)

    def drq_links(ids: list[str]) -> str:
        return " · ".join(link(i) for i in ids if i in drq_by)

    def name_of(i: str) -> str:
        for m in (sb_by, rel_by, at_by, lk_by):
            if i in m:
                return plain(m[i]["code"])
        raise KeyError(i)

    out: list[str] = []
    w = out.append

    # ---------------------------------------------------------------- counts
    n_concept_new = sum(1 for s in subjects if s["dda_action"] == "create")
    n_concept_re = sum(1 for s in subjects if s["dda_action"] == "reuse" and s["dda_id"])
    n_concept_ref = sum(1 for s in subjects if s["dda_action"] == "reuse" and not s["dda_id"])
    n_rel_new = sum(1 for r in verbs if r["dda_action"] == "create")
    n_lk_new = sum(1 for l in lookups if l["dda_action"] == "create")
    n_lk_ext = sum(1 for l in lookups if l["dda_action"] == "extend")
    ext_vals = sum(len(l["values"]) for l in lookups if l["dda_action"] == "extend")
    n_dom_re = sum(1 for d in doms if d["dda_action"] == "reuse")
    n_dom_ext = sum(1 for d in doms if d["dda_action"] == "extend")
    n_dom_new = sum(1 for d in doms if d["dda_action"] == "create")
    n_in_dda = n_dom_re + n_dom_ext
    scenarios = state["scenarios"]
    n_pass = sum(1 for s in scenarios if s["result"] == "pass")
    n_limit = sum(1 for s in scenarios if s["result"] != "pass")
    n_class = sum(1 for a in attrs if a["classification"])
    n_crit = sum(1 for a in attrs if a["critical"])
    open_decisions = [d for d in state["decisions"] if d["status"] == "open"]

    # ---------------------------------------------------------------- cover
    w(f"# {TITLE} Data Model Design Document")
    w("")
    w(st[2])
    w("")
    w("## Version")
    w("")
    w("|  |  |")
    w("|---|---|")
    w(f"| Domain | {scope['domain']} |")
    w(f"| Document date | {TODAY} |")
    w("| Package reference (the working files this document is produced from) | cpg-manufacturing |")
    w(f"| Method version | {state['spec_version']} |")
    w("| Edition | Lite |")
    w("")
    w("**In brief.** This design covers how a food and beverage manufacturer makes its product, in its own factories and through outside manufacturers: "
      "the materials it receives, the factory down to the shop floor, how each product is made, the batches that result, the tests and problems that follow, "
      "and how any batch is traced back to its ingredients and forward to where it went. "
      "The full summary, the questions it answers and the counts are in section 1.3. In this document, DDA means the Data Design Authority, the central register where the company's data model is kept.")
    w("")

    # ---------------------------------------------------------------- contents
    w("## Table of Contents")
    w("")
    toc = [
        (0, "1 Introduction"), (1, "1.1 About M&A Operating System"), (1, "1.2 About the MAOS Practical Data Modelling Approach"),
        (1, "1.3 Summary of Findings"),
        (0, "2 Scope"), (1, "2.1 The business"), (1, "2.2 In scope"), (1, "2.3 Out of scope"), (1, "2.4 Shared with other models"),
        (1, "2.5 Assumptions"), (1, "2.6 Open questions"),
        (0, "3 Business Requirements"), (0, "4 Data Requirements"), (0, "5 Data Model"),
        (1, "5.1 Diagrams"), (2, "5.1.1 Domains Data Model"), (2, "5.1.2 Roles Data Model"), (2, "5.1.3 Concept Models by Domain"),
        (1, "5.2 Subject Domains"), (1, "5.3 Canonical Roles"), (1, "5.4 Role–Verb–Role Relationships"), (1, "5.5 Concepts"),
        (1, "5.6 Lookups and Values"),
        (0, "6 Outstanding Decisions"), (1, "6.1 Decisions still open"), (1, "6.2 Where the design departs from DDA's principles"),
        (0, "Appendix A — Sources"), (0, "Appendix E — Business Test Cases"),
    ]
    for lvl, h in toc:
        w(f"{'  ' * lvl}- [{h}](#{slug(h)})")
    w("")
    w("**What this edition leaves out.** This is the lite edition, written for the business owner and the data steward. "
      "The full edition adds *Source Validation*, *Existing Model Findings*, *Conformance to DDA Standards*, *Exceptions*, *DDA Domain Definitions*, *Standards*, "
      "*New Subject Domains* and the *Data Dictionary* of every attribute. Nothing here is abridged: whole sections are left out, never part of a table. "
      "Ask for the full edition to read any of them.")
    w("")

    # ---------------------------------------------------------------- 1 introduction (supplied text, verbatim)
    s11 = st.index("### 1.1 About M&A Operating System")
    s13 = st.index("### 1.3 Summary of Findings")
    w("## 1 Introduction")
    w("")
    w("\n".join(st[s11:s13]).rstrip("\n"))
    w("")

    # ---------------------------------------------------------------- 1.3 summary
    w("### 1.3 Summary of Findings")
    w("")
    w("This design covers how a food and beverage manufacturer makes its product, in its own factories and through outside manufacturers. "
      "It holds the materials the organisation receives and the suppliers they come from, the factory and the places inside it down to the shop floor, the machines in those places, "
      "the way each product is made, the production runs and the batches they make, the testing, problems, corrections and release that follow, and the stock held at the organisation's own sites. "
      "Food and beverage is the one subgroup in scope; household, personal care, pet care and beauty are left for a later extension.")
    w("")
    w("Tracing is the thread through it. A batch is the one thing a trace starts from and ends at, so every link that matters for a recall, a complaint or a failed test points at a batch: "
      "what went into it, what came out of it, what was found against it, what was complained of and who was exposed. "
      "The links carry the quantity the recipe called for and the quantity actually used, so the design says how far a batch departed from its recipe. "
      f"The design is shown with three markets' traceability duties: the United States, the United Kingdom and the European Union (assumption SCA006).")
    w("")
    w("The design has stated limits. The chain of what goes into what stops at anything bought in already made, where only what the supplier declares is known, with who declared it (assumption SCA003, and test cases SCN037 and SCN038 in Appendix E). "
      "What a product is made from, what it must be and what its pack says belong to the CPG - Product Definition model (assumption SCA004). "
      "Costs are not held (assumption SCA007). Whether finished output is identified individually or only by batch is an open question (SCQ001), and the design supports both.")
    w("")
    w("**What the business can answer with this design**")
    w("")
    for sid in ("SCN004", "SCN006", "SCN007", "SCN023", "SCN029", "SCN031", "SCN034", "SCN042"):
        q = next(s["question"] for s in scenarios if s["id"] == sid)
        w(f"- {q if q.endswith('?') else q}")
    w("")
    w(f"This design creates {words(n_concept_new)} concepts, {words(len(roles))} roles, {words(n_rel_new)} relationships and {words(n_lk_new)} lists of values in DDA, "
      f"extends {words(n_dom_ext)} existing domain (Locations) with the structure of a factory, adds {words(ext_vals)} values to {words(n_lk_ext)} existing list, and reuses {words(n_dom_re)} existing domains and {words(n_concept_re)} existing concepts. "
      f"It refers to {words(n_concept_ref)} concept, Product, that CPG - Product Definition creates and owns. "
      f"It proposes {words(n_dom_new)} new domains.")
    w("")
    w("|  | Count |")
    w("|---|---|")
    w(f"| Business requirements | {len(reqs)} |")
    w(f"| Data requirements | {len(drqs)} |")
    w(f"| Areas of the business covered (domains) | {len(doms)} ({n_in_dda} already in DDA, {n_dom_new} proposed) |")
    w(f"| Roles, meaning the part something plays in a relationship | {len(roles)} |")
    w(f"| Relationships between roles | {len(verbs)} |")
    w(f"| Concepts, meaning groups of related facts | {len(subjects)} |")
    w(f"| Lists of allowed values | {len(lookups)} |")
    w(f"| Business test cases | {n_pass} pass · {n_limit} with a limit accepted |")
    w(f"| Sources | {len(sources)} |")
    w("")

    # ---------------------------------------------------------------- 2 scope
    w("## 2 Scope")
    w("")
    w("### 2.1 The business")
    w("")
    w(scope["business"])
    w("")
    subs = [g["name"] for g in scope["subgroups"]]
    w(f"The subgroup in scope is {' and '.join(subs).lower() if len(subs) < 3 else ', '.join(subs)}.")
    w("")
    w("### 2.2 In scope")
    w("")
    w("| ID | In scope |")
    w("|---|---|")
    for i in active(scope["in_scope"]):
        w(f"| {i['id']} | {i['statement']} |")
    w("")
    w("### 2.3 Out of scope")
    w("")
    w("What this design leaves out, and the model that is intended to own it.")
    w("")
    w("| ID | Out of scope | Owned by another model |")
    w("|---|---|---|")
    for i in active(scope["out_of_scope"]):
        w(f"| {i['id']} | {i['statement']} | {i['owned_by']} |")
    w("")
    w("### 2.4 Shared with other models")
    w("")
    w("These are used as DDA already holds them.")
    w("")
    w("| ID | Shared area | In DDA |")
    w("|---|---|---|")
    for i in active(scope["shared_objects"]):
        w(f"| {i['id']} | {i['name']} | [{i['dda_id']}]({BASE}/domains/{i['dda_id']}) |")
    w("")
    w("### 2.5 Assumptions")
    w("")
    w("| ID | Assumption |")
    w("|---|---|")
    for i in active(scope["assumptions"]):
        w(f"| {anchor(i['id'])}{i['id']} | {i['statement']} |")
    w("")
    w("### 2.6 Open questions")
    w("")
    w("| ID | Question |")
    w("|---|---|")
    for i in active(scope["questions_unanswered"]):
        w(f"| {anchor(i['id'])}{i['id']} | {i['note']} |")
    w("")

    # ---------------------------------------------------------------- 3 business requirements
    w("## 3 Business Requirements")
    w("")
    w("Each requirement can be checked against the sources beside it. Food traceability duties differ by market (assumption SCA006).")
    w("")
    w("| ID | Category | Business requirement | Proposed owner | Sources |")
    w("|---|---|---|---|---|")
    for r in sorted(reqs, key=lambda r: (r["category"], r["id"])):
        s = ", ".join(f"[{i}]({src_by[i]['url']})" for i in r["source_ids"] if i in src_by)
        w(f"| {anchor(r['id'])}{r['id']} | {r['category']} | {r['statement']} | {r['owner']} | {s} |")
    w("")

    # ---------------------------------------------------------------- 4 data requirements
    w("## 4 Data Requirements")
    w("")
    w("What the business must keep, the questions it must be able to answer, and the mistakes the design prevents. Each links back to the requirements it serves.")
    w("")
    w("| ID | The business must keep | It must be able to answer | When | Mistakes it must prevent | How the design prevents them | Requirements |")
    w("|---|---|---|---|---|---|---|")

    def cell(items: list[str]) -> str:
        return "<br>".join(items) if items else "—"

    def prevented_by(d: dict[str, Any], idx: int) -> str:
        for p in d["prevent_resolution"]:
            if p["must_prevent_index"] != idx:
                continue
            aid, how = p["artefact_id"], p["expressed_by"]
            if how == "mandatory-attribute":
                return f"The fact *{name_of(aid)}* must always be given."
            if how == "relationship-cardinality":
                return f"The relationship {link(aid)} (*{name_of(aid)}*) allows only the number of links it states."
            if how == "parent-cardinality":
                return f"The concept {link(aid)} (*{name_of(aid)}*) sits under its parent in the numbers it states."
            if how == "lookup":
                return f"{link(aid)} (*{name_of(aid)}*) allows only its listed values."
            if how == "dates":
                return f"*{name_of(aid)}* keeps a start and an end date."
            raise SystemExit(f"unhandled resolution {how}")
        return "—"

    for d in drqs:
        prevent = [f"{x}" for x in d["must_prevent"]]
        how = [prevented_by(d, i) for i in range(len(d["must_prevent"]))]
        w(f"| {anchor(d['id'])}{d['id']} | {cell(d['must_record'])} | {cell(d['must_answer'])} | {WHEN[d['temporality']]} | {cell(prevent)} | {cell(how)} | {req_links(d['business_requirement_ids'])} |")
    w("")

    # ---------------------------------------------------------------- 5 data model
    w("## 5 Data Model")
    w("")
    w("**How to read this section.** A *domain* is an area of the business the design keeps information about. A *concept* is a group of related facts kept about something in a domain. "
      "A *role* is the part something plays, such as a batch while it is being traced. A *relationship* links two roles with a verb that reads naturally in both directions. "
      "A *list of values* is a fixed set of allowed answers. Names follow DDA's naming rules, so a concept called LegalEntityAssessments is the group of facts about the assessments of a legal entity.")
    w("")
    w("### 5.1 Diagrams")
    w("")
    w("The diagrams come first, as a map of the model. The tables that follow give every area, role, relationship and concept in full: areas in 5.2, roles in 5.3, relationships in 5.4, concepts in 5.5 and lists of values in 5.6.")
    w("")
    w("#### 5.1.1 Domains Data Model")
    w("")
    w("One box for each area of the business. Each arrow is one relationship, labelled with the role at each end and the verb between them. An arrow that returns to its own box is a relationship between two things of the same kind. Areas DDA already holds are solid; proposed areas are dashed.")
    w("")
    w("```mermaid")
    w("flowchart LR")
    for d in doms:
        anc = sb_by[d["anchor_subject_id"]]
        w(f'  {d["id"]}("{plain(anc["code"])}<br>{dname(d["id"]).upper()}")')
    for r in verbs:
        w(f'  {r["source_domain_id"]} -->|"{role_by[r["source_role_id"]]["name"]} → {r["forward_verb"]} → {role_by[r["target_role_id"]]["name"]}"| {r["destination_domain_id"]}')
    w("  classDef indda fill:#1f3a5f,stroke:#0d1f33,stroke-width:2px,color:#fff")
    w("  classDef prop fill:#3d2b56,stroke:#241733,stroke-width:2px,color:#fff,stroke-dasharray:5 3")
    w("  class " + ",".join(d["id"] for d in doms if d["dda_action"] != "create") + " indda")
    w("  class " + ",".join(d["id"] for d in doms if d["dda_action"] == "create") + " prop")
    w("```")
    w("")
    w("#### 5.1.2 Roles Data Model")
    w("")
    w("One diagram of every role. Each box is an area of the business, and holds the roles that area plays. An arrow joins the two roles of a relationship, labelled with its verb, and runs between boxes wherever the two roles belong to different areas.")
    w("")
    w("```mermaid")
    w("flowchart LR")
    for d in doms:
        rs = [r for r in roles if r["played_by_domain_ids"][0] == d["id"]]
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
    w("One diagram per area: its main concept and the concepts beneath it, each arrow saying how many of the lower concept the upper one may have.")
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
            if s["parent_id"] and s["parent_id"] in sb_by:
                w(f'  {s["parent_id"]} -->|"{CARD_EDGE[s["parent_cardinality"]]}"| {s["id"]}')
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
        text = d["definition"] if d["dda_action"] != "reuse" else d["used_here"]
        w(f"| {anchor(d['id'])}{d['id']}<br>**{dname(d['id'])}** | {dda_link('domains', d['dda_id'])} | {plain(sb_by[d['anchor_subject_id']]['code'])} | {text} | [{nr}](#53-canonical-roles) | [{ns}](#55-concepts) |")
    w("")

    # 5.3 roles
    w("### 5.3 Canonical Roles")
    w("")
    w("A role describes what something is while it is in a relationship. The same thing can play several roles at once.")
    w("")
    w("| Area | Role | What it means | Requirements |")
    w("|---|---|---|---|")
    for d in doms:
        for r in sorted([x for x in roles if x["played_by_domain_ids"][0] == d["id"]], key=lambda x: x["name"]):
            w(f"| {dname(d['id'])} | {anchor(r['id'])}{r['id']}<br>**{r['name']}** | {r['definition']} | {req_links(r['stated_in'])} |")
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

    for r in sorted(verbs, key=lambda x: (x["source_domain_id"], x["source_role_id"], x["id"])):
        s, t = role_by[r["source_role_id"]], role_by[r["target_role_id"]]
        card = r["cardinality"]
        fwd_plural = card not in ("MANY_TO_ONE", "ONE_TO_ONE")
        inv_plural = card not in ("ONE_TO_MANY", "ONE_TO_ONE")
        a1, a2 = article(s["name"]).capitalize(), article(t["name"]).capitalize()
        fwd_obj = rl(t, True) if fwd_plural else f"{article(t['name'])} {rl(t, False)}"
        inv_obj = rl(s, True) if inv_plural else f"{article(s['name'])} {rl(s, False)}"
        read = f"{a1} {rl(s, False)} {r['forward_verb']} {fwd_obj}.<br>{a2} {rl(t, False)} {r['inverse_verb']} {inv_obj}."
        w(f"| {anchor(r['id'])}{r['id']}<br>{plain(r['code'])} | {read} | {REL_CARD[card]} | {'Yes' if r['dates'] else 'No'} | {drq_links(r['data_requirement_ids'])} | {dda_link('relationships', r['dda_id'])} |")
    w("")

    # 5.5 concepts
    w("### 5.5 Concepts")
    w("")
    w("Every concept the design uses, whether DDA already has it or the design adds it. The code beneath each name is its DDA name.")
    w("")
    w("| Area | Concept | In DDA | What it is | Sits under | How many | Why it is needed |")
    w("|---|---|---|---|---|---|---|")
    for d in doms:
        for s in [x for x in subjects if x["domain_id"] == d["id"]]:
            if s["parent_id"] and s["parent_id"] in sb_by:
                p = sb_by[s["parent_id"]]
                under, how = plain(p["code"]), f"For each {plain(p['code']).lower()}: {CARD_ROW[s['parent_cardinality']]}"
            else:
                under, how = "—", "—"
            w(f"| {dname(d['id'])} | {anchor(s['id'])}{s['id']}<br>**{plain(s['code'])}**<br>{s['code']} | {dda_link('concepts', s['dda_id']) if s['dda_id'] or not s.get('proposed_by') else 'Created by ' + s['proposed_by']} | {s['definition']} | {under} | {how} | {drq_links(s['data_requirement_ids'])} |")
    w("")

    # 5.6 lookups
    w("### 5.6 Lookups and Values")
    w("")
    w("Each list is a fixed set of allowed answers, so the same thing is always described the same way. Where a list is used by a relationship rather than a concept, the name beside it is that relationship's own group of facts.")
    w("")
    for l in sorted(lookups, key=lambda x: (0 if x["scope"] == "universal" else 1, x["code"])):
        w(f"#### {plain(l['code'])}")
        w("")
        w(l["definition"])
        w("")
        if l["dda_action"] == "extend":
            w("DDA already holds this list, created without values. The values below are what this design contributes to it. CPG - Product Definition contributes the same values.")
            w("")
        used: list[str] = []
        for a in sorted(attrs, key=lambda x: 0 if x["subject_id"] else 1):
            if a["lookup_id"] == l["id"]:
                nm = plain(sb_by[a["subject_id"]]["code"]) if a["subject_id"] else plain(rel_by[a["relationship_id"]]["code"])
                if nm not in used:
                    used.append(nm)
        w("| List | In DDA | Used for |")
        w("|---|---|---|")
        w(f"| {anchor(l['id'])}{l['id']} {l['code']} | {dda_link('lookup-types', l['dda_id'])} | {', '.join(used)} |")
        w("")
        w("| Value | Meaning |")
        w("|---|---|")
        for v in l["values"]:
            w(f"| **{v['name']}**<br>{v['code']} | {v['definition']} |")
        w("")

    # ---------------------------------------------------------------- 6 decisions and exceptions
    w("## 6 Outstanding Decisions")
    w("")
    w("### 6.1 Decisions still open")
    w("")
    w("Design choices that remain open.")
    w("")
    w("| ID | Decision | Options |")
    w("|---|---|---|")
    for d in open_decisions:
        w(f"| {d['id']} | {d['question']} | {' · '.join(d['options'])} |")
    w("")
    w("### 6.2 Where the design departs from DDA's principles")
    w("")
    w("DDA sets its design principles in its standard [DMS000000169](" + BASE + "/standards/DMS000000169). Every principle is met or does not apply, except the following, each stated with its consequence, its owner and the route back.")
    w("")
    w("| ID | Principle | What is not met | Consequence | Owner and route back |")
    w("|---|---|---|---|---|")
    for e in active(state["exceptions"]):
        kind = "**Conflict with a requirement.** " if e["kind"] == "conflict" else "**Not met.** "
        w(f"| {e['id']} | {e['principle']} | {kind}{e['justification']} | {e['consequence']} | **Owner:** {e['owner']}<br>{e['route_back']} |")
    w("")

    # ---------------------------------------------------------------- Appendix A
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

    # ---------------------------------------------------------------- Appendix E
    w("## Appendix E — Business Test Cases")
    w("")
    w("Each case is a question the business must be able to ask, with the path through the design that answers it. A case marked *Limit accepted* shows where the design stops by intention.")
    w("")
    w("| Case | Question | Kind | As at | Requirements | Walked through | Result | Note |")
    w("|---|---|---|---|---|---|---|---|")
    for sc in sorted(scenarios, key=lambda x: x["id"]):
        rq = sorted({rid for did in sc["data_requirement_ids"] if did in drq_by for rid in drq_by[did]["business_requirement_ids"]})
        path = " → ".join(name_of(i) for i in sc["path"])
        w(f"| {sc['id']} | {sc['question']} | {sc['kind'].title()} | {sc['as_at']} | {req_links(rq)} | {path} | {RESULT[sc['result']]} | {sc['reason'] or '—'} |")
    w("")
    md = "\n".join(out)
    return md, len(changeset["operations"])


def main(pkg: Path, static: Path, dest: Path) -> None:
    md, ops = render(pkg, static)
    dest.write_text(md, encoding="utf-8")
    h = hashlib.sha256(md.encode("utf-8")).hexdigest()
    print("change operations:", ops, "| document bytes:", len(md.encode()), "| sha256:", h)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
