# pages/partido_en_vivo.py

import streamlit as st
from datetime import datetime
from utils.events import load_json, save_json, get_event_file

# Nombre de archivo para log de eventos
EVENTS_FILE = "events_log.json"

def registrar_evento(categoria, accion, jersey, periodo, tiempo):
    """
    Añade un evento al log en session_state y persiste en JSON.
    """
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "jersey":    jersey,
        "categoria": categoria,
        "accion":    accion,
        "periodo":   periodo,
        "tiempo":    tiempo
    }
    st.session_state.events_log.append(entry)
    save_json(st.session_state.event_id, EVENTS_FILE, st.session_state.events_log)
    st.success(f"✅ J{jersey} | {categoria}/{accion} | {periodo} @ {tiempo}")

def app():
    # 1) Contexto: solo si estamos en el paso 5
    if st.session_state.get("wizard_step") != 5:
        return

    # 2) Cabecera y cronómetro
    st.set_page_config(page_title="⏱ Partido en Vivo", layout="wide")
    st.title("⏱ Paso 5: Partido en Vivo")

    # Validar que exista evento y partido activo
    event_id = st.session_state.get("evento_activo")
    partido  = st.session_state.get("partido_activo")
    if not event_id or not partido:
        st.error("🔴 Debes crear un evento y seleccionar un partido antes.")
        return
    st.session_state.event_id = event_id  # para save_json en registrar_evento

    # Inicialización de timer
    if "running" not in st.session_state:
        st.session_state.running    = False
        st.session_state.start_time = None
        st.session_state.elapsed    = 0.0
        st.session_state.events_log = load_json(event_id, EVENTS_FILE)

    col1, col2, col3 = st.columns([1,1,2])
    # ▶ / ▮
    with col1:
        if not st.session_state.running:
            if st.button("▶ Iniciar", key="pv_start"):
                st.session_state.running    = True
                st.session_state.start_time = datetime.now()
        else:
            if st.button("▮ Pausar", key="pv_pause"):
                st.session_state.elapsed    += (datetime.now() - st.session_state.start_time).total_seconds()
                st.session_state.running    = False
    # Reset
    with col2:
        if st.button("↺ Reset", key="pv_reset"):
            st.session_state.running    = False
            st.session_state.elapsed    = 0.0
            st.session_state.start_time = None
    # Mostrar MM:SS
    with col3:
        total = st.session_state.elapsed
        if st.session_state.running:
            total += (datetime.now() - st.session_state.start_time).total_seconds()
        mins, secs = divmod(int(total), 60)
        st.metric("Tiempo", f"{mins:02d}:{secs:02d}")

    # Selector de periodo
    periodo = st.radio(
        "Periodo",
        ["1er TIEMPO", "2do TIEMPO", "EXTRA TIEMPO"],
        index=0,
        key="pv_periodo"
    )
    st.markdown("---")

    # 3) Selección de camiseta a partir de plantilla.json
    st.subheader("👕 Selecciona Camiseta")
    plantilla = load_json(event_id, "plantilla.json")
    # extraer dorsales de Local + Visitante
    local = partido["local"].strip().lower()
    vist  = partido["visitante"].strip().lower()
    dorsales = sorted({
        j["dorsal"] for j in plantilla
        if j["equipo"].strip().lower() in {local, vist}
    })
    cols = st.columns(4)
    selected = st.session_state.get("selected_jersey")
    for i, d in enumerate(dorsales):
        col = cols[i % 4]
        style = ""
        if selected == d:
            style = "background-color:#198754;color:white;"
        # botón de selección
        if col.button(str(d), key=f"jersey_{d}"):
            st.session_state.selected_jersey = d
        # resaltar número
        if selected == d:
            col.markdown(f"<div style='{style}padding:6px;border-radius:4px;text-align:center;'>{d}</div>",
                         unsafe_allow_html=True)
    st.markdown("---")

    # 4) Panel de Acciones Ofensivas
    st.subheader("⚽ Ofensiva")
    acciones_off = ["PASE","ÉXITO","DESVÍO","FALLO","ASISTENCIA","CENTRO","TIRO","GOL"]
    cols = st.columns(4)
    for i, act in enumerate(acciones_off):
        col = cols[i % 4]
        if col.button(act, key=f"off_{i}"):
            jersey = st.session_state.get("selected_jersey")
            if not jersey:
                st.error("❗ Primero selecciona una camiseta.")
            else:
                registrar_evento("Ofensiva", act, jersey, periodo, f"{mins:02d}:{secs:02d}")
    st.markdown("---")

    # 5) Panel de Acciones Defensivas
    st.subheader("🛡️ Defensiva")
    acciones_def = ["INTERCEPCIÓN","BLOQUEO","DESPEJE","FALTA","T.AMARILLA","T.ROJA"]
    cols = st.columns(3)
    for i, act in enumerate(acciones_def):
        col = cols[i % 3]
        if col.button(act, key=f"def_{i}"):
            jersey = st.session_state.get("selected_jersey")
            if not jersey:
                st.error("❗ Primero selecciona una camiseta.")
            else:
                registrar_evento("Defensiva", act, jersey, periodo, f"{mins:02d}:{secs:02d}")
    st.markdown("---")

    # 6) Panel de Especiales
    st.subheader("⭐ Especiales")
    acciones_esp = ["PENALTY","TIRO LIBRE","SAQUE ESQUINA","OFFSIDE"]
    cols = st.columns(4)
    for i, act in enumerate(acciones_esp):
        col = cols[i % 4]
        if col.button(act, key=f"esp_{i}"):
            jersey = st.session_state.get("selected_jersey")
            if not jersey:
                st.error("❗ Primero selecciona una camiseta.")
            else:
                registrar_evento("Especial", act, jersey, periodo, f"{mins:02d}:{secs:02d}")
    st.markdown("---")

    # 7) Panel de Cambios (Sale/Entra + dorsal)
    st.subheader("🔄 Cambios")
    c1, c2, c3 = st.columns(3)
    with c1:
        if c1.button("🔻 SALE", key="chg_sale"):
            st.session_state.chg_type = "Sale"
    with c2:
        if c2.button("🔺 ENTRA", key="chg_entra"):
            st.session_state.chg_type = "Entra"
    with c3:
        dorsal = c3.text_input("Dorsal", key="chg_dorsal")
        if dorsal:
            st.session_state.chg_dorsal = dorsal
    if st.button("Registrar Cambio", key="chg_reg"):
        jersey = st.session_state.get("selected_jersey")
        ct     = st.session_state.get("chg_type")
        dr     = st.session_state.get("chg_dorsal")
        if not ct or not dr:
            st.error("❗ Selecciona Sale/Entra y un dorsal.")
        else:
            registrar_evento("Cambio", ct, dr, periodo, f"{mins:02d}:{secs:02d}")
    st.markdown("---")

    # 8) Log de eventos
    st.subheader("📋 Log de Eventos")
    st.dataframe(st.session_state.events_log)
