#!/usr/bin/env python3
# dashboard_central_final.py
# Centro de Mando Narrativo España 🇪🇸
# Dashboard central con análisis de narrativas mediáticas y footer con timestamp

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------

st.set_page_config(
    page_title="Centro de Mando Narrativo España",
    layout="wide"
)

st.title("Centro de Mando Narrativo España 🇪🇸")
st.markdown(
    "Panel central que integra indicadores de narrativas, emociones, polarización y cobertura mediática."
)

# -------------------------------------------------------
# Directorio de datos
# -------------------------------------------------------

base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/processed")
)

paths = {
    "Radar Narrativo": os.path.join(base_dir, "narratives_summary.csv"),
    "Radar Emocional": os.path.join(base_dir, "emotions_summary.csv"),
    "Polarización": os.path.join(base_dir, "polarization_summary.csv"),
    "Red de Actores": os.path.join(base_dir, "actors_network.csv"),
    "Propagación": os.path.join(base_dir, "propagation_summary.csv"),
    "Tendencias": os.path.join(base_dir, "trends_summary.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage.csv"),
    "Análisis Masivos": os.path.join(base_dir, "mass_media_coverage.csv")
}

# -------------------------------------------------------
# Función genérica para mostrar cada tab
# -------------------------------------------------------

def mostrar_tab(tab_name, csv_path):

    st.header(tab_name)

    if not os.path.exists(csv_path):
        st.warning(f"No hay datos disponibles para {tab_name}.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error leyendo CSV: {e}")
        return

    if df.empty:
        st.warning("El CSV está vacío.")
        return

    # -----------------------------------------
    # Radar Narrativo
    # -----------------------------------------
    if tab_name == "Radar Narrativo" and "cluster" in df.columns:
        fig = px.bar(df, x="cluster", y="count", color="cluster",
                     title="Clusters de narrativas detectadas")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Radar Emocional
    # -----------------------------------------
    elif tab_name == "Radar Emocional" and "emotion" in df.columns:
        fig = px.bar(df, x="emotion", y="count", color="emotion",
                     title="Distribución emocional de las noticias")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Polarización
    # -----------------------------------------
    elif tab_name == "Polarización" and "date" in df.columns:
        fig = px.line(df, x="date", y="polarization_index", markers=True,
                      title="Índice de polarización mediática")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Red de Actores
    # -----------------------------------------
    elif tab_name == "Red de Actores" and "source" in df.columns and "target" in df.columns:
        fig = px.scatter(df, x="source", y="target", size="weight", color="weight",
                         title="Red de actores mediáticos")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Propagación
    # -----------------------------------------
    elif tab_name == "Propagación" and "date" in df.columns:
        fig = px.line(df, x="date", y="spread_index", markers=True,
                      title="Índice de propagación de noticias")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Tendencias
    # -----------------------------------------
    elif tab_name == "Tendencias" and "keyword" in df.columns:
        fig = px.bar(df, x="keyword", y="count", color="count",
                     title="Tendencias de palabras clave")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Cobertura Gobierno
    # -----------------------------------------
    elif tab_name == "Cobertura Gobierno" and "source" in df.columns:
        fig = px.bar(df, x="source", y="alignment", color="alignment",
                     title="Cobertura mediática del gobierno")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

    # -----------------------------------------
    # Análisis Masivos
    # -----------------------------------------
    elif tab_name == "Análisis Masivos" and "source" in df.columns:
        fig = px.line(df, x="last_update", y="intensity_index", color="source", markers=True,
                      title="Intensidad mediática por fuente")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)

# -------------------------------------------------------
# Footer con copyright y timestamp de última ingestión
# -------------------------------------------------------
def mostrar_footer():
    try:
        df_news = pd.read_csv(os.path.join(base_dir, "news_summary.csv"))
        if "ingestion_ts" in df_news.columns and not df_news.empty:
            last_ingest = df_news['ingestion_ts'].max()
        else:
            last_ingest = "No disponible"
    except Exception:
        last_ingest = "No disponible"

    st.markdown("---")
    st.markdown(
        f"""
        <small>
        © M. Castillo – <a href="mailto:mybloggingnotes@gmail.com">mybloggingnotes@gmail.com</a><br>
        Última ingestión de datos: {last_ingest}<br>
        Fuente de datos: CSV reales de RSS
        </small>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------
# Main: Tabs en sidebar
# -------------------------------------------------------

tabs = list(paths.keys()) + ["Guía de Uso"]
tab_selection = st.sidebar.selectbox("Selecciona Tab", tabs)

if tab_selection == "Guía de Uso":
    st.header("Guía de Uso del Centro de Mando Narrativo 🇪🇸")
    st.markdown("""
    ### Centro de Mando Narrativo España

    Este dashboard analiza la narrativa mediática utilizando datos RSS de medios.

    ### Pasos básicos

    1. Ejecutar pipeline de datos:
       ```bash
       python3 scripts/run_all.py
       ```
    2. Seleccionar tab en la barra lateral.
    3. Observar gráficos interactivos y tablas de datos.
    """)
else:
    mostrar_tab(tab_selection, paths[tab_selection])

# -------------------------------------------------------
# Mostrar footer
# -------------------------------------------------------
mostrar_footer()
