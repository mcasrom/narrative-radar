#!/usr/bin/env python3
# dashboard_central_final.py
# Centro de Mando Narrativo España 🇪🇸
# Versión final con tab de guía HowTo + descarga PDF

import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Centro de Mando Narrativo España", layout="wide")
st.title("Centro de Mando Narrativo España 🇪🇸")
st.markdown("Panel central que integra múltiples indicadores de noticias, narrativas y polarización.")

# -----------------------------
# Paths de CSV por tab
# -----------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
paths = {
    "Radar Narrativo": os.path.join(base_dir, "narratives_summary.csv"),
    "Radar Emocional": os.path.join(base_dir, "emotions_summary.csv"),
    "Polarización": os.path.join(base_dir, "polarization_summary.csv"),
    "Red de Actores": os.path.join(base_dir, "actors_network.csv"),
    "Propagación": os.path.join(base_dir, "propagation_summary.csv"),
    "Tendencias": os.path.join(base_dir, "trends_summary.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage.csv"),
    "Análisis Masivos": os.path.join(base_dir, "mass_media_coverage.csv"),
    # PDF guía (no rompe tabs existentes)
    "Guía / HowTo PDF": os.path.join(base_dir, "Guia_Centro_Mando_Narrativo.pdf")
}

# -----------------------------
# Función para mostrar tabs existentes
# -----------------------------
def mostrar_tab(tab_name, csv_path):
    st.header(tab_name)
    
    if not os.path.exists(csv_path):
        st.warning(f"No hay datos de {tab_name}. Ejecuta los scripts correspondientes.")
        return
    
    df = pd.read_csv(csv_path)
    
    if df.empty:
        st.warning(f"El CSV de {tab_name} está vacío.")
        return
    
    # Radar Narrativo
    if tab_name == "Radar Narrativo":
        fig = px.bar(df, x='cluster', y='count', color='cluster', title="Clusters de narrativas")
        fig.update_layout(xaxis_title="Cluster", yaxis_title="Cantidad de noticias")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Radar Emocional
    elif tab_name == "Radar Emocional":
        fig = px.bar(df, x='emotion', y='count', color='emotion', title="Distribución de emociones")
        fig.update_layout(xaxis_title="Emoción", yaxis_title="Cantidad")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Polarización
    elif tab_name == "Polarización":
        fig = px.bar(df, x='date', y='polarization_index', color='polarization_index', title="Índice de polarización por fecha")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Polarización")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Red de Actores
    elif tab_name == "Red de Actores":
        fig = px.scatter(df, x='source', y='target', size='weight', color='weight',
                         title="Red de actores (peso de conexiones)", hover_data=['last_update'])
        fig.update_layout(xaxis_title="Fuente / Actor", yaxis_title="Destino / Actor")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Propagación
    elif tab_name == "Propagación":
        fig = px.line(df, x='date', y='spread_index', color='spread_index', 
                      title="Propagación de noticias (índice)")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Índice de propagación")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Tendencias
    elif tab_name == "Tendencias":
        fig = px.bar(df, x='keyword', y='count', color='count', title="Tendencias de palabras clave")
        fig.update_layout(xaxis_title="Palabra clave", yaxis_title="Cantidad")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Cobertura Gobierno
    elif tab_name == "Cobertura Gobierno":
        fig = px.bar(df, x='source', y='alignment', color='alignment', title="Cobertura mediática del gobierno")
        fig.update_layout(xaxis_title="Fuente", yaxis_title="Alineamiento/Polaridad")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df)
    
    # Análisis Masivos
    elif tab_name == "Análisis Masivos":
        fig = px.line(df, x='last_update', y='intensity_index', color='source', markers=True,
                      title="Intensidad mediática por fuente")
        fig.update_layout(xaxis_title="Última actualización", yaxis_title="Intensidad")
        st.plotly_chart(fig, width="stretch")
        st.subheader("Detalle por fuente")
        st.dataframe(df)

# -----------------------------
# Función para mostrar tab de guía
# -----------------------------
def mostrar_howto_tab():
    st.header("Guía de Uso del Centro de Mando Narrativo 🇪🇸")
    
    st.markdown("""
    Bienvenido al **Centro de Mando Narrativo España**. Este tab ofrece instrucciones sobre cómo utilizar el dashboard.

    ### Contenido
    - **Radar Narrativo**: Visualiza clusters de noticias agrupadas por temática.
    - **Radar Emocional**: Distribución de emociones en las noticias.
    - **Polarización**: Índice de polarización por fecha.
    - **Red de Actores**: Conexiones entre fuentes de noticias y actores.
    - **Propagación**: Cómo se difunden las noticias en el tiempo.
    - **Tendencias**: Palabras clave más frecuentes.
    - **Cobertura Gobierno**: Alineamiento mediático hacia el gobierno.
    - **Análisis Masivos**: Intensidad mediática por fuente.
    """)

    st.subheader("Cómo usar el dashboard")
    st.markdown("""
    1. Selecciona el tab que quieres explorar.
    2. Observa los gráficos interactivos y las tablas de datos.
    3. Para actualizar los datos, ejecuta los scripts del pipeline:
       ```bash
       ./update_dashboard.sh
       ```
    4. Los CSV se almacenan en `../data/processed/` para análisis externos.
    """)

    st.subheader("Tips Avanzados")
    st.markdown("""
    - Puedes filtrar o exportar las tablas de cada tab usando el menú de Streamlit.
    - Los clusters de noticias se etiquetan automáticamente según palabras clave principales.
    - Para modificar la configuración de recolección de noticias, edita los scripts en `scripts/`.
    """)

    # --- Botón para descargar PDF ---
    pdf_path = paths["Guía / HowTo PDF"]
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            "📥 Descargar PDF completo de la Guía",
            pdf_bytes,
            file_name="Guia_Centro_Mando_Narrativo.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("No se encontró el PDF. Ejecuta scripts/generate_user_guide_pdf.py para generarlo.")

    st.info("Este tab es seguro: no modifica datos y no depende de CSV. Solo guía al usuario.")

# -----------------------------
# Crear tabs en Streamlit
# -----------------------------
tab_names = list(paths.keys())
# Reordenar para que el PDF no aparezca como tab visual
visual_tabs = [t for t in tab_names if t != "Guía / HowTo PDF"] + ["Guía / HowTo"]

tabs = st.tabs(visual_tabs)

for tab, tab_name in zip(tabs, visual_tabs):
    with tab:
        if tab_name == "Guía / HowTo":
            mostrar_howto_tab()
        else:
            mostrar_tab(tab_name, paths[tab_name])
