import streamlit as st
from utils.events import load_json, save_json, get_event_file

ALINEACION_FILE = "alineacion.json"
POSICIONES = [
    "Arquero", "Defensa 1", "Defensa 2", "Defensa 3", "Defensa 4",
    "Medio 1", "Medio 2", "Medio 3",
    "Delantero 1", "Delantero 2"
]


def app():
    st.title("📋 Paso 4: Construcción de Alineaciones por Tiempo")

    # Validar evento y partido
    event_id = st.session_state.get("evento_activo")
    partido = st.session_state.get("partido_activo")
    if not event_id or not partido:
        st.error("Debes seleccionar un evento y un partido antes de continuar.")
        return

    equipos = [partido['local'], partido['visitante']]
    plantilla = load_json(event_id, "plantilla.json")

    st.markdown(f"### {equipos[0]} vs {equipos[1]}")

    # --- Seleccionar momento del partido ---
    momento = st.radio("Selecciona el momento del partido:", ["1er Tiempo", "2do Tiempo", "Extra Tiempo"], horizontal=True)

    # --- Diccionario para almacenar alineaciones por equipo y momento ---
    alineaciones_guardadas = load_json(event_id, ALINEACION_FILE)
    if not alineaciones_guardadas:
        alineaciones_guardadas = {equipo: {} for equipo in equipos}

    # --- Bloque de alineación para cada equipo ---
    for equipo in equipos:
        st.subheader(f"Alineación {equipo} - {momento}")
        jugadores_equipo = [j for j in plantilla if j['equipo'] == equipo]
        nombres = [f"{j['nombre']} (#{j['dorsal']})" for j in jugadores_equipo]

        # Mostrar selectbox por posición
        for pos in POSICIONES:
            clave = f"{equipo}_{pos}_{momento}"
            valor_guardado = None
            if momento in alineaciones_guardadas.get(equipo, {}):
                for j in alineaciones_guardadas[equipo][momento]:
                    if j['posicion'] == pos:
                        valor_guardado = j['jugador']
                        break
            st.selectbox(
                f"{pos} ({equipo})", options=[""] + nombres,
                index=nombres.index(valor_guardado) + 1 if valor_guardado in nombres else 0,
                key=clave
            )

    # --- Botón para guardar la alineación de ese tiempo ---
    if st.button("💾 Guardar alineación del momento"):
        for equipo in equipos:
            alineaciones_guardadas[equipo][momento] = []
            for pos in POSICIONES:
                jugador = st.session_state.get(f"{equipo}_{pos}_{momento}")
                if jugador:
                    alineaciones_guardadas[equipo][momento].append({
                        "posicion": pos,
                        "jugador": jugador
                    })
        save_json(event_id, ALINEACION_FILE, alineaciones_guardadas)
        st.success(f"Alineación guardada correctamente para el {momento}.")

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with colB:
        if st.button("Siguiente ▶"):
            st.session_state["wizard_step"] = 5
            st.rerun()
