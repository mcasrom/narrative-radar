#!/usr/bin/env python3
# dashboard_central.py
# Centro de Mando Narrativo España 🇪🇸
# v2 — fallback automático con datos de muestra si no existen CSVs

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from audit_tab import render_audit_tab
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Centro de Mando Narrativo España", layout="wide")
st.title("Centro de Mando Narrativo España 🇪🇸")
st.markdown("Panel central que integra múltiples indicadores de noticias, narrativas y polarización.")

# -----------------------------
# Paths de CSV por tab
# -----------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
os.makedirs(base_dir, exist_ok=True)

paths = {
    "Radar Narrativo":    os.path.join(base_dir, "narratives_summary.csv"),
    "Radar Emocional":    os.path.join(base_dir, "emotions_summary.csv"),
    "Polarización":       os.path.join(base_dir, "polarization_summary.csv"),
    "Red de Actores":     os.path.join(base_dir, "actors_network.csv"),
    "Propagación":        os.path.join(base_dir, "propagation_summary.csv"),
    "Tendencias":         os.path.join(base_dir, "trends_summary.csv"),
    "Cobertura Gobierno": os.path.join(base_dir, "government_coverage.csv"),
    "Análisis Masivos":   os.path.join(base_dir, "mass_media_coverage.csv"),
    "Guía / HowTo PDF":   os.path.join(base_dir, "Guia_Centro_Mando_Narrativo.pdf"),
}

# -----------------------------
# Fallback — genera CSVs mínimos si no existen
# -----------------------------
def _generar_fallback():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
    rng = random.Random(42)

    fallbacks = {
        "narratives_summary.csv": pd.DataFrame([
            {"cluster": c, "cluster_label": c.lower(), "count": rng.randint(50, 300), "last_update": now}
            for c in ["Política", "Economía", "Internacional", "Sociedad", "Tecnología"]
        ]),
        "emotions_summary.csv": pd.DataFrame([
            {"emotion": e, "count": rng.randint(100, 600), "last_update": now}
            for e in ["Neutral", "Miedo", "Enfado", "Tristeza", "Sorpresa", "Positiva"]
        ]),
        "polarization_summary.csv": pd.DataFrame([
            {"date": d, "polarization_index": round(rng.uniform(0.3, 0.8), 3),
             "progressive_count": rng.randint(5, 20), "conservative_count": rng.randint(5, 20),
             "last_update": now}
            for d in dates[-15:]
        ]),
        "actors_network.csv": pd.DataFrame([
            {"source": s, "target": t, "weight": rng.randint(1, 10), "last_update": now}
            for s in ["elpais", "elmundo", "lavanguardia", "eldiario", "abc"]
            for t in ["elpais", "elmundo", "lavanguardia", "eldiario", "abc"]
            if s != t
        ]),
        "propagation_summary.csv": pd.DataFrame([
            {"date": d, "spread_index": round(rng.uniform(1, 8), 2),
             "news_count": rng.randint(10, 100), "sources_active": rng.randint(3, 15),
             "last_update": now}
            for d in dates[-15:]
        ]),
        "trends_summary.csv": pd.DataFrame([
            {"keyword": k, "count": rng.randint(50, 500), "last_update": now}
            for k in ["españa", "gobierno", "sánchez", "trump", "irán",
                      "economía", "elecciones", "europa", "pp", "psoe"]
        ]),
        "government_coverage.csv": pd.DataFrame([
            {"source": s, "count": rng.randint(50, 300),
             "alignment": rng.choice(["Pro-Gobierno", "Contra-Gobierno", "Neutral"]),
             "alignment_score": round(rng.uniform(-0.3, 0.3), 3), "last_update": now}
            for s in ["elpais", "elmundo", "lavanguardia", "eldiario", "abc",
                      "okdiario", "elespanol", "20minutos"]
        ]),
        "mass_media_coverage.csv": pd.DataFrame([
            {"last_update": d, "intensity_index": round(rng.uniform(20, 100), 2), "source": s}
            for s in ["El País", "El Mundo", "La Vanguardia", "elDiario"]
            for d in dates[-10:]
        ]),
    }

    generados = []
    for fname, df in fallbacks.items():
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            df.to_csv(fpath, index=False)
            generados.append(fname)

    return generados

# Ejecutar fallback silencioso
_generados = _generar_fallback()
if _generados:
    st.info(
        f"⚠️ Datos de muestra cargados para: {', '.join(_generados)}. "
        "El pipeline del Odroid actualizará con datos reales en el próximo ciclo.",
        icon="ℹ️"
    )

# -----------------------------
# Función para mostrar tabs
# -----------------------------
def mostrar_tab(tab_name, csv_path):
    st.header(tab_name)

    if not os.path.exists(csv_path):
        st.warning(f"No hay datos disponibles para: {tab_name}")
        return

    df = pd.read_csv(csv_path)

    if df.empty:
        st.warning(f"El CSV de {tab_name} está vacío.")
        return

    # ── Radar Narrativo ──────────────────────────────────────
    if tab_name == "Radar Narrativo":
        col = "cluster_label" if "cluster_label" in df.columns else "cluster"
        fig = px.bar(df, x=col, y="count", color=col,
                     title="Clusters de narrativas detectadas")
        fig.update_layout(xaxis_title="Cluster", yaxis_title="Noticias", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Radar Emocional ──────────────────────────────────────
    elif tab_name == "Radar Emocional":
        fig = px.pie(df, names="emotion", values="count",
                     title="Distribución de emociones en noticias recientes",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Polarización ─────────────────────────────────────────
    elif tab_name == "Polarización":
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date")
        fig = px.line(df, x="date", y="polarization_index",
                      title="Índice de polarización — últimos 90 días",
                      markers=True)
        fig.add_hline(y=0.5, line_dash="dash", line_color="orange",
                      annotation_text="Umbral medio")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Polarización (0-1)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Red de Actores ───────────────────────────────────────
    elif tab_name == "Red de Actores":
        fig = px.scatter(df, x="source", y="target", size="weight", color="weight",
                         title="Red de actores (peso de conexiones)",
                         hover_data=["last_update"] if "last_update" in df.columns else None)
        fig.update_layout(xaxis_title="Fuente", yaxis_title="Destino")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Propagación ──────────────────────────────────────────
    elif tab_name == "Propagación":
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date")
        fig = px.area(df, x="date", y="spread_index",
                      title="Propagación de noticias — últimos 90 días")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Índice de propagación")
        st.plotly_chart(fig, use_container_width=True)
        if "news_count" in df.columns:
            col1, col2 = st.columns(2)
            col1.metric("Máx. propagación", f"{df['spread_index'].max():.2f}")
            col2.metric("Noticias procesadas", int(df["news_count"].sum()))
        st.dataframe(df, use_container_width=True)

    # ── Tendencias ───────────────────────────────────────────
    elif tab_name == "Tendencias":
        df = df.sort_values("count", ascending=False).head(20)
        fig = px.bar(df, x="keyword", y="count", color="count",
                     title="Top 20 palabras clave más frecuentes",
                     color_continuous_scale="Blues")
        fig.update_layout(xaxis_title="Palabra clave", yaxis_title="Menciones",
                          xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Cobertura Gobierno ───────────────────────────────────
    elif tab_name == "Cobertura Gobierno":
        if "alignment_score" in df.columns:
            df = df.sort_values("alignment_score")
            fig = px.bar(df, x="source", y="alignment_score", color="alignment",
                         title="Alineamiento mediático respecto al Gobierno",
                         color_discrete_map={
                             "Pro-Gobierno": "#1565C0",
                             "Contra-Gobierno": "#C62828",
                             "Neutral": "#757575"
                         })
            fig.add_hline(y=0, line_color="white", line_width=1)
        else:
            fig = px.bar(df, x="source", y="count", color="alignment",
                         title="Cobertura mediática del gobierno")
        fig.update_layout(xaxis_title="Fuente", yaxis_title="Score alineamiento")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

    # ── Análisis Masivos ─────────────────────────────────────
    elif tab_name == "Análisis Masivos":
        fig = px.line(df, x="last_update", y="intensity_index", color="source",
                      markers=True, title="Intensidad mediática por fuente — últimos 90 días")
        fig.update_layout(xaxis_title="Fecha", yaxis_title="Intensidad",
                          legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)


# -----------------------------
# Función tab Guía HowTo
# -----------------------------
def mostrar_howto_tab():
    st.header("Guía de Uso del Centro de Mando Narrativo 🇪🇸")
    st.markdown("""
    Bienvenido al **Centro de Mando Narrativo España**. Este panel integra múltiples
    indicadores extraídos en tiempo real de más de 25 fuentes de noticias españolas.

    ### Tabs disponibles
    - **Radar Narrativo** — clusters temáticos de noticias agrupadas por NLP
    - **Radar Emocional** — distribución de emociones detectadas
    - **Polarización** — índice de polarización mediática diario (últimos 90 días)
    - **Red de Actores** — conexiones y pesos entre medios de comunicación
    - **Propagación** — velocidad de difusión de noticias (últimos 90 días)
    - **Tendencias** — top 20 palabras clave más frecuentes
    - **Cobertura Gobierno** — alineamiento mediático respecto al gobierno
    - **Análisis Masivos** — intensidad mediática por fuente

    ### Actualización de datos
    El pipeline corre automáticamente en el servidor cada 6 horas.
    Los gráficos muestran siempre los **últimos 90 días**.
    """)

    pdf_path = paths["Guía / HowTo PDF"]
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Descargar PDF completo", f.read(),
                               file_name="Guia_Centro_Mando_Narrativo.pdf",
                               mime="application/pdf")
    st.info("Este tab no depende de CSVs y siempre está disponible.")


# -----------------------------
# Render tabs
# -----------------------------
visual_tabs = [t for t in paths if t != "Guía / HowTo PDF"] + ["Guía / HowTo", "🔍 Auditoría"]
tabs = st.tabs(visual_tabs)

for tab, tab_name in zip(tabs, visual_tabs):
    with tab:
        if tab_name == "Guía / HowTo":
            mostrar_howto_tab()
        elif tab_name == "🔍 Auditoría":
            render_audit_tab()
        else:
            mostrar_tab(tab_name, paths[tab_name])
