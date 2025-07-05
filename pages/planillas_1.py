# pages/planillas.py

import streamlit as st
import json
from pathlib import Path
from utils.constants import POSICIONES

# Ruta al directorio de datos de eventos
BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_ROOT = BASE_DIR / "data" / "events"


def app():
    """
    Paso 3: Gestión de plantillas de jugadores para el evento activo
    """
    st.header("👥 Paso 3: Gestión de Plantillas")

    # Verificar evento activo
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("No hay evento activo. Por favor, regresa al paso 1.")
        return

    # Directorio del evento y archivo de plantilla
    event_dir = EVENTS_ROOT / event_id
    plantilla_file = event_dir / "plantilla.json"

    # Carga o inicializa plantilla
    if plantilla_file.exists():
        with open(plantilla_file, "r", encoding="utf-8") as f:
            plantilla = json.load(f)
    else:
        plantilla = []

    # Mostrar plantilla actual
    st.subheader("Jugadores en plantilla")
    if plantilla:
        st.table(plantilla)
    else:
        st.info("Aún no se han agregado jugadores.")

    st.markdown("---")
    st.subheader("Agregar nuevo jugador")

    # Formulario de jugador
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre del Jugador")
        dorsal = st.text_input("Dorsal")
    with col2:
        posicion = st.selectbox(
            "Posición",
            options=POSICIONES,
            help="Selecciona la posición del jugador"
        )
    with col3:
        equipo = st.text_input("Equipo")

    # Botón para añadir
    if st.button("Añadir Jugador"):
        errores = []
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not dorsal.isdigit():
            errores.append("El dorsal debe ser un número.")
        if posicion not in POSICIONES:
            errores.append("Debes seleccionar una posición válida.")
        if errores:
            for e in errores:
                st.error(e)
        else:
            nuevo_jugador = {
                "nombre": nombre.strip(),
                "dorsal": int(dorsal),
                "posicion": posicion,
                "equipo": equipo.strip() or "-"
            }
            plantilla.append(nuevo_jugador)
            with open(plantilla_file, "w", encoding="utf-8") as f:
                json.dump(plantilla, f, ensure_ascii=False, indent=2)
            st.success(f"Jugador {nombre} agregado.")
            st.rerun()

    st.markdown("---")
    # Navegación
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 2
            st.rerun()
    with colB:
        if st.button("Siguiente ▶"):
            if len(plantilla) < 1:
                st.error("Agrega al menos un jugador antes de continuar.")
            else:
                st.session_state["wizard_step"] = 4
                st.rerun()
