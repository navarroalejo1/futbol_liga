# pages/calendario.py

import streamlit as st
from datetime import datetime
import utils.events as ev

def app():
    st.title("Calendario de partidos")
    """
    Paso 2: Configurar el calendario de partidos para el evento activo
    """
    st.header("📅 Paso 2: Configurar Calendario de Partidos")

    # Verificar que exista un evento activo
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("No hay evento activo. Por favor, regresa al paso 1.")
        return

    st.subheader(f"Evento activo: {event_id}")

    # Cargar partidos existentes
    partidos = ev.load_partidos(event_id)
    st.markdown("### Partidos existentes")
    if partidos:
        st.table(partidos)
    else:
        st.info("No hay partidos programados aún.")

    st.markdown("---")
    st.subheader("Agregar nuevo partido")

    # Formulario de nuevo partido
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha = st.date_input("Fecha del Partido")
        hora  = st.time_input("Hora del Partido")
    with col2:
        local      = st.text_input("Equipo Local")
        visitante  = st.text_input("Equipo Visitante")
    with col3:
        competicion = st.text_input("Competición")
        cancha      = st.text_input("Cancha")

    # Guardar partido
    if st.button("Guardar Partido"):
        nueva_fecha = fecha.strftime("%d/%m/%Y")
        nueva_hora  = hora.strftime("%H:%M")
        nuevo = {
            "fecha":      nueva_fecha,
            "hora":       nueva_hora,
            "local":      local,
            "visitante":  visitante,
            "competicion": competicion,
            "cancha":     cancha
        }
        partidos.append(nuevo)
        ev.save_partidos(event_id, partidos)
        st.success("Partido agregado correctamente.")
        st.rerun()

    st.markdown("---")
    # Navegación Anterior / Siguiente
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with colB:
        if st.button("Siguiente ▶"):
            if not ev.load_partidos(event_id):
                st.error("Debes agregar al menos un partido antes de continuar.")
            else:
                st.session_state["partidos"] = ev.load_partidos(event_id)
                st.session_state["wizard_step"] = 3
                st.rerun()
