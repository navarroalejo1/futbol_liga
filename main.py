
import streamlit as st

st.set_page_config(
    page_title="Fútbol Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Fútbol Analytics Pro")
st.sidebar.markdown("---")
st.sidebar.info("Seleccione un módulo:")

# Mostrar los módulos disponibles
modules = {
    "👥 Plantillas": "1_👥_Plantillas",
    "📅 Calendario": "2_📅_Calendario",
    "⏱ Partido en Vivo": "3_⏱_Partido_En_Vivo"
}

selection = st.sidebar.radio("Ir a:", list(modules.keys()))

# Redirigir al módulo seleccionado
page = modules[selection]
st.switch_page(f"app/pages/{page}.py")
