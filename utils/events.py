# utils/events.py

import json
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
# Root para todos los eventos
EVENTS_ROOT = BASE_DIR / "data" / "events"


def init_event(event_id: str, meta: dict = None) -> Path:
    """
    Crea la carpeta del evento con ID de 7 caracteres y la estructura interna:
      data/events/{event_id}/meta.json
      data/events/{event_id}/partidos.json
      data/events/{event_id}/exports/csv/
      data/events/{event_id}/exports/pdf/

    Args:
        event_id: ID único de 7 caracteres.
        meta: Diccionario opcional con metadata a guardar en meta.json.

    Raises:
        ValueError: Si el event_id no tiene exactamente 7 caracteres.

    Returns:
        Path al directorio del evento.
    """
    if len(event_id) != 7:
        raise ValueError("El ID de evento debe tener exactamente 7 caracteres")

    event_dir = EVENTS_ROOT / event_id
    csv_dir = event_dir / "exports" / "csv"
    pdf_dir = event_dir / "exports" / "pdf"

    # Crear estructura de carpetas
    for path in (event_dir, csv_dir, pdf_dir):
        path.mkdir(parents=True, exist_ok=True)

    # Archivos base
    partidos_file = event_dir / "partidos.json"
    meta_file = event_dir / "meta.json"

    # Inicializar lista de partidos si no existe
    if not partidos_file.exists():
        partidos_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

    # Guardar meta si se proporciona
    if meta is not None:
        meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return event_dir


def load_partidos(event_id: str) -> list:
    """
    Carga y retorna la lista de partidos desde data/events/{event_id}/partidos.json.
    """
    partidos_file = EVENTS_ROOT / event_id / "partidos.json"
    if not partidos_file.exists():
        return []
    return json.loads(partidos_file.read_text(encoding="utf-8"))


def save_partidos(event_id: str, partidos: list):
    """
    Guarda la lista de partidos en data/events/{event_id}/partidos.json.
    """
    partidos_file = EVENTS_ROOT / event_id / "partidos.json"
    partidos_file.write_text(json.dumps(partidos, ensure_ascii=False, indent=2), encoding="utf-8")


def get_csv_path(event_id: str, filename: str) -> str:
    """
    Retorna la ruta completa para un CSV en data/events/{event_id}/exports/csv.
    """
    return str(EVENTS_ROOT / event_id / "exports" / "csv" / f"{filename}.csv")


def get_pdf_path(event_id: str, filename: str) -> str:
    """
    Retorna la ruta completa para un PDF en data/events/{event_id}/exports/pdf.
    """
    return str(EVENTS_ROOT / event_id / "exports" / "pdf" / f"{filename}.pdf")
