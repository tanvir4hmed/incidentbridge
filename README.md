# IncidentBridge

Vendor-neutral incident event validation and normalization for Python.

IncidentBridge converts a documented event envelope into a strict, provenance-aware model. It supplies schema validation, deterministic normalization, retry identities, payload digests and conservative safety metadata. It is usable independently of Aenea, AWS or a device vendor.

## Install

Requires Python 3.11 or later. From a checkout:

```sh
python -m pip install .
```

The source repository is the installation source; no PyPI publication is claimed.

## Use

```sh
incidentbridge validate fixtures/smoke.json --adapter sensor
incidentbridge emit fixtures/camera.json --adapter camera-simulator
incidentbridge replay fixtures/scenario.jsonl
incidentbridge schema
```

Validate checks one JSON event; emit writes a normalized event to stdout; replay validates JSONL and emits events in input order; schema exports the Pydantic-derived JSON Schema. The commands do not contact devices, publish cloud events or control outputs.

```python
import json
from pathlib import Path
from incidentbridge import normalize_event, idempotency_key, payload_digest, safety_metadata

event = normalize_event(
    json.loads(Path("fixtures/smoke.json").read_text()),
    "sensor",
)
print(idempotency_key(event))
print(payload_digest(event))
print(safety_metadata(event).model_dump())
```

## Contract and integrations

The version 1.0 contract carries event/household/source identity, timezone-aware time, source category, simulation provenance, signal kind and observation. It includes household safety/security signals such as smoke, CO, heat, gas, water leak, contacts, forced entry, glass break and tamper. Unknown fields are rejected.

Adapters accept the canonical envelope and constrain supported categories/kinds; they do not parse arbitrary vendor payloads or authenticate callers. The synthetic-camera adapter rejects non-simulated context. A consumer must authenticate sources and persist idempotency/conflict checks atomically.

[Aenea](https://github.com/tanvir4hmed/aenea) imports and calls this toolkit during ingestion. Its separate envelope adds trusted catalog/location context and device state without changing the embedded IncidentBridge contract. Aenea owns incident routing, schedules, storage, assessment and access control.

The [EventBridge entry example](examples/eventbridge_entry.py) constructs a payload without an AWS SDK. Your integration owns publication and recovery.

## Cost and boundaries

The library and CLI run locally and do not create cloud resources or paid service calls. Your machine's compute/storage and any downstream infrastructure remain your responsibility. Aenea's cloud estimate belongs to its [Operations guide](https://github.com/tanvir4hmed/aenea/blob/main/docs/operations.md#cost-estimate), not to the toolkit's runtime.

Source provenance is an assertion, not authentication or proof of real conditions. Safety metadata never authorizes actions or verifies occupancy. See the [contract guide](docs/contract.md) for state, retries, adapters and CLI limits.

## Development

GitHub Actions checks Python 3.11, 3.12 and 3.13, builds distributions, installs a clean wheel and compares its schema/CLI output. Documentation-only changes do not run package builds. Reproduce checks with [CONTRIBUTING](CONTRIBUTING.md).

## License and security

[Apache License 2.0](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Security policy](SECURITY.md)
