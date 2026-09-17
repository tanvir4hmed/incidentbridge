"""Context hints for downstream policy, never authorization decisions."""

from typing import Literal

from .models import Contract, IncidentEvent


class SafetyMetadata(Contract):
    simulated: bool
    evidence_type: Literal["unverified_observation"] = "unverified_observation"
    authorizes_action: Literal[False] = False
    occupancy_verified: Literal[False] = False


def safety_metadata(event: IncidentEvent) -> SafetyMetadata:
    return SafetyMetadata(simulated=event.source.simulated)
