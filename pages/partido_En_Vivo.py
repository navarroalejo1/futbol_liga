# pages/partido_en_vivo.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.events import (
    get_event_file,
    load_json,
    save_json,
    get_csv_path,
    get_pdf_path
)

# Archivo donde guardamos el log de eventos
EVENTS_LOG_FILE = "events_log.json"
PLANTILLA_FILE  = "plantilla.json"

def app():
    """
    Paso 4: Partido en Vivo - Cronómetro, Registro de Eventos y Exportación
    """
    st.header("⏱ Paso 4: Partido en Vivo")

    # 1) Validar evento activo
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("❌ No hay evento activo. Regresa al Paso 1.")
        return

    st.subheader(f"Evento activo: {event_id}")

    # 2) Validar partido activo
    partido = st.session_state.get("partido_activo")
    if not partido:
        st.error("❌ No hay partido seleccionado. Regresa al Paso 2.")
        return

    st.markdown(f"**Partido:** {partido['fecha']} {partido['hora']} – "
                f"{partido['local']} vs {partido['visitante']}")

    # 3) Cronómetro y periodo
    if "running" not in st.session_state:
        st.session_state.update({
            "running": False,
            "start_time": None,
            "elapsed": 0.0,
            "periodo": "1er tiempo"
        })

    col1, col2, col3 = st.columns(3)
    with col1:
        if not st.session_state["running"]:
            if st.button("▶ Iniciar"):
                st.session_state["running"] = True
                st.session_state["start_time"] = datetime.now()
        else:
            if st.button("▮ Pausar"):
                st.session_state["running"] = False
                st.session_state["elapsed"] += (datetime.now() - st.session_state["start_time"]).total_seconds()
    with col2:
        if st.button("↺ Reset"):
            st.session_state["running"] = False
            st.session_state["start_time"] = None
            st.session_state["elapsed"] = 0.0
    with col3:
        total = st.session_state["elapsed"]
        if st.session_state["running"]:
            total += (datetime.now() - st.session_state["start_time"]).total_seconds()
        mins, secs = divmod(int(total), 60)
        st.metric("Tiempo", f"{mins:02d}:{secs:02d}")

    st.markdown("### Periodo")
    st.session_state["periodo"] = st.radio(
        "",
        ["1er tiempo", "2do tiempo"],
        horizontal=True,
        key="periodo_radio"
    )

    st.markdown("---")

    # 4) Cargar plantilla y filtrar solo jugadores del partido
    plantilla = load_json(event_id, PLANTILLA_FILE)
    local_eq = partido["local"].strip().lower()
    vist_eq  = partido["visitante"].strip().lower()

    jugadores_local = [
        j for j in plantilla
        if j["equipo"].strip().lower() == local_eq
    ]
    jugadores_visitante = [
        j for j in plantilla
        if j["equipo"].strip().lower() == vist_eq
    ]
    jugadores = [
        f"{j['nombre']} ({j['equipo']})"
        for j in jugadores_local + jugadores_visitante
    ]

    # 5) Registro de eventos
    if "events_log" not in st.session_state:
        st.session_state["events_log"] = load_json(event_id, EVENTS_LOG_FILE)

    st.subheader("Registrar Evento")
    col_a, col_b = st.columns([2, 3])
    with col_a:
        st.markdown("**Jugador**")
        jugador = st.selectbox("", jugadores, key="jugador_select")
    with col_b:
        st.markdown("**Acción**")
        acciones = ["Gol", "Tiro", "Pase", "Robo", "Falta", "Recuperación", "Pérdida"]
        accion = st.selectbox("", acciones, key="accion_select")

    col_c, col_d, col_e = st.columns(3)
    with col_c:
        st.markdown("**Zona**")
        zona = st.radio("", ["Defensa", "Medio", "Ataque"], horizontal=True, key="zona_radio")
    with col_d:
        st.markdown("**Resultado**")
        resultado = st.radio("", ["Éxito", "Fracaso"], horizontal=True, key="resultado_radio")
    with col_e:
        st.markdown("**Agregar**")
        if st.button("Agregar Evento", key="agregar_evento"):
            entry = {
                "periodo": st.session_state["periodo"],
                "tiempo": f"{mins:02d}:{secs:02d}",
                "jugador": jugador,
                "accion": accion,
                "zona": zona,
                "resultado": resultado,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state["events_log"].append(entry)
            save_json(event_id, EVENTS_LOG_FILE, st.session_state["events_log"])
            st.success("✔️ Evento registrado.")

    st.markdown("### Log de Eventos")
    if st.session_state["events_log"]:
        df = pd.DataFrame(st.session_state["events_log"])
        st.dataframe(df)
    else:
        st.info("No hay eventos registrados aún.")

    st.markdown("---")

    # 6) Exportar CSV / PDF
    filename = st.text_input(
        "Nombre de archivo para exportar",
        value=f"{event_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Exportar CSV"):
            csv_path = get_csv_path(event_id, filename)
            df.to_csv(csv_path, index=False)
            st.success(f"CSV guardado en: {csv_path}")
    with c2:
        if st.button("Exportar PDF"):
            pdf_path = get_pdf_path(event_id, filename)
            # Aquí invocarías tu generador de PDF
            st.success(f"PDF generado en: {pdf_path}")

    st.markdown("---")

    # 7) Navegación final del wizard
    prev, finish = st.columns([1, 1])
    with prev:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with finish:
        if st.button("Terminar Partido"):
            # Limpiar estado y volver al inicio
            st.session_state.update({
                "wizard_step": 1,
                "evento_activo": None,
                "partidos": [],
                "partido_activo": None,
                "events_log": []
            })
            st.rerun()
