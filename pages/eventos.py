import os
from pathlib import Path
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import utils.events as ev

# Ruta al directorio de datos
BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_DATA = BASE_DIR / "data" / "events"

# Registrar esta página en Dash
dash.register_page(__name__, path="/eventos", name="Eventos")

layout = html.Div([
    html.H3("Gestión de Eventos"),
    html.Div([
        dcc.Input(id="input-event-id", type="text", maxLength=7, placeholder="ID (7 caracteres)"),
        dcc.Input(id="input-event-name", type="text", placeholder="Nombre del evento"),
        dcc.Input(id="input-event-start", type="text", placeholder="Fecha inicio DD/MM/AAAA"),
        dcc.Input(id="input-event-end", type="text", placeholder="Fecha fin DD/MM/AAAA"),
        html.Button("Crear Evento", id="btn-crear-evento"),
    ], style={"display":"flex", "gap":"10px"}),
    html.Div(id="msg-evento", style={"marginTop":"10px"}),
    html.Hr(),
    html.Div([
        dcc.Dropdown(id="dropdown-eventos", placeholder="Selecciona evento"),
        html.Button("Cargar Evento", id="btn-cargar-evento"),
    ], style={"display":"flex", "gap":"10px"}),
    html.Div(id="msg-cargar-evento", style={"marginTop":"10px"}),
    dcc.Store(id="evento-activo"),
])

@callback(
    Output("msg-evento", "children"),
    Input("btn-crear-evento", "n_clicks"),
    State("input-event-id", "value"),
    State("input-event-name", "value"),
    State("input-event-start", "value"),
    State("input-event-end", "value"),
    prevent_initial_call=True
)
def crear_evento(n, eid, name, start, end):
    if not eid or len(eid) != 7:
        return "El ID debe tener exactamente 7 caracteres."
    meta = {"name": name, "start": start, "end": end}
    try:
        ev.init_event(eid, meta)
        return f"Evento {eid} creado correctamente."
    except Exception as e:
        return f"Error al crear evento: {e}"

@callback(
    Output("dropdown-eventos", "options"),
    Input("msg-evento", "children"),
)
def actualizar_lista(_):
    if not EVENTS_DATA.exists():
        return []
    ids = [p.name for p in EVENTS_DATA.iterdir() if p.is_dir()]
    return [{"label": i, "value": i} for i in ids]

@callback(
    Output("msg-cargar-evento", "children"),
    Output("evento-activo", "data"),
    Input("btn-cargar-evento", "n_clicks"),
    State("dropdown-eventos", "value"),
    prevent_initial_call=True
)
def cargar_evento(n, selected):
    if not selected:
        return "Selecciona un evento.", no_update
    return f"Evento {selected} cargado.", {"event_id": selected}