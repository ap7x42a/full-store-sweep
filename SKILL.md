---
name: full-store-sweep
description: Use before confirming OR refuting any claim about system state ("is X in the data?", "did this stop?", "are those still there?"). Enumerate every store the evidence could live in and query each; a partial sweep can only report "absent from what I checked," never "refuted" — and the store you skip is usually the first-class one you don't know how to open.
metadata:
  self_test: "python3 scripts/self_test.py"
---

# Full Store Sweep

**a partial sweep is not a verdict**

## The one rule

To rule a state-claim **true or false**, you must query **every store the evidence could live in**. Checking the stores you already know how to query and finding nothing licenses exactly one sentence — *"absent from {the stores I checked}"* — which is a **scoped negative, not a refutation**. Refutation requires exhaustion. The store you leave unopened is not neutral; it is where the answer usually is, precisely because you skipped it.

> "Not in the drawer I opened" is not "not in the house."

## The failure that authored this

A state audit checked only the familiar stores: one relational table and a few
filesystem directories. Finding nothing there, it declared the claim refuted.
The skipped stores were first-class evidence stores: a graph database and a
separate symbolic/semantic index. When those were finally opened, they contained
the evidence. The failure was not a bad query; it was calling a partial sweep a
verdict.

## The store map — write it before you rule

Enumerate, explicitly, every place this system's state can live. For a typical
software system that may include: relational databases, vector stores, graph
databases, search indexes, object/blob storage, filesystem exports, append-only
JSONL/event ledgers, telemetry systems, queues, caches, and code-index tools. A
claim of the form "the data isn't here" is only meaningful once it names which
stores were queried and which were not.

## The procedure

1. **Enumerate first.** List every store/surface the fact could inhabit *before* the first query, so a store cannot be dropped by omission.
2. **The unfamiliar store is the one that holds the answer.** If you don't know its query API, that is a reason to *learn it* (`listMethods`, `describeMethod`, the schema resource), never a reason to skip it. Silent skipping is the failure; an explicit "unchecked, API unknown" is at least honest.
3. **Query each; record checked/unchecked with the result.** Keep a small ledger: store → queried? → found?
4. **Gate the verdict on exhaustion.** "Refuted" / "confirmed" is licensed only when every plausible store was queried. Short of that, report the scoped negative and name the unchecked stores as unchecked.
5. **Never launder agreement as evidence.** Restating the claimant's narrative back to them is not verification — it is affirmation wearing a lab coat. And refuting their *specifics* from a partial sweep is worse than saying nothing: it spends your credibility on a claim you never earned.

## Naive baseline that fails

Query the store you already know (`psql`, `find`, a dashboard), find nothing,
declare the claim false. The first-class store you never opened refutes *you*
when someone finally checks it.

## Red flags — stop and open the other store

| Rationalization | Reality |
|---|---|
| "It's not in the database or on disk, so it's not there." | Name every other first-class store. Did you query them? If not, you have a scoped negative, not a refutation. |
| "I don't know how to query that store." | Then learn its API (`listMethods`/`describeMethod`/schema). Unfamiliarity is not absence. |
| "The claimant's theory is invalidated." | By which sweep? List the stores you actually checked. If the list is partial, you invalidated nothing. |
| "I'll confirm their point and move on." | Agreement is not verification. Query the claim; don't echo it. |
| "Two stores agree it's absent — good enough." | Two of how many? Absence is a verdict only when the sweep is exhaustive. |

## Done means

- Every store the claim could live in was enumerated *before* querying.
- Each store was queried or explicitly marked unchecked (with why) — including the unfamiliar first-class ones.
- Any verdict of "confirmed"/"refuted" rests on an exhaustive sweep; anything less is reported as a scoped negative.
- No claimant's narrative was restated as if repetition were evidence.

## Harness

The coverage rule is deterministic — a gate you can run, not just a maxim:

- `scripts/sweep_gate.py` — takes a JSON sweep-ledger (`store_map`, `checked` as `[{store, found}]`, `proposed_verdict`) and returns the *licensed* verdict. A "refuted"/"confirmed" verdict is downgraded to a `scoped_negative` that names the unchecked stores unless the sweep was exhaustive; "refuted" is `contradicted` if any checked store reported `found:true`. It exits nonzero when the proposed verdict is not licensed, so it can gate a pipeline. Omit `store_map` to use the bundled generic map: relational database, vector store, graph database, search index, filesystem corpus, event ledger, object storage, cache, queue, and code index.
- `scripts/self_test.py` (declared in `metadata.self_test`) encodes the authoring failure as a test: a 2-of-6 sweep proposing "refuted" MUST be downgraded and MUST surface the unchecked graph and semantic stores; a full sweep may refute; found-evidence blocks refutation. It fails if the gate ever licenses a partial-sweep verdict.

Run it: `python3 scripts/self_test.py`.

## Scope

Sibling to **the-monkey-paw** (distrust the inherited artifact) and **evaluate-by-experiment** (build a check that can fail): this one governs **coverage** - the completeness of the evidence sweep before a verdict. Higher-priority safety and operator instructions win.
