#!/usr/bin/env python3
"""
patch_keywords_mgmt.py
Inserta la función mostrar_keywords_gestion() en dashboard_central_final.py
y actualiza trends_analysis.py con soporte de keywords_config.json
Ejecutar desde: /home/dietpi/narrative-radar/
"""
from pathlib import Path
import json, ast, shutil
from datetime import datetime

BASE = Path(__file__).parent
DASH = BASE / "dashboard/dashboard_central_final.py"
TRENDS = BASE / "scripts/trends_analysis.py"
CONFIG = BASE / "data/processed/keywords_config.json"

# ── 0. Backup ──────────────────────────────────────────────────────
ts = datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy(DASH, DASH.parent / f"dashboard_central_final_bak_{ts}.py")
shutil.copy(TRENDS, TRENDS.parent / f"trends_analysis_bak_{ts}.py")
print(f"✅ Backups creados ({ts})")

# ── 1. Crear keywords_config.json si no existe ────────────────────
if not CONFIG.exists():
    cfg = {
        "version": 1,
        "stopwords_custom": [],
        "keywords_pinned": [],
        "keywords_blocked": [],
        "autolearn": {
            "enabled": True,
            "min_cycles_inactive": 10,
            "max_pct_change_threshold": 5
        },
        "autolearn_suggestions": [],
        "last_updated": ""
    }
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print("✅ keywords_config.json creado")
else:
    print("✅ keywords_config.json ya existe")

# ── 2. Actualizar trends_analysis.py ─────────────────────────────
NEW_TRENDS = '''#!/usr/bin/env python3
"""
trends_analysis.py
Extrae tendencias reales de palabras clave desde titulares usando TF-IDF.
Lee:     data/processed/news_summary.csv
         data/processed/keywords_config.json
Genera:  data/processed/trends_summary.csv
         data/processed/trends_history.csv
"""
import pandas as pd, os, json, numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT   = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/news_summary.csv"))
OUTPUT  = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/trends_summary.csv"))
HISTORY = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/trends_history.csv"))
CONFIG  = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/keywords_config.json"))

STOPWORDS_BASE = [
    "de","la","el","en","y","a","que","los","del","se","las","por","un","con","una","su","al","es","para",
    "como","mas","pero","sus","le","ya","o","este","fue","ha","lo","si","sobre","entre","cuando","hasta",
    "sin","no","te","le","da","hay","muy","bien","tambien","despues","antes","donde","desde","segun"
]

cfg = {}
if os.path.exists(CONFIG):
    try:
        cfg = json.loads(open(CONFIG).read())
    except Exception:
        cfg = {}

stopwords_custom = cfg.get("stopwords_custom", [])
keywords_blocked = set(cfg.get("keywords_blocked", []))
keywords_pinned  = cfg.get("keywords_pinned", [])
STOPWORDS = list(set(STOPWORDS_BASE + stopwords_custom))

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

titles = df["title"].fillna("").tolist()
now = datetime.now().strftime("%Y-%m-%d %H:%M")

vectorizer = TfidfVectorizer(stop_words=STOPWORDS, max_features=200, ngram_range=(1,2), min_df=2)
X = vectorizer.fit_transform(titles)
scores = X.sum(axis=0).A1
words  = vectorizer.get_feature_names_out()
top_idx = scores.argsort()[::-1][:50]

rows = []
for i in top_idx:
    kw = words[i]
    if kw in keywords_blocked:
        continue
    rows.append({"keyword": kw, "count": int(round(scores[i]*100)), "last_update": now})
    if len(rows) >= 30:
        break

pinned_rows = [{"keyword": kw, "count": 999, "last_update": now}
               for kw in keywords_pinned if kw not in [r["keyword"] for r in rows]]
result = pd.DataFrame(pinned_rows + rows)
result.to_csv(OUTPUT, index=False)

result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), result], ignore_index=True)
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)
print(f"Tendencias: {len(result)} keywords | {len(keywords_blocked)} bloqueadas | {len(keywords_pinned)} fijadas")

# Autolearn
al = cfg.get("autolearn", {})
if al.get("enabled") and os.path.exists(HISTORY):
    hist_full = pd.read_csv(HISTORY)
    cycles = sorted(hist_full["cycle"].unique())
    min_cycles = al.get("min_cycles_inactive", 10)
    threshold  = al.get("max_pct_change_threshold", 5)
    if len(cycles) >= min_cycles:
        recent = hist_full[hist_full["cycle"].isin(cycles[-min_cycles:])]
        kw_counts = recent.groupby("keyword")["count"].agg(["mean","std"]).reset_index()
        kw_counts["cv"] = (kw_counts["std"] / kw_counts["mean"].replace(0, 1)) * 100
        inactive = kw_counts[kw_counts["cv"] < threshold]["keyword"].tolist()
        suggestions = cfg.get("autolearn_suggestions", [])
        new_sugg = [kw for kw in inactive if kw not in suggestions and kw not in keywords_blocked]
        if new_sugg:
            cfg["autolearn_suggestions"] = suggestions + new_sugg
            cfg["last_updated"] = now
            open(CONFIG, "w").write(json.dumps(cfg, indent=2, ensure_ascii=False))
            print(f"Autolearn: {len(new_sugg)} keywords sugeridas para revision")
'''

TRENDS.write_text(NEW_TRENDS, encoding="utf-8")
try:
    import ast
    ast.parse(NEW_TRENDS)
    print("✅ trends_analysis.py actualizado (sintaxis OK)")
except SyntaxError as e:
    print(f"❌ SyntaxError en trends_analysis: {e}")

# ── 3. Insertar función en dashboard ─────────────────────────────
FUNC = '''
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

'''

src = DASH.read_text(encoding="utf-8")

# Insertar función antes de mostrar_keywords
if "def mostrar_keywords_gestion():" not in src:
    OLD = "def mostrar_keywords():"
    src = src.replace(OLD, FUNC + "\ndef mostrar_keywords():", 1)
    print("✅ Funcion mostrar_keywords_gestion() insertada")
else:
    print("⚠️  Funcion ya existe — reemplazando...")
    import re
    # Reemplazar función existente
    pattern = r'def mostrar_keywords_gestion\(\):.*?(?=\ndef )'
    src = re.sub(pattern, FUNC.strip(), src, flags=re.DOTALL)
    print("✅ Funcion reemplazada")

# Verificar que la llamada existe
if "mostrar_keywords_gestion()" not in src:
    OLD2 = '    st.caption(f"Actualizado cada 30 minutos'
    src = src.replace(OLD2, '    mostrar_keywords_gestion()\n    st.caption(f"Actualizado cada 30 minutos', 1)
    print("✅ Llamada añadida")
else:
    print("✅ Llamada ya existe")

# Verificar sintaxis
try:
    ast.parse(src)
    print("✅ Sintaxis dashboard OK")
    DASH.write_text(src, encoding="utf-8")
    print("✅ dashboard_central_final.py actualizado")
except SyntaxError as e:
    print(f"❌ SyntaxError: {e} — no se guarda")

print("\n--- Siguiente paso ---")
print("git add -A && git commit -m 'feat: gestion keywords + autolearning + stopwords custom' && git push")
