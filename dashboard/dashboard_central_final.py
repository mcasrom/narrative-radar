#!/usr/bin/env python3
# dashboard_central_final.py
# Centro de Mando Narrativo España 🇪🇸
# Autor: M. Castillo <mybloggingnotes@gmail.com>

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
from audit_tab import render_audit_tab

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
    "Desinformación": os.path.join(base_dir, "disinfo_alerts.csv"),
    "Coordinación": os.path.join(base_dir, "coordination_alerts.csv"),
    "Agenda-Setting": os.path.join(base_dir, "agenda_score.csv"),
    "Sentimiento NLP": os.path.join(base_dir, "sentiment_summary.csv"),
    "Mapa Geográfico": os.path.join(base_dir, "geo_summary.csv"),
    "Temas Virales": os.path.join(base_dir, "viral_topics.csv"),
    "Personajes": os.path.join(base_dir, "personas_summary.csv"),
    "Diversidad": os.path.join(base_dir, "diversity_index.csv"),
    "Keywords": None,
    "🔍 Auditoría": None,
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


def mostrar_keywords_gestion():
    """Panel de gestion, auditoria y autolearning de keywords."""
    import json

    CONFIG_KW = os.path.join(base_dir, "keywords_config.json")
    HISTORY_KW = keywords_paths.get("history", "")

    def load_cfg():
        if os.path.exists(CONFIG_KW):
            try:
                return json.loads(open(CONFIG_KW).read())
            except Exception:
                pass
        return {"stopwords_custom": [], "keywords_pinned": [], "keywords_blocked": [],
                "autolearn": {"enabled": True, "min_cycles_inactive": 10, "max_pct_change_threshold": 5},
                "autolearn_suggestions": []}

    def save_cfg(cfg):
        from datetime import datetime as _dt
        cfg["last_updated"] = _dt.now().strftime("%Y-%m-%d %H:%M")
        open(CONFIG_KW, "w").write(json.dumps(cfg, indent=2, ensure_ascii=False))

    cfg = load_cfg()

    st.markdown("---")
    st.header("Gestion de Keywords")

    # Proteccion con password
    import streamlit as _st
    try:
        _admin_pw = _st.secrets["admin"]["password"]
    except Exception:
        _admin_pw = "yuuwwsjibbuzalnc"
    _pw_input = st.text_input("Password de administrador:", type="password", key="admin_pw_kw")
    if _pw_input != _admin_pw:
        st.warning("Introduce la password de administrador para acceder al panel de gestion.")
        return

    tab_act, tab_blq, tab_stop, tab_auto = st.tabs([
        "Activas & Fijadas",
        "Bloqueadas (inutiles)",
        "Stopwords custom",
        "Autolearning"
    ])

    with tab_act:
        st.subheader("Keywords activas en el pipeline")
        if os.path.exists(HISTORY_KW):
            df_h = pd.read_csv(HISTORY_KW)
            cycles = sorted(df_h["cycle"].unique())
            df_top = df_h.groupby("keyword")["count"].agg(["sum", "mean", "count"]).reset_index()
            df_top.columns = ["keyword", "score_total", "score_medio", "n_ciclos"]
            df_top["pinned"] = df_top["keyword"].isin(cfg.get("keywords_pinned", []))
            df_top["bloqueada"] = df_top["keyword"].isin(cfg.get("keywords_blocked", []))
            df_top = df_top[~df_top["bloqueada"]].sort_values("score_total", ascending=False)
            st.dataframe(df_top[["keyword", "score_total", "score_medio", "n_ciclos", "pinned"]],
                         use_container_width=True, height=300)
            st.caption(f"{len(df_top)} keywords activas | {len(cycles)} ciclos acumulados")
            st.subheader("Fijar keywords prioritarias")
            all_kws = df_top["keyword"].tolist()
            current_pinned = cfg.get("keywords_pinned", [])
            new_pinned = st.multiselect("Keywords fijadas (siempre incluidas):", all_kws,
                                        default=current_pinned, key="kw_pin")
            if st.button("Guardar keywords fijadas", key="save_pin"):
                cfg["keywords_pinned"] = new_pinned
                save_cfg(cfg)
                st.success(f"{len(new_pinned)} keywords fijadas guardadas")
                st.rerun()
        else:
            st.info("Sin historico de keywords aun.")

    with tab_blq:
        st.subheader("Keywords bloqueadas (excluidas del pipeline)")
        blocked = cfg.get("keywords_blocked", [])
        if blocked:
            st.dataframe(pd.DataFrame({"keyword": blocked}), use_container_width=True)
        else:
            st.info("No hay keywords bloqueadas.")
        st.subheader("Bloquear keywords manualmente")
        if os.path.exists(HISTORY_KW):
            df_h2 = pd.read_csv(HISTORY_KW)
            all_kws2 = df_h2["keyword"].unique().tolist()
            to_block = st.multiselect("Selecciona keywords a bloquear:", all_kws2, key="kw_block")
            if st.button("Bloquear seleccionadas", key="btn_block"):
                cfg["keywords_blocked"] = list(set(blocked + to_block))
                save_cfg(cfg)
                st.success(f"{len(to_block)} keywords bloqueadas")
                st.rerun()
        if blocked:
            to_unblock = st.multiselect("Desbloquear keywords:", blocked, key="kw_unblock")
            if st.button("Desbloquear", key="btn_unblock"):
                cfg["keywords_blocked"] = [k for k in blocked if k not in to_unblock]
                save_cfg(cfg)
                st.success(f"{len(to_unblock)} keywords desbloqueadas")
                st.rerun()

    with tab_stop:
        st.subheader("Stopwords personalizadas")
        sw = cfg.get("stopwords_custom", [])
        st.info("Stopwords base: 27 palabras (articulos, preposiciones, etc.)")
        st.write(f"Stopwords custom anadidas: **{len(sw)}**")
        if sw:
            st.dataframe(pd.DataFrame({"stopword": sw}), use_container_width=True)
        new_sw = st.text_input("Anadir stopword:", key="sw_input")
        if st.button("Anadir stopword", key="btn_sw"):
            if new_sw.strip() and new_sw.strip() not in sw:
                sw.append(new_sw.strip().lower())
                cfg["stopwords_custom"] = sw
                save_cfg(cfg)
                st.success(f"'{new_sw}' anadida — se aplicara en el proximo ciclo")
                st.rerun()
        if sw:
            to_remove = st.multiselect("Eliminar stopwords:", sw, key="sw_remove")
            if st.button("Eliminar seleccionadas", key="btn_sw_rm"):
                cfg["stopwords_custom"] = [s for s in sw if s not in to_remove]
                save_cfg(cfg)
                st.success("Stopwords eliminadas")
                st.rerun()

    with tab_auto:
        st.subheader("Autolearning - Sugerencias automaticas")
        al = cfg.get("autolearn", {})
        suggestions = cfg.get("autolearn_suggestions", [])
        col1, col2 = st.columns(2)
        with col1:
            enabled = st.toggle("Autolearning activo", value=al.get("enabled", True), key="al_toggle")
            min_cycles = st.slider("Ciclos minimos inactivos:", 5, 30,
                                   al.get("min_cycles_inactive", 10), key="al_cycles")
        with col2:
            threshold = st.slider("Umbral variacion maxima (CV%):", 1, 20,
                                  al.get("max_pct_change_threshold", 5), key="al_thresh")
            if st.button("Guardar config autolearning", key="save_al"):
                cfg["autolearn"] = {"enabled": enabled, "min_cycles_inactive": min_cycles,
                                    "max_pct_change_threshold": threshold}
                save_cfg(cfg)
                st.success("Config autolearning guardada")
        st.markdown("---")
        if suggestions:
            st.warning(f"{len(suggestions)} keywords detectadas como poco utiles")
            st.dataframe(pd.DataFrame({"keyword_sugerida_para_bloqueo": suggestions}),
                         use_container_width=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Bloquear TODAS las sugeridas", key="block_all_sugg"):
                    blocked2 = cfg.get("keywords_blocked", [])
                    cfg["keywords_blocked"] = list(set(blocked2 + suggestions))
                    cfg["autolearn_suggestions"] = []
                    save_cfg(cfg)
                    st.success(f"{len(suggestions)} keywords bloqueadas")
                    st.rerun()
            with col_b:
                to_keep = st.multiselect("Mantener activas:", suggestions, key="keep_sugg")
                if st.button("Bloquear el resto", key="block_rest"):
                    to_block2 = [k for k in suggestions if k not in to_keep]
                    blocked3 = cfg.get("keywords_blocked", [])
                    cfg["keywords_blocked"] = list(set(blocked3 + to_block2))
                    cfg["autolearn_suggestions"] = []
                    save_cfg(cfg)
                    st.success(f"{len(to_block2)} bloqueadas, {len(to_keep)} mantenidas")
                    st.rerun()
        else:
            st.success("No hay sugerencias pendientes - pipeline limpio")
            if os.path.exists(HISTORY_KW):
                cycles_total = pd.read_csv(HISTORY_KW)["cycle"].nunique()
                if cycles_total < min_cycles:
                    st.info(f"Acumulando ciclos: {cycles_total}/{min_cycles} para autolearning")
        last = cfg.get("last_updated", "")
        if last:
            st.caption(f"Config actualizada: {last}")


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
            if len(df) >= 5:
                fig = px.bar(df, x="keyword", y="delta", color="pct_change",
                             title="Keywords con mayor bajada (último ciclo)",
                             labels={"keyword": "Keyword", "delta": "Decremento", "pct_change": "% cambio"},
                             color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            elif len(df) > 0:
                st.info(f"Solo {len(df)} keyword(s) decayente(s) detectada(s) — acumulando histórico (mín. 5 para gráfico)")
                st.dataframe(df[["keyword","count_last","count_prev","delta","pct_change"]], use_container_width=True)
            else:
                st.info("Sin keywords decayentes en este ciclo — todas las palabras clave están en alza.")
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
    mostrar_keywords_gestion()

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
    try:
        _mostrar_tab_inner(tab_name, csv_path)
    except Exception as e:
        st.error(f"Error en tab '{tab_name}': {type(e).__name__}: {e}")
        import traceback
        st.code(traceback.format_exc())

def _mostrar_tab_inner(tab_name, csv_path):
    if tab_name == "Temas Virales":
        st.header("Temas Virales 🔥")
        st.markdown("Keywords que **explotan >200%** en menos de 2 horas respecto al período anterior.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún."); return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        if df.empty:
            st.info("Sin temas virales detectados en este ciclo."); return
        col1, col2, col3 = st.columns(3)
        col1.metric("Temas virales", len(df))
        col2.metric("Alto score (≥60)", len(df[df["viral_score"]>=60]))
        col3.metric("Keyword top", df.iloc[0]["keyword"] if len(df)>0 else "-")
        fig = px.bar(df.head(15).sort_values("viral_score"),
                     x="viral_score", y="keyword", orientation="h",
                     color="ratio", color_continuous_scale="Hot",
                     title="Score viral por keyword",
                     labels={"viral_score":"Score viral","keyword":"Keyword","ratio":"Multiplicador"})
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df[["keyword","viral_score","ratio","count_now","count_base","sources"]],
                     use_container_width=True)
        return

    if tab_name == "Personajes":
        st.header("Seguimiento de Personajes 👤")
        st.markdown("Menciones y sentimiento de **personajes políticos clave** en los medios monitorizados.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún."); return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        df = df[df["mentions"]>0]
        if df.empty:
            st.info("Sin menciones detectadas."); return
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df.sort_values("mentions"),
                         x="mentions", y="persona", orientation="h",
                         color="sentiment_score",
                         color_continuous_scale="RdYlGn",
                         color_continuous_midpoint=0,
                         title="Menciones por personaje",
                         labels={"mentions":"Menciones","persona":"Personaje","sentiment_score":"Sentimiento"})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df.sort_values("sentiment_score"),
                          x="sentiment_score", y="persona", orientation="h",
                          color="sentiment_score",
                          color_continuous_scale="RdYlGn",
                          color_continuous_midpoint=0,
                          title="Score de sentimiento por personaje",
                          labels={"sentiment_score":"Score","persona":"Personaje"})
            st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df[["persona","mentions","positive","negative","neutral","sentiment_score","last_title"]],
                     use_container_width=True)
        return

    if tab_name == "Diversidad":
        st.header("Índice de Diversidad Informativa 📊")
        st.markdown("Mide cuántos temas **únicos** publica cada medio vs cuántos **replica** de otros.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún."); return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        col1, col2, col3 = st.columns(3)
        col1.metric("Fuente más diversa", df.iloc[0]["source"] if len(df)>0 else "-")
        col2.metric("Score máximo", f"{df['diversity_score'].max():.1f}" if len(df)>0 else "-")
        col3.metric("Score medio", f"{df['diversity_score'].mean():.1f}" if len(df)>0 else "-")
        fig = px.bar(df.sort_values("diversity_score"),
                     x="diversity_score", y="source", orientation="h",
                     color="originality",
                     color_continuous_scale="Viridis",
                     title="Índice de diversidad por fuente",
                     labels={"diversity_score":"Score diversidad","source":"Fuente","originality":"Originalidad"})
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🏆 Más diversos")
            st.dataframe(df.head(5)[["source","diversity_score","originality","news_count"]],
                         use_container_width=True)
        with col_b:
            st.subheader("📋 Menos originales")
            st.dataframe(df.tail(5)[["source","diversity_score","originality","repeated_news"]],
                         use_container_width=True)
        return

    if tab_name == "Mapa Geográfico":
        st.header("Mapa Geográfico 🗺️")
        st.markdown("Menciones de **Comunidades Autónomas** en titulares de los últimos ciclos.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún."); return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return

        col1, col2, col3 = st.columns(3)
        col1.metric("Total menciones", int(df["mentions"].sum()))
        col2.metric("CCAs con menciones", int((df["mentions"]>0).sum()))
        col3.metric("CCAA líder", df.loc[df["mentions"].idxmax(),"ccaa"] if len(df)>0 else "-")

        # Mapa usando scattergeo con coordenadas de capitales de CCAA
        CCAA_COORDS = {
            "Madrid":{"lat":40.42,"lon":-3.70},"Cataluña":{"lat":41.38,"lon":2.17},
            "Andalucía":{"lat":37.39,"lon":-5.99},"Comunidad Valenciana":{"lat":39.47,"lon":-0.38},
            "País Vasco":{"lat":43.26,"lon":-2.93},"Galicia":{"lat":42.88,"lon":-8.54},
            "Castilla y León":{"lat":41.65,"lon":-4.72},"Aragón":{"lat":41.65,"lon":-0.89},
            "Murcia":{"lat":37.98,"lon":-1.13},"Navarra":{"lat":42.82,"lon":-1.64},
            "Asturias":{"lat":43.36,"lon":-5.85},"Extremadura":{"lat":39.47,"lon":-6.37},
            "La Rioja":{"lat":42.47,"lon":-2.45},"Cantabria":{"lat":43.18,"lon":-3.99},
            "Baleares":{"lat":39.57,"lon":2.65},"Canarias":{"lat":28.29,"lon":-15.63},
            "Castilla-La Mancha":{"lat":39.86,"lon":-4.02},"Ceuta":{"lat":35.89,"lon":-5.32},
            "Melilla":{"lat":35.29,"lon":-2.94},
        }
        df_map = df[df["mentions"]>0].copy()
        df_map["lat"] = df_map["ccaa"].map(lambda x: CCAA_COORDS.get(x,{}).get("lat"))
        df_map["lon"] = df_map["ccaa"].map(lambda x: CCAA_COORDS.get(x,{}).get("lon"))
        df_map = df_map.dropna(subset=["lat","lon"])
        fig = px.scatter_geo(
            df_map, lat="lat", lon="lon",
            size="mentions", color="mentions",
            hover_name="ccaa", hover_data={"mentions":True,"lat":False,"lon":False},
            color_continuous_scale="Reds",
            size_max=40,
            title="Intensidad informativa por Comunidad Autónoma",
        )
        fig.update_geos(
            center={"lat":40.4,"lon":-3.7}, projection_scale=4,
            scope="europe",
            showland=True, landcolor="#f0f0f0",
            showcoastlines=True, coastlinecolor="#cccccc",
            showcountries=True, countrycolor="#aaaaaa",
        )
        fig.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(df[df["mentions"]>0].sort_values("mentions"),
                      x="mentions", y="ccaa", orientation="h",
                      color="mentions", color_continuous_scale="Reds",
                      title="Ranking de menciones por CCAA",
                      labels={"mentions":"Menciones","ccaa":"CCAA"})
        fig2.update_layout(height=450)
        st.plotly_chart(fig2, use_container_width=True)
        return

    if tab_name == "Sentimiento NLP":
        st.header("Análisis de Sentimiento NLP 🧠")
        st.markdown("Sentimiento real de titulares usando léxico expandido español — **3200+ titulares analizados en < 4 segundos**.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún — se generarán en el próximo ciclo.")
            return
        try:
            df = pd.read_csv(csv_path)
            by_source_path = os.path.join(base_dir, "sentiment_by_source.csv")
            df_source = pd.read_csv(by_source_path) if os.path.exists(by_source_path) else pd.DataFrame()
        except Exception as e:
            st.error(f"Error: {e}"); return

        col1, col2, col3 = st.columns(3)
        if len(df) > 0:
            pos = df[df["sentiment"]=="positivo"]["count"].sum() if "count" in df.columns else 0
            neg = df[df["sentiment"]=="negativo"]["count"].sum() if "count" in df.columns else 0
            neu = df[df["sentiment"]=="neutral"]["count"].sum() if "count" in df.columns else 0
            col1.metric("Positivos", f"{pos} ({pos/(pos+neg+neu)*100:.1f}%)" if pos+neg+neu>0 else "0")
            col2.metric("Negativos", f"{neg} ({neg/(pos+neg+neu)*100:.1f}%)" if pos+neg+neu>0 else "0")
            col3.metric("Neutrales", f"{neu} ({neu/(pos+neg+neu)*100:.1f}%)" if pos+neg+neu>0 else "0")

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df, values="count", names="sentiment",
                         title="Distribución global de sentimiento",
                         color="sentiment",
                         color_discrete_map={"positivo":"#2ECC71","negativo":"#E74C3C","neutral":"#95A5A6"})
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            if len(df_source) > 0:
                fig2 = px.bar(df_source.sort_values("negativity_pct", ascending=True).tail(15),
                              x="negativity_pct", y="source", orientation="h",
                              color="avg_score",
                              title="% negativo por fuente",
                              labels={"negativity_pct":"% negativo","source":"Fuente"},
                              color_continuous_scale="RdYlGn")
                st.plotly_chart(fig2, use_container_width=True)

        if len(df_source) > 0:
            st.subheader("Sentimiento por fuente")
            st.dataframe(df_source[["source","avg_score","positivity_pct","negativity_pct","total"]].sort_values("avg_score", ascending=False),
                         use_container_width=True)
        return

    if tab_name == "Agenda-Setting":
        st.header("Score de Agenda-Setting 📡")
        st.markdown("Mide qué medios **marcan agenda** (publican primero los temas) vs cuáles **siguen** la agenda de otros.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún — se generarán en el próximo ciclo.")
            return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        if df.empty:
            st.warning("Sin datos disponibles."); return

        col1, col2, col3 = st.columns(3)
        marcadores = df[df["role"]=="Marcador de agenda"]
        seguidores = df[df["role"]=="Seguidor"]
        col1.metric("Marcadores de agenda", len(marcadores))
        col2.metric("Seguidores", len(seguidores))
        col3.metric("Temas analizados", int(df["topics_total"].sum()//2))

        fig = px.bar(df.sort_values("agenda_score", ascending=True).tail(20),
                     x="agenda_score", y="source", orientation="h",
                     color="role",
                     title="Score de agenda-setting por fuente",
                     labels={"agenda_score":"Score (%)","source":"Fuente","role":"Rol"},
                     color_discrete_map={
                         "Marcador de agenda":"#C00000",
                         "Mixto":"#FF9900",
                         "Seguidor":"#1F77B4",
                         "Independiente":"#888888"
                     })
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🔴 Marcadores de agenda")
            st.dataframe(df[df["role"]=="Marcador de agenda"][["source","agenda_score","times_first","topics_total"]],
                         use_container_width=True)
        with col_b:
            st.subheader("🔵 Seguidores")
            st.dataframe(df[df["role"].isin(["Seguidor","Mixto"])][["source","agenda_score","follower_score","topics_total"]],
                         use_container_width=True)
        return

    if tab_name == "Coordinación":
        st.header("Narrativas Coordinadas 🔴")
        st.markdown("Detección de grupos de medios que publican titulares semánticamente similares en ventanas de **2 horas**.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún — se generarán en el próximo ciclo.")
            return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        if df.empty:
            st.info("Sin narrativas coordinadas detectadas en este ciclo.")
            return

        col1, col2, col3 = st.columns(3)
        col1.metric("Eventos detectados", len(df))
        col2.metric("Alto score (≥50)", len(df[df["coord_score"]>=50]))
        col3.metric("Max fuentes coordinadas", int(df["n_sources"].max()) if len(df)>0 else 0)

        fig = px.bar(df.head(15), x="coord_score", y="representative",
                     orientation="h", color="n_sources",
                     title="Narrativas coordinadas por score",
                     labels={"coord_score":"Score coordinación","representative":"Titular","n_sources":"Nº fuentes"},
                     color_continuous_scale="Reds")
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detalle de eventos")
        st.dataframe(df[["window","coord_score","n_sources","sources","representative"]],
                     use_container_width=True)
        return

    if tab_name == "Desinformación":
        st.header("Detector de Desinformación ⚠️")
        st.markdown("Alertas generadas cruzando titulares con bulos verificados de **maldita.es** y **newtral.es** mediante similitud TF-IDF.")
        if not os.path.exists(csv_path):
            st.warning("Sin datos aún — se generarán en el próximo ciclo.")
            return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error: {e}"); return
        if df.empty:
            st.success("✅ Sin alertas activas — no se detectó desinformación en este ciclo.")
            return
        col1, col2, col3 = st.columns(3)
        col1.metric("Total alertas", len(df))
        col2.metric("Alto riesgo (≥60)", len(df[df["risk_score"]>=60]))
        col3.metric("Fuentes afectadas", df["news_source"].nunique())
        fig = px.bar(df.head(20), x="news_source", y="risk_score", color="risk_score",
                     title="Score de riesgo por fuente",
                     color_continuous_scale="Reds",
                     labels={"news_source":"Fuente","risk_score":"Score riesgo"})
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Detalle de alertas")
        st.dataframe(df[["news_source","risk_score","similarity","news_title","bulo_source","bulo_title"]],
                     use_container_width=True)
        return
    if tab_name == "Keywords":
        mostrar_keywords()
        return
    if tab_name == "Histórico":
        mostrar_historico()
        return
    if tab_name == "Guía / HowTo":
        mostrar_howto()
        return
    if tab_name == "🔍 Auditoría":
        render_audit_tab()
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
    try:
        from gen_guia_narrativa import generar_pdf_completo
        return generar_pdf_completo(base_dir, current_dir, paths)
    except ImportError:
        # Fallback: generador mínimo original (fpdf)
        from fpdf import FPDF
        import os
        from datetime import datetime
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
        texto = f"Centro de Mando Narrativo España\nAutor: M. Castillo\nFecha: {fecha_pdf}\nCSV: data/processed/"
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
# ── Briefing diario descargable ──────────────────────────────────
briefing_pdf = os.path.join(base_dir, "briefing_diario.pdf")
if os.path.exists(briefing_pdf):
    with open(briefing_pdf, "rb") as _f:
        _pdf_bytes = _f.read()
    _mtime = datetime.fromtimestamp(os.path.getmtime(briefing_pdf)).strftime("%Y-%m-%d %H:%M")
    st.download_button(
        label=f"📥 Descargar Briefing Diario (PDF) — {_mtime}",
        data=_pdf_bytes,
        file_name=f"briefing_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.info("Briefing diario no disponible aún — se genera a las 07:08 y 19:08.")

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
