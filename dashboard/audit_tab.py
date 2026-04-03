#!/usr/bin/env python3
# ============================================================
# audit_tab.py — Tab 🔍 Auditoría del Sistema
# Dashboard Narrative Radar España
# ============================================================

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))


def _load(fname):
    path = os.path.join(BASE_DIR, fname)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def _gauge(score, titulo="Score global", height=220):
    color = "#00C853" if score >= 75 else ("#FFD600" if score >= 50 else "#FF5252")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 32, "color": "white"}},
        title={"text": titulo, "font": {"size": 13, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(20,20,40,0.8)",
            "bordercolor": "rgba(255,255,255,0.15)",
            "steps": [
                {"range": [0,  50], "color": "rgba(255,82,82,0.2)"},
                {"range": [50, 75], "color": "rgba(255,214,0,0.2)"},
                {"range": [75,100], "color": "rgba(0,200,83,0.2)"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75, "value": 75
            },
        },
    ))
    fig.update_layout(
        height=height,
        margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    return fig


def _semaforo(score):
    if score >= 75: return "🟢"
    if score >= 50: return "🟡"
    return "🔴"




def _freshness_block():
    """Sección de frescura de CSVs — semáforo simple."""
    import os
    from datetime import datetime
    from pathlib import Path

    PROCESSED = Path(BASE_DIR)
    DATE_COLS = ["date", "fecha", "cycle", "last_update", "timestamp"]
    UMBRAL_OK = 2       # horas
    UMBRAL_CRIT = 24    # horas
    NOW = datetime.now()

    def detectar_col_fecha(df):
        for col in DATE_COLS:
            if col in df.columns:
                return col
        for col in df.columns:
            if any(k in col.lower() for k in ["date","fecha","time","cycle","update"]):
                return col
        return None

    def evaluar(path):
        try:
            import pandas as pd
            df = pd.read_csv(path)
            if df.empty:
                return "🔴", "vacío", None
            col = detectar_col_fecha(df)
            horas = None
            fecha_max = None
            if col:
                fechas = pd.to_datetime(df[col], errors="coerce").dropna()
                if not fechas.empty:
                    fecha_max = fechas.max()
                    horas = (NOW - fecha_max.to_pydatetime()).total_seconds() / 3600
            if horas is None:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                horas = (NOW - mtime).total_seconds() / 3600
            if horas > UMBRAL_CRIT:
                return "🔴", f"{horas:.0f}h", fecha_max
            elif horas > UMBRAL_OK:
                return "🟡", f"{horas:.1f}h", fecha_max
            else:
                return "🟢", f"{horas:.1f}h", fecha_max
        except Exception as e:
            return "🔴", f"error: {e}", None

    csvs = sorted(PROCESSED.glob("*.csv"))
    filas = []
    for p in csvs:
        if ".bak" in p.name:
            continue
        icono, edad, fecha_max = evaluar(p)
        fecha_str = fecha_max.strftime("%m-%d %H:%M") if fecha_max else "—"
        filas.append((icono, p.name, edad, fecha_str))

    parados = [f for f in filas if f[0] == "🔴"]
    retrasos = [f for f in filas if f[0] == "🟡"]
    oks = [f for f in filas if f[0] == "🟢"]

    st.divider()
    st.markdown("### 🗂 Frescura de CSVs")

    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 OK", len(oks))
    c2.metric("🟡 Retraso (>2h)", len(retrasos))
    c3.metric("🔴 Parados (>24h)", len(parados))

    if parados or retrasos:
        problemas = parados + retrasos
        import pandas as pd
        df_prob = pd.DataFrame(problemas, columns=["Estado","Archivo","Antigüedad","Último dato"])
        st.dataframe(df_prob, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos los CSVs están actualizados")

    with st.expander("Ver todos los CSVs"):
        import pandas as pd
        df_all = pd.DataFrame(filas, columns=["Estado","Archivo","Antigüedad","Último dato"])
        st.dataframe(df_all, use_container_width=True, hide_index=True)

def render_audit_tab():
    st.markdown("## 🔍 Auditoría del Sistema")
    st.markdown("Monitorización continua de la calidad del pipeline · auto-corrección automática si score < 50")

    # ── Cargar datos ────────────────────────────────────────
    df_latest  = _load("audit_quality_latest.csv")
    df_history = _load("audit_quality_history.csv")
    df_global  = _load("audit_global_summary.csv")
    df_acciones = _load("audit_autocorrections.csv")

    if df_latest.empty:
        st.warning("⚠️ No hay datos de auditoría todavía. Ejecuta `scripts/audit_quality.py` para iniciar.")
        st.code("cd /home/dietpi/narrative-radar/scripts && python3 audit_quality.py")
        return

    # ── Score global ────────────────────────────────────────
    score_global   = int(df_latest["score_global"].iloc[0]) if "score_global" in df_latest else 0
    score_datos    = int(df_latest["score_datos"].mean()) if "score_datos" in df_latest else 0
    _nlp_val = df_latest["score_nlp"].iloc[0] if "score_nlp" in df_latest else 0
    _rss_val = df_latest["score_rss"].iloc[0] if "score_rss" in df_latest else 0
    score_nlp = int(_nlp_val) if _nlp_val == _nlp_val else 0  # nan check
    score_rss = int(_rss_val) if _rss_val == _rss_val else 0  # nan check
    ts_ultimo      = df_latest["timestamp"].iloc[0] if "timestamp" in df_latest else "N/D"
    fuentes_act    = int(df_latest["fuentes_activas_6h"].iloc[0]) if "fuentes_activas_6h" in df_latest else 0
    fuentes_tot    = int(df_latest["fuentes_total"].iloc[0]) if "fuentes_total" in df_latest else 0

    # ── KPIs cabecera ───────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🕐 Última auditoría", ts_ultimo[:16] if len(str(ts_ultimo)) > 16 else ts_ultimo)
    c2.metric("📡 Fuentes RSS activas", f"{fuentes_act}/{fuentes_tot}")
    mods_ok   = (df_latest["score_datos"] >= 75).sum() if "score_datos" in df_latest else 0
    mods_warn = ((df_latest["score_datos"] >= 50) & (df_latest["score_datos"] < 75)).sum() if "score_datos" in df_latest else 0
    mods_err  = (df_latest["score_datos"] < 50).sum() if "score_datos" in df_latest else 0
    c3.metric("✅ Módulos OK / ⚠️ Aviso / ❌ Error", f"{mods_ok} / {mods_warn} / {mods_err}")
    n_acc = len(df_acciones) if not df_acciones.empty else 0
    c4.metric("🔧 Auto-correcciones", n_acc)

    st.divider()

    # ── Gauges ──────────────────────────────────────────────
    st.markdown("### 📊 Scores de calidad")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(_gauge(score_global, "🎯 Score Global"), use_container_width=True, key="aud_g_global")
    with g2:
        st.plotly_chart(_gauge(score_datos, "📁 Datos CSV"), use_container_width=True, key="aud_g_datos")
    with g3:
        st.plotly_chart(_gauge(score_nlp, "🧠 Coherencia NLP"), use_container_width=True, key="aud_g_nlp")
    with g4:
        st.plotly_chart(_gauge(score_rss, "📡 Fuentes RSS"), use_container_width=True, key="aud_g_rss")

    st.divider()

    # ── Semáforo por módulo ─────────────────────────────────
    st.markdown("### 🚦 Estado por módulo")

    if "score_datos" in df_latest and "modulo" in df_latest:
        df_mod = df_latest[["modulo","filas","pct_fechas_recientes","pct_nulos",
                             "score_datos","alerta","autocorregido"]].copy()
        df_mod = df_mod.sort_values("score_datos", ascending=True)

        # Gráfico barras horizontales
        bar_colors = ["#00C853" if s >= 75 else ("#FFD600" if s >= 50 else "#FF5252")
                      for s in df_mod["score_datos"]]
        fig_mod = go.Figure(go.Bar(
            x=df_mod["score_datos"],
            y=df_mod["modulo"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{s}" for s in df_mod["score_datos"]],
            textposition="outside",
        ))
        fig_mod.add_vline(x=75, line_dash="dash", line_color="white",
                          annotation_text="Bueno (75)", annotation_font_color="white")
        fig_mod.add_vline(x=50, line_dash="dot", line_color="orange",
                          annotation_text="Aviso (50)", annotation_font_color="orange")
        fig_mod.update_layout(
            title="Score de calidad por módulo CSV",
            xaxis=dict(range=[0, 115], showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(showgrid=False),
            height=500,
            margin=dict(t=50, b=30, l=200, r=60),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        st.plotly_chart(fig_mod, use_container_width=True, key="aud_modulos")

        # Tabla detallada
        st.markdown("**Detalle por módulo**")
        df_display = df_mod.copy()
        df_display["semaforo"] = df_display["score_datos"].apply(_semaforo)
        df_display["filas_recientes"] = (df_display["pct_fechas_recientes"] * 100).round(0).astype(int).astype(str) + "%"
        df_display["nulos"] = (df_display["pct_nulos"] * 100).round(1).astype(str) + "%"
        df_display["auto"] = df_display["autocorregido"].apply(lambda x: "✅" if x else "")
        df_show = df_display[["semaforo","modulo","filas","filas_recientes","nulos","score_datos","alerta","auto"]]
        df_show.columns = ["", "Módulo", "Filas", "% Recientes", "% Nulos", "Score", "Alerta", "🔧"]
        st.dataframe(df_show.reset_index(drop=True), use_container_width=True)

    st.divider()

    # ── Histórico de scores ─────────────────────────────────
    st.markdown("### 📈 Histórico de calidad del sistema")

    if not df_history.empty and "timestamp" in df_history and "score_global" in df_history:
        # Agrupar por timestamp (un score por ciclo)
        df_h = df_history.copy()
        df_h["timestamp"] = pd.to_datetime(df_h["timestamp"], errors="coerce")
        df_resumen = df_h.groupby("timestamp").agg(
            score_global=("score_global", "first"),
            score_datos=("score_datos", "mean"),
            score_nlp=("score_nlp", "first"),
            score_rss=("score_rss", "first"),
        ).reset_index()
        df_resumen = df_resumen.sort_values("timestamp")

        fig_hist = go.Figure()
        fig_hist.add_scatter(x=df_resumen["timestamp"], y=df_resumen["score_global"],
                             name="🎯 Global", line=dict(color="#00E676", width=2), mode="lines+markers")
        fig_hist.add_scatter(x=df_resumen["timestamp"], y=df_resumen["score_datos"],
                             name="📁 Datos", line=dict(color="#40C4FF", width=1.5, dash="dot"))
        fig_hist.add_scatter(x=df_resumen["timestamp"], y=df_resumen["score_nlp"],
                             name="🧠 NLP", line=dict(color="#CE93D8", width=1.5, dash="dash"))
        fig_hist.add_scatter(x=df_resumen["timestamp"], y=df_resumen["score_rss"],
                             name="📡 RSS", line=dict(color="#FFAB40", width=1.5, dash="longdash"))
        fig_hist.add_hline(y=75, line_dash="dash", line_color="rgba(0,200,83,0.4)",
                           annotation_text="Umbral bueno", annotation_font_color="white")
        fig_hist.add_hline(y=50, line_dash="dot", line_color="rgba(255,82,82,0.4)",
                           annotation_text="Umbral auto-corrección", annotation_font_color="orange")
        fig_hist.update_layout(
            title="Evolución del score de calidad (últimos 90 días)",
            xaxis_title="Fecha",
            yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            height=350,
            margin=dict(t=50, b=30),
            legend=dict(orientation="h", y=-0.25),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        st.plotly_chart(fig_hist, use_container_width=True, key="aud_historico")
    else:
        st.info("El histórico se irá construyendo con cada ciclo del pipeline.")

    st.divider()

    # ── Alertas activas ─────────────────────────────────────
    st.markdown("### 🚨 Alertas activas")

    alertas_mostradas = 0
    if "alerta" in df_latest.columns:
        for _, row in df_latest[df_latest["alerta"].astype(str).str.len() > 0].iterrows():
            score = row.get("score_datos", 0)
            if score < 50:
                st.error(f"❌ **{row['modulo']}** — {row['alerta']}")
            elif score < 75:
                st.warning(f"⚠️ **{row['modulo']}** — {row['alerta']}")
            alertas_mostradas += 1

    alerta_nlp = df_latest["alerta_nlp"].iloc[0] if "alerta_nlp" in df_latest.columns else ""
    alerta_rss = df_latest["alerta_rss"].iloc[0] if "alerta_rss" in df_latest.columns else ""

    if str(alerta_nlp).strip():
        if str(alerta_nlp) != "nan": st.warning(f"🧠 NLP — {alerta_nlp}")
        alertas_mostradas += 1
    if str(alerta_rss).strip():
        if str(alerta_rss) != "nan": st.warning(f"📡 RSS — {alerta_rss}")
        alertas_mostradas += 1

    if alertas_mostradas == 0:
        st.success("✅ No hay alertas activas — sistema operando correctamente")

    # ── Log de auto-correcciones ────────────────────────────
    if not df_acciones.empty:
        st.divider()
        st.markdown("### 🔧 Historial de auto-correcciones")
        st.dataframe(df_acciones.sort_values("timestamp", ascending=False).head(20),
                     use_container_width=True)
    _freshness_block()
