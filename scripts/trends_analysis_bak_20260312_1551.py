#!/usr/bin/env python3
"""
trends_analysis.py
Extrae tendencias reales de palabras clave desde titulares usando TF-IDF.
Lee:     data/processed/news_summary.csv
         data/processed/keywords_config.json  (stopwords custom + bloqueadas)
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
    "como","más","pero","sus","le","ya","o","este","fue","ha","lo","si","sobre","entre","cuando","hasta",
    "sin","no","te","le","da","hay","muy","bien","también","después","antes","donde","desde","según"
]

# Cargar config
cfg = {}
if os.path.exists(CONFIG):
    try:
        cfg = json.loads(open(CONFIG).read())
    except Exception:
        cfg = {}
stopwords_custom  = cfg.get("stopwords_custom", [])
keywords_blocked  = set(cfg.get("keywords_blocked", []))
keywords_pinned   = cfg.get("keywords_pinned", [])
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

# Insertar pinned al principio si no están ya
pinned_rows = [{"keyword": kw, "count": 999, "last_update": now} for kw in keywords_pinned
               if kw not in [r["keyword"] for r in rows]]
result = pd.DataFrame(pinned_rows + rows)
result.to_csv(OUTPUT, index=False)

# Histórico
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), result], ignore_index=True)
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)
print(f"CSV de tendencias generado en {OUTPUT} ({len(result)} keywords, {len(keywords_blocked)} bloqueadas)")

# ── Autolearn: detectar keywords inactivas y sugerirlas para bloqueo ──
al = cfg.get("autolearn", {})
if al.get("enabled") and os.path.exists(HISTORY):
    hist_full = pd.read_csv(HISTORY)
    cycles = sorted(hist_full["cycle"].unique())
    min_cycles = al.get("min_cycles_inactive", 10)
    threshold  = al.get("max_pct_change_threshold", 5)
    if len(cycles) >= min_cycles:
        recent = hist_full[hist_full["cycle"].isin(cycles[-min_cycles:])]
        kw_counts = recent.groupby("keyword")["count"].agg(["mean","std"]).reset_index()
        kw_counts["cv"] = (kw_counts["std"] / kw_counts["mean"].replace(0,1)) * 100
        inactive = kw_counts[kw_counts["cv"] < threshold]["keyword"].tolist()
        suggestions = cfg.get("autolearn_suggestions", [])
        new_sugg = [kw for kw in inactive if kw not in suggestions and kw not in keywords_blocked]
        if new_sugg:
            cfg["autolearn_suggestions"] = suggestions + new_sugg
            cfg["last_updated"] = now
            open(CONFIG, "w").write(json.dumps(cfg, indent=2, ensure_ascii=False))
            print(f"Autolearn: {len(new_sugg)} keywords sugeridas para revisión: {new_sugg[:5]}")
