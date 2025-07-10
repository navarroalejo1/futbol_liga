import streamlit as st
import json
from utils.events import init_event, get_event_file, EVENTS_ROOT, load_json, save_json

def app():
    ## ============================================================
    ## PASO 1: CREACIÓN O CARGA DE EVENTO Y GESTIÓN DE EQUIPOS
    ## ============================================================

    st.header("⚽ Paso 1: Selección / Creación de Evento")

    ## Creamos dos columnas: una para crear un nuevo evento, otra para cargar uno existente
    col1, col2 = st.columns([3, 2])

    ## ------------------------------------------------------------
    ## BLOQUE 1: CREAR NUEVO EVENTO
    ## ------------------------------------------------------------
    with col1:
        eid = st.text_input("ID del Evento (7 caracteres)", max_chars=7)
        name = st.text_input("Nombre del Evento")
        start = st.text_input("Fecha de Inicio (DD/MM/AAAA)")
        end = st.text_input("Fecha de Fin (DD/MM/AAAA)")

        if st.button("Crear Evento", key="crear_evento"):
            if not eid or len(eid) != 7:
                st.error("❌ El ID debe tener exactamente 7 caracteres.")
            else:
                try:
                    ## Inicializa la carpeta del evento y guarda los metadatos
                    init_event(eid, {"name": name, "start": start, "end": end})
                    ## Guarda el evento como activo en la sesión
                    st.session_state["evento_activo"] = eid
                    st.success(f"✔️ Evento {eid} creado y activado correctamente.")
                except Exception as e:
                    st.error(f"Error al crear evento: {e}")

    ## ------------------------------------------------------------
    ## BLOQUE 2: CARGAR EVENTO EXISTENTE
    ## ------------------------------------------------------------
    with col2:
        st.subheader("Cargar Evento Existente")
        try:
            ## Lista las carpetas de eventos existentes
            eventos = sorted([p.name for p in EVENTS_ROOT.iterdir() if p.is_dir()])
        except Exception:
            eventos = []

        selected = st.selectbox("Selecciona un Evento", options=eventos)

        if st.button("Cargar Existente", key="cargar_existente"):
            if selected:
                ## Guarda el evento como activo en la sesión
                st.session_state["evento_activo"] = selected
                st.success(f"✔️ Evento {selected} cargado y activado.")
                ## NOTA: No avanzamos automáticamente al paso 2 para permitir gestión de equipos
            else:
                st.error("No hay eventos disponibles para cargar.")

    st.markdown("---")

    ## ------------------------------------------------------------
    ## BLOQUE 3: GESTIÓN DE EQUIPOS DEL EVENTO ACTIVO
    ## ------------------------------------------------------------
    event_id = st.session_state.get("evento_activo")
    if event_id:
        st.subheader("🏟️ Equipos del Evento")

        ## Ruta al archivo de equipos
        equipos_path = get_event_file(event_id, "equipos.json")

        ## Cargar equipos desde archivo (si existe)
        try:
            equipos = load_json(event_id, "equipos.json")
        except:
            equipos = []

        ## Mostrar tabla de equipos registrados
        if equipos:
            st.markdown("**Equipos registrados:**")
            st.dataframe(equipos, use_container_width=True, height=min(300, 40 * len(equipos)))
        else:
            st.info("Aún no se han registrado equipos.")

        ## --------------------------------------------------------
        ## BLOQUE 3A: GESTIÓN RÁPIDA EN DOS COLUMNAS
        ## --------------------------------------------------------
        st.markdown("### ➕➖ Gestión rápida de equipos")
        col_add, col_del = st.columns(2)

        ## --- Columna izquierda: Agregar equipo ---
        with col_add:
            nuevo_equipo = st.text_input("Agregar equipo", key="nuevo_equipo")
            if st.button("➕", key="btn_add_equipo"):
                if not nuevo_equipo.strip():
                    st.error("❌ El nombre no puede estar vacío.")
                elif nuevo_equipo.strip() in equipos:
                    st.warning("⚠️ Ese equipo ya está registrado.")
                else:
                    equipos.append(nuevo_equipo.strip())
                    save_json(event_id, "equipos.json", equipos)
                    st.success("✔️ Equipo agregado.")
                    st.rerun()

        ## --- Columna derecha: Eliminar equipo ---
        with col_del:
            if equipos:
                equipo_borrar = st.selectbox("Eliminar equipo", equipos, key="equipo_borrar")
                if st.button("🗑️", key="btn_del_equipo"):
                    equipos.remove(equipo_borrar)
                    save_json(event_id, "equipos.json", equipos)
                    st.success("✔️ Equipo eliminado.")
                    st.rerun()

    ## ------------------------------------------------------------
    ## BLOQUE 4: NAVEGACIÓN AL SIGUIENTE PASO
    ## ------------------------------------------------------------
    st.markdown("---")
    colA, colB = st.columns([1, 1])

    with colA:
        if st.button("Siguiente ▶", key="siguiente_evento"):
            if not st.session_state.get("evento_activo"):
                st.error("Debes crear o cargar un evento antes de continuar.")
            else:
                st.session_state["wizard_step"] = 2
                st.rerun()

    with colB:
        st.write("")  # Espaciador visual para mantener simetría
