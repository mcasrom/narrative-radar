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
    "Keywords": None,
    "Histórico": None,
    "Guía / HowTo": None
}

keywords_paths = {
    "emerging": os.path.join(base_dir, "keywords_emerging.csv"),
    "decaying": os.path.join(base_dir, "keywords_decaying.csv"),
    "history":  os.path.join(base_dir, "trends_history.csv"),
}

history_paths = {
    "Narrativas": os.path.join(base_dir, "narratives_history.csv"),
    "Emociones": os.path.join(base_dir, "emotions_history.csv"),
    "Polarización": os.path.join(base_dir, "polarization_history.csv"),
    "Tendencias": os.path.join(base_dir, "trends_history.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage_history.csv"),
    "Red de Actores": os.path.join(base_dir, "actors_network_history.csv"),
    "Propagación": os.path.join(base_dir, "propagation_history.csv"),
    "Análisis Masivos": os.path.join(base_dir, "mass_media_history.csv"),
}

def mostrar_keywords():
    st.header("Keywords & Frases Clave")
    st.markdown("Análisis profundo de palabras clave emergentes, decayentes y su evolución temporal.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Keywords emergentes")
        path = keywords_paths["emerging"]
        if os.path.exists(path):
            df = pd.read_csv(path)
            fig = px.bar(df, x="keyword", y="delta", color="pct_change",
                         title="Keywords con mayor subida (último ciclo)",
                         labels={"keyword": "Keyword", "delta": "Incremento", "pct_change": "% cambio"},
                         color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df[["keyword","count_last","count_prev","delta","pct_change"]], use_container_width=True)
        else:
            st.info("Sin datos de keywords emergentes aún.")

    with col2:
        st.subheader("📉 Keywords decayentes")
        path = keywords_paths["decaying"]
        if os.path.exists(path):
            df = pd.read_csv(path)
            fig = px.bar(df, x="keyword", y="delta", color="pct_change",
                         title="Keywords con mayor bajada (último ciclo)",
                         labels={"keyword": "Keyword", "delta": "Decremento", "pct_change": "% cambio"},
                         color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df[["keyword","count_last","count_prev","delta","pct_change"]], use_container_width=True)
        else:
            st.info("Sin datos de keywords decayentes aún.")

    st.subheader("📈 Evolución temporal de keywords")
    path = keywords_paths["history"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        top_kw = df.groupby("keyword")["count"].sum().sort_values(ascending=False).head(20).index.tolist()
        selected_kw = st.multiselect("Selecciona keywords a comparar:", top_kw, default=top_kw[:5])
        if selected_kw:
            df_sel = df[df["keyword"].isin(selected_kw)]
            fig = px.line(df_sel, x="cycle", y="count", color="keyword", markers=True,
                          title="Evolución temporal de keywords seleccionados",
                          labels={"cycle": "Ciclo", "count": "Score TF-IDF", "keyword": "Keyword"})
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏆 Top keywords acumulados")
    path = keywords_paths["history"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        top = df.groupby("keyword")["count"].sum().reset_index()
        top = top.sort_values("count", ascending=False).head(30)
        fig = px.bar(top, x="keyword", y="count", color="count",
                     title="Top 30 keywords por score acumulado",
                     color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Actualizado cada 30 minutos · Odroid-C2 · © 2026 M. Castillo")

def mostrar_historico():
    st.header("Histórico de ciclos")
    st.markdown("Evolución temporal de cada módulo a lo largo de los ciclos de ingestión.")

    # ── Narrativas ─────────────────────────────────────────
    st.subheader("🧩 Narrativas — evolución de clusters por ciclo")
    path = history_paths["Narrativas"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        fig = px.line(df, x="cycle", y="count", color="cluster_label", markers=True,
                      title="Evolución de clusters narrativos por ciclo",
                      labels={"cycle": "Ciclo", "count": "Noticias", "cluster_label": "Cluster"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de narrativas aún.")

    # ── Emociones ──────────────────────────────────────────
    st.subheader("📊 Emociones — evolución por ciclo")
    path = history_paths["Emociones"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[df["emotion"] != "Neutral"]
        fig = px.line(df, x="cycle", y="count", color="emotion", markers=True,
                      title="Evolución emocional por ciclo de ingestión",
                      labels={"cycle": "Ciclo", "count": "Noticias", "emotion": "Emoción"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de emociones aún.")

    # ── Polarización ───────────────────────────────────────
    st.subheader("📈 Polarización — evolución por ciclo")
    path = history_paths["Polarización"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        df_agg = df.groupby("cycle")["polarization_index"].mean().reset_index()
        df_agg.columns = ["cycle", "polarization_media"]
        fig = px.line(df_agg, x="cycle", y="polarization_media", markers=True,
                      title="Índice de polarización medio por ciclo",
                      labels={"cycle": "Ciclo", "polarization_media": "Polarización media"})
        fig.update_traces(line_color="#e05c00", line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de polarización aún.")

    # ── Tendencias ─────────────────────────────────────────
    st.subheader("🔑 Tendencias — top keywords por ciclo")
    path = history_paths["Tendencias"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        cycles = sorted(df["cycle"].unique())
        selected = st.selectbox("Selecciona ciclo:", cycles, index=len(cycles)-1)
        df_sel = df[df["cycle"] == selected].sort_values("count", ascending=False).head(15)
        fig = px.bar(df_sel, x="keyword", y="count", color="count",
                     title=f"Top keywords — {selected}",
                     color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de tendencias aún.")

    # ── Cobertura Gobierno ─────────────────────────────────
    st.subheader("🏛️ Cobertura Gobierno — alineamiento por ciclo")
    path = history_paths["Cobertura Gobierno"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        df_agg = df.groupby(["cycle","alignment"]).size().reset_index(name="count")
        fig = px.bar(df_agg, x="cycle", y="count", color="alignment", barmode="stack",
                     title="Distribución de alineamiento mediático por ciclo",
                     labels={"cycle": "Ciclo", "count": "Fuentes", "alignment": "Alineamiento"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de cobertura gobierno aún.")

    # ── Propagación ────────────────────────────────────────
    st.subheader("📡 Propagación — spread index por ciclo")
    path = history_paths["Propagación"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        df_agg = df.groupby("cycle")["spread_index"].mean().reset_index()
        df_agg.columns = ["cycle", "spread_medio"]
        fig = px.line(df_agg, x="cycle", y="spread_medio", markers=True,
                      title="Spread index medio por ciclo",
                      labels={"cycle": "Ciclo", "spread_medio": "Spread medio"})
        fig.update_traces(line_color="#1f77b4", line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de propagación aún.")

    # ── Red de Actores ─────────────────────────────────────
    st.subheader("🕸️ Red de Actores — relaciones por ciclo")
    path = history_paths["Red de Actores"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        df_agg = df.groupby("cycle")["weight"].sum().reset_index()
        fig = px.bar(df_agg, x="cycle", y="weight",
                     title="Peso total de relaciones por ciclo",
                     labels={"cycle": "Ciclo", "weight": "Peso total"})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Top relaciones acumuladas:**")
        top = df.groupby(["source","target"])["weight"].sum().reset_index()
        top = top.sort_values("weight", ascending=False).head(10)
        st.dataframe(top, use_container_width=True)
    else:
        st.info("Sin histórico de red de actores aún.")

    # ── Análisis Masivos ───────────────────────────────────
    st.subheader("📰 Análisis Masivos — intensidad por ciclo")
    path = history_paths["Análisis Masivos"]
    if os.path.exists(path):
        df = pd.read_csv(path)
        cycles = sorted(df["cycle"].unique())
        selected = st.selectbox("Selecciona ciclo:", cycles, index=len(cycles)-1, key="masivos_cycle")
        df_sel = df[df["cycle"] == selected].sort_values("intensity_index", ascending=False)
        fig = px.bar(df_sel, x="source", y="intensity_index", color="intensity_index",
                     title=f"Intensidad por medio — {selected}",
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin histórico de análisis masivos aún — disponible en próximo ciclo.")

    st.markdown("---")
    st.caption(f"Histórico actualizado cada 30 minutos · Odroid-C2 · © 2026 M. Castillo")

def mostrar_howto():
    st.header("Guía de uso / HowTo")
    st.markdown("""
    Bienvenido al **Centro de Mando Narrativo España 🇪🇸**.  
    Este tab contiene instrucciones para entender y operar el dashboard.
    """)

    # ── PDF embebido ─────────────────────────────────────────────
    pdf_current = os.path.join(base_dir, "guia_dashboard.pdf")
    history_dir = os.path.join(base_dir, "guia_history")

    if os.path.exists(pdf_current):
        mtime = os.path.getmtime(pdf_current)
        fecha_pdf = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"📄 Guía v1.2 — Última actualización: {fecha_pdf}")

        with open(pdf_current, "rb") as f:
            pdf_bytes = f.read()
        import base64
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(
            f'''<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" style="border:1px solid #ccc; border-radius:6px;"></iframe>''',
            unsafe_allow_html=True
        )
        st.download_button("⬇️ Descargar guía PDF", data=pdf_bytes,
                           file_name="CMNE_Guia_v1.2.pdf", mime="application/pdf")
    else:
        st.warning("PDF de guía no generado aún — se generará en el próximo ciclo.")

    # ── Versiones anteriores ─────────────────────────────────────
    if os.path.exists(history_dir):
        versions = sorted(os.listdir(history_dir), reverse=True)
        if versions:
            st.subheader("📁 Versiones anteriores")
            selected = st.selectbox("Selecciona versión:", versions)
            hist_path = os.path.join(history_dir, selected)
            with open(hist_path, "rb") as f:
                hist_bytes = f.read()
            ts = selected.replace("guia_","").replace(".pdf","").replace("_"," ")
            st.download_button(f"⬇️ Descargar {ts}", data=hist_bytes,
                               file_name=selected, mime="application/pdf")
    st.markdown("---")

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
    1. `collect_rss.py` — 28 fuentes RSS desde `config/sources.yaml`
    2. `detect_narratives.py` — clustering TF-IDF + KMeans
    3. `detect_emotions.py` — léxico emocional
    4. `detect_polarization.py` — divergencia progresista/conservador
    5. `build_network.py` — co-actividad de fuentes
    6. `propagation_analysis.py` — spread index diario
    7. `trends_analysis.py` — keywords TF-IDF top 30
    8. `government_coverage.py` — léxico político por medio
    9. `audit_sources.py` — auditoría RSS con alerta email
    """)

    st.subheader("3️⃣ Ejecución manual")
    st.code("""cd ~/narrative-radar
source env/bin/activate
python3 scripts/run_all.py""", language="bash")

    st.subheader("4️⃣ Cron Jobs activos")
    st.markdown("""
    - **Pipeline:** cada 30 min · `update_dashboard.sh` con flock
    - **Auditoría:** cada 30 min a :05 · `audit_sources.py` con email
    - Verificar: `crontab -l | grep narrative`
    """)

    st.subheader("5️⃣ Fuentes RSS activas")
    sources_path = os.path.abspath(os.path.join(current_dir, "../config/sources.yaml"))
    try:
        import yaml
        with open(sources_path, "r") as f:
            config = yaml.safe_load(f)
        st.dataframe(pd.DataFrame(config["sources"]), use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo cargar sources.yaml: {e}")

    st.subheader("6️⃣ Histórico de ciclos")
    for name, path in history_paths.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            ciclos = df["cycle"].nunique() if "cycle" in df.columns else "—"
            st.markdown(f"- ✅ **{name}** — {len(df)} registros · {ciclos} ciclos")
        else:
            st.markdown(f"- ❌ **{name}** — sin histórico aún")

    st.subheader("7️⃣ Notas importantes")
    st.markdown("""
    - No modifiques los CSV en `data/processed/` manualmente
    - Para añadir fuentes RSS edita solo `config/sources.yaml`
    - Revisa `pipeline.log` para diagnóstico de errores
    """)

    st.subheader("8️⃣ Contacto")
    st.markdown("""
    - **Autor:** M. Castillo · mybloggingnotes@gmail.com  
    - **Repo:** https://github.com/mcasrom/narrative-radar  
    - **Nodo:** Odroid-C2 · DietPi · 24/7
    """)
    st.success("✅ Sistema operativo. Pipeline cada 30 min.")

def mostrar_tab(tab_name, csv_path):
    if tab_name == "Keywords":
        mostrar_keywords()
        return
    if tab_name == "Histórico":
        mostrar_historico()
        return
    if tab_name == "Guía / HowTo":
        mostrar_howto()
        return

    st.header(tab_name)
    if not os.path.exists(csv_path):
        st.warning(f"No hay datos disponibles para el módulo: {tab_name}")
        return
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Error leyendo CSV: {e}"); return
    if df.empty:
        st.warning("El CSV está vacío."); return

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
                      labels={"date": "Fecha", "spread_index": "Índice"})
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
        generar_pdf()
        st.success("PDF generado exitosamente")
with col2:
    testigo = paths["Tendencias"]
    if os.path.exists(testigo):
        last_ingestion = datetime.fromtimestamp(os.path.getmtime(testigo)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_ingestion = "Archivo no encontrado"
    st.write(f"**Última ingestión de datos (Real):** {last_ingestion}")
    st.write("© 2026 M. Castillo | mybloggingnotes@gmail.com")
