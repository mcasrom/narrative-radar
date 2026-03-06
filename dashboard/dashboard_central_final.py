#!/usr/bin/env python3
# dashboard_central_final.py
# Centro de Mando Narrativo España 🇪🇸
# Autor: M. Castillo <mybloggingnotes@gmail.com>

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
st.set_page_config(
    page_title="Centro de Mando Narrativo España",
    layout="wide"
)

st.title("Centro de Mando Narrativo España 🇪🇸")
st.markdown("Panel central que integra indicadores de narrativas, emociones, polarización y cobertura mediática.")

# -------------------------------------------------------
# Directorio de datos (Ruta absoluta segura)
# -------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(current_dir, "../data/processed"))

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
        st.warning(f"No hay datos disponibles para el módulo: {tab_name}")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error leyendo CSV: {e}")
        return

    if df.empty:
        st.warning("El CSV está vacío.")
        return

    # Visualizaciones por Tab
    if tab_name == "Radar Narrativo" and "cluster" in df.columns:
        fig = px.bar(df, x="cluster", y="count", color="cluster",
                     title="Clusters de narrativas detectadas")
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Radar Emocional" and "emotion" in df.columns:
        fig = px.bar(df, x="emotion", y="count", color="emotion",
                     title="Distribución emocional")
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Polarización" and "date" in df.columns:
        fig = px.line(df, x="date", y="polarization_index", markers=True,
                      title="Índice de polarización",
                      labels={"date": "Fecha", "polarization_index": "Índice de polarización"})
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Red de Actores" and "source" in df.columns:
        fig = px.bar(df, x="source", y="weight", color="target",
                     title="Red de actores — peso de relaciones",
                     labels={"source": "Actor origen", "weight": "Peso", "target": "Actor destino"})
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Propagación" and "date" in df.columns:
        fig = px.line(df, x="date", y="spread_index", markers=True,
                      title="Índice de propagación narrativa",
                      labels={"date": "Fecha", "spread_index": "Índice de propagación"})
        fig.update_traces(line_color="#e05c00", line_width=2)
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Tendencias" and "keyword" in df.columns:
        fig = px.bar(df, x="keyword", y="count", color="count",
                     title="Tendencias de palabras clave")
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Cobertura Gobierno" and "source" in df.columns:
        fig = px.bar(df, x="source", y="alignment", color="alignment",
                     title="Alineamiento mediático")
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Análisis Masivos" and "source" in df.columns:
        fig = px.bar(df, x="source", y="intensity_index", color="intensity_index",
                     title="Intensidad de cobertura por medio",
                     labels={"source": "Medio", "intensity_index": "Índice de intensidad"},
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)

# -------------------------------------------------------
# PDF guía
# -------------------------------------------------------
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(current_dir, "DejaVuSans.ttf")

    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Arial", size=12)

    testigo = paths["Tendencias"]
    fecha_pdf = datetime.fromtimestamp(os.path.getmtime(testigo)).strftime("%Y-%m-%d %H:%M:%S") if os.path.exists(testigo) else "N/A"

    texto = f"""
Centro de Mando Narrativo España
Autor: M. Castillo <mybloggingnotes@gmail.com>
Fecha de datos: {fecha_pdf}

Este dashboard analiza la narrativa mediática usando fuentes RSS.
CSV almacenados en: data/processed/
"""
    pdf.multi_cell(0, 10, texto)
    output_pdf = os.path.join(base_dir, "guia_dashboard.pdf")
    pdf.output(output_pdf)
    return output_pdf

# -------------------------------------------------------
# Layout Principal
# -------------------------------------------------------
tab_names = list(paths.keys())
tabs = st.tabs(tab_names)

for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        mostrar_tab(tab_name, paths[tab_name])

# -------------------------------------------------------
# Pie de Página (footer) Dinámico
# -------------------------------------------------------
st.markdown("---")
st.subheader("📄 Guía y Metadatos")

col1, col2 = st.columns(2)

with col1:
    if st.button("Generar PDF guía actualizado"):
        pdf_file = generar_pdf()
        st.success(f"PDF generado exitosamente")

with col2:
    testigo = paths["Tendencias"]
    if os.path.exists(testigo):
        mtime = os.path.getmtime(testigo)
        last_ingestion = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_ingestion = "Archivo no encontrado"

    st.write(f"**Última ingestión de datos (Real):** {last_ingestion}")
    st.write("© 2026 M. Castillo | mybloggingnotes@gmail.com")
