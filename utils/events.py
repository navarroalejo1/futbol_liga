import json
from pathlib import Path
from typing import Any, Union

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
# Carpeta donde viven todos los eventos
EVENTS_ROOT = BASE_DIR / "data" / "events"


def get_event_dir(event_id: str) -> Path:
    """
    Devuelve el Path al directorio de un evento (data/events/{event_id}),
    creándolo si no existía.
    """
    event_dir = EVENTS_ROOT / event_id
    event_dir.mkdir(parents=True, exist_ok=True)
    return event_dir


def get_event_file(event_id: str, filename: str) -> Path:
    """
    Construye la ruta completa a un archivo dentro del directorio del evento.
    """
    event_dir = get_event_dir(event_id)
    return event_dir / filename


def load_json(event_id: str, filename: str) -> Union[list, dict]:
    """
    Lee un JSON desde data/events/{event_id}/{filename}.
    Si el archivo no existe, devuelve [] para listas o {} para dicts según uso.
    """
    file_path = get_event_file(event_id, filename)
    if file_path.exists():
        return json.loads(file_path.read_text(encoding="utf-8"))
    return []


def save_json(event_id: str, filename: str, data: Any) -> None:
    """
    Serializa y guarda `data` como JSON en data/events/{event_id}/{filename},
    con indentación para ser legible.
    """
    file_path = get_event_file(event_id, filename)
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def init_event(event_id: str, meta: dict = None) -> Path:
    """
    Crea la estructura básica de un evento:
      - data/events/{event_id}/
      - data/events/{event_id}/partidos.json   (lista vacía)
      - data/events/{event_id}/meta.json       (si se pasa `meta`)
      - data/events/{event_id}/exports/csv/
      - data/events/{event_id}/exports/pdf/

    Args:
        event_id: ID de 7 caracteres.
        meta:    Diccionario opcional con información adicional.

    Raises:
        ValueError: si `event_id` no tiene 7 caracteres.

    Returns:
        Path al directorio del evento.
    """
    if len(event_id) != 7:
        raise ValueError("El ID de evento debe tener exactamente 7 caracteres")

    # Crear carpetas
    main_dir = get_event_dir(event_id)
    (main_dir / "exports" / "csv").mkdir(parents=True, exist_ok=True)
    (main_dir / "exports" / "pdf").mkdir(parents=True, exist_ok=True)

    # Inicializar archivos JSON
    if not get_event_file(event_id, "partidos.json").exists():
        save_json(event_id, "partidos.json", [])
    if meta is not None:
        save_json(event_id, "meta.json", meta)

    return main_dir


def load_partidos(event_id: str) -> list:
    """
    Alias para cargar data/events/{event_id}/partidos.json.
    """
    return load_json(event_id, "partidos.json")


def save_partidos(event_id: str, partidos: list) -> None:
    """
    Alias para guardar data/events/{event_id}/partidos.json.
    """
    save_json(event_id, "partidos.json", partidos)


def get_csv_path(event_id: str, filename: str) -> str:
    """
    Retorna la ruta para exportar un CSV en data/events/{event_id}/exports/csv/{filename}.csv
    """
    return str(get_event_file(event_id, f"exports/csv/{filename}.csv"))


def get_pdf_path(event_id: str, filename: str) -> str:
    """
    Retorna la ruta para exportar un PDF en data/events/{event_id}/exports/pdf/{filename}.pdf
    """
    return str(get_event_file(event_id, f"exports/pdf/{filename}.pdf"))
