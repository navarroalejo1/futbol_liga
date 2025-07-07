import streamlit as st
import pandas as pd
from datetime import datetime

def app():
    """
    Paso 4: Partido en Vivo - Cronómetro, Registro de Eventos y Exportación
    """
    st.header("⏱ Paso 4: Partido en Vivo")

    # Verificar evento activo
    event_id = st.session_state.get("evento_activo")
    if not event_id:
        st.error("No hay evento activo. Por favor, regresa al paso 1.")
        return

    st.subheader(f"Evento activo: {event_id}")

    # --- Cronómetro y periodo ---
    if "running" not in st.session_state:
        st.session_state["running"] = False
        st.session_state["start_time"] = None
        st.session_state["elapsed"] = 0.0
        st.session_state["periodo"] = "1er tiempo"

    col_t1, col_t2, col_t3 = st.columns([1,1,1])
    with col_t1:
        if not st.session_state["running"]:
            if st.button("▶ Iniciar"):
                st.session_state["running"] = True
                st.session_state["start_time"] = datetime.now()
        else:
            if st.button("▮ Pausar"):
                st.session_state["running"] = False
                dt = (datetime.now() - st.session_state["start_time"]).total_seconds()
                st.session_state["elapsed"] += dt
    with col_t2:
        if st.button("↺ Reset"):
            st.session_state["running"] = False
            st.session_state["start_time"] = None
            st.session_state["elapsed"] = 0.0
    with col_t3:
        # Mostrar tiempo transcurrido
        total = st.session_state["elapsed"]
        if st.session_state["running"]:
            total += (datetime.now() - st.session_state["start_time"]).total_seconds()
        mins, secs = divmod(int(total), 60)
        st.metric("Tiempo", f"{mins:02d}:{secs:02d}")

    # Selección de periodo (1er/2do tiempo)
    st.markdown("### Periodo")
    st.session_state["periodo"] = st.radio(
        "Selecciona el periodo",
        ["1er tiempo", "2do tiempo"],
        horizontal=True,
        index=0 if st.session_state.get("periodo", "1er tiempo") == "1er tiempo" else 1,
        key="periodo_radio"
    )

    st.markdown("---")

    # --- Registro de eventos optimizado ---
    if "events_log" not in st.session_state:
        st.session_state["events_log"] = []

    st.subheader("Registrar Evento")

    # Ejemplo de jugadores (puedes cargar desde plantilla)
    jugadores = [str(i) for i in range(1, 12)]
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("**Jugador**")
        jugador = st.selectbox("", jugadores, key="jugador_select")

    with col2:
        st.markdown("**Acción**")
        acciones = ["Gol", "Tiro", "Pase", "Robo", "Falta", "Recuperación", "Pérdida"]
        accion = st.selectbox("", acciones, key="accion_select")

    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown("**Zona**")
        zona = st.radio("", ["Defensa", "Medio", "Ataque"], horizontal=True, key="zona_radio")
    with col4:
        st.markdown("**Resultado**")
        resultado = st.radio("", ["Éxito", "Fracaso"], horizontal=True, key="resultado_radio")
    with col5:
        st.markdown("**Agregar**")
        if st.button("Agregar Evento", key="agregar_evento"):
            # Tomar el tiempo actual del cronómetro
            total = st.session_state["elapsed"]
            if st.session_state["running"]:
                total += (datetime.now() - st.session_state["start_time"]).total_seconds()
            mins, secs = divmod(int(total), 60)
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
            st.success("Evento registrado.")

    st.markdown("### Log de Eventos")
    if st.session_state["events_log"]:
        df = pd.DataFrame(st.session_state["events_log"])
        st.dataframe(df)
    else:
        st.info("Aún no hay eventos registrados.")

    st.markdown("---")
    # Exportar CSV / PDF
    from utils.events import get_csv_path, get_pdf_path
    filename = st.text_input("Nombre de archivo para exportar", value=f"{event_id}_{datetime.now().strftime('%Y%m%d_%H%M')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exportar CSV"):
            csv_path = get_csv_path(event_id, filename)
            df.to_csv(csv_path, index=False)
            st.success(f"CSV guardado en: {csv_path}")
    with col2:
        if st.button("Exportar PDF"):
            pdf_path = get_pdf_path(event_id, filename)
            st.success(f"PDF generado en: {pdf_path}")

    st.markdown("---")
    # Botones de navegación final
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with colB:
        if st.button("Terminar Partido"):
            st.session_state["wizard_step"] = 1
            st.session_state["evento_activo"] = None
            st.session_state["partidos"] = []
            st.session_state["events_log"] = []
            st.rerun()