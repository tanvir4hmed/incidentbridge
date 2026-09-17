"""Adapters for our documented formats, not any vendor's private API."""

from typing import Protocol

from .models import IncidentEvent
from .validate import InvalidEvent, validate_event


class Adapter(Protocol):
    def normalize(self, payload: object) -> IncidentEvent: ...


class WebhookAdapter:
    """Canonical JSON object adapter; callers authenticate webhooks upstream."""

    def normalize(self, payload: object) -> IncidentEvent:
        return validate_event(payload)


class SensorAdapter:
    """Canonical sensor observations, including explicitly marked simulations."""

    kinds = frozenset({"smoke", "carbon_monoxide", "water_leak", "medical_sos"})

    def normalize(self, payload: object) -> IncidentEvent:
        event = validate_event(payload)
        if event.source.category != "sensor" or event.kind not in self.kinds:
            raise InvalidEvent("sensor adapter requires a supported sensor event")
        return event


class CameraSimulatorAdapter:
    """Synthetic camera context only; motion never proves occupancy."""

    kinds = frozenset({"motion", "doorbell", "package", "vehicle"})

    def normalize(self, payload: object) -> IncidentEvent:
        event = validate_event(payload)
        if (
            event.source.category != "camera"
            or not event.source.simulated
            or event.kind not in self.kinds
        ):
            raise InvalidEvent("camera simulator requires a supported synthetic camera event")
        return event
