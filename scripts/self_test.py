#!/usr/bin/env python3
"""Falsifiable self-test for sweep_gate.

FAILS if the gate would license a 'refuted' verdict from a partial sweep. Also
proves a full sweep is allowed to refute, found-evidence blocks refutation, and
the bundled default map names first-class stores a familiar-tools-only sweep is
likely to skip.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep_gate as G  # noqa: E402

STORES = ["relational_db", "graph_db", "semantic_index", "filesystem", "event_ledger", "code_index"]


def main():
    # 1. THE authoring failure: only relational_db + filesystem checked, proposed 'refuted'.
    partial = G.gate({
        "store_map": STORES,
        "checked": [{"store": "relational_db", "found": False},
                    {"store": "filesystem", "found": False}],
        "proposed_verdict": "refuted",
    })
    assert partial["licensed"] is False, "partial sweep wrongly licensed a verdict"
    assert partial["licensed_verdict"] == "scoped_negative", "partial 'refuted' not downgraded"
    assert set(partial["unchecked"]) == {"graph_db", "semantic_index", "event_ledger", "code_index"}, \
        "unchecked first-class stores not surfaced"

    # 2. exhaustive sweep, evidence absent everywhere -> 'refuted' is licensed
    full = G.gate({
        "store_map": STORES,
        "checked": [{"store": s, "found": False} for s in STORES],
        "proposed_verdict": "refuted",
    })
    assert full["licensed"] is True and full["licensed_verdict"] == "refuted", \
        "exhaustive absence not allowed to refute"

    # 3. exhaustive sweep but graph_db FOUND it -> refutation is contradicted
    contra = G.gate({
        "store_map": STORES,
        "checked": [{"store": s, "found": (s == "graph_db")} for s in STORES],
        "proposed_verdict": "refuted",
    })
    assert contra["licensed"] is False and contra["licensed_verdict"] == "contradicted", \
        "refutation not blocked when evidence was found"

    # 4. empty store_map is an error
    try:
        G.gate({"store_map": [], "checked": [], "proposed_verdict": "refuted"})
        raise AssertionError("empty store_map should have raised")
    except ValueError:
        pass

    # 5. the default map names first-class stores that get skipped
    assert "graph_db" in G.DEFAULT_STORES and "semantic_index" in G.DEFAULT_STORES, \
        "default store map is missing graph/semantic stores"

    print("sweep_gate self-test: PASS (a partial sweep cannot license a verdict; skipped stores are surfaced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
