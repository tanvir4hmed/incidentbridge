import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from incidentbridge import (
    IncidentEvent,
    InvalidEvent,
    idempotency_key,
    normalize_event,
    payload_digest,
    safety_metadata,
    validate_event,
)
from incidentbridge.cli import main

FIXTURES = Path(__file__).parents[1] / "fixtures"


def payload():
    return json.loads((FIXTURES / "smoke.json").read_text())


def test_roundtrip():
    event = validate_event(payload())
    assert IncidentEvent.model_validate_json(event.model_dump_json()) == event


@pytest.mark.parametrize("field", ["event_id", "household_id", "source", "occurred_at"])
def test_required_fields(field):
    data = payload()
    del data[field]
    with pytest.raises(InvalidEvent):
        validate_event(data)


@pytest.mark.parametrize("mutation", [
    {"event_id": 123},
    {"event_id": "bad/id"},
    {"occurred_at": "2026-09-17T00:00:00"},
    {"occurred_at": 1234},
    {"schema_version": "2.0"},
    {"kind": "unlock_door"},
    {"observation": " "},
    {"observation": "x" * 1001},
    {"secret": "unwanted"},
])
def test_rejects_invalid_contract(mutation):
    data = payload()
    data.update(mutation)
    with pytest.raises(InvalidEvent):
        validate_event(data)


@pytest.mark.parametrize("value", ["true", 1, None])
def test_simulation_flag_is_strict(value):
    data = payload()
    data["source"]["simulated"] = value
    with pytest.raises(InvalidEvent):
        validate_event(data)


def test_simulation_flag_required():
    data = payload()
    del data["source"]["simulated"]
    with pytest.raises(InvalidEvent):
        validate_event(data)


def test_nested_unknown_fields_rejected():
    data = payload()
    data["source"]["token"] = "private"
    with pytest.raises(InvalidEvent) as exc:
        validate_event(data)
    assert "private" not in str(exc.value)


def test_invalid_value_not_in_error():
    data = payload()
    data["kind"] = "PRIVATE-HOUSEHOLD-INFORMATION"
    with pytest.raises(InvalidEvent) as exc:
        validate_event(data)
    assert "PRIVATE" not in str(exc.value)


def test_timezone_normalized():
    data = payload()
    data["occurred_at"] = "2026-09-17T06:00:00+06:00"
    assert validate_event(data) == validate_event(payload())


def test_identity_scoped_to_household_and_source():
    original = validate_event(payload())
    for field in ("household_id", "event_id"):
        data = payload()
        data[field] += "-other"
        assert idempotency_key(validate_event(data)) != idempotency_key(original)
    data = payload()
    data["source"]["source_id"] += "-other"
    assert idempotency_key(validate_event(data)) != idempotency_key(original)


def test_changed_payload_has_same_key_but_different_digest():
    data = payload()
    original = validate_event(data)
    data["observation"] = "Changed observation"
    changed = validate_event(data)
    assert idempotency_key(original) == idempotency_key(changed)
    assert payload_digest(original) != payload_digest(changed)


def test_digest_stable_for_reordered_keys():
    data = payload()
    reordered = dict(reversed(list(data.items())))
    assert payload_digest(validate_event(data)) == payload_digest(validate_event(reordered))


def test_sensor_adapter():
    assert normalize_event(payload(), "sensor").kind == "smoke"


def test_sensor_rejects_camera():
    data = payload()
    data["source"]["category"] = "camera"
    with pytest.raises(InvalidEvent):
        normalize_event(data, "sensor")


def test_camera_requires_simulation_and_camera_kind():
    data = json.loads((FIXTURES / "camera.json").read_text())
    assert normalize_event(data, "camera-simulator").kind == "motion"
    for mutation in ({"simulated": False}, {"category": "sensor"}):
        invalid = copy.deepcopy(data)
        invalid["source"].update(mutation)
        with pytest.raises(InvalidEvent):
            normalize_event(invalid, "camera-simulator")
    data["kind"] = "smoke"
    with pytest.raises(InvalidEvent):
        normalize_event(data, "camera-simulator")


def test_safety_hints_never_authorize():
    hints = safety_metadata(validate_event(payload()))
    assert hints.simulated
    assert not hints.authorizes_action
    assert not hints.occupancy_verified


def test_schema_accepts_fixture_and_rejects_extra():
    validator = Draft202012Validator(IncidentEvent.model_json_schema())
    data = payload()
    assert not list(validator.iter_errors(data))
    data["unknown"] = True
    assert list(validator.iter_errors(data))


def test_cli_validate_and_emit(capsys):
    assert main(["validate", str(FIXTURES / "smoke.json")]) == 0
    assert capsys.readouterr().out == "valid\n"
    assert main(["emit", str(FIXTURES / "smoke.json")]) == 0
    assert json.loads(capsys.readouterr().out)["source"]["simulated"] is True


def test_cli_replay(capsys):
    assert main(["replay", str(FIXTURES / "scenario.jsonl")]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_cli_replay_atomic_validation(tmp_path, capsys):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps(payload()) + '\n{"private":"secret"}\n')
    assert main(["replay", str(path)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "secret" not in captured.err


def test_cli_malformed_json_redacted(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text("PRIVATE not json")
    assert main(["validate", str(path)]) == 2
    assert "PRIVATE" not in capsys.readouterr().err


def test_cli_missing_file(tmp_path, capsys):
    assert main(["validate", str(tmp_path / "absent")]) == 2
    assert "FileNotFoundError" in capsys.readouterr().err


def test_cli_schema(capsys):
    assert main(["schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["additionalProperties"] is False
