import streamlit as st
from pathlib import Path

# Importamos nuestras utilidades genéricas
import page.eventos as eventos
import page.calendario as calendario
import page.planillas as planillas
import page.alineacion as alineacion
import page.partido_en_vivo as partido_en_vivo

st.set_page_config(
    page_title="Fútbol Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

## Diccionario de pasos: número -> (nombre, función)
steps = {
    1: ("🎟 Evento", eventos.app),
    2: ("📅 Calendario", calendario.app),
    3: ("👥 Plantillas", planillas.app),
    4: ("📋 Alineaciones", alineacion.app),
    5: ("⏱ Partido En Vivo", partido_en_vivo.app)
}

## Inicializamos wizard_step si no existe
if "wizard_step" not in st.session_state:
    st.session_state["wizard_step"] = 1

## Sidebar: mostrar los pasos y permitir saltar manualmente (opcional)
step_names = [v[0] for v in steps.values()]
current_idx = st.session_state["wizard_step"] - 1

# Sidebar para navegación manual (opcional)
selection = st.sidebar.radio("Ir a paso:", step_names, index=current_idx)
# Sincronizamos wizard_step con la selección del sidebar
for k, v in steps.items():
    if v[0] == selection:
        st.session_state["wizard_step"] = k

st.sidebar.markdown("---")
st.sidebar.write(f"Paso actual: **{steps[st.session_state['wizard_step']][0]}**")
st.sidebar.markdown("")

## Ejecuta la función correspondiente al paso actual
steps[st.session_state["wizard_step"]][1]()