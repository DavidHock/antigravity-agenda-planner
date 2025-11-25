#!/usr/bin/env python3
"""
Simple console helper for interacting with the Agenda Planner backend.

Examples:
  Generate an agenda:
    python3 cli/agenda_cli.py generate \
        --topic "Exchange Dev <> Research" \
        --location "HQ Berlin / Teams" \
        --start "2024-12-05T10:00:00" \
        --end "2024-12-05T11:00:00" \
        --language EN \
        --email "Please align on priorities."

  Refine free-text agenda content:
    python3 cli/agenda_cli.py refine --text-file agenda.txt --language EN

  Download ICS for previously generated agenda JSON:
    python3 cli/agenda_cli.py ics \
        --topic "Dev Sync" \
        --location "Room A" \
        --start "2024-12-05T10:00:00" \
        --end "2024-12-05T11:00:00" \
        --agenda-json agenda.json \
        --output dev_sync.ics
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable

import requests

API_BASE = os.environ.get("AGENDA_API_BASE", "http://localhost:8086")


def _print_json(payload: str | dict) -> None:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            print(payload)
            return
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _open_files(file_paths: Iterable[Path]):
    for path in file_paths:
        if not path.exists():
            raise FileNotFoundError(path)
        yield ("files", (path.name, path.open("rb")))


def handle_generate(args: argparse.Namespace) -> None:
    data = {
        "topic": args.topic,
        "start_time": args.start,
        "end_time": args.end,
        "language": args.language,
        "email_content": args.email or "",
    }

    files = list(_open_files(Path(p) for p in args.attachments or []))

    resp = requests.post(f"{API_BASE}/generate-agenda", data=data, files=files or None, timeout=120)
    resp.raise_for_status()

    agenda = resp.json().get("agenda", "")
    if args.output:
        Path(args.output).write_text(agenda, encoding="utf-8")
        print(f"Agenda JSON stored at {args.output}")
    else:
        _print_json(agenda)


def handle_refine(args: argparse.Namespace) -> None:
    text = Path(args.text_file).read_text(encoding="utf-8")
    instruction = "Please keep the text in German." if args.language == "DE" else "Keep the text in English."
    if args.instruction:
        instruction = args.instruction

    data = {"text": text, "instruction": instruction}
    resp = requests.post(f"{API_BASE}/refine-text", data=data, timeout=60)
    resp.raise_for_status()

    refined = resp.json().get("refined_text", "")
    if args.output:
        Path(args.output).write_text(refined, encoding="utf-8")
        print(f"Refined text stored at {args.output}")
    else:
        print(refined)


def handle_ics(args: argparse.Namespace) -> None:
    if args.agenda_json:
        agenda_content = Path(args.agenda_json).read_text(encoding="utf-8")
    elif args.agenda_text:
        agenda_content = Path(args.agenda_text).read_text(encoding="utf-8")
    else:
        print("Either --agenda-json or --agenda-text must be provided for ICS export.")
        sys.exit(1)

    data = {
        "topic": args.topic,
        "start_time": args.start,
        "end_time": args.end,
        "location": args.location,
        "agenda_content": agenda_content,
    }
    resp = requests.post(f"{API_BASE}/create-ics", data=data, timeout=60)
    resp.raise_for_status()

    output = Path(args.output or f"{args.topic.replace(' ', '_')}.ics")
    output.write_bytes(resp.content)
    print(f"ICS saved to {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Console helper for Agenda Planner.")
    parser.add_argument(
        "--api-base",
        default=API_BASE,
        help=f"Agenda Planner backend base URL (default: {API_BASE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Generate a new agenda")
    gen.add_argument("--topic", required=True)
    gen.add_argument("--location", default="TBD")
    gen.add_argument("--start", required=True, help="Start timestamp (ISO, e.g. 2024-05-01T09:00:00)")
    gen.add_argument("--end", required=True, help="End timestamp (ISO)")
    gen.add_argument("--language", choices=["DE", "EN"], default="DE")
    gen.add_argument("--email", help="Email context or notes")
    gen.add_argument("--attachments", nargs="*", help="Optional file paths to include")
    gen.add_argument("--output", help="Optional file to store agenda JSON")
    gen.set_defaults(func=handle_generate)

    refine = subparsers.add_parser("refine", help="Refine agenda text via LLM")
    refine.add_argument("--text-file", required=True, help="Path to text file to refine")
    refine.add_argument("--language", choices=["DE", "EN"], default="DE")
    refine.add_argument("--instruction", help="Custom instruction for refinement")
    refine.add_argument("--output", help="Optional file to store refined text")
    refine.set_defaults(func=handle_refine)

    ics = subparsers.add_parser("ics", help="Create ICS file from existing agenda content")
    ics.add_argument("--topic", required=True)
    ics.add_argument("--location", required=True)
    ics.add_argument("--start", required=True)
    ics.add_argument("--end", required=True)
    ics.add_argument("--agenda-json", help="Path to agenda JSON file")
    ics.add_argument("--agenda-text", help="Path to agenda text file")
    ics.add_argument("--output", help="Destination .ics file")
    ics.set_defaults(func=handle_ics)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    global API_BASE
    API_BASE = args.api_base
    try:
        args.func(args)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc.response.status_code} {exc.response.text}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

