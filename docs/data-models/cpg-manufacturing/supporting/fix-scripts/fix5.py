"""Stage 5 — wording the document must not carry."""
from __future__ import annotations
from common import by_id, load, save

scope = load("scope")
for a in scope["assumptions"]:
    if a["id"] == "SCA006":
        a["statement"] = ("Food traceability duties differ by market. The United States, the United Kingdom and the European Union are the sample markets, "
                          "and other markets come in as further requirements, not as a different design.")
save("scope", scope)

drqs = load("data-requirements"); D = by_id(drqs)
D["DRQ027"]["must_record"] = ["Each hold, the decision taken, the reason, and who decided it"]
D["DRQ027"]["must_prevent"] = ["A decision with no named decider"]
save("data-requirements", drqs)

doms = load("domains")
for d in doms["domains"]:
    if d["id"] == "DOM009":
        for t in d["domain_tests"].values():
            t["answer"] = t["answer"].replace("approval,", "authorisation,")
for c in doms["rejected_candidates"]:
    c["reason"] = c["reason"].replace("the relationship that approves it to supply", "the relationship that allows it to supply")
save("domains", doms)
