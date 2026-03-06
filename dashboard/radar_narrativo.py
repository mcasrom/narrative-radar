#!/usr/bin/env python3

# ==================================================
# Radar Narrativo España 🇪🇸
# Dashboard Streamlit para mostrar narrativas
# ==================================================

import os
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Configuración de paths
# --------------------------------------------------
CSV_FILE = "../data/processed/narratives_summary.csv"

st.set_page_config(page_title="Radar Narrativo España", layout="wide")

st.title("Radar Narrativo España 🇪🇸")
st.markdown(
    "Este dashboard muestra las narrativas detectadas en noticias recientes "
    "y su intensidad por cluster."
)

# --------------------------------------------------
# Verificar si el archivo existe
# --------------------------------------------------
if not os.path.exists(CSV_FILE):
    st.error(
        f"Archivo no encontrado: {CSV_FILE}.\n\n"
        "Primero ejecuta:\n"
        "1. `python3 scripts/collect_rss.py`\n"
        "2. `python3 scripts/detect_narratives.py`"
    )
    st.stop()

# --------------------------------------------------
# Cargar CSV
# --------------------------------------------------
df = pd.read_csv(CSV_FILE)

if df.empty:
    st.warning("El archivo CSV existe pero no contiene datos.")
    st.stop()

# --------------------------------------------------
# Mostrar tabla de resumen
# --------------------------------------------------
st.subheader("Resumen de narrativas detectadas")
st.dataframe(df)

# --------------------------------------------------
# Gráfico radar
# --------------------------------------------------
st.subheader("Radar de intensidad de narrativas")

# Preparar gráfico
fig = px.line_polar(
    df,
    r='count',
    theta='cluster',
    line_close=True,
    title='Intensidad de narrativas por cluster',
    template='plotly_dark'
)

st.plotly_chart(fig, width="stretch")

# --------------------------------------------------
# Información adicional
# --------------------------------------------------
st.markdown(
    f"Última actualización de datos: {df['last_update'].max()}"
)

st.info(
    "Este radar se actualiza automáticamente al ejecutar `detect_narratives.py` "
    "después de recolectar noticias con `collect_rss.py`."
)
