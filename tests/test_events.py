import json
import pytest
from pathlib import Path

import utils.events as ev


def test_init_event_creates_structure(tmp_path, monkeypatch):
    # Redirect EVENTS_ROOT to temporary directory
    monkeypatch.setattr(ev, 'EVENTS_ROOT', tmp_path)
    event_id = 'ABC1234'
    meta = {'name': 'Test Event', 'start': '01/01/2025', 'end': '02/01/2025'}

    # Call init_event
    event_dir = ev.init_event(event_id, meta)

    # Check directories
    assert (tmp_path / event_id).is_dir()
    assert (tmp_path / event_id / 'exports' / 'csv').is_dir()
    assert (tmp_path / event_id / 'exports' / 'pdf').is_dir()

    # Check base files
    partidos_file = tmp_path / event_id / 'partidos.json'
    meta_file = tmp_path / event_id / 'meta.json'
    assert partidos_file.exists()
    assert meta_file.exists()

    # Validate contents
    with partidos_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert data == []

    with meta_file.open('r', encoding='utf-8') as f:
        metadata = json.load(f)
        assert metadata == meta


def test_init_event_invalid_id_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, 'EVENTS_ROOT', tmp_path)
    with pytest.raises(ValueError):
        ev.init_event('SHORT', {'name': 'Bad'})


def test_load_and_save_partidos(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, 'EVENTS_ROOT', tmp_path)
    event_id = 'EVENT01'
    ev.init_event(event_id)

    # Initially empty
    partidos = ev.load_partidos(event_id)
    assert partidos == []

    # Save a list and load again
    sample = [{'fecha': '01/01/2025', 'hora': '12:00'}]
    ev.save_partidos(event_id, sample)

    loaded = ev.load_partidos(event_id)
    assert loaded == sample


def test_get_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, 'EVENTS_ROOT', tmp_path)
    event_id = 'ABC1234'
    ev.init_event(event_id)

    # CSV path
    csv_path = ev.get_csv_path(event_id, 'match1')
    assert csv_path.endswith(f"data/events/{event_id}/exports/csv/match1.csv") or csv_path.endswith(f"{event_id}/exports/csv/match1.csv")

    # PDF path
    pdf_path = ev.get_pdf_path(event_id, 'report1')
    assert pdf_path.endswith(f"data/events/{event_id}/exports/pdf/report1.pdf") or pdf_path.endswith(f"{event_id}/exports/pdf/report1.pdf")
