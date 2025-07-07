import streamlit as st
import utils.events as ev

def app():
    ## Título principal del paso 1
    st.header("⚽ Paso 1: Selección / Creación de Evento")

    ## Creamos dos columnas: una para crear evento, otra para cargar existente
    col1, col2 = st.columns([3, 2])

    ## --- Columna para crear un nuevo evento ---
    with col1:
        ## Campos de entrada para los datos del evento
        eid = st.text_input("ID del Evento (7 caracteres)", max_chars=7)
        name = st.text_input("Nombre del Evento")
        start = st.text_input("Fecha de Inicio (DD/MM/AAAA)")
        end = st.text_input("Fecha de Fin (DD/MM/AAAA)")

        ## Botón para crear el evento
        if st.button("Crear Evento", key="crear_evento"):
            ## Validamos que el ID tenga exactamente 7 caracteres
            if not eid or len(eid) != 7:
                st.error("El ID debe tener exactamente 7 caracteres.")
            else:
                try:
                    ## Llamamos a la función para inicializar el evento (guardar en disco)
                    ev.init_event(eid, {"name": name, "start": start, "end": end})
                    ## Guardamos el evento como activo en la sesión
                    st.session_state["evento_activo"] = eid
                    st.success(f"Evento {eid} creado y activado correctamente.")
                except Exception as e:
                    st.error(f"Error al crear evento: {e}")

    ## --- Columna para cargar un evento existente ---
    with col2:
        st.subheader("Cargar Evento Existente")
        try:
            ## Listamos los eventos existentes leyendo las carpetas en EVENTS_ROOT
            eventos = sorted([p.name for p in ev.EVENTS_ROOT.iterdir() if p.is_dir()])
        except Exception:
            eventos = []
        ## Selector para elegir un evento existente
        selected = st.selectbox("Selecciona un Evento", options=eventos)
        ## Botón para cargar el evento seleccionado
        if st.button("Cargar Existente", key="cargar_existente"):
            if selected:
                ## Guardamos el evento como activo y avanzamos al paso 2
                st.session_state["evento_activo"] = selected
                st.session_state["wizard_step"] = 2
                st.success(f"Evento {selected} cargado y activado.")
                st.rerun()
            else:
                st.error("No hay eventos disponibles para cargar.")

    ## Línea divisoria
    st.markdown("---")

    ## --- Navegación al siguiente paso ---
    colA, colB = st.columns([1, 1])
    with colA:
        ## Botón para avanzar al paso 2 (calendario)
        if st.button("Siguiente ▶", key="siguiente_evento"):
            ## Validamos que haya un evento activo antes de avanzar
            if not st.session_state.get("evento_activo"):
                st.error("Debes crear o cargar un evento antes de continuar.")
            else:
                st.session_state["wizard_step"] = 2
                st.rerun()
    with colB:
        st.write("")  ## Solo para equilibrar el diseño de columnas