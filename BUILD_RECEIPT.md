# BUILD_RECEIPT - full-store-sweep

Harness extracted under the create-harness discipline: keep judgment in prose,
but make the coverage rule executable.

## What was mechanized (kept judgment in prose; extracted the coverage rule)
- `scripts/sweep_gate.py` — given a JSON sweep-ledger (`store_map`, `checked`, `proposed_verdict`)
  it returns the *licensed* verdict: a "refuted"/"confirmed" verdict is downgraded to a
  `scoped_negative` (naming the unchecked stores) unless the sweep was exhaustive, and "refuted"
  is `contradicted` when a checked store reported `found:true`. Bundles a generic default store
  map for common systems, while allowing every run to pass its own explicit `store_map`. Exits
  nonzero when the verdict is not licensed, so it can gate a pipeline.

## Falsifiable receipt (`metadata.self_test`)
- `scripts/self_test.py` — encodes the authoring failure: a 2-of-6 sweep proposing "refuted" MUST
  be downgraded and MUST surface unchecked first-class stores; a full sweep may refute;
  found-evidence blocks refutation; an empty `store_map` errors.

## Measured this session
- `self_test.py`: **PASS** (exit 0).
- The self-test **caught a real bug during build**: `store_map = ledger.get("store_map") or
  DEFAULT` silently substituted the default map for an explicitly-empty map. Fixed to distinguish
  *omitted* (→ default) from *empty* (→ error). The test earned its keep before it was even packaged.
- Falsifiability proof: `sweep_gate.gate` patched to license everything → `self_test.py` **FAILS**
  ("partial sweep wrongly licensed a verdict").

## Not measured (honest gaps)
- The gate enforces coverage; it cannot judge whether a store was queried *correctly*. That
  remains prose judgment — the harness gates completeness, not query quality.
