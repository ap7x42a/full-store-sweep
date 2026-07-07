# Full Store Sweep

Full Store Sweep is an agent skill for verifying system-state claims across
multiple evidence stores. Its rule is simple:

```text
A partial sweep is not a verdict.
```

If a fact could live in several places, enumerate those places before querying.
A missed store means the strongest honest answer is "absent from what I
checked," not "refuted."

## Use It When

- Someone asks whether data, events, files, jobs, records, or failures exist.
- A claim could be true in a database, index, graph, event stream, cache, object
  store, filesystem export, queue, or external service.
- Familiar tooling finds nothing and the agent is tempted to declare absence.
- A dashboard, report, or summary might only reflect one backing store.
- The proof depends on checked versus unchecked coverage.

## What The Package Includes

- `SKILL.md` - the sweep doctrine and verdict rules.
- `scripts/sweep_gate.py` - a deterministic gate that reads a JSON sweep ledger
  and decides whether the proposed verdict is licensed.
- `scripts/self_test.py` - hostile tests proving partial sweeps cannot license
  "confirmed" or "refuted" verdicts and that found evidence blocks refutation.
- `agents/openai.yaml` - skill metadata for runtimes that display skill cards.
- `SHA256SUMS.txt` - drift manifest.

## Sweep Ledger Shape

`scripts/sweep_gate.py` accepts JSON like:

```json
{
  "store_map": ["relational_db", "graph_db", "filesystem", "event_ledger"],
  "checked": [
    {"store": "relational_db", "found": false},
    {"store": "filesystem", "found": false}
  ],
  "proposed_verdict": "refuted"
}
```

Because `graph_db` and `event_ledger` were not checked, the gate downgrades the
verdict to a scoped negative and exits nonzero.

Run it:

```bash
python3 scripts/sweep_gate.py sweep-ledger.json
```

Omit `store_map` to use the bundled generic map: relational database, vector
store, graph database, search index, filesystem corpus, event ledger, object
storage, cache, queue, and code index.

## Install As An Agent Skill

```bash
git clone https://github.com/ap7x42a/full-store-sweep.git
cp -a full-store-sweep ~/.codex/skills/full-store-sweep
```

For project-local skill surfaces, copy the directory into the location your
runtime uses, such as `.agents/skills/full-store-sweep`.

## Verify The Package

```bash
python3 scripts/self_test.py
sha256sum -c SHA256SUMS.txt
```

## Limits

This skill does not tell you how to query every possible backend. It forces the
coverage question into the open: which stores were enumerated, which were
checked, which were not, and what verdict that coverage actually licenses.
