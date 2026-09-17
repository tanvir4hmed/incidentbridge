"""Keys for caller-owned durable deduplication; no in-memory exactly-once claim."""

import hashlib
import json

from .models import IncidentEvent


def idempotency_key(event: IncidentEvent) -> str:
    identity = [event.household_id, event.source.source_id, event.event_id]
    return hashlib.sha256(json.dumps(identity, separators=(",", ":")).encode()).hexdigest()


def payload_digest(event: IncidentEvent) -> str:
    """Detect changed content under the same identity in the caller's store."""
    canonical = json.dumps(event.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
