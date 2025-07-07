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
PARTIDOS_FILE   = "partidos.json"
PLANTILLA_FILE  = "plantilla.json"


def app():
    """
    Paso 2: Configurar el calendario de partidos para el evento activo
    """
    st.title("📅 Paso 2: Calendario de Partidos")

    # -- Inyectar CSS para colorear solo los botones de navegación --
    st.markdown("""
    <style>
      .nav-buttons .stButton>button:first-child {
        background-color: orange !important;
        color: white !important;
        border: none !important;
      }
      .nav-buttons .stButton>button:last-child {
        background-color: #007BFF !important;
        color: white !important;
        border: none !important;
      }
      .nav-buttons .stButton>button:hover {
        opacity: 0.9 !important;
      }
    </style>
    """, unsafe_allow_html=True)

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

    # --- Navegación entre pasos (primera sección) ---
    st.markdown("<div class='nav-buttons'>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior", key="cal_prev_1"):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with colB:
        if st.button("Siguiente ▶", key="cal_next_1"):
            # No avanzar si no hay partido seleccionado
            if not partidos or st.session_state.get("partido_activo") is None:
                st.error("⚠️ Agrega y selecciona un partido antes de continuar.")
            else:
                st.session_state["partidos"]    = partidos
                st.session_state["wizard_step"] = 3
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("➕ Agregar nuevo partido")

    # 4) Sugerir equipos a partir de la plantilla de jugadores
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
        fecha = st.date_input("Fecha", key="fecha_input")
        hora  = st.time_input("Hora", key="hora_input")
    with col2:
        if equipos_plantilla:
            local     = st.selectbox("Equipo Local",    options=equipos_plantilla, key="local_input")
            visitante = st.selectbox(
                "Equipo Visitante",
                options=[e for e in equipos_plantilla if e != local],
                key="visitante_input"
            )
        else:
            local     = st.text_input("Equipo Local", key="local_input")
            visitante = st.text_input("Equipo Visitante", key="visitante_input")
    with col3:
        competicion = st.text_input("Competición", key="competicion_input")
        cancha      = st.text_input("Cancha", key="cancha_input")

    # 6) Botón para guardar, con validaciones
    if st.button("Guardar Partido", key="guardar_partido"):
        errores = []
        if local == visitante:
            errores.append("El local y el visitante no pueden ser el mismo equipo.")
        if not fecha or not hora:
            errores.append("Debes indicar fecha y hora del partido.")
        if not local.strip() or not visitante.strip():
            errores.append("Es obligatorio indicar ambos equipos.")
        if errores:
            for e in errores:
                st.error("❌ " + e)
        else:
            nuevo = {
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
    # --- Navegación entre pasos (segunda sección) ---
    st.markdown("<div class='nav-buttons'>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior", key="cal_prev_2"):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with colB:
        if st.button("Siguiente ▶", key="cal_next_2"):
            if not partidos or st.session_state.get("partido_activo") is None:
                st.error("⚠️ Agrega y selecciona un partido antes de continuar.")
            else:
                st.session_state["partidos"]    = partidos
                st.session_state["wizard_step"] = 3
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
