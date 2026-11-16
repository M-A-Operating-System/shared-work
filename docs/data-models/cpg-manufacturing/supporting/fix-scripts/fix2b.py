"""Stage 2b — view names, scope evidence, retired domain."""
from __future__ import annotations
from common import by_id, load, save

verbs = load("verbs"); V = by_id(verbs)
# One Traced Batch role is played by every batch end, so the derived view names collide; each is named for what it says.
for rid, name in (("REL029", "EventBatchesConsumed"), ("REL030", "EventBatchesProduced"), ("REL032", "EventBatchesFoundAgainst"),
                  ("REL033", "EventBatchesComplainedOf"), ("REL038", "EventBatchesExposed")):
    V[rid]["name_override"] = name
save("verbs", verbs)

sources = load("sources"); S = by_id(sources)
for sid, scope in (("SRC030", "SCI010"), ("SRC031", "SCI010"), ("SRC041", "SCI011"), ("SRC042", "SCI011")):
    if scope not in S[sid]["scope_ids"]:
        S[sid]["scope_ids"].append(scope)
save("sources", sources)

doms = load("domains")
doms["domains"] = [d for d in doms["domains"] if d["id"] != "DOM008"]
save("domains", doms)
print("ok")
