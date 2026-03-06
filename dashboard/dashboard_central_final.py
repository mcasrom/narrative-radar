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

st.set_page_config(page_title="Centro de Mando Narrativo España", layout="wide")
st.title("Centro de Mando Narrativo España 🇪🇸")
st.markdown("Panel central que integra indicadores de narrativas, emociones, polarización y cobertura mediática.")

current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(current_dir, "../data/processed"))
scripts_dir = os.path.abspath(os.path.join(current_dir, "../scripts"))

paths = {
    "Radar Narrativo": os.path.join(base_dir, "narratives_summary.csv"),
    "Radar Emocional": os.path.join(base_dir, "emotions_summary.csv"),
    "Polarización": os.path.join(base_dir, "polarization_summary.csv"),
    "Red de Actores": os.path.join(base_dir, "actors_network.csv"),
    "Propagación": os.path.join(base_dir, "propagation_summary.csv"),
    "Tendencias": os.path.join(base_dir, "trends_summary.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage.csv"),
    "Análisis Masivos": os.path.join(base_dir, "mass_media_coverage.csv"),
    "Guía / HowTo": None
}

def mostrar_tab(tab_name, csv_path):
    st.header(tab_name)

    if tab_name == "Guía / HowTo":
        st.markdown("""
        Bienvenido al **Centro de Mando Narrativo España 🇪🇸**.  
        Este tab contiene instrucciones para entender y operar el dashboard.
        """)

        st.subheader("1️⃣ Rutas de CSV utilizados")
        csv_files = {
            "Radar Narrativo": "narratives_summary.csv",
            "Radar Emocional": "emotions_summary.csv",
            "Polarización": "polarization_summary.csv",
            "Red de Actores": "actors_network.csv",
            "Propagación": "propagation_summary.csv",
            "Tendencias": "trends_summary.csv",
            "Cobertura Gobierno": "government_coverage.csv",
            "Análisis Masivos": "mass_media_coverage.csv"
        }
        for tab, filename in csv_files.items():
            full_path = os.path.join(base_dir, filename)
            exists = "✅" if os.path.exists(full_path) else "❌"
            try:
                df = pd.read_csv(full_path)
                nrows = len(df)
            except:
                nrows = "N/A"
            st.markdown(f"- {exists} **{tab}** → `{filename}` ({nrows} filas)")

        st.subheader("2️⃣ Flujo de actualización de datos")
        st.markdown("""
        1. **Recolectar noticias reales:** `collect_rss.py` — lee 28 fuentes RSS desde `config/sources.yaml`
        2. **Detectar narrativas:** `detect_narratives.py` — clustering TF-IDF + KMeans
        3. **Detectar emociones:** `detect_emotions.py` — léxico por categoría emocional
        4. **Calcular polarización:** `detect_polarization.py` — divergencia progresista/conservador
        5. **Red de actores:** `build_network.py` — co-actividad de fuentes por día
        6. **Propagación:** `propagation_analysis.py` — spread index diario
        7. **Tendencias:** `trends_analysis.py` — keywords TF-IDF top 30
        8. **Cobertura gobierno:** `government_coverage.py` — léxico político por medio
        9. **Pipeline completa:** `python3 scripts/run_all.py`
        """)

        st.subheader("3️⃣ Cómo ejecutar manualmente")
        st.code("""cd ~/narrative-radar
source env/bin/activate
python3 scripts/run_all.py""", language="bash")

        st.subheader("4️⃣ Cron Jobs activos")
        st.markdown("""
        - **Pipeline:** cada 30 minutos vía `update_dashboard.sh` con bloqueo flock
        - **Streamlit:** arranca automáticamente al reiniciar el Odroid (retraso 90s)
        - Verificar: `crontab -l | grep narrative-radar`
        """)

        st.subheader("5️⃣ Fuentes RSS activas")
        sources_path = os.path.abspath(os.path.join(current_dir, "../config/sources.yaml"))
        try:
            import yaml
            with open(sources_path, "r") as f:
                config = yaml.safe_load(f)
            sources_df = pd.DataFrame(config["sources"])
            st.dataframe(sources_df, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo cargar sources.yaml: {e}")

        st.subheader("6️⃣ Histórico de ciclos")
        history_files = {
            "Emociones": os.path.join(base_dir, "emotions_history.csv"),
            "Polarización": os.path.join(base_dir, "polarization_history.csv"),
            "Tendencias": os.path.join(base_dir, "trends_history.csv"),
            "Cobertura Gobierno": os.path.join(base_dir, "government_coverage_history.csv"),
        }
        for name, path in history_files.items():
            if os.path.exists(path):
                df = pd.read_csv(path)
                st.markdown(f"- ✅ **{name}** — {len(df)} registros acumulados")
            else:
                st.markdown(f"- ❌ **{name}** — sin histórico aún")

        st.subheader("7️⃣ Notas importantes")
        st.markdown("""
        - No modifiques directamente los CSV en `data/processed/`
        - Los nombres de columnas deben coincidir con los esperados por el dashboard
        - Revisa `pipeline.log` para diagnóstico de errores
        - Para añadir fuentes RSS edita `config/sources.yaml` — sin tocar código Python
        """)

        st.subheader("8️⃣ Contacto y mantenimiento")
        st.markdown("""
        - **Autor:** M. Castillo · mybloggingnotes@gmail.com  
        - **Repo:** https://github.com/mcasrom/narrative-radar  
        - **Nodo físico:** Odroid-C2 (ARM, DietPi) — operación continua 24/7
        """)

        st.success("✅ Sistema operativo. Pipeline ejecutándose cada 30 minutos.")
        return

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
                      labels={"date": "Fecha", "polarization_index": "Índice"})
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
        fig = px.bar(df, x="source", y="alignment_score", color="alignment",
                     title="Alineamiento mediático por fuente",
                     labels={"source": "Medio", "alignment_score": "Score"})
        st.plotly_chart(fig, use_container_width=True)

    elif tab_name == "Análisis Masivos" and "source" in df.columns:
        fig = px.bar(df, x="source", y="intensity_index", color="intensity_index",
                     title="Intensidad de cobertura por medio",
                     labels={"source": "Medio", "intensity_index": "Índice de intensidad"},
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

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

Este dashboard analiza la narrativa mediatica usando fuentes RSS.
CSV almacenados en: data/processed/
"""
    pdf.multi_cell(0, 10, texto)
    output_pdf = os.path.join(base_dir, "guia_dashboard.pdf")
    pdf.output(output_pdf)
    return output_pdf

tab_names = list(paths.keys())
tabs = st.tabs(tab_names)

for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        mostrar_tab(tab_name, paths[tab_name])

st.markdown("---")
st.subheader("📄 Guía y Metadatos")
col1, col2 = st.columns(2)

with col1:
    if st.button("Generar PDF guía actualizado"):
        pdf_file = generar_pdf()
        st.success("PDF generado exitosamente")

with col2:
    testigo = paths["Tendencias"]
    if os.path.exists(testigo):
        mtime = os.path.getmtime(testigo)
        last_ingestion = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_ingestion = "Archivo no encontrado"
    st.write(f"**Última ingestión de datos (Real):** {last_ingestion}")
    st.write("© 2026 M. Castillo | mybloggingnotes@gmail.com")
