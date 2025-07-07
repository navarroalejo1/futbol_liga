# page/planillas.py

import streamlit as st
import json
from pathlib import Path

from utils.constants import POSICIONES
from utils.events import get_event_file, load_json, save_json

# Nombres de archivos JSON
PLANTILLA_FILE = "plantilla.json"
PARTIDOS_FILE  = "partidos.json"

def app():
    """
    Paso 3: Gestión de plantillas de jugadores para el evento activo.
    - Muestra las plantillas de Local y Visitante por separado.
    - Permite eliminar cualquier jugador de la plantilla del partido.
    - Permite añadir nuevos jugadores con validaciones avanzadas.
    """
    st.title("👥 Paso 3: Gestión de Plantillas")

    # 1) Validar evento activo
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("❌ No hay evento activo. Vuelve al Paso 1 para crear o cargar uno.")
        return

    # 2) Rutas a JSON de plantilla y partidos
    plantilla_path = get_event_file(event_id, PLANTILLA_FILE)
    partidos_path  = get_event_file(event_id, PARTIDOS_FILE)

    # 3) Cargar la lista completa de jugadores
    plantilla = load_json(event_id, PLANTILLA_FILE)

    # --- Mostrar partido activo y filtrar jugadores ---
    partido = st.session_state.get("partido_activo")
    if partido:
        st.markdown(f"### Partido activo: **{partido['local']} vs {partido['visitante']}**")
        # Normalizamos a minúsculas para comparar
        equipos_partido = [
            partido['local'].strip(),
            partido['visitante'].strip()
        ]
        equipos_lower = [e.lower() for e in equipos_partido]

        # Filtramos todos los jugadores que pertenecen a los equipos de este partido
        plantilla_filtrada = [
            j for j in plantilla
            if j['equipo'].strip().lower() in equipos_lower
        ]

        # 3a) Separar y ordenar por dorsal
        plantilla_local = sorted(
            [j for j in plantilla_filtrada if j['equipo'].strip().lower() == equipos_lower[0]],
            key=lambda x: x['dorsal']
        )
        plantilla_visitante = sorted(
            [j for j in plantilla_filtrada if j['equipo'].strip().lower() == equipos_lower[1]],
            key=lambda x: x['dorsal']
        )
    else:
        st.warning("No hay partido activo seleccionado. Selecciona un partido en el Paso 2.")
        plantilla_filtrada   = []
        plantilla_local      = []
        plantilla_visitante  = []
        equipos_partido      = []

    # --- Mostrar planillas en paralelo ---
    st.subheader("📋 Jugadores en plantilla")
    col_local, col_visitante = st.columns(2)
    with col_local:
        st.markdown(f"#### {equipos_partido[0] if equipos_partido else 'Equipo Local'}")
        if plantilla_local:
            st.table(plantilla_local)
        else:
            st.info("Sin jugadores.")
    with col_visitante:
        st.markdown(f"#### {equipos_partido[1] if equipos_partido else 'Equipo Visitante'}")
        if plantilla_visitante:
            st.table(plantilla_visitante)
        else:
            st.info("Sin jugadores.")

    # --- Eliminar jugador de la plantilla filtrada ---
    if plantilla_filtrada:
        idx_borrar = st.selectbox(
            "Selecciona un jugador para eliminar:",
            options=list(range(len(plantilla_filtrada))),
            format_func=lambda i: f"{plantilla_filtrada[i]['nombre']} ({plantilla_filtrada[i]['equipo']})",
            key="idx_borrar"
        )
        if st.button("🗑️ Eliminar jugador seleccionado"):
            jugador = plantilla_filtrada[idx_borrar]
            # Encontrar índice real en la lista original
            idx_real = next(i for i, j in enumerate(plantilla) if j == jugador)
            plantilla.pop(idx_real)
            save_json(event_id, PLANTILLA_FILE, plantilla)
            st.success("✔️ Jugador eliminado.")
            st.rerun()
    else:
        st.info("Aún no se han agregado jugadores para este partido.")

    st.markdown("---")
    st.subheader("➕ Agregar nuevo jugador")

    # 4) Formulario para agregar nuevos jugadores
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre del Jugador", key="in_nombre")
        dorsal = st.text_input("Dorsal", key="in_dorsal")
    with col2:
        posicion = st.selectbox(
            "Posición", options=POSICIONES,
            help="Selecciona la posición del jugador",
            key="in_posicion"
        )
    with col3:
        equipo = st.selectbox(
            "Equipo",
            options=equipos_partido,
            help="Selecciona el equipo al que pertenece el jugador",
            key="in_equipo"
        )

    if st.button("Añadir Jugador"):
        errores = []
        # Validación nombre
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        # Validación dorsal
        if not dorsal.isdigit():
            errores.append("El dorsal debe ser un número entero.")
        else:
            dorsal_int = int(dorsal)
            # Asegurar unicidad dentro del equipo
            dorsales_equipo = {
                j['dorsal']
                for j in plantilla_filtrada
                if j['equipo'].strip().lower() == equipo.strip().lower()
            }
            if dorsal_int in dorsales_equipo:
                errores.append(f"El dorsal {dorsal_int} ya está en uso en {equipo}.")
        # Validación posición
        if posicion not in POSICIONES:
            errores.append("Debes seleccionar una posición válida.")
        # Validación equipo
        if not equipo or equipo not in equipos_partido:
            errores.append("Debes seleccionar un equipo válido para este partido.")

        if errores:
            st.error("\n".join(f"❌ {e}" for e in errores))
        else:
            nuevo = {
                "nombre":   nombre.strip(),
                "dorsal":   dorsal_int,
                "posicion": posicion,
                "equipo":   equipo.strip()
            }
            plantilla.append(nuevo)
            save_json(event_id, PLANTILLA_FILE, plantilla)
            st.success(f"✔️ Jugador {nombre.strip()} agregado.")
            st.rerun()

    # -----------------------------------------------
    # 5) Navegación del wizard (Anterior / Siguiente)
    # -----------------------------------------------
    st.markdown("---")
    prev_col, next_col = st.columns(2)
    with prev_col:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 2
            st.rerun()
    with next_col:
        if st.button("Siguiente ▶"):
            if not plantilla_filtrada:
                st.error("⚠️ Agrega al menos un jugador para este partido antes de continuar.")
            else:
                st.session_state["wizard_step"] = 4
                st.rerun()
