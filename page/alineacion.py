# pages/alineacion.py

import streamlit as st
import os
from PIL import Image
from utils.events import load_json, save_json, get_event_file

# Archivo donde se guardan las alineaciones de dorsales por esquema
ALINEACION_FILE = "alineacion.json"
# Los tres momentos para los que guardamos formaciones
TIEMPOS = ["Inicial", "2do TIEMPO", "EXTRA TIEMPO"]
# Rutas relativas a la carpeta raíz del proyecto
SHIRT_PATH_GOALIE = "camisetas/camiseta_arquero.png"
SHIRT_PATH_FIELD  = "camisetas/camiseta_blanca.png"

def camiseta_html(ruta_img: str, numero: str) -> str:
    """
    Devuelve un fragmento HTML que muestra una camiseta y superpone el dorsal.
    """
    return f"""
    <div style='position: relative; display: inline-block; margin: 2px;'>
      <img src='{ruta_img}' width='55'>
      <div style='
          position: absolute;
          top: 12px; left: 0; width: 100%;
          text-align: center;
          font-weight: bold;
          font-size: 18px;
          color: {"white" if ruta_img.endswith("arquero.png") else "black"};
      '>{numero}</div>
    </div>
    """

def app():
    st.title("📋 Paso 4: Construcción de Alineaciones")

    # 1) Validar contexto
    event_id = st.session_state.get("evento_activo")
    partido  = st.session_state.get("partido_activo")
    if not event_id or not partido:
        st.error("Debes crear/cargar un evento y seleccionar un partido antes de continuar.")
        return

    # 2) Preparar datos
    equipos  = [partido["local"], partido["visitante"]]
    plantilla = load_json(event_id, "plantilla.json")
    # Dorsales disponibles por equipo
    dorsales = {
        equipo: [str(j["dorsal"]) for j in plantilla if j["equipo"] == equipo]
        for equipo in equipos
    }

    # 3) Selector de tiempo y nombre de esquema
    tiempo = st.radio("Selecciona el tiempo:", TIEMPOS, horizontal=True)
    nombre = st.text_input("Nombre del esquema", value=tiempo)

    # 4) Cargar o inicializar alineaciones
    alineaciones = load_json(event_id, ALINEACION_FILE)
    if not isinstance(alineaciones, dict):
        alineaciones = {}
    if nombre not in alineaciones:
        # Cada equipo tiene 11 slots (None si vacíos)
        alineaciones[nombre] = {eq: [None]*11 for eq in equipos}

    st.markdown("---")
    col_local, col_visitante = st.columns(2)

    # 5) Para cada equipo, 11 selectboxes y render HTML
    for idx, equipo in enumerate(equipos):
        with (col_local if idx == 0 else col_visitante):
            st.subheader(equipo)
            # Prepara el HTML de la formación
            html = ""
            for slot in range(11):
                key = f"{equipo}_{slot}_{nombre}"
                # Valor guardado por defecto
                default = alineaciones[nombre][equipo][slot] or "-"
                # Selectbox para elegir dorsal
                elegido = st.selectbox(
                    f"Posición {slot+1}",
                    options=["-"] + dorsales[equipo],
                    index=(dorsales[equipo].index(default) + 1) if default in dorsales[equipo] else 0,
                    key=key
                )
                # Actualizar en memoria
                alineaciones[nombre][equipo][slot] = elegido if elegido != "-" else None

                # Elegir imagen: arquero es slot 0
                is_gk = (slot == 0)
                ruta = SHIRT_PATH_GOALIE if is_gk else SHIRT_PATH_FIELD
                # Ruta absoluta para render
                ruta_abs = ruta if os.path.exists(ruta) else os.path.join("..", ruta)
                num = elegido if elegido != "-" else ""
                html += camiseta_html(ruta_abs, num)

            # Mostrar la fila de 11 camisetas
            st.markdown(f"<div style='display: flex; flex-wrap: wrap;'>{html}</div>", unsafe_allow_html=True)

    # 6) Guardar la alineación
    st.markdown("---")
    if st.button("💾 Guardar alineación"):
        save_json(event_id, ALINEACION_FILE, alineaciones)
        st.success(f"Alineación '{nombre}' guardada correctamente.")

    # 7) Navegación del wizard
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with c2:
        if st.button("Siguiente ▶"):
            st.session_state["wizard_step"] = 5
            st.rerun()
