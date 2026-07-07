#!/usr/bin/env python3
"""sweep_gate.py -- refuse a state-verdict that rests on a partial store sweep.

The deterministic core of the skill: a "refuted"/"confirmed" verdict is licensed
ONLY when every store in the canonical map was queried. A partial sweep is
downgraded to a scoped negative that names the unchecked stores; a "refuted"
verdict is rejected outright if any checked store reported the evidence FOUND.

Input (JSON, --input or stdin):
    {
      "store_map": ["relational_db","graph_db","semantic_index","filesystem","event_ledger","code_index"],
      "checked":   [{"store":"relational_db","found":false},
                    {"store":"filesystem","found":false}],
      "proposed_verdict": "refuted"
    }
Omit "store_map" to use the bundled generic map, which names several common
first-class stores that familiar-tools-only sweeps often skip.

Exit code 0 iff the proposed verdict is licensed, so this can gate a pipeline.
Stdlib only; mutates nothing.
"""
from __future__ import annotations

import argparse
import json
import sys

# A generic starting map. Real systems should pass their own explicit store_map.
DEFAULT_STORES = [
    "relational_db",
    "vector_store",
    "graph_db",
    "semantic_index",
    "filesystem_corpus",
    "event_ledger",
    "object_storage",
    "cache",
    "queue",
    "code_index",
]
VERDICTS = {"refuted", "confirmed", "scoped_negative", "inconclusive"}


def gate(ledger):
    # Omitted or null store_map -> the bundled generic map. An EXPLICITLY empty
    # store_map is a user error, never a silent fallback to a different map.
    if "store_map" not in ledger or ledger["store_map"] is None:
        store_map = DEFAULT_STORES
    else:
        store_map = ledger["store_map"]
    if not isinstance(store_map, list) or not store_map:
        raise ValueError("store_map must be a non-empty list of store names")
    store_map = [str(s) for s in store_map]

    proposed = str(ledger.get("proposed_verdict", "")).strip().lower()
    if proposed not in VERDICTS:
        raise ValueError(f"proposed_verdict must be one of {sorted(VERDICTS)}")

    checked = ledger.get("checked") or []
    checked_names, found_any, unknown = [], False, []
    for entry in checked:
        name = str(entry.get("store"))
        checked_names.append(name)
        if name not in store_map:
            unknown.append(name)
        if bool(entry.get("found")):
            found_any = True

    unchecked = [s for s in store_map if s not in checked_names]
    coverage = f"{len(store_map) - len(unchecked)}/{len(store_map)}"

    # Cannot 'refute' when a checked store actually FOUND the evidence.
    if proposed == "refuted" and found_any:
        return {
            "licensed_verdict": "contradicted",
            "licensed": False,
            "reason": "proposed 'refuted' but a checked store reported found=true",
            "coverage": coverage,
            "unchecked": unchecked,
            "unknown_stores": unknown,
        }

    # A hard verdict requires an exhaustive sweep.
    if proposed in {"refuted", "confirmed"} and unchecked:
        return {
            "licensed_verdict": "scoped_negative",
            "licensed": False,
            "reason": (f"partial sweep: {len(unchecked)} store(s) unchecked -- a partial sweep "
                       f"cannot license '{proposed}'; it can only say 'absent from what was checked'"),
            "coverage": coverage,
            "unchecked": unchecked,
            "unknown_stores": unknown,
        }

    licensed = not unknown  # a store outside the map taints even a 'complete' sweep
    return {
        "licensed_verdict": proposed,
        "licensed": licensed,
        "reason": "exhaustive sweep" if licensed else "a checked store is outside the store_map",
        "coverage": coverage,
        "unchecked": unchecked,
        "unknown_stores": unknown,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate a state-verdict on store-sweep completeness.")
    ap.add_argument("--input", "-i", help="JSON ledger file (default: stdin)")
    args = ap.parse_args(argv)

    raw = open(args.input).read() if args.input else sys.stdin.read()
    result = gate(json.loads(raw))
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result.get("licensed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
