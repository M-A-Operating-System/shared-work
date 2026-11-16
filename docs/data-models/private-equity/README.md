# Private Equity Data Model - Working Folder

Working folder for the Private Equity data model. The design document is the **target state**: the intended final design, which leads the Data Design Authority (DDA) rather than following it.

| File | Purpose |
|---|---|
| `private-equity-data-design-document.md` | Data Model Design Document (package PE-STRUCT-20261114-01, dated 2026-11-14) |
| `*.json` | Package definition files (domains, roles, relationships, concepts, attributes, lookups, requirements, sources, state and so on) |
| `dda-changeset.json` | The changes DDA needs to reach this target state, including retirements to confirm before applying |

## Target state compared with DDA (2026-11-14)

| Area | Target design | DDA today |
|---|---|---|
| Transaction parties | One role and one relationship (`LegalEntityTransactionParty`), with the side (paid or received), amount, purpose and units on each party | Relationship DMR000000037 exists, but its description says the amount belongs to the transaction (open decision DEC004) |
| Valuations | One `Valuation` concept with a measure list (net asset value, equity value, enterprise value), linked to the fund valued (`ValuationPrivateEquityFundValued`) and to the portfolio company valued (`ValuationPrivateEquityPortCoValued`) | Matches. DMR000000039 now links to the fund and DMR000000050 to the portfolio company; `LegalEntityValuations` (DMC000000112) and the general valued-entity role (DMO000000019) are still to be retired |
| Instrument traded | `TransactionInstrumentTraded` | Not yet created |
| Accounts | Not in this design; open question SCQ001 (needs an agreed requirement, owner and source) | The Private Equity model includes `AccountTransactionBooking` (DMR000000038) and `PrivateEquityFundAccountBeneficialOwnership` (DMR000000051) |

Open design decisions are in section 10 of the document (DEC001 to DEC005).

## Not yet refreshed

- `validation.json` is the report from the 2026-10-28 baseline and has not been re-run. It records one blocking defect (RN03, change vocabulary), which appears to come from the standard MAOS introduction text and needs confirming, and 22 advisory items.
- The generator scripts that produce these files are not in this folder.
