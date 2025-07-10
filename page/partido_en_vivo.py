# pages/partido_en_vivo.py

import streamlit as st
from datetime import datetime
import time
import pandas as pd
from utils.events import load_json, save_json
import importlib

# ───────────────────────────────────────────────────────────────
# Compatibilidad con rerun en distintas versiones de Streamlit
# ───────────────────────────────────────────────────────────────
try:
    rerun = st.experimental_rerun
except AttributeError:
    try:
        mod = importlib.import_module("streamlit.runtime.scriptrunner.script_requests")
        rerun = mod.request_rerun
    except ImportError:
        rerun = lambda: None

def registrar_evento(team, dorsal, name, tiempo, periodo, categoria, accion, detalle=""):
    """Añade un evento al log específico del partido."""
    evento = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "Team":      team,
        "Dorsal":    dorsal,
        "Name":      name,
        "Tiempo":    tiempo,
        "Periodo":   periodo,
        "Categoria": categoria,
        "Acción":    accion,
        "Detalle":   detalle
    }

    # Cargo el log de ESTE partido
    log = load_json(st.session_state.event_id, st.session_state.match_log_file) or []
    log.append(evento)
    save_json(st.session_state.event_id, st.session_state.match_log_file, log)

    # Actualizo estado de sesión
    st.session_state.events_log = log

    txt_det = f" ({detalle})" if detalle else ""
    st.success(f"✅ {team} • J{dorsal} {name} • {categoria}: {accion}{txt_det} @ {tiempo}")

def app():
    if st.session_state.get("wizard_step") != 5:
        return

    # ───────────────────────────────────────────────────────────────
    # Configuración de página y CSS
    # ───────────────────────────────────────────────────────────────
    st.set_page_config(page_title="Paso 5: Partido en Vivo", layout="wide")
    st.markdown("""
      <style>
        .block-container { padding-top:0.5rem !important; padding-bottom:0.5rem !important; }
        .element-container { padding-top:0.25rem !important; padding-bottom:0.25rem !important; }
        #MainMenu, header, footer { visibility:hidden; }
        .hex-btn { width:72px; height:42px; clip-path:polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%); background: var(--hex-color)!important; color:#fff!important; font-size:11px; font-weight:bold; text-align:center; line-height:42px; border:none!important; margin:1px 2px; }
        .circle-btn { width:40px; height:40px; border-radius:50%; background: var(--circle-color)!important; color:#fff!important; font-size:10px; font-weight:bold; text-align:center; line-height:40px; border:none!important; margin:1px 2px; }
        .dorsal-selected { background:#198754; color:#fff; padding:4px; border-radius:4px; margin:2px; display:inline-block; font-size:12px; }
      </style>
    """, unsafe_allow_html=True)

    # ───────────────────────────────────────────────────────────────
    # Contexto de evento y partido
    # ───────────────────────────────────────────────────────────────
    event_id = st.session_state.get("evento_activo")
    partido  = st.session_state.get("partido_activo")
    if not event_id or not partido:
        st.error("🔴 Debes crear/cargar un evento y seleccionar un partido antes de continuar.")
        return
    st.session_state.event_id = event_id

    # Defino el fichero de log único para este MatchID
    match_key = partido["id"]
    st.session_state.match_log_file = f"{match_key}_events.json"

    # ───────────────────────────────────────────────────────────────
    # Inicializar o recargar el log de ESTE partido
    # ───────────────────────────────────────────────────────────────
    if "events_log" not in st.session_state or st.session_state.get("match_key") != match_key:
        st.session_state.match_key = match_key
        # Cargo del JSON
        log = load_json(event_id, st.session_state.match_log_file) or []
        st.session_state.events_log = log
        # Reinicio cronómetro
        st.session_state.running    = False
        st.session_state.start_time = None
        st.session_state.elapsed    = 0.0

    # ───────────────────────────────────────────────────────────────
    # Cronómetro
    # ───────────────────────────────────────────────────────────────
    total = st.session_state.elapsed + (
        (datetime.now() - st.session_state.start_time).total_seconds()
        if st.session_state.running else 0
    )
    m, s = divmod(int(total), 60)
    tiempo_str = f"{m:02d}:{s:02d}"

    # ───────────────────────────────────────────────────────────────
    # Cabecera y controles
    # ───────────────────────────────────────────────────────────────
    local, visita = partido["local"], partido["visitante"]
    comp, cancha  = partido.get("competicion","-"), partido.get("cancha","-")
    c1, c2, c3, c4 = st.columns([4,1,1,2], gap="small")
    with c1:
        st.markdown(f"### 🏟️ {local} vs {visita}   |   Competición: {comp}   |   Cancha: {cancha}")
    with c2:
        if not st.session_state.running:
            if st.button("▶", key="pv_start"):
                st.session_state.running    = True
                st.session_state.start_time = datetime.now()
        else:
            if st.button("⏸", key="pv_pause"):
                st.session_state.elapsed += (datetime.now() - st.session_state.start_time).total_seconds()
                st.session_state.running = False
    with c3:
        if st.button("↺", key="pv_reset"):
            st.session_state.running    = False
            st.session_state.elapsed    = 0.0
            st.session_state.start_time = None
    with c4:
        st.metric("⏱️ Tiempo", tiempo_str)

    periodo = st.radio("", ["1er TIEMPO","2do TIEMPO","EXTRA TIEMPO"], horizontal=True, key="pv_periodo")
    st.markdown("---")
    if st.session_state.running:
        time.sleep(1)
        rerun()

    # ───────────────────────────────────────────────────────────────
    # Selección de jugador (dorsal + nombre)
    # ───────────────────────────────────────────────────────────────
    st.subheader("🏷️ Jugador")
    team     = st.radio("", [local, visita], horizontal=True, key="pv_team")
    plantilla = load_json(event_id, "plantilla.json") or []
    dorsales = sorted({j["dorsal"] for j in plantilla if j["equipo"] == team})
    sel      = st.session_state.get("dorsal_sel")
    name     = st.session_state.get("name_sel")
    cols     = st.columns(len(dorsales), gap="small")
    for col, d in zip(cols, dorsales):
        nm = next((j["nombre"] for j in plantilla if j["dorsal"]==d and j["equipo"]==team), "—")
        with col:
            if st.button(str(d), key=f"d_{d}"):
                st.session_state.dorsal_sel = d
                st.session_state.name_sel   = nm
        if sel == d:
            col.markdown(f"<div class='dorsal-selected'>{d} – {nm}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if not sel or not name:
        st.warning("Selecciona primero un dorsal.")
        return

    # ───────────────────────────────────────────────────────────────
    # Pestañas de acciones
    # ───────────────────────────────────────────────────────────────
    tabs = st.tabs(["⚽ Ofensiva","🛡️ Defensiva","⭐ Especiales"])

    # Ofensiva con sub-pestañas
    with tabs[0]:
        sub_actions = {
            "PASE":    ["ÉXITO","DESVÍO","FALLO","CENTRO", "SAQUE PORTERO"],
            "REGATE":  ["R-ÉXITO","R-FALLO"],
            "TIRO":    ["GOL","PARADO","FUERA"],
            "PENALTI": ["CONVERTIDO","FALLADO"],
            "FALTA RECIBIDA": ["RECIBIDA"],
            "CORNERS": ["CORNER"],
            "SAQUE LATERAL": ["ÉXITO","FALLO"]
        }
        sub_colors = {
            "PASE":    "#007bff",
            "REGATE":  "#fd7e14",
            "TIRO":    "#dc3545",
            "PENALTI": "#6610f2",
            "CORNERS": "#5aeb20",
            "SAQUE LATERAL": "#07a544"
        }
        sub_tabs = st.tabs(list(sub_actions.keys()))
        for cat, pane in zip(sub_actions, sub_tabs):
            with pane:
                items = sub_actions[cat]
                cols2 = st.columns(len(items), gap="small")
                for i, act in enumerate(items):
                    clr = sub_colors.get(cat, "#6c757d")
                    cols2[i].markdown(
                        f"<div class='hex-btn' style='--hex-color:{clr}'>{act}</div>",
                        unsafe_allow_html=True
                    )
                    if cols2[i].button(act, key=f"{cat}_{act}"):
                        registrar_evento(team, sel, name, tiempo_str, periodo, "Ofensiva", act, detalle=cat)

    # Defensiva
    with tabs[1]:
        def_actions = [
            "INTERCEPCIÓN","BLOQUEO","DESPEJE","DUELO", "CABECEO",
            "PRESION BALON", "ROBO","FALTA","TARJETA AMARILLA","TARJETA ROJA"
        ]
        def_colors  = {
            "INTERCEPCIÓN":    "#20c997","BLOQUEO":         "#17a2b8",
            "DESPEJE":         "#6f42c1","DUELO":           "#3562dc",
            "CABECEO":         "#fd7e14", "ROBO":            "#fd7e14",
            "FALTA":           "#ffc107", "PRESION BALON":   "#dc35c6",
            "TARJETA AMARILLA":"#ffc107","TARJETA ROJA":    "#dc3545",
        }
        cols3 = st.columns(6, gap="small")
        for i, act in enumerate(def_actions):
            clr = def_colors.get(act, "#6c757d")
            idx = i % 6
            cols3[idx].markdown(
                f"<div class='circle-btn' style='--circle-color:{clr}'>{act[:2]}</div>",
                unsafe_allow_html=True
            )
            if cols3[idx].button(act, key=f"def_{act}"):
                registrar_evento(team, sel, name, tiempo_str, periodo, "Defensiva", act)

    # Especiales
    with tabs[2]:
        esp_actions = ["OFFSIDE","SUSTITUCION ENTRA", "SUSTITUCION SALE","ABP_DIRECTO","ABP_INDIRECTO", "ABP_GOL"]
        esp_colors  = {
            "OFFSIDE":     "#6c757d","SUSTITUCION ENTRA":"#6610f2","SUSTITUCION SALE":"#6610f2",
            "ABP_DIRECTO":"#e83e8c","ABP_GOL":     "#28a745"
        }
        cols4 = st.columns(len(esp_actions), gap="small")
        for i, act in enumerate(esp_actions):
            clr = esp_colors.get(act, "#6c757d")
            cols4[i].markdown(
                f"<div class='hex-btn' style='--hex-color:{clr}'>{act}</div>",
                unsafe_allow_html=True
            )
            if cols4[i].button(act, key=f"esp_{act}"):
                registrar_evento(team, sel, name, tiempo_str, periodo, "Especial", act)

    # ───────────────────────────────────────────────────────────────
    # Mostrar log de ESTE partido
    # ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Registro de eventos")
    df = pd.DataFrame(st.session_state.events_log)
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True)
        if st.button("🗑️ Borrar log de este partido"):
            save_json(event_id, st.session_state.match_log_file, [])
            st.session_state.events_log = []
            st.success("Log borrado.")
            rerun()
    else:
        st.info("Aún no hay eventos para este partido.")

