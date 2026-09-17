# IncidentBridge

IncidentBridge is a reusable Python toolkit for converting heterogeneous incident signals into a canonical, provenance-aware event model with validation and safety metadata.

## Status

Phase 1 implementation: Pydantic event contract, generic webhook/sensor/synthetic-camera adapters, idempotency keys, payload conflict digests, conservative safety metadata, and offline JSON/JSONL tools. Releases are tagged after GitHub Actions verifies tests and a clean wheel installation.

## Design goals

- deterministic normalization
- explicit source and simulation provenance
- strict schema validation
- validation errors that omit raw input values
- adapter isolation
- useful independently of Aenea

## Install and use

Requires Python 3.11+. From a checkout:

```sh
python -m pip install .
incidentbridge validate fixtures/smoke.json --adapter sensor
incidentbridge emit fixtures/camera.json --adapter camera-simulator
incidentbridge replay fixtures/scenario.jsonl
incidentbridge schema
```

Emit/replay write normalized events to stdout. They do not contact devices or services. No PyPI publication is claimed.

```python
import json
from pathlib import Path
from incidentbridge import normalize_event, idempotency_key, safety_metadata

event = normalize_event(json.loads(Path("fixtures/smoke.json").read_text()), "sensor")
print(idempotency_key(event))
print(safety_metadata(event).model_dump())
```

All adapters accept the documented canonical envelope; none claim Ring API compatibility. Camera simulation rejects non-synthetic events. Source provenance is a producer assertion: callers must authenticate inputs. No event authorizes an action or verifies occupancy.

## Verification

GitHub Actions runs Ruff, strict mypy, pytest, distribution builds and fresh-environment wheel/CLI checks on Python 3.11, 3.12 and 3.13. It exports JSON Schema and distributions as artifacts. Documentation-only pushes do not build the package.

Contributor reproduction commands:

```sh
python -m pip install -e ".[dev]"
ruff check src tests examples
mypy src
pytest -q
python -m build
```

See the [contract and integration guide](docs/contract.md) and [EventBridge entry example](examples/eventbridge_entry.py). The example constructs an entry without AWS credentials; the consumer owns delivery and durable deduplication. Live Aenea consumption starts in its ingress phase.

IncidentBridge remains deliberately small. Aenea may consume it at runtime, but the package will not depend on Aenea, AWS or a specific device vendor. Open Source mini submission work proceeds only while it does not delay the Alexa+ primary project.

## Project records

- [Project timeline](docs/project-timeline.md)
- [Build evidence](docs/build-evidence.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## License

Apache License 2.0. See `LICENSE`.
