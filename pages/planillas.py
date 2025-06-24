#planillas

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import os

# Configuración de la base de datos
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "futbol.db"
os.makedirs(DB_PATH.parent, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jugadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo TEXT NOT NULL,
        nombre TEXT NOT NULL,
        numero INTEGER NOT NULL,
        posicion TEXT NOT NULL,
        color TEXT NOT NULL,
        UNIQUE(equipo, numero)
    ''')
    conn.commit()
    return conn

def guardar_jugador(equipo, nombre, numero, posicion, color):
    conn = init_db()
    try:
        conn.execute(
            "INSERT INTO jugadores (equipo, nombre, numero, posicion, color) VALUES (?, ?, ?, ?, ?)",
            (equipo, nombre, numero, posicion, color)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        st.error(f"❌ Error: El número {numero} ya está asignado en el {equipo}")

def cargar_plantilla(equipo):
    conn = init_db()
    query = f"SELECT nombre, numero, posicion, color FROM jugadores WHERE equipo = '{equipo}' ORDER BY numero"
    return pd.read_sql_query(query, conn)

def main():
    st.title("👥 Gestión de Plantillas")
    st.markdown("---")
    
    tab_local, tab_visitante = st.tabs(["Equipo Local", "Equipo Visitante"])
    
    with tab_local:
        equipo = "Local"
        st.subheader(f"Jugadores del {equipo}")
        gestionar_jugadores(equipo)
    
    with tab_visitante:
        equipo = "Visitante"
        st.subheader(f"Jugadores del {equipo}")
        gestionar_jugadores(equipo)

def gestionar_jugadores(equipo):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form(f"form_{equipo}"):
            nombre = st.text_input("Nombre completo", key=f"nombre_{equipo}")
            numero = st.number_input("Número", 1, 99, key=f"numero_{equipo}")
            posicion = st.selectbox(
                "Posición",
                ["Portero", "Defensa", "Centrocampista", "Delantero"],
                key=f"pos_{equipo}"
            )
            color = st.color_picker(
                "Color de camiseta",
                "#FF0000" if equipo == "Local" else "#0000FF",
                key=f"color_{equipo}"
            )
            
            if st.form_submit_button("➕ Añadir Jugador"):
                guardar_jugador(equipo, nombre, numero, posicion, color)
                st.success(f"✅ Jugador {nombre} añadido al {equipo}!")
    
    with col2:
        st.markdown("### Plantilla Actual")
        plantilla = cargar_plantilla(equipo)
        if not plantilla.empty:
            st.dataframe(
                plantilla.style.apply(
                    lambda x: [f"background-color: {x['color']}; color: white"] * len(x), 
                    axis=1
                ),
                hide_index=True
            )
        else:
            st.info(f"No hay jugadores registrados para el {equipo}")

if __name__ == "__main__":
    main()