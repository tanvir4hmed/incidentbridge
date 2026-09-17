"""Offline JSON/JSONL interface; emit/replay write stdout, never actuate devices."""

import argparse
import json
import sys
from pathlib import Path
from typing import cast

from .models import IncidentEvent
from .normalize import AdapterName, normalize_event
from .validate import InvalidEvent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "emit", "replay"):
        command = sub.add_parser(name)
        command.add_argument("path", type=Path)
        command.add_argument(
            "--adapter", choices=["webhook", "sensor", "camera-simulator"], default="webhook"
        )
    sub.add_parser("schema")
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            print(json.dumps(IncidentEvent.model_json_schema(), indent=2, sort_keys=True))
            return 0
        content = args.path.read_text(encoding="utf-8")
        records = content.splitlines() if args.command == "replay" else [content]
        if not records or any(not record.strip() for record in records):
            raise InvalidEvent("input must contain nonempty JSON records")
        # Validate the whole batch before emitting anything (no partial replay).
        events = [
            normalize_event(json.loads(record), cast(AdapterName, args.adapter))
            for record in records
        ]
        if args.command == "validate":
            print("valid")
        else:
            for event in events:
                print(event.model_dump_json())
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, InvalidEvent) as exc:
        # Parser/OS errors may contain input or paths: expose only their type.
        message = str(exc) if isinstance(exc, InvalidEvent) else type(exc).__name__
        print(f"invalid: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
