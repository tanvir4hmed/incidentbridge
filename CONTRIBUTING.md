# Contributing

Contributions should preserve deterministic behavior, provenance, and backward compatibility.

1. Add tests for every adapter and schema behavior change.
2. Run formatting, lint, type checks, and the full test suite.
3. Use synthetic, redacted fixtures only.
4. Document new dependencies and external formats.
5. Do not couple the core package to Aenea or an AWS account.

By contributing, you agree that your contribution is licensed under Apache-2.0.

## Reproducible check setup

Create a virtual environment (Python 3.11–3.13), then run from the repository root:

```sh
python -m pip install -r requirements-dev.txt -e ".[dev]"
python -m ruff check src tests examples
python -m ruff format --check src tests examples
python -m mypy src
python -m pytest -q
python -m build
```

Direct check-tool versions are pinned; this is not a full transitive/runtime lock. CI also installs the wheel in a clean environment, runs validate/emit/replay and compares the generated schema with the committed schema. Keep that packaging check: tests against an editable source tree alone do not validate a release artifact.

Keep adapters independent from AWS and Aenea. Schema changes require version/compatibility tests; action authorization must never be inferred from observations. The current contract has no device-state lifecycle or automatic incident routing. These must be designed explicitly rather than added as undocumented fields.
