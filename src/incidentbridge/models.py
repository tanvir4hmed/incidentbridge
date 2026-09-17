"""Small, versioned event contract. Observations never authorize actions."""

from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictBool, field_validator

Identifier = Annotated[str, Field(strict=True, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
EventKind = Literal[
    "smoke", "carbon_monoxide", "water_leak", "medical_sos", "severe_weather",
    "motion", "doorbell", "package", "vehicle", "person_status", "device_status",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class Source(Contract):
    source_id: Identifier
    simulated: StrictBool
    category: Literal["sensor", "camera", "household", "device", "weather"]


class IncidentEvent(Contract):
    schema_version: Literal["1.0"] = "1.0"
    event_id: Identifier
    household_id: Identifier
    occurred_at: AwareDatetime
    source: Source
    kind: EventKind
    observation: Annotated[str, Field(strict=True, min_length=1, max_length=1000)]

    @field_validator("occurred_at", mode="before")
    @classmethod
    def reject_numeric_timestamp(cls, value: object) -> object:
        if not isinstance(value, (str, datetime)):
            raise ValueError("timestamp must be an ISO 8601 string or aware datetime")
        return value

    @field_validator("occurred_at")
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @field_validator("observation")
    @classmethod
    def nonblank_observation(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("observation must not be blank")
        return value
