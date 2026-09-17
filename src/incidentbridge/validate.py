"""Validation errors expose locations/codes, never raw household payloads."""

from pydantic import ValidationError

from .models import IncidentEvent


class InvalidEvent(ValueError):
    """A payload does not satisfy the public event contract."""


def validate_event(payload: object) -> IncidentEvent:
    try:
        return IncidentEvent.model_validate(payload)
    except ValidationError as exc:
        problems = [
            f"{'.'.join(map(str, error['loc'])) or 'event'}: {error['type']}"
            for error in exc.errors(include_input=False, include_url=False)
        ]
        raise InvalidEvent("; ".join(problems)) from None
