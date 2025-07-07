# pages/partido_en_vivo.py

import streamlit as st
from datetime import datetime
import time
from utils.events import load_json, save_json

EVENTS_FILE = "events_log.json"

def registrar_evento(categoria, accion, jersey, periodo, tiempo, equipo):
    """
    Añade un evento al log en session_state y persiste en JSON.
    """
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "jersey":    jersey,
        "categoria": categoria,
        "accion":    accion,
        "periodo":   periodo,
        "tiempo":    tiempo,
        "equipo":    equipo
    }
    st.session_state.events_log.append(entry)
    save_json(st.session_state.event_id, EVENTS_FILE, st.session_state.events_log)
    st.success(f"✅ J{jersey} • {categoria}/{accion} • {periodo} @ {tiempo} • {equipo}")

def app():
    # --- 0) Solo ejecutar en el paso 5 ---
    if st.session_state.get("wizard_step") != 5:
        return

    st.set_page_config(page_title="⏱ Partido en Vivo", layout="wide")
    st.title("⏱ Paso 5: Partido en Vivo")

    # --- 1) Validar contexto ---
    event_id = st.session_state.get("evento_activo")
    partido  = st.session_state.get("partido_activo")
    if not event_id or not partido:
        st.error("🔴 Debes crear un evento y seleccionar un partido primero.")
        return

    # lo guardamos para el save_json
    st.session_state.event_id = event_id

    # --- 2) Cronómetro & periodo ---
    if "running" not in st.session_state:
        st.session_state.running     = False
        st.session_state.start_time  = None
        st.session_state.elapsed     = 0.0
        st.session_state.events_log  = load_json(event_id, EVENTS_FILE)
        st.session_state.current_action = None

    ## selector de periodo obligatorio
    periodo = st.selectbox(
        "📋 Periodo",
        options=["", "1er TIEMPO", "2do TIEMPO", "EXTRA TIEMPO"],
        key="pv_periodo"
    )

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("▶ Iniciar", key="pv_start"):
            if not periodo:
                st.error("❗ Debes seleccionar un periodo antes de iniciar.")
            else:
                st.session_state.running    = True
                st.session_state.start_time = datetime.now()
    with col2:
        if st.button("↺ Reset", key="pv_reset"):
            st.session_state.running     = False
            st.session_state.elapsed     = 0.0
            st.session_state.start_time  = None

    # Métrica de tiempo
    timer = col3.empty()
    def mostrar_tiempo():
        total = st.session_state.elapsed
        if st.session_state.running:
            total += (datetime.now() - st.session_state.start_time).total_seconds()
        m, s = divmod(int(total), 60)
        timer.metric("⏰ Tiempo", f"{m:02d}:{s:02d}")
        return f"{m:02d}:{s:02d}"

    tiempo_actual = mostrar_tiempo()
    if st.session_state.running:
        time.sleep(1)
        st.experimental_rerun()

    st.markdown("---")

    # --- 3) Selección de equipo ---
    st.subheader("🏷️ Seleccionar Equipo para Análisis")
    equipo = st.radio(
        "Equipo:",
        options=[partido["local"], partido["visitante"]],
        key="pv_team"
    )

    st.markdown("---")

    # --- 4) Selección de camiseta desde plantilla.json ---
    plantilla = load_json(event_id, "plantilla.json")
    local = partido["local"].strip().lower()
    vist  = partido["visitante"].strip().lower()
    dorsales = sorted({
        j["dorsal"] for j in plantilla
        if j["equipo"].strip().lower() in {local, vist}
    })

    st.subheader("👕 Selecciona Camiseta")
    cols = st.columns(6)
    sel = st.session_state.get("selected_jersey")
    for i, d in enumerate(dorsales):
        col = cols[i % 6]
        if col.button(str(d), key=f"jersey_{d}"):
            st.session_state.selected_jersey = d
        # mostrar resaltado
        if sel == d:
            col.markdown(
                f"<div style='background:#198754;color:white;padding:4px;border-radius:3px;text-align:center;'>{d}</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # --- 5) Acciones Ofensivas con sub-flujos ---
    st.subheader("⚽ Ofensiva")
    colA, colB, colC = st.columns(3)
    # 5.1 PASE
    if colA.button("PASE", key="act_pase"):
        st.session_state.current_action = "PASE"
    # 5.2 TIRO A PUERTA
    if colB.button("TIRO A PUERTA", key="act_tiro"):
        st.session_state.current_action = "TIRO"
    # 5.3 GOL directo
    if colC.button("GOL", key="act_gol"):
        if not sel:
            st.error("❗ Selecciona una camiseta.")
        elif not periodo:
            st.error("❗ El periodo es obligatorio.")
        else:
            registrar_evento("Ofensiva", "GOL", sel, periodo, tiempo_actual, equipo)

    # 5.4 resultado de PASE
    if st.session_state.current_action == "PASE":
        res = st.selectbox("Resultado del PASE:", ["DESVÍO","FALLO","CENTRO"], key="res_pase")
        if st.button("✅ Confirmar PASE", key="conf_pase"):
            if not sel or not periodo:
                st.error("❗ Selecciona camiseta y periodo.")
            else:
                registrar_evento("Ofensiva", f"PASE – {res}", sel, periodo, tiempo_actual, equipo)
                st.session_state.current_action = None

    # 5.5 resultado de TIRO A PUERTA
    if st.session_state.current_action == "TIRO":
        res2 = st.selectbox("Resultado del TIRO A PUERTA:", ["FUERA","PARADO"], key="res_tiro")
        if st.button("✅ Confirmar TIRO", key="conf_tiro"):
            if not sel or not periodo:
                st.error("❗ Selecciona camiseta y periodo.")
            else:
                registrar_evento("Ofensiva", f"TIRO A PUERTA – {res2}", sel, periodo, tiempo_actual, equipo)
                st.session_state.current_action = None

    st.markdown("---")

    # --- 6) Aquí seguir con defensiva, especiales y cambios… ---

    # --- 7) Log de Eventos ---
    st.subheader("📋 Log de Eventos")
    st.dataframe(st.session_state.events_log)
