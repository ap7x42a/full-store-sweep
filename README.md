# Full Store Sweep

Reusable Agent Skill for state-claim verification across multiple stores.

The rule: a partial sweep is not a verdict. If a fact could live in multiple
stores, enumerate them before querying and report unchecked stores explicitly.

## Verify

```bash
python3 scripts/self_test.py
sha256sum -c SHA256SUMS.txt
```
