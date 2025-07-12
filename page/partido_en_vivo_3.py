# pages/partido_en_vivo.py

import streamlit as st
from datetime import datetime
import time
import pandas as pd
from utils.events import load_json, save_json
import importlib

# ───────────────────────────────────────────────────────────────
# Compatibilidad con st.experimental_rerun en todas las versiones
# ───────────────────────────────────────────────────────────────
try:
    rerun = st.experimental_rerun
except AttributeError:
    try:
        sr = importlib.import_module("streamlit.runtime.scriptrunner.script_requests")
        rerun = sr.request_rerun
    except ImportError:
        rerun = lambda: None

def registrar_evento(team, dorsal, name, tiempo, periodo, categoria, accion, detalle=""):
    """Añade un evento al log específico de este partido."""
    ev = {
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
    log = load_json(st.session_state.event_id, st.session_state.match_log_file) or []
    log.append(ev)
    save_json(st.session_state.event_id, st.session_state.match_log_file, log)
    st.session_state.events_log = log
    suf = f" ({detalle})" if detalle else ""
    st.success(f"✅ {team} • J{dorsal} {name} • {categoria}: {accion}{suf} @ {tiempo}")

def app():
    # Solo paso 5
    if st.session_state.get("wizard_step") != 5:
        return

    # ───────────────────────────────────────────────────────────
    # Page config + CSS ultra-compacto
    # ───────────────────────────────────────────────────────────
    st.set_page_config(page_title="⚽ Paso 5 – Partido en Vivo", layout="wide")
    st.markdown("""
<style>
  .block-container { padding: 0.2rem 1rem !important; }
  .element-container { padding: 0.1rem 0 !important; }
  #MainMenu, header, footer { visibility: hidden; }
  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { margin:0; padding:0; }
  .stSubheader, .stHeader { margin:0.15rem 0 !important; }
  .stRadio, .stRadio > div { margin:0.1rem 0 !important; }
  .stButton>button {
    border-radius:8px !important;
    margin:0.1rem !important;
    padding:0.2rem 0.4rem !important;
    font-size:0.8rem !important;
    min-height:28px !important;
  }
  .stMarkdown hr { margin:0.2rem 0 !important; border-color:#ddd !important; }
  .stColumns { gap:0.2rem !important; }
  /* Colores por sección */
  .ofensiva .stButton>button { background:#007bff !important; color:#fff !important; }
  .defensiva .stButton>button { background:#28a745 !important; color:#fff !important; }
  .especial  .stButton>button { background:#6610f2 !important; color:#fff !important; }
  /* Selección de dorsal */
  .titular-btn  { background:#198754 !important; color:#fff !important; }
  .suplente-btn { background:#ffc107 !important; color:#000 !important; }
</style>
""", unsafe_allow_html=True)

    # ───────────────────────────────────────────────────────────
    # Contexto de evento y partido
    # ───────────────────────────────────────────────────────────
    ev_id   = st.session_state.get("evento_activo")
    partido = st.session_state.get("partido_activo")
    if not ev_id or not partido:
        st.error("🔴 Debes crear/cargar un evento y seleccionar un partido.")
        return
    st.session_state.event_id = ev_id

    # unique match ID y fichero de log
    mid = partido.get("id") or f"{partido['local']}_{partido['visitante']}_{partido.get('fecha','')}_{partido.get('hora','')}"
    st.session_state.match_log_file = f"{mid}_events.json"

    # si cambiamos de partido, (re)inicializamos
    if st.session_state.get("current_mid") != mid:
        st.session_state.current_mid  = mid
        st.session_state.events_log   = load_json(ev_id, st.session_state.match_log_file) or []
        st.session_state.running      = False
        st.session_state.start_time   = None
        st.session_state.elapsed      = 0.0

    # ───────────────────────────────────────────────────────────
    # Cronómetro automático
    # ───────────────────────────────────────────────────────────
    elapsed = st.session_state.elapsed + (
        (datetime.now() - st.session_state.start_time).total_seconds()
        if st.session_state.running else 0
    )
    m, s = divmod(int(elapsed), 60)
    tiempo_str = f"{m:02d}:{s:02d}"

    # ───────────────────────────────────────────────────────────
    # Cabecera + controles
    # ───────────────────────────────────────────────────────────
    local, visita = partido["local"], partido["visitante"]
    comp  = partido.get("competicion","–")
    cancha= partido.get("cancha","–")
    c1, c2, c3, c4 = st.columns([4,1,1,2], gap="small")
    with c1:
        st.markdown(f"**🏟️ {local} vs {visita}**  |  Competición: {comp}  |  Cancha: {cancha}")
    with c2:
        if not st.session_state.running:
            if st.button("▶", key="start"): 
                st.session_state.running    = True
                st.session_state.start_time = datetime.now()
        else:
            if st.button("⏸", key="pause"):
                st.session_state.elapsed += (datetime.now() - st.session_state.start_time).total_seconds()
                st.session_state.running = False
    with c3:
        if st.button("↺", key="reset"):
            st.session_state.running    = False
            st.session_state.elapsed    = 0.0
            st.session_state.start_time = None
    with c4:
        st.metric("⏱️ Tiempo", tiempo_str)

    periodo = st.radio("", ["1er TIEMPO","2do TIEMPO","EXTRA TIEMPO"], horizontal=True, key="pv_periodo")
    st.markdown("---")
    if st.session_state.running:
        time.sleep(1); rerun()

    # ───────────────────────────────────────────────────────────
    # Selección de jugador (Titulares / Suplentes)
    # ───────────────────────────────────────────────────────────
    st.subheader("🏷️ Selección de Jugador")
    team = st.radio("", [local, visita], horizontal=True, key="pv_team")
    plantilla = load_json(ev_id, "plantilla.json") or []
    titulares = [j for j in plantilla if j["equipo"]==team and j.get("tipo","Titular")=="Titular"]
    suplentes = [j for j in plantilla if j["equipo"]==team and j.get("tipo","Titular")=="Suplente"]
    sel  = st.session_state.get("dorsal_sel")
    name = st.session_state.get("name_sel")

    if titulares:
        st.markdown("**Titulares:**")
        cols = st.columns(len(titulares), gap="small")
        for col, j in zip(cols, titulares):
            if col.button(str(j["dorsal"]), key=f"d_{j['dorsal']}"):
                st.session_state.dorsal_sel = j["dorsal"]; st.session_state.name_sel = j["nombre"]
            if sel == j["dorsal"]:
                col.markdown(f"<div class='titular-btn'>{j['dorsal']}</div>", unsafe_allow_html=True)

    if suplentes:
        st.markdown("**Suplentes:**")
        cols = st.columns(len(suplentes), gap="small")
        for col, j in zip(cols, suplentes):
            if col.button(str(j["dorsal"]), key=f"d_{j['dorsal']}_s"):
                st.session_state.dorsal_sel = j["dorsal"]; st.session_state.name_sel = j["nombre"]
            if sel == j["dorsal"]:
                col.markdown(f"<div class='suplente-btn'>{j['dorsal']}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if not sel or not name:
        st.warning("Selecciona primero un dorsal.")
        return

    # ───────────────────────────────────────────────────────────
    # ACCIONES: filas de 8 botones coloreados
    # ───────────────────────────────────────────────────────────
    acciones = {
      "Ofensiva": (
         ["P_ÉXITO","P_DESVÍO","P_FALLO","CENTRO","REG-ÉXITO","REG-FALLO","F_RECIB","DRIBLING",
          "CABECEO","DUELO_OF","GOL","TIRO_DIR","TIRO_DESV","TIRO_FUERA"],
         "ofensiva"
      ),
      "Defensiva": (
         ["INTERCEPCIÓN","DESPEJE","DUELO_DF","ROBO",
          "FALTA","TARJETA AMARILLA","TARJETA ROJA","ARQ_ATRAP"],
         "defensiva"
      ),
      "Especial": (
         ["OFFSIDE","SUST_ENTRA","SUST_SALE","ABP_DIRECTO","ABP_INDIRECTO","ABP_GOL"],
         "especial"
      )
    }
    for cat, (lista, css_class) in acciones.items():
        st.subheader(("⚽" if cat=="Ofensiva" else "🛡️" if cat=="Defensiva" else "⭐") + f" {cat}")
        st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
        # chunk de 8 en 8
        chunk = 8
        for i in range(0, len(lista), chunk):
            row = lista[i:i+chunk]
            cols = st.columns(len(row), gap="small")
            for col, act in zip(cols, row):
                if col.button(act, key=f"{css_class}_{act}"):
                    registrar_evento(team, sel, name, tiempo_str, periodo, cat, act)
        st.markdown("</div>", unsafe_allow_html=True)

    # ───────────────────────────────────────────────────────────
    # Log invertido + edición
    # ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Registro de eventos")
    df = pd.DataFrame(st.session_state.events_log)
    if not df.empty:
        df_rev = df.iloc[::-1].reset_index(drop=True)
        st.dataframe(df_rev, use_container_width=True)
        idx = st.number_input("Índice a editar (0 = más reciente)", 0, len(df_rev)-1, key="idx_ev")
        ev_sel = df_rev.iloc[idx].to_dict()
        with st.expander("✏️ Editar/Eliminar"):
            edited = {}
            for k, v in ev_sel.items():
                edited[k] = st.text_input(k, value=str(v), key=f"edit_{k}")
            c1, c2, c3 = st.columns(3, gap="small")
            with c1:
                if st.button("💾 Guardar", key="save_ev"):
                    orig = len(df)-1-idx
                    log = st.session_state.events_log.copy()
                    log[orig] = edited
                    save_json(ev_id, st.session_state.match_log_file, log)
                    st.session_state.events_log = log; st.success("Actualizado"); rerun()
            with c2:
                if st.button("🗑️ Eliminar", key="del_ev"):
                    orig = len(df)-1-idx
                    log = st.session_state.events_log.copy()
                    log.pop(orig)
                    save_json(ev_id, st.session_state.match_log_file, log)
                    st.session_state.events_log = log; st.success("Eliminado"); rerun()
            with c3:
                if st.button("❌ Cancelar", key="cancel_ev"):
                    rerun()
        if st.button("🗑️ Borrar todo", key="clear_ev"):
            save_json(ev_id, st.session_state.match_log_file, [])
            st.session_state.events_log = []; st.success("Log borrado"); rerun()
    else:
        st.info("Aún no hay eventos para este partido.")

    # ───────────────────────────────────────────────────────────
    # Control manual del cronómetro
    # ───────────────────────────────────────────────────────────
    with st.expander("⏱️ Control manual del cronómetro", False):
        mi = st.number_input("Minuto",  0, 180, int(st.session_state.elapsed//60), key="min_in")
        si = st.number_input("Segundo",0,  59, int(st.session_state.elapsed%60), key="sec_in")
        if st.button("⏩ Establecer tiempo"):
            st.session_state.elapsed = mi*60 + si
            if st.session_state.running:
                st.session_state.start_time = datetime.now()
            st.success(f"{mi:02d}:{si:02d}"); rerun()
        if st.button("🔄 Reset completo"):
            st.session_state.running = False; st.session_state.elapsed = 0.0; st.session_state.start_time = None
            st.success("Reiniciado"); rerun()

