import json
from pathlib import Path

import pytest
import responses

from cli import agenda_cli


@responses.activate
def test_generate_writes_agenda_file(tmp_path):
    output = tmp_path / "agenda.json"
    api_base = "http://mock-api"
    responses.post(
        f"{api_base}/generate-agenda",
        json={"agenda": json.dumps({"title": "Dev <> Research"})},
        status=200,
    )

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "generate",
        "--topic", "Exchange Dev <> Research",
        "--location", "HQ Berlin",
        "--start", "2025-01-15T09:00:00",
        "--end", "2025-01-15T10:00:00",
        "--language", "EN",
        "--output", str(output),
    ])

    assert exit_code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["title"] == "Dev <> Research"


@responses.activate
def test_refine_uses_instruction_and_outputs_file(tmp_path):
    text_file = tmp_path / "agenda.txt"
    text_file.write_text("Initial content", encoding="utf-8")
    output = tmp_path / "agenda_refined.txt"

    api_base = "http://mock-api"
    responses.post(
        f"{api_base}/refine-text",
        json={"refined_text": "Refined EN text"},
        status=200,
    )

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "refine",
        "--text-file", str(text_file),
        "--language", "EN",
        "--output", str(output),
    ])

    assert exit_code == 0
    assert output.read_text(encoding="utf-8") == "Refined EN text"


@responses.activate
def test_ics_downloads_calendar_file(tmp_path):
    agenda = tmp_path / "agenda.json"
    agenda.write_text(json.dumps({"title": "Dev Sync"}), encoding="utf-8")
    ics_output = tmp_path / "dev_sync.ics"

    api_base = "http://mock-api"
    responses.post(
        f"{api_base}/create-ics",
        body=b"ICS-DATA",
        status=200,
    )

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "ics",
        "--topic", "Dev Sync",
        "--location", "Room A",
        "--start", "2025-01-15T09:00:00",
        "--end", "2025-01-15T10:00:00",
        "--agenda-json", str(agenda),
        "--output", str(ics_output),
    ])

    assert exit_code == 0
    assert ics_output.read_bytes() == b"ICS-DATA"


@responses.activate
def test_generate_supports_attachments(tmp_path):
    attachment = tmp_path / "notes.txt"
    attachment.write_text("Notes", encoding="utf-8")

    api_base = "http://mock-api"
    captured_headers = {}

    def _callback(request):
        captured_headers["content_type"] = request.headers.get("Content-Type")
        return 200, {}, json.dumps({"agenda": "{}"})

    responses.add_callback(
        responses.POST,
        f"{api_base}/generate-agenda",
        callback=_callback,
        content_type="application/json",
    )

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "generate",
        "--topic", "Exchange Dev <> Research",
        "--location", "HQ Berlin",
        "--start", "2025-01-15T09:00:00",
        "--end", "2025-01-15T10:00:00",
        "--language", "EN",
        "--attachments", str(attachment),
    ])

    assert exit_code == 0
    assert "multipart/form-data" in captured_headers.get("content_type", "")


@responses.activate
def test_generate_prompts_for_missing_topic(monkeypatch):
    api_base = "http://mock-api"
    responses.post(
        f"{api_base}/generate-agenda",
        json={"agenda": "{}"},
        status=200,
    )

    inputs = iter(["Prompted Topic", "2025-02-01T11:00:00"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "generate",
        "--start", "2025-02-01T10:00:00",
        "--language", "EN",
    ])

    assert exit_code == 0


@responses.activate
def test_ics_prompts_for_agenda_content(monkeypatch, tmp_path):
    api_base = "http://mock-api"
    responses.post(
        f"{api_base}/create-ics",
        body=b"ICS",
        status=200,
    )

    inputs = iter([
        "Prompted Topic",
        "Room A",
        "2025-03-01T09:00:00",
        "2025-03-01T10:00:00",
        '{"title": "Prompted"}',
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    output_file = tmp_path / "meeting.ics"

    exit_code = agenda_cli.main([
        "--api-base", api_base,
        "ics",
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.read_bytes() == b"ICS"

