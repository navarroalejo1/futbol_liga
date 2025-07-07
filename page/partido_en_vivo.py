import streamlit as st
from datetime import datetime
from utils.events import load_json, save_json

# ———————————————————
# 1) Setup básico
# ———————————————————
st.set_page_config(page_title="⏱ Paso 5: Partido en Vivo", layout="wide")
st.title("⏱ Paso 5: Partido en Vivo")

# ———————————————————
# 2) Inyección de CSS (hexágonos, btn-panel…)
# ———————————————————
st.markdown("""
  <style>
    /* Hexágonos */
    .hexagon { width:80px; height:46.19px; background:#0d6efd; position:relative; margin:4px; display:inline-block; }
    .hexagon:before, .hexagon:after {
      content:""; position:absolute; border-left:40px solid transparent; border-right:40px solid transparent;
    }
    .hexagon:before { bottom:100%; border-bottom:23.09px solid #0d6efd; }
    .hexagon:after  { top:100%; border-top:23.09px solid #0d6efd; }
    .hex-label {
      position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
      color:white; font-weight:600; font-size:14px;
    }
    /* Panel general de botones */
    .btn-panel .stButton>button { margin:3px; padding:6px 10px; }
  </style>
""", unsafe_allow_html=True)

# ———————————————————
# 3) State init
# ———————————————————
if "events_log" not in st.session_state:
    st.session_state["events_log"] = []

def registrar_evento(categoria, accion):
    st.session_state.events_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "categoria": categoria,
        "accion":    accion
    })
    st.success(f"✅ {categoria}: {accion}")

# ———————————————————
# 4) Cronómetro & Periodo
# ———————————————————
col1, col2, col3 = st.columns([1,1,2])
# – inicio/pausa
if "running" not in st.session_state:
    st.session_state.running = False
    st.session_state.start_time = None
    st.session_state.elapsed = 0.0

with col1:
    if not st.session_state.running:
        if st.button("▶ Iniciar", key="pv_start"):
            st.session_state.running = True
            st.session_state.start_time = datetime.now()
    else:
        if st.button("▮ Pausar", key="pv_pause"):
            st.session_state.elapsed += (datetime.now() - st.session_state.start_time).total_seconds()
            st.session_state.running = False

with col2:
    if st.button("↺ Reset", key="pv_reset"):
        st.session_state.running = False
        st.session_state.elapsed = 0.0
        st.session_state.start_time = None

with col3:
    total = st.session_state.elapsed
    if st.session_state.running:
        total += (datetime.now() - st.session_state.start_time).total_seconds()
    mins, secs = divmod(int(total), 60)
    st.metric("Tiempo", f"{mins:02d}:{secs:02d}")

periodo = st.radio("Periodo", ["1er TIEMPO", "2do TIEMPO", "EXTRA TIEMPO"], key="pv_periodo")
st.markdown("---")

# ———————————————————
# 5) Acciones Ofensivas
# ———————————————————
st.subheader("⚽ Ofensiva")
acciones_off = ["PASE","ÉXITO","DESVÍO","FALLO","ASISTENCIA","CENTRO","TIRO","GOL"]
cols = st.columns(4)
for i, act in enumerate(acciones_off):
    col = cols[i % 4]
    # 1) hexágono gráfico
    col.markdown(f"""
      <div class="hexagon">
        <div class="hex-label">{act}</div>
      </div>
    """, unsafe_allow_html=True)
    # 2) botón invisible encima para el click
    if col.button("", key=f"pv_off_{i}", help=act):
        registrar_evento("Ofensiva", act)

# ———————————————————
# 6) Log de eventos
# ———————————————————
st.markdown("---")
st.subheader("📋 Log de Eventos")
st.dataframe(st.session_state.events_log)
