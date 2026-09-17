# Event contract and integration

Version 1.0 requires event identity, household identity, an aware ISO 8601 timestamp, source identity/category, an explicit boolean simulation flag, an event kind and a bounded observation. Unknown properties are rejected. Identifiers are ASCII tokens; observations may contain Unicode. Timestamps normalize to UTC.

All adapters currently accept the documented canonical envelope. Sensor and camera adapters additionally constrain its category/kind. They do not parse vendor payloads or authenticate callers. The camera adapter accepts only synthetic context.

The schema command exports JSON Schema from the same Pydantic model used by validation. CI publishes the export alongside the wheel and source archive. Runtime validation additionally enforces nonblank observations and UTC normalization; JSON Schema alone does not reproduce every Python validator.

## Safe ingestion

Authenticate the producer before normalization. Enforce HTTP/body limits upstream. The simulation flag is a producer assertion, not cryptographic proof. Avoid putting personal data or credentials in observations. Validation errors omit input values; valid observations are preserved, not automatically redacted.

Store the idempotency key using an atomic conditional write in your durable store. Compare the payload digest when a key already exists: equal means duplicate, different means identity conflict. Keys include household, source and event IDs. IncidentBridge supplies helpers, not persistence, retry scheduling or exactly-once delivery.

Safety metadata labels all events unverified and never authorizes device actions. A downstream policy must evaluate freshness, evidence, household permissions and any required confirmation. Camera motion is not proof of occupancy.

## EventBridge / Aenea example

See `examples/eventbridge_entry.py`. It creates a PutEvents entry without importing an AWS SDK. The integration owns authentication, bus selection, payload limits, deduplication and delivery retries, including individual failed entries returned by PutEvents.

Aenea will pin the tested release when its ingress is implemented in Phase 3. No live Aenea runtime integration is claimed by this package release.

## CLI semantics

`validate` checks one JSON event. `emit` writes one normalized JSON event to stdout. `replay` reads JSONL, validates the entire file, then writes normalized events in input order. Replay preserves event IDs and timestamps and does not remove duplicates. Empty or blank-line input is rejected. CLI tools do not send HTTP requests or control devices.

Replay loads the file into memory; use bounded synthetic fixture files. This interface is intended for developer fixtures, not unbounded production streams.
