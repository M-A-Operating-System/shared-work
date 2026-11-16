# CPG Manufacturer — Pass 2 delta

## UNQ002 resolved — turnkey

**Material at an upstream supplier or external manufacturer is theirs.** Title transfers to the organisation on receipt. The organisation holds no inventory at a party it does not operate.

| Removed | Because |
|---|---|
| REQ073 *material may be owned by the organisation while held by another party* | Withdrawn. There is no such state |
| REQ080 *material held at a partner is counted separately* | Withdrawn. It is not counted at all until received |
| A partner as an inventory location | Not a location this organisation holds stock at |

**One requirement replaces three.**

> **REQ073** — What the organisation buys becomes its own on receipt, and what a supplier holds before that is the supplier's.

---

## The finding this exposes

**A purchased input may be another organisation's finished consumer product.**

A branded ingredient, a bottle, a closure, a filled sachet inside a gift set, a component of a multipack. To the supplier it is saleable output with its own composition, specification, lots and declarations. **To this organisation it is an ingredient or a part.**

### Kind is a perspective, not a property

`ProductKindType` describes what a product is **to this organisation**. The same physical thing is the supplier's `CONSUMERUNIT` and this organisation's `RAWMATERIAL`, and both are correct.

**A product may hold more than one kind here simultaneously** — bought as an input and also sold on, which is ordinary in gift sets, multipacks and bulk resale. Kind is therefore not exclusive, and it is derivable as well as declared:

| Appears as | Implies |
|---|---|
| A child in a composition record | Input |
| A line on an outbound transaction | Saleable |

### The composition graph terminates at every purchase

This is the structural consequence, and it changes a rule.

**RUL010 said derived properties are computed from inputs and never asserted.** That holds inside the organisation's own composition. It cannot hold at a purchased boundary, because what is beneath is not known here.

> **RUL010 (revised)** — Hazards, certifications, origin and shelf-life constraint are computed from inputs within the organisation's own composition. At a purchased input the graph terminates, and those properties are **supplier-declared**. A declared property is recorded with the party that declared it, the document declaring it, and whether the organisation verified it.

**This is what a certificate of analysis is for.** It is the mechanism by which properties cross a boundary the composition graph cannot.

### New requirements

| ID | Requirement |
|---|---|
| REQ082 | Something bought as an input may be a finished product to whoever supplied it, and what it is made from may not be known here |
| REQ083 | Where what an input contains is not known, what it must be declared to contain is stated by the supplier and relied upon |
| REQ084 | The same thing may be bought as an input and also sold on unchanged |
| REQ085 | How far back something can be traced depends on the supplier's own records once it leaves this organisation's sight |

### New rules

| ID | Rule |
|---|---|
| RUL062 | A product's kind is its role to this organisation, not a property of the thing. A product may hold several kinds at once |
| RUL063 | Composition below a purchased input is not modelled. The graph terminates and the terminus is marked as purchased |
| RUL064 | A supplier-declared property carries the declaring party, the declaring document, and whether it was verified. It is never reported as a computed property or as a test result |
| RUL065 | Recall scope below a purchased input is the supplier's to produce. The model records the request and the response, not the lineage |

### New derived roles

| ID | Role | Derived from |
|---|---|---|
| ROL025 | Terminal input | A product with no composition records of its own that is purchased rather than made |
| ROL026 | Resold product | A product appearing both as a composition child and on an outbound transaction line |
| ROL027 | Declared-property product | Holds at least one property asserted by a supplier rather than computed |

---

## What this changes about risk

**Two of the model's strongest claims now have a stated limit.**

*Hazards propagate from what went in* — **within this organisation's composition.** A nut allergen introduced inside a purchased compound ingredient is known only because the supplier declared it.

*Recall scope is a query over lineage* — **down to the purchase boundary.** Below it, scope is a request to a supplier and a wait.

**Neither is a defect.** Both are the truth of buying rather than making, and stating them is better than a model that implies it can see further than it can. It also explains why supplier assessment carries the weight it does: **where the graph stops, the assessment is what stands in for it.**

---

## Pass 2 status

| | |
|---|---|
| Requirements added | 4 |
| Requirements withdrawn | 2 |
| Rules added | 4 |
| Rules revised | 1 — RUL010, the propagation rule |
| Roles added | 3 |
| Subjects added | 0 |
| Domains changed | 0 |

**Still not stable**, and one open question remains at step 1 — UNQ001, serialisation.

The household and pet care source gap from pass 1 is unaddressed and still returns the next pass to step 2.
