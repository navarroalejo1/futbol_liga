# pages/calendario.py

import streamlit as st
import json
import uuid
from datetime import datetime
from utils.events import get_event_file, load_json, save_json

# Archivos asociados al evento
PARTIDOS_FILE = "partidos.json"
EQUIPOS_FILE  = "equipos.json"

def app():
    st.title("📅 Paso 2: Calendario de Partidos")

    # --- Validar evento activo ---
    # Aumentar el tamaño de la letra usando CSS en Streamlit
    st.markdown(
        """
        <style>
        .stApp {
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("❌ No hay evento activo. Regresa al Paso 1 para crear o cargar uno.")
        return

    st.subheader(f"Evento activo: {event_id}")

    # --- Cargar o inicializar partidos existentes ---
    partidos_path = get_event_file(event_id, PARTIDOS_FILE)
    try:
        partidos = load_json(event_id, PARTIDOS_FILE) or []
    except:
        partidos = []

    # --- Asignar ID a los que no lo tienen (migra) ---
    migrated = False
    for p in partidos:
        if "id" not in p:
            p["id"] = uuid.uuid4().hex
            migrated = True
    if migrated:
        save_json(event_id, PARTIDOS_FILE, partidos)

    # --- Mostrar tabla de partidos ---
    if partidos:
        st.markdown("### Partidos existentes")
        st.dataframe(
            [{**p, "mostrar": f"{p['fecha']} {p['hora']} — {p['local']} vs {p['visitante']}"} 
             for p in partidos],
            use_container_width=True
        )
    else:
        st.info("Aún no se ha programado ningún partido.")

    # --- Seleccionar partido activo ---
    if partidos:
        opciones = {f"{p['fecha']} {p['hora']} — {p['local']} vs {p['visitante']}": p["id"] 
                    for p in partidos}
        sel_str = st.selectbox("Selecciona un partido:", options=list(opciones.keys()))
        partido_id = opciones[sel_str]
        partido = next(p for p in partidos if p["id"] == partido_id)
        st.session_state["partido_activo"] = partido
        st.success(f"Partido seleccionado: {sel_str}")

        # --- Eliminar partido seleccionado ---
        if st.button("🗑️ Borrar partido"):
            partidos = [p for p in partidos if p["id"] != partido_id]
            save_json(event_id, PARTIDOS_FILE, partidos)
            st.success("✔️ Partido eliminado.")
            st.rerun()
    else:
        st.session_state["partido_activo"] = None

    st.markdown("---")
    st.subheader("➕ Agregar nuevo partido")

    # --- Formulario compacto: Fecha y Hora en una fila ---
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", key="fecha_input")
    with col2:
        hora = st.time_input("Hora", key="hora_input")

    # --- Selección de equipos y datos del partido ---
    equipos = load_json(event_id, EQUIPOS_FILE) or []
    col3, col4, col5 = st.columns(3)
    with col3:
        local = st.selectbox("Equipo Local", options=equipos, key="local_input") if equipos else st.text_input("Equipo Local", key="local_input")
    with col4:
        visitante = (
            st.selectbox("Equipo Visitante", options=[e for e in equipos if e != local], key="visitante_input")
            if equipos else st.text_input("Equipo Visitante", key="visitante_input")
        )
    with col5:
        competicion = st.text_input("Competición", key="competicion_input")
        cancha      = st.text_input("Cancha", key="cancha_input")

    # --- Guardar nuevo partido con ID único ---
    if st.button("Guardar Partido", key="guardar_partido"):
        errores = []
        if local == visitante:
            errores.append("El local y el visitante no pueden ser el mismo.")
        if not fecha or not hora:
            errores.append("Debes indicar fecha y hora.")
        if not local.strip() or not visitante.strip():
            errores.append("Es obligatorio indicar ambos equipos.")
        if errores:
            for e in errores:
                st.error("❌ " + e)
        else:
            nuevo = {
                "id":          uuid.uuid4().hex,
                "fecha":       fecha.strftime("%d/%m/%Y"),
                "hora":        hora.strftime("%H:%M"),
                "local":       local.strip(),
                "visitante":   visitante.strip(),
                "competicion": competicion.strip(),
                "cancha":      cancha.strip()
            }
            partidos.append(nuevo)
            save_json(event_id, PARTIDOS_FILE, partidos)
            st.success("✔️ Partido agregado con éxito.")
            st.rerun()

    st.markdown("---")
    # --- Navegación al siguiente paso ---
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior", key="cal_prev"):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with colB:
        if st.button("Siguiente ▶", key="cal_next"):
            if not partidos or st.session_state.get("partido_activo") is None:
                st.error("⚠️ Agrega y selecciona un partido antes de continuar.")
            else:
                st.session_state["wizard_step"] = 3
                st.rerun()
