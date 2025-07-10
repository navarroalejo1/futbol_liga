# pages/planillas.py

import streamlit as st
import pandas as pd
import importlib
from utils.events import load_json, save_json
from utils.constants import POSICIONES

# ───────────────────────────────────────────────────────────────
# Compatibilidad rerun en distintas versiones de Streamlit
# ───────────────────────────────────────────────────────────────
try:
    rerun = st.experimental_rerun
except AttributeError:
    try:
        script_req = importlib.import_module("streamlit.runtime.scriptrunner.script_requests")
        rerun = script_req.request_rerun
    except ImportError:
        rerun = lambda: None

# ───────────────────────────────────────────────────────────────
# Archivos JSON dentro de cada carpeta de evento
# ───────────────────────────────────────────────────────────────
PLANTILLA_FILE = "plantilla.json"
PARTIDOS_FILE  = "partidos.json"

def app():
    st.set_page_config(page_title="👥 Paso 3: Gestión de Planillas", layout="wide")
    st.header("👥 Paso 3: Gestión de Planillas")

    # 1) Contexto
    event_id = st.session_state.get("evento_activo")
    partido  = st.session_state.get("partido_activo")
    if not event_id:
        st.warning("⚠️ Selecciona primero un evento en el Paso 1.")
        return
    if not partido:
        st.warning("⚠️ Selecciona primero un partido en el Paso 2.")
        return

    # 2) Datos del partido
    local   = partido["local"]
    visita  = partido["visitante"]
    fecha   = partido.get("fecha","-")
    hora    = partido.get("hora","-")
    competi = partido.get("competicion","-")
    cancha  = partido.get("cancha","-")
    st.subheader(f"🏟️ {local} vs {visita} — {fecha} {hora}")
    st.markdown(f"**Competición:** {competi}   |   **Cancha:** {cancha}")
    st.markdown("---")

    # 3) Carga de JSON
    plantilla     = load_json(event_id, PLANTILLA_FILE) or []
    partidos_list = load_json(event_id, PARTIDOS_FILE)  or []

    # 4) Agregar jugador
    st.subheader("➕ Agregar nuevo jugador a plantilla")
    with st.form("form_add_player", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns([4,1,2,2,1])
        with c1:
            new_name = st.text_input("Nombre completo")
        with c2:
            new_dorsal = st.number_input("Dorsal", min_value=1, max_value=99, step=1)
        with c3:
            new_pos = st.selectbox("Posición", options=POSICIONES)
        with c4:
            new_team = st.selectbox("Equipo", options=[local, visita])
        with c5:
            submitted = st.form_submit_button("Agregar")
        if submitted:
            errs=[]
            if not new_name.strip():
                errs.append("El nombre es obligatorio.")
            if any(j["dorsal"]==new_dorsal and j["equipo"]==new_team for j in plantilla):
                errs.append(f"El dorsal {new_dorsal} ya existe en {new_team}.")
            if errs:
                for e in errs: st.error(f"❌ {e}")
            else:
                plantilla.append({
                    "nombre": new_name.strip(),
                    "dorsal": new_dorsal,
                    "posicion": new_pos,
                    "equipo": new_team
                })
                save_json(event_id, PLANTILLA_FILE, plantilla)
                st.success(f"✔️ Jugador {new_name.strip()} agregado.")
                rerun()

    st.markdown("---")

    # 5) Modificar jugador
    st.subheader("✏️ Modificar jugador existente")
    for equipo in (local, visita):
        st.markdown(f"**{equipo}**")
        jug_eq = [j for j in plantilla if j["equipo"]==equipo]
        if not jug_eq:
            st.info("ℹ️ No hay jugadores en plantilla para este equipo.")
            continue

        idx = st.selectbox(
            f"Selecciona para editar ({equipo})",
            options=list(range(len(jug_eq))),
            format_func=lambda i, eq=equipo: f"J{jug_eq[i]['dorsal']} – {jug_eq[i]['nombre']}",
            key=f"mod_idx_{equipo}"
        )
        jugador = jug_eq[idx]
        col1, col2, col3 = st.columns([4,1,2])
        with col1:
            mod_name = st.text_input("Nombre", value=jugador["nombre"], key=f"mod_name_{equipo}")
        with col2:
            mod_dorsal = st.number_input("Dorsal", value=jugador["dorsal"], min_value=1, max_value=99, key=f"mod_dorsal_{equipo}")
        with col3:
            mod_pos = st.selectbox("Posición", POSICIONES, index=POSICIONES.index(jugador["posicion"]), key=f"mod_pos_{equipo}")
        if st.button(f"💾 Guardar cambios ({equipo})", key=f"mod_btn_{equipo}"):
            otros = {j["dorsal"] for j in plantilla if j is not jugador and j["equipo"]==equipo}
            if mod_dorsal in otros:
                st.error(f"❌ Dorsal {mod_dorsal} ya existe en {equipo}.")
            else:
                jugador.update({"nombre":mod_name.strip(),"dorsal":mod_dorsal,"posicion":mod_pos})
                save_json(event_id, PLANTILLA_FILE, plantilla)
                st.success("✔️ Jugador modificado.")
                rerun()

    st.markdown("---")

    # 6) Localizar partido en partidos.json
    idx_p = next((
        i for i,p in enumerate(partidos_list)
        if p.get("local")==local and p.get("visitante")==visita
           and p.get("fecha")==fecha and p.get("hora")==hora
    ), None)
    if idx_p is None:
        st.error("❌ Partido no encontrado en el calendario (Paso 2).")
        return
    partido_sel = partidos_list[idx_p]
    partido_sel.setdefault("titulares",{})
    partido_sel.setdefault("banquillo",{})

    # 7) Selección de Titulares
    st.subheader("✅ Selección de Titulares (max 11)")
    for equipo in (local, visita):
        st.markdown(f"**{equipo}**")
        jug_eq = [j for j in plantilla if j["equipo"]==equipo]
        opciones = [f"J{j['dorsal']} – {j['nombre']} ({j['posicion']})" for j in jug_eq]
        guard = partido_sel["titulares"].get(equipo,[])
        default = [o for o in opciones if int(o.split(" – ")[0][1:]) in guard]

        sel = st.multiselect(f"Titulares {equipo}", opciones, default, key=f"tit_{equipo}")
        if len(sel)>11:
            st.warning("⚠️ Máximo 11 titulares.")
        dors_sel = [int(o.split(" – ")[0][1:]) for o in sel]
        partido_sel["titulares"][equipo]=dors_sel

        # reconstrucción explícita del DataFrame
        df_eq = pd.DataFrame([{
            "Dorsal":j["dorsal"],
            "Nombre":j["nombre"],
            "Posición":j["posicion"],
            "Titular": (j["dorsal"] in dors_sel)
        } for j in jug_eq])
        st.dataframe(df_eq, use_container_width=True)
        st.markdown("---")

    # 8) Selección de Suplentes
    st.subheader("🏋️ Suplentes (Banquillo)")
    for equipo in (local, visita):
        st.markdown(f"**{equipo}**")
        jug_eq = [j for j in plantilla if j["equipo"]==equipo]
        opciones = [f"J{j['dorsal']} – {j['nombre']} ({j['posicion']})" for j in jug_eq]
        tit_guard = partido_sel["titulares"].get(equipo,[])
        opts_bank = [o for o in opciones if int(o.split(" – ")[0][1:]) not in tit_guard]
        ban_guard = partido_sel["banquillo"].get(equipo,[])
        default_bank = [o for o in opts_bank if int(o.split(" – ")[0][1:]) in ban_guard]

        sel_b = st.multiselect(f"Suplentes {equipo}", opts_bank, default_bank, key=f"ban_{equipo}")
        dors_b = [int(o.split(" – ")[0][1:]) for o in sel_b]
        partido_sel["banquillo"][equipo]=dors_b

        df_b = pd.DataFrame([{
            "Dorsal":j["dorsal"],
            "Nombre":j["nombre"],
            "Posición":j["posicion"],
            "Suplente": (j["dorsal"] in dors_b)
        } for j in jug_eq])
        st.dataframe(df_b, use_container_width=True)
        st.markdown("---")

    # 9) Guardar en JSON
    partidos_list[idx_p]=partido_sel
    save_json(event_id, PARTIDOS_FILE, partidos_list)
    st.success("✔️ Titulares y suplentes guardados.")

    # 10) Resumen final
    st.subheader("📝 Resumen de Plantilla")
    resumen=[]
    for equipo in (local, visita):
        for j in plantilla:
            rol = ("Titular" if j["dorsal"] in partido_sel["titulares"].get(equipo,[])
                  else "Suplente" if j["dorsal"] in partido_sel["banquillo"].get(equipo,[])
                  else "Reserva")
            if j["equipo"]==equipo:
                resumen.append({
                    "Equipo":equipo,
                    "Dorsal":j["dorsal"],
                    "Nombre":j["nombre"],
                    "Posición":j["posicion"],
                    "Rol":rol
                })
    df_res = pd.DataFrame(resumen).sort_values(["Equipo","Dorsal"]).reset_index(drop=True)
    st.table(df_res)

    # 11) Navegación wizard
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("◀ Anterior"):
            st.session_state["wizard_step"]=2
            rerun()
    with c2:
        if st.button("Siguiente ▶"):
            counts=[len(partido_sel["titulares"].get(eq,[])) for eq in (local,visita)]
            if any(c<11 for c in counts):
                st.error(f"❌ Cada equipo necesita 11 titulares (tienes {counts}).")
            else:
                st.session_state["wizard_step"]=4
                rerun()
