# pages/partido_en_vivo.py

import streamlit as st
from datetime import datetime
import time
import pandas as pd
from utils.events import load_json, save_json
import importlib

EVENTS_FILE = "events_log.json"

# ───────────────────────────────────────────────────────────────
# Compatibilidad rerun en todas versiones de Streamlit
# ───────────────────────────────────────────────────────────────
try:
    rerun = st.experimental_rerun
except AttributeError:
    try:
        _mod = importlib.import_module("streamlit.runtime.scriptrunner.script_requests")
        rerun = _mod.request_rerun
    except ImportError:
        rerun = lambda: None

# ───────────────────────────────────────────────────────────────
# Función: registrar eventos con formato fijo
# ───────────────────────────────────────────────────────────────
def registrar_evento(team, dorsal, name, tiempo, periodo, categoria, accion, detalle=""):
    evento = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "Team": team,
        "Dorsal": dorsal,
        "Name": name,
        "Tiempo": tiempo,
        "Periodo": periodo,
        "Categoria": categoria,
        "Acción": accion,
        "Detalle": detalle
    }
    st.session_state.events_log.append(evento)
    save_json(st.session_state.event_id, EVENTS_FILE, st.session_state.events_log)
    st.success(f"✅ {team} • J{dorsal} {name} • {categoria}: {accion} @ {tiempo}")

# ───────────────────────────────────────────────────────────────
# App Partido en Vivo: compacta y sin espacios fantasma
# ───────────────────────────────────────────────────────────────
def app():
    if st.session_state.get("wizard_step") != 5:
        return

    # Página wide y CSS para eliminar márgenes y padding
    st.set_page_config(page_title="Paso 5: Partido en Vivo", layout="wide")
    st.markdown("""
    <style>
      /* Quitar padding global */
      .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
      /* Reducir padding entre elementos */
      .element-container { padding-top: 0.25rem !important; padding-bottom: 0.25rem !important; }
      /* Ocultar menú/header/footer */
      #MainMenu, header, footer { visibility: hidden; }
      /* Márgenes de títulos */
      .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { margin: 0; padding: 0; }
      /* Reducir márgenes de subheader */
      .stSubheader { margin-top: 0.25rem; margin-bottom: 0.25rem; }
      /* Reducir márgenes de radio */
      .stRadio { margin-top: 0.25rem !important; margin-bottom: 0.25rem !important; }
      /* Hexágono */
      .hex-btn {
        width: 72px; height: 42px;
        clip-path: polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%);
        background: var(--hex-color) !important;
        color: white !important; font-weight: bold;
        border: none !important; margin: 1px 2px;
        font-size: 11px; text-align: center; line-height: 42px;
      }
      /* Círculo */
      .circle-btn {
        width: 40px; height: 40px; border-radius: 50%;
        background: var(--circle-color) !important;
        color: white !important; font-weight: bold;
        border: none !important; margin: 1px 2px;
        font-size: 10px; text-align: center; line-height: 40px;
      }
      /* Dorsal seleccionado */
      .dorsal-selected {
        background: #198754; color: white;
        padding: 4px; border-radius: 4px;
        margin: 2px; display: inline-block;
      }
    </style>
    """, unsafe_allow_html=True)

    # Cargar contexto de evento y partido
    partido = st.session_state.get("partido_activo")
    event_id = st.session_state.get("evento_activo")
    if not event_id or not partido:
        st.error("🔴 Debes crear un evento y seleccionar un partido antes de continuar.")
        return
    st.session_state.event_id = event_id

    # Datos de cabecera
    local = partido["local"]
    visita = partido["visitante"]
    comp = partido.get("competicion", "-")
    cancha = partido.get("cancha", "-")

    # Inicializar cronómetro y log
    if "running" not in st.session_state:
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.elapsed = 0.0
        st.session_state.events_log = load_json(event_id, EVENTS_FILE) or []

    # Cabecera + cronómetro en una sola fila
    c1, c2 = st.columns([4, 1], gap="small")
    with c1:
        st.markdown(f"### 🏟️ {local} vs {visita}   •   Competición: {comp}   •   Cancha: {cancha}")
    with c2:
        if not st.session_state.running:
            if st.button("▶", key="pv_start"):
                st.session_state.running = True
                st.session_state.start_time = datetime.now()
        else:
            if st.button("⏸", key="pv_pause"):
                st.session_state.elapsed += (datetime.now() - st.session_state.start_time).total_seconds()
                st.session_state.running = False
        if st.button("↺", key="pv_reset"):
            st.session_state.running = False
            st.session_state.elapsed = 0.0
            st.session_state.start_time = None
        total = st.session_state.elapsed + ((datetime.now() - st.session_state.start_time).total_seconds() if st.session_state.running else 0)
        m, s = divmod(int(total), 60)
        st.metric("⏱️ Tiempo", f"{m:02d}:{s:02d}")

    # Selector de periodo compacto
    periodo = st.radio("Periodo", ["1er TIEMPO", "2do TIEMPO", "EXTRA TIEMPO"], horizontal=True, key="pv_periodo")
    st.markdown("---")
    if st.session_state.running:
        time.sleep(1)
        rerun()

    # Selección de jugador y dorsal (en una sola línea)
    st.subheader("🏷️ Jugador")
    team = st.radio("Team", [local, visita], horizontal=True, key="pv_team")
    plantilla = load_json(event_id, "plantilla.json") or []
    dorsales = sorted({p.get('dorsal') for p in plantilla if p.get('equipo') == team})
    sel = st.session_state.get("dorsal_sel")
    name = st.session_state.get("name_sel")
    cols = st.columns(len(dorsales))
    for col, d in zip(cols, dorsales):
        nm = next((p['nombre'] for p in plantilla if p['dorsal']==d and p['equipo']==team), "Desconocido")
        with col:
            if st.button(str(d), key=f"d{d}"):
                st.session_state.dorsal_sel = d
                st.session_state.name_sel = nm
        if sel == d:
            col.markdown(f"<div class='dorsal-selected'>{d} - {nm}</div>", unsafe_allow_html=True)
    st.markdown("---")
    if not sel or not name:
        st.warning("Selecciona un dorsal.")
        return
    tiempo_str = f"{m:02d}:{s:02d}"

    # Pestañas principales de acciones
    tabs = st.tabs(["⚽ Ofensiva", "🛡️ Defensiva", "⭐ Especiales"])

    # Ofensiva con sub-pestañas para cada tipo
    with tabs[0]:
        sub_actions = {
            "PASE": ["ÉXITO","DESVÍO","FALLO","ASISTENCIA","CENTRO"],
            "REGATE": ["R-ÉXITO","R-FALLO"],
            "FALTA RECIBIDA": ["FALTA RECIBIDA"],
            "TIRO": ["GOL","PARADO","FUERA"],
            "PENALTI": ["CONVERTIDO","FALLADO"],
            "CORNERS": ["CORNER"]
        }
        colors = {"PASE":"#007bff","REGATE":"#fd7e14","FALTA RECIBIDA":"#ffc107","TIRO":"#dc3545","PENALTI":"#6610f2","CORNERS":"#20c997"}
        sub_tabs = st.tabs(list(sub_actions.keys()))
        for cat, sub_tab in zip(sub_actions, sub_tabs):
            with sub_tab:
                cols2 = st.columns(len(sub_actions[cat]))
                for i, act in enumerate(sub_actions[cat]):
                    clr = colors.get(cat, "#6c757d")
                    cols2[i].markdown(
                        f"<div class='hex-btn' style='--hex-color:{clr}'>{act}</div>", unsafe_allow_html=True
                    )
                    if cols2[i].button(act, key=f"{cat}_{act}"):
                        registrar_evento(team, sel, name, tiempo_str, periodo, "Ofensiva", act, detalle=cat)

    # Defensivas en grid compacto
    with tabs[1]:
        def_actions = ["INTERCEPCIÓN","BLOQUEO","DESPEJE","DUELO","ROBO","FALTA","TARJETA AMARILLA","TARJETA ROJA"]
        def_colors = {"INTERCEPCIÓN":"#20c997","BLOQUEO":"#17a2b8","DESPEJE":"#6f42c1","DUELO":"#3562dc","ROBO":"#fd7e14","FALTA":"#ffc107","TARJETA AMARILLA":"#ffc107","TARJETA ROJA":"#dc3545"}
        cols3 = st.columns(4)
        for i, act in enumerate(def_actions):
            clr = def_colors.get(act, "#6c757d")
            cols3[i%4].markdown(
                f"<div class='circle-btn' style='--circle-color:{clr}'>{act[:2]}</div>", unsafe_allow_html=True
            )
            if cols3[i%4].button(act, key=f"def_{act}"):
                registrar_evento(team, sel, name, tiempo_str, periodo, "Defensiva", act)

    # Especiales en una sola fila
    with tabs[2]:
        esp_actions = ["OFFSIDE","SUSTITUCION","ABP_DIRECTO","ABP_GOL"]
        esp_colors = {"OFFSIDE":"#6c757d","SUSTITUCION":"#6610f2","ABP_DIRECTO":"#e83e8c","ABP_GOL":"#28a745"}
        cols4 = st.columns(len(esp_actions))
        for i, act in enumerate(esp_actions):
            clr = esp_colors.get(act, "#6c757d")
            cols4[i].markdown(
                f"<div class='hex-btn' style='--hex-color:{clr}'>{act}</div>", unsafe_allow_html=True
            )
            if cols4[i].button(act, key=f"esp_{act}"):
                registrar_evento(team, sel, name, tiempo_str, periodo, "Especial", act)

    # Log final compacto
    st.markdown("---")
    st.subheader("📋 Registro de eventos")
    df = pd.DataFrame(st.session_state.events_log)
    if not df.empty:
        df = df[["timestamp","Team","Dorsal","Name","Tiempo","Periodo","Categoria","Acción","Detalle"]]
        df = df.iloc[::-1]  # Invierte el DataFrame para mostrar el más reciente arriba
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay eventos registrados.")

if __name__ == "__main__":
    app()
