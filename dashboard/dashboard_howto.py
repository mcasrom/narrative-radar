#!/usr/bin/env python3
# dashboard_howto.py
# Tab adicional para el Centro de Mando Narrativo España 🇪🇸
# Muestra guía y how-to del proyecto sin modificar los tabs existentes

import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Guía Narrativa", layout="wide")
st.title("Guía de Uso — Centro de Mando Narrativo España 🇪🇸")
st.markdown("""
Este tab proporciona instrucciones y rutas de uso del pipeline de noticias y del dashboard.
No altera los tabs existentes ni los CSV actuales.
""")

# -----------------------------
# Definición de rutas de los scripts y CSV
# -----------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts"))

paths = {
    "Noticias (raw/news.csv)": os.path.join(base_dir, "news.csv"),
    "Narrativas detectadas": os.path.join(base_dir, "narratives_summary.csv"),
    "Emociones detectadas": os.path.join(base_dir, "emotions_summary.csv"),
    "Polarización": os.path.join(base_dir, "polarization_summary.csv"),
    "Red de actores": os.path.join(base_dir, "actors_network.csv"),
    "Propagación": os.path.join(base_dir, "propagation_summary.csv"),
    "Tendencias": os.path.join(base_dir, "trends_summary.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage.csv"),
    "Análisis Masivos": os.path.join(base_dir, "mass_media_coverage.csv")
}

scripts = {
    "Recolectar noticias RSS": os.path.join(scripts_dir, "collect_rss.py"),
    "Detectar narrativas": os.path.join(scripts_dir, "detect_narratives.py"),
    "Detectar emociones": os.path.join(scripts_dir, "detect_emotions.py"),
    "Detectar polarización": os.path.join(scripts_dir, "detect_polarization.py")
}

# -----------------------------
# Mostrar rutas de CSV
# -----------------------------
st.subheader("Rutas de CSV generados por el pipeline")
for name, path in paths.items():
    exists = os.path.exists(path)
    status = "✅ Existe" if exists else "❌ No existe"
    st.markdown(f"- **{name}** → `{path}` ({status})")

# -----------------------------
# Mostrar scripts y cómo ejecutarlos
# -----------------------------
st.subheader("Scripts principales y cómo ejecutarlos")
for name, path in scripts.items():
    exists = os.path.exists(path)
    status = "✅ Disponible" if exists else "❌ No encontrado"
    st.markdown(f"- **{name}** → `{path}` ({status})")
    st.code(f"python3 {path}", language="bash")

# -----------------------------
# Instrucciones generales
# -----------------------------
st.subheader("Instrucciones generales de uso")
st.markdown("""
1. **Recolectar noticias:**  
   Ejecuta `collect_rss.py` para obtener las noticias reales de los RSS configurados.  
   Esto genera `news.csv` y `news_summary.csv`.

2. **Detectar narrativas:**  
   Ejecuta `detect_narratives.py` para procesar `news.csv` y generar `narratives_summary.csv`.

3. **Detectar emociones y polarización:**  
   Ejecuta `detect_emotions.py` y `detect_polarization.py` para generar los CSV correspondientes.

4. **Actualizar dashboard:**  
   Ejecuta `update_dashboard.sh` para que todos los tabs se refresquen con los CSV procesados.

5. **Notas importantes:**  
   - No elimines ni renombres los CSV procesados, el dashboard depende de los nombres exactos.  
   - Puedes consultar cada CSV con `pd.read_csv("<ruta>")` si quieres análisis manual.  
   - Los scripts se pueden automatizar vía crontab como ya está configurado.
""")

# -----------------------------
# Mostrar tabla resumen de CSV existentes
# -----------------------------
st.subheader("Resumen rápido de CSV existentes")
summary = []
for name, path in paths.items():
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            nrows = len(df)
        except:
            nrows = "Error al leer"
    else:
        nrows = "No existe"
    summary.append({"CSV": name, "Filas": nrows, "Ruta": path})

st.dataframe(pd.DataFrame(summary))
