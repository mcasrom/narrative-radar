#!/usr/bin/env python3
"""
diversity_index.py
Índice de diversidad informativa — cuántos temas únicos cubre cada medio
vs cuántos repite de otros.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/diversity_index.csv")
HISTORY = os.path.join(BASE, "data/processed/diversity_history.csv")

SIMILARITY_THRESHOLD = 0.40
RECENT_DAYS          = 3
STOPWORDS = ["de","la","el","en","y","a","que","los","del","se","las","por",
             "un","con","una","su","al","es","para","como","mas","pero","no",
             "este","esta","fue","ha","lo","si","sobre","entre","cuando","hasta"]

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
print(f"[DIVERSITY] {now_str} — Iniciando índice de diversidad")

try:
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    cutoff = now - timedelta(days=RECENT_DAYS)
    df = df[(df["date"] >= cutoff) & (df["date"] <= now)]
    df = df.drop_duplicates(subset=["title"])
    print(f"[DIVERSITY] {len(df)} noticias recientes ({RECENT_DAYS} días)")
except Exception as e:
    print(f"[DIVERSITY] ERROR: {e}"); exit(1)

sources = df["source"].unique()
print(f"[DIVERSITY] {len(sources)} fuentes analizadas")

# Vectorizar todos los titulares
titles  = df["title"].fillna("").tolist()
try:
    vec = TfidfVectorizer(stop_words=STOPWORDS, max_features=5000, ngram_range=(1,2))
    X   = vec.fit_transform(titles)
except Exception as e:
    print(f"[DIVERSITY] ERROR vectorización: {e}"); exit(1)

records = []
for source in sources:
    mask_src    = df["source"] == source
    mask_others = df["source"] != source
    idx_src     = df[mask_src].index.tolist()
    idx_others  = df[mask_others].index.tolist()

    if len(idx_src) < 2:
        continue

    # Posiciones en el array
    pos_src    = [df.index.get_loc(i) for i in idx_src]
    pos_others = [df.index.get_loc(i) for i in idx_others]

    X_src    = X[pos_src]
    X_others = X[pos_others] if pos_others else None

    # Diversidad interna — cuánto varían sus propios titulares
    if len(pos_src) > 1:
        sim_internal = cosine_similarity(X_src)
        np.fill_diagonal(sim_internal, 0)
        avg_internal_sim = float(sim_internal.mean())
        internal_diversity = round(1 - avg_internal_sim, 3)
    else:
        internal_diversity = 1.0

    # Originalidad — cuántos de sus titulares NO aparecen en otros medios
    original = 0
    repeated = 0
    if X_others is not None and X_others.shape[0] > 0:
        sim_vs_others = cosine_similarity(X_src, X_others)
        for i in range(len(pos_src)):
            max_sim = float(sim_vs_others[i].max())
            if max_sim < SIMILARITY_THRESHOLD:
                original += 1
            else:
                repeated += 1
    else:
        original = len(pos_src)

    total          = len(pos_src)
    originality    = round(original / total, 3)
    diversity_score = round((internal_diversity * 0.4 + originality * 0.6) * 100, 1)

    records.append({
        "source":             source,
        "news_count":         total,
        "internal_diversity": internal_diversity,
        "originality":        originality,
        "original_news":      original,
        "repeated_news":      repeated,
        "diversity_score":    diversity_score,
        "last_update":        now_str
    })

df_result = pd.DataFrame(records).sort_values("diversity_score", ascending=False)
df_result.to_csv(OUTPUT, index=False)

# Histórico
df_result["cycle"] = now_str
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_result], ignore_index=True)
    hist = hist.drop_duplicates(subset=["source","cycle"], keep="last")
else:
    hist = df_result.copy()
hist.to_csv(HISTORY, index=False)

print("\n=== ÍNDICE DE DIVERSIDAD INFORMATIVA ===")
print(f"  {'Fuente':<25} {'Score':>6} {'Original%':>10} {'Div.Int':>8} {'Noticias':>9}")
print("  " + "-"*60)
for _, row in df_result.iterrows():
    bar = "█" * int(row["diversity_score"] / 10)
    print(f"  {row['source']:<25} {row['diversity_score']:>5.1f}  {row['originality']*100:>8.1f}%  {row['internal_diversity']:>7.3f}  {row['news_count']:>8}  {bar}")

print(f"\n[DIVERSITY] Completado — {len(df_result)} fuentes indexadas")
