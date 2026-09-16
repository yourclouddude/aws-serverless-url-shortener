## What changed?

Describe the problem this PR solves and the approach you took.

## Why this approach?

Explain any architecture, IAM, API, DynamoDB, or failure-handling trade-offs introduced by the change.

## Validation

- [ ] `python -m ruff check src tests`
- [ ] `python -m pytest -q`
- [ ] `sam validate --lint`
- [ ] `sam build`
- [ ] No credentials, secrets, or generated deployment artifacts were committed

## Risk / rollback

Describe what could break, any AWS resources affected, and how the change can be reverted or cleaned up.

## Documentation

- [ ] README/docs updated when behavior or architecture changed
- [ ] No documentation change needed
