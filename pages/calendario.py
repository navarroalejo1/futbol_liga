# pages/calendario.py

import streamlit as st
from datetime import datetime
import json
from pathlib import Path

"""
    Paso 2: Configurar el calendario de partidos para el evento activo
    """

# Importamos nuestras utilidades genéricas
from utils.events import (
    get_event_file,
    load_json,
    save_json
)

# Nombre de archivo en el que guardamos los partidos
PARTIDOS_FILE = "partidos.json"
PLANTILLA_FILE = "plantilla.json"

def app():
    """
    Paso 2: Configurar el calendario de partidos para el evento activo
    """
    st.title("📅 Paso 2: Calendario de Partidos")

    # 1) Validar que exista un evento activo en sesión
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("❌ No hay evento activo. Regresa al Paso 1 para crear o cargar uno.")
        return

    st.subheader(f"Evento activo: {event_id}")

    # 2) Cargar partidos existentes desde JSON
    partidos = load_json(event_id, PARTIDOS_FILE)
    st.markdown("### Partidos existentes")
    if partidos:
        st.table(partidos)
    else:
        st.info("Aún no se ha programado ningún partido.")

    # 3) Seleccionar uno de los partidos cargados para los siguientes pasos
    if partidos:
        opciones = [
            f"{i+1}. {p['fecha']} {p['hora']} — {p['local']} vs {p['visitante']} ({p['competicion']})"
            for i, p in enumerate(partidos)
        ]
        idx = st.selectbox(
            "Selecciona un partido para trabajar a continuación:",
            options=list(range(len(opciones))),
            format_func=lambda i: opciones[i],
            key="partido_select"
        )
        # Guardamos toda la estructura del partido en session_state
        st.session_state["partido_activo"] = partidos[idx]
        st.success(f"Partido seleccionado: {opciones[idx]}")
    else:
        st.session_state["partido_activo"] = None

    st.markdown("---")
    st.subheader("➕ Agregar nuevo partido")

    # 4) Sugerir equipos a partir de la plantilla de jugadores
    #    en lugar de inputs de texto libres
    plantilla_path = get_event_file(event_id, PLANTILLA_FILE)
    equipos_plantilla = []
    if plantilla_path.exists():
        with plantilla_path.open("r", encoding="utf-8") as f:
            plantilla = json.load(f)
        # Extraemos equipos únicos (y no vacíos)
        equipos_plantilla = sorted(
            {j["equipo"].strip() for j in plantilla if j.get("equipo") and j["equipo"].strip() != "-"}
        )

    # 5) Formulario de nuevo partido usando selectbox para equipos
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha = st.date_input("Fecha")
        hora  = st.time_input("Hora")
    with col2:
        # Si no tenemos plantilla, se habilitan como texto libre
        if equipos_plantilla:
            local     = st.selectbox("Equipo Local", options=equipos_plantilla)
            # El visitante no puede ser el mismo que el local
            visitante = st.selectbox(
                "Equipo Visitante",
                options=[e for e in equipos_plantilla if e != local]
            )
        else:
            local     = st.text_input("Equipo Local")
            visitante = st.text_input("Equipo Visitante")
    with col3:
        competicion = st.text_input("Competición")
        cancha      = st.text_input("Cancha")

    # 6) Botón para guardar, con validaciones
    if st.button("Guardar Partido"):
        errores = []
        # Validar que no se inscriban equipos idénticos
        if local == visitante:
            errores.append("El local y el visitante no pueden ser el mismo equipo.")
        # Validar que fecha y hora existan
        if not fecha or not hora:
            errores.append("Debes indicar fecha y hora del partido.")
        # Validar campos obligatorios
        if not local.strip() or not visitante.strip():
            errores.append("Es obligatorio indicar ambos equipos.")
        if errores:
            for e in errores:
                st.error("❌ " + e)
        else:
            # Formatear y añadir
            nuevo = {
                "fecha":      fecha.strftime("%d/%m/%Y"),
                "hora":       hora.strftime("%H:%M"),
                "local":      local.strip(),
                "visitante":  visitante.strip(),
                "competicion": competicion.strip(),
                "cancha":     cancha.strip()
            }
            partidos.append(nuevo)
            # Persistir en disco
            save_json(event_id, PARTIDOS_FILE, partidos)
            st.success("✔️ Partido agregado con éxito.")
            # Recargar para actualizar tabla/selector
            st.rerun()

    st.markdown("---")
    # 7) Navegación entre pasos
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with colB:
        if st.button("Siguiente ▶"):
            # No avanzar si no hay partido seleccionado
            if not partidos or st.session_state.get("partido_activo") is None:
                st.error("⚠️ Agrega y selecciona un partido antes de continuar.")
            else:
                st.session_state["partidos"] = partidos
                st.session_state["wizard_step"] = 3
                st.rerun()
