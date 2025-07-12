# pages/eventos.py

import streamlit as st
from utils.events import init_event, get_event_file, EVENTS_ROOT, load_json, save_json

def app():
    st.set_page_config(page_title="Paso 1 – Play by Play en Fútbol", layout="wide")
    st.title("Play by Play en Fútbol")
    st.header("⚽ Paso 1: Selección / Creación de Evento")

    # ────────────────────────────────────────────────────────
    # Contenedor centrado para CREAR y CARGAR evento
    # ────────────────────────────────────────────────────────
    with st.container():
        # Tres columnas: margen, contenido, margen
        m1, main, m2 = st.columns([1, 6, 1])
        with main:
            # Dentro del contenido, dos columnas iguales
            col_create, col_load = st.columns(2)

            # ----- CREAR NUEVO EVENTO -----
            with col_create:
                st.subheader("➕ Crear Nuevo Evento")
                eid   = st.text_input("ID (7 caracteres)", max_chars=7)
                name  = st.text_input("Nombre del Evento")
                start = st.text_input("Fecha Inicio (DD/MM/AAAA)")
                end   = st.text_input("Fecha Fin (DD/MM/AAAA)")
                if st.button("Crear Evento", key="crear_evento"):
                    if not eid or len(eid) != 7:
                        st.error("❌ El ID debe tener exactamente 7 caracteres.")
                    else:
                        try:
                            init_event(eid, {"name": name, "start": start, "end": end})
                            st.session_state["evento_activo"] = eid
                            st.success(f"✔️ Evento {eid} creado y activado.")
                        except Exception as e:
                            st.error(f"Error al crear evento: {e}")

            # ----- CARGAR EVENTO EXISTENTE -----
            with col_load:
                st.subheader("📂 Cargar Evento Existente")
                try:
                    opciones = sorted([p.name for p in EVENTS_ROOT.iterdir() if p.is_dir()])
                except Exception:
                    opciones = []
                seleccionado = st.selectbox("Selecciona un Evento", opciones)
                if st.button("Cargar Evento", key="cargar_existente"):
                    if seleccionado:
                        st.session_state["evento_activo"] = seleccionado
                        st.success(f"✔️ Evento {seleccionado} cargado.")
                    else:
                        st.error("⚠️ No hay eventos para cargar.")

    st.markdown("---")

    # ────────────────────────────────────────────────────────
    # Gestión de equipos (paso 1 continúa)
    # ────────────────────────────────────────────────────────
    event_id = st.session_state.get("evento_activo")
    if event_id:
        st.subheader("🏟️ Equipos del Evento")
        # cuatro columnas: margen, tabla, gestión, margen
        ml, col_table, col_manage, mr = st.columns([1, 4, 4, 1])
        with col_table:
            equipos = load_json(event_id, "equipos.json") or []
            if equipos:
                st.markdown("**Equipos registrados:**")
                st.dataframe(equipos, use_container_width=True, height=min(300, 40*len(equipos)))
            else:
                st.info("No hay equipos registrados todavía.")
        with col_manage:
            st.markdown("➕➖ Gestión rápida")
            nuevo = st.text_input("Nuevo equipo", key="nuevo_equipo")
            if st.button("Agregar", key="add_equipo"):
                if not nuevo.strip():
                    st.error("❌ El nombre no puede estar vacío.")
                elif nuevo.strip() in equipos:
                    st.warning("⚠️ Ese equipo ya existe.")
                else:
                    equipos.append(nuevo.strip())
                    save_json(event_id, "equipos.json", equipos)
                    st.success("✔️ Equipo agregado.")
                    st.rerun()

            if equipos:
                to_delete = st.selectbox("Eliminar equipo", equipos, key="del_equipo")
                if st.button("Eliminar", key="del_button"):
                    equipos.remove(to_delete)
                    save_json(event_id, "equipos.json", equipos)
                    st.success("✔️ Equipo eliminado.")
                    st.rerun()

    st.markdown("---")

    # ────────────────────────────────────────────────────────
    # Navegación al siguiente paso
    # ────────────────────────────────────────────────────────
    c_back, c_next, c_empty = st.columns([1,2,1])
    with c_back:
        if st.button("◀ Anterior"):
            # en este paso no hay anterior
            pass
    with c_next:
        if st.button("Siguiente ▶"):
            if not st.session_state.get("evento_activo"):
                st.error("Debes crear o cargar un evento antes de continuar.")
            else:
                st.session_state["wizard_step"] = 2
                st.rerun()
  

