"""Explicit adapter selection: unknown formats fail rather than being guessed."""

from typing import Literal

from .adapters import Adapter, CameraSimulatorAdapter, SensorAdapter, WebhookAdapter
from .models import IncidentEvent

AdapterName = Literal["webhook", "sensor", "camera-simulator"]


def normalize_event(payload: object, adapter: AdapterName = "webhook") -> IncidentEvent:
    adapters: dict[str, Adapter] = {
        "webhook": WebhookAdapter(),
        "sensor": SensorAdapter(),
        "camera-simulator": CameraSimulatorAdapter(),
    }
    if adapter not in adapters:
        raise ValueError("unknown adapter")
    return adapters[adapter].normalize(payload)
