# CPG Manufacturer — Pass 1 under v28

**Run:** Business Domain Discovery Agent v28, single-document specification
**Date:** 20 September 2026
**Mode:** research-only

---

## Step 1 — Scope established

Confirmed before research, per the specification. `scope.json` written.

| | |
|---|---|
| Domain | CPG manufacturing operations |
| Subgroups | **All five equally** — food and beverage, household, personal care and cosmetics, pet care, beauty |
| Production | **Own plants and external partners** |
| Serialisation | **Not yet known** |
| In scope | 9 functions |
| Out of scope | 6 areas, each with its owning model |
| Mode | Research-only — no certifier available |

**Three unanswered questions recorded** rather than assumed. An unanswered scoping question is a finding and renders in the document.

---

## Step 2 — Sources

**37 sources: 27 carried forward, 10 added** to cover the widened scope.

| Area | Sources | Status |
|---|---|---|
| Manufacturing execution and genealogy | 6 | Carried forward |
| ISA-95 and ISA-88 | 7 | Carried forward |
| Quality and corrective action | 9 | Carried forward |
| Maintenance and reliability | 5 | Carried forward |
| **Personal care and cosmetics** | **4** | **New** |
| **External manufacturing** | **6** | **New** |
| Household and cleaning products | **0** | **Gap** |
| Pet care | **0** | **Gap** |

**Two subgroups have no source.** Requirements covering them rest on the assumption that they behave like food and beverage — which is precisely what the previous DEC011 flagged and the scope answer widened. The gap is now explicit rather than asserted, and it returns the next pass to step 2.

---

## Steps 3 to 7 — Material changes

### The three scope answers each changed the model

**Widening to all CPG subgroups** invalidates the **F&B** marking on nine requirements and six rules. Food-specific framing must generalise or split per subgroup:

| Was | Becomes |
|---|---|
| Allergen declaration | **Hazard declaration** — allergen in food, irritant or sensitiser in cosmetics, GHS classification in household chemicals |
| Food safety classification of equipment | **Consequence classification** — safety, regulatory or quality, by subgroup regime |
| 24-hour recall production | **Regulatory production window**, which differs by subgroup and jurisdiction |
| HACCP-critical | **Critical control point**, the generic form |

ISO 22716 (SRC028–SRC031) confirms the structures hold across subgroups: personnel, premises, equipment, materials, production, laboratory control, batch records. **The structure generalises; the vocabulary does not.**

### External manufacturing adds a domain-level question

Ten new requirements, and one that is structural rather than additive:

| ID | Requirement |
|---|---|
| REQ072 | Production may happen at a facility the organisation does not own, and the record of it is held by another party |
| REQ073 | Material may be owned by the organisation while held by another party, or bought back as finished output |
| REQ074 | What a partner must supply about a run, and when, is agreed in advance |
| REQ075 | A partner is assessed on delivery, quality, waste, changeover and cost against what was quoted |
| REQ076 | The organisation's own forecast accuracy affects the partner's ability to plan, and is part of the same assessment |
| REQ077 | A partner may make the product, pack it, or both, and these are different arrangements |
| REQ078 | Formulations and specifications supplied to a partner are proprietary and their use is governed |
| REQ079 | Output from a partner arrives with a declaration, and the organisation may or may not verify it |
| REQ080 | Material held at a partner is counted separately from material at the organisation's own places |
| REQ081 | A product may pass through more than one partner before it is finished |

**The structural consequence:** `EventProductionRuns` presumes the organisation observes the run. Where a partner does, the organisation holds what the partner reported, not what happened. **That is a mastery question, not a new concept** — the same subject, `ingested` rather than `mastered`, with the reporting party recorded.

**REQ073 is unresolved and is UNQ002.** Tolling and turnkey produce different transaction structures, and the scope answer does not settle which applies.

### Serialisation unknown is a constraint, not a gap

The model must accommodate both without assuming either. Two rules follow:

- **No rule may require an instance to exist.** A purely lot-tracked portfolio must be fully expressible.
- **No rule may assume a lot is the finest grain.** A serialised portfolio must be expressible without restructuring.

The Instances domain stays, carrying physical assets regardless, and carries product instances where they exist. **UNQ001 remains open and is a scope-level unknown rather than a modelling decision.**

---

## Step 8 — Convergence

**Pass 1 is not stable.** Material changes:

| | Count |
|---|---|
| Requirements added | 10 |
| Requirements requiring generalisation | 9 |
| Rules requiring generalisation | 6 |
| Subjects added | 0 |
| Domains added or reassigned | 0 |
| Verbs added | 2 — partner reporting, partner assessment |
| Mastery reclassifications | 1 — production runs may be ingested |

**No domain changed**, which is the substantive finding. Widening from one subgroup to five and adding external manufacturing produced requirements, rules and two verbs — and no new subject and no new domain. The nine-domain structure absorbed both.

### Returns to earlier steps

| Finding | Returns to |
|---|---|
| Household and pet care have no source | **Step 2** |
| Tolling versus turnkey unresolved | **Step 1** — it is a scope question, not a modelling one |
| Nine requirements carry subgroup-specific vocabulary | **Step 3** |
| Production run mastery varies by producing party | **Step 5** |

### Scenarios

Two new scenarios fail, both on external manufacturing:

| | Scenario | Why it fails |
|---|---|---|
| SCN043 | A partner reports a run three days after it happened, and the report disagrees with the material it consumed | Nothing distinguishes what was observed from what was reported, so reconciliation has no anchor |
| SCN044 | A product is made by one partner and packed by another | Nothing chains partners. The composition graph holds it, but no relationship records that two parties each performed part of one production |

Both are additive rather than structural — they need relationships, not domains.

---

## Pass 2 target

1. **Source household, pet care and chemical-product manufacturing.** Two subgroups asserted and unevidenced.
2. **Settle tolling versus turnkey** — a scope answer, not a design decision.
3. **Generalise the nine subgroup-specific requirements** and six rules to a hazard-and-consequence vocabulary that holds across all five.
4. **Add the partner reporting and partner assessment verbs**, and the relationship chaining partners across one production.
5. **Re-run all 44 scenarios.**

**Convergence is not close.** One stable pass has not occurred, and two of five subgroups have no evidential basis.
