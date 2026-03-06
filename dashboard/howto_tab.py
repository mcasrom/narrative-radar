#!/usr/bin/env python3
# howto_tab.py
# Tab Guía / HowTo para Centro de Mando Narrativo España 🇪🇸
# Compatible con dashboard_central.py

import streamlit as st
import os

def mostrar_howto_tab():
    st.header("Guía de uso / HowTo")
    
    st.markdown("""
    Bienvenido al **Centro de Mando Narrativo España 🇪🇸**.  
    Este tab contiene instrucciones para entender y operar el dashboard sin alterar los CSV ni los scripts existentes.
    """)
    
    st.subheader("1️⃣ Rutas de CSV utilizados")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
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
        st.markdown(f"- **{tab}** → `{full_path}`")
    
    st.subheader("2️⃣ Flujo de actualización de datos")
    st.markdown("""
    1. **Recolectar noticias reales:** `collect_rss.py`  
    2. **Detectar narrativas:** `detect_narratives.py`  
    3. **Detectar emociones:** `detect_emotions.py`  
    4. **Calcular polarización:** `detect_polarization.py`  
    5. Todos los scripts generan CSV en `data/processed/`  
    6. Ejecuta `update_dashboard.sh` para regenerar todos los dashboards
    """)
    
    st.subheader("3️⃣ Cómo ejecutar manualmente")
    st.code("""
    cd ~/narrative-radar
    python3 scripts/collect_rss.py
    python3 scripts/detect_narratives.py
    python3/scripts/detect_emotions.py
    python3/scripts/detect_polarization.py
    """, language="bash")
    
    st.subheader("4️⃣ Notas importantes")
    st.markdown("""
    - No modifiques directamente los CSV dentro de `data/processed/`.  
    - Los nombres de columnas deben coincidir con los que esperan los scripts y el dashboard.  
    - Si aparecen warnings de Plotly (`use_container_width`), están corregidos usando `width='stretch'`.  
    - Este tab **HowTo** se puede actualizar en cualquier momento sin tocar el dashboard principal.  
    - Para solucionar errores frecuentes, revisa la salida de logs en `pipeline.log` (si existe) o los cron jobs que ejecutan los scripts automáticamente.
    """)
    
    st.subheader("5️⃣ Cron Jobs")
    st.markdown("""
    - Los scripts se ejecutan automáticamente vía `crontab` cada 30-35 minutos.  
    - Ubicación: `crontab -l | grep narrative-radar`  
    - Puedes desactivar temporalmente un cron editando con `crontab -e`.
    """)
    
    st.subheader("6️⃣ Contacto y mantenimiento")
    st.markdown("""
    - Este dashboard y scripts están gestionados por el equipo de **narrative-radar**.  
    - Cualquier duda sobre CSV, ejecución o nuevas fuentes RSS, documenta en este tab o en `README.md`.  
    - Recuerda que los tabs existentes **no deben ser eliminados ni renombrados**, ya que dependen de los CSV generados.
    """)
    
    st.success("✅ Tab HowTo cargado correctamente. Puedes consultarlo en cualquier momento.")
