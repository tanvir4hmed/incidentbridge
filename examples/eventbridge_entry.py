"""Build an EventBridge entry without AWS credentials or an AWS dependency."""

import json

from incidentbridge import idempotency_key, normalize_event


def eventbridge_entry(payload: object, bus_name: str) -> dict[str, str]:
    event = normalize_event(payload)
    return {
        "EventBusName": bus_name,
        "Source": "aenea.incidentbridge",
        "DetailType": "IncidentEvent",
        "Detail": json.dumps({
            "event": event.model_dump(mode="json"),
            "idempotency_key": idempotency_key(event),
        }),
    }
